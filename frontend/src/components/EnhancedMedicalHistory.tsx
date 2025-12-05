import React, { useState, useCallback } from 'react';
import {
  Box,
  Typography,
  Grid,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Paper,
  Chip,
  Alert,
  Button,
  Stack,
  Autocomplete,
} from '@mui/material';
import {
  ExpandMore as ExpandMoreIcon,
  Add as AddIcon,
  Remove as RemoveIcon,
} from '@mui/icons-material';

export interface MedicalHistoryItem {
  condition: string;
  duration: string;
  durationUnit: 'days' | 'weeks' | 'months' | 'years';
  severity?: 'mild' | 'moderate' | 'severe';
  notes?: string;
}

export interface SmokingHistory {
  isSmoker: boolean;
  packsPerDay?: number;
  yearsSmoked?: number;
  packYears?: number;
  quitDate?: string;
}

interface EnhancedMedicalHistoryProps {
  onHistoryChange: (history: {
    medicalHistory: MedicalHistoryItem[];
    smokingHistory: SmokingHistory;
  }) => void;
  initialHistory?: {
    medicalHistory?: MedicalHistoryItem[];
    smokingHistory?: SmokingHistory;
  };
}

// Common medical conditions for autocomplete
const commonConditions = [
  'Hypertension',
  'Diabetes Mellitus Type 2',
  'Diabetes Mellitus Type 1',
  'Asthma',
  'COPD',
  'Heart Disease',
  'Stroke',
  'Cancer',
  'Arthritis',
  'Depression',
  'Anxiety',
  'Thyroid Disease',
  'Kidney Disease',
  'Liver Disease',
  'High Cholesterol',
  'Migraine',
  'Epilepsy',
  'Allergies',
];

