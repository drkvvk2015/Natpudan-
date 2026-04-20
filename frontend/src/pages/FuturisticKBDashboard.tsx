import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  Grid,
  Card,
  CardContent,
  LinearProgress,
  Chip,
  Alert,
  Button,
  TextField,
  List,
  ListItem,
  ListItemText,
  Divider,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Tooltip,
  Fade,
  CircularProgress
} from '@mui/material';
import {
  ExpandMore as ExpandMoreIcon,
  Psychology as PsychologyIcon,
  AutoGraph as AutoGraphIcon,
  NetworkCheck as NetworkCheckIcon,
  Science as ScienceIcon,
  SmartToy as SmartToyIcon,
  TrendingUp as TrendingUpIcon,
  Warning as WarningIcon,
  CheckCircle as CheckCircleIcon
} from '@mui/icons-material';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer, AreaChart, Area } from 'recharts';
import apiClient from '../services/apiClient';

interface QuantumStats {
  total_documents: number;
  holographic_memory_size: number;
  average_uncertainty: number;
  average_coherence: number;
  entanglement_pairs: number;
  queries_served: number;
  memory_utilization: number;
}

interface NeuralStats {
  total_nodes: number;
  total_edges: number;
  node_types: Record<string, number>;
  relation_types: Record<string, number>;
  average_degree: number;
  embedding_dim: number;
  gnn_layers: number;
  cached_paths: number;
}

interface PredictiveStats {
  topics_tracked: number;
  emerging_signals: number;
  seasonal_patterns: number;
  forecasts_made: number;
  last_analysis: string;
}

interface AgentStatus {
  state: {
    total_tasks: number;
    successful_tasks: number;
    knowledge_added: number;
    learning_iterations: number;
  };
  queue_size: number;
  completed_tasks: number;
  total_findings: number;
  is_active: boolean;
}

interface GrowthMetrics {
  timestamp: string;
  kb: any;
  gaps: any;
  ingestion: any;
  graph: any;
  futuristic: {
    quantum: QuantumStats;
    neural: NeuralStats;
    predictive: PredictiveStats;
    autonomous: AgentStatus;
  };
}

interface EmergingTopic {
  topic: string;
  current_demand: number;
  predicted_demand: number;
  trend: string;
  confidence: number;
  urgency: number;
  action: string;
}

interface Forecast {
  forecast_timestamp: string;
  emerging_topics: EmergingTopic[];
  critical_gaps: any[];
  seasonal_patterns: any;
}

