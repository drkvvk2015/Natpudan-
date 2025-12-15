/* eslint-disable jsx-a11y/aria-role, jsx-a11y/no-invalid-aria-role, jsx-a11y/no-blank-anchor, jsx-a11y/label-has-associated-control */
import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import { register as apiRegister } from '../services/api';
import { TextField, Button, Container, Typography, Box, Divider, Alert } from '@mui/material';
import { Google as GoogleIcon, GitHub as GitHubIcon, Microsoft as MicrosoftIcon } from '@mui/icons-material';

const RegisterPage: React.FC = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [role, setRole] = useState<'patient' | 'staff' | 'doctor'>('patient');
  const [license, setLicense] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    try {
      const payload: any = { email, password, full_name: fullName, role };
      if (role === 'doctor') {
        payload.license_number = license;
      }
      const { access_token, user } = await apiRegister(payload);
      login(access_token, user);
      navigate('/');
    } catch (err: any) {
      console.error('Registration error:', err);
      let errorMsg = 'Failed to register. Please try again.';
      
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
      setError('');
      setLoading(true);
      
      // Use current origin to ensure redirect URI matches across all ports
      const frontendURL = window.location.origin;
      const redirectUri = `${frontendURL}/auth/callback`;
      const baseURL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';
      
      console.log(`Initiating ${provider} OAuth registration...`);
      console.log(`Using API Base URL: ${baseURL}`);
      console.log(`OAuth redirect URI: ${redirectUri}`);
      
      const response = await fetch(`${baseURL}/api/auth/oauth/${provider}/url?redirect_uri=${encodeURIComponent(redirectUri)}`);
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: 'Unknown error' }));
        setError(errorData.detail || `${provider} login is not available`);
        setLoading(false);
        return;
      }
      
      const data = await response.json();
      
      if (data.auth_url) {
        // Store provider and state for callback
        localStorage.setItem('oauth_provider', provider);
        if (data.state) {
          localStorage.setItem('oauth_state', data.state);
        }
        
        console.log(`Redirecting to ${provider}...`);
        window.location.href = data.auth_url;
      } else {
        setError(`Failed to initiate ${provider} login`);
        setLoading(false);
      }
    } catch (err) {
      setError(`Failed to connect to ${provider}. Please check your internet connection.`);
      console.error(`${provider} login error:`, err);
      setLoading(false);
    }
  };

  return (
    <Container maxWidth="xs">
      <Box sx={{ mt: 8, display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
        <Typography component="h1" variant="h5">Register</Typography>
        <Box component="form" onSubmit={handleSubmit} sx={{ mt: 1 }}>
          <TextField
            margin="normal"
            required
            fullWidth
            id="fullName"
            label="Full Name"
            name="fullName"
            autoComplete="name"
            autoFocus
            value={fullName}
            onChange={(e) => setFullName(e.target.value)}
          />
          <TextField
            margin="normal"
            required
            fullWidth
            id="email"
            label="Email Address"
            name="email"
            autoComplete="email"
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
            autoComplete="new-password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
          <TextField
            margin="normal"
            select
            fullWidth
            id="role"
            label="Role"
            value={role}
            onChange={(e) => setRole(e.target.value as 'patient' | 'staff' | 'doctor')}
            SelectProps={{ native: true, title: 'Select your role' }}
            inputProps={{ 'aria-label': 'Role', title: 'Select your role' }}
          >
            <option value="patient">Patient</option>
            <option value="staff">Staff</option>
            <option value="doctor">Doctor</option>
          </TextField>
          {role === 'doctor' && (
            <TextField
              margin="normal"
              required
              fullWidth
              id="license"
              label="License Number"
              name="license"
              value={license}
              onChange={(e) => setLicense(e.target.value)}
            />
          )}
          {error && <Alert severity="error" sx={{ mt: 2 }}>{typeof error === 'string' ? error : JSON.stringify(error, null, 2)}</Alert>}
          <Button type="submit" fullWidth variant="contained" sx={{ mt: 3, mb: 2 }}>Sign Up</Button>
          
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
            Already have an account? <a href="/login">Sign in</a>
          </Typography>
        </Box>
      </Box>
    </Container>
  );
};

export default RegisterPage;
