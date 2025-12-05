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
} from '@mui/icons-material'
import apiClient from '../services/apiClient'
import { ImageViewer } from '../components/ImageViewer'

interface SearchResult {
  content: string
  metadata: {
    source: string
    page?: number
  }
  relevance: number
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
}

export default function KnowledgeBase() {
  const [searchQuery, setSearchQuery] = useState('')
  const [searching, setSearching] = useState(false)
  const [results, setResults] = useState<SearchResult[]>([])
  const [imageResults, setImageResults] = useState<ImageResult[]>([])
  const [verification, setVerification] = useState<VerificationResult | null>(null)
  const [knowledgeStats, setKnowledgeStats] = useState<KnowledgeStats | null>(null)
  const [statsLoading, setStatsLoading] = useState(true)
  const [includeImages, setIncludeImages] = useState(true)
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
  }, []) // Load stats on mount

  const handleSearch = async () => {
    if (!searchQuery.trim()) return

    setSearching(true)
    try {
      const response = await apiClient.post('/api/medical/knowledge/search/enhanced', {
        query: searchQuery,
        top_k: 5,
        include_images: includeImages,
        verify_online: verifyOnline,
      })

      setResults(response.data.text_results || [])
      setImageResults(response.data.image_results || [])
      setVerification(response.data.verification || null)
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
          {/* Categories Card */}
          <Grid item xs={12} md={4}>
            <Card elevation={2}>
              <CardContent>
                <Box display="flex" alignItems="center" gap={1} mb={1}>
                  <AssessmentIcon color="warning" />
                  <Typography variant="h6">Categories</Typography>
                </Box>
                <Typography variant="h3" color="warning.main">
                  {knowledgeStats.categories_count || 0}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  Document categories
                </Typography>
              </CardContent>
            </Card>
          </Grid>
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

        <Box display="flex" gap={2} mb={3}>
          <FormControlLabel
            control={
              <Switch
                checked={includeImages}
                onChange={(e) => setIncludeImages(e.target.checked)}
              />
            }
            label="Include images"
          />
          <FormControlLabel
            control={
              <Switch
                checked={verifyOnline}
                onChange={(e) => setVerifyOnline(e.target.checked)}
              />
            }
            label="Verify online"
          />
        </Box>

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
                <ul style={{ margin: '4px 0', paddingLeft: '20px' }}>
                  {verification.concerns.map((concern, idx) => (
                    <li key={idx}><Typography variant="caption">{concern}</Typography></li>
                  ))}
                </ul>
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
                  <img
                    src={img.path}
                    alt={img.caption || `Image ${idx + 1}`}
                    loading="lazy"
                    style={{ height: '200px', objectFit: 'cover' }}
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

        {results.length > 0 && (
          <Box>
            <Typography variant="h6" gutterBottom>
              Text Results ({results.length})
            </Typography>
            <List>
              {results.map((result, index) => {
                // Handle different response formats
                const metadata = result.metadata || {};
                const source = result.source || metadata.source || result.filename || metadata.filename || 'Unknown Source';
                const page = result.page_number || result.page || metadata.page || metadata.page_number;
                const relevance = result.score || result.similarity_score || result.relevance || 0;
                const text = result.chunk_text || result.content || result.text || '';
                
                return (
                  <Box key={index}>
                    <ListItem alignItems="flex-start">
                      <DocIcon sx={{ mr: 2, mt: 1, color: 'primary.main' }} />
                      <ListItemText
                        primary={
                          <Box display="flex" alignItems="center" gap={1}>
                            <Typography variant="subtitle2">
                              {source}
                            </Typography>
                            {page && (
                              <Chip label={`Page ${page}`} size="small" />
                            )}
                            <Chip
                              label={`${Math.round(relevance * 100)}% relevant`}
                              size="small"
                              color="primary"
                            />
                          </Box>
                        }
                        secondary={
                          <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                            {text}
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
