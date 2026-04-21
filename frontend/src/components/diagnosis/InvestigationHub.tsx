import React from 'react';
import {
  Box,
  Typography,
  Card,
  Chip,
  Divider,
  Grid,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Button,
  IconButton,
} from '@mui/material';
import {
  Science as LabIcon,
  Biotech as BiologyIcon,
  Upload as UploadIcon,
  GetApp as DownloadIcon,
  ClearAll as ClearIcon,
  Add as AddIcon,
} from '@mui/icons-material';

export interface LabTest {
  id: string;
  test: string;
  result: string;
  normalRange: string;
  units: string;
  date: string;
  status: 'normal' | 'abnormal' | 'critical' | 'pending';
}

export interface UploadedReport {
  id: string;
  name: string;
  type: 'lab' | 'radiology' | 'pathology' | 'other';
  date: string;
  url?: string;
  summary?: string;
}

export interface InvestigationAdvice {
  category: string;
  tests: string[];
  reason: string;
  urgency: 'routine' | 'urgent' | 'stat';
}

interface InvestigationHubProps {
  investigationAdvice: InvestigationAdvice[];
  labTests: LabTest[];
  uploadedReports: UploadedReport[];
  categories: Record<string, string[]>;
  commonTests: Array<{ test: string; normalRange: string; units: string }>;
  onAddAdvice: (category: string, tests: string[], reason: string, urgency?: 'routine' | 'urgent' | 'stat') => void;
  onRemoveAdvice: (index: number) => void;
  onUpdateLabTest: (id: string, field: keyof LabTest, value: string) => void;
  onAddLabTest: (testData?: Partial<LabTest>) => void;
  onRemoveLabTest: (id: string) => void;
  onUploadReport: (event: React.ChangeEvent<HTMLInputElement>) => void;
  onRemoveReport: (id: string) => void;
}

