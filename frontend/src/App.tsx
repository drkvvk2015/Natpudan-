import React from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { ThemeProvider, createTheme } from '@mui/material/styles'
import CssBaseline from '@mui/material/CssBaseline'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import Diagnosis from './pages/Diagnosis'
import DrugChecker from './pages/DrugChecker'
import KnowledgeBase from './pages/KnowledgeBase'
import MedicalReportParser from './pages/MedicalReportParser'
import PatientIntake from './pages/PatientIntake'
import PatientList from './pages/PatientList'
import TreatmentPlan from './pages/TreatmentPlan'
import AnalyticsDashboard from './pages/AnalyticsDashboard'
import FHIRExplorer from './pages/FHIRExplorer'
import LoginPage from './pages/LoginPage'
import ProtectedRoute from './components/ProtectedRoute'
import { AuthProvider } from './context/AuthContext'

const theme = createTheme({})

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <AuthProvider>
        <Router>
          <Routes>
            <Route path="/login" element={<LoginPage />} />
            <Route path="/*" element={
              <ProtectedRoute>
                <Layout>
                  <Routes>
                    <Route path="/" element={<Dashboard />} />
                    <Route path="/diagnosis" element={<ProtectedRoute allowedRoles={["doctor","admin"]}><Diagnosis /></ProtectedRoute>} />
                    <Route path="/drugs" element={<ProtectedRoute allowedRoles={["doctor","admin"]}><DrugChecker /></ProtectedRoute>} />
                    <Route path="/knowledge" element={<ProtectedRoute allowedRoles={["doctor","admin"]}><KnowledgeBase /></ProtectedRoute>} />
                    <Route path="/report-parser" element={<ProtectedRoute allowedRoles={["doctor","admin"]}><MedicalReportParser /></ProtectedRoute>} />
                    <Route path="/patient-intake/*" element={<ProtectedRoute allowedRoles={["staff","doctor","admin"]}><PatientIntake /></ProtectedRoute>} />
                    <Route path="/patients" element={<ProtectedRoute allowedRoles={["doctor","admin"]}><PatientList /></ProtectedRoute>} />
                    <Route path="/treatment-plan/:patientId/*" element={<ProtectedRoute allowedRoles={["doctor","admin"]}><TreatmentPlan /></ProtectedRoute>} />
                    <Route path="/analytics" element={<ProtectedRoute allowedRoles={["admin"]}><AnalyticsDashboard /></ProtectedRoute>} />
                    <Route path="/fhir" element={<ProtectedRoute allowedRoles={["admin"]}><FHIRExplorer /></ProtectedRoute>} />
                  </Routes>
                </Layout>
              </ProtectedRoute>
            } />
          </Routes>
        </Router>
      </AuthProvider>
    </ThemeProvider>
  )
}

export default App
