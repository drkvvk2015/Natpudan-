import React from "react";
import {
  BrowserRouter as Router,
  Routes,
  Route,
  Navigate,
} from "react-router-dom";
import { ThemeProvider, createTheme } from "@mui/material/styles";
import CssBaseline from "@mui/material/CssBaseline";
import Layout from "./components/Layout";
import Dashboard from "./pages/Dashboard";
import ClinicalCaseSheet from "./pages/Diagnosis";
import DrugChecker from "./pages/DrugChecker";
import KnowledgeBase from "./pages/KnowledgeBase";
import KnowledgeBaseUpload from "./pages/KnowledgeBaseUpload";
import MedicalReportParser from "./pages/MedicalReportParser";
import PatientIntake from "./pages/PatientIntake";
import PatientList from "./pages/PatientList";
import TreatmentPlan from "./pages/TreatmentPlan";
import AnalyticsDashboard from "./pages/AnalyticsDashboard";
import FHIRExplorer from "./pages/FHIRExplorer";
import UserManagement from "./pages/admin/UserManagement";
import LoginPage from "./pages/LoginPage";
import RegisterPage from "./pages/RegisterPage";
import ForgotPasswordPage from "./pages/ForgotPasswordPage";
import ResetPasswordPage from "./pages/ResetPasswordPage";
import OAuthCallback from "./pages/OAuthCallback";
import ChatPage from "./pages/ChatPage";
import DischargeSummaryPage from "./pages/DischargeSummaryPage";
import ProtectedRoute from "./components/ProtectedRoute";
import PublicRoute from "./components/PublicRoute";
import { AuthProvider } from "./context/AuthContext";
import FloatingChatBot from "./components/FloatingChatBot";

const theme = createTheme({});

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <AuthProvider>
        <Router
          future={{
            v7_startTransition: true,
            v7_relativeSplatPath: true,
          }}
        >
          <FloatingChatBot />
          <Routes>
            <Route
              path="/"
              element={
                <PublicRoute>
                  <LoginPage />
                </PublicRoute>
              }
            />
            <Route
              path="/login"
              element={
                <PublicRoute>
                  <LoginPage />
                </PublicRoute>
              }
            />
            <Route
              path="/register"
              element={
                <PublicRoute>
                  <RegisterPage />
                </PublicRoute>
              }
            />
            <Route
              path="/forgot-password"
              element={
                <PublicRoute>
                  <ForgotPasswordPage />
                </PublicRoute>
              }
            />
            <Route
              path="/reset-password"
              element={
                <PublicRoute>
                  <ResetPasswordPage />
                </PublicRoute>
              }
            />
            <Route path="/auth/callback" element={<OAuthCallback />} />
            <Route
              path="/dashboard"
              element={
                <ProtectedRoute>
                  <Layout>
                    <Dashboard />
                  </Layout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/chat"
              element={
                <ProtectedRoute>
                  <Layout>
                    <ChatPage />
                  </Layout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/discharge-summary"
              element={
                <ProtectedRoute allowedRoles={["doctor", "admin"]}>
                  <Layout>
                    <DischargeSummaryPage />
                  </Layout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/diagnosis"
              element={
                <ProtectedRoute allowedRoles={["doctor", "admin"]}>
                  <Layout>
                    <ClinicalCaseSheet />
                  </Layout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/drugs"
              element={
                <ProtectedRoute allowedRoles={["doctor", "admin"]}>
                  <Layout>
                    <DrugChecker />
                  </Layout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/knowledge"
              element={
                <ProtectedRoute allowedRoles={["doctor", "admin"]}>
                  <Layout>
                    <KnowledgeBase />
                  </Layout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/knowledge-upload"
              element={
                <ProtectedRoute allowedRoles={["doctor", "admin"]}>
                  <Layout>
                    <KnowledgeBaseUpload />
                  </Layout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/report-parser"
              element={
                <ProtectedRoute allowedRoles={["doctor", "admin"]}>
                  <Layout>
                    <MedicalReportParser />
                  </Layout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/patient-intake/*"
              element={
                <ProtectedRoute allowedRoles={["staff", "doctor", "admin"]}>
                  <Layout>
                    <PatientIntake />
                  </Layout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/patients"
              element={
                <ProtectedRoute allowedRoles={["doctor", "admin"]}>
                  <Layout>
                    <PatientList />
                  </Layout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/treatment-plan/:patientId/*"
              element={
                <ProtectedRoute allowedRoles={["doctor", "admin"]}>
                  <Layout>
                    <TreatmentPlan />
                  </Layout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/analytics"
              element={
                <ProtectedRoute allowedRoles={["admin"]}>
                  <Layout>
                    <AnalyticsDashboard />
                  </Layout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/fhir"
              element={
                <ProtectedRoute allowedRoles={["admin"]}>
                  <Layout>
                    <FHIRExplorer />
                  </Layout>
                </ProtectedRoute>
              }
            />
            <Route
              path="/admin/users"
              element={
                <ProtectedRoute allowedRoles={["admin"]}>
                  <Layout>
                    <UserManagement />
                  </Layout>
                </ProtectedRoute>
              }
            />
          </Routes>
        </Router>
      </AuthProvider>
    </ThemeProvider>
  );
}

export default App;
