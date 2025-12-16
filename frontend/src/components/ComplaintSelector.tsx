/**
 * ComplaintSelector Component
 * Simplified mouse-click interface for selecting chief complaints with structured data entry
 */

import React, { useState, useEffect } from "react";
import {
  Box,
  Button,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  FormControl,
  Grid,
  InputLabel,
  MenuItem,
  Paper,
  Select,
  SelectChangeEvent,
  Slider,
  TextField,
  Typography,
  Autocomplete,
  IconButton,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Stack,
} from "@mui/material";
import {
  Add as AddIcon,
  Delete as DeleteIcon,
  ExpandMore as ExpandMoreIcon,
  AccessTime as TimeIcon,
  TrendingUp as TrendingUpIcon,
  TrendingDown as TrendingDownIcon,
} from "@mui/icons-material";

// ==================== Types ====================

export interface ChiefComplaint {
  complaint: string;
  onset: string;
  duration: string;
  severity: string;
  character?: string;
  location?: string;
  radiation?: string;
  relieving_factors: string[];
  aggravating_factors: string[];
  associated_symptoms: string[];
  progression: string;
  timing?: string;
  quality?: string;
}

interface ComplaintSelectorProps {
  complaints: ChiefComplaint[];
  onChange: (complaints: ChiefComplaint[]) => void;
}

// ==================== Common Options ====================

const COMPLAINT_CATEGORIES = {
  "General/Constitutional": [
    "Fever",
    "Chills",
    "Fatigue",
    "Weight loss",
    "Weight gain",
    "Night sweats",
    "Weakness",
    "Malaise",
  ],
  Respiratory: [
    "Cough",
    "Shortness of breath",
    "Chest pain",
    "Wheezing",
    "Hemoptysis",
    "Sputum production",
  ],
  Cardiovascular: [
    "Chest pressure",
    "Palpitations",
    "Leg swelling",
    "Syncope",
    "Orthopnea",
    "Paroxysmal nocturnal dyspnea",
  ],
  Gastrointestinal: [
    "Nausea",
    "Vomiting",
    "Diarrhea",
    "Constipation",
    "Abdominal pain",
    "Heartburn",
    "Loss of appetite",
    "Blood in stool",
    "Melena",
    "Dysphagia",
    "Bloating",
  ],
  Neurological: [
    "Headache",
    "Dizziness",
    "Vertigo",
    "Confusion",
    "Memory problems",
    "Seizures",
    "Loss of consciousness",
    "Numbness",
    "Tingling",
    "Weakness in limbs",
    "Vision changes",
  ],
  Musculoskeletal: [
    "Joint pain",
    "Muscle pain",
    "Back pain",
    "Neck pain",
    "Stiffness",
    "Swelling in joints",
    "Limited range of motion",
  ],
  Dermatological: [
    "Rash",
    "Itching",
    "Skin lesions",
    "Bruising",
    "Hair loss",
    "Nail changes",
    "Discoloration",
  ],
  ENT: [
    "Sore throat",
    "Ear pain",
    "Runny nose",
    "Nasal congestion",
    "Hearing loss",
    "Tinnitus",
    "Epistaxis",
    "Hoarseness",
  ],
  Genitourinary: [
    "Painful urination",
    "Frequent urination",
    "Blood in urine",
    "Difficulty urinating",
    "Incontinence",
    "Decreased urine output",
  ],
  Psychiatric: [
    "Anxiety",
    "Depression",
    "Insomnia",
    "Mood changes",
    "Hallucinations",
    "Agitation",
  ],
};

const ALL_COMPLAINTS = Object.values(COMPLAINT_CATEGORIES).flat().sort();

const ONSET_OPTIONS = [
  "Today",
  "Yesterday",
  "2 days ago",
  "3 days ago",
  "1 week ago",
  "2 weeks ago",
  "1 month ago",
  "2 months ago",
  "3 months ago",
  "6 months ago",
  "1 year ago",
  "More than 1 year ago",
];

const SEVERITY_OPTIONS = ["Mild", "Moderate", "Severe"];

