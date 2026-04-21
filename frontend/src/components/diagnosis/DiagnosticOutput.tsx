import React from 'react';
import {
  Box,
  Typography,
  Paper,
  Stack,
  Chip,
  LinearProgress,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Divider,
  Button,
  CircularProgress,
  Alert,
  Skeleton,
} from '@mui/material';
import {
  Psychology as PsychologyIcon,
  AutoAwesome as AutoAwesomeIcon,
  Assignment as AssignmentIcon,
  PictureAsPdf as PictureAsPdfIcon,
} from '@mui/icons-material';

interface DifferentialDiagnosis {
  diagnosis?: string;
  disease_name?: string;
  confidence: number;
  icd_code: string;
  supporting_evidence: string[];
}

interface LiveDiagnosisResponse {
  differential_diagnoses: DifferentialDiagnosis[];
  recommended_tests: string[];
  clinical_summary: string;
  data_completeness: number;
}

interface DiagnosticOutputProps {
  liveDiagnosis: LiveDiagnosisResponse | null;
  isAnalyzing: boolean;
  treatmentPlan: any | null;
  prescriptionPlan: any | null;
  generatingReport: boolean;
  onSuggestTreatment: () => void;
  onGeneratePrescription: () => void;
  onGenerateReport: () => void;
  onExportCaseSheet: () => void;
}

