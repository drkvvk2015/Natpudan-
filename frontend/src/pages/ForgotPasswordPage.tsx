import React, { useState } from 'react';
import {
  Box,
  Container,
  Paper,
  TextField,
  Button,
  Typography,
  Alert,
  CircularProgress,
  Link as MuiLink,
} from '@mui/material';
import { Link, useNavigate } from 'react-router-dom';
import { Email as EmailIcon, ArrowBack as ArrowBackIcon } from '@mui/icons-material';
import apiClient from '../services/apiClient';

const ForgotPasswordPage: React.FC = () => {
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [resetToken, setResetToken] = useState('');
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    setLoading(true);

    try {
      const response = await apiClient.post('/api/auth/forgot-password', {
        email,
      });

      setSuccess(response.data.message);
      
      // In development, we get the token directly
      if (response.data.reset_token) {
        setResetToken(response.data.reset_token);
      }

      // Redirect to reset password page after 3 seconds
      setTimeout(() => {
        if (response.data.reset_token) {
          navigate(`/reset-password?token=${response.data.reset_token}`);
        } else {
          navigate('/login');
        }
      }, 3000);

    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Failed to send reset link. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box
      sx={{
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        padding: 2,
      }}
    >
      <Container maxWidth="sm">
        <Paper
          elevation={24}
          sx={{
            padding: 4,
            borderRadius: 3,
            background: 'rgba(255, 255, 255, 0.95)',
            backdropFilter: 'blur(10px)',
          }}
        >
          <Box sx={{ textAlign: 'center', mb: 3 }}>
            <EmailIcon sx={{ fontSize: 48, color: '#667eea', mb: 2 }} />
            <Typography variant="h4" gutterBottom fontWeight="bold">
              Forgot Password?
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Enter your email address and we'll send you instructions to reset your password.
            </Typography>
          </Box>

          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {typeof error === 'string' ? error : JSON.stringify(error, null, 2)}
            </Alert>
          )}

          {success && (
            <Alert severity="success" sx={{ mb: 2 }}>
              {success}
              {resetToken && (
                <Typography variant="caption" display="block" sx={{ mt: 1 }}>
                  Redirecting to reset password page...
                </Typography>
              )}
            </Alert>
          )}

          <form onSubmit={handleSubmit}>
            <TextField
              fullWidth
              label="Email Address"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              disabled={loading || !!success}
              autoFocus
              sx={{ mb: 3 }}
              InputProps={{
                startAdornment: <EmailIcon sx={{ mr: 1, color: 'text.secondary' }} />,
              }}
            />

            <Button
              type="submit"
              fullWidth
              variant="contained"
              size="large"
              disabled={loading || !!success}
              sx={{
                mb: 2,
                py: 1.5,
                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                '&:hover': {
                  background: 'linear-gradient(135deg, #764ba2 0%, #667eea 100%)',
                },
              }}
            >
              {loading ? (
                <CircularProgress size={24} sx={{ color: 'white' }} />
              ) : (
                'Send Reset Link'
              )}
            </Button>

            <Box sx={{ textAlign: 'center' }}>
              <MuiLink
                component={Link}
                to="/login"
                sx={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: 0.5,
                  textDecoration: 'none',
                  color: '#667eea',
                  '&:hover': {
                    textDecoration: 'underline',
                  },
                }}
              >
                <ArrowBackIcon fontSize="small" />
                Back to Login
              </MuiLink>
            </Box>
          </form>
        </Paper>
      </Container>
    </Box>
  );
};

export default ForgotPasswordPage;
