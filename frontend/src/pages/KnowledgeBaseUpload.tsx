import React, { useState, useCallback } from 'react';
import {
  Box,
  Paper,
  Typography,
  Button,
  LinearProgress,
  Alert,
  Chip,
  Stack,
  FormControlLabel,
  Switch,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Grid,
  Card,
  CardContent,
  IconButton,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
} from '@mui/material';
import {
  CloudUpload as UploadIcon,
  Delete as DeleteIcon,
  Article as ArticleIcon,
  CheckCircle as SuccessIcon,
  Error as ErrorIcon,
  Replay as RetryIcon,
  AutoFixHigh as ReprocessIcon,
} from '@mui/icons-material';
import { useDropzone } from 'react-dropzone';
import apiClient from '../services/apiClient';

interface UploadedFile {
  file: File;
  status: 'pending' | 'uploading' | 'processing' | 'success' | 'error';
  progress: number;
  error?: string;
  chunks?: number;
  characters?: number;
  statusMessage?: string;
  documentId?: string;
  processingStatus?: {
    status: string;
    progress_percent: number;
    current_chunk: number;
    total_chunks: number;
    estimated_time_seconds?: number;
  };
}

const KnowledgeBaseUpload: React.FC = () => {
  const [files, setFiles] = useState<UploadedFile[]>([]);
  const [uploading, setUploading] = useState(false);
  const [useFullContent, setUseFullContent] = useState(true);
  const [chunkSize, setChunkSize] = useState(1000);
  const [extractImages, setExtractImages] = useState(true);
  const [ocrEnabled, setOcrEnabled] = useState(true);
  const [forceOcr, setForceOcr] = useState(false);
  const [qualityMode, setQualityMode] = useState<'fast' | 'balanced' | 'high'>('balanced');
  const [duplicateMode, setDuplicateMode] = useState<'skip' | 'replace' | 'allow'>('skip');
  const [uploadResults, setUploadResults] = useState<any>(null);
  const [statistics, setStatistics] = useState<any>(null);
  const [currentUploadingFile, setCurrentUploadingFile] = useState<string>('');
  const [uploadedDocumentIds, setUploadedDocumentIds] = useState<string[]>([]);
  const [pollingActive, setPollingActive] = useState(false);

  // Load statistics on mount
  React.useEffect(() => {
    loadStatistics();
  }, []);

  // Poll for processing status of uploaded documents
  React.useEffect(() => {
    if (!pollingActive || uploadedDocumentIds.length === 0) return;

    const pollStatus = async () => {
      try {
        const response = await apiClient.get('/api/medical/knowledge/upload-status');
        const queuedDocs = response.data.documents || [];

        setFiles((prev) =>
          prev.map((fileData) => {
            const doc = queuedDocs.find((d: any) => d.document_id === fileData.documentId);
            if (doc) {
              return {
                ...fileData,
                processingStatus: {
                  status: doc.status,
                  progress_percent: doc.progress_percent,
                  current_chunk: doc.current_chunk,
                  total_chunks: doc.total_chunks,
                  estimated_time_seconds: doc.estimated_time_seconds,
                },
                progress: Math.max(fileData.progress, doc.progress_percent),
                statusMessage:
                  doc.status === 'completed'
                    ? '[OK] Processing completed and indexed'
                    : `[${doc.status.toUpperCase()}] ${doc.progress_percent}% complete (${doc.current_chunk}/${doc.total_chunks} chunks)`,
              };
            }
            return fileData;
          })
        );
      } catch (error) {
        console.error('Failed to poll processing status:', error);
      }
    };

    const interval = setInterval(pollStatus, 2000); // Poll every 2 seconds
    return () => clearInterval(interval);
  }, [pollingActive, uploadedDocumentIds]);

  // Stop polling when all documents are completed
  React.useEffect(() => {
    const allCompleted = files
      .filter((f) => uploadedDocumentIds.includes(f.documentId || ''))
      .every((f) => f.processingStatus?.status === 'completed' || f.status === 'success');

    if (allCompleted && uploadedDocumentIds.length > 0) {
      setPollingActive(false);
    }
  }, [files, uploadedDocumentIds]);

  const loadStatistics = async () => {
    try {
      const response = await apiClient.get('/api/medical/knowledge/statistics');
      setStatistics(response.data);
    } catch (error) {
      console.error('Failed to load statistics:', error);
    }
  };

  const onDrop = useCallback((acceptedFiles: File[]) => {
    const newFiles: UploadedFile[] = acceptedFiles.map((file) => ({
      file,
      status: 'pending',
      progress: 0,
    }));
    setFiles((prev) => [...prev, ...newFiles]);
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'text/plain': ['.txt'],
      'application/msword': ['.doc'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
    },
    maxSize: 1024 * 1024 * 1024, // 1GB
    multiple: true,
  });

  const removeFile = (index: number) => {
    setFiles((prev) => prev.filter((_, i) => i !== index));
  };

  const retryFile = async (index: number) => {
    const target = files[index];
    if (!target) return;
    setFiles((prev) => prev.map((f, i) => i === index ? { ...f, status: 'pending', progress: 0, error: undefined, statusMessage: 'Ready to retry' } : f));
    await uploadFiles();
  };

  const reprocessFileWithForceOCR = async (index: number) => {
    const target = files[index];
    if (!target?.documentId) return;
    try {
      await apiClient.post(`/api/medical/knowledge/reprocess/${target.documentId}?force_ocr=true&ocr_preprocess=true&ocr_dpi=350`);
      setFiles((prev) => prev.map((f, i) => i === index ? { ...f, status: 'processing', progress: 15, statusMessage: '[REPROCESS] Queued with force OCR' } : f));
      setPollingActive(true);
      setUploadedDocumentIds((prev) => Array.from(new Set([...prev, target.documentId as string])));
    } catch (e: any) {
      setFiles((prev) => prev.map((f, i) => i === index ? { ...f, status: 'error', statusMessage: `[ERROR] Reprocess failed: ${e?.response?.data?.detail || e?.message || 'unknown error'}` } : f));
    }
  };

  const uploadFiles = async () => {
    if (files.length === 0) return;

    setUploading(true);
    setUploadResults(null);

    try {
      const pendingFiles = files.filter((f) => f.status === 'pending' || f.status === 'error');
      const hasLargeFiles = pendingFiles.some((f) => f.file.size > 200 * 1024 * 1024);

      const formData = new FormData();
      
      pendingFiles.forEach((fileData) => {
        formData.append('files', fileData.file);
      });
      
      formData.append('use_full_content', String(useFullContent));
      formData.append('chunk_size', String(chunkSize));
      formData.append('extract_images', String(extractImages));
      formData.append('ocr_enabled', String(ocrEnabled));
      formData.append('force_ocr', String(forceOcr));
      formData.append('ocr_preprocess', String(true));
      formData.append('ocr_dpi', String(qualityMode === 'high' ? 350 : 300));
      formData.append('quality_mode', qualityMode);
      formData.append('duplicate_mode', duplicateMode);

      // Update status to uploading with initial message
      setFiles((prev) =>
        prev.map((f) => ({ 
          ...f, 
          status: 'uploading' as const, 
          progress: 10,
          statusMessage: '[UP] Uploading file to server...'
        }))
      );

      let response: any;
      if (hasLargeFiles && pendingFiles.length === 1) {
        const largeFd = new FormData();
        largeFd.append('file', pendingFiles[0].file);
        response = await apiClient.post('/api/medical/knowledge/upload-large', largeFd, {
          headers: { 'Content-Type': 'multipart/form-data' },
          onUploadProgress: (progressEvent) => {
            const percentCompleted = progressEvent.total
              ? Math.round((progressEvent.loaded * 100) / progressEvent.total)
              : 0;
            setFiles((prev) =>
              prev.map((f) => ({ ...f, progress: percentCompleted, statusMessage: '[UP] Large-file streaming upload...' }))
            );
          },
        });

        // Normalize upload-large response shape to existing structure
        response = {
          data: {
            results: [
              {
                filename: pendingFiles[0].file.name,
                status: response?.data?.processing_result?.status === 'success' ? 'success' : 'error',
                chunks: response?.data?.processing_result?.chunks_processed || 0,
                characters: undefined,
                document_id: undefined,
                info: response?.data?.message,
                error: response?.data?.processing_result?.error,
              },
            ],
            summary: {
              successful: response?.data?.processing_result?.status === 'success' ? 1 : 0,
              failed: response?.data?.processing_result?.status === 'success' ? 0 : 1,
              total_chunks_created: response?.data?.processing_result?.chunks_processed || 0,
              total_size_mb: response?.data?.file_size_mb || 0,
            },
            message: response?.data?.message || 'Large file upload completed',
          },
        };
      } else {
        response = await apiClient.post('/api/medical/knowledge/upload', formData, {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
          onUploadProgress: (progressEvent) => {
            const percentCompleted = progressEvent.total
              ? Math.round((progressEvent.loaded * 100) / progressEvent.total)
              : 0;
            
            let statusMessage = '[UP] Uploading file to server...';
            if (percentCompleted > 80) {
              statusMessage = '[GEAR] Processing and extracting text...';
            } else if (percentCompleted > 50) {
              statusMessage = '[UP] Uploading... Almost there!';
            }
            
            setFiles((prev) =>
              prev.map((f) => ({ 
                ...f, 
                progress: percentCompleted,
                statusMessage: f.status === 'uploading' ? statusMessage : f.statusMessage
              }))
            );
          },
        });
      }

      // Processing phase
      setFiles((prev) =>
        prev.map((f) => ({ 
          ...f, 
          status: 'processing' as const,
          progress: 90,
          statusMessage: '[BACKGROUND] Embeddings being generated asynchronously - will be ready in 10-30 seconds'
        }))
      );

      setUploadResults(response.data);

      // Extract document IDs and start polling
      const docIds: string[] = [];
      response.data.results.forEach((result: any) => {
        if (result.status === 'success' && result.document_id) {
          docIds.push(result.document_id);
        }
      });
      
      if (docIds.length > 0) {
        setUploadedDocumentIds(docIds);
        setPollingActive(true);
      }

      // Update file statuses based on results
      setFiles((prev) =>
        prev.map((fileData) => {
          const result = response.data.results?.find(
            (r: any) => r.filename === fileData.file.name
          );
          if (!result) return { ...fileData, status: 'error' as const, progress: 100, statusMessage: '[ERROR] No response from server for this file' };
          const info = result.info ? `\n${result.info}` : '';
          if (result.status === 'success') {
            return {
              ...fileData,
              status: 'success' as const,
              progress: 100,
              chunks: result.chunks,
              characters: result.characters,
              documentId: result.document_id,
              statusMessage: `[OK] Document queued - background processing started${info}`,
            };
          } else if (result.status === 'skipped') {
            return {
              ...fileData,
              status: 'success' as const,
              progress: 100,
              statusMessage: `[SKIP] Already uploaded: ${result.reason || 'Duplicate document'}`,
            };
          } else {
            const errorMsg = result.error || result.detail || result.reason || 'Unknown error';
            return {
              ...fileData,
              status: 'error' as const,
              progress: 100,
              error: errorMsg,
              statusMessage: `[ERROR] ${errorMsg}`,
            };
          }
        })
      );

      // Reload statistics
      await loadStatistics();

    } catch (error: any) {
      console.error('Upload error:', error);
      setFiles((prev) =>
        prev.map((f) => ({
          ...f,
          status: 'error',
          error: error.response?.data?.detail || 'Upload failed',
          statusMessage: `[ERROR] ${error.response?.data?.detail || 'Upload failed'}`,
        }))
      );
    } finally {
      setUploading(false);
      setCurrentUploadingFile('');
    }
  };

  const clearFiles = () => {
    setFiles([]);
    setUploadResults(null);
  };

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(2)} KB`;
    return `${(bytes / 1024 / 1024).toFixed(2)} MB`;
  };

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        [BOOKS] Knowledge Base - PDF Upload
      </Typography>
      <Typography variant="body1" color="text.secondary" paragraph>
        Upload medical PDFs, documents, and textbooks to enhance the AI knowledge base.
        Supports multiple file uploads with intelligent text extraction.
      </Typography>

      {/* Statistics Card */}
      {statistics && (
        <Card sx={{ mb: 3, bgcolor: 'primary.50' }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Current Knowledge Base Statistics
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={12} sm={6} md={3}>
                <Typography variant="body2" color="text.secondary">
                  Database Entries
                </Typography>
                <Typography variant="h5">
                  {statistics.total_documents || 0}
                </Typography>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Typography variant="body2" color="text.secondary">
                  Total Chunks
                </Typography>
                <Typography variant="h5">{statistics.total_chunks || 0}</Typography>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Typography variant="body2" color="text.secondary">
                  Categories
                </Typography>
                <Typography variant="h5">
                  {statistics.categories_count || 0}
                </Typography>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Typography variant="body2" color="text.secondary">
                  Categories
                </Typography>
                <Typography variant="h5">
                  {statistics.source_details?.['Local Database']?.categories || 0}
                </Typography>
              </Grid>
            </Grid>
          </CardContent>
        </Card>
      )}

      {/* Upload Settings */}
      <Paper sx={{ p: 3, mb: 3 }}>
        <Typography variant="h6" gutterBottom>
          Upload Settings
        </Typography>
        <Stack spacing={2}>
          <FormControlLabel
            control={
              <Switch
                checked={useFullContent}
                onChange={(e) => setUseFullContent(e.target.checked)}
                disabled={uploading}
              />
            }
            label={
              <Box>
                <Typography variant="body1">
                  Use Full PDF Content
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  {useFullContent
                    ? 'Entire document will be processed as one piece (preserves context)'
                    : 'Document will be split into intelligent chunks (better for large files)'}
                </Typography>
              </Box>
            }
          />

          <FormControlLabel
            control={
              <Switch
                checked={extractImages}
                onChange={(e) => setExtractImages(e.target.checked)}
                disabled={uploading}
              />
            }
            label="Extract medical images/charts from PDF"
          />

          <FormControlLabel
            control={
              <Switch
                checked={ocrEnabled}
                onChange={(e) => setOcrEnabled(e.target.checked)}
                disabled={uploading}
              />
            }
            label="Enable OCR fallback for scanned pages"
          />

          <FormControlLabel
            control={
              <Switch
                checked={forceOcr}
                onChange={(e) => setForceOcr(e.target.checked)}
                disabled={uploading || !ocrEnabled}
              />
            }
            label="Force OCR on all pages (higher quality, slower)"
          />

          <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2}>
            <FormControl sx={{ minWidth: 220 }} disabled={uploading}>
              <InputLabel id="quality-mode-label">Quality Mode</InputLabel>
              <Select
                labelId="quality-mode-label"
                value={qualityMode}
                label="Quality Mode"
                onChange={(e) => setQualityMode(e.target.value as 'fast' | 'balanced' | 'high')}
              >
                <MenuItem value="fast">Fast (optimized throughput)</MenuItem>
                <MenuItem value="balanced">Balanced (recommended)</MenuItem>
                <MenuItem value="high">High quality (deeper processing)</MenuItem>
              </Select>
            </FormControl>

            <FormControl sx={{ minWidth: 220 }} disabled={uploading}>
              <InputLabel id="duplicate-mode-label">Duplicate Handling</InputLabel>
              <Select
                labelId="duplicate-mode-label"
                value={duplicateMode}
                label="Duplicate Handling"
                onChange={(e) => setDuplicateMode(e.target.value as 'skip' | 'replace' | 'allow')}
              >
                <MenuItem value="skip">Skip duplicates</MenuItem>
                <MenuItem value="replace">Replace previous duplicate</MenuItem>
                <MenuItem value="allow">Allow duplicates</MenuItem>
              </Select>
            </FormControl>
          </Stack>

          {!useFullContent && (
            <TextField
              label="Chunk Size (characters)"
              type="number"
              value={chunkSize}
              onChange={(e) => setChunkSize(Number(e.target.value))}
              disabled={uploading}
              helperText="Size of each text chunk. Larger = more context, Smaller = more granular search"
              sx={{ maxWidth: 300 }}
            />
          )}
        </Stack>
      </Paper>

      {/* Dropzone */}
      <Paper
        {...getRootProps()}
        sx={{
          p: 4,
          mb: 3,
          border: '2px dashed',
          borderColor: isDragActive ? 'primary.main' : 'grey.300',
          bgcolor: isDragActive ? 'primary.50' : 'grey.50',
          cursor: 'pointer',
          transition: 'all 0.3s',
          '&:hover': {
            borderColor: 'primary.main',
            bgcolor: 'primary.50',
          },
        }}
      >
        <input {...getInputProps()} />
        <Box sx={{ textAlign: 'center' }}>
          <UploadIcon sx={{ fontSize: 64, color: 'primary.main', mb: 2 }} />
          <Typography variant="h6" gutterBottom>
            {isDragActive ? 'Drop files here...' : 'Drag & drop files here'}
          </Typography>
          <Typography variant="body2" color="text.secondary" paragraph>
            or click to select files
          </Typography>
          <Stack direction="row" spacing={1} justifyContent="center" flexWrap="wrap">
            <Chip label="PDF" size="small" />
            <Chip label="TXT" size="small" />
            <Chip label="DOC" size="small" />
            <Chip label="DOCX" size="small" />
          </Stack>
          <Typography variant="caption" color="text.secondary" sx={{ mt: 2, display: 'block' }}>
            Max 1GB per file - Max 20 files - Server-side large upload optimization enabled
          </Typography>
        </Box>
      </Paper>

      {/* File List */}
      {files.length > 0 && (
        <Paper sx={{ p: 2, mb: 3 }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
            <Typography variant="h6">
              Selected Files ({files.length})
            </Typography>
            {!uploading && (
              <Button size="small" onClick={clearFiles}>
                Clear All
              </Button>
            )}
          </Box>

          <List>
            {files.map((fileData, index) => (
              <ListItem
                key={index}
                sx={{
                  bgcolor: 'grey.50',
                  mb: 1,
                  borderRadius: 1,
                }}
              >
                <ArticleIcon sx={{ mr: 2, color: 'primary.main' }} />
                <ListItemText
                  primary={fileData.file.name}
                  secondaryTypographyProps={{ component: 'div' }}
                  secondary={
                    <span>
                      <Typography variant="caption" component="span" display="block">
                        {formatFileSize(fileData.file.size)}
                      </Typography>
                      {(fileData.status === 'uploading' || fileData.status === 'processing') && (
                        <Box sx={{ display: 'block', mt: 0.5 }}>
                          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 0.25 }}>
                            <Typography variant="caption" color="primary" fontWeight={600} component="span">
                              {fileData.statusMessage || 'Processing...'}
                            </Typography>
                            <Typography variant="caption" color="text.secondary" component="span">
                              {fileData.progress}%
                            </Typography>
                          </Box>
                          <LinearProgress
                            variant="determinate"
                            value={fileData.progress}
                            sx={{ height: 6, borderRadius: 3 }}
                          />
                        </Box>
                      )}
                      {fileData.status === 'success' && (
                        <Alert severity="success" sx={{ mt: 1, display: 'block' }} icon={<SuccessIcon />}>
                          <Typography variant="caption" display="block" fontWeight={600}>
                            {fileData.statusMessage}
                          </Typography>
                          <Typography variant="caption" display="block">
                            {fileData.chunks} chunks - {fileData.characters?.toLocaleString()} characters
                          </Typography>
                        </Alert>
                      )}
                      {fileData.status === 'error' && (
                        <Alert severity="error" sx={{ mt: 1, display: 'block' }} icon={<ErrorIcon />}>
                          {fileData.statusMessage || fileData.error}
                        </Alert>
                      )}
                    </span>
                  }
                />
                <ListItemSecondaryAction>
                  {fileData.status === 'pending' && (
                    <IconButton edge="end" onClick={() => removeFile(index)}>
                      <DeleteIcon />
                    </IconButton>
                  )}
                  {fileData.status === 'success' && <SuccessIcon color="success" />}
                  {fileData.status === 'error' && (
                    <Stack direction="row" spacing={1}>
                      <IconButton edge="end" onClick={() => retryFile(index)} title="Retry upload">
                        <RetryIcon color="warning" />
                      </IconButton>
                      {fileData.documentId && (
                        <IconButton edge="end" onClick={() => reprocessFileWithForceOCR(index)} title="Reprocess with force OCR">
                          <ReprocessIcon color="primary" />
                        </IconButton>
                      )}
                      <ErrorIcon color="error" />
                    </Stack>
                  )}
                </ListItemSecondaryAction>
              </ListItem>
            ))}
          </List>

          <Box sx={{ mt: 2, display: 'flex', gap: 2 }}>
            <Button
              variant="contained"
              size="large"
              startIcon={<UploadIcon />}
              onClick={uploadFiles}
              disabled={uploading || files.every((f) => f.status !== 'pending')}
              fullWidth
            >
              {uploading ? 'Uploading...' : `Upload ${files.length} File(s)`}
            </Button>
          </Box>
        </Paper>
      )}

      {/* Upload Results */}
      {uploadResults && (
        <Alert
          severity={uploadResults.summary.failed === 0 ? 'success' : 'warning'}
          sx={{ mb: 3 }}
        >
          <Typography variant="body1" gutterBottom>
            <strong>{uploadResults.message}</strong>
          </Typography>
          <Typography variant="body2">
            - Successful: {uploadResults.summary.successful}
            <br />
            - Failed: {uploadResults.summary.failed}
            <br />
            - Total Chunks: {uploadResults.summary.total_chunks_created}
            <br />
            - Total Size: {uploadResults.summary.total_size_mb.toFixed(2)} MB
          </Typography>
        </Alert>
      )}
    </Box>
  );
};

export default KnowledgeBaseUpload;
