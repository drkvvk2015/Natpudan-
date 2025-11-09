import React from 'react';
import { CssBaseline, Container, Typography } from '@mui/material';

function App() {
  return (
    <>
      <CssBaseline />
      <Container sx={{ py: 4 }}>
        <Typography variant="h5" gutterBottom>
          Physician AI Assistant UI
        </Typography>
        <Typography variant="body1">
          Frontend is scaffolded. Hook up routes and pages as needed.
        </Typography>
      </Container>
    </>
  );
}

export default App;