const FuturisticKBDashboard: React.FC = () => {
  const [metrics, setMetrics] = useState<GrowthMetrics | null>(null);
  const [forecast, setForecast] = useState<Forecast | null>(null);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<any[]>([]);
  const [agentTriggering, setAgentTriggering] = useState(false);

  const fetchMetrics = async () => {
    try {
      const response = await apiClient.get('/api/kb-growth/metrics');
      setMetrics(response.data);
    } catch (error) {
      console.error('Failed to fetch metrics:', error);
    }
  };

  const fetchForecast = async () => {
    try {
      const response = await apiClient.get('/api/futuristic-kb/predictive-forecast');
      setForecast(response.data);
    } catch (error) {
      console.error('Failed to fetch forecast:', error);
    }
  };

  const handleQuantumSearch = async () => {
    if (!searchQuery) return;
    try {
      const response = await apiClient.post('/api/futuristic-kb/quantum-search', { query: searchQuery, top_k: 10 });
      setSearchResults(response.data.results || []);
    } catch (error) {
      console.error('Quantum search failed:', error);
    }
  };

  const triggerAgent = async () => {
    setAgentTriggering(true);
    try {
      await apiClient.post('/api/futuristic-kb/agent/trigger-cycle');
      setTimeout(fetchMetrics, 2000);
    } catch (error) {
      console.error('Failed to trigger agent:', error);
    } finally {
      setAgentTriggering(false);
    }
  };

  useEffect(() => {
    const loadData = async () => {
      await Promise.all([fetchMetrics(), fetchForecast()]);
      setLoading(false);
    };
    loadData();

    const interval = setInterval(fetchMetrics, 30000);
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <Box sx={{ p: 4, textAlign: 'center' }}>
        <CircularProgress size={60} />
        <Typography sx={{ mt: 2 }}>Loading Quantum Knowledge Systems...</Typography>
      </Box>
    );
  }

  const quantum = metrics?.futuristic?.quantum;
  const neural = metrics?.futuristic?.neural;
  const predictive = metrics?.futuristic?.predictive;
  const agent = metrics?.futuristic?.autonomous;

  return (
    <Fade in>
      <Box sx={{ p: 3 }}>
        <Typography variant="h4" sx={{ mb: 3, fontWeight: 'bold', display: 'flex', alignItems: 'center', gap: 1 }}>
          <PsychologyIcon sx={{ fontSize: 40, color: 'primary.main' }} />
          Quantum Knowledge Intelligence
        </Typography>

        {/* Status Overview */}
        <Grid container spacing={3} sx={{ mb: 4 }}>
          <Grid item xs={12} md={3}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                  <ScienceIcon color="primary" />
                  <Typography variant="h6">Quantum Engine</Typography>
                </Box>
                <Typography variant="h3" color="primary">{quantum?.total_documents || 0}</Typography>
                <Typography color="text.secondary">Indexed Documents</Typography>
                <LinearProgress
                  variant="determinate"
                  value={(quantum?.average_coherence || 0) * 100}
                  sx={{ mt: 1 }}
                />
                <Typography variant="caption">
                  Coherence: {((quantum?.average_coherence || 0) * 100).toFixed(1)}%
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={3}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                  <NetworkCheckIcon color="secondary" />
                  <Typography variant="h6">Neural Graph</Typography>
                </Box>
                <Typography variant="h3" color="secondary">{neural?.total_nodes || 0}</Typography>
                <Typography color="text.secondary">Connected Nodes</Typography>
                <Box sx={{ mt: 1 }}>
                  <Chip
                    size="small"
                    label={`${neural?.total_edges || 0} edges`}
                    color="secondary"
                    variant="outlined"
                  />
                </Box>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={3}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                  <AutoGraphIcon color="info" />
                  <Typography variant="h6">Predictive AI</Typography>
                </Box>
                <Typography variant="h3" color="info.main">{predictive?.topics_tracked || 0}</Typography>
                <Typography color="text.secondary">Topics Tracked</Typography>
                <Box sx={{ mt: 1 }}>
                  <Chip
                    size="small"
                    label={`${forecast?.emerging_topics?.length || 0} emerging`}
                    color="warning"
                    variant="outlined"
                  />
                </Box>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} md={3}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                  <SmartToyIcon color={agent?.is_active ? "success" : "disabled"} />
                  <Typography variant="h6">Auto Agent</Typography>
                </Box>
                <Typography variant="h3" color={agent?.is_active ? "success.main" : "text.secondary"}>
                  {agent?.state?.successful_tasks || 0}
                </Typography>
                <Typography color="text.secondary">Tasks Completed</Typography>
                <Box sx={{ mt: 1 }}>
                  <Button
                    size="small"
                    variant="outlined"
                    onClick={triggerAgent}
                    disabled={agentTriggering}
                  >
                    {agentTriggering ? 'Running...' : 'Trigger Cycle'}
                  </Button>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        {/* Quantum Search */}
        <Paper sx={{ p: 3, mb: 3 }}>
          <Typography variant="h5" sx={{ mb: 2, display: 'flex', alignItems: 'center', gap: 1 }}>
            <ScienceIcon />
            Quantum-Inspired Search
          </Typography>
          <Box sx={{ display: 'flex', gap: 2, mb: 2 }}>
            <TextField
              fullWidth
              label="Enter medical query"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleQuantumSearch()}
            />
            <Button variant="contained" onClick={handleQuantumSearch}>
              Search
            </Button>
          </Box>

          {searchResults.length > 0 && (
            <Box sx={{ mt: 2 }}>
              <Typography variant="subtitle2" gutterBottom>
                Quantum Results (with uncertainty measures):
              </Typography>
              <List>
                {searchResults.map((result, idx) => (
                  <ListItem key={idx} sx={{ bgcolor: 'background.default', mb: 1, borderRadius: 1 }}>
                    <ListItemText
                      primary={result.content?.substring(0, 100) + '...'}
                      secondary={
                        <Box sx={{ display: 'flex', gap: 1, mt: 0.5, flexWrap: 'wrap' }}>
                          <Chip size="small" label={`Score: ${(result.score * 100).toFixed(1)}%`} />
                          <Chip size="small" label={`Uncertainty: ${(result.quantum_properties?.uncertainty * 100).toFixed(1)}%`} color="info" />
                          <Chip size="small" label={`Coherence: ${(result.quantum_properties?.coherence * 100).toFixed(1)}%`} color="success" />
                          {result.quantum_properties?.entangled_with?.length > 0 && (
                            <Chip size="small" label={`Entangled: ${result.quantum_properties.entangled_with.length}`} color="secondary" />
                          )}
                        </Box>
                      }
                    />
                  </ListItem>
                ))}
              </List>
            </Box>
          )}
        </Paper>

        {/* Predictive Forecast */}
        {forecast && forecast.emerging_topics?.length > 0 && (
          <Paper sx={{ p: 3, mb: 3 }}>
            <Typography variant="h5" sx={{ mb: 2, display: 'flex', alignItems: 'center', gap: 1 }}>
              <TrendingUpIcon />
              Predictive Forecast
            </Typography>
            <Alert severity="info" sx={{ mb: 2 }}>
              AI predicts these knowledge areas will see increased demand
            </Alert>
            <Grid container spacing={2}>
              {forecast.emerging_topics.slice(0, 6).map((topic, idx) => (
                <Grid item xs={12} md={6} key={idx}>
                  <Card variant="outlined">
                    <CardContent>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                        <Typography variant="h6">{topic.topic}</Typography>
                        <Chip
                          size="small"
                          label={topic.trend}
                           color={topic.trend === 'increasing' ? 'success' : 'default'}
                        />
                      </Box>
                      <LinearProgress
                        variant="determinate"
                        value={topic.urgency * 100}
                        color={topic.urgency > 0.7 ? 'error' : 'primary'}
                        sx={{ mb: 1 }}
                      />
                      <Typography variant="caption" color="text.secondary">
                        Urgency: {(topic.urgency * 100).toFixed(0)}% |
                        Confidence: {(topic.confidence * 100).toFixed(0)}%
                      </Typography>
                      <Typography variant="body2" sx={{ mt: 1, fontSize: '0.875rem' }}>
                        {topic.action}
                      </Typography>
                    </CardContent>
                  </Card>
                </Grid>
              ))}
            </Grid>
          </Paper>
        )}

        {/* Detailed Components */}
        <Accordion defaultExpanded>
          <AccordionSummary expandIcon={<ExpandMoreIcon />}>
            <Typography variant="h6" sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <ScienceIcon /> Quantum KB Statistics
            </Typography>
          </AccordionSummary>
          <AccordionDetails>
            <Grid container spacing={2}>
              <Grid item xs={6} md={3}>
                <Paper sx={{ p: 2, textAlign: 'center' }}>
                  <Typography variant="h4">{quantum?.entanglement_pairs || 0}</Typography>
                  <Typography color="text.secondary">Entangled Pairs</Typography>
                </Paper>
              </Grid>
              <Grid item xs={6} md={3}>
                <Paper sx={{ p: 2, textAlign: 'center' }}>
                  <Typography variant="h4">{quantum?.queries_served || 0}</Typography>
                  <Typography color="text.secondary">Queries Served</Typography>
                </Paper>
              </Grid>
              <Grid item xs={6} md={3}>
                <Paper sx={{ p: 2, textAlign: 'center' }}>
                  <Typography variant="h4">{(quantum?.memory_utilization || 0).toFixed(2)}</Typography>
                  <Typography color="text.secondary">Memory Utilization</Typography>
                </Paper>
              </Grid>
              <Grid item xs={6} md={3}>
                <Paper sx={{ p: 2, textAlign: 'center' }}>
                  <Typography variant="h4">{quantum?.holographic_memory_size || 0}</Typography>
                  <Typography color="text.secondary">Holographic Dim</Typography>
                </Paper>
              </Grid>
            </Grid>
          </AccordionDetails>
        </Accordion>

        <Accordion>
          <AccordionSummary expandIcon={<ExpandMoreIcon />}>
            <Typography variant="h6" sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <NetworkCheckIcon /> Neural Graph Statistics
            </Typography>
          </AccordionSummary>
          <AccordionDetails>
            <Grid container spacing={2}>
              <Grid item xs={6} md={3}>
                <Paper sx={{ p: 2, textAlign: 'center' }}>
                  <Typography variant="h4">{neural?.total_nodes || 0}</Typography>
                  <Typography color="text.secondary">Total Nodes</Typography>
                </Paper>
              </Grid>
              <Grid item xs={6} md={3}>
                <Paper sx={{ p: 2, textAlign: 'center' }}>
                  <Typography variant="h4">{neural?.total_edges || 0}</Typography>
                  <Typography color="text.secondary">Total Edges</Typography>
                </Paper>
              </Grid>
              <Grid item xs={6} md={3}>
                <Paper sx={{ p: 2, textAlign: 'center' }}>
                  <Typography variant="h4">{(neural?.average_degree || 0).toFixed(2)}</Typography>
                  <Typography color="text.secondary">Avg Degree</Typography>
                </Paper>
              </Grid>
              <Grid item xs={6} md={3}>
                <Paper sx={{ p: 2, textAlign: 'center' }}>
                  <Typography variant="h4">{neural?.cached_paths || 0}</Typography>
                  <Typography color="text.secondary">Cached Paths</Typography>
                </Paper>
              </Grid>
            </Grid>
            <Box sx={{ mt: 2 }}>
              <Typography variant="subtitle2" gutterBottom>Node Types:</Typography>
              <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                {Object.entries(neural?.node_types || {}).map(([type, count]) => (
                  <Chip key={type} label={`${type}: ${count}`} variant="outlined" />
                ))}
              </Box>
            </Box>
          </AccordionDetails>
        </Accordion>

        <Accordion>
          <AccordionSummary expandIcon={<ExpandMoreIcon />}>
            <Typography variant="h6" sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <SmartToyIcon /> Autonomous Agent Status
            </Typography>
          </AccordionSummary>
          <AccordionDetails>
            <Grid container spacing={2}>
              <Grid item xs={6} md={3}>
                <Paper sx={{ p: 2, textAlign: 'center' }}>
                  <Typography variant="h4">{agent?.state?.total_tasks || 0}</Typography>
                  <Typography color="text.secondary">Total Tasks</Typography>
                </Paper>
              </Grid>
              <Grid item xs={6} md={3}>
                <Paper sx={{ p: 2, textAlign: 'center' }}>
                  <Typography variant="h4">{agent?.state?.successful_tasks || 0}</Typography>
                  <Typography color="text.secondary">Successful</Typography>
                </Paper>
              </Grid>
              <Grid item xs={6} md={3}>
                <Paper sx={{ p: 2, textAlign: 'center' }}>
                  <Typography variant="h4">{agent?.state?.knowledge_added || 0}</Typography>
                  <Typography color="text.secondary">KB Entries</Typography>
                </Paper>
              </Grid>
              <Grid item xs={6} md={3}>
                <Paper sx={{ p: 2, textAlign: 'center' }}>
                  <Typography variant="h4">{agent?.state?.learning_iterations || 0}</Typography>
                  <Typography color="text.secondary">Learning Iter</Typography>
                </Paper>
              </Grid>
            </Grid>
            <Box sx={{ mt: 2, display: 'flex', gap: 2 }}>
              <Chip
                icon={agent?.is_active ? <CheckCircleIcon /> : <WarningIcon />}
                label={agent?.is_active ? 'Active' : 'Inactive'}
                color={agent?.is_active ? 'success' : 'warning'}
              />
              <Chip label={`Queue: ${agent?.queue_size || 0}`} variant="outlined" />
              <Chip label={`Completed: ${agent?.completed_tasks || 0}`} variant="outlined" />
            </Box>
          </AccordionDetails>
        </Accordion>

        <Box sx={{ mt: 3, p: 2, bgcolor: 'background.default', borderRadius: 2 }}>
          <Typography variant="caption" color="text.secondary">
            Last updated: {metrics?.timestamp ? new Date(metrics.timestamp).toLocaleString() : 'Unknown'}
          </Typography>
        </Box>
      </Box>
    </Fade>
  );
};

export default FuturisticKBDashboard;
