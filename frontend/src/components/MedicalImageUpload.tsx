/**
 * Medical Image Upload Component
 *
 * Allows doctors to upload medical images (X-ray, ECG, ultrasound, etc.)
 * for AI analysis using Claude Vision API.
 *
 * Features:
 * - Drag-and-drop file upload
 * - Image type selection
 * - Clinical context input
 * - Real-time analysis status
 * - Display AI findings with severity
 */

import React, { useState } from "react";
import {
  Box,
  Button,
  Card,
  CardContent,
  CircularProgress,
  FormControl,
  InputLabel,
  MenuItem,
  Select,
  TextField,
  Typography,
  Alert,
  Chip,
  Grid,
  Paper,
  List,
  ListItem,
  ListItemText,
} from "@mui/material";
import {
  CloudUpload as CloudUploadIcon,
  CheckCircle as CheckCircleIcon,
  Warning as WarningIcon,
  Error as ErrorIcon,
} from "@mui/icons-material";
import axios from "axios";

interface AnalysisResult {
  image_id: number;
  image_type: string;
  findings: string[];
  severity: string;
  confidence: number;
  differential_diagnoses: string[];
  recommendations: string[];
  ai_analysis_date: string;
}

const IMAGE_TYPES = [
  { value: "xray", label: "X-Ray" },
  { value: "ecg", label: "ECG/EKG" },
  { value: "ultrasound", label: "Ultrasound" },
  { value: "pathology", label: "Pathology Slide" },
  { value: "mri", label: "MRI" },
  { value: "ct", label: "CT Scan" },
];

const SEVERITY_COLORS: Record<string, string> = {
  CRITICAL: "error",
  HIGH: "warning",
  MODERATE: "info",
  LOW: "success",
  NORMAL: "success",
};

