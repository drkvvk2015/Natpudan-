import React, { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { 
  Box, 
  CircularProgress, 
  Typography, 
  Alert, 
  Card,
  CardContent,
  Button,
  FormControl,
  RadioGroup,
  FormControlLabel,
  Radio,
  FormLabel
} from '@mui/material';
import apiClient from '../services/apiClient';

const OAuthCallback: React.FC = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const { login } = useAuth();
  const [error, setError] = useState('');
  const [needsRoleSelection, setNeedsRoleSelection] = useState(false);
  const [selectedRole, setSelectedRole] = useState('staff');
  const [oauthData, setOauthData] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const handleCallback = async () => {
      const code = searchParams.get('code');
      const state = searchParams.get('state');
      const provider = localStorage.getItem('oauth_provider') || 'google';
      const storedState = localStorage.getItem('oauth_state');
      
      if (!code) {
        setError('No authorization code received');
        setTimeout(() => navigate('/login'), 3000);
        return;
      }

      // Verify state for CSRF protection
      if (state && storedState && state !== storedState) {
        console.error('State mismatch - possible CSRF attack');
        setError('Security validation failed. Please try again.');
        setTimeout(() => navigate('/login'), 3000);
        return;
      }

      // Store OAuth data and show role selection
      const frontendURL = import.meta.env.VITE_FRONTEND_URL || 'http://localhost:5173';
      const redirectUri = `${frontendURL}/auth/callback`;
      
      setOauthData({
        provider,
        code,
        redirect_uri: redirectUri,
      });
      setNeedsRoleSelection(true);
    };

    handleCallback();
  }, [searchParams, navigate]);

  const completeOAuthLogin = async () => {
    if (!oauthData) return;
    
    setLoading(true);
    try {
      const response = await apiClient.post('/api/auth/oauth/callback', {
        ...oauthData,
        role: selectedRole, // Include selected role
      });

      const { access_token, user } = response.data;
      
      console.log('[OK] OAuth callback successful!');
      console.log('Token received:', access_token ? 'YES' : 'NO');
      console.log('User data:', user);
      
      // Clean up OAuth state from localStorage
      localStorage.removeItem('oauth_provider');
      localStorage.removeItem('oauth_state');
      
      console.log('Calling login() with token and user...');
      login(access_token, user);
      
      console.log('Token stored in localStorage:', localStorage.getItem('token') ? 'YES' : 'NO');
      console.log('Navigating to dashboard...');
      navigate('/dashboard');
    } catch (err: any) {
      const errorMsg = err?.response?.data?.detail || 'Failed to complete social login';
      setError(errorMsg);
      console.error('OAuth callback error:', err);
      setTimeout(() => navigate('/login'), 3000);
    } finally {
      setLoading(false);
    }
  };

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

  if (needsRoleSelection) {
    return (
      <Box
        sx={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          minHeight: '100vh',
          gap: 2,
          p: 2,
        }}
      >
        <Card sx={{ maxWidth: 400, width: '100%' }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Complete Your Registration
            </Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
              Please select your role to complete the setup:
            </Typography>
            
            <FormControl component="fieldset" sx={{ width: '100%' }}>
              <FormLabel component="legend">Role</FormLabel>
              <RadioGroup
                value={selectedRole}
                onChange={(e) => setSelectedRole(e.target.value)}
                sx={{ mt: 1 }}
              >
                <FormControlLabel 
                  value="staff" 
                  control={<Radio />} 
                  label="Staff - General medical staff access" 
                />
                <FormControlLabel 
                  value="doctor" 
                  control={<Radio />} 
                  label="Doctor - Full medical access with diagnosis features" 
                />
                <FormControlLabel 
                  value="admin" 
                  control={<Radio />} 
                  label="Admin - Full system administration access" 
                />
              </RadioGroup>
            </FormControl>
            
            <Button
              fullWidth
              variant="contained"
              onClick={completeOAuthLogin}
              disabled={loading}
              sx={{ mt: 3 }}
            >
              {loading ? <CircularProgress size={24} /> : 'Complete Registration'}
            </Button>
          </CardContent>
        </Card>
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
