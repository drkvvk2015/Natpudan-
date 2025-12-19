import React, { useState, useCallback } from "react";
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
  Grid,
  Card,
  CardContent,
  IconButton,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
} from "@mui/material";
import { keyframes } from "@mui/system";
import {
  CloudUpload as UploadIcon,
  Delete as DeleteIcon,
  Article as ArticleIcon,
  CheckCircle as SuccessIcon,
  Error as ErrorIcon,
} from "@mui/icons-material";
import { useDropzone } from "react-dropzone";
import apiClient from "../services/apiClient";

// Futuristic animations
const gradientShift = keyframes`
  0% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
`;

const progressGlow = keyframes`
  0% { background-position: 0% 50%; }
  100% { background-position: 200% 50%; }
`;

const pulse = keyframes`
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.1); }
`;

const fadeIn = keyframes`
  0% { transform: scale(0.95); opacity: 0; }
  100% { transform: scale(1); opacity: 1; }
`;

const shake = keyframes`
  0%, 100% { transform: translateX(0); }
  10%, 30%, 50%, 70%, 90% { transform: translateX(-5px); }
  20%, 40%, 60%, 80% { transform: translateX(5px); }
`;

interface UploadedFile {
  file: File;
  status: "pending" | "uploading" | "processing" | "success" | "error";
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
  const [uploadResults, setUploadResults] = useState<any>(null);
  const [statistics, setStatistics] = useState<any>(null);
  const [statisticsLoading, setStatisticsLoading] = useState(true);
  const [currentUploadingFile, setCurrentUploadingFile] = useState<string>("");
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
        const response = await apiClient.get(
          "/api/medical/knowledge/upload-status"
        );
        const queuedDocs = response.data.documents || [];