export const DiagnosticOutput: React.FC<DiagnosticOutputProps> = ({
  liveDiagnosis,
  isAnalyzing,
  treatmentPlan,
  prescriptionPlan,
  generatingReport,
  onSuggestTreatment,
  onGeneratePrescription,
  onGenerateReport,
  onExportCaseSheet,
}) => {
  if (isAnalyzing && !liveDiagnosis) {
    return (
      <Stack spacing={3}>
        <Paper elevation={3} sx={{ p: 3 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
            <Skeleton variant="circular" width={24} height={24} sx={{ mr: 1 }} />
            <Skeleton variant="text" width="60%" height={32} />
          </Box>
          <Skeleton variant="rectangular" height={100} sx={{ mb: 2, borderRadius: 1 }} />
          <Skeleton variant="text" width="40%" />
          <Skeleton variant="text" width="90%" />
        </Paper>
        <Paper elevation={3} sx={{ p: 3 }}>
          <Skeleton variant="text" width="50%" height={32} sx={{ mb: 2 }} />
          <Box sx={{ display: 'flex', gap: 1 }}>
            <Skeleton variant="rounded" width={80} height={32} />
            <Skeleton variant="rounded" width={80} height={32} />
            <Skeleton variant="rounded" width={80} height={32} />
          </Box>
        </Paper>
      </Stack>
    );
  }

  if (!liveDiagnosis) {
    return (
      <Paper elevation={3} sx={{ p: 3, textAlign: 'center', bgcolor: 'grey.50' }}>
        <PsychologyIcon sx={{ fontSize: 40, color: 'text.disabled', mb: 1 }} />
        <Typography color="text.secondary">
          AI Differential Diagnosis will appear here as you enter patient data
        </Typography>
      </Paper>
    );
  }

  return (
    <Stack spacing={3}>
      {/* AI Differential Diagnosis */}
      <Paper elevation={3} sx={{ p: 3, borderTop: '4px solid #2196f3' }}>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
          <PsychologyIcon color="primary" sx={{ mr: 1 }} />
          <Typography variant="h6">AI Differential Diagnosis</Typography>
          {isAnalyzing && <CircularProgress size={20} sx={{ ml: 2 }} />}
        </Box>

        <Typography variant="body2" color="text.secondary" gutterBottom>
          Based on the clinical findings and history:
        </Typography>

        <List sx={{ mb: 2 }}>
          {liveDiagnosis.differential_diagnoses.map((dd, index) => (
            <React.Fragment key={index}>
              <ListItem alignItems="flex-start" sx={{ px: 0 }}>
                <ListItemText
                  primary={
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <Typography variant="subtitle1" fontWeight={700}>
                        {dd.diagnosis || dd.disease_name}
                      </Typography>
                      <Chip
                        label={`${Math.round(dd.confidence * 100)}% Match`}
                        size="small"
                        color={dd.confidence > 0.7 ? "success" : dd.confidence > 0.4 ? "warning" : "default"}
                      />
                    </Box>
                  }
                  secondary={
                    <Box sx={{ mt: 0.5 }}>
                      <Typography variant="caption" display="block" color="primary" fontWeight={600}>
                        ICD-10: {dd.icd_code}
                      </Typography>
                      <Typography variant="caption" display="block" sx={{ mt: 0.5 }}>
                        Supporting findings: {dd.supporting_evidence.join(', ')}
                      </Typography>
                    </Box>
                  }
                />
              </ListItem>
              {index < liveDiagnosis.differential_diagnoses.length - 1 && <Divider component="li" />}
            </React.Fragment>
          ))}
        </List>

        <Typography variant="subtitle2" gutterBottom sx={{ mt: 2 }}>
          Data Completeness:
        </Typography>
        <Box sx={{ display: 'flex', alignItems: 'center' }}>
          <Box sx={{ width: '100%', mr: 1 }}>
            <LinearProgress
              variant="determinate"
              value={liveDiagnosis.data_completeness * 100}
              color={liveDiagnosis.data_completeness > 0.8 ? "success" : liveDiagnosis.data_completeness > 0.5 ? "primary" : "warning"}
              sx={{ height: 8, borderRadius: 5 }}
            />
          </Box>
          <Box sx={{ minWidth: 35 }}>
            <Typography variant="body2" color="text.secondary">{`${Math.round(liveDiagnosis.data_completeness * 100)}%`}</Typography>
          </Box>
        </Box>
      </Paper>

      {/* Recommended Tests */}
      <Paper elevation={3} sx={{ p: 3 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
          <AutoAwesomeIcon color="secondary" sx={{ mr: 1 }} />
          <Typography variant="h6">Recommended Workup</Typography>
        </Box>
        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
          {liveDiagnosis.recommended_tests.map(test => (
            <Chip key={test} label={test} variant="outlined" color="secondary" />
          ))}
        </Box>
      </Paper>

      {/* Clinical Summary */}
      <Paper elevation={3} sx={{ p: 3, bgcolor: 'primary.main', color: 'primary.contrastText' }}>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
          <AssignmentIcon sx={{ mr: 1 }} />
          <Typography variant="subtitle1" fontWeight={600}>Clinical Summary (AI Draft)</Typography>
        </Box>
        <Typography variant="body2" sx={{ fontStyle: 'italic', opacity: 0.9 }}>
          "{liveDiagnosis.clinical_summary}"
        </Typography>
      </Paper>

      {/* Action Buttons */}
      <Stack spacing={2}>
        <Button
          fullWidth
          variant="contained"
          startIcon={<AutoAwesomeIcon />}
          onClick={onSuggestTreatment}
          sx={{ py: 1.5, borderRadius: 2 }}
        >
          Suggest Treatment Pathway
        </Button>
        <Button
          fullWidth
          variant="contained"
          color="secondary"
          startIcon={<PsychologyIcon />}
          onClick={onGeneratePrescription}
          sx={{ py: 1.5, borderRadius: 2 }}
        >
          Generate AI Prescription
        </Button>
        <Box sx={{ display: 'flex', gap: 2 }}>
          <Button
            fullWidth
            variant="outlined"
            startIcon={generatingReport ? <CircularProgress size={20} /> : <PictureAsPdfIcon />}
            onClick={onGenerateReport}
            disabled={generatingReport}
          >
            Export Analysis
          </Button>
          <Button
            fullWidth
            variant="outlined"
            startIcon={generatingReport ? <CircularProgress size={20} /> : <AssignmentIcon />}
            onClick={onExportCaseSheet}
            disabled={generatingReport}
          >
            OPD Case Sheet
          </Button>
        </Box>
      </Stack>

      {/* Results Display for Treatment and Prescription */}
      {treatmentPlan && (
        <Alert severity="success" sx={{ mt: 2 }}>
          Treatment plan generated successfully.
        </Alert>
      )}
      {prescriptionPlan && (
        <Alert severity="info" sx={{ mt: 2 }}>
          AI Prescription generated successfully.
        </Alert>
      )}
    </Stack>
  );
};
