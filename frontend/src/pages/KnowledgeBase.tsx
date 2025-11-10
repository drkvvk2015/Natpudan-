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
} from '@mui/material'
import {
  CloudUpload as UploadIcon,
  Search as SearchIcon,
  Description as DocIcon,
  Science as ScienceIcon,
  Storage as StorageIcon,
  Assessment as AssessmentIcon,
} from '@mui/icons-material'
import axios from 'axios'

interface SearchResult {
  content: string
  metadata: {
    source: string
    page?: number
  }
  relevance: number
}

interface KnowledgeStats {
  status: string
  total_documents: number
  total_chunks: number
  search_mode: string
  pdf_sources: Array<{name: string, size_mb: number, status: string}>
  knowledge_level: string
}

export default function KnowledgeBase() {
  const [file, setFile] = useState<File | null>(null)
  const [uploading, setUploading] = useState(false)
  const [uploadSuccess, setUploadSuccess] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')
  const [searching, setSearching] = useState(false)
  const [results, setResults] = useState<SearchResult[]>([])
  const [knowledgeStats, setKnowledgeStats] = useState<KnowledgeStats | null>(null)
  const [statsLoading, setStatsLoading] = useState(true)

  // Fetch knowledge base statistics on mount
  useEffect(() => {
    const fetchKnowledgeStats = async () => {
      try {
        const response = await axios.get('/api/medical/knowledge/statistics')
        setKnowledgeStats(response.data)
      } catch (error) {
        console.error('Failed to fetch knowledge stats:', error)
      } finally {
        setStatsLoading(false)
      }
    }
    fetchKnowledgeStats()
  }, [uploadSuccess]) // Refetch when new file uploaded

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0])
      setUploadSuccess(false)
    }
  }

  const handleUpload = async () => {
    if (!file) return

    setUploading(true)
    const formData = new FormData()
    formData.append('file', file)

    try {
      await axios.post('/api/upload/pdf', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      })
      setUploadSuccess(true)
      setFile(null)
    } catch (error) {
      console.error('Upload failed:', error)
    } finally {
      setUploading(false)
    }
  }

  const handleSearch = async () => {
    if (!searchQuery.trim()) return

    setSearching(true)
    try {
      const response = await axios.post('/api/upload/search', {
        query: searchQuery,
        top_k: 5,
      })

      setResults(response.data.results || [])
    } catch (error) {
      console.error('Search failed:', error)
    } finally {
      setSearching(false)
    }
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
                  {knowledgeStats.total_documents}
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
                  {knowledgeStats.total_chunks.toLocaleString()}
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
                  {knowledgeStats.knowledge_level.toUpperCase()}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  Mode: {knowledgeStats.search_mode}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {/* Indexed Sources */}
      {knowledgeStats && knowledgeStats.pdf_sources.length > 0 && (
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

      <Paper elevation={3} sx={{ p: 3, mb: 3 }}>
        <Typography variant="h6" gutterBottom>
          Upload Medical PDF
        </Typography>
        <Box display="flex" gap={2} alignItems="center">
          <Button variant="outlined" component="label" startIcon={<UploadIcon />}>
            Choose PDF
            <input type="file" hidden accept=".pdf" onChange={handleFileChange} />
          </Button>
          {file && (
            <>
              <Chip label={file.name} onDelete={() => setFile(null)} />
              <Button
                variant="contained"
                onClick={handleUpload}
                disabled={uploading}
              >
                {uploading ? 'Uploading...' : 'Upload'}
              </Button>
            </>
          )}
        </Box>
        {uploading && <LinearProgress sx={{ mt: 2 }} />}
        {uploadSuccess && (
          <Alert severity="success" sx={{ mt: 2 }}>
            PDF uploaded and processed successfully!
          </Alert>
        )}
      </Paper>

      <Paper elevation={3} sx={{ p: 3 }}>
        <Typography variant="h6" gutterBottom>
          Search Knowledge Base
        </Typography>
        <Box display="flex" gap={2} mb={3}>
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

        {searching && <LinearProgress />}

        {results.length > 0 && (
          <Box>
            <Typography variant="subtitle1" gutterBottom>
              Found {results.length} results
            </Typography>
            <List>
              {results.map((result, index) => (
                <Box key={index}>
                  <ListItem alignItems="flex-start">
                    <DocIcon sx={{ mr: 2, mt: 1, color: 'primary.main' }} />
                    <ListItemText
                      primary={
                        <Box display="flex" alignItems="center" gap={1}>
                          <Typography variant="subtitle2">
                            {result.metadata.source}
                          </Typography>
                          {result.metadata.page && (
                            <Chip label={`Page ${result.metadata.page}`} size="small" />
                          )}
                          <Chip
                            label={`${Math.round(result.relevance * 100)}% relevant`}
                            size="small"
                            color="primary"
                          />
                        </Box>
                      }
                      secondary={
                        <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                          {result.content}
                        </Typography>
                      }
                    />
                  </ListItem>
                  {index < results.length - 1 && <Divider />}
                </Box>
              ))}
            </List>
          </Box>
        )}

        {!searching && results.length === 0 && searchQuery && (
          <Alert severity="info">
            No results found for "{searchQuery}"
          </Alert>
        )}
      </Paper>
    </Box>
  )
}
