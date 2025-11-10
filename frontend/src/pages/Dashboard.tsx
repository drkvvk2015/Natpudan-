//
import { useState, useEffect } from 'react'
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
} from '@mui/material'
import {
  Memory as MemoryIcon,
  Storage as StorageIcon,
  Timer as TimerIcon,
  DeveloperBoard as CpuIcon,
  CheckCircle as CheckCircleIcon,
  Warning as WarningIcon,
} from '@mui/icons-material';
import { checkDetailedHealth, type DetailedHealthStatus } from '../services/api';

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
  const theme = useTheme();

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
          value: formatUptime(health.uptime),
          icon: <TimerIcon sx={{ fontSize: 40 }} />,
          color: theme.palette.primary.main,
        },
        {
          title: 'CPU Usage',
          value: `${health.cpu_usage.toFixed(1)}%`,
          icon: <CpuIcon sx={{ fontSize: 40 }} />,
          color: theme.palette.success.main,
        },
        {
          title: 'Memory Usage',
          value: `${health.memory_usage.percent}%`,
          icon: <MemoryIcon sx={{ fontSize: 40 }} />,
          color: theme.palette.warning.main,
        },
        {
          title: 'Disk Usage',
          value: `${health.disk_usage.percent}%`,
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
              🤖
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
              label="🧠 AI Powered"
              sx={{
                bgcolor: 'rgba(255,255,255,0.25)',
                color: 'white',
                fontWeight: 600,
                backdropFilter: 'blur(10px)',
                border: '1px solid rgba(255,255,255,0.3)',
              }}
            />
            <Chip
              label="⚡ Real-time Analysis"
              sx={{
                bgcolor: 'rgba(255,255,255,0.25)',
                color: 'white',
                fontWeight: 600,
                backdropFilter: 'blur(10px)',
                border: '1px solid rgba(255,255,255,0.3)',
              }}
            />
            <Chip
              label="🔒 HIPAA Compliant"
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
                  🔍 Drug interaction check: Warfarin + Aspirin (10 mins ago)
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                  💬 AI consultation: Patient with chest pain (25 mins ago)
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                  📋 Diagnosis: Hypertension Stage 2 (1 hour ago)
                </Typography>
                <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                  📚 PDF uploaded: Harrison's Internal Medicine Ch.12 (2 hours ago)
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
                  → Start AI Chat
                </Typography>
                <Typography variant="body2" color="primary" sx={{ cursor: 'pointer', mb: 1 }}>
                  → Check Drug Interactions
                </Typography>
                <Typography variant="body2" color="primary" sx={{ cursor: 'pointer', mb: 1 }}>
                  → Upload Medical PDF
                </Typography>
                <Typography variant="body2" color="primary" sx={{ cursor: 'pointer' }}>
                  → View Knowledge Base
                </Typography>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  )
}