export const InvestigationHub: React.FC<InvestigationHubProps> = ({
  investigationAdvice,
  labTests,
  uploadedReports,
  categories,
  commonTests,
  onAddAdvice,
  onRemoveAdvice,
  onUpdateLabTest,
  onAddLabTest,
  onRemoveLabTest,
  onUploadReport,
  onRemoveReport,
}) => {
  return (
    <Box>
      {/* Investigation Advice */}
      <Box sx={{ mb: 3 }}>
        <Typography variant="subtitle2" gutterBottom sx={{ display: 'flex', alignItems: 'center' }}>
          <LabIcon sx={{ mr: 1 }} />
          Suggested Investigations
        </Typography>

        <Box sx={{ mb: 2 }}>
          {Object.entries(categories).map(([category, tests]) => (
            <Card key={category} variant="outlined" sx={{ mb: 1, p: 1 }}>
              <Typography variant="caption" fontWeight={600} color="primary">
                {category}:
              </Typography>
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5, mt: 0.5 }}>
                {tests.map(test => (
                  <Chip
                    key={test}
                    label={test}
                    size="small"
                    onClick={() => onAddAdvice(category, [test], `${category} workup indicated`, 'routine')}
                    sx={{ cursor: 'pointer' }}
                    variant="outlined"
                  />
                ))}
              </Box>
            </Card>
          ))}
        </Box>

        {investigationAdvice.length > 0 && (
          <Box sx={{ mb: 2 }}>
            <Typography variant="body2" gutterBottom>Selected Investigations:</Typography>
            {investigationAdvice.map((advice, index) => (
              <Card key={index} variant="outlined" sx={{ mb: 1, p: 2 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start' }}>
                  <Box>
                    <Typography variant="subtitle2" color="primary">
                      {advice.category}
                    </Typography>
                    <Typography variant="body2">
                      Tests: {advice.tests.join(', ')}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      Reason: {advice.reason} | Urgency: {advice.urgency}
                    </Typography>
                  </Box>
                  <IconButton size="small" onClick={() => onRemoveAdvice(index)}>
                    <ClearIcon />
                  </IconButton>
                </Box>
              </Card>
            ))}
          </Box>
        )}
      </Box>

      <Divider sx={{ my: 2 }} />

      {/* Lab Results Entry */}
      <Box sx={{ mb: 3 }}>
        <Typography variant="subtitle2" gutterBottom sx={{ display: 'flex', alignItems: 'center' }}>
          <BiologyIcon sx={{ mr: 1 }} />
          Lab Results
        </Typography>

        <Box sx={{ mb: 2 }}>
          <Typography variant="caption" gutterBottom>Quick Add Common Tests:</Typography>
          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5, mb: 2 }}>
            {commonTests.map(labTest => (
              <Chip
                key={labTest.test}
                label={labTest.test}
                size="small"
                onClick={() => onAddLabTest({
                  test: labTest.test,
                  normalRange: labTest.normalRange,
                  units: labTest.units,
                  status: 'pending'
                })}
                sx={{ cursor: 'pointer' }}
                variant="outlined"
              />
            ))}
          </Box>
        </Box>

        {labTests.map((test) => (
          <Card key={test.id} variant="outlined" sx={{ mb: 2, p: 2 }}>
            <Grid container spacing={2}>
              <Grid item xs={12} md={3}>
                <TextField
                  fullWidth
                  label="Test Name"
                  value={test.test}
                  onChange={(e) => onUpdateLabTest(test.id, 'test', e.target.value)}
                  size="small"
                />
              </Grid>
              <Grid item xs={6} md={2}>
                <TextField
                  fullWidth
                  label="Result"
                  value={test.result}
                  onChange={(e) => onUpdateLabTest(test.id, 'result', e.target.value)}
                  size="small"
                />
              </Grid>
              <Grid item xs={6} md={2}>
                <TextField
                  fullWidth
                  label="Units"
                  value={test.units}
                  onChange={(e) => onUpdateLabTest(test.id, 'units', e.target.value)}
                  size="small"
                />
              </Grid>
              <Grid item xs={12} md={2}>
                <TextField
                  fullWidth
                  label="Normal Range"
                  value={test.normalRange}
                  onChange={(e) => onUpdateLabTest(test.id, 'normalRange', e.target.value)}
                  size="small"
                />
              </Grid>
              <Grid item xs={6} md={2}>
                <FormControl fullWidth size="small">
                  <InputLabel>Status</InputLabel>
                  <Select
                    value={test.status}
                    onChange={(e) => onUpdateLabTest(test.id, 'status', e.target.value as any)}
                    label="Status"
                  >
                    <MenuItem value="normal">Normal</MenuItem>
                    <MenuItem value="abnormal">Abnormal</MenuItem>
                    <MenuItem value="critical">Critical</MenuItem>
                    <MenuItem value="pending">Pending</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={6} md={1}>
                <IconButton color="error" onClick={() => onRemoveLabTest(test.id)} size="small">
                  <ClearIcon />
                </IconButton>
              </Grid>
            </Grid>
          </Card>
        ))}

        <Button variant="outlined" onClick={() => onAddLabTest()} startIcon={<AddIcon />} size="small">
          Add Lab Test
        </Button>
      </Box>

      <Divider sx={{ my: 2 }} />

      {/* Report Upload */}
      <Box>
        <Typography variant="subtitle2" gutterBottom sx={{ display: 'flex', alignItems: 'center' }}>
          <UploadIcon sx={{ mr: 1 }} />
          Previous Reports Upload
        </Typography>

        <Box sx={{ mb: 2 }}>
          <Box
            component="input"
            type="file"
            multiple
            accept=".pdf,.jpg,.jpeg,.png,.doc,.docx"
            onChange={onUploadReport}
            sx={{ display: 'none' }}
            id="report-upload-comp"
          />
          <label htmlFor="report-upload-comp">
            <Button variant="outlined" component="span" startIcon={<UploadIcon />} size="small">
              Upload Lab/Radiology Reports
            </Button>
          </label>
        </Box>

        {uploadedReports.length > 0 && (
          <Box>
            <Typography variant="body2" gutterBottom>Uploaded Reports:</Typography>
            {uploadedReports.map((report) => (
              <Card key={report.id} variant="outlined" sx={{ mb: 1, p: 2 }}>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <Box>
                    <Typography variant="subtitle2">{report.name}</Typography>
                    <Typography variant="caption" color="text.secondary">
                      Type: {report.type} | Date: {report.date}
                    </Typography>
                  </Box>
                  <Box>
                    <IconButton size="small" color="primary">
                      <DownloadIcon />
                    </IconButton>
                    <IconButton size="small" color="error" onClick={() => onRemoveReport(report.id)}>
                      <ClearIcon />
                    </IconButton>
                  </Box>
                </Box>
              </Card>
            ))}
          </Box>
        )}
      </Box>
    </Box>
  );
};
