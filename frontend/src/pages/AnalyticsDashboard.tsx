import React, { useState, useEffect } from 'react'
import {
  Box,
  Container,
  Typography,
  Paper,
  Grid,
  Card,
  CardContent,
  CircularProgress,
  Alert,
  Divider,
  Chip,
  useTheme
} from '@mui/material'
import {
  People as PeopleIcon,
  LocalHospital as LocalHospitalIcon,
  Medication as MedicationIcon,
  TrendingUp as TrendingUpIcon,
  Assessment as AssessmentIcon,
  EventNote as EventNoteIcon
} from '@mui/icons-material'
import {
  BarChart,
  Bar,
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts'
import { getAnalyticsDashboard, AnalyticsDashboardResponse } from '../services/api'

const AnalyticsDashboard: React.FC = () => {
  const theme = useTheme()
  const [data, setData] = useState<AnalyticsDashboardResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const COLORS = ['#667eea', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899', '#06b6d4']

  useEffect(() => {
    fetchAnalytics()
  }, [])

  const fetchAnalytics = async () => {
    setLoading(true)
    setError(null)
    try {
      const response = await getAnalyticsDashboard()
      setData(response)
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load analytics data')
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
        <Box display="flex" justifyContent="center" alignItems="center" minHeight="60vh">
          <CircularProgress size={60} />
        </Box>
      </Container>
    )
  }

  if (error || !data) {
    return (
      <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
        <Alert severity="error">{error || 'No data available'}</Alert>
      </Container>
    )
  }

  // Prepare chart data
  const ageChartData = Object.entries(data.demographics.age_distribution).map(([age, count]) => ({
    age,
    count
  }))

  const genderChartData = Object.entries(data.demographics.gender_distribution).map(([gender, count]) => ({
    name: gender,
    value: count
  }))

  const bloodTypeChartData = Object.entries(data.demographics.blood_type_distribution).map(([type, count]) => ({
    name: type,
    value: count
  }))

  const treatmentStatusData = [
    { name: 'Active', value: data.treatment_outcomes.active_treatments, color: '#10b981' },
    { name: 'Completed', value: data.treatment_outcomes.completed_treatments, color: '#667eea' },
    { name: 'Discontinued', value: data.treatment_outcomes.discontinued_treatments, color: '#ef4444' },
    { name: 'On Hold', value: data.treatment_outcomes.on_hold_treatments, color: '#f59e0b' }
  ]

  const riskChartData = Object.entries(data.performance_metrics.risk_assessment_summary).map(([level, count]) => ({
    name: level.charAt(0).toUpperCase() + level.slice(1),
    value: count
  }))

  return (
    <Container maxWidth="xl" sx={{ mt: 4, mb: 4 }}>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" gutterBottom fontWeight="bold">
          <AssessmentIcon sx={{ mr: 1, verticalAlign: 'middle', fontSize: 40 }} />
          Analytics Dashboard
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Generated: {new Date(data.generated_at).toLocaleString()}
        </Typography>
      </Box>

      {/* Summary Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', color: 'white' }}>
            <CardContent>
              <Box display="flex" justifyContent="space-between" alignItems="center">
                <Box>
                  <Typography variant="h4" fontWeight="bold">
                    {data.demographics.total_patients}
                  </Typography>
                  <Typography variant="body2">Total Patients</Typography>
                </Box>
                <PeopleIcon sx={{ fontSize: 50, opacity: 0.7 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)', color: 'white' }}>
            <CardContent>
              <Box display="flex" justifyContent="space-between" alignItems="center">
                <Box>
                  <Typography variant="h4" fontWeight="bold">
                    {data.disease_trends.total_diagnoses}
                  </Typography>
                  <Typography variant="body2">Total Diagnoses</Typography>
                </Box>
                <LocalHospitalIcon sx={{ fontSize: 50, opacity: 0.7 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ background: 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)', color: 'white' }}>
            <CardContent>
              <Box display="flex" justifyContent="space-between" alignItems="center">
                <Box>
                  <Typography variant="h4" fontWeight="bold">
                    {data.treatment_outcomes.total_treatment_plans}
                  </Typography>
                  <Typography variant="body2">Treatment Plans</Typography>
                </Box>
                <EventNoteIcon sx={{ fontSize: 50, opacity: 0.7 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ background: 'linear-gradient(135deg, #ef4444 0%, #dc2626 100%)', color: 'white' }}>
            <CardContent>
              <Box display="flex" justifyContent="space-between" alignItems="center">
                <Box>
                  <Typography variant="h4" fontWeight="bold">
                    {data.treatment_outcomes.medication_statistics.total}
                  </Typography>
                  <Typography variant="body2">Total Medications</Typography>
                </Box>
                <MedicationIcon sx={{ fontSize: 50, opacity: 0.7 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Demographics Section */}
      <Paper elevation={3} sx={{ p: 3, mb: 3 }}>
        <Typography variant="h5" gutterBottom fontWeight="bold">
          Patient Demographics
        </Typography>
        <Divider sx={{ mb: 3 }} />

        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Typography variant="h6" gutterBottom align="center">
              Age Distribution
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={ageChartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="age" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="count" fill="#667eea" />
              </BarChart>
            </ResponsiveContainer>
            <Box textAlign="center" mt={2}>
              <Typography variant="body2" color="text.secondary">
                Average Age: <strong>{data.demographics.average_age} years</strong>
              </Typography>
            </Box>
          </Grid>

          <Grid item xs={12} md={3}>
            <Typography variant="h6" gutterBottom align="center">
              Gender Distribution
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={genderChartData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={(entry) => `${entry.name}: ${entry.value}`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {genderChartData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </Grid>

          <Grid item xs={12} md={3}>
            <Typography variant="h6" gutterBottom align="center">
              Blood Type Distribution
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={bloodTypeChartData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={(entry) => `${entry.name}: ${entry.value}`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {bloodTypeChartData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </Grid>
        </Grid>
      </Paper>

      {/* Disease Trends Section */}
      <Paper elevation={3} sx={{ p: 3, mb: 3 }}>
        <Typography variant="h5" gutterBottom fontWeight="bold">
          Disease Trends
        </Typography>
        <Divider sx={{ mb: 3 }} />

        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Typography variant="h6" gutterBottom>
              Top 10 Diagnoses
            </Typography>
            <Box>
              {data.disease_trends.top_diagnoses.slice(0, 10).map((diagnosis, index) => (
                <Box key={index} sx={{ mb: 2 }}>
                  <Box display="flex" justifyContent="space-between" alignItems="center" mb={0.5}>
                    <Typography variant="body2">{diagnosis.diagnosis}</Typography>
                    <Chip
                      label={`${diagnosis.count} (${diagnosis.percentage}%)`}
                      size="small"
                      color="primary"
                    />
                  </Box>
                  <Box sx={{ width: '100%', bgcolor: '#e0e0e0', height: 8, borderRadius: 1 }}>
                    <Box
                      sx={{
                        width: `${diagnosis.percentage}%`,
                        bgcolor: COLORS[index % COLORS.length],
                        height: 8,
                        borderRadius: 1
                      }}
                    />
                  </Box>
                </Box>
              ))}
            </Box>
          </Grid>

          <Grid item xs={12} md={6}>
            <Typography variant="h6" gutterBottom>
              Diagnoses by Month (Last 12 Months)
            </Typography>
            <ResponsiveContainer width="100%" height={400}>
              <LineChart data={data.disease_trends.diagnoses_by_month}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="month" angle={-45} textAnchor="end" height={80} />
                <YAxis />
                <Tooltip />
                <Legend />
                <Line type="monotone" dataKey="count" stroke="#667eea" strokeWidth={2} />
              </LineChart>
            </ResponsiveContainer>
          </Grid>
        </Grid>
      </Paper>

      {/* Treatment Outcomes Section */}
      <Paper elevation={3} sx={{ p: 3, mb: 3 }}>
        <Typography variant="h5" gutterBottom fontWeight="bold">
          Treatment Outcomes
        </Typography>
        <Divider sx={{ mb: 3 }} />

        <Grid container spacing={3}>
          <Grid item xs={12} md={4}>
            <Typography variant="h6" gutterBottom align="center">
              Treatment Status
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={treatmentStatusData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={(entry) => `${entry.name}: ${entry.value}`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {treatmentStatusData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
            <Box textAlign="center" mt={2}>
              <Typography variant="body2" color="text.secondary">
                Average Duration: <strong>{data.treatment_outcomes.average_treatment_duration} days</strong>
              </Typography>
            </Box>
          </Grid>

          <Grid item xs={12} md={4}>
            <Typography variant="h6" gutterBottom align="center">
              Medication Statistics
            </Typography>
            <Box sx={{ p: 2 }}>
              <Box sx={{ mb: 2 }}>
                <Typography variant="body2" color="text.secondary">Total Medications</Typography>
                <Typography variant="h4" color="primary">
                  {data.treatment_outcomes.medication_statistics.total}
                </Typography>
              </Box>
              <Box sx={{ mb: 2 }}>
                <Typography variant="body2" color="text.secondary">Active</Typography>
                <Typography variant="h5" color="success.main">
                  {data.treatment_outcomes.medication_statistics.active}
                </Typography>
              </Box>
              <Box sx={{ mb: 2 }}>
                <Typography variant="body2" color="text.secondary">Discontinued</Typography>
                <Typography variant="h5" color="error.main">
                  {data.treatment_outcomes.medication_statistics.discontinued}
                </Typography>
              </Box>
              <Box>
                <Typography variant="body2" color="text.secondary">Discontinuation Rate</Typography>
                <Typography variant="h5" color="warning.main">
                  {data.treatment_outcomes.medication_statistics.discontinuation_rate}%
                </Typography>
              </Box>
            </Box>
          </Grid>

          <Grid item xs={12} md={4}>
            <Typography variant="h6" gutterBottom align="center">
              Follow-up Statistics
            </Typography>
            <Box sx={{ p: 2 }}>
              <Box sx={{ mb: 2 }}>
                <Typography variant="body2" color="text.secondary">Total Follow-ups</Typography>
                <Typography variant="h4" color="primary">
                  {data.treatment_outcomes.follow_up_statistics.total}
                </Typography>
              </Box>
              <Box sx={{ mb: 2 }}>
                <Typography variant="body2" color="text.secondary">Completed</Typography>
                <Typography variant="h5" color="success.main">
                  {data.treatment_outcomes.follow_up_statistics.completed}
                </Typography>
              </Box>
              <Box sx={{ mb: 2 }}>
                <Typography variant="body2" color="text.secondary">Scheduled</Typography>
                <Typography variant="h5" color="info.main">
                  {data.treatment_outcomes.follow_up_statistics.scheduled}
                </Typography>
              </Box>
              <Box>
                <Typography variant="body2" color="text.secondary">Completion Rate</Typography>
                <Typography variant="h5" color="success.main">
                  {data.treatment_outcomes.follow_up_statistics.completion_rate}%
                </Typography>
              </Box>
            </Box>
          </Grid>
        </Grid>
      </Paper>

      {/* Performance Metrics Section */}
      <Paper elevation={3} sx={{ p: 3, mb: 3 }}>
        <Typography variant="h5" gutterBottom fontWeight="bold">
          Performance Metrics
        </Typography>
        <Divider sx={{ mb: 3 }} />

        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <Typography variant="h6" gutterBottom>
              Patient Intake Rate (Last 12 Months)
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={data.performance_metrics.patient_intake_rate.monthly_data}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="month" angle={-45} textAnchor="end" height={80} />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="count" fill="#10b981" />
              </BarChart>
            </ResponsiveContainer>
            <Box textAlign="center" mt={2}>
              <Typography variant="body2" color="text.secondary">
                Average Monthly: <strong>{data.performance_metrics.patient_intake_rate.average_monthly}</strong>
                {' | '}Total Last Year: <strong>{data.performance_metrics.patient_intake_rate.total_last_year}</strong>
              </Typography>
            </Box>
          </Grid>

          <Grid item xs={12} md={6}>
            <Typography variant="h6" gutterBottom align="center">
              Risk Assessment Summary
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={riskChartData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={(entry) => `${entry.name}: ${entry.value}`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {riskChartData.map((entry, index) => {
                    const color = entry.name === 'High' ? '#ef4444' : entry.name === 'Medium' ? '#f59e0b' : '#10b981'
                    return <Cell key={`cell-${index}`} fill={color} />
                  })}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </Grid>
        </Grid>

        <Grid container spacing={3} sx={{ mt: 2 }}>
          <Grid item xs={12} md={6}>
            <Typography variant="h6" gutterBottom>
              Travel History Summary
            </Typography>
            <Box sx={{ p: 2, bgcolor: '#f5f5f5', borderRadius: 2 }}>
              <Typography variant="body1" gutterBottom>
                <strong>Total Records:</strong> {data.performance_metrics.travel_history_summary.total_records}
              </Typography>
              <Typography variant="body1" gutterBottom>
                <strong>Unique Countries:</strong> {data.performance_metrics.travel_history_summary.unique_countries}
              </Typography>
              <Typography variant="body2" gutterBottom sx={{ mt: 2 }}>
                <strong>Top Destinations:</strong>
              </Typography>
              {data.performance_metrics.travel_history_summary.top_destinations.map((dest, index) => (
                <Chip
                  key={index}
                  label={`${dest.destination}, ${dest.country} (${dest.count})`}
                  size="small"
                  sx={{ mr: 1, mb: 1 }}
                />
              ))}
            </Box>
          </Grid>

          <Grid item xs={12} md={6}>
            <Typography variant="h6" gutterBottom>
              Family History Summary
            </Typography>
            <Box sx={{ p: 2, bgcolor: '#f5f5f5', borderRadius: 2 }}>
              <Typography variant="body1" gutterBottom>
                <strong>Total Records:</strong> {data.performance_metrics.family_history_summary.total_records}
              </Typography>
              <Typography variant="body2" gutterBottom sx={{ mt: 2 }}>
                <strong>Common Conditions:</strong>
              </Typography>
              {data.performance_metrics.family_history_summary.common_conditions.map((condition, index) => (
                <Box key={index} sx={{ mb: 1 }}>
                  <Chip
                    label={`${condition.condition} (${condition.count})`}
                    size="small"
                    color="secondary"
                  />
                </Box>
              ))}
            </Box>
          </Grid>
        </Grid>
      </Paper>
    </Container>
  )
}

export default AnalyticsDashboard
