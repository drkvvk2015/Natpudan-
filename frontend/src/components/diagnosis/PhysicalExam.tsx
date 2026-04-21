import React from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Chip,
  TextField,
} from '@mui/material';

interface ClinicalFinding {
  system: string;
  finding: string;
  normal: boolean;
  details: string;
}

interface PhysicalExamProps {
  systems: Record<string, { icon: React.ReactNode; findings: string[] }>;
  clinicalFindings: ClinicalFinding[];
  toggleClinicalFinding: (system: string, finding: string, normal?: boolean) => void;
  onRemoveFinding: (system: string, finding: string) => void;
}

export const PhysicalExam: React.FC<PhysicalExamProps> = ({
  systems,
  clinicalFindings,
  toggleClinicalFinding,
  onRemoveFinding,
}) => {
  return (
    <Box>
      {Object.entries(systems).map(([system, { icon, findings }]) => (
        <Card key={system} variant="outlined" sx={{ mb: 2 }}>
          <CardContent>
            <Typography variant="subtitle2" gutterBottom sx={{ display: 'flex', alignItems: 'center' }}>
              {icon}
              <Box sx={{ ml: 1 }}>{system}</Box>
            </Typography>
            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
              {findings.map(finding => {
                const existing = clinicalFindings.find(f => f.system === system && f.finding === finding);
                const isSelected = !!existing;
                const isNormal = existing ? existing.normal : true;
                return (
                  <Chip
                    key={finding}
                    label={finding}
                    size="small"
                    variant={isSelected ? 'filled' : 'outlined'}
                    onClick={() => toggleClinicalFinding(system, finding, true)}
                    onDelete={isSelected ? () => onRemoveFinding(system, finding) : undefined}
                    sx={{ cursor: 'pointer' }}
                    color={isSelected ? (isNormal ? 'success' : 'error') : 'default'}
                  />
                );
              })}
            </Box>

            {/* Custom findings input */}
            <TextField
              fullWidth
              placeholder={`Add custom ${system.toLowerCase()} findings...`}
              size="small"
              sx={{ mt: 1 }}
              onKeyPress={(e) => {
                if (e.key === 'Enter') {
                  const target = e.target as HTMLInputElement;
                  if (target.value.trim()) {
                    toggleClinicalFinding(system, target.value.trim(), true);
                    target.value = '';
                  }
                }
              }}
            />

            {/* Show selected findings */}
            {clinicalFindings.filter(f => f.system === system).length > 0 && (
              <Box sx={{ mt: 2 }}>
                <Typography variant="caption" color="text.secondary">
                  Selected findings:
                </Typography>
                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5, mt: 0.5 }}>
                  {clinicalFindings
                    .filter(f => f.system === system)
                    .map((finding, index) => (
                      <Chip
                        key={index}
                        label={finding.finding}
                        onDelete={() => onRemoveFinding(finding.system, finding.finding)}
                        size="small"
                        color="primary"
                        variant={finding.normal ? "filled" : "outlined"}
                      />
                    ))}
                </Box>
              </Box>
            )}
          </CardContent>
        </Card>
      ))}
    </Box>
  );
};
