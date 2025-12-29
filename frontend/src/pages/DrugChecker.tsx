import React, { useState, useEffect } from "react";
import {
  Box,
  Typography,
  Paper,
  TextField,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  CircularProgress,
  Alert,
  Autocomplete,
  Card,
  CardContent,
  Grid,
  Icon,
  Tooltip,
} from "@mui/material";
import { styled } from "@mui/material/styles";

interface DrugInteraction {
  drug1: string;
  drug2: string;
  severity: "high" | "moderate" | "low";
  description: string;
  mechanism?: string;
  recommendation?: string;
}

interface CheckResponse {
  total_interactions: number;
  high_risk_warning: boolean;
  severity_breakdown: {
    high: number;
    moderate: number;
    low: number;
  };
  interactions?: DrugInteraction[];
}

const StyledPaper = styled(Paper)(({ theme }) => ({
  padding: theme.spacing(3),
  borderRadius: theme.spacing(1),
  boxShadow: theme.shadows[2],
}));

const SeverityChip = styled(Chip)(({ theme }) => ({
  fontWeight: 600,
}));

const DrugChecker: React.FC = () => {
  const [medications, setMedications] = useState<string[]>([]);
  const [newMedication, setNewMedication] = useState<string>("");
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<CheckResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [showResults, setShowResults] = useState(false);

  // Sample medication list for autocomplete
  const commonMedications = [
    "Warfarin",
    "Aspirin",
    "Amiodarone",
    "Metformin",
    "Lisinopril",
    "Amoxicillin",
    "Ibuprofen",
    "Naproxen",
    "Acetaminophen",
    "Metoprolol",
    "Atorvastatin",
    "Simvastatin",
    "Omeprazole",
    "Ranitidine",
    "Levothyroxine",
    "NSAIDs",
    "ACE inhibitors",
    "Beta-blockers",
    "Statins",
    "Azithromycin",
    "Clopidogrel",
    "Rivaroxaban",
    "Apixaban",
    "Heparin",
    "Citalopram",
    "Sertraline",
    "Fluoxetine",
    "Ketoconazole",
    "Clarithromycin",
  ];

  const handleAddMedication = () => {
    if (newMedication.trim() && !medications.includes(newMedication.trim())) {
      setMedications([...medications, newMedication.trim()]);
      setNewMedication("");
      setError(null);
    }
  };

  const handleRemoveMedication = (index: number) => {
    setMedications(medications.filter((_, i) => i !== index));
  };

  const handleCheck = async () => {
    if (medications.length < 2) {
      setError("Please add at least 2 medications to check for interactions");
      return;
    }

    setLoading(true);
    setError(null);
    setShowResults(false);

    try {
      const response = await fetch(
        "http://127.0.0.1:8001/api/prescription/check-interactions",
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${localStorage.getItem("token") || ""}`,
          },
          body: JSON.stringify({ medications }),
        }
      );

      if (!response.ok) {
        throw new Error(`API error: ${response.statusText}`);
      }

      const data: CheckResponse = await response.json();
      setResults(data);
      setShowResults(true);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Failed to check interactions"
      );
      setShowResults(false);
    } finally {
      setLoading(false);
    }
  };

  const getSeverityColor = (
    severity: string
  ): "error" | "warning" | "success" => {
    switch (severity.toLowerCase()) {
      case "high":
        return "error";
      case "moderate":
        return "warning";
      case "low":
        return "success";
      default:
        return "success";
    }
  };

  const getSeverityIcon = (severity: string) => {
    switch (severity.toLowerCase()) {
      case "high":
        return "[ALARM]";
      case "moderate":
        return "[WARN]";
      case "low":
        return "[INFO]";
      default:
        return "[INFO]";
    }
  };

  return (
    <Box sx={{ p: 2 }}>
      <Typography variant="h4" gutterBottom sx={{ fontWeight: 600, mb: 3 }}>
        Drug Interaction Checker
      </Typography>

      <Grid container spacing={3}>
        {/* Input Form Section */}
        <Grid item xs={12} md={6}>
          <StyledPaper>
            <Typography variant="h6" gutterBottom sx={{ fontWeight: 600 }}>
              Add Medications
            </Typography>
            <Typography variant="body2" color="textSecondary" sx={{ mb: 2 }}>
              Search and add medications to check for potential interactions
            </Typography>

            {/* Medication Input */}
            <Box sx={{ mb: 2, display: "flex", gap: 1 }}>
              <Autocomplete
                freeSolo
                options={commonMedications}
                value={newMedication}
                onChange={(_, newValue) => {
                  setNewMedication(newValue || "");
                }}
                onInputChange={(_, newInputValue) => {
                  setNewMedication(newInputValue);
                }}
                renderInput={(params) => (
                  <TextField
                    {...params}
                    label="Medication name"
                    placeholder="Search or type..."
                    fullWidth
                    onKeyPress={(e) => {
                      if (e.key === "Enter") {
                        handleAddMedication();
                        e.preventDefault();
                      }
                    }}
                  />
                )}
                sx={{ flex: 1 }}
              />
              <Button
                variant="contained"
                onClick={handleAddMedication}
                sx={{ mt: 1 }}
              >
                Add
              </Button>
            </Box>

            {/* Medication List */}
            <Box sx={{ mb: 2 }}>
              <Typography variant="subtitle2" sx={{ mb: 1, fontWeight: 600 }}>
                Selected Medications ({medications.length})
              </Typography>
              <Box sx={{ display: "flex", flexWrap: "wrap", gap: 1 }}>
                {medications.length === 0 ? (
                  <Typography variant="body2" color="textSecondary">
                    No medications added yet
                  </Typography>
                ) : (
                  medications.map((med, idx) => (
                    <Chip
                      key={idx}
                      label={med}
                      onDelete={() => handleRemoveMedication(idx)}
                      color="primary"
                      variant="outlined"
                    />
                  ))
                )}
              </Box>
            </Box>

            {/* Error Message */}
            {error && (
              <Alert severity="error" sx={{ mb: 2 }}>
                {error}
              </Alert>
            )}

            {/* Check Button */}
            <Button
              variant="contained"
              color="primary"
              fullWidth
              onClick={handleCheck}
              disabled={loading || medications.length < 2}
              sx={{ py: 1.5, fontWeight: 600 }}
            >
              {loading ? (
                <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
                  <CircularProgress size={20} />
                  Checking...
                </Box>
              ) : (
                "Check for Interactions"
              )}
            </Button>
          </StyledPaper>

          {/* Summary Card */}
          {showResults && results && (
            <Card sx={{ mt: 2 }}>
              <CardContent>
                <Typography variant="h6" gutterBottom sx={{ fontWeight: 600 }}>
                  Summary
                </Typography>
                <Box
                  sx={{
                    display: "grid",
                    gridTemplateColumns: "1fr 1fr",
                    gap: 1,
                  }}
                >
                  <Box>
                    <Typography variant="body2" color="textSecondary">
                      Total Interactions
                    </Typography>
                    <Typography variant="h6" sx={{ fontWeight: 600 }}>
                      {results.total_interactions}
                    </Typography>
                  </Box>
                  <Box>
                    <Typography variant="body2" color="textSecondary">
                      Risk Level
                    </Typography>
                    <Typography
                      variant="h6"
                      sx={{
                        fontWeight: 600,
                        color: results.high_risk_warning
                          ? "#d32f2f"
                          : "#388e3c",
                      }}
                    >
                      {results.high_risk_warning ? "HIGH RISK" : "SAFE"}
                    </Typography>
                  </Box>
                </Box>

                {/* Severity Breakdown */}
                <Box sx={{ mt: 2 }}>
                  <Typography
                    variant="subtitle2"
                    sx={{ mb: 1, fontWeight: 600 }}
                  >
                    By Severity
                  </Typography>
                  <Box
                    sx={{
                      display: "grid",
                      gridTemplateColumns: "1fr 1fr 1fr",
                      gap: 1,
                    }}
                  >
                    <Box>
                      <Typography variant="caption" color="textSecondary">
                        High
                      </Typography>
                      <Typography
                        variant="body2"
                        sx={{ fontWeight: 600, color: "#d32f2f" }}
                      >
                        {results.severity_breakdown.high}
                      </Typography>
                    </Box>
                    <Box>
                      <Typography variant="caption" color="textSecondary">
                        Moderate
                      </Typography>
                      <Typography
                        variant="body2"
                        sx={{ fontWeight: 600, color: "#f57c00" }}
                      >
                        {results.severity_breakdown.moderate}
                      </Typography>
                    </Box>
                    <Box>
                      <Typography variant="caption" color="textSecondary">
                        Low
                      </Typography>
                      <Typography
                        variant="body2"
                        sx={{ fontWeight: 600, color: "#388e3c" }}
                      >
                        {results.severity_breakdown.low}
                      </Typography>
                    </Box>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          )}
        </Grid>

        {/* Results Section */}
        <Grid item xs={12} md={6}>
          {showResults && results ? (
            <StyledPaper>
              {results.total_interactions === 0 ? (
                <Alert severity="success" sx={{ mb: 2 }}>
                  No interactions detected. The selected medications are
                  generally safe to use together.
                </Alert>
              ) : (
                <>
                  {results.high_risk_warning && (
                    <Alert severity="error" sx={{ mb: 2 }}>
                      [ALARM] High-risk interactions detected. Review details
                      below and consult with clinical staff.
                    </Alert>
                  )}

                  <Typography
                    variant="h6"
                    gutterBottom
                    sx={{ fontWeight: 600 }}
                  >
                    Interaction Details
                  </Typography>

                  <TableContainer sx={{ maxHeight: 500 }}>
                    <Table stickyHeader>
                      <TableHead>
                        <TableRow sx={{ backgroundColor: "#f5f5f5" }}>
                          <TableCell sx={{ fontWeight: 600 }}>Drug 1</TableCell>
                          <TableCell sx={{ fontWeight: 600 }}>Drug 2</TableCell>
                          <TableCell sx={{ fontWeight: 600 }}>
                            Severity
                          </TableCell>
                          <TableCell sx={{ fontWeight: 600 }}>
                            Description
                          </TableCell>
                        </TableRow>
                      </TableHead>
                      <TableBody>
                        {results.interactions &&
                        results.interactions.length > 0 ? (
                          results.interactions.map((interaction, idx) => (
                            <Tooltip
                              key={idx}
                              title={`Mechanism: ${
                                interaction.mechanism || "Unknown"
                              }\nRecommendation: ${
                                interaction.recommendation || "Monitor closely"
                              }`}
                              arrow
                            >
                              <TableRow
                                sx={{
                                  "&:hover": { backgroundColor: "#fafafa" },
                                  borderLeft:
                                    interaction.severity === "high"
                                      ? "4px solid #d32f2f"
                                      : interaction.severity === "moderate"
                                      ? "4px solid #f57c00"
                                      : "4px solid #388e3c",
                                }}
                              >
                                <TableCell sx={{ fontWeight: 500 }}>
                                  {interaction.drug1}
                                </TableCell>
                                <TableCell sx={{ fontWeight: 500 }}>
                                  {interaction.drug2}
                                </TableCell>
                                <TableCell>
                                  <SeverityChip
                                    label={`${getSeverityIcon(
                                      interaction.severity
                                    )} ${interaction.severity.toUpperCase()}`}
                                    color={getSeverityColor(
                                      interaction.severity
                                    )}
                                    variant="filled"
                                    size="small"
                                  />
                                </TableCell>
                                <TableCell sx={{ fontSize: "0.875rem" }}>
                                  {interaction.description}
                                </TableCell>
                              </TableRow>
                            </Tooltip>
                          ))
                        ) : (
                          <TableRow>
                            <TableCell colSpan={4} align="center">
                              No detailed interaction data available
                            </TableCell>
                          </TableRow>
                        )}
                      </TableBody>
                    </Table>
                  </TableContainer>
                </>
              )}
            </StyledPaper>
          ) : (
            <StyledPaper>
              <Box sx={{ textAlign: "center", py: 4 }}>
                <Typography variant="h6" color="textSecondary" gutterBottom>
                  No Results Yet
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  Add medications and click "Check for Interactions" to see
                  results
                </Typography>
              </Box>
            </StyledPaper>
          )}
        </Grid>
      </Grid>

      {/* Information Section */}
      <Paper sx={{ mt: 3, p: 2, backgroundColor: "#f5f5f5" }}>
        <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 1 }}>
          [INFO] About Severity Levels
        </Typography>
        <Box
          sx={{
            display: "grid",
            gridTemplateColumns: { xs: "1fr", sm: "1fr 1fr 1fr" },
            gap: 2,
          }}
        >
          <Box>
            <SeverityChip
              label="[ALARM] HIGH"
              color="error"
              variant="filled"
              size="small"
              sx={{ mb: 1 }}
            />
            <Typography variant="caption" color="textSecondary">
              Significant clinical consequence. Consider alternative or close
              monitoring.
            </Typography>
          </Box>
          <Box>
            <SeverityChip
              label="[WARN] MODERATE"
              color="warning"
              variant="filled"
              size="small"
              sx={{ mb: 1 }}
            />
            <Typography variant="caption" color="textSecondary">
              Some potential concern. May need dose adjustment or monitoring.
            </Typography>
          </Box>
          <Box>
            <SeverityChip
              label="[INFO] LOW"
              color="success"
              variant="filled"
              size="small"
              sx={{ mb: 1 }}
            />
            <Typography variant="caption" color="textSecondary">
              Minimal clinical consequence. Usually safe to combine.
            </Typography>
          </Box>
        </Box>
      </Paper>
    </Box>
  );
};

export default DrugChecker;