        setFiles((prev) =>
          prev.map((fileData) => {
            const doc = queuedDocs.find(
              (d: any) => d.document_id === fileData.documentId
            );
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
                  doc.status === "completed"
                    ? "[OK] Processing completed and indexed"
                    : `[${doc.status.toUpperCase()}] ${
                        doc.progress_percent
                      }% complete (${doc.current_chunk}/${
                        doc.total_chunks
                      } chunks)`,
              };
            }
            return fileData;
          })
        );
      } catch (error) {
        console.error("Failed to poll processing status:", error);
      }
    };

    const interval = setInterval(pollStatus, 2000); // Poll every 2 seconds
    return () => clearInterval(interval);
  }, [pollingActive, uploadedDocumentIds]);

  // Stop polling when all documents are completed
  React.useEffect(() => {
    const allCompleted = files
      .filter((f) => uploadedDocumentIds.includes(f.documentId || ""))
      .every(
        (f) =>
          f.processingStatus?.status === "completed" || f.status === "success"
      );

    if (allCompleted && uploadedDocumentIds.length > 0) {
      setPollingActive(false);
    }
  }, [files, uploadedDocumentIds]);

  const loadStatistics = async () => {
    try {
      setStatisticsLoading(true);
      const response = await apiClient.get("/api/medical/knowledge/statistics");
      setStatistics(response.data);
    } catch (error) {
      console.error("Failed to load statistics:", error);
    } finally {
      setStatisticsLoading(false);
    }
  };

  const onDrop = useCallback((acceptedFiles: File[]) => {
    const newFiles: UploadedFile[] = acceptedFiles.map((file) => ({
      file,
      status: "pending",
      progress: 0,
    }));
    setFiles((prev) => [...prev, ...newFiles]);
  }, []);

  // Upload constraints (aligned with backend):
  // - Standard path: <= 50MB goes to /upload (synchronous)
  // - Large path: > 50MB goes to /upload-large (background)
  // - Backend hard limit: 1GB per file, 5GB total
  const MAX_FILE_BYTES = 1024 * 1024 * 1024; // 1GB
  const LARGE_FILE_THRESHOLD = 50 * 1024 * 1024; // 50MB

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      "application/pdf": [".pdf"],
      "text/plain": [".txt"],
      "application/msword": [".doc"],
      "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        [".docx"],
    },
    maxSize: MAX_FILE_BYTES,
    multiple: true,
  });

  const removeFile = (index: number) => {
    setFiles((prev) => prev.filter((_, i) => i !== index));
  };

  const uploadFiles = async () => {
    if (files.length === 0) return;

    setUploading(true);
    setUploadResults(null);

    try {
      // Split files into large (>50MB) and standard
      const standardFiles = files.filter(
        (f) => f.file.size <= LARGE_FILE_THRESHOLD
      );
      const largeFiles = files.filter(
        (f) => f.file.size > LARGE_FILE_THRESHOLD
      );

      let standardResults = { results: [] };
      let largeFileResults: any[] = [];

      // 1. Process Standard Files (Batch)
      if (standardFiles.length > 0) {
        const formData = new FormData();
        standardFiles.forEach((fileData) => {
          formData.append("files", fileData.file);
        });
        formData.append("use_full_content", String(useFullContent));
        formData.append("chunk_size", String(chunkSize));

        // Update status for standard files
        setFiles((prev) =>
          prev.map((f) => {
            if (standardFiles.some((sf) => sf.file === f.file)) {
              return {
                ...f,
                status: "uploading",
                progress: 10,
                statusMessage: "[UP] Uploading standard file...",
              };
            }
            return f;
          })
        );

        try {
          const response = await apiClient.post(
            "/api/medical/knowledge/upload",
            formData,
            {
              headers: { "Content-Type": "multipart/form-data" },
              onUploadProgress: (progressEvent) => {
                const percent = progressEvent.total
                  ? Math.round(
                      (progressEvent.loaded * 100) / progressEvent.total
                    )
                  : 0;
                setFiles((prev) =>
                  prev.map((f) => {
                    if (standardFiles.some((sf) => sf.file === f.file)) {
                      return { ...f, progress: percent };
                    }
                    return f;
                  })
                );
              },
            }
          );
          standardResults = response.data;
        } catch (error: any) {
          console.error("Standard upload failed", error);
          // Mark standard files as error
          setFiles((prev) =>
            prev.map((f) => {
              if (standardFiles.some((sf) => sf.file === f.file)) {
                return {
                  ...f,
                  status: "error",
                  error: "Batch upload failed",
                  statusMessage: "[ERROR] Upload failed",
                };
              }
              return f;
            })
          );
        }
      }

      // 2. Process Large Files (Individually)
      for (const largeFile of largeFiles) {
        try {
          setFiles((prev) =>
            prev.map((f) => {
              if (f.file === largeFile.file) {
                return {
                  ...f,
                  status: "uploading" as const,
                  progress: 1,
                  statusMessage:
                    "[UP] Uploading large file (this may take time)...",
                };
              }
              return f;
            })
          );

          const formData = new FormData();
          formData.append("file", largeFile.file);

          const response = await apiClient.post(
            "/api/medical/knowledge/upload-large",
            formData,
            {
              headers: { "Content-Type": "multipart/form-data" },
              // Allow very long uploads for large textbooks (e.g., 300MB+)
              timeout: 20 * 60 * 1000, // 20 minutes
              onUploadProgress: (progressEvent) => {
                const percent = progressEvent.total
                  ? Math.round(
                      (progressEvent.loaded * 100) / progressEvent.total
                    )
                  : 0;
                setFiles((prev) =>
                  prev.map((f) => {
                    if (f.file === largeFile.file) {
                      return { ...f, progress: percent };
                    }
                    return f;
                  })
                );
              },
            }
          );

          if (response.data.results && response.data.results[0]) {
            largeFileResults.push(response.data.results[0]);
          }
        } catch (error: any) {
          console.error(
            `Large file upload failed: ${largeFile.file.name}`,
            error
          );
          setFiles((prev) =>
            prev.map((f) => {
              if (f.file === largeFile.file) {
                return {
                  ...f,
                  status: "error",
                  error: "Large file upload failed",
                  statusMessage: "[ERROR] Server timeout or error",
                };
              }
              return f;
            })
          );
        }
      }

      // Merge results
      const allResults = [
        ...(standardResults.results || []),
        ...largeFileResults,
      ];
      const mergedResponse = {
        message: `Processed ${allResults.length} files`,
        results: allResults,
        summary: {
          successful: allResults.filter((r: any) => r.status === "success")
            .length,
          failed: allResults.filter((r: any) => r.status === "error").length,
          total_chunks_created: 0, // Simplified
          total_size_mb: 0,
        },
      };

      setUploadResults(mergedResponse);

      // Extract document IDs and start polling
      const docIds: string[] = [];
      allResults.forEach((result: any) => {
        if (result.status === "success" && result.document_id) {
          docIds.push(result.document_id);
        }
      });

      if (docIds.length > 0) {
        setUploadedDocumentIds((prev) => [...prev, ...docIds]);
        setPollingActive(true);
      }

      // Update UI status based on results
      setFiles((prev) =>
        prev.map((fileData) => {
          // Match result by filename
          const result = allResults.find(
            (r: any) => r.filename === fileData.file.name
          );

          if (!result) return fileData; // Keep existing status if not in this batch (or error handled above)

          const info = result.info ? `\n${result.info}` : "";

          const updatedFile: UploadedFile = {
            ...fileData,
            status: result.status === "success" ? "success" : "error",
            progress: 100,
            error: result.error,
            chunks: result.chunks,
            characters: result.characters,
            documentId: result.document_id,
            statusMessage:
              result.status === "success"
                ? `[OK] Queued for processing${info}`
                : result.status === "skipped"
                ? `[INFO] ${result.reason || "Document already uploaded"}`
                : `[ERROR] ${result.error || "Unknown error"}`,
          };

          if (result.status === "skipped") updatedFile.status = "success";

          return updatedFile;
        })
      );

      // Reload statistics
      await loadStatistics();
    } catch (error: any) {
      // Global error handler (fallback)
      console.error("Upload error:", error);
    } finally {
      setUploading(false);
      setCurrentUploadingFile("");
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
        Upload medical PDFs, documents, and textbooks to enhance the AI
        knowledge base. Supports multiple file uploads with intelligent text
        extraction.
      </Typography>

      {/* Statistics Card */}
      {statisticsLoading ? (
        <Card sx={{ mb: 3, bgcolor: "grey.50" }}>
          <CardContent>
            <Box
              sx={{
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                py: 3,
              }}
            >
              <CircularProgress size={40} sx={{ mr: 2 }} />
              <Typography variant="body1" color="text.secondary">
                Loading knowledge base status...
              </Typography>
            </Box>
          </CardContent>
        </Card>
      ) : statistics ? (
        <Card sx={{ mb: 3, bgcolor: "primary.50" }}>
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
                <Typography variant="h5">
                  {statistics.total_chunks || 0}
                </Typography>
              </Grid>
              <Grid item xs={12} sm={6} md={3}>
                <Typography variant="body2" color="text.secondary">
                  Categories
                </Typography>
                <Typography variant="h5">
                  {statistics.categories_count || 0}
                </Typography>
              </Grid>
            </Grid>
          </CardContent>
        </Card>
      ) : (
        <Alert severity="info" sx={{ mb: 3 }}>
          No statistics available. Upload some documents to get started.
        </Alert>
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
                <Typography variant="body1">Use Full PDF Content</Typography>
                <Typography variant="caption" color="text.secondary">
                  {useFullContent
                    ? "Entire document will be processed as one piece (preserves context)"
                    : "Document will be split into intelligent chunks (better for large files)"}
                </Typography>
              </Box>
            }
          />

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
          border: "2px dashed",
          borderColor: isDragActive ? "primary.main" : "grey.300",
          bgcolor: isDragActive ? "primary.50" : "grey.50",
          cursor: "pointer",
          transition: "all 0.3s",
          "&:hover": {
            borderColor: "primary.main",
            bgcolor: "primary.50",
          },
        }}
      >
        <input {...getInputProps()} />
        <Box sx={{ textAlign: "center" }}>
          <UploadIcon sx={{ fontSize: 64, color: "primary.main", mb: 2 }} />
          <Typography variant="h6" gutterBottom>
            {isDragActive ? "Drop files here..." : "Drag & drop files here"}
          </Typography>
          <Typography variant="body2" color="text.secondary" paragraph>
            or click to select files
          </Typography>
          <Stack
            direction="row"
            spacing={1}
            justifyContent="center"
            flexWrap="wrap"
          >
            <Chip label="PDF" size="small" />
            <Chip label="TXT" size="small" />
            <Chip label="DOC" size="small" />
            <Chip label="DOCX" size="small" />
          </Stack>
          <Typography
            variant="caption"
            color="text.secondary"
            sx={{ mt: 2, display: "block" }}
          >
            Max 1GB per file (PDF/TXT/DOC/DOCX) · Max 20 files · Max 5GB total.
            Files over 50MB are queued for background processing.
          </Typography>
        </Box>
      </Paper>

      {/* File List */}
      {files.length > 0 && (
        <Paper sx={{ p: 2, mb: 3 }}>
          <Box
            sx={{
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
              mb: 2,
            }}
          >
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
                  bgcolor: "grey.50",
                  mb: 1,
                  borderRadius: 1,
                }}
              >
                <ArticleIcon sx={{ mr: 2, color: "primary.main" }} />
                <ListItemText
                  primary={fileData.file.name}
                  secondary={
                    <span>
                      <Typography
                        variant="caption"
                        component="span"
                        display="block"
                      >
                        {formatFileSize(fileData.file.size)}
                      </Typography>
                      {(fileData.status === "uploading" ||
                        fileData.status === "processing") && (
                        <Box sx={{ mt: 1 }}>
                          <Box
                            display="flex"
                            justifyContent="space-between"
                            alignItems="center"
                            mb={0.5}
                          >
                            <Typography
                              variant="caption"
                              sx={{
                                fontWeight: 600,
                                background:
                                  fileData.status === "processing"
                                    ? "linear-gradient(90deg, #00f5ff 0%, #00d4ff 50%, #0099ff 100%)"
                                    : "linear-gradient(90deg, #4CAF50 0%, #81C784 100%)",
                                backgroundSize: "200% 100%",
                                animation:
                                  fileData.status === "processing"
                                    ? `${gradientShift} 3s ease infinite`
                                    : "none",
                                WebkitBackgroundClip: "text",
                                WebkitTextFillColor: "transparent",
                                backgroundClip: "text",
                              }}
                            >
                              {fileData.statusMessage || "Processing..."}
                            </Typography>
                            <Chip
                              label={`${fileData.progress}%`}
                              size="small"
                              sx={{
                                bgcolor:
                                  fileData.status === "processing"
                                    ? "#00d4ff"
                                    : "#4CAF50",
                                color: "white",
                                fontWeight: "bold",
                                animation:
                                  fileData.status === "processing"
                                    ? `${pulse} 2s ease-in-out infinite`
                                    : "none",
                              }}
                            />
                          </Box>
                          <LinearProgress
                            variant="determinate"
                            value={fileData.progress}
                            sx={{
                              height: 8,
                              borderRadius: 4,
                              background:
                                "linear-gradient(90deg, #f0f0f0 0%, #e0e0e0 100%)",
                              "& .MuiLinearProgress-bar": {
                                background:
                                  fileData.status === "processing"
                                    ? "linear-gradient(90deg, #00f5ff 0%, #00d4ff 50%, #0099ff 100%)"
                                    : "linear-gradient(90deg, #4CAF50 0%, #81C784 100%)",
                                backgroundSize: "200% 100%",
                                animation:
                                  fileData.status === "processing"
                                    ? `${progressGlow} 2s linear infinite`
                                    : "none",
                                borderRadius: 4,
                                boxShadow:
                                  fileData.status === "processing"
                                    ? "0 0 10px rgba(0, 212, 255, 0.5)"
                                    : "0 0 10px rgba(76, 175, 80, 0.3)",
                              },
                            }}
                          />
                        </Box>
                      )}
                      {fileData.status === "success" && (
                        <Alert
                          severity="success"
                          sx={{
                            mt: 1,
                            display: "block",
                            background:
                              "linear-gradient(135deg, #E8F5E9 0%, #C8E6C9 100%)",
                            border: "2px solid #4CAF50",
                            animation: `${fadeIn} 0.5s ease-out`,
                          }}
                          icon={<SuccessIcon sx={{ color: "#2E7D32" }} />}
                        >
                          <Typography
                            variant="caption"
                            display="block"
                            fontWeight={600}
                            sx={{ color: "#1B5E20" }}
                          >
                            ✅ {fileData.statusMessage}
                          </Typography>
                          <Typography
                            variant="caption"
                            display="block"
                            sx={{ color: "#2E7D32" }}
                          >
                            {fileData.chunks} chunks -{" "}
                            {fileData.characters?.toLocaleString()} characters
                          </Typography>
                        </Alert>
                      )}
                      {fileData.status === "error" && (
                        <Box sx={{ mt: 1 }}>
                          <Box
                            display="flex"
                            justifyContent="space-between"
                            alignItems="center"
                            mb={0.5}
                          >
                            <Typography
                              variant="caption"
                              sx={{
                                fontWeight: 600,
                                color: "#d32f2f",
                              }}
                            >
                              ❌ Upload Failed
                            </Typography>
                            <Chip
                              label="0%"
                              size="small"
                              sx={{
                                bgcolor: "#d32f2f",
                                color: "white",
                                fontWeight: "bold",
                              }}
                            />
                          </Box>
                          <LinearProgress
                            variant="determinate"
                            value={0}
                            sx={{
                              height: 8,
                              borderRadius: 4,
                              background: "#ffebee",
                              "& .MuiLinearProgress-bar": {
                                background: "#d32f2f",
                                borderRadius: 4,
                              },
                            }}
                          />
                          <Alert
                            severity="error"
                            sx={{
                              mt: 1,
                              display: "block",
                              background:
                                "linear-gradient(135deg, #FFEBEE 0%, #FFCDD2 100%)",
                              border: "2px solid #d32f2f",
                              animation: `${shake} 0.6s ease`,
                            }}
                            icon={<ErrorIcon sx={{ color: "#c62828" }} />}
                          >
                            <Typography
                              variant="caption"
                              sx={{ color: "#b71c1c", fontWeight: 600 }}
                            >
                              {fileData.statusMessage || fileData.error}
                            </Typography>
                          </Alert>
                        </Box>
                      )}
                    </span>
                  }
                />
                <ListItemSecondaryAction>
                  {fileData.status === "pending" && (
                    <IconButton edge="end" onClick={() => removeFile(index)}>
                      <DeleteIcon />
                    </IconButton>
                  )}
                  {fileData.status === "success" && (
                    <SuccessIcon color="success" />
                  )}
                  {fileData.status === "error" && <ErrorIcon color="error" />}
                </ListItemSecondaryAction>
              </ListItem>
            ))}
          </List>

          <Box sx={{ mt: 2, display: "flex", gap: 2 }}>
            <Button
              variant="contained"
              size="large"
              startIcon={<UploadIcon />}
              onClick={uploadFiles}
              disabled={uploading || files.every((f) => f.status !== "pending")}
              fullWidth
            >
              {uploading ? "Uploading..." : `Upload ${files.length} File(s)`}
            </Button>
          </Box>
        </Paper>
      )}

      {/* Upload Results */}
      {uploadResults && (
        <Alert
          severity={uploadResults.summary.failed === 0 ? "success" : "warning"}
          sx={{ mb: 3 }}
        >
          <Typography variant="body1" gutterBottom>
            <strong>{uploadResults.message}</strong>
          </Typography>
          <Typography variant="body2">
            - Successful: {uploadResults.summary.successful}
            <br />- Failed: {uploadResults.summary.failed}
            <br />- Total Chunks: {uploadResults.summary.total_chunks_created}
            <br />- Total Size: {uploadResults.summary.total_size_mb.toFixed(
              2
            )}{" "}
            MB
          </Typography>
        </Alert>
      )}
    </Box>
  );
};

export default KnowledgeBaseUpload;
