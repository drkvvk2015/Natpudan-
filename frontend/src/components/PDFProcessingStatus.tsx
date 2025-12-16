import React, { useState, useEffect, useCallback } from "react";
import {
  AlertCircle,
  CheckCircle,
  Clock,
  PauseCircle,
  PlayCircle,
  Trash2,
  Loader,
} from "lucide-react";
import apiClient from "../services/apiClient";

interface ProcessingJob {
  id: number;
  pdf_name: string;
  status: "PENDING" | "PROCESSING" | "PAUSED" | "COMPLETED" | "FAILED";
  progress_percentage: number;
  pages_processed: number;
  total_pages: number;
  embeddings_created: number;
  created_at: string;
  started_at: string | null;
  completed_at: string | null;
  error_message: string | null;
}

interface PDFProcessingStatusProps {
  refreshInterval?: number; // milliseconds
  autoRefresh?: boolean;
}

export const PDFProcessingStatus: React.FC<PDFProcessingStatusProps> = ({
  refreshInterval = 2000,
  autoRefresh = true,
}) => {
  const [jobs, setJobs] = useState<ProcessingJob[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [actionLoading, setActionLoading] = useState<Record<number, boolean>>(
    {}
  );

  const fetchJobs = useCallback(async () => {
    try {
      const response = await apiClient.get(
        "/api/knowledge-base/pdf/processing-list"
      );
      setJobs(response.data.data || []);
      setError(null);
    } catch (err) {
      setError("Failed to fetch processing jobs");
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchJobs();

    if (!autoRefresh) return;

    const interval = setInterval(fetchJobs, refreshInterval);
    return () => clearInterval(interval);
  }, [fetchJobs, refreshInterval, autoRefresh]);

  const handlePause = async (jobId: number) => {
    setActionLoading((prev) => ({ ...prev, [jobId]: true }));
    try {
      await apiClient.post(`/api/knowledge-base/pdf/pause/${jobId}`);
      await fetchJobs();
    } catch (err) {
      console.error("Failed to pause job:", err);
    } finally {
      setActionLoading((prev) => ({ ...prev, [jobId]: false }));
    }
  };

  const handleResume = async (jobId: number) => {
    setActionLoading((prev) => ({ ...prev, [jobId]: true }));
    try {
      await apiClient.post(`/api/knowledge-base/pdf/resume/${jobId}`);
      await fetchJobs();
    } catch (err) {
      console.error("Failed to resume job:", err);
    } finally {
      setActionLoading((prev) => ({ ...prev, [jobId]: false }));
    }
  };

  const handleCancel = async (jobId: number) => {
    if (!window.confirm("Are you sure you want to cancel this job?")) return;

    setActionLoading((prev) => ({ ...prev, [jobId]: true }));
    try {
      await apiClient.post(`/api/knowledge-base/pdf/cancel/${jobId}`);
      await fetchJobs();
    } catch (err) {
      console.error("Failed to cancel job:", err);
    } finally {
      setActionLoading((prev) => ({ ...prev, [jobId]: false }));
    }
  };

  const getStatusIcon = (status: ProcessingJob["status"]) => {
    switch (status) {
      case "COMPLETED":
        return <CheckCircle className="w-5 h-5 text-green-500" />;
      case "PROCESSING":
        return <Loader className="w-5 h-5 text-blue-500 animate-spin" />;
      case "PAUSED":
        return <PauseCircle className="w-5 h-5 text-yellow-500" />;
      case "FAILED":
        return <AlertCircle className="w-5 h-5 text-red-500" />;
      case "PENDING":
        return <Clock className="w-5 h-5 text-gray-500" />;
      default:
        return null;
    }
  };

  const getStatusBadge = (status: ProcessingJob["status"]) => {
    const baseClasses = "px-3 py-1 rounded-full text-sm font-medium";
    switch (status) {
      case "COMPLETED":
        return `${baseClasses} bg-green-100 text-green-800`;
      case "PROCESSING":
        return `${baseClasses} bg-blue-100 text-blue-800`;
      case "PAUSED":
        return `${baseClasses} bg-yellow-100 text-yellow-800`;
      case "FAILED":
        return `${baseClasses} bg-red-100 text-red-800`;
      case "PENDING":
        return `${baseClasses} bg-gray-100 text-gray-800`;
      default:
        return baseClasses;
    }
  };

  if (loading && jobs.length === 0) {
    return <div className="text-center py-8">Loading processing jobs...</div>;
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <div className="flex items-center">
          <AlertCircle className="w-5 h-5 text-red-600 mr-2" />
          <span className="text-red-800">{error}</span>
        </div>
      </div>
    );
  }

  if (jobs.length === 0) {
    return (
      <div className="text-center py-8 text-gray-500">
        No PDF processing jobs yet
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-lg font-semibold">PDF Processing Jobs</h2>
        <button
          onClick={fetchJobs}
          className="text-sm text-blue-600 hover:text-blue-800"
        >
          Refresh
        </button>
      </div>

      {jobs.map((job) => (
        <div
          key={job.id}
          className="border rounded-lg p-4 bg-white shadow-sm hover:shadow-md transition-shadow"
        >
          <div className="flex items-start justify-between mb-3">
            <div className="flex items-center gap-3 flex-1">
              {getStatusIcon(job.status)}
              <div className="flex-1">
                <h3 className="font-medium text-gray-900">{job.pdf_name}</h3>
                <p className="text-sm text-gray-500">
                  {job.pages_processed} / {job.total_pages} pages processed
                </p>
              </div>
            </div>
            <span className={getStatusBadge(job.status)}>
              {job.status.replace(/_/g, " ")}
            </span>
          </div>

          {/* Progress Bar */}
          <div className="mb-4">
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                style={{ width: `${job.progress_percentage}%` }}
              />
            </div>
            <div className="flex justify-between items-center mt-2 text-xs text-gray-600">
              <span>{job.progress_percentage}% complete</span>
              <span>{job.embeddings_created} embeddings created</span>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex gap-2 justify-end">
            {job.status === "PROCESSING" && (
              <button
                onClick={() => handlePause(job.id)}
                disabled={actionLoading[job.id]}
                className="flex items-center gap-1 px-3 py-1.5 bg-yellow-500 hover:bg-yellow-600 text-white rounded text-sm disabled:opacity-50"
              >
                <PauseCircle className="w-4 h-4" />
                Pause
              </button>
            )}

            {job.status === "PAUSED" && (
              <button
                onClick={() => handleResume(job.id)}
                disabled={actionLoading[job.id]}
                className="flex items-center gap-1 px-3 py-1.5 bg-green-500 hover:bg-green-600 text-white rounded text-sm disabled:opacity-50"
              >
                <PlayCircle className="w-4 h-4" />
                Resume
              </button>
            )}

            {(job.status === "PROCESSING" ||
              job.status === "PAUSED" ||
              job.status === "PENDING") && (
              <button
                onClick={() => handleCancel(job.id)}
                disabled={actionLoading[job.id]}
                className="flex items-center gap-1 px-3 py-1.5 bg-red-500 hover:bg-red-600 text-white rounded text-sm disabled:opacity-50"
              >
                <Trash2 className="w-4 h-4" />
                Cancel
              </button>
            )}
          </div>

          {/* Error Message */}
          {job.error_message && (
            <div className="mt-3 p-2 bg-red-50 border border-red-200 rounded text-sm text-red-700">
              <strong>Error:</strong> {job.error_message}
            </div>
          )}

          {/* Timestamps */}
          <div className="mt-3 text-xs text-gray-500 space-y-1">
            {job.started_at && (
              <p>Started: {new Date(job.started_at).toLocaleString()}</p>
            )}
            {job.completed_at && (
              <p>Completed: {new Date(job.completed_at).toLocaleString()}</p>
            )}
          </div>
        </div>
      ))}
    </div>
  );
};

export default PDFProcessingStatus;
