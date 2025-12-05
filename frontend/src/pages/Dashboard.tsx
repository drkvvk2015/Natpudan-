//
import { useState, useEffect, useContext } from 'react'
import {
  Grid,
  Card,
  CardContent,
  Typography,
  Box,
  LinearProgress,
  useTheme,
  Chip,
  Alert,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
} from '@mui/material'
import {
  Memory as MemoryIcon,
  Storage as StorageIcon,
  Timer as TimerIcon,
  DeveloperBoard as CpuIcon,
  CheckCircle as CheckCircleIcon,
  Warning as WarningIcon,
  Delete as DeleteIcon,
  Schedule as ScheduleIcon,
  Check as CheckIcon,
  Error as ErrorIcon,
} from '@mui/icons-material';
import { checkDetailedHealth, type DetailedHealthStatus } from '../services/api';
import { AuthContext } from '../context/AuthContext';
import apiClient from '../services/apiClient';

interface StatCard {
  title: string;
  value: string;
  change?: string;
  icon: React.ReactNode;
  color: string;
}

export default function Dashboard() {
  const [loading, setLoading] = useState(true);
  const [health, setHealth] = useState<DetailedHealthStatus | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [resetDialogOpen, setResetDialogOpen] = useState(false);
  const [resetting, setResetting] = useState(false);
  const [resetMessage, setResetMessage] = useState('');
  const [queueStatus, setQueueStatus] = useState<any>(null);
  const [queueLoading, setQueueLoading] = useState(false);
  const theme = useTheme();
  const authContext = useContext(AuthContext);
  const userRole = authContext?.user?.role;

  useEffect(() => {
    const fetchHealth = async () => {
      try {
        const data = await checkDetailedHealth();
        setHealth(data);
        setError(null);
      } catch (err) {
        console.error('Failed to fetch detailed health status:', err);
        setError('Failed to load detailed system status');
      } finally {
        setLoading(false);
      }
    };

    fetchHealth();
  }, []);

  // Poll queue status every 5 seconds
  useEffect(() => {
    const fetchQueueStatus = async () => {
      try {
        setQueueLoading(true);
        const response = await apiClient.get('/api/medical/knowledge/queue-status');
        setQueueStatus(response.data);
      } catch (err) {
        console.error('Failed to fetch queue status:', err);
      } finally {
        setQueueLoading(false);
      }
    };

    fetchQueueStatus();
    const interval = setInterval(fetchQueueStatus, 5000);
    return () => clearInterval(interval);
  }, []);

  const handleResetKnowledgeBase = async () => {
    setResetting(true);
    setResetMessage('');
    try {
      const response = await apiClient.post('/api/medical/knowledge/reset');
      setResetMessage(`Success: Deleted ${response.data.deleted_documents} documents`);
      setResetDialogOpen(false);
      setTimeout(() => setResetMessage(''), 5000);
    } catch (err: any) {
      setResetMessage(`Error: ${err.response?.data?.detail || 'Failed to reset KB'}`);
    } finally {
      setResetting(false);
    }
  };

  const formatUptime = (seconds: number) => {
    const days = Math.floor(seconds / (24 * 3600));
    seconds %= 24 * 3600;
    const hours = Math.floor(seconds / 3600);
    seconds %= 3600;
    const minutes = Math.floor(seconds / 60);
    return `${days}d ${hours}h ${minutes}m`;
  };

  const stats: StatCard[] = health
    ? [
        {
          title: 'Uptime',
          value: health.uptime ? formatUptime(health.uptime) : 'N/A',
          icon: <TimerIcon sx={{ fontSize: 40 }} />,
          color: theme.palette.primary.main,
        },
        {
          title: 'CPU Usage',
          value: health.cpu_usage != null ? `${health.cpu_usage.toFixed(1)}%` : 'N/A',
          icon: <CpuIcon sx={{ fontSize: 40 }} />,
          color: theme.palette.success.main,
        },
        {
          title: 'Memory Usage',
          value: health.memory_usage?.percent != null ? `${health.memory_usage.percent}%` : 'N/A',
          icon: <MemoryIcon sx={{ fontSize: 40 }} />,
          color: theme.palette.warning.main,
        },
        {
          title: 'Disk Usage',
          value: health.disk_usage?.percent != null ? `${health.disk_usage.percent}%` : 'N/A',
          icon: <StorageIcon sx={{ fontSize: 40 }} />,
          color: theme.palette.secondary.main,
        },
      ]
    : [];

  const getStatusChip = (status: string) => {
    const isActive = status?.toLowerCase() === 'active'
    return (
      <Chip
        icon={isActive ? <CheckCircleIcon /> : <WarningIcon />}
        label={status?.toUpperCase() || 'ACTIVE'}
        color={isActive ? 'success' : 'warning'}
        size="small"
        sx={{
          fontWeight: 600,
          color: 'white',
          '& .MuiChip-icon': { color: 'white' },
        }}
      />
    )
  }

  if (loading) {
    return <LinearProgress />
  }

  return (
    <Box>
      <Box
        sx={{
          mb: 4,
          p: 4,
          borderRadius: 4,
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%)',
          color: 'white',
          position: 'relative',
          overflow: 'hidden',
          boxShadow: '0 8px 32px rgba(102, 126, 234, 0.3)',
          '&::before': {
            content: '""',
            position: 'absolute',
            top: '-50%',
            right: '-10%',
            width: '400px',
            height: '400px',
            borderRadius: '50%',
            background: 'radial-gradient(circle, rgba(255,255,255,0.15) 0%, transparent 70%)',
            animation: 'float 6s ease-in-out infinite',
          },
          '@keyframes float': {
            '0%, 100%': { transform: 'translate(0, 0) scale(1)' },
            '50%': { transform: 'translate(-20px, -20px) scale(1.1)' },
          },
        }}
      >
        <Box sx={{ position: 'relative', zIndex: 1 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
            <Box
              sx={{
                fontSize: '48px',
                animation: 'bounce 2s ease-in-out infinite',
                '@keyframes bounce': {
                  '0%, 100%': { transform: 'translateY(0)' },
                  '50%': { transform: 'translateY(-10px)' },
                },
              }}
            >
              [AI]
            </Box>
            <Box>
              <Typography
                variant="h3"
                sx={{
                  fontWeight: 800,
                  letterSpacing: '-0.03em',
                  mb: 1,
                  textShadow: '0 2px 12px rgba(0,0,0,0.2)',
                }}
              >
                Welcome Back, Doctor
              </Typography>
              <Typography
                variant="h6"
                sx={{
                  fontWeight: 400,
                  opacity: 0.95,
                  letterSpacing: '0.02em',
                }}
              >
                Your AI-powered medical intelligence platform is ready
              </Typography>
            </Box>
          </Box>
          <Box sx={{ display: 'flex', gap: 2, mt: 3 }}>
            <Chip
              label="[BRAIN] AI Powered"
              sx={{
                bgcolor: 'rgba(255,255,255,0.25)',
                color: 'white',
                fontWeight: 600,
                backdropFilter: 'blur(10px)',
                border: '1px solid rgba(255,255,255,0.3)',
              }}
            />
            <Chip
              label="[FAST] Real-time Analysis"
              sx={{
                bgcolor: 'rgba(255,255,255,0.25)',
                color: 'white',
                fontWeight: 600,
                backdropFilter: 'blur(10px)',
                border: '1px solid rgba(255,255,255,0.3)',
              }}
            />
            <Chip
              label="[LOCK] HIPAA Compliant"
              sx={{
                bgcolor: 'rgba(255,255,255,0.25)',
                color: 'white',
                fontWeight: 600,
                backdropFilter: 'blur(10px)',
                border: '1px solid rgba(255,255,255,0.3)',
              }}
            />
          </Box>
        </Box>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {health && (
        <Card
          sx={{
            mb: 4,
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            color: 'white',
            borderRadius: 3,
            boxShadow: '0 8px 24px rgba(102, 126, 234, 0.3)',
            border: 'none',
          }}
        >
          <CardContent>
            <Typography
              variant="h6"
              sx={{
                color: 'white',
                mb: 2,
                fontWeight: 600,
                display: 'flex',
                alignItems: 'center',
                gap: 1,
              }}
            >
              System Status
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={12} sm={4}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <Typography variant="body2" sx={{ color: 'rgba(255,255,255,0.9)' }}>
                    Database:
                  </Typography>
                  {getStatusChip(health.database_status)}
                </Box>
              </Grid>
              <Grid item xs={12} sm={4}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <Typography variant="body2" sx={{ color: 'rgba(255,255,255,0.9)' }}>
                    Cache:
                  </Typography>
                  {getStatusChip(health.cache_status)}
                </Box>
              </Grid>
              <Grid item xs={12} sm={4}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <Typography variant="body2" sx={{ color: 'rgba(255,255,255,0.9)' }}>
                    AI Assistant:
                  </Typography>
                  {getStatusChip(health.assistant_status)}
                </Box>
              </Grid>
              <Grid item xs={12} sm={4}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <Typography variant="body2" sx={{ color: 'rgba(255,255,255,0.9)' }}>
                    Knowledge Base:
                  </Typography>
                  {getStatusChip(health.knowledge_base_status)}
                </Box>
              </Grid>
            </Grid>
          </CardContent>
        </Card>
      )}

      <Grid container spacing={3}>
        {stats.map((stat) => (
          <Grid item xs={12} sm={6} md={3} key={stat.title}>
            <Card
              sx={{
                height: '100%',
                transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
                borderRadius: 3,
                background: 'linear-gradient(135deg, #ffffff 0%, #f8f9ff 100%)',
                border: '1px solid rgba(102, 126, 234, 0.1)',
                position: 'relative',
                overflow: 'hidden',
                '&::before': {
                  content: '""',
                  position: 'absolute',
                  top: 0,
                  left: 0,
                  right: 0,
                  height: '4px',
                  background: `linear-gradient(90deg, ${stat.color} 0%, transparent 100%)`,
                },
                '&:hover': {
                  transform: 'translateY(-8px) scale(1.02)',
                  boxShadow: `0 12px 24px ${stat.color}25`,
                  border: `1px solid ${stat.color}40`,
                },
              }}
            >
              <CardContent>
                <Box display="flex" justifyContent="space-between" alignItems="flex-start">
                  <Box>
                    <Typography color="text.secondary" variant="body2" gutterBottom>
                      {stat.title}
                    </Typography>
                    <Typography variant="h4" fontWeight={600}>
                      {stat.value}
                    </Typography>
                    <Typography
                      variant="body2"
                      sx={{ color: 'text.secondary', mt: 1 }}
                    >
                      {stat.change}
                    </Typography>
                  </Box>
                  <Box sx={{ color: stat.color }}>{stat.icon}</Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      <Grid container spacing={3} sx={{ mt: 2 }}>
        <Grid item xs={12} md={8}>
          <Card
            sx={{
              borderRadius: 3,
              boxShadow: '0 4px 16px rgba(0,0,0,0.08)',
              transition: 'all 0.3s',
              '&:hover': {
                boxShadow: '0 8px 24px rgba(0,0,0,0.12)',
              },
            }}
          >
            <CardContent>
              <Typography variant="h6" gutterBottom fontWeight={600}>
                Recent Activity
              </Typography>
              <Box sx={{ py: 2 }}>
                <Typography variant="body2" color="text.secondary">
                  [SEARCH] Drug interaction check: Warfarin + Aspirin (10 mins ago)
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                  [CHAT] AI consultation: Patient with chest pain (25 mins ago)
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                  [LIST] Diagnosis: Hypertension Stage 2 (1 hour ago)
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                  [BOOKS] PDF uploaded: Harrison's Internal Medicine Ch.12 (2 hours ago)
                </Typography>
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={4}>
          <Card
            sx={{
              borderRadius: 3,
              background: 'linear-gradient(135deg, #f8f9ff 0%, #ffffff 100%)',
              border: '1px solid rgba(102, 126, 234, 0.1)',
              boxShadow: '0 4px 16px rgba(0,0,0,0.08)',
              transition: 'all 0.3s',
              '&:hover': {
                boxShadow: '0 8px 24px rgba(102, 126, 234, 0.15)',
              },
            }}
          >
            <CardContent>
              <Typography variant="h6" gutterBottom fontWeight={600}>
                Quick Actions
              </Typography>
              <Box sx={{ py: 2 }}>
                <Typography variant="body2" color="primary" sx={{ cursor: 'pointer', mb: 1 }}>
                  * Start AI Chat
                </Typography>
                <Typography variant="body2" color="primary" sx={{ cursor: 'pointer', mb: 1 }}>
                  * Check Drug Interactions
                </Typography>
                <Typography variant="body2" color="primary" sx={{ cursor: 'pointer', mb: 1 }}>
                  * Upload Medical PDF
                </Typography>
                <Typography variant="body2" color="primary" sx={{ cursor: 'pointer' }}>
                  * View Knowledge Base
                </Typography>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {resetMessage && (
        <Alert severity={resetMessage.includes('Error') ? 'error' : 'success'} sx={{ mt: 3 }}>
          {resetMessage}
        </Alert>
      )}

      {/* Knowledge Base Management Section */}
      {userRole === 'admin' && queueStatus && (
        <Card sx={{ mt: 3, bgcolor: 'info.50', borderLeft: `4px solid ${theme.palette.info.main}` }}>
          <CardContent>
            <Typography variant="h6" gutterBottom fontWeight={600} color="info">
              Knowledge Base Management
            </Typography>
            
            {/* Queue Status */}
            <Box sx={{ mt: 2 }}>
              <Typography variant="subtitle2" fontWeight={600} gutterBottom>
                Upload Queue Status
              </Typography>
              <Grid container spacing={2} sx={{ mt: 0.5 }}>
                <Grid item xs={6} sm={3}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <ScheduleIcon sx={{ color: 'warning.main' }} />
                    <Box>
                      <Typography variant="caption" color="text.secondary">
                        Queued
                      </Typography>
                      <Typography variant="h6" color="warning.main">
                        {queueStatus.queue?.queued || 0}
                      </Typography>
                    </Box>
                  </Box>
                </Grid>
                <Grid item xs={6} sm={3}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <CpuIcon sx={{ color: 'primary.main' }} />
                    <Box>
                      <Typography variant="caption" color="text.secondary">
                        Processing
                      </Typography>
                      <Typography variant="h6" color="primary.main">
                        {queueStatus.queue?.processing || 0}
                      </Typography>
                    </Box>
                  </Box>
                </Grid>
                <Grid item xs={6} sm={3}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <CheckIcon sx={{ color: 'success.main' }} />
                    <Box>
                      <Typography variant="caption" color="text.secondary">
                        Completed
                      </Typography>
                      <Typography variant="h6" color="success.main">
                        {queueStatus.queue?.completed || 0}
                      </Typography>
                    </Box>
                  </Box>
                </Grid>
                <Grid item xs={6} sm={3}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <ErrorIcon sx={{ color: 'error.main' }} />
                    <Box>
                      <Typography variant="caption" color="text.secondary">
                        Failed
                      </Typography>
                      <Typography variant="h6" color="error.main">
                        {queueStatus.queue?.failed || 0}
                      </Typography>
                    </Box>
                  </Box>
                </Grid>
              </Grid>
            </Box>

            {/* Worker Status */}
            <Box sx={{ mt: 2 }}>
              <Chip 
                label={`Worker Status: ${queueStatus.worker_status?.toUpperCase() || 'UNKNOWN'}`}
                color={queueStatus.worker_status === 'running' ? 'success' : 'warning'}
                variant="outlined"
              />
            </Box>

            {/* Processing Details */}
            {queueStatus.processing_details && queueStatus.processing_details.length > 0 && (
              <Box sx={{ mt: 2 }}>
                <Typography variant="subtitle2" fontWeight={600} gutterBottom>
                  Currently Processing
                </Typography>
                {queueStatus.processing_details.map((doc: any, idx: number) => (
                  <Box key={idx} sx={{ mb: 1.5, p: 1.5, bgcolor: 'white', borderRadius: 1 }}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                      <Typography variant="body2" fontWeight={500}>
                        Doc ID: {doc.document_id?.substring(0, 8)}...
                      </Typography>
                      <Typography variant="caption" color="primary">
                        {doc.progress_percent}%
                      </Typography>
                    </Box>
                    <LinearProgress 
                      variant="determinate" 
                      value={doc.progress_percent || 0}
                      sx={{ mb: 0.5 }}
                    />
                    <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                      <Typography variant="caption" color="text.secondary">
                        {doc.current_chunk}/{doc.total_chunks} chunks
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        ~{doc.estimated_time_seconds}s remaining
                      </Typography>
                    </Box>
                  </Box>
                ))}
              </Box>
            )}
          </CardContent>
        </Card>
      )}

      {userRole === 'admin' && (
        <Card sx={{ mt: 3, bgcolor: 'error.50', borderLeft: `4px solid ${theme.palette.error.main}` }}>
          <CardContent>
            <Typography variant="h6" gutterBottom fontWeight={600} color="error">
              Admin Tools
            </Typography>
            <Typography variant="body2" color="text.secondary" paragraph>
              Dangerous operations - use with caution
            </Typography>
            <Button
              variant="contained"
              color="error"
              startIcon={<DeleteIcon />}
              onClick={() => setResetDialogOpen(true)}
            >
              Reset Knowledge Base
            </Button>
          </CardContent>
        </Card>
      )}

      <Dialog open={resetDialogOpen} onClose={() => setResetDialogOpen(false)}>
        <DialogTitle>Confirm Knowledge Base Reset</DialogTitle>
        <DialogContent>
          <Alert severity="warning" sx={{ mb: 2 }}>
            This will delete ALL documents from the knowledge base. This action cannot be undone.
          </Alert>
          <Typography>
            Are you sure you want to reset the knowledge base?
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setResetDialogOpen(false)}>Cancel</Button>
          <Button
            onClick={handleResetKnowledgeBase}
            color="error"
            variant="contained"
            disabled={resetting}
          >
            {resetting ? 'Resetting...' : 'Reset'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  )
}
