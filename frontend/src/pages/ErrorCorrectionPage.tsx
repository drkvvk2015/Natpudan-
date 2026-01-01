import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Button,
  Alert,
  LinearProgress,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  IconButton,
  Tooltip,
} from '@mui/material';
import {
  Refresh as RefreshIcon,
  Delete as DeleteIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  Warning as WarningIcon,
  Info as InfoIcon,
} from '@mui/icons-material';
import apiClient from '../services/apiClient';

interface ErrorStats {
  total_errors: number;
  auto_corrected: number;
  correction_rate: number;
  recent_errors: any[];
}

interface ErrorLog {
  id: number;
  timestamp: string;
  severity: 'critical' | 'high' | 'medium' | 'low';
  category: string;
  message: string;
  auto_corrected: boolean;
  correction_applied: string | null;
}

interface CorrectionRule {
  error_pattern: string;
  correction_action: string;
  times_applied: number;
  success_rate: number;
}

const ErrorCorrectionPage = () => {
  const [stats, setStats] = useState<ErrorStats | null>(null);
  const [errors, setErrors] = useState<ErrorLog[]>([]);
  const [rules, setRules] = useState<CorrectionRule[]>([]);
  const [loading, setLoading] = useState(true);
  const [filterCategory, setFilterCategory] = useState('all');
  const [filterSeverity, setFilterSeverity] = useState('all');

  const fetchData = async () => {
    setLoading(true);
    try {
      const [statsRes, errorsRes, rulesRes] = await Promise.all([
        apiClient.get('/api/error-correction/errors/stats'),
        apiClient.get('/api/error-correction/errors', {
          params: {
            limit: 50,
            ...(filterCategory !== 'all' && { category: filterCategory }),
            ...(filterSeverity !== 'all' && { severity: filterSeverity }),
          },
        }),
        apiClient.get('/api/error-correction/correction-rules'),
      ]);

      setStats(statsRes.data);
      setErrors(errorsRes.data);
      setRules(rulesRes.data);
    } catch (error) {
      console.error('Failed to fetch error data:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [filterCategory, filterSeverity]);

  const handleClearErrors = async () => {
    if (window.confirm('Are you sure you want to clear all error logs?')) {
      try {
        await apiClient.post('/api/error-correction/errors/clear');
        fetchData();
      } catch (error) {
        console.error('Failed to clear errors:', error);
      }
    }
  };

  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case 'critical':
        return <ErrorIcon color="error" />;
      case 'high':
        return <WarningIcon color="warning" />;
      case 'medium':
        return <InfoIcon color="info" />;
      default:
        return <InfoIcon color="disabled" />;
    }
  };

  const getSeverityColor = (severity: string): "error" | "warning" | "info" | "default" => {
    switch (severity) {
      case 'critical':
        return 'error';
      case 'high':
        return 'warning';
      case 'medium':
        return 'info';
      default:
        return 'default';
    }
  };

  if (loading && !stats) {
    return (
      <Box sx={{ width: '100%', mt: 2 }}>
        <LinearProgress />
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ mb: 3, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Typography variant="h4" component="h1">
          Error Correction System
        </Typography>
        <Box>
          <Button
            variant="outlined"
            startIcon={<RefreshIcon />}
            onClick={fetchData}
            sx={{ mr: 1 }}
          >
            Refresh
          </Button>
          <Button
            variant="outlined"
            color="error"
            startIcon={<DeleteIcon />}
            onClick={handleClearErrors}
          >
            Clear Logs
          </Button>
        </Box>
      </Box>

      {/* Statistics Cards */}
      {stats && (
        <Grid container spacing={3} sx={{ mb: 3 }}>
          <Grid item xs={12} md={3}>
            <Card>
              <CardContent>
                <Typography color="textSecondary" gutterBottom>
                  Total Errors
                </Typography>
                <Typography variant="h4">{stats.total_errors}</Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={3}>
            <Card>
              <CardContent>
                <Typography color="textSecondary" gutterBottom>
                  Auto-Corrected
                </Typography>
                <Typography variant="h4" color="success.main">
                  {stats.auto_corrected}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={3}>
            <Card>
              <CardContent>
                <Typography color="textSecondary" gutterBottom>
                  Correction Rate
                </Typography>
                <Typography variant="h4">
                  {(stats.correction_rate * 100).toFixed(1)}%
                </Typography>
                <LinearProgress
                  variant="determinate"
                  value={stats.correction_rate * 100}
                  sx={{ mt: 1 }}
                />
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={3}>
            <Card>
              <CardContent>
                <Typography color="textSecondary" gutterBottom>
                  Recent (1 hour)
                </Typography>
                <Typography variant="h4">{stats.recent_errors.length}</Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {/* Correction Rules */}
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Active Correction Rules
          </Typography>
          <Grid container spacing={2}>
            {rules.map((rule, index) => (
              <Grid item xs={12} md={6} key={index}>
                <Alert
                  severity="success"
                  icon={<CheckCircleIcon />}
                  sx={{ height: '100%' }}
                >
                  <Typography variant="subtitle2" fontWeight="bold">
                    {rule.error_pattern}
                  </Typography>
                  <Typography variant="body2">
                    Action: {rule.correction_action}
                  </Typography>
                  <Typography variant="caption">
                    Applied {rule.times_applied} times • Success: {(rule.success_rate * 100).toFixed(0)}%
                  </Typography>
                </Alert>
              </Grid>
            ))}
          </Grid>
        </CardContent>
      </Card>

      {/* Filters */}
      <Card sx={{ mb: 2 }}>
        <CardContent>
          <Grid container spacing={2} alignItems="center">
            <Grid item xs={12} md={4}>
              <FormControl fullWidth>
                <InputLabel>Category</InputLabel>
                <Select
                  value={filterCategory}
                  label="Category"
                  onChange={(e) => setFilterCategory(e.target.value)}
                >
                  <MenuItem value="all">All Categories</MenuItem>
                  <MenuItem value="database">Database</MenuItem>
                  <MenuItem value="authentication">Authentication</MenuItem>
                  <MenuItem value="api">API</MenuItem>
                  <MenuItem value="validation">Validation</MenuItem>
                  <MenuItem value="network">Network</MenuItem>
                  <MenuItem value="permission">Permission</MenuItem>
                  <MenuItem value="system">System</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={4}>
              <FormControl fullWidth>
                <InputLabel>Severity</InputLabel>
                <Select
                  value={filterSeverity}
                  label="Severity"
                  onChange={(e) => setFilterSeverity(e.target.value)}
                >
                  <MenuItem value="all">All Severities</MenuItem>
                  <MenuItem value="critical">Critical</MenuItem>
                  <MenuItem value="high">High</MenuItem>
                  <MenuItem value="medium">Medium</MenuItem>
                  <MenuItem value="low">Low</MenuItem>
                </Select>
              </FormControl>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Error Logs Table */}
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Error Logs
          </Typography>
          <TableContainer component={Paper}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Time</TableCell>
                  <TableCell>Severity</TableCell>
                  <TableCell>Category</TableCell>
                  <TableCell>Message</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Correction</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {errors.map((error) => (
                  <TableRow key={error.id}>
                    <TableCell>
                      {new Date(error.timestamp).toLocaleString()}
                    </TableCell>
                    <TableCell>
                      <Chip
                        icon={getSeverityIcon(error.severity)}
                        label={error.severity}
                        color={getSeverityColor(error.severity)}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>
                      <Chip label={error.category} size="small" variant="outlined" />
                    </TableCell>
                    <TableCell>
                      <Tooltip title={error.message}>
                        <Typography variant="body2" noWrap sx={{ maxWidth: 300 }}>
                          {error.message}
                        </Typography>
                      </Tooltip>
                    </TableCell>
                    <TableCell>
                      {error.auto_corrected ? (
                        <Chip
                          icon={<CheckCircleIcon />}
                          label="Auto-Fixed"
                          color="success"
                          size="small"
                        />
                      ) : (
                        <Chip label="Manual" size="small" />
                      )}
                    </TableCell>
                    <TableCell>
                      {error.correction_applied || '-'}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </CardContent>
      </Card>
    </Box>
  );
};

export default ErrorCorrectionPage;
