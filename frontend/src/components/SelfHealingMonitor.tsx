import React, { useState, useEffect } from "react";
import {
  Card,
  CardContent,
  Typography,
  Box,
  Chip,
  LinearProgress,
  Grid,
  Alert,
  Tooltip,
  IconButton,
  Collapse,
} from "@mui/material";
import {
  AutoFixHigh as HealingIcon,
  TrendingUp as TrendingUpIcon,
  Warning as WarningIcon,
  CheckCircle as SuccessIcon,
  Refresh as RefreshIcon,
  ExpandMore as ExpandMoreIcon,
} from "@mui/icons-material";
import apiClient from "../services/apiClient";

interface SelfHealingStatus {
  system_health: {
    status: string;
    warnings: string[];
    predicted_errors: any[];
  };
  metrics: {
    total_errors_handled: number;
    successful_fixes: number;
    failed_fixes: number;
    prevented_errors: number;
  };
  success_rate: number;
  known_solutions: number;
}

const SelfHealingMonitor: React.FC = () => {
  const [status, setStatus] = useState<SelfHealingStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [expanded, setExpanded] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadStatus();
    // Refresh every 30 seconds
    const interval = setInterval(loadStatus, 30000);
    return () => clearInterval(interval);
  }, []);

  const loadStatus = async () => {
    try {
      setLoading(true);
      const response = await apiClient.get("/api/self-healing/status");
      setStatus(response.data);
      setError(null);
    } catch (err: any) {
      console.error("Failed to load self-healing status:", err);
      setError("Failed to load system status");
    } finally {
      setLoading(false);
    }
  };

  const runMaintenance = async () => {
    try {
      await apiClient.post("/api/self-healing/run-maintenance");
      setTimeout(loadStatus, 2000); // Reload after 2 seconds
    } catch (err) {
      console.error("Failed to run maintenance:", err);
    }
  };

  if (loading && !status) {
    return (
      <Card>
        <CardContent>
          <Box sx={{ display: "flex", alignItems: "center", gap: 2 }}>
            <HealingIcon color="primary" />
            <Typography variant="h6">Self-Healing System</Typography>
          </Box>
          <LinearProgress sx={{ mt: 2 }} />
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card>
        <CardContent>
          <Alert severity="warning">{error}</Alert>
        </CardContent>
      </Card>
    );
  }

  if (!status) return null;

  const successRate = (status.success_rate * 100).toFixed(1);
  const healthStatus = status.system_health.status;
  const isHealthy = healthStatus === "healthy";

  return (
    <Card sx={{ mb: 3 }}>
      <CardContent>
        {/* Header */}
        <Box
          sx={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            mb: 2,
          }}
        >
          <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
            <HealingIcon color={isHealthy ? "success" : "warning"} />
            <Typography variant="h6">Self-Healing System</Typography>
            <Chip
              label={isHealthy ? "Healthy" : "At Risk"}
              color={isHealthy ? "success" : "warning"}
              size="small"
            />
          </Box>
          <Box>
            <Tooltip title="Refresh status">
              <IconButton onClick={loadStatus} size="small">
                <RefreshIcon />
              </IconButton>
            </Tooltip>
            <Tooltip title={expanded ? "Show less" : "Show more"}>
              <IconButton onClick={() => setExpanded(!expanded)} size="small">
                <ExpandMoreIcon
                  sx={{
                    transform: expanded ? "rotate(180deg)" : "rotate(0deg)",
                    transition: "0.3s",
                  }}
                />
              </IconButton>
            </Tooltip>
          </Box>
        </Box>

        {/* Quick Stats */}
        <Grid container spacing={2} sx={{ mb: 2 }}>
          <Grid item xs={6} sm={3}>
            <Box sx={{ textAlign: "center" }}>
              <Typography variant="h4" color="success.main">
                {successRate}%
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Success Rate
              </Typography>
            </Box>
          </Grid>
          <Grid item xs={6} sm={3}>
            <Box sx={{ textAlign: "center" }}>
              <Typography variant="h4" color="primary.main">
                {status.metrics.total_errors_handled}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Errors Handled
              </Typography>
            </Box>
          </Grid>
          <Grid item xs={6} sm={3}>
            <Box sx={{ textAlign: "center" }}>
              <Typography variant="h4" color="success.main">
                {status.metrics.prevented_errors}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Prevented
              </Typography>
            </Box>
          </Grid>
          <Grid item xs={6} sm={3}>
            <Box sx={{ textAlign: "center" }}>
              <Typography variant="h4" color="info.main">
                {status.known_solutions}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                Solutions Learned
              </Typography>
            </Box>
          </Grid>
        </Grid>

        {/* Warnings */}
        {status.system_health.warnings.length > 0 && (
          <Alert severity="warning" sx={{ mb: 2 }}>
            <Typography variant="body2" fontWeight="bold">
              System Warnings:
            </Typography>
            <Box component="ul" sx={{ margin: "4px 0", paddingLeft: "20px" }}>
              {status.system_health.warnings.map((warning, idx) => (
                <li key={idx}>
                  <Typography variant="caption">{warning}</Typography>
                </li>
              ))}
            </Box>
          </Alert>
        )}

        {/* Predicted Errors */}
        {status.system_health.predicted_errors.length > 0 && (
          <Alert severity="info" sx={{ mb: 2 }}>
            <Typography variant="body2" fontWeight="bold">
              Predicted Issues:
            </Typography>
            <Box component="ul" sx={{ margin: "4px 0", paddingLeft: "20px" }}>
              {status.system_health.predicted_errors
                .slice(0, 3)
                .map((pred, idx) => (
                  <li key={idx}>
                    <Typography variant="caption">
                      {pred.type} ({(pred.likelihood * 100).toFixed(0)}%
                      likelihood) - {pred.prevention}
                    </Typography>
                  </li>
                ))}
            </Box>
          </Alert>
        )}

        {/* Expanded Details */}
        <Collapse in={expanded}>
          <Box
            sx={{
              mt: 2,
              pt: 2,
              borderTop: "1px solid",
              borderColor: "divider",
            }}
          >
            <Typography variant="subtitle2" gutterBottom>
              Detailed Metrics
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={6}>
                <Typography variant="body2" color="text.secondary">
                  Successful Fixes:
                </Typography>
                <Typography variant="body1" color="success.main">
                  {status.metrics.successful_fixes}
                </Typography>
              </Grid>
              <Grid item xs={6}>
                <Typography variant="body2" color="text.secondary">
                  Failed Fixes:
                </Typography>
                <Typography variant="body1" color="error.main">
                  {status.metrics.failed_fixes}
                </Typography>
              </Grid>
            </Grid>

            <Box sx={{ mt: 2, textAlign: "center" }}>
              <Chip
                label="Run Preventive Maintenance"
                onClick={runMaintenance}
                color="primary"
                icon={<HealingIcon />}
                sx={{ cursor: "pointer" }}
              />
            </Box>
          </Box>
        </Collapse>

        {/* Status Indicator */}
        {isHealthy && (
          <Box sx={{ display: "flex", alignItems: "center", gap: 1, mt: 2 }}>
            <SuccessIcon fontSize="small" color="success" />
            <Typography variant="caption" color="success.main">
              System is healthy and actively learning from errors
            </Typography>
          </Box>
        )}
      </CardContent>
    </Card>
  );
};

export default SelfHealingMonitor;
