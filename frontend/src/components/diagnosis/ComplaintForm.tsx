import React from 'react';
import {
  Box,
  Typography,
  Grid,
  Card,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  Divider,
  Button,
  IconButton,
} from '@mui/material';
import {
  Add as AddIcon,
  ClearAll as ClearIcon,
} from '@mui/icons-material';

export interface Complaint {
  id: string;
  complaint: string;
  duration: string;
  severity: string;
  details: string;
}

interface ComplaintFormProps {
  complaints: Complaint[];
  updateComplaint: (id: string, field: keyof Complaint, value: string) => void;
  addComplaint: () => void;
  removeComplaint: (id: string) => void;
  templates: Record<string, string[]>;
  durationOptions: string[];
  severityOptions: string[];
  onQuickSelect: (template: string) => void;
}

export const ComplaintForm: React.FC<ComplaintFormProps> = ({
  complaints,
  updateComplaint,
  addComplaint,
  removeComplaint,
  templates,
  durationOptions,
  severityOptions,
  onQuickSelect,
}) => {
  return (
    <Box>
      {/* Quick Complaint Categories */}
      <Typography variant="body2" gutterBottom>Quick Select:</Typography>
      <Box sx={{ mb: 2 }}>
        {Object.entries(templates).map(([category, templatesList]) => (
          <Box key={category} sx={{ mb: 1 }}>
            <Typography variant="caption" fontWeight={600}>{category}:</Typography>
            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5, mt: 0.5 }}>
              {templatesList.map(template => (
                <Chip
                  key={template}
                  label={template}
                  size="small"
                  onClick={() => onQuickSelect(template)}
                  sx={{ cursor: 'pointer' }}
                />
              ))}
            </Box>
          </Box>
        ))}
      </Box>

      <Divider sx={{ my: 2 }} />

      {/* Individual Complaints */}
      {(complaints || []).map((complaint, index) => (
        <Card key={complaint.id} variant="outlined" sx={{ mb: 2, p: 2 }}>
          <Grid container spacing={2}>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label={`Chief Complaint ${index + 1}`}
                value={complaint.complaint}
                onChange={(e) => updateComplaint(complaint.id, 'complaint', e.target.value)}
                size="small"
              />
            </Grid>
            <Grid item xs={6} md={3}>
              <FormControl fullWidth size="small">
                <InputLabel>Duration</InputLabel>
                <Select
                  value={complaint.duration}
                  onChange={(e) => updateComplaint(complaint.id, 'duration', e.target.value)}
                  label="Duration"
                >
                  {durationOptions.map(duration => (
                    <MenuItem key={duration} value={duration}>{duration}</MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={6} md={3}>
              <FormControl fullWidth size="small">
                <InputLabel>Severity</InputLabel>
                <Select
                  value={complaint.severity}
                  onChange={(e) => updateComplaint(complaint.id, 'severity', e.target.value)}
                  label="Severity"
                >
                  {severityOptions.map(severity => (
                    <MenuItem key={severity} value={severity}>{severity}</MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Additional Details"
                value={complaint.details}
                onChange={(e) => updateComplaint(complaint.id, 'details', e.target.value)}
                size="small"
                multiline
                rows={2}
                placeholder="Character, location, radiation, triggers..."
              />
            </Grid>
            <Grid item xs={12}>
              <Box sx={{ display: 'flex', justifyContent: 'flex-end' }}>
                <IconButton
                  color="error"
                  onClick={() => removeComplaint(complaint.id)}
                  disabled={(complaints || []).length === 1}
                >
                  <ClearIcon />
                </IconButton>
              </Box>
            </Grid>
          </Grid>
        </Card>
      ))}
      <Button
        variant="outlined"
        onClick={addComplaint}
        startIcon={<AddIcon />}
        size="small"
        sx={{ mt: 1 }}
      >
        Add Complaint
      </Button>
    </Box>
  );
};