const EnhancedMedicalHistory: React.FC<EnhancedMedicalHistoryProps> = ({
  onHistoryChange,
  initialHistory,
}) => {
  const [medicalHistory, setMedicalHistory] = useState<MedicalHistoryItem[]>(
    initialHistory?.medicalHistory || []
  );

  const [smokingHistory, setSmokingHistory] = useState<SmokingHistory>(
    initialHistory?.smokingHistory || { isSmoker: false }
  );

  const calculatePackYears = useCallback((packsPerDay: number, years: number) => {
    return packsPerDay * years;
  }, []);

  const updateHistory = useCallback(() => {
    onHistoryChange({ medicalHistory, smokingHistory });
  }, [medicalHistory, smokingHistory, onHistoryChange]);

  React.useEffect(() => {
    updateHistory();
  }, [updateHistory]);

  const addMedicalCondition = () => {
    const newCondition: MedicalHistoryItem = {
      condition: '',
      duration: '',
      durationUnit: 'months',
      severity: 'mild',
      notes: '',
    };
    setMedicalHistory([...medicalHistory, newCondition]);
  };

  const removeMedicalCondition = (index: number) => {
    setMedicalHistory(medicalHistory.filter((_, i) => i !== index));
  };

  const updateMedicalCondition = (index: number, field: keyof MedicalHistoryItem, value: any) => {
    const updated = [...medicalHistory];
    updated[index] = { ...updated[index], [field]: value };
    setMedicalHistory(updated);
  };

  const handleSmokingChange = (field: keyof SmokingHistory, value: any) => {
    const updatedSmoking = { ...smokingHistory, [field]: value };

    // Auto-calculate pack-years when packs per day or years change
    if (field === 'packsPerDay' || field === 'yearsSmoked') {
      const packs = field === 'packsPerDay' ? value : smokingHistory.packsPerDay || 0;
      const years = field === 'yearsSmoked' ? value : smokingHistory.yearsSmoked || 0;
      updatedSmoking.packYears = calculatePackYears(packs, years);
    }

    setSmokingHistory(updatedSmoking);
  };

  const getSmokingRisk = () => {
    const packYears = smokingHistory.packYears || 0;
    if (packYears === 0) return { level: 'none', color: 'success' as const };
    if (packYears < 10) return { level: 'low', color: 'info' as const };
    if (packYears < 20) return { level: 'moderate', color: 'warning' as const };
    return { level: 'high', color: 'error' as const };
  };

  return (
    <Paper elevation={2} sx={{ p: 2, mb: 3 }}>
      <Typography variant="h6" gutterBottom>
        Enhanced Medical History
      </Typography>

      {/* Medical History Section */}
      <Accordion defaultExpanded>
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <Typography variant="subtitle1">Past Medical History</Typography>
        </AccordionSummary>
        <AccordionDetails>
          <Box>
            {medicalHistory.map((item, index) => (
              <Paper key={index} variant="outlined" sx={{ p: 2, mb: 2 }}>
                <Grid container spacing={2} alignItems="center">
                  <Grid item xs={12} md={4}>
                    <Autocomplete
                      options={commonConditions}
                      value={item.condition}
                      onChange={(_, newValue) =>
                        updateMedicalCondition(index, 'condition', newValue || '')
                      }
                      renderInput={(params) => (
                        <TextField
                          {...params}
                          label="Condition"
                          fullWidth
                          size="small"
                        />
                      )}
                      freeSolo
                    />
                  </Grid>

                  <Grid item xs={6} md={2}>
                    <TextField
                      label="Duration"
                      type="number"
                      value={item.duration}
                      onChange={(e) =>
                        updateMedicalCondition(index, 'duration', e.target.value)
                      }
                      size="small"
                      fullWidth
                    />
                  </Grid>

                  <Grid item xs={6} md={2}>
                    <FormControl fullWidth size="small">
                      <InputLabel>Unit</InputLabel>
                      <Select
                        value={item.durationUnit}
                        onChange={(e) =>
                          updateMedicalCondition(index, 'durationUnit', e.target.value)
                        }
                        label="Unit"
                      >
                        <MenuItem value="days">Days</MenuItem>
                        <MenuItem value="weeks">Weeks</MenuItem>
                        <MenuItem value="months">Months</MenuItem>
                        <MenuItem value="years">Years</MenuItem>
                      </Select>
                    </FormControl>
                  </Grid>

                  <Grid item xs={6} md={2}>
                    <FormControl fullWidth size="small">
                      <InputLabel>Severity</InputLabel>
                      <Select
                        value={item.severity}
                        onChange={(e) =>
                          updateMedicalCondition(index, 'severity', e.target.value)
                        }
                        label="Severity"
                      >
                        <MenuItem value="mild">Mild</MenuItem>
                        <MenuItem value="moderate">Moderate</MenuItem>
                        <MenuItem value="severe">Severe</MenuItem>
                      </Select>
                    </FormControl>
                  </Grid>

                  <Grid item xs={6} md={1}>
                    <Button
                      onClick={() => removeMedicalCondition(index)}
                      color="error"
                      size="small"
                      startIcon={<RemoveIcon />}
                    >
                      Remove
                    </Button>
                  </Grid>

                  <Grid item xs={12}>
                    <TextField
                      label="Additional Notes"
                      value={item.notes}
                      onChange={(e) =>
                        updateMedicalCondition(index, 'notes', e.target.value)
                      }
                      multiline
                      rows={2}
                      fullWidth
                      size="small"
                    />
                  </Grid>
                </Grid>
              </Paper>
            ))}

            <Button
              onClick={addMedicalCondition}
              startIcon={<AddIcon />}
              variant="outlined"
              size="small"
            >
              Add Medical Condition
            </Button>
          </Box>
        </AccordionDetails>
      </Accordion>

      {/* Smoking History Section */}
      <Accordion defaultExpanded>
        <AccordionSummary expandIcon={<ExpandMoreIcon />}>
          <Typography variant="subtitle1">Smoking History</Typography>
        </AccordionSummary>
        <AccordionDetails>
          <Grid container spacing={2}>
            <Grid item xs={12}>
              <FormControl fullWidth size="small">
                <InputLabel>Smoking Status</InputLabel>
                <Select
                  value={smokingHistory.isSmoker ? 'current' : 'never'}
                  onChange={(e) =>
                    handleSmokingChange('isSmoker', e.target.value === 'current')
                  }
                  label="Smoking Status"
                >
                  <MenuItem value="never">Never Smoker</MenuItem>
                  <MenuItem value="current">Current/Former Smoker</MenuItem>
                </Select>
              </FormControl>
            </Grid>

            {smokingHistory.isSmoker && (
              <>
                <Grid item xs={6} md={3}>
                  <TextField
                    label="Packs per Day"
                    type="number"
                    inputProps={{ step: 0.5, min: 0 }}
                    value={smokingHistory.packsPerDay || ''}
                    onChange={(e) =>
                      handleSmokingChange('packsPerDay', parseFloat(e.target.value) || 0)
                    }
                    size="small"
                    fullWidth
                  />
                </Grid>

                <Grid item xs={6} md={3}>
                  <TextField
                    label="Years Smoked"
                    type="number"
                    inputProps={{ min: 0 }}
                    value={smokingHistory.yearsSmoked || ''}
                    onChange={(e) =>
                      handleSmokingChange('yearsSmoked', parseInt(e.target.value) || 0)
                    }
                    size="small"
                    fullWidth
                  />
                </Grid>

                <Grid item xs={6} md={3}>
                  <TextField
                    label="Pack-Years"
                    value={smokingHistory.packYears?.toFixed(1) || '0'}
                    size="small"
                    fullWidth
                    disabled
                    helperText="Auto-calculated"
                  />
                </Grid>

                <Grid item xs={6} md={3}>
                  <TextField
                    label="Quit Date (if applicable)"
                    type="date"
                    value={smokingHistory.quitDate || ''}
                    onChange={(e) =>
                      handleSmokingChange('quitDate', e.target.value)
                    }
                    size="small"
                    fullWidth
                    InputLabelProps={{ shrink: true }}
                  />
                </Grid>

                <Grid item xs={12}>
                  <Stack direction="row" spacing={1} alignItems="center">
                    <Typography variant="body2">Smoking Risk Level:</Typography>
                    <Chip
                      label={`${getSmokingRisk().level.toUpperCase()} RISK`}
                      color={getSmokingRisk().color}
                      size="small"
                    />
                    <Typography variant="caption" color="text.secondary">
                      ({smokingHistory.packYears?.toFixed(1) || 0} pack-years)
                    </Typography>
                  </Stack>

                  {(smokingHistory.packYears || 0) > 20 && (
                    <Alert severity="warning" sx={{ mt: 1 }}>
                      High smoking exposure. Consider lung cancer screening and enhanced monitoring.
                    </Alert>
                  )}
                </Grid>
              </>
            )}
          </Grid>
        </AccordionDetails>
      </Accordion>
    </Paper>
  );
};

export default EnhancedMedicalHistory;