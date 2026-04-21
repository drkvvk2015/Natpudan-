import React from 'react';
import {
  Grid,
  TextField,
  Skeleton,
  Box,
} from '@mui/material';

interface VitalSigns {
  temperature: string;
  pulse: string;
  bloodPressure: string;
  respiratoryRate: string;
  oxygenSaturation: string;
  height: string;
  weight: string;
  bmi: string;
}

interface VitalsPanelProps {
  vitalSigns: VitalSigns;
  onVitalChange: (field: keyof VitalSigns, value: string) => void;
  isLoading: boolean; // Added to control skeleton visibility
}

export const VitalsPanel: React.FC<VitalsPanelProps> = ({
  vitalSigns,
  onVitalChange,
  isLoading, // Destructure isLoading
}) => {
  // Define skeleton props for consistent styling
  const skeletonProps = {
    variant: "rounded" as "rounded",
    height: 40, // Adjust height to match TextField size="small"
    sx: { mb: 2 }, // Margin bottom for spacing
  };

  return (
    <Grid container spacing={2}>
      {isLoading ? (
        <>
          <Grid item xs={6} md={4}><Skeleton {...skeletonProps} /></Grid>
          <Grid item xs={6} md={4}><Skeleton {...skeletonProps} /></Grid>
          <Grid item xs={6} md={4}><Skeleton {...skeletonProps} /></Grid>
          <Grid item xs={6} md={4}><Skeleton {...skeletonProps} /></Grid>
          <Grid item xs={6} md={4}><Skeleton {...skeletonProps} /></Grid>
          <Grid item xs={6} md={4}><Skeleton {...skeletonProps} /></Grid>
          <Grid item xs={6} md={4}><Skeleton {...skeletonProps} /></Grid>
          <Grid item xs={6} md={4}><Skeleton {...skeletonProps} /></Grid>
        </>
      ) : (
        <>
          <Grid item xs={6} md={4}>
            <TextField
              fullWidth
              label="Temperature (°F)"
              type="number"
              value={vitalSigns.temperature}
              onChange={(e) => onVitalChange('temperature', e.target.value)}
              size="small"
              placeholder="98.6"
            />
          </Grid>
          <Grid item xs={6} md={4}>
            <TextField
              fullWidth
              label="Pulse (bpm)"
              type="number"
              value={vitalSigns.pulse}
              onChange={(e) => onVitalChange('pulse', e.target.value)}
              size="small"
              placeholder="72"
            />
          </Grid>
          <Grid item xs={6} md={4}>
            <TextField
              fullWidth
              label="BP (mmHg)"
              value={vitalSigns.bloodPressure}
              onChange={(e) => onVitalChange('bloodPressure', e.target.value)}
              size="small"
              placeholder="120/80"
            />
          </Grid>
          <Grid item xs={6} md={4}>
            <TextField
              fullWidth
              label="RR (/min)"
              type="number"
              value={vitalSigns.respiratoryRate}
              onChange={(e) => onVitalChange('respiratoryRate', e.target.value)}
              size="small"
              placeholder="16"
            />
          </Grid>
          <Grid item xs={6} md={4}>
            <TextField
              fullWidth
              label="SpO2 (%)"
              type="number"
              value={vitalSigns.oxygenSaturation}
              onChange={(e) => onVitalChange('oxygenSaturation', e.target.value)}
              size="small"
              placeholder="98"
            />
          </Grid>
          <Grid item xs={6} md={4}>
            <TextField
              fullWidth
              label="Height (cm)"
              type="number"
              value={vitalSigns.height}
              onChange={(e) => onVitalChange('height', e.target.value)}
              size="small"
            />
          </Grid>
          <Grid item xs={6} md={4}>
            <TextField
              fullWidth
              label="Weight (kg)"
              type="number"
              value={vitalSigns.weight}
              onChange={(e) => onVitalChange('weight', e.target.value)}
              size="small"
            />
          </Grid>
          <Grid item xs={6} md={4}>
            <TextField
              fullWidth
              label="BMI"
              value={vitalSigns.bmi}
              size="small"
              disabled
            />
          </Grid>
        </>
      )}
    </Grid>
  );
};
