import React from 'react';
import { Box, Typography } from '@mui/material';

const DiagnosisTemp: React.FC = () => {
  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Diagnosis Page
      </Typography>
      <Typography variant="body1">
        The diagnosis functionality is temporarily simplified while we fix parsing issues.
        The full enhanced medical history with smoking index and PDF export will be restored shortly.
      </Typography>
    </Box>
  );
};

export default DiagnosisTemp;