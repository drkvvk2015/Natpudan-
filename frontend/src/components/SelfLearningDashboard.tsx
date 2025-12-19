/**
 * Phase 7: Self-Learning Dashboard
 *
 * Monitor and manage the self-learning engine:
 * - Case collection statistics
 * - Training job status
 * - Model performance metrics
 * - Manual triggers for collection/training
 */

import React, { useState, useEffect } from "react";
import {
  Container,
  Grid,
  Card,
  CardContent,
  Typography,
  Button,
  LinearProgress,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  Box,
  Alert,
  IconButton,
  Tooltip,
  Divider,
} from "@mui/material";
import {
  Refresh as RefreshIcon,
  PlayArrow as PlayIcon,
  CloudUpload as UploadIcon,
  Assessment as AssessmentIcon,
  Timeline as TimelineIcon,
  CheckCircle as CheckIcon,
  Error as ErrorIcon,
  Pending as PendingIcon,
} from "@mui/icons-material";
import apiClient from "../services/apiClient";

interface CollectionStats {
  total_cases: number;
  validated_cases: number;
  pending_cases: number;
  anonymized_cases: number;
  used_in_training: number;
  average_quality_score: number;
  collection_rate: number;
}

interface TrainingJob {
  id: number;
  job_id: string;
  model_type: string;
  model_version: string;
  status: string;
  progress_percentage: number;
  dataset_size: number;
  start_time: string | null;
  end_time: string | null;
  final_accuracy: number | null;
}

interface ModelPerformance {
  id: number;
  model_version: string;
  model_type: string;
  accuracy: number | null;
  precision: number | null;
  recall: number | null;
  f1_score: number | null;
  is_active: boolean;
  deployed_at: string | null;
}

