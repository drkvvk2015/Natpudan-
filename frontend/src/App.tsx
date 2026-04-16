import React, { Suspense, lazy } from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { ThemeProvider, createTheme } from '@mui/material/styles'
import CssBaseline from '@mui/material/CssBaseline'
import Box from '@mui/material/Box'
import CircularProgress from '@mui/material/CircularProgress'
import Layout from './components/Layout'
import ProtectedRoute from './components/ProtectedRoute'
import PublicRoute from './components/PublicRoute'
import { AuthProvider } from './context/AuthContext'
import FloatingChatBot from './components/FloatingChatBot'

const Dashboard = lazy(() => import('./pages/Dashboard'))
const ClinicalCaseSheet = lazy(() => import('./pages/Diagnosis'))
const DrugChecker = lazy(() => import('./pages/DrugChecker'))
const KnowledgeBase = lazy(() => import('./pages/KnowledgeBase'))
const KnowledgeBaseUpload = lazy(() => import('./pages/KnowledgeBaseUpload'))
const MedicalReportParser = lazy(() => import('./pages/MedicalReportParser'))
const PatientIntake = lazy(() => import('./pages/PatientIntake'))
const PatientList = lazy(() => import('./pages/PatientList'))
const TreatmentPlan = lazy(() => import('./pages/TreatmentPlan'))
const AnalyticsDashboard = lazy(() => import('./pages/AnalyticsDashboard'))
const FHIRExplorer = lazy(() => import('./pages/FHIRExplorer'))
const LoginPage = lazy(() => import('./pages/LoginPage'))
const RegisterPage = lazy(() => import('./pages/RegisterPage'))
const ForgotPasswordPage = lazy(() => import('./pages/ForgotPasswordPage'))
const ResetPasswordPage = lazy(() => import('./pages/ResetPasswordPage'))
const OAuthCallback = lazy(() => import('./pages/OAuthCallback'))
const ChatPage = lazy(() => import('./pages/ChatPage'))
const DischargeSummaryPage = lazy(() => import('./pages/DischargeSummaryPage'))

const theme = createTheme({})

const routeFallback = (
  <Box display="flex" justifyContent="center" alignItems="center" minHeight="50vh">
    <CircularProgress />
  </Box>
)

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <AuthProvider>
        <Router future={{ 
          v7_startTransition: true,
          v7_relativeSplatPath: true 
        }}>
          <FloatingChatBot />
          <Suspense fallback={routeFallback}>
            <Routes>
              <Route path="/" element={<PublicRoute><LoginPage /></PublicRoute>} />
              <Route path="/login" element={<PublicRoute><LoginPage /></PublicRoute>} />
              <Route path="/register" element={<PublicRoute><RegisterPage /></PublicRoute>} />
              <Route path="/forgot-password" element={<PublicRoute><ForgotPasswordPage /></PublicRoute>} />
              <Route path="/reset-password" element={<PublicRoute><ResetPasswordPage /></PublicRoute>} />
              <Route path="/auth/callback" element={<OAuthCallback />} />
              <Route path="/dashboard" element={<ProtectedRoute><Layout><Dashboard /></Layout></ProtectedRoute>} />
              <Route path="/chat" element={<ProtectedRoute><Layout><ChatPage /></Layout></ProtectedRoute>} />
              <Route path="/discharge-summary" element={<ProtectedRoute allowedRoles={["doctor","admin"]}><Layout><DischargeSummaryPage /></Layout></ProtectedRoute>} />
              <Route path="/diagnosis" element={<ProtectedRoute allowedRoles={["doctor","admin"]}><Layout><ClinicalCaseSheet /></Layout></ProtectedRoute>} />
              <Route path="/drugs" element={<ProtectedRoute allowedRoles={["doctor","admin"]}><Layout><DrugChecker /></Layout></ProtectedRoute>} />
              <Route path="/knowledge" element={<ProtectedRoute allowedRoles={["doctor","admin"]}><Layout><KnowledgeBase /></Layout></ProtectedRoute>} />
              <Route path="/knowledge-upload" element={<ProtectedRoute allowedRoles={["doctor","admin"]}><Layout><KnowledgeBaseUpload /></Layout></ProtectedRoute>} />
              <Route path="/report-parser" element={<ProtectedRoute allowedRoles={["doctor","admin"]}><Layout><MedicalReportParser /></Layout></ProtectedRoute>} />
              <Route path="/patient-intake/*" element={<ProtectedRoute allowedRoles={["staff","doctor","admin"]}><Layout><PatientIntake /></Layout></ProtectedRoute>} />
              <Route path="/patients" element={<ProtectedRoute allowedRoles={["doctor","admin"]}><Layout><PatientList /></Layout></ProtectedRoute>} />
              <Route path="/treatment-plan/:patientId/*" element={<ProtectedRoute allowedRoles={["doctor","admin"]}><Layout><TreatmentPlan /></Layout></ProtectedRoute>} />
              <Route path="/analytics" element={<ProtectedRoute allowedRoles={["admin"]}><Layout><AnalyticsDashboard /></Layout></ProtectedRoute>} />
              <Route path="/fhir" element={<ProtectedRoute allowedRoles={["admin"]}><Layout><FHIRExplorer /></Layout></ProtectedRoute>} />
            </Routes>
          </Suspense>
        </Router>
      </AuthProvider>
    </ThemeProvider>
  )
}

export default App
