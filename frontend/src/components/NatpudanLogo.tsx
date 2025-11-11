import React from 'react';
import { SvgIcon, SvgIconProps, Box } from '@mui/material';

interface NatpudanLogoProps extends SvgIconProps {
  variant?: 'icon' | 'full';
}

const NatpudanLogo: React.FC<NatpudanLogoProps> = ({ variant = 'icon', ...props }) => {
  if (variant === 'full') {
    return (
      <Box component="svg" viewBox="0 0 400 100" fill="none" xmlns="http://www.w3.org/2000/svg" sx={{ width: '100%', height: 'auto' }}>
        {/* Icon Part */}
        <g transform="translate(10, 10)">
          {/* Outer circle with gradient */}
          <defs>
            <linearGradient id="logoGradient" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#1976d2" />
              <stop offset="50%" stopColor="#2196f3" />
              <stop offset="100%" stopColor="#4caf50" />
            </linearGradient>
            <linearGradient id="accentGradient" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="#4caf50" />
              <stop offset="100%" stopColor="#8bc34a" />
            </linearGradient>
          </defs>
          
          {/* Main circle background */}
          <circle cx="40" cy="40" r="38" fill="url(#logoGradient)" opacity="0.1" />
          <circle cx="40" cy="40" r="38" fill="none" stroke="url(#logoGradient)" strokeWidth="2" />
          
          {/* Medical Cross */}
          <rect x="36" y="20" width="8" height="40" rx="2" fill="url(#logoGradient)" />
          <rect x="20" y="36" width="40" height="8" rx="2" fill="url(#logoGradient)" />
          
          {/* AI Circuit nodes */}
          <circle cx="25" cy="25" r="3" fill="url(#accentGradient)" />
          <circle cx="55" cy="25" r="3" fill="url(#accentGradient)" />
          <circle cx="25" cy="55" r="3" fill="url(#accentGradient)" />
          <circle cx="55" cy="55" r="3" fill="url(#accentGradient)" />
          
          {/* Circuit connections */}
          <line x1="25" y1="25" x2="36" y2="36" stroke="url(#accentGradient)" strokeWidth="1.5" opacity="0.6" />
          <line x1="55" y1="25" x2="44" y2="36" stroke="url(#accentGradient)" strokeWidth="1.5" opacity="0.6" />
          <line x1="25" y1="55" x2="36" y2="44" stroke="url(#accentGradient)" strokeWidth="1.5" opacity="0.6" />
          <line x1="55" y1="55" x2="44" y2="44" stroke="url(#accentGradient)" strokeWidth="1.5" opacity="0.6" />
          
          {/* Central AI pulse */}
          <circle cx="40" cy="40" r="6" fill="#fff" opacity="0.9" />
          <circle cx="40" cy="40" r="4" fill="url(#accentGradient)" />
        </g>

        {/* Text Part */}
        <text x="100" y="45" fontFamily="Arial, sans-serif" fontSize="28" fontWeight="700" fill="#1976d2">
          Natpudan
        </text>
        <text x="100" y="70" fontFamily="Arial, sans-serif" fontSize="16" fontWeight="400" fill="#4caf50">
          AI Medical Assistant
        </text>
      </Box>
    );
  }

  // Icon only variant
  return (
    <SvgIcon viewBox="0 0 80 80" {...props}>
      <defs>
        <linearGradient id="iconGradient" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stopColor="#1976d2" />
          <stop offset="50%" stopColor="#2196f3" />
          <stop offset="100%" stopColor="#4caf50" />
        </linearGradient>
        <linearGradient id="iconAccent" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stopColor="#4caf50" />
          <stop offset="100%" stopColor="#8bc34a" />
        </linearGradient>
      </defs>
      
      {/* Main circle background */}
      <circle cx="40" cy="40" r="38" fill="url(#iconGradient)" opacity="0.1" />
      <circle cx="40" cy="40" r="38" fill="none" stroke="url(#iconGradient)" strokeWidth="2" />
      
      {/* Medical Cross */}
      <rect x="36" y="20" width="8" height="40" rx="2" fill="url(#iconGradient)" />
      <rect x="20" y="36" width="40" height="8" rx="2" fill="url(#iconGradient)" />
      
      {/* AI Circuit nodes */}
      <circle cx="25" cy="25" r="3" fill="url(#iconAccent)" />
      <circle cx="55" cy="25" r="3" fill="url(#iconAccent)" />
      <circle cx="25" cy="55" r="3" fill="url(#iconAccent)" />
      <circle cx="55" cy="55" r="3" fill="url(#iconAccent)" />
      
      {/* Circuit connections */}
      <line x1="25" y1="25" x2="36" y2="36" stroke="url(#iconAccent)" strokeWidth="1.5" opacity="0.6" />
      <line x1="55" y1="25" x2="44" y2="36" stroke="url(#iconAccent)" strokeWidth="1.5" opacity="0.6" />
      <line x1="25" y1="55" x2="36" y2="44" stroke="url(#iconAccent)" strokeWidth="1.5" opacity="0.6" />
      <line x1="55" y1="55" x2="44" y2="44" stroke="url(#iconAccent)" strokeWidth="1.5" opacity="0.6" />
      
      {/* Central AI pulse */}
      <circle cx="40" cy="40" r="6" fill="#fff" opacity="0.9" />
      <circle cx="40" cy="40" r="4" fill="url(#iconAccent)" />
    </SvgIcon>
  );
};

export default NatpudanLogo;
