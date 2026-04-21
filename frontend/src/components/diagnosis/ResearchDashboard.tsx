import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Paper,
  Chip,
  List,
  ListItem,
  ListItemText,
  Divider,
  CircularProgress,
  Button,
  Stack,
  Alert,
  IconButton,
  Skeleton,
} from '@mui/material';
import {
  Science as ResearchIcon,
  AutoAwesome as AutoAwesomeIcon,
  OpenInNew as OpenIcon,
  Refresh as RefreshIcon,
} from '@mui/icons-material';
import apiClient from '../../services/apiClient';

interface Paper {
  title: string;
  authors: string[];
  journal: string;
  date: string;
  abstract: string;
  url: string;
}

interface ResearchDashboardProps {
  topic: string;
  diagnosis: string;
}

export const ResearchDashboard: React.FC<ResearchDashboardProps> = ({
  topic,
  diagnosis,
}) => {
  const [papers, setPapers] = useState<Paper[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchResearch = async () => {
    if (!diagnosis && !topic) return;
    
    setLoading(true);
    setError(null);
    try {
      const searchTerm = diagnosis || topic;
      const response = await apiClient.get('/api/medical/knowledge/pubmed-latest', {
        params: {
          topic: searchTerm,
          max_results: 5,
        }
      });
      setPapers(response.data.papers || []);
    } catch (err) {
      console.error('Error fetching research:', err);
      setError('Failed to load latest research papers.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchResearch();
  }, [diagnosis, topic]);

  if (!diagnosis && !topic) {
    return (
      <Paper elevation={3} sx={{ p: 3, bgcolor: 'grey.50', borderStyle: 'dashed', borderWidth: 2 }}>
        <Typography color="text.secondary" align="center">
          Enter a diagnosis to see latest medical research
        </Typography>
      </Paper>
    );
  }

  return (
    <Paper elevation={3} sx={{ p: 3, borderTop: '4px solid #9c27b0' }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Box sx={{ display: 'flex', alignItems: 'center' }}>
          <ResearchIcon color="secondary" sx={{ mr: 1 }} />
          <Typography variant="h6">Latest Evidence-Based Research</Typography>
        </Box>
        <IconButton size="small" onClick={fetchResearch} disabled={loading}>
          <RefreshIcon fontSize="small" />
        </IconButton>
      </Box>

      {loading ? (
        <List sx={{ px: 0 }}>
          {[1, 2, 3].map((i) => (
            <Box key={i} sx={{ mb: 3 }}>
              <Skeleton variant="text" width="80%" height={24} sx={{ mb: 1 }} />
              <Skeleton variant="text" width="40%" height={16} sx={{ mb: 1 }} />
              <Skeleton variant="rectangular" height={60} sx={{ borderRadius: 1 }} />
            </Box>
          ))}
        </List>
      ) : error ? (
        <Alert severity="error">{error}</Alert>
      ) : papers.length === 0 ? (
        <Typography variant="body2" color="text.secondary">
          No recent papers found for "{diagnosis || topic}".
        </Typography>
      ) : (
        <List sx={{ px: 0 }}>
          {papers.map((paper, index) => (
            <React.Fragment key={index}>
              <ListItem alignItems="flex-start" sx={{ px: 0 }}>
                <ListItemText
                  primary={
                    <Typography variant="subtitle2" fontWeight={700} gutterBottom>
                      {paper.title}
                    </Typography>
                  }
                  secondary={
                    <Box>
                      <Typography variant="caption" display="block" color="text.secondary">
                        {paper.journal} • {paper.date}
                      </Typography>
                      <Typography
                        variant="body2"
                        sx={{
                          mt: 1,
                          display: '-webkit-box',
                          WebkitLineClamp: 2,
                          WebkitBoxOrient: 'vertical',
                          overflow: 'hidden',
                        }}
                      >
                        {paper.abstract}
                      </Typography>
                      <Button
                        size="small"
                        startIcon={<OpenIcon />}
                        href={paper.url}
                        target="_blank"
                        sx={{ mt: 1, textTransform: 'none' }}
                      >
                        Read Full Paper
                      </Button>
                    </Box>
                  }
                />
              </ListItem>
              {index < papers.length - 1 && <Divider component="li" />}
            </React.Fragment>
          ))}
        </List>
      )}

      <Box sx={{ mt: 2, p: 2, bgcolor: 'purple.50', borderRadius: 1, border: '1px solid', borderColor: 'purple.100' }}>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
          <AutoAwesomeIcon sx={{ fontSize: 16, color: 'purple.700', mr: 1 }} />
          <Typography variant="caption" fontWeight={700} color="purple.700">
            AUTONOMOUS AGENT INSIGHT
          </Typography>
        </Box>
        <Typography variant="caption" color="purple.900">
          The AI agent is continuously monitoring these topics. New findings are automatically indexed into your local knowledge base.
        </Typography>
      </Box>
    </Paper>
  );
};
