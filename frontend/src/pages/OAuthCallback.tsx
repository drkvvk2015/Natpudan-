import React, { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Box, CircularProgress, Typography, Alert } from '@mui/material';
import apiClient from '../services/apiClient';

const OAuthCallback: React.FC = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const { login } = useAuth();
  const [error, setError] = useState('');

  useEffect(() => {
    const handleCallback = async () => {
      const code = searchParams.get('code');
      const provider = searchParams.get('state') || localStorage.getItem('oauth_provider') || 'google';
      
      if (!code) {
        setError('No authorization code received');
        setTimeout(() => navigate('/login'), 3000);
        return;
      }

      try {
        const redirectUri = `${window.location.origin}/auth/callback`;
        const response = await apiClient.post('/api/auth/oauth/callback', {
          provider,
          code,
          redirect_uri: redirectUri,
        });

        const { access_token, user } = response.data;
        login(access_token, user);
        navigate('/dashboard');
      } catch (err: any) {
        const errorMsg = err?.response?.data?.detail || 'Failed to complete social login';
        setError(errorMsg);
        console.error('OAuth callback error:', err);
        setTimeout(() => navigate('/login'), 3000);
      }
    };

    handleCallback();
  }, [searchParams, navigate, login]);

  if (error) {
    return (
      <Box
        sx={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          minHeight: '100vh',
          gap: 2,
        }}
      >
        <Alert severity="error">{error}</Alert>
        <Typography variant="body2" color="text.secondary">
          Redirecting to login...
        </Typography>
      </Box>
    );
  }

  return (
    <Box
      sx={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        minHeight: '100vh',
        gap: 2,
      }}
    >
      <CircularProgress size={60} />
      <Typography variant="h6">Completing sign in...</Typography>
      <Typography variant="body2" color="text.secondary">
        Please wait while we verify your credentials
      </Typography>
    </Box>
  );
};

export default OAuthCallback;
