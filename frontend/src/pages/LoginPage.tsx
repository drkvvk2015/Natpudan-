import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import { login as apiLogin } from '../services/api';
import { TextField, Button, Container, Typography, Box, Divider, Alert } from '@mui/material';
import { Google as GoogleIcon, GitHub as GitHubIcon, Microsoft as MicrosoftIcon } from '@mui/icons-material';

const LoginPage: React.FC = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    try {
      const { access_token, user } = await apiLogin({ email, password });
      login(access_token, user);
      navigate('/');
    } catch (err: any) {
      console.error('Login error:', err);
      let errorMsg = 'Failed to login. Please check your credentials.';
      
      if (err?.response?.data?.detail) {
        const detail = err.response.data.detail;
        // Handle validation errors array
        if (Array.isArray(detail)) {
          errorMsg = detail.map((e: any) => e.msg || e.message || String(e)).join(', ');
        } else if (typeof detail === 'string') {
          errorMsg = detail;
        } else if (typeof detail === 'object') {
          errorMsg = detail.msg || detail.message || JSON.stringify(detail);
        }
      } else if (err?.message) {
        errorMsg = err.message;
      }
      
      setError(errorMsg);
    }
  };

  const handleSocialLogin = async (provider: 'google' | 'github' | 'microsoft') => {
    try {
      const redirectUri = `${window.location.origin}/auth/callback`;
      const baseURL = (import.meta as any).env?.VITE_API_BASE_URL || 'http://localhost:8001';
      const response = await fetch(`${baseURL}/api/auth/oauth/${provider}/url?redirect_uri=${encodeURIComponent(redirectUri)}`);
      const data = await response.json();
      
      if (data.auth_url) {
        window.location.href = data.auth_url;
      } else {
        setError(`Failed to initiate ${provider} login`);
      }
    } catch (err) {
      setError(`Failed to connect to ${provider}`);
      console.error(`${provider} login error:`, err);
    }
  };

  return (
    <Container maxWidth="xs">
      <Box sx={{ mt: 8, display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
        <Typography component="h1" variant="h5">
          Login
        </Typography>
        <Box component="form" onSubmit={handleSubmit} sx={{ mt: 1 }}>
          <TextField
            margin="normal"
            required
            fullWidth
            id="email"
            label="Email Address"
            name="email"
            autoComplete="email"
            autoFocus
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />
          <TextField
            margin="normal"
            required
            fullWidth
            name="password"
            label="Password"
            type="password"
            id="password"
            autoComplete="current-password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
          {error && <Alert severity="error" sx={{ mt: 2 }}>{error}</Alert>}
          <Button
            type="submit"
            fullWidth
            variant="contained"
            sx={{ mt: 3, mb: 2 }}
          >
            Sign In
          </Button>
          
          <Divider sx={{ my: 2 }}>
            <Typography variant="body2" color="text.secondary">OR</Typography>
          </Divider>
          
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1, mb: 2 }}>
            <Button
              fullWidth
              variant="outlined"
              startIcon={<GoogleIcon />}
              onClick={() => handleSocialLogin('google')}
              sx={{ 
                textTransform: 'none',
                borderColor: '#4285F4',
                color: '#4285F4',
                '&:hover': { borderColor: '#357ae8', backgroundColor: '#4285F410' }
              }}
            >
              Continue with Google
            </Button>
            <Button
              fullWidth
              variant="outlined"
              startIcon={<GitHubIcon />}
              onClick={() => handleSocialLogin('github')}
              sx={{ 
                textTransform: 'none',
                borderColor: '#333',
                color: '#333',
                '&:hover': { borderColor: '#000', backgroundColor: '#33333310' }
              }}
            >
              Continue with GitHub
            </Button>
            <Button
              fullWidth
              variant="outlined"
              startIcon={<MicrosoftIcon />}
              onClick={() => handleSocialLogin('microsoft')}
              sx={{ 
                textTransform: 'none',
                borderColor: '#00A4EF',
                color: '#00A4EF',
                '&:hover': { borderColor: '#0078D4', backgroundColor: '#00A4EF10' }
              }}
            >
              Continue with Microsoft
            </Button>
          </Box>
          
          <Typography variant="body2" align="center" sx={{ mt: 1 }}>
            New here? <a href="/register">Create an account</a>
          </Typography>
        </Box>
      </Box>
    </Container>
  );
};

export default LoginPage;
