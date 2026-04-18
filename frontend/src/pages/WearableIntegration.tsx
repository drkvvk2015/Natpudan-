import React, { useState, useEffect } from "react";
import {
  Container,
  Paper,
  Box,
  Button,
  Typography,
  Card,
  CardContent,
  Grid,
  LinearProgress,
  Alert,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  CircularProgress,
} from "@mui/material";
import {
  Watch,
  Favorite,
  DirectionsRun,
  BedtimeOutlined,
  CloudSync,
  Delete,
} from "@mui/icons-material";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, BarChart, Bar } from "recharts";
import axios from "axios";

interface WearableDevice {
  device_id: string;
  device_type: string;
  device_name: string;
  last_sync_at: string;
  is_active: boolean;
  auto_sync_enabled: boolean;
}

interface WearableData {
  heart_rate: number;
  steps: number;
  sleep_hours: number;
  oxygen_saturation: number;
  timestamp: string;
}

interface WearableStats {
  device_type: string;
  last_sync: string;
  today_data: Record<string, number>;
  week_data: WearableData[];
}

const WearableIntegration: React.FC = () => {
  const [devices, setDevices] = useState<WearableDevice[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [authDialogOpen, setAuthDialogOpen] = useState(false);
  const [selectedDeviceType, setSelectedDeviceType] = useState<string>("");
  const [chartData, setChartData] = useState<WearableData[]>([]);
  const [todayStats, setTodayStats] = useState<Record<string, number>>({});
  const [syncInProgress, setSyncInProgress] = useState(false);

  useEffect(() => {
    loadDevices();
    const interval = setInterval(loadDevices, 60000); // Refresh every minute
    return () => clearInterval(interval);
  }, []);

  const loadDevices = async () => {
    try {
      const response = await axios.get("/api/wearable/devices");
      setDevices(response.data.devices || []);
      if (response.data.today_stats) {
        setTodayStats(response.data.today_stats);
      }
      if (response.data.week_data) {
        setChartData(response.data.week_data);
      }
    } catch (err: any) {
      console.error("Failed to load devices:", err);
    }
  };

  const handleConnectDevice = (deviceType: string) => {
    setSelectedDeviceType(deviceType);
    setAuthDialogOpen(true);
  };

  const startOAuthFlow = async () => {
    try {
      setLoading(true);
      const response = await axios.get(
        `/api/wearable/auth/${selectedDeviceType}/url`
      );
      if (response.data.auth_url) {
        window.location.href = response.data.auth_url;
      }
    } catch (err: any) {
      setError("Failed to start authentication: " + err.message);
    } finally {
      setLoading(false);
      setAuthDialogOpen(false);
    }
  };

  const syncNow = async () => {
    setSyncInProgress(true);
    try {
      const response = await axios.post("/api/wearable/sync-now");
      setSuccess("Wearable data synced successfully!");
      await loadDevices();
    } catch (err: any) {
      setError("Sync failed: " + err.message);
    } finally {
      setSyncInProgress(false);
    }
  };

  const deleteDevice = async (deviceId: string) => {
    if (window.confirm("Are you sure you want to disconnect this device?")) {
      try {
        await axios.delete(`/api/wearable/devices/${deviceId}`);
        setSuccess("Device disconnected");
        await loadDevices();
      } catch (err: any) {
        setError("Failed to delete device: " + err.message);
      }
    }
  };

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "center", mb: 4 }}>
        <Typography variant="h4" sx={{ fontWeight: "bold" }}>
          Wearable Device Integration
        </Typography>
        <Button
          variant="contained"
          onClick={syncNow}
          disabled={syncInProgress}
          startIcon={syncInProgress ? <CircularProgress size={20} /> : <CloudSync />}
        >
          {syncInProgress ? "Syncing..." : "Sync Now"}
        </Button>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError("")}>
          {error}
        </Alert>
      )}
      {success && (
        <Alert severity="success" sx={{ mb: 2 }} onClose={() => setSuccess("")}>
          {success}
        </Alert>
      )}

      <Grid container spacing={3}>
        {/* Quick Stats */}
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: "flex", alignItems: "center", mb: 1 }}>
                <Favorite sx={{ color: "#e53935", mr: 1 }} />
                <Typography variant="subtitle2" color="textSecondary">
                  Heart Rate
                </Typography>
              </Box>
              <Typography variant="h5">
                {todayStats.heart_rate || "--"} bpm
              </Typography>
              <Typography variant="caption">Today's average</Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: "flex", alignItems: "center", mb: 1 }}>
                <DirectionsRun sx={{ color: "#1976d2", mr: 1 }} />
                <Typography variant="subtitle2" color="textSecondary">
                  Steps
                </Typography>
              </Box>
              <Typography variant="h5">
                {todayStats.steps || "--"}
              </Typography>
              <Typography variant="caption">Today's total</Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: "flex", alignItems: "center", mb: 1 }}>
                <BedtimeOutlined sx={{ color: "#7b1fa2", mr: 1 }} />
                <Typography variant="subtitle2" color="textSecondary">
                  Sleep
                </Typography>
              </Box>
              <Typography variant="h5">
                {todayStats.sleep_hours || "--"} hrs
              </Typography>
              <Typography variant="caption">Last night</Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: "flex", alignItems: "center", mb: 1 }}>
                <Watch sx={{ color: "#00796b", mr: 1 }} />
                <Typography variant="subtitle2" color="textSecondary">
                  Devices
                </Typography>
              </Box>
              <Typography variant="h5">
                {devices.filter(d => d.is_active).length || 0}
              </Typography>
              <Typography variant="caption">Connected</Typography>
            </CardContent>
          </Card>
        </Grid>

        {/* Heart Rate Trend */}
        {chartData.length > 0 && (
          <Grid item xs={12} md={6}>
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" sx={{ mb: 2 }}>
                Heart Rate Trend
              </Typography>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis
                    dataKey="timestamp"
                    tick={{ fontSize: 12 }}
                  />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Line
                    type="monotone"
                    dataKey="heart_rate"
                    stroke="#e53935"
                    dot={false}
                  />
                </LineChart>
              </ResponsiveContainer>
            </Paper>
          </Grid>
        )}

        {/* Steps Chart */}
        {chartData.length > 0 && (
          <Grid item xs={12} md={6}>
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" sx={{ mb: 2 }}>
                Daily Steps
              </Typography>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={chartData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis
                    dataKey="timestamp"
                    tick={{ fontSize: 12 }}
                  />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="steps" fill="#1976d2" />
                </BarChart>
              </ResponsiveContainer>
            </Paper>
          </Grid>
        )}

        {/* Connected Devices */}
        <Grid item xs={12}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" sx={{ mb: 2 }}>
              Connected Devices
            </Typography>

            {devices.length === 0 ? (
              <Typography variant="body2" sx={{ color: "text.secondary", mb: 3 }}>
                No devices connected yet
              </Typography>
            ) : (
              <TableContainer>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Device Type</TableCell>
                      <TableCell>Status</TableCell>
                      <TableCell>Last Sync</TableCell>
                      <TableCell>Auto Sync</TableCell>
                      <TableCell align="right">Actions</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {devices.map((device) => (
                      <TableRow key={device.device_id}>
                        <TableCell>
                          <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
                            <Watch fontSize="small" />
                            {device.device_type}
                          </Box>
                        </TableCell>
                        <TableCell>
                          <Chip
                            label={device.is_active ? "Active" : "Inactive"}
                            color={device.is_active ? "success" : "default"}
                            size="small"
                          />
                        </TableCell>
                        <TableCell>
                          {device.last_sync_at
                            ? new Date(device.last_sync_at).toLocaleString()
                            : "Never"}
                        </TableCell>
                        <TableCell>
                          <Chip
                            label={device.auto_sync_enabled ? "Enabled" : "Disabled"}
                            size="small"
                          />
                        </TableCell>
                        <TableCell align="right">
                          <Button
                            size="small"
                            color="error"
                            startIcon={<Delete />}
                            onClick={() => deleteDevice(device.device_id)}
                          >
                            Disconnect
                          </Button>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            )}

            <Divider sx={{ my: 3 }} />

            <Typography variant="subtitle1" sx={{ mb: 2, fontWeight: "bold" }}>
              Connect New Device
            </Typography>

            <Grid container spacing={2}>
              <Grid item xs={12} sm={6} md={4}>
                <Button
                  fullWidth
                  variant="outlined"
                  startIcon={<Watch />}
                  onClick={() => handleConnectDevice("fitbit")}
                >
                  Connect Fitbit
                </Button>
              </Grid>
              <Grid item xs={12} sm={6} md={4}>
                <Button
                  fullWidth
                  variant="outlined"
                  startIcon={<Watch />}
                  onClick={() => handleConnectDevice("apple_watch")}
                >
                  Connect Apple Watch
                </Button>
              </Grid>
              <Grid item xs={12} sm={6} md={4}>
                <Button
                  fullWidth
                  variant="outlined"
                  startIcon={<Watch />}
                  onClick={() => handleConnectDevice("garmin")}
                >
                  Connect Garmin
                </Button>
              </Grid>
            </Grid>
          </Paper>
        </Grid>
      </Grid>

      {/* OAuth Dialog */}
      <Dialog open={authDialogOpen} onClose={() => setAuthDialogOpen(false)}>
        <DialogTitle>Connect {selectedDeviceType}</DialogTitle>
        <DialogContent>
          <Typography sx={{ mt: 2 }}>
            You will be redirected to {selectedDeviceType} to authorize Natpudan to access your health data.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setAuthDialogOpen(false)}>Cancel</Button>
          <Button
            variant="contained"
            onClick={startOAuthFlow}
            disabled={loading}
          >
            {loading ? <CircularProgress size={20} /> : "Continue"}
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default WearableIntegration;