const PROGRESSION_OPTIONS = [
  "Getting better",
  "Getting worse",
  "Stable",
  "Fluctuating",
];

const TIMING_OPTIONS = [
  "Constant",
  "Intermittent",
  "Morning",
  "Evening",
  "Night",
  "After meals",
  "Before meals",
  "During activity",
  "At rest",
];

const RELIEVING_FACTORS = [
  "Rest",
  "Medication",
  "Cold compress",
  "Heat application",
  "Position change",
  "Deep breathing",
  "Massage",
  "Stretching",
  "Eating",
  "Drinking water",
  "Sleep",
  "Lying down",
  "Sitting up",
  "Movement",
];

const AGGRAVATING_FACTORS = [
  "Physical activity",
  "Stress",
  "Eating",
  "Lying down",
  "Standing",
  "Walking",
  "Coughing",
  "Deep breathing",
  "Cold weather",
  "Hot weather",
  "Night time",
  "Morning",
  "Bending",
  "Lifting",
  "Noise",
  "Light",
  "Touch",
  "Pressure",
];

const CHARACTER_OPTIONS: Record<string, string[]> = {
  Pain: [
    "Sharp",
    "Dull",
    "Aching",
    "Burning",
    "Throbbing",
    "Stabbing",
    "Cramping",
    "Shooting",
  ],
  Cough: ["Dry", "Productive", "Barking", "Hacking"],
  Headache: ["Throbbing", "Pressure", "Sharp", "Dull", "Band-like"],
  Fever: ["High grade", "Low grade", "Intermittent", "Continuous"],
  Dyspnea: ["Gradual onset", "Sudden onset", "Exertional", "At rest"],
};

// ==================== Component ====================

