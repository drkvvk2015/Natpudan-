import React from 'react'
import { Box, Typography, Button, Paper } from '@mui/material'
import { useNavigate } from 'react-router-dom'
import { Lock as LockIcon } from '@mui/icons-material'

const Unauthorized: React.FC = () => {
  const navigate = useNavigate()

  return (
    <Box
      sx={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        minHeight: '80vh',
        px: 2,
      }}
    >
      <Paper
        elevation={3}
        sx={{
          p: 4,
          maxWidth: 500,
          textAlign: 'center',
        }}
      >
        <LockIcon
          sx={{
            fontSize: 80,
            color: 'error.main',
            mb: 2,
          }}
        />
        <Typography variant="h4" gutterBottom fontWeight={600}>
          Access Denied
        </Typography>
        <Typography variant="body1" color="text.secondary" paragraph>
          You don't have permission to access this page. Please contact your administrator if you believe this is an error.
        </Typography>
        <Box sx={{ mt: 3, display: 'flex', gap: 2, justifyContent: 'center' }}>
          <Button
            variant="outlined"
            onClick={() => navigate(-1)}
          >
            Go Back
          </Button>
          <Button
            variant="contained"
            onClick={() => navigate('/dashboard')}
          >
            Go to Dashboard
          </Button>
        </Box>
      </Paper>
    </Box>
  )
}

export default Unauthorized