const SelfLearningDashboard: React.FC = () => {
  const [collectionStats, setCollectionStats] =
    useState<CollectionStats | null>(null);
  const [trainingJobs, setTrainingJobs] = useState<TrainingJob[]>([]);
  const [modelPerformance, setModelPerformance] = useState<ModelPerformance[]>(
    []
  );
  const [loading, setLoading] = useState(true);
  const [collecting, setCollecting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  useEffect(() => {
    fetchDashboardData();

    // Auto-refresh every 30 seconds
    const interval = setInterval(fetchDashboardData, 30000);
    return () => clearInterval(interval);
  }, []);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      setError(null);

      // Fetch collection statistics
      const statsRes = await apiClient.get("/api/phase-7/cases/statistics");
      setCollectionStats(statsRes.data);

      // Fetch training jobs
      const jobsRes = await apiClient.get(
        "/api/phase-7/training/jobs?limit=10"
      );
      setTrainingJobs(jobsRes.data);

      // Fetch model performance
      const perfRes = await apiClient.get(
        "/api/phase-7/models/performance?limit=5"
      );
      setModelPerformance(perfRes.data);

      setLoading(false);
    } catch (err: any) {
      console.error("Error fetching dashboard data:", err);
      setError(err.response?.data?.detail || "Failed to load dashboard data");
      setLoading(false);
    }
  };

  const handleCollectCases = async () => {
    try {
      setCollecting(true);
      setError(null);
      setSuccess(null);

      const response = await apiClient.post("/api/phase-7/cases/collect", {
        limit: 50,
        min_confidence: 80,
      });

      setSuccess(response.data.message);

      // Refresh data after collection
      setTimeout(fetchDashboardData, 1000);
    } catch (err: any) {
      console.error("Error collecting cases:", err);
      setError(err.response?.data?.detail || "Failed to collect cases");
    } finally {
      setCollecting(false);
    }
  };

  const getStatusChip = (status: string) => {
    const statusMap: { [key: string]: { color: any; icon: React.ReactNode } } =
      {
        completed: { color: "success", icon: <CheckIcon fontSize="small" /> },
        running: { color: "info", icon: <TimelineIcon fontSize="small" /> },
        queued: { color: "warning", icon: <PendingIcon fontSize="small" /> },
        failed: { color: "error", icon: <ErrorIcon fontSize="small" /> },
        validated: { color: "success", icon: <CheckIcon fontSize="small" /> },
        pending: { color: "warning", icon: <PendingIcon fontSize="small" /> },
      };

    const config = statusMap[status.toLowerCase()] || {
      color: "default",
      icon: null,
    };

    return (
      <Chip
        label={status}
        color={config.color}
        size="small"
        icon={config.icon}
      />
    );
  };

  if (loading && !collectionStats) {
    return (
      <Container sx={{ mt: 4 }}>
        <Typography variant="h4" gutterBottom>
          Phase 7: Self-Learning Engine
        </Typography>
        <LinearProgress />
      </Container>
    );
  }

  return (
    <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
      {/* Header */}
      <Box
        sx={{
          mb: 4,
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
        }}
      >
        <div>
          <Typography variant="h4" gutterBottom>
            🚀 Phase 7: Self-Learning Engine
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Automated case collection, training, and model deployment
          </Typography>
        </div>
        <Box>
          <Tooltip title="Refresh Data">
            <IconButton onClick={fetchDashboardData} disabled={loading}>
              <RefreshIcon />
            </IconButton>
          </Tooltip>
          <Button
            variant="contained"
            startIcon={<UploadIcon />}
            onClick={handleCollectCases}
            disabled={collecting}
            sx={{ ml: 1 }}
          >
            {collecting ? "Collecting..." : "Collect Cases"}
          </Button>
        </Box>
      </Box>

      {/* Alerts */}
      {error && (
        <Alert severity="error" onClose={() => setError(null)} sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}
      {success && (
        <Alert
          severity="success"
          onClose={() => setSuccess(null)}
          sx={{ mb: 2 }}
        >
          {success}
        </Alert>
      )}

      <Grid container spacing={3}>
        {/* Collection Statistics */}
        <Grid item xs={12} md={6} lg={3}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Total Cases
              </Typography>
              <Typography variant="h3" color="primary">
                {collectionStats?.total_cases || 0}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Collected from treatment plans
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6} lg={3}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Validated
              </Typography>
              <Typography variant="h3" color="success.main">
                {collectionStats?.validated_cases || 0}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Ready for training
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6} lg={3}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Quality Score
              </Typography>
              <Typography variant="h3" color="info.main">
                {collectionStats?.average_quality_score.toFixed(1) || "0.0"}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Average data quality
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6} lg={3}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Used in Training
              </Typography>
              <Typography variant="h3" color="secondary.main">
                {collectionStats?.used_in_training || 0}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Cases already trained
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        {/* Training Jobs */}
        <Grid item xs={12} lg={8}>
          <Card>
            <CardContent>
              <Box
                sx={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                  mb: 2,
                }}
              >
                <Typography variant="h6">Recent Training Jobs</Typography>
                <Chip
                  label={`${trainingJobs.length} jobs`}
                  size="small"
                  color="primary"
                  variant="outlined"
                />
              </Box>
              <Divider sx={{ mb: 2 }} />

              {trainingJobs.length === 0 ? (
                <Alert severity="info">
                  No training jobs yet. Jobs will appear here once training
                  begins.
                </Alert>
              ) : (
                <TableContainer component={Paper} variant="outlined">
                  <Table size="small">
                    <TableHead>
                      <TableRow>
                        <TableCell>Job ID</TableCell>
                        <TableCell>Model Type</TableCell>
                        <TableCell>Status</TableCell>
                        <TableCell>Progress</TableCell>
                        <TableCell>Dataset Size</TableCell>
                        <TableCell>Accuracy</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {trainingJobs.map((job) => (
                        <TableRow key={job.job_id}>
                          <TableCell>
                            <Typography
                              variant="body2"
                              sx={{ fontFamily: "monospace" }}
                            >
                              {job.job_id.substring(0, 20)}...
                            </Typography>
                          </TableCell>
                          <TableCell>
                            <Chip
                              label={job.model_type}
                              size="small"
                              variant="outlined"
                            />
                          </TableCell>
                          <TableCell>{getStatusChip(job.status)}</TableCell>
                          <TableCell>
                            <Box sx={{ display: "flex", alignItems: "center" }}>
                              <Box sx={{ width: "100%", mr: 1 }}>
                                <LinearProgress
                                  variant="determinate"
                                  value={job.progress_percentage}
                                />
                              </Box>
                              <Typography
                                variant="body2"
                                color="text.secondary"
                              >
                                {job.progress_percentage}%
                              </Typography>
                            </Box>
                          </TableCell>
                          <TableCell>{job.dataset_size}</TableCell>
                          <TableCell>
                            {job.final_accuracy
                              ? `${job.final_accuracy}%`
                              : "-"}
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Model Performance */}
        <Grid item xs={12} lg={4}>
          <Card>
            <CardContent>
              <Box
                sx={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                  mb: 2,
                }}
              >
                <Typography variant="h6">Model Performance</Typography>
                <AssessmentIcon color="primary" />
              </Box>
              <Divider sx={{ mb: 2 }} />

              {modelPerformance.length === 0 ? (
                <Alert severity="info">
                  No models deployed yet. Models will appear here after
                  training.
                </Alert>
              ) : (
                <Box>
                  {modelPerformance.map((model) => (
                    <Card key={model.id} variant="outlined" sx={{ mb: 2 }}>
                      <CardContent>
                        <Box
                          sx={{
                            display: "flex",
                            justifyContent: "space-between",
                            alignItems: "center",
                            mb: 1,
                          }}
                        >
                          <Typography variant="subtitle1" fontWeight="bold">
                            {model.model_version}
                          </Typography>
                          {model.is_active && (
                            <Chip label="ACTIVE" color="success" size="small" />
                          )}
                        </Box>
                        <Typography
                          variant="body2"
                          color="text.secondary"
                          gutterBottom
                        >
                          {model.model_type}
                        </Typography>

                        <Grid container spacing={1} sx={{ mt: 1 }}>
                          <Grid item xs={6}>
                            <Typography
                              variant="caption"
                              color="text.secondary"
                            >
                              Accuracy
                            </Typography>
                            <Typography variant="body2" fontWeight="bold">
                              {model.accuracy ? `${model.accuracy}%` : "N/A"}
                            </Typography>
                          </Grid>
                          <Grid item xs={6}>
                            <Typography
                              variant="caption"
                              color="text.secondary"
                            >
                              F1 Score
                            </Typography>
                            <Typography variant="body2" fontWeight="bold">
                              {model.f1_score ? `${model.f1_score}%` : "N/A"}
                            </Typography>
                          </Grid>
                        </Grid>

                        {model.deployed_at && (
                          <Typography
                            variant="caption"
                            color="text.secondary"
                            sx={{ mt: 1, display: "block" }}
                          >
                            Deployed:{" "}
                            {new Date(model.deployed_at).toLocaleString()}
                          </Typography>
                        )}
                      </CardContent>
                    </Card>
                  ))}
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* System Status */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                System Status
              </Typography>
              <Divider sx={{ mb: 2 }} />

              <Grid container spacing={2}>
                <Grid item xs={12} md={4}>
                  <Paper variant="outlined" sx={{ p: 2 }}>
                    <Typography variant="subtitle2" color="text.secondary">
                      Collection Rate
                    </Typography>
                    <Box sx={{ display: "flex", alignItems: "center", mt: 1 }}>
                      <LinearProgress
                        variant="determinate"
                        value={collectionStats?.collection_rate || 0}
                        sx={{ flexGrow: 1, mr: 2 }}
                      />
                      <Typography variant="body2">
                        {collectionStats?.collection_rate.toFixed(1)}%
                      </Typography>
                    </Box>
                  </Paper>
                </Grid>

                <Grid item xs={12} md={4}>
                  <Paper variant="outlined" sx={{ p: 2 }}>
                    <Typography variant="subtitle2" color="text.secondary">
                      Anonymization
                    </Typography>
                    <Box sx={{ display: "flex", alignItems: "center", mt: 1 }}>
                      <LinearProgress
                        variant="determinate"
                        value={
                          collectionStats?.total_cases
                            ? (collectionStats.anonymized_cases /
                                collectionStats.total_cases) *
                              100
                            : 0
                        }
                        sx={{ flexGrow: 1, mr: 2 }}
                      />
                      <Typography variant="body2">
                        {collectionStats?.anonymized_cases || 0} /{" "}
                        {collectionStats?.total_cases || 0}
                      </Typography>
                    </Box>
                  </Paper>
                </Grid>

                <Grid item xs={12} md={4}>
                  <Paper variant="outlined" sx={{ p: 2 }}>
                    <Typography variant="subtitle2" color="text.secondary">
                      Pending Review
                    </Typography>
                    <Box sx={{ display: "flex", alignItems: "center", mt: 1 }}>
                      <Typography variant="h4" color="warning.main">
                        {collectionStats?.pending_cases || 0}
                      </Typography>
                      <Typography
                        variant="body2"
                        color="text.secondary"
                        sx={{ ml: 1 }}
                      >
                        cases awaiting validation
                      </Typography>
                    </Box>
                  </Paper>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Container>
  );
};

export default SelfLearningDashboard;
