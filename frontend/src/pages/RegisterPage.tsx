import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import { register as apiRegister } from '../services/api';
import { TextField, Button, Container, Typography, Box } from '@mui/material';

const RegisterPage: React.FC = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [role, setRole] = useState<'patient' | 'staff' | 'doctor'>('patient');
  const [license, setLicense] = useState('');
  const [error, setError] = useState('');
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
    } catch (err) {
      setError('Failed to register. Please try again.');
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
            SelectProps={{ native: true }}
            inputProps={{ 'aria-label': 'Role' }}
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
          {error && <Typography color="error">{error}</Typography>}
          <Button type="submit" fullWidth variant="contained" sx={{ mt: 3, mb: 2 }}>Sign Up</Button>
          <Typography variant="body2" align="center" sx={{ mt: 1 }}>
            Already have an account? <a href="/login">Sign in</a>
          </Typography>
        </Box>
      </Box>
    </Container>
  );
};

export default RegisterPage;