export const ComplaintSelector: React.FC<ComplaintSelectorProps> = ({
  complaints,
  onChange,
}) => {
  const [dialogOpen, setDialogOpen] = useState(false);
  const [currentComplaint, setCurrentComplaint] = useState<ChiefComplaint>({
    complaint: "",
    onset: "",
    duration: "",
    severity: "Moderate",
    character: "",
    location: "",
    radiation: "",
    relieving_factors: [],
    aggravating_factors: [],
    associated_symptoms: [],
    progression: "Stable",
    timing: "",
    quality: "",
  });
  const [editIndex, setEditIndex] = useState<number | null>(null);

  const handleAddComplaint = () => {
    setCurrentComplaint({
      complaint: "",
      onset: "",
      duration: "",
      severity: "Moderate",
      character: "",
      location: "",
      radiation: "",
      relieving_factors: [],
      aggravating_factors: [],
      associated_symptoms: [],
      progression: "Stable",
      timing: "",
      quality: "",
    });
    setEditIndex(null);
    setDialogOpen(true);
  };

  const handleEditComplaint = (index: number) => {
    setCurrentComplaint({ ...complaints[index] });
    setEditIndex(index);
    setDialogOpen(true);
  };

  const handleDeleteComplaint = (index: number) => {
    const newComplaints = complaints.filter((_, i) => i !== index);
    onChange(newComplaints);
  };

  const handleSaveComplaint = () => {
    if (
      !currentComplaint.complaint ||
      !currentComplaint.onset ||
      !currentComplaint.severity
    ) {
      alert("Please fill in required fields: Complaint, Onset, and Severity");
      return;
    }

    if (editIndex !== null) {
      const newComplaints = [...complaints];
      newComplaints[editIndex] = currentComplaint;
      onChange(newComplaints);
    } else {
      onChange([...complaints, currentComplaint]);
    }

    setDialogOpen(false);
  };

  const handleCloseDialog = () => {
    setDialogOpen(false);
    setEditIndex(null);
  };

  const getCharacterOptions = (complaint: string): string[] => {
    for (const [key, options] of Object.entries(CHARACTER_OPTIONS)) {
      if (complaint.toLowerCase().includes(key.toLowerCase())) {
        return options;
      }
    }
    return [];
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case "Mild":
        return "success";
      case "Moderate":
        return "warning";
      case "Severe":
        return "error";
      default:
        return "default";
    }
  };

  const getProgressionIcon = (progression: string) => {
    if (progression === "Getting worse")
      return <TrendingUpIcon fontSize="small" color="error" />;
    if (progression === "Getting better")
      return <TrendingDownIcon fontSize="small" color="success" />;
    return <TimeIcon fontSize="small" />;
  };

  return (
    <Box>
      <Box
        display="flex"
        justifyContent="space-between"
        alignItems="center"
        mb={2}
      >
        <Typography variant="h6">Chief Complaints</Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={handleAddComplaint}
        >
          Add Complaint
        </Button>
      </Box>

      {/* Display complaints in chronological order */}
      {complaints.length === 0 ? (
        <Paper sx={{ p: 3, textAlign: "center", bgcolor: "grey.50" }}>
          <Typography color="text.secondary">
            No complaints added yet. Click "Add Complaint" to begin.
          </Typography>
        </Paper>
      ) : (
        <Stack spacing={2}>
          {complaints
            .sort(
              (a, b) =>
                ONSET_OPTIONS.indexOf(a.onset) - ONSET_OPTIONS.indexOf(b.onset)
            )
            .map((complaint, index) => (
              <Accordion key={index}>
                <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                  <Box display="flex" alignItems="center" gap={2} width="100%">
                    <Typography variant="subtitle1" fontWeight="bold">
                      {complaint.complaint}
                    </Typography>
                    <Chip
                      label={complaint.severity}
                      color={getSeverityColor(complaint.severity) as any}
                      size="small"
                    />
                    <Typography variant="body2" color="text.secondary">
                      {complaint.onset}
                    </Typography>
                    {getProgressionIcon(complaint.progression)}
                  </Box>
                </AccordionSummary>
                <AccordionDetails>
                  <Grid container spacing={2}>
                    <Grid item xs={12}>
                      <Typography variant="body2">
                        <strong>Onset:</strong> {complaint.onset} |{" "}
                        <strong>Duration:</strong> {complaint.duration}
                      </Typography>
                    </Grid>
                    {complaint.character && (
                      <Grid item xs={12}>
                        <Typography variant="body2">
                          <strong>Character:</strong> {complaint.character}
                        </Typography>
                      </Grid>
                    )}
                    {complaint.location && (
                      <Grid item xs={12}>
                        <Typography variant="body2">
                          <strong>Location:</strong> {complaint.location}
                        </Typography>
                      </Grid>
                    )}
                    {complaint.relieving_factors.length > 0 && (
                      <Grid item xs={12}>
                        <Typography variant="body2" gutterBottom>
                          <strong>Relieving Factors:</strong>
                        </Typography>
                        <Box display="flex" gap={1} flexWrap="wrap">
                          {complaint.relieving_factors.map((factor, i) => (
                            <Chip
                              key={i}
                              label={factor}
                              size="small"
                              color="success"
                              variant="outlined"
                            />
                          ))}
                        </Box>
                      </Grid>
                    )}
                    {complaint.aggravating_factors.length > 0 && (
                      <Grid item xs={12}>
                        <Typography variant="body2" gutterBottom>
                          <strong>Aggravating Factors:</strong>
                        </Typography>
                        <Box display="flex" gap={1} flexWrap="wrap">
                          {complaint.aggravating_factors.map((factor, i) => (
                            <Chip
                              key={i}
                              label={factor}
                              size="small"
                              color="error"
                              variant="outlined"
                            />
                          ))}
                        </Box>
                      </Grid>
                    )}
                    {complaint.associated_symptoms.length > 0 && (
                      <Grid item xs={12}>
                        <Typography variant="body2" gutterBottom>
                          <strong>Associated Symptoms:</strong>
                        </Typography>
                        <Box display="flex" gap={1} flexWrap="wrap">
                          {complaint.associated_symptoms.map((symptom, i) => (
                            <Chip
                              key={i}
                              label={symptom}
                              size="small"
                              variant="outlined"
                            />
                          ))}
                        </Box>
                      </Grid>
                    )}
                    <Grid item xs={12}>
                      <Box display="flex" gap={1}>
                        <Button
                          size="small"
                          variant="outlined"
                          onClick={() => handleEditComplaint(index)}
                        >
                          Edit
                        </Button>
                        <Button
                          size="small"
                          variant="outlined"
                          color="error"
                          startIcon={<DeleteIcon />}
                          onClick={() => handleDeleteComplaint(index)}
                        >
                          Delete
                        </Button>
                      </Box>
                    </Grid>
                  </Grid>
                </AccordionDetails>
              </Accordion>
            ))}
        </Stack>
      )}

      {/* Add/Edit Dialog */}
      <Dialog
        open={dialogOpen}
        onClose={handleCloseDialog}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          {editIndex !== null ? "Edit Complaint" : "Add Chief Complaint"}
        </DialogTitle>
        <DialogContent>
          <Grid container spacing={3} sx={{ mt: 0.5 }}>
            {/* Complaint Selection */}
            <Grid item xs={12}>
              <Autocomplete
                value={currentComplaint.complaint}
                onChange={(_, newValue) =>
                  setCurrentComplaint({
                    ...currentComplaint,
                    complaint: newValue || "",
                  })
                }
                options={ALL_COMPLAINTS}
                renderInput={(params) => (
                  <TextField
                    {...params}
                    label="Chief Complaint *"
                    required
                    helperText="Select or type a complaint"
                  />
                )}
                freeSolo
              />
            </Grid>

            {/* Onset and Duration */}
            <Grid item xs={6}>
              <FormControl fullWidth required>
                <InputLabel>Onset *</InputLabel>
                <Select
                  value={currentComplaint.onset}
                  onChange={(e) =>
                    setCurrentComplaint({
                      ...currentComplaint,
                      onset: e.target.value,
                    })
                  }
                  label="Onset *"
                >
                  {ONSET_OPTIONS.map((option) => (
                    <MenuItem key={option} value={option}>
                      {option}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>

            <Grid item xs={6}>
              <TextField
                fullWidth
                label="Duration"
                value={currentComplaint.duration}
                onChange={(e) =>
                  setCurrentComplaint({
                    ...currentComplaint,
                    duration: e.target.value,
                  })
                }
                helperText="e.g., '3 days', '2 weeks'"
              />
            </Grid>

            {/* Severity */}
            <Grid item xs={12}>
              <Typography gutterBottom>Severity *</Typography>
              <Box sx={{ px: 2 }}>
                <Stack direction="row" spacing={2} alignItems="center">
                  {SEVERITY_OPTIONS.map((option) => (
                    <Button
                      key={option}
                      variant={
                        currentComplaint.severity === option
                          ? "contained"
                          : "outlined"
                      }
                      color={
                        option === "Mild"
                          ? "success"
                          : option === "Moderate"
                          ? "warning"
                          : "error"
                      }
                      onClick={() =>
                        setCurrentComplaint({
                          ...currentComplaint,
                          severity: option,
                        })
                      }
                      fullWidth
                    >
                      {option}
                    </Button>
                  ))}
                </Stack>
              </Box>
            </Grid>

            {/* Character */}
            {getCharacterOptions(currentComplaint.complaint).length > 0 && (
              <Grid item xs={12}>
                <FormControl fullWidth>
                  <InputLabel>Character</InputLabel>
                  <Select
                    value={currentComplaint.character || ""}
                    onChange={(e) =>
                      setCurrentComplaint({
                        ...currentComplaint,
                        character: e.target.value,
                      })
                    }
                    label="Character"
                  >
                    {getCharacterOptions(currentComplaint.complaint).map(
                      (option) => (
                        <MenuItem key={option} value={option}>
                          {option}
                        </MenuItem>
                      )
                    )}
                  </Select>
                </FormControl>
              </Grid>
            )}

            {/* Location and Radiation */}
            <Grid item xs={6}>
              <TextField
                fullWidth
                label="Location"
                value={currentComplaint.location || ""}
                onChange={(e) =>
                  setCurrentComplaint({
                    ...currentComplaint,
                    location: e.target.value,
                  })
                }
                helperText="Where is the complaint?"
              />
            </Grid>

            <Grid item xs={6}>
              <TextField
                fullWidth
                label="Radiation"
                value={currentComplaint.radiation || ""}
                onChange={(e) =>
                  setCurrentComplaint({
                    ...currentComplaint,
                    radiation: e.target.value,
                  })
                }
                helperText="Does it spread elsewhere?"
              />
            </Grid>

            {/* Progression and Timing */}
            <Grid item xs={6}>
              <FormControl fullWidth>
                <InputLabel>Progression</InputLabel>
                <Select
                  value={currentComplaint.progression}
                  onChange={(e) =>
                    setCurrentComplaint({
                      ...currentComplaint,
                      progression: e.target.value,
                    })
                  }
                  label="Progression"
                >
                  {PROGRESSION_OPTIONS.map((option) => (
                    <MenuItem key={option} value={option}>
                      {option}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>

            <Grid item xs={6}>
              <FormControl fullWidth>
                <InputLabel>Timing</InputLabel>
                <Select
                  value={currentComplaint.timing || ""}
                  onChange={(e) =>
                    setCurrentComplaint({
                      ...currentComplaint,
                      timing: e.target.value,
                    })
                  }
                  label="Timing"
                >
                  {TIMING_OPTIONS.map((option) => (
                    <MenuItem key={option} value={option}>
                      {option}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>

            {/* Relieving Factors */}
            <Grid item xs={12}>
              <Autocomplete
                multiple
                value={currentComplaint.relieving_factors}
                onChange={(_, newValue) =>
                  setCurrentComplaint({
                    ...currentComplaint,
                    relieving_factors: newValue,
                  })
                }
                options={RELIEVING_FACTORS}
                renderInput={(params) => (
                  <TextField
                    {...params}
                    label="Relieving Factors"
                    helperText="What makes it better?"
                  />
                )}
                renderTags={(value, getTagProps) =>
                  value.map((option, index) => (
                    <Chip
                      label={option}
                      {...getTagProps({ index })}
                      color="success"
                      size="small"
                    />
                  ))
                }
                freeSolo
              />
            </Grid>

            {/* Aggravating Factors */}
            <Grid item xs={12}>
              <Autocomplete
                multiple
                value={currentComplaint.aggravating_factors}
                onChange={(_, newValue) =>
                  setCurrentComplaint({
                    ...currentComplaint,
                    aggravating_factors: newValue,
                  })
                }
                options={AGGRAVATING_FACTORS}
                renderInput={(params) => (
                  <TextField
                    {...params}
                    label="Aggravating Factors"
                    helperText="What makes it worse?"
                  />
                )}
                renderTags={(value, getTagProps) =>
                  value.map((option, index) => (
                    <Chip
                      label={option}
                      {...getTagProps({ index })}
                      color="error"
                      size="small"
                    />
                  ))
                }
                freeSolo
              />
            </Grid>

            {/* Associated Symptoms */}
            <Grid item xs={12}>
              <Autocomplete
                multiple
                value={currentComplaint.associated_symptoms}
                onChange={(_, newValue) =>
                  setCurrentComplaint({
                    ...currentComplaint,
                    associated_symptoms: newValue,
                  })
                }
                options={ALL_COMPLAINTS.filter(
                  (c) => c !== currentComplaint.complaint
                )}
                renderInput={(params) => (
                  <TextField
                    {...params}
                    label="Associated Symptoms"
                    helperText="Other symptoms occurring together"
                  />
                )}
                renderTags={(value, getTagProps) =>
                  value.map((option, index) => (
                    <Chip
                      label={option}
                      {...getTagProps({ index })}
                      size="small"
                    />
                  ))
                }
                freeSolo
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>Cancel</Button>
          <Button onClick={handleSaveComplaint} variant="contained">
            {editIndex !== null ? "Update" : "Add"} Complaint
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};
