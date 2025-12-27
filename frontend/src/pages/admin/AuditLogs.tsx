import React, { useEffect, useState } from "react";
import {
  Box,
  Button,
  Grid,
  MenuItem,
  Paper,
  TextField,
  Typography,
} from "@mui/material";
import dayjs from "dayjs";
import {
  AuditLogItem,
  fetchAuditLogs,
  exportAuditLogsCSV,
} from "../../services/auditLogs";

export default function AuditLogs() {
  const [rows, setRows] = useState<AuditLogItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [filters, setFilters] = useState<{
    user_id?: number;
    action?: string;
    resource?: string;
    start?: string;
    end?: string;
  }>({});

  const load = async () => {
    setLoading(true);
    try {
      const { items } = await fetchAuditLogs({ ...filters, limit: 100 });
      setRows(items);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const onExport = async () => {
    try {
      const blob = await exportAuditLogsCSV(filters);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `audit_logs_${dayjs().format("YYYYMMDD_HHmmss")}.csv`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <Box sx={{ p: 2 }}>
      <Typography variant="h5" sx={{ mb: 2 }}>
        Audit Logs
      </Typography>

      <Paper sx={{ p: 2, mb: 2 }}>
        <Grid container spacing={2}>
          <Grid item xs={12} md={2}>
            <TextField
              label="User ID"
              value={filters.user_id ?? ""}
              onChange={(e) =>
                setFilters((f) => ({
                  ...f,
                  user_id: e.target.value ? Number(e.target.value) : undefined,
                }))
              }
              fullWidth
            />
          </Grid>
          <Grid item xs={12} md={3}>
            <TextField
              label="Action"
              value={filters.action ?? ""}
              onChange={(e) =>
                setFilters((f) => ({
                  ...f,
                  action: e.target.value || undefined,
                }))
              }
              fullWidth
            />
          </Grid>
          <Grid item xs={12} md={3}>
            <TextField
              label="Resource"
              value={filters.resource ?? ""}
              onChange={(e) =>
                setFilters((f) => ({
                  ...f,
                  resource: e.target.value || undefined,
                }))
              }
              fullWidth
            />
          </Grid>
          <Grid item xs={12} md={2}>
            <TextField
              label="Start (ISO)"
              value={filters.start ?? ""}
              onChange={(e) =>
                setFilters((f) => ({
                  ...f,
                  start: e.target.value || undefined,
                }))
              }
              fullWidth
            />
          </Grid>
          <Grid item xs={12} md={2}>
            <TextField
              label="End (ISO)"
              value={filters.end ?? ""}
              onChange={(e) =>
                setFilters((f) => ({ ...f, end: e.target.value || undefined }))
              }
              fullWidth
            />
          </Grid>
          <Grid item xs={12} md={2}>
            <Button
              variant="contained"
              onClick={load}
              disabled={loading}
              fullWidth
            >
              {loading ? "Loading..." : "Filter"}
            </Button>
          </Grid>
          <Grid item xs={12} md={2}>
            <Button variant="outlined" onClick={onExport} fullWidth>
              Export CSV
            </Button>
          </Grid>
        </Grid>
      </Paper>

      <Paper sx={{ p: 2 }}>
        <Box
          component="table"
          sx={{ width: "100%", borderCollapse: "collapse" }}
        >
          <Box component="thead">
            <Box component="tr">
              <Box component="th" sx={{ textAlign: "left", p: 1 }}>
                ID
              </Box>
              <Box component="th" sx={{ textAlign: "left", p: 1 }}>
                User
              </Box>
              <Box component="th" sx={{ textAlign: "left", p: 1 }}>
                Action
              </Box>
              <Box component="th" sx={{ textAlign: "left", p: 1 }}>
                Resource
              </Box>
              <Box component="th" sx={{ textAlign: "left", p: 1 }}>
                Details
              </Box>
              <Box component="th" sx={{ textAlign: "left", p: 1 }}>
                IP
              </Box>
              <Box component="th" sx={{ textAlign: "left", p: 1 }}>
                User-Agent
              </Box>
              <Box component="th" sx={{ textAlign: "left", p: 1 }}>
                Time
              </Box>
            </Box>
          </Box>
          <Box component="tbody">
            {rows.map((r) => (
              <Box component="tr" key={r.id}>
                <Box component="td" sx={{ p: 1 }}>
                  {r.id}
                </Box>
                <Box component="td" sx={{ p: 1 }}>
                  {r.user_id ?? "-"}
                </Box>
                <Box component="td" sx={{ p: 1 }}>
                  {r.action}
                </Box>
                <Box component="td" sx={{ p: 1 }}>
                  {r.resource ?? "-"}
                </Box>
                <Box component="td" sx={{ p: 1 }}>
                  {typeof r.details === "string"
                    ? r.details
                    : JSON.stringify(r.details)}
                </Box>
                <Box component="td" sx={{ p: 1 }}>
                  {r.ip_address ?? "-"}
                </Box>
                <Box component="td" sx={{ p: 1 }}>
                  {r.user_agent
                    ? r.user_agent.substring(0, 80) +
                      (r.user_agent.length > 80 ? "…" : "")
                    : "-"}
                </Box>
                <Box component="td" sx={{ p: 1 }}>
                  {r.created_at
                    ? dayjs(r.created_at).format("YYYY-MM-DD HH:mm:ss")
                    : "-"}
                </Box>
              </Box>
            ))}
          </Box>
        </Box>
      </Paper>
    </Box>
  );
}
