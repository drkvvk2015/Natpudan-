import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate, Link } from 'react-router-dom';
import { login as apiLogin } from '../services/api';
import { TextField, Button, Container, Typography, Box, Divider, Alert } from '@mui/material';
import { Google as GoogleIcon, GitHub as GitHubIcon, Microsoft as MicrosoftIcon } from '@mui/icons-material';

const LoginPage: React.FC = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [loginSuccess, setLoginSuccess] = useState(false);
  const { login, isAuthenticated } = useAuth();
  const navigate = useNavigate();

  // Navigate to dashboard after successful login (once auth state updates)
  useEffect(() => {
    if (loginSuccess && isAuthenticated) {
      console.log('LoginPage: Auth state confirmed, navigating to dashboard');
      navigate('/dashboard');
    }
  }, [loginSuccess, isAuthenticated, navigate]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    try {
      console.log('LoginPage: Submitting login...');
      const { access_token, user } = await apiLogin({ email, password });
      console.log('LoginPage: API login successful, calling context login()');
      login(access_token, user);
      setLoginSuccess(true); // This will trigger navigation via useEffect
      console.log('LoginPage: Login context updated, waiting for auth state...');
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
      setLoading(false);
    }
  };

  const handleSocialLogin = async (provider: 'google' | 'github' | 'microsoft') => {
    try {
      setError(''); // Clear previous errors
      setLoading(true);
      
      const frontendURL = import.meta.env.VITE_FRONTEND_URL || 'http://localhost:5173';
      const redirectUri = `${frontendURL}/auth/callback`;
      const baseURL = import.meta.env.VITE_API_URL || import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';
      
      console.log(`Initiating ${provider} OAuth flow...`);
      console.log(`Using API Base URL: ${baseURL}`);
      console.log(`OAuth redirect URI: ${redirectUri}`);
      
      const response = await fetch(`${baseURL}/api/auth/oauth/${provider}/url?redirect_uri=${encodeURIComponent(redirectUri)}`);
      
      // Check if response is ok
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }));
        const errorMsg = errorData.detail || errorData.error || `${provider} login is not available`;
        setError(errorMsg);
        console.error(`OAuth error for ${provider}:`, errorData);
        setLoading(false);
        return;
      }
      
      const data = await response.json();
      
      if (data.auth_url) {
        // Store provider and state for callback verification
        localStorage.setItem('oauth_provider', provider);
        if (data.state) {
          localStorage.setItem('oauth_state', data.state);
        }
        
        console.log(`Redirecting to ${provider} OAuth authorization page...`);
        // Redirect to OAuth provider
        window.location.href = data.auth_url;
      } else {
        const errorMsg = data.detail || data.error || `Failed to initiate ${provider} login. No auth URL returned.`;
        setError(errorMsg);
        setLoading(false);
      }
    } catch (err: any) {
      console.error(`Social login error for ${provider}:`, err);
      const errorMsg = err?.message || `Failed to connect to ${provider}. Please check your internet connection and try again.`;
      setError(errorMsg);
      setLoading(false);
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
          {error && <Alert severity="error" sx={{ mt: 2 }}>{typeof error === 'string' ? error : JSON.stringify(error, null, 2)}</Alert>}
          <Button
            type="submit"
            fullWidth
            variant="contained"
            sx={{ mt: 3, mb: 1 }}
          >
            Sign In
          </Button>
          
          <Box sx={{ textAlign: 'center', mb: 2 }}>
            <Typography
              component={Link}
              to="/forgot-password"
              variant="body2"
              sx={{
                color: 'primary.main',
                textDecoration: 'none',
                '&:hover': {
                  textDecoration: 'underline',
                },
              }}
            >
              Forgot password?
            </Typography>
          </Box>
          
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
