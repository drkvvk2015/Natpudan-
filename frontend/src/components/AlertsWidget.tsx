import React, { useState, useEffect } from "react";
import {
  Card,
  CardContent,
  CardHeader,
  Typography,
  Box,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  LinearProgress,
  IconButton,
  Collapse,
} from "@mui/material";
import {
  Warning,
  ErrorOutline,
  CheckCircle,
  Close,
  ExpandMore,
  ExpandLess,
} from "@mui/icons-material";
import axios from "axios";

export interface Alert {
  id: number;
  patient_intake_id: number;
  alert_type: string;
  severity: "low" | "medium" | "high" | "critical";
  description: string;
  recommended_action: string;
  is_acknowledged: boolean;
  acknowledged_by?: string;
  created_at: string;
}

export interface PatientRiskData {
  patient_id: number;
  patient_name: string;
  risk_score: number;
  risk_level: string;
  top_risk_factors: string[];
}

interface AlertsWidgetProps {
  patientId?: number;
  compact?: boolean;
}

const AlertsWidget: React.FC<AlertsWidgetProps> = ({ patientId, compact = false }) => {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [highRiskPatients, setHighRiskPatients] = useState<PatientRiskData[]>([]);
  const [loading, setLoading] = useState(false);
  const [selectedAlert, setSelectedAlert] = useState<Alert | null>(null);
  const [detailsOpen, setDetailsOpen] = useState(false);
  const [expanded, setExpanded] = useState(!compact);

  useEffect(() => {
    loadAlerts();
    const interval = setInterval(loadAlerts, 30000); // Refresh every 30 seconds
    return () => clearInterval(interval);
  }, [patientId]);

  const loadAlerts = async () => {
    try {
      setLoading(true);

      if (patientId) {
        // Load alerts for specific patient
        const response = await axios.get(`/api/predictions/patient/${patientId}/alerts`);
        setAlerts(response.data.alerts || []);
      } else {
        // Load high-risk patients (for admin/overview)
        const response = await axios.get("/api/predictions/high-risk-patients");
        setHighRiskPatients(response.data.patients || []);

        // Also load recent alerts
        const alertsResponse = await axios.get("/api/predictions/recent-alerts");
        setAlerts(alertsResponse.data.alerts || []);
      }
    } catch (err: any) {
      console.error("Failed to load alerts:", err);
    } finally {
      setLoading(false);
    }
  };

  const acknowledgeAlert = async (alertId: number) => {
    try {
      await axios.post(`/api/predictions/alerts/${alertId}/acknowledge`);
      setAlerts(alerts.map(a => a.id === alertId ? { ...a, is_acknowledged: true } : a));
      setDetailsOpen(false);
    } catch (err: any) {
      console.error("Failed to acknowledge alert:", err);
    }
  };

  const getSeverityColor = (severity: string) => {
    const colors: Record<string, string> = {
      critical: "#d32f2f",
      high: "#f57c00",
      medium: "#fbc02d",
      low: "#388e3c",
    };
    return colors[severity] || "#999";
  };

  const getSeverityIcon = (severity: string) => {
    if (severity === "critical") return <ErrorOutline />;
    if (severity === "high") return <Warning />;
    return <CheckCircle />;
  };

  const unacknowledgedCount = alerts.filter(a => !a.is_acknowledged).length;
  const criticalCount = alerts.filter(a => a.severity === "critical").length;

  if (compact && !unacknowledgedCount) {
    return null; // Don't show if compact and no unacknowledged alerts
  }

  return (
    <Card>
      <CardHeader
        title={
          <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
            <Typography variant="h6">Clinical Alerts</Typography>
            {unacknowledgedCount > 0 && (
              <Chip
                label={unacknowledgedCount}
                color="error"
                size="small"
                sx={{ fontWeight: "bold" }}
              />
            )}
          </Box>
        }
        action={
          <IconButton
            onClick={() => setExpanded(!expanded)}
            size="small"
          >
            {expanded ? <ExpandLess /> : <ExpandMore />}
          </IconButton>
        }
      />
      <Collapse in={expanded}>
        <CardContent>
          {loading && <LinearProgress sx={{ mb: 2 }} />}

          {alerts.length === 0 ? (
            <Typography variant="body2" sx={{ color: "text.secondary", textAlign: "center", py: 2 }}>
              No active alerts
            </Typography>
          ) : (
            <TableContainer>
              <Table size="small">
                <TableHead>
                  <TableRow sx={{ backgroundColor: "#f5f5f5" }}>
                    <TableCell>Severity</TableCell>
                    <TableCell>Type</TableCell>
                    <TableCell>Description</TableCell>
                    <TableCell align="center">Status</TableCell>
                    <TableCell align="right">Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {alerts.map((alert) => (
                    <TableRow
                      key={alert.id}
                      sx={{
                        backgroundColor: alert.is_acknowledged ? "#fafafa" : "#fffde7",
                        "&:hover": { backgroundColor: "#f0f0f0" },
                      }}
                    >
                      <TableCell>
                        <Box
                          sx={{
                            display: "flex",
                            alignItems: "center",
                            gap: 1,
                          }}
                        >
                          <Box
                            sx={{
                              color: getSeverityColor(alert.severity),
                            }}
                          >
                            {getSeverityIcon(alert.severity)}
                          </Box>
                          <Chip
                            label={alert.severity.toUpperCase()}
                            size="small"
                            sx={{
                              backgroundColor: getSeverityColor(alert.severity),
                              color: "#fff",
                            }}
                          />
                        </Box>
                      </TableCell>
                      <TableCell sx={{ fontWeight: "bold" }}>
                        {alert.alert_type}
                      </TableCell>
                      <TableCell>{alert.description}</TableCell>
                      <TableCell align="center">
                        <Chip
                          label={alert.is_acknowledged ? "Acknowledged" : "New"}
                          color={alert.is_acknowledged ? "default" : "error"}
                          size="small"
                          variant={alert.is_acknowledged ? "outlined" : "filled"}
                        />
                      </TableCell>
                      <TableCell align="right">
                        <Button
                          size="small"
                          variant="outlined"
                          onClick={() => {
                            setSelectedAlert(alert);
                            setDetailsOpen(true);
                          }}
                        >
                          Details
                        </Button>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          )}

          {highRiskPatients.length > 0 && (
            <Box sx={{ mt: 3 }}>
              <Typography variant="subtitle2" sx={{ fontWeight: "bold", mb: 2 }}>
                High-Risk Patients ({highRiskPatients.length})
              </Typography>
              <TableContainer>
                <Table size="small">
                  <TableHead>
                    <TableRow sx={{ backgroundColor: "#f5f5f5" }}>
                      <TableCell>Patient</TableCell>
                      <TableCell align="right">Risk Score</TableCell>
                      <TableCell>Risk Level</TableCell>
                      <TableCell>Top Factors</TableCell>
                      <TableCell align="right">Actions</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {highRiskPatients.slice(0, 5).map((patient) => (
                      <TableRow key={patient.patient_id}>
                        <TableCell>{patient.patient_name}</TableCell>
                        <TableCell align="right">
                          <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
                            <LinearProgress
                              variant="determinate"
                              value={patient.risk_score * 100}
                              sx={{ flex: 1, mr: 1 }}
                            />
                            <Typography variant="body2" sx={{ fontWeight: "bold", minWidth: 40 }}>
                              {(patient.risk_score * 100).toFixed(0)}%
                            </Typography>
                          </Box>
                        </TableCell>
                        <TableCell>
                          <Chip
                            label={patient.risk_level}
                            color={
                              patient.risk_level === "critical"
                                ? "error"
                                : patient.risk_level === "high"
                                ? "warning"
                                : "default"
                            }
                            size="small"
                          />
                        </TableCell>
                        <TableCell>
                          <Box sx={{ display: "flex", flexWrap: "wrap", gap: 0.5 }}>
                            {patient.top_risk_factors.slice(0, 2).map((factor, i) => (
                              <Chip
                                key={i}
                                label={factor}
                                variant="outlined"
                                size="small"
                              />
                            ))}
                          </Box>
                        </TableCell>
                        <TableCell align="right">
                          <Button
                            size="small"
                            variant="outlined"
                            href={`/patient/${patient.patient_id}`}
                          >
                            View
                          </Button>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </Box>
          )}
        </CardContent>
      </Collapse>

      {/* Alert Details Dialog */}
      <Dialog open={detailsOpen} onClose={() => setDetailsOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Alert Details</DialogTitle>
        <DialogContent>
          {selectedAlert && (
            <Box sx={{ mt: 2 }}>
              <Box sx={{ mb: 2 }}>
                <Chip
                  label={selectedAlert.severity.toUpperCase()}
                  sx={{
                    backgroundColor: getSeverityColor(selectedAlert.severity),
                    color: "#fff",
                  }}
                />
              </Box>

              <Box sx={{ mb: 2 }}>
                <Typography variant="subtitle2" sx={{ fontWeight: "bold", mb: 0.5 }}>
                  Alert Type
                </Typography>
                <Typography variant="body2">{selectedAlert.alert_type}</Typography>
              </Box>

              <Box sx={{ mb: 2 }}>
                <Typography variant="subtitle2" sx={{ fontWeight: "bold", mb: 0.5 }}>
                  Description
                </Typography>
                <Typography variant="body2">{selectedAlert.description}</Typography>
              </Box>

              <Box sx={{ mb: 2 }}>
                <Typography variant="subtitle2" sx={{ fontWeight: "bold", mb: 0.5 }}>
                  Recommended Action
                </Typography>
                <Typography variant="body2">{selectedAlert.recommended_action}</Typography>
              </Box>

              <Box>
                <Typography variant="caption" sx={{ color: "text.secondary" }}>
                  Created: {new Date(selectedAlert.created_at).toLocaleString()}
                </Typography>
              </Box>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDetailsOpen(false)}>Close</Button>
          {selectedAlert && !selectedAlert.is_acknowledged && (
            <Button
              variant="contained"
              color="primary"
              onClick={() => acknowledgeAlert(selectedAlert.id)}
            >
              Acknowledge
            </Button>
          )}
        </DialogActions>
      </Dialog>
    </Card>
  );
};

export default AlertsWidget;
