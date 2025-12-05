import React from 'react'
import { Navigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { Box, CircularProgress } from '@mui/material'

interface PublicRouteProps {
  children: JSX.Element
}

const PublicRoute: React.FC<PublicRouteProps> = ({ children }) => {
  const { isAuthenticated, loading } = useAuth()

  // Don't make routing decisions until auth state is initialized
  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="100vh">
        <CircularProgress />
      </Box>
    )
  }

  // If user is authenticated, redirect to dashboard
  if (isAuthenticated) {
    console.log('PublicRoute: User is authenticated, redirecting to dashboard')
    return <Navigate to="/dashboard" replace />
  }

  // Otherwise, show the public page (login, register, etc.)
  console.log('PublicRoute: User not authenticated, showing public page')
  return children
}

export default PublicRoute
