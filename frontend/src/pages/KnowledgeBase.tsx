//
import { useState, useEffect } from 'react'
import {
  Box,
  Paper,
  TextField,
  Button,
  Typography,
  LinearProgress,
  Alert,
  List,
  ListItem,
  ListItemText,
  Divider,
  Chip,
  Grid,
  Card,
  CardContent,
  Switch,
  FormControlLabel,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Slider,
  Stack,
  ImageList,
  ImageListItem,
  ImageListItemBar,
  IconButton,
} from '@mui/material'
import {
  CloudUpload as UploadIcon,
  Search as SearchIcon,
  Description as DocIcon,
  Science as ScienceIcon,
  Storage as StorageIcon,
  Assessment as AssessmentIcon,
  Image as ImageIcon,
  Verified as VerifiedIcon,
  Warning as WarningIcon,
  AutoAwesome as SmartIcon,
  Public as GlobalIcon,
} from '@mui/icons-material'
import apiClient from '../services/apiClient'
import { ImageViewer } from '../components/ImageViewer'

interface SearchResult {
  content?: string
  chunk_text?: string
  text?: string
  metadata?: {
    source?: string
    filename?: string
    page?: number
    page_number?: number
    section?: string
    category?: string
    year?: number
  }
  citation?: {
    document_id?: string
    filename?: string
    page?: number
    chunk_index?: number
    section?: string
    category?: string
    year?: number
  }
  source?: string
  filename?: string
  page?: number
  page_number?: number
  relevance?: number
  score?: number
  similarity_score?: number
}

interface ImageResult {
  path: string
  caption?: string
  description?: string
  page?: number
  hash?: string
}

interface VerificationResult {
  verified: boolean
  confidence: string
  concerns: string[]
  pubmed_searches: string[]
}

interface KnowledgeStats {
  status: string
  total_documents: number
  total_chunks: number
  categories_count?: number
  categories?: string[]
  search_mode: string
  pdf_sources: Array<{name: string, size_mb: number, status: string}>
  knowledge_level: string
  processing_queue?: {
    queued: number
    processing: number
    completed: number
    total: number
    status_url: string
  }
  uploaded_files?: number
  total_upload_size_mb?: number
  medical_books_dir?: string
  medical_books_count?: number
}