export default function MedicalImageUpload() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [imageType, setImageType] = useState<string>("xray");
  const [clinicalContext, setClinicalContext] = useState<string>("");
  const [patientId, setPatientId] = useState<number | null>(null);
  const [analyzing, setAnalyzing] = useState<boolean>(false);
  const [analysisResult, setAnalysisResult] = useState<AnalysisResult | null>(
    null
  );
  const [error, setError] = useState<string | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [dragOver, setDragOver] = useState<boolean>(false);

  const handleFileSelect = (file: File) => {
    if (!file.type.startsWith("image/")) {
      setError("Please select a valid image file");
      return;
    }

    setSelectedFile(file);
    setError(null);

    // Create preview
    const reader = new FileReader();
    reader.onloadend = () => {
      setPreview(reader.result as string);
    };
    reader.readAsDataURL(file);
  };

  const handleFileInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      handleFileSelect(e.target.files[0]);
    }
  };

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setDragOver(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileSelect(e.dataTransfer.files[0]);
    }
  };

  const handleDragOver = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setDragOver(true);
  };

  const handleDragLeave = () => {
    setDragOver(false);
  };

  const handleAnalyze = async () => {
    if (!selectedFile) {
      setError("Please select an image file");
      return;
    }

    setAnalyzing(true);
    setError(null);
    setAnalysisResult(null);

    try {
      const formData = new FormData();
      formData.append("image", selectedFile);

      const response = await axios.post<AnalysisResult>(
        `/api/phase-4/image/analyze?image_type=${imageType}&clinical_context=${encodeURIComponent(
          clinicalContext || ""
        )}&patient_id=${patientId || ""}`,
        formData,
        {
          headers: {
            "Content-Type": "multipart/form-data",
          },
        }
      );

      setAnalysisResult(response.data);
    } catch (err: any) {
      setError(
        err.response?.data?.detail || "Analysis failed. Please try again."
      );
      console.error("Analysis error:", err);
    } finally {
      setAnalyzing(false);
    }
  };

  const handleReset = () => {
    setSelectedFile(null);
    setPreview(null);
    setAnalysisResult(null);
    setError(null);
    setClinicalContext("");
  };

  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case "CRITICAL":
      case "HIGH":
        return <ErrorIcon color="error" />;
      case "MODERATE":
        return <WarningIcon color="warning" />;
      case "LOW":
      case "NORMAL":
        return <CheckCircleIcon color="success" />;
      default:
        return null;
    }
  };

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Medical Image Analysis
      </Typography>
      <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
        Upload medical images for AI-powered analysis using Claude Vision
      </Typography>

      <Grid container spacing={3}>
        {/* Upload Section */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Upload Image
              </Typography>

              {/* Drag & Drop Zone */}
              {!preview && (
                <Paper
                  onDrop={handleDrop}
                  onDragOver={handleDragOver}
                  onDragLeave={handleDragLeave}
                  sx={{
                    p: 4,
                    textAlign: "center",
                    border: dragOver
                      ? "2px dashed primary.main"
                      : "2px dashed grey.300",
                    bgcolor: dragOver ? "action.hover" : "background.default",
                    cursor: "pointer",
                    transition: "all 0.2s",
                  }}
                >
                  <CloudUploadIcon
                    sx={{ fontSize: 64, color: "text.secondary", mb: 2 }}
                  />
                  <Typography variant="body1" gutterBottom>
                    Drag & drop an image here
                  </Typography>
                  <Typography
                    variant="body2"
                    color="text.secondary"
                    sx={{ mb: 2 }}
                  >
                    or
                  </Typography>
                  <Button variant="contained" component="label">
                    Choose File
                    <input
                      type="file"
                      hidden
                      accept="image/*"
                      onChange={handleFileInputChange}
                    />
                  </Button>
                </Paper>
              )}

              {/* Image Preview */}
              {preview && (
                <Box sx={{ mb: 2 }}>
                  <img
                    src={preview}
                    alt="Preview"
                    style={{
                      width: "100%",
                      maxHeight: "300px",
                      objectFit: "contain",
                      borderRadius: "8px",
                    }}
                  />
                  <Typography variant="caption" display="block" sx={{ mt: 1 }}>
                    {selectedFile?.name} (
                    {(selectedFile?.size || 0 / 1024 / 1024).toFixed(2)} MB)
                  </Typography>
                </Box>
              )}

              {/* Image Type Selection */}
              <FormControl fullWidth sx={{ mb: 2 }}>
                <InputLabel>Image Type</InputLabel>
                <Select
                  value={imageType}
                  label="Image Type"
                  onChange={(e) => setImageType(e.target.value)}
                >
                  {IMAGE_TYPES.map((type) => (
                    <MenuItem key={type.value} value={type.value}>
                      {type.label}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>

              {/* Patient ID (Optional) */}
              <TextField
                fullWidth
                label="Patient ID (Optional)"
                type="number"
                value={patientId || ""}
                onChange={(e) =>
                  setPatientId(e.target.value ? parseInt(e.target.value) : null)
                }
                sx={{ mb: 2 }}
              />

              {/* Clinical Context */}
              <TextField
                fullWidth
                label="Clinical Context (Optional)"
                multiline
                rows={3}
                value={clinicalContext}
                onChange={(e) => setClinicalContext(e.target.value)}
                placeholder="Patient history, symptoms, previous diagnoses..."
                sx={{ mb: 2 }}
              />

              {/* Action Buttons */}
              <Box sx={{ display: "flex", gap: 2 }}>
                <Button
                  variant="contained"
                  color="primary"
                  onClick={handleAnalyze}
                  disabled={!selectedFile || analyzing}
                  fullWidth
                  startIcon={analyzing ? <CircularProgress size={20} /> : null}
                >
                  {analyzing ? "Analyzing..." : "Analyze Image"}
                </Button>
                <Button
                  variant="outlined"
                  onClick={handleReset}
                  disabled={analyzing}
                >
                  Reset
                </Button>
              </Box>

              {/* Error Alert */}
              {error && (
                <Alert severity="error" sx={{ mt: 2 }}>
                  {error}
                </Alert>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Results Section */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Analysis Results
              </Typography>

              {!analysisResult && !analyzing && (
                <Box sx={{ textAlign: "center", py: 4 }}>
                  <Typography variant="body2" color="text.secondary">
                    Upload and analyze an image to see results here
                  </Typography>
                </Box>
              )}

              {analyzing && (
                <Box sx={{ textAlign: "center", py: 4 }}>
                  <CircularProgress />
                  <Typography variant="body2" sx={{ mt: 2 }}>
                    Analyzing image with Claude Vision AI...
                  </Typography>
                </Box>
              )}

              {analysisResult && (
                <Box>
                  {/* Severity Badge */}
                  <Box
                    sx={{
                      display: "flex",
                      alignItems: "center",
                      gap: 1,
                      mb: 2,
                    }}
                  >
                    {getSeverityIcon(analysisResult.severity)}
                    <Chip
                      label={analysisResult.severity}
                      color={SEVERITY_COLORS[analysisResult.severity] as any}
                      size="small"
                    />
                    <Typography variant="caption" color="text.secondary">
                      Confidence: {(analysisResult.confidence * 100).toFixed(1)}
                      %
                    </Typography>
                  </Box>

                  {/* Findings */}
                  <Typography variant="subtitle2" gutterBottom>
                    Findings:
                  </Typography>
                  <List dense sx={{ mb: 2 }}>
                    {analysisResult.findings.map((finding, idx) => (
                      <ListItem key={idx}>
                        <ListItemText primary={`• ${finding}`} />
                      </ListItem>
                    ))}
                  </List>

                  {/* Differential Diagnoses */}
                  {analysisResult.differential_diagnoses.length > 0 && (
                    <>
                      <Typography variant="subtitle2" gutterBottom>
                        Differential Diagnoses:
                      </Typography>
                      <List dense sx={{ mb: 2 }}>
                        {analysisResult.differential_diagnoses.map(
                          (diagnosis, idx) => (
                            <ListItem key={idx}>
                              <ListItemText primary={`• ${diagnosis}`} />
                            </ListItem>
                          )
                        )}
                      </List>
                    </>
                  )}

                  {/* Recommendations */}
                  {analysisResult.recommendations.length > 0 && (
                    <>
                      <Typography variant="subtitle2" gutterBottom>
                        Recommendations:
                      </Typography>
                      <List dense sx={{ mb: 2 }}>
                        {analysisResult.recommendations.map((rec, idx) => (
                          <ListItem key={idx}>
                            <ListItemText primary={`• ${rec}`} />
                          </ListItem>
                        ))}
                      </List>
                    </>
                  )}

                  {/* Metadata */}
                  <Typography
                    variant="caption"
                    color="text.secondary"
                    display="block"
                  >
                    Image ID: {analysisResult.image_id}
                  </Typography>
                  <Typography
                    variant="caption"
                    color="text.secondary"
                    display="block"
                  >
                    Analyzed:{" "}
                    {new Date(analysisResult.ai_analysis_date).toLocaleString()}
                  </Typography>

                  {/* Action Button */}
                  <Button
                    variant="outlined"
                    fullWidth
                    sx={{ mt: 2 }}
                    onClick={() => {
                      // TODO: Navigate to image details page
                      window.location.href = `/images/${analysisResult.image_id}`;
                    }}
                  >
                    View Full Report
                  </Button>
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
}
