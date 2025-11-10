import React from 'react'
import { Navigate, useLocation } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

type Role = 'staff' | 'doctor' | 'admin'

interface ProtectedRouteProps {
  children: JSX.Element
  allowedRoles?: Role[]
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children, allowedRoles }) => {
  const { isAuthenticated, user } = useAuth()
  const location = useLocation()

  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />
  }

  if (allowedRoles && allowedRoles.length > 0) {
    const role: Role | undefined = user?.role
    if (!role || !allowedRoles.includes(role)) {
      return <Navigate to="/" replace />
    }
  }

  return children
}

export default ProtectedRoute