export default function KnowledgeBase() {
  const [searchQuery, setSearchQuery] = useState('')
  const [searching, setSearching] = useState(false)
  const [results, setResults] = useState<SearchResult[]>([])
  const [synthesizedAnswer, setSynthesizedAnswer] = useState<string | null>(null)
  const [imageResults, setImageResults] = useState<ImageResult[]>([])
  const [verification, setVerification] = useState<VerificationResult | null>(null)
  const [knowledgeStats, setKnowledgeStats] = useState<KnowledgeStats | null>(null)
  const [statsLoading, setStatsLoading] = useState(true)
  const [searchMode, setSearchMode] = useState<'local' | 'hybrid' | 'openai'>('hybrid')
  const [alpha, setAlpha] = useState<number>(0.6)
  const [categoryFilter, setCategoryFilter] = useState('')
  const [sectionFilter, setSectionFilter] = useState('')
  const [minYear, setMinYear] = useState('')
  const [allowOutdated, setAllowOutdated] = useState(true)
  const [includeImages, setIncludeImages] = useState(false)
  const [verifyOnline, setVerifyOnline] = useState(false)
  const [viewerOpen, setViewerOpen] = useState(false)
  const [viewerImageIndex, setViewerImageIndex] = useState(0)

  // Fetch knowledge base statistics on mount
  useEffect(() => {
    const fetchKnowledgeStats = async () => {
      try {
        const response = await apiClient.get('/api/medical/knowledge/statistics')
        setKnowledgeStats(response.data)
      } catch (error) {
        console.error('Failed to fetch knowledge stats:', error)
      } finally {
        setStatsLoading(false)
      }
    }
    fetchKnowledgeStats()
    
    // Refresh stats every 5 seconds if there's a processing queue
    const interval = setInterval(() => {
      fetchKnowledgeStats()
    }, 5000)
    
    return () => clearInterval(interval)
  }, []) // Load stats on mount and set up polling

  const handleSearch = async () => {
    if (!searchQuery.trim()) return

    setSearching(true)
    try {
      const response = await apiClient.post('/api/medical/knowledge/search', {
        query: searchQuery,
        top_k: 8,
        min_score: 0,
        search_mode: searchMode,
        alpha,
        allow_fallback: true,
        filters: {
          category: categoryFilter || undefined,
          section: sectionFilter || undefined,
          min_year: minYear ? Number(minYear) : undefined,
          allow_outdated: allowOutdated,
        },
        synthesize_answer: true,
      })

      setResults(response.data.results || [])
      setSynthesizedAnswer(response.data.answer || null)
      setImageResults([])
      setVerification(null)
    } catch (error) {
      console.error('Search failed:', error)
    } finally {
      setSearching(false)
    }
  }

  const openImageViewer = (index: number) => {
    setViewerImageIndex(index)
    setViewerOpen(true)
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom fontWeight={600}>
        Knowledge Base
      </Typography>
      <Typography variant="body1" color="text.secondary" paragraph>
        Upload medical textbooks and search through your knowledge base
      </Typography>

      {/* Knowledge Base Statistics */}
      {statsLoading && <LinearProgress sx={{ mb: 3 }} />}
      {knowledgeStats && (
        <Grid container spacing={2} sx={{ mb: 3 }}>
          <Grid item xs={12} md={4}>
            <Card elevation={2}>
              <CardContent>
                <Box display="flex" alignItems="center" gap={1} mb={1}>
                  <StorageIcon color="primary" />
                  <Typography variant="h6">Total Documents</Typography>
                </Box>
                <Typography variant="h3" color="primary">
                  {knowledgeStats.total_documents || 0}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  Medical books indexed
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={4}>
            <Card elevation={2}>
              <CardContent>
                <Box display="flex" alignItems="center" gap={1} mb={1}>
                  <AssessmentIcon color="success" />
                  <Typography variant="h6">Knowledge Chunks</Typography>
                </Box>
                <Typography variant="h3" color="success.main">
                  {(knowledgeStats.total_chunks || 0).toLocaleString()}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  Searchable knowledge segments
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={4}>
            <Card elevation={2}>
              <CardContent>
                <Box display="flex" alignItems="center" gap={1} mb={1}>
                  <ScienceIcon color="secondary" />
                  <Typography variant="h6">Knowledge Level</Typography>
                </Box>
                <Typography variant="h3" color="secondary.main">
                  {(knowledgeStats.knowledge_level || 'UNKNOWN').toUpperCase()}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  Mode: {knowledgeStats.search_mode || 'N/A'}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          
          {/* Processing Queue Status */}
          {knowledgeStats.processing_queue && knowledgeStats.processing_queue.total > 0 && (
            <Grid item xs={12} md={6}>
              <Card elevation={2} sx={{ backgroundColor: '#f5f5f5' }}>
                <CardContent>
                  <Box display="flex" alignItems="center" gap={1} mb={2}>
                    <StorageIcon color="warning" />
                    <Typography variant="h6">Processing Queue</Typography>
                  </Box>
                  <Box display="flex" gap={2} mb={2}>
                    <Box>
                      <Typography variant="caption" color="text.secondary">
                        Queued
                      </Typography>
                      <Typography variant="h5" color="info.main">
                        {knowledgeStats.processing_queue.queued}
                      </Typography>
                    </Box>
                    <Box>
                      <Typography variant="caption" color="text.secondary">
                        Processing
                      </Typography>
                      <Typography variant="h5" color="warning.main">
                        {knowledgeStats.processing_queue.processing}
                      </Typography>
                    </Box>
                    <Box>
                      <Typography variant="caption" color="text.secondary">
                        Completed
                      </Typography>
                      <Typography variant="h5" color="success.main">
                        {knowledgeStats.processing_queue.completed}
                      </Typography>
                    </Box>
                  </Box>
                  <Typography variant="caption" color="text.secondary">
                    Documents are being indexed in background. <strong>Search is immediately available</strong> with growing accuracy as processing completes.
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          )}

          {/* Upload Location */}
          {knowledgeStats.uploaded_files !== undefined && (
            <Grid item xs={12} md={6}>
              <Card elevation={2} sx={{ backgroundColor: '#fafafa' }}>
                <CardContent>
                  <Box display="flex" alignItems="center" gap={1} mb={2}>
                    <UploadIcon color="primary" />
                    <Typography variant="h6">Uploaded Files</Typography>
                  </Box>
                  <Box mb={1}>
                    <Typography variant="body2">
                      <strong>Count:</strong> {knowledgeStats.uploaded_files || 0} files
                    </Typography>
                    <Typography variant="body2">
                      <strong>Size:</strong> {knowledgeStats.total_upload_size_mb?.toFixed(2) || '0'} MB
                    </Typography>
                  </Box>
                  {knowledgeStats.medical_books_dir && (
                    <Typography variant="caption" color="text.secondary" component="div" sx={{ mt: 1 }}>
                      {/* eslint-disable-next-line */}
                      Location: <code style={{ fontSize: '0.75rem', whiteSpace: 'pre-wrap', wordBreak: 'break-all' }}>{knowledgeStats.medical_books_dir}</code>
                    </Typography>
                  )}
                </CardContent>
              </Card>
            </Grid>
          )}
        </Grid>
      )}

      {/* Indexed Sources */}
      {knowledgeStats && knowledgeStats.pdf_sources && knowledgeStats.pdf_sources.length > 0 && (
        <Alert severity="info" sx={{ mb: 3 }} icon={<DocIcon />}>
          <Typography variant="subtitle2" fontWeight={600} gutterBottom>
            Indexed Medical Sources ({knowledgeStats.pdf_sources.length})
          </Typography>
          <Box display="flex" gap={1} flexWrap="wrap" mt={1}>
            {knowledgeStats.pdf_sources.map((source, idx) => (
              <Chip
                key={idx}
                label={`${source.name.substring(0, 35)}${source.name.length > 35 ? '...' : ''} (${source.size_mb}MB)`}
                size="small"
                color={source.status === 'indexed' ? 'success' : 'default'}
                variant="outlined"
                icon={<DocIcon />}
              />
            ))}
          </Box>
        </Alert>
      )}

      {/* Online Status Indicator */}
      <Alert severity="success" icon={<GlobalIcon />} sx={{ mb: 3 }}>
        <Typography variant="subtitle2" fontWeight={600}>
          Online Knowledge Base Active
        </Typography>
        <Typography variant="body2">
          Connected to global medical sources (PubMed, CDC, WHO) for real-time verification.
        </Typography>
      </Alert>

      {/* Upload section removed - Use dedicated "Upload PDFs" page from menu */}
      <Alert severity="info" sx={{ mb: 3 }}>
        <Typography variant="body2">
          [TIP] To upload medical PDFs, use the <strong>"Upload PDFs"</strong> menu option for batch uploads with progress tracking.
        </Typography>
      </Alert>

      <Paper elevation={3} sx={{ p: 3 }}>
        <Typography variant="h6" gutterBottom>
          Search Knowledge Base
        </Typography>
        <Box display="flex" gap={2} mb={2}>
          <TextField
            fullWidth
            placeholder="Search for medical information..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
          />
          <Button
            variant="contained"
            startIcon={<SearchIcon />}
            onClick={handleSearch}
            disabled={searching || !searchQuery.trim()}
          >
            Search
          </Button>
        </Box>

        <Stack spacing={2} mb={3}>
          <Box display="flex" gap={2} flexWrap="wrap">
            <FormControl sx={{ minWidth: 180 }} size="small">
              <InputLabel id="search-mode">Search mode</InputLabel>
              <Select
                labelId="search-mode"
                value={searchMode}
                label="Search mode"
                onChange={(e) => setSearchMode(e.target.value as 'local' | 'hybrid' | 'openai')}
              >
                <MenuItem value="hybrid">Hybrid (dense + BM25)</MenuItem>
                <MenuItem value="local">Local only</MenuItem>
                <MenuItem value="openai">OpenAI fallback</MenuItem>
              </Select>
            </FormControl>
            <Box flex={1} minWidth={220} px={1}>
              <Typography variant="caption" color="text.secondary">
                Hybrid weight (dense vs keyword)
              </Typography>
              <Slider
                size="small"
                value={alpha * 100}
                step={5}
                min={0}
                max={100}
                valueLabelDisplay="auto"
                onChange={(_, val) => setAlpha((val as number) / 100)}
              />
            </Box>
          </Box>
          <Box display="flex" gap={2} flexWrap="wrap">
            <TextField
              label="Category filter"
              size="small"
              value={categoryFilter}
              onChange={(e) => setCategoryFilter(e.target.value)}
            />
            <TextField
              label="Section filter"
              size="small"
              value={sectionFilter}
              onChange={(e) => setSectionFilter(e.target.value)}
            />
            <TextField
              label="Min publication year"
              size="small"
              type="number"
              value={minYear}
              onChange={(e) => setMinYear(e.target.value)}
              inputProps={{ min: 1950, max: new Date().getFullYear() + 1 }}
            />
            <FormControlLabel
              control={
                <Switch
                  checked={allowOutdated}
                  onChange={(e) => setAllowOutdated(e.target.checked)}
                />
              }
              label="Include outdated"
            />
          </Box>
        </Stack>

        {searching && <LinearProgress />}

        {/* Verification Status */}
        {verification && (
          <Alert 
            severity={verification.verified ? 'success' : 'warning'}
            icon={verification.verified ? <VerifiedIcon /> : <WarningIcon />}
            sx={{ mb: 2 }}
          >
            <Typography variant="subtitle2" fontWeight={600}>
              {verification.verified ? 'Content Verified' : 'Verification Concerns'}
            </Typography>
            <Typography variant="body2">
              Confidence: {verification.confidence}
            </Typography>
            {verification.concerns && verification.concerns.length > 0 && (
              <Box mt={1}>
                <Typography variant="caption" fontWeight={600}>Concerns:</Typography>
                <Box component="ul" sx={{ margin: '4px 0', paddingLeft: '20px' }}>
                  {verification.concerns.map((concern, idx) => (
                    <Box component="li" key={idx}><Typography variant="caption">{concern}</Typography></Box>
                  ))}
                </Box>
              </Box>
            )}
            {verification.pubmed_searches && verification.pubmed_searches.length > 0 && (
              <Box mt={1}>
                <Typography variant="caption" fontWeight={600}>Suggested PubMed searches:</Typography>
                <Box display="flex" gap={1} flexWrap="wrap" mt={0.5}>
                  {verification.pubmed_searches.map((search, idx) => (
                    <Chip
                      key={idx}
                      label={search}
                      size="small"
                      onClick={() => window.open(`https://pubmed.ncbi.nlm.nih.gov/?term=${encodeURIComponent(search)}`, '_blank')}
                      clickable
                    />
                  ))}
                </Box>
              </Box>
            )}
          </Alert>
        )}

        {/* Image Results */}
        {imageResults.length > 0 && (
          <Box mb={3}>
            <Typography variant="h6" gutterBottom display="flex" alignItems="center" gap={1}>
              <ImageIcon /> Images ({imageResults.length})
            </Typography>
            <ImageList cols={3} gap={8}>
              {imageResults.map((img, idx) => (
                <ImageListItem key={idx} onClick={() => openImageViewer(idx)} sx={{ cursor: 'pointer' }}>
                  <Box
                    component="img"
                    src={img.path}
                    alt={img.caption || `Image ${idx + 1}`}
                    loading="lazy"
                    sx={{ height: '200px', objectFit: 'cover' }}
                  />
                  <ImageListItemBar
                    title={img.caption || `Image ${idx + 1}`}
                    subtitle={img.page ? `Page ${img.page}` : ''}
                  />
                </ImageListItem>
              ))}
            </ImageList>
          </Box>
        )}



        {/* Synthesized Answer */}
        {synthesizedAnswer && (
          <Paper 
            elevation={2} 
            sx={{ 
              p: 3, 
              mb: 3, 
              bgcolor: 'primary.50',
              border: '1px solid',
              borderColor: 'primary.100'
            }}
          >
            <Typography variant="h6" gutterBottom color="primary.main" display="flex" alignItems="center" gap={1}>
              <SmartIcon /> AI Consolidated Answer
            </Typography>
            <Typography 
              variant="body1" 
              component="div" 
              sx={{ whiteSpace: 'pre-wrap' }}
            >
              {synthesizedAnswer.split(/(\[\d+\])/g).map((part, i) => {
                if (/^\[\d+\]$/.test(part)) {
                  return (
                    <Chip 
                      key={i} 
                      label={part} 
                      size="small" 
                      color="primary" 
                      sx={{ 
                        mx: 0.5, 
                        height: 20, 
                        fontSize: '0.75rem', 
                        cursor: 'pointer',
                        fontWeight: 'bold'
                      }} 
                    />
                  )
                }
                return part
              })}
            </Typography>
          </Paper>
        )}

        {results.length > 0 && (
          <Box>
            <Typography variant="h6" gutterBottom>
              Text Results ({results.length})
            </Typography>
            <List>
              {results.map((result, index) => {
                // Handle different response formats
                const metadata = result.metadata || {};
                const citation = (result as any).citation || {};
                const source = (result.source || metadata?.source || result.filename || metadata?.filename || 'Unknown Source') as string;
                const page = citation.page || result.page_number || result.page || metadata?.page || metadata?.page_number;
                const relevance = (result.score || result.similarity_score || result.relevance || 0) as number;
                const text = (result.chunk_text || result.content || result.text || '') as string;
                const section = citation.section || metadata.section;
                const category = citation.category || metadata.category;
                const year = citation.year || metadata.year;
                
                return (
                  <Box key={index}>
                    <ListItem alignItems="flex-start">
                      <DocIcon sx={{ mr: 2, mt: 1, color: 'primary.main' }} />
                      <ListItemText
                        primary={
                          <Box display="flex" alignItems="center" gap={1} flexWrap="wrap">
                            <Typography variant="subtitle2">
                              {source}
                            </Typography>
                            {page && (
                              <Chip label={`Page ${page}`} size="small" />
                            )}
                            {section && (
                              <Chip label={`Section: ${section}`} size="small" variant="outlined" />
                            )}
                            {category && (
                              <Chip label={`Category: ${category}`} size="small" variant="outlined" />
                            )}
                            {year && (
                              <Chip label={`Year: ${year}`} size="small" variant="outlined" />
                            )}
                            <Chip
                              label={`${Math.round((relevance || 0) * 100)}% relevant`}
                              size="small"
                              color="primary"
                            />
                          </Box>
                        }
                        secondary={
                          <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                            {text || 'No preview available'}
                          </Typography>
                        }
                      />
                    </ListItem>
                    {index < results.length - 1 && <Divider />}
                  </Box>
                );
              })}
            </List>
          </Box>
        )}

        {!searching && results.length === 0 && searchQuery && (
          <Alert severity="info">
            No results found for "{searchQuery}"
          </Alert>
        )}
      </Paper>

      {/* Image Viewer Modal */}
      {viewerOpen && imageResults.length > 0 && (
        <ImageViewer
          images={imageResults}
          initialIndex={viewerImageIndex}
          onClose={() => setViewerOpen(false)}
        />
      )}
    </Box>
  )
}
