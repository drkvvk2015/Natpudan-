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

      // Verify state for CSRF protection (warn but don't block if missing)
      if (state && storedState) {
        if (state !== storedState) {
          console.error('State mismatch - possible CSRF attack');
          setError('Security validation failed. Please try logging in again.');
          setTimeout(() => navigate('/login'), 3000);
          return;
        }
      } else {
        console.warn('[OAuth] State parameter missing - CSRF protection bypassed');
      }

      // Store OAuth data for later use
      // Use current origin to ensure consistency (handles dynamic ports like 5174)
      const frontendURL = window.location.origin;
      const redirectUri = `${frontendURL}/auth/callback`;
      
      setOauthData({
        code,
        provider,
        redirect_uri: redirectUri,
        state: state || storedState,
      });
      
      // Show role selection before making API call
      setNeedsRoleSelection(true);
    };

    handleCallback();
  }, [searchParams, navigate]);

  const completeOAuthLogin = async () => {
    if (!oauthData) return;
    
    setLoading(true);
    try {
      console.log('🔄 Exchanging OAuth code for token with role:', selectedRole);
      
      const response = await apiClient.post('/api/auth/oauth/callback', {
        ...oauthData,
        role: selectedRole, // Include selected role
      });

      // Clean up stored OAuth state
      localStorage.removeItem('oauth_state');
      localStorage.removeItem('oauth_provider');

      const { access_token, user } = response.data;
      
      console.log('[OK] OAuth callback successful!');
      console.log('Token received:', access_token ? 'YES' : 'NO');
      console.log('User data:', user);

      // Store token and login
      login(access_token, user);
      
      // Redirect to dashboard
      navigate('/dashboard');
    } catch (err: any) {
      console.error('[ERROR] Complete OAuth login failed:', err);
      const errorMessage = err.response?.data?.detail || err.response?.data?.message || 'Failed to complete login';
      setError(errorMessage);
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
        <Alert severity="error">{typeof error === 'string' ? error : JSON.stringify(error, null, 2)}</Alert>
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
          padding: 3,
        }}
      >
        <Card sx={{ maxWidth: 400, width: '100%' }}>
          <CardContent sx={{ padding: 4 }}>
            <Typography variant="h5" component="h1" gutterBottom align="center">
              Select Your Role
            </Typography>
            <Typography variant="body2" color="text.secondary" align="center" sx={{ mb: 3 }}>
              Choose your role to access the appropriate features
            </Typography>

            <FormControl component="fieldset" sx={{ width: '100%' }}>
              <FormLabel component="legend" sx={{ mb: 2 }}>
                User Role
              </FormLabel>
              <RadioGroup
                value={selectedRole}
                onChange={(e) => setSelectedRole(e.target.value)}
                sx={{ gap: 1 }}
              >
                <FormControlLabel 
                  value="staff" 
                  control={<Radio />} 
                  label={
                    <Box>
                      <Typography variant="subtitle1">Staff</Typography>
                      <Typography variant="body2" color="text.secondary">
                        Basic access - Patient intake, chat assistance
                      </Typography>
                    </Box>
                  }
                />
                <FormControlLabel 
                  value="doctor" 
                  control={<Radio />} 
                  label={
                    <Box>
                      <Typography variant="subtitle1">Doctor</Typography>
                      <Typography variant="body2" color="text.secondary">
                        Full medical access - Diagnosis, prescriptions, knowledge base
                      </Typography>
                    </Box>
                  }
                />
                <FormControlLabel 
                  value="admin" 
                  control={<Radio />} 
                  label={
                    <Box>
                      <Typography variant="subtitle1">Administrator</Typography>
                      <Typography variant="body2" color="text.secondary">
                        System administration - All features + analytics, FHIR
                      </Typography>
                    </Box>
                  }
                />
              </RadioGroup>
            </FormControl>

            <Button
              variant="contained"
              fullWidth
              size="large"
              onClick={completeOAuthLogin}
              disabled={loading}
              sx={{ mt: 3 }}
            >
              {loading ? (
                <>
                  <CircularProgress size={20} sx={{ mr: 1 }} />
                  Completing Sign In...
                </>
              ) : (
                `Continue as ${selectedRole.charAt(0).toUpperCase() + selectedRole.slice(1)}`
              )}
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

export default OAuthCallback;