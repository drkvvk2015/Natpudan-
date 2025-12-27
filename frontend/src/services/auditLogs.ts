import apiClient from "./apiClient";

export interface AuditLogItem {
  id: number;
  user_id?: number;
  action: string;
  resource?: string;
  details?: any;
  ip_address?: string;
  user_agent?: string;
  created_at?: string;
}

export async function fetchAuditLogs(params: {
  user_id?: number;
  action?: string;
  resource?: string;
  start?: string;
  end?: string;
  limit?: number;
  offset?: number;
}): Promise<{ items: AuditLogItem[]; count: number; offset: number; limit: number }>
{
  const { data } = await apiClient.get("/api/admin/audit-logs", { params });
  return data;
}

export async function createAuditLog(payload: {
  user_id?: number;
  action: string;
  resource?: string;
  details?: any;
}) {
  const { data } = await apiClient.post("/api/admin/audit-logs", payload);
  return data as AuditLogItem;
}

export async function exportAuditLogsCSV(params: {
  user_id?: number;
  action?: string;
  resource?: string;
  start?: string;
  end?: string;
}) {
  const resp = await apiClient.get("/api/admin/audit-logs/export", {
    params,
    responseType: "blob",
  });
  return resp.data as Blob;
}
