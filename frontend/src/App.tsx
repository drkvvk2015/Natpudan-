import React from 'react';
import { CssBaseline, Container, Typography } from '@mui/material';

function App() {
  return (
    <>
      <CssBaseline />
      <Container sx={{ py: 4 }}>
        <Typography variant="h5" gutterBottom>
          Physician AI Assistant UI
        </Typography>
        <Typography variant="body1">
          Frontend is scaffolded. Hook up routes and pages as needed.
        </Typography>
      </Container>
    </>
  );
}

export default App;import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { ThemeProvider, createTheme } from '@mui/material/styles'
import CssBaseline from '@mui/material/CssBaseline'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import Chat from './pages/Chat'
import Diagnosis from './pages/Diagnosis'
import DrugChecker from './pages/DrugChecker'
import KnowledgeBase from './pages/KnowledgeBaseEnhanced'
import MedicalReportParser from './pages/MedicalReportParser'
import PatientIntake from './pages/PatientIntake'
import PatientList from './pages/PatientList'
import TreatmentPlan from './pages/TreatmentPlan'
import AnalyticsDashboard from './pages/AnalyticsDashboard'
import FHIRExplorer from './pages/FHIRExplorer'
import { AuthProvider } from './context/AuthContext'
import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'
import ProtectedRoute from './components/ProtectedRoute'

const theme = createTheme({
// ... (theme configuration remains the same)
});

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <AuthProvider>
        <Router>
          <Routes>
            <Route path="/login" element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />
            <Route
              path="/*"
              element={
                <ProtectedRoute>
                  <Layout>
                    <Routes>
                      <Route path="/" element={<Dashboard />} />
                      <Route path="/chat" element={<Chat />} />
                      <Route path="/diagnosis" element={<Diagnosis />} />
                      <Route path="/drugs" element={<DrugChecker />} />
                      <Route path="/knowledge" element={<KnowledgeBase />} />
                      <Route path="/report-parser" element={<MedicalReportParser />} />
                      <Route path="/patient-intake" element={<PatientIntake />} />
                      <Route path="/patient-intake/edit/:intakeId" element={<PatientIntake />} />
                      <Route path="/patient-intake/view/:intakeId" element={<PatientIntake />} />
                      <Route path="/patients" element={<PatientList />} />
                      <Route path="/treatment-plan/:patientId" element={<TreatmentPlan />} />
                      <Route path="/treatment-plan/:patientId/:planId" element={<TreatmentPlan />} />
                      <Route path="/analytics" element={<AnalyticsDashboard />} />
                      <Route path="/fhir" element={<FHIRExplorer />} />
                    </Routes>
                  </Layout>
                </ProtectedRoute>
              }
            />
          </Routes>
        </Router>
      </AuthProvider>
    </ThemeProvider>
  )
}

export default App
