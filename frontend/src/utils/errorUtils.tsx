/**
 * Utility function to safely format error objects for display in React components
 * @param error - The error to format (string, object, or any)
 * @returns A string representation of the error suitable for display
 */
export function formatErrorForDisplay(error: any): string {
  if (typeof error === 'string') {
    return error;
  }
  
  if (error?.message) {
    return error.message;
  }
  
  if (error?.detail) {
    return typeof error.detail === 'string' ? error.detail : JSON.stringify(error.detail, null, 2);
  }
  
  if (error && typeof error === 'object') {
    // Handle Pydantic validation errors with type, loc, msg, input structure
    if (error.type && error.msg) {
      return `Validation Error: ${error.msg}`;
    }
    
    return JSON.stringify(error, null, 2);
  }
  
  return String(error || 'Unknown error');
}

/**
 * Component to safely render errors
 */
import React from 'react';
import { Alert, AlertProps } from '@mui/material';

interface ErrorDisplayProps extends Omit<AlertProps, 'children'> {
  error: any;
  onClose?: () => void;
}

export const ErrorDisplay: React.FC<ErrorDisplayProps> = ({ error, onClose, ...alertProps }) => {
  if (!error) return null;
  
  return (
    <Alert severity="error" onClose={onClose} {...alertProps}>
      {formatErrorForDisplay(error)}
    </Alert>
  );
};