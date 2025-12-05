import React from 'react'
import { Navigate, useLocation } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { Box, CircularProgress } from '@mui/material'

type Role = 'staff' | 'doctor' | 'admin'

interface ProtectedRouteProps {
  children: JSX.Element
  allowedRoles?: Role[]
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children, allowedRoles }) => {
  const { isAuthenticated, user, loading } = useAuth()
  const location = useLocation()

  // Don't make routing decisions until auth state is initialized
  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="100vh">
        <CircularProgress />
      </Box>
    )
  }

  if (!isAuthenticated) {
    console.log('ProtectedRoute: User not authenticated, redirecting to login')
    return <Navigate to="/" state={{ from: location }} replace />
  }

  if (allowedRoles && allowedRoles.length > 0) {
    const role: Role | undefined = user?.role
    if (!role || !allowedRoles.includes(role)) {
      console.log('ProtectedRoute: User role not allowed, redirecting to dashboard')
      return <Navigate to="/dashboard" replace />
    }
  }

  console.log('ProtectedRoute: User authenticated and authorized, showing protected page')
  return children
}

export default ProtectedRoute
