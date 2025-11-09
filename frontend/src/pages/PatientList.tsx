import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Box,
  Paper,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  TextField,
  IconButton,
  Chip,
  Button,
  InputAdornment,
  Tooltip,
  CircularProgress,
  Alert,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Card,
  CardContent,
  Grid,
} from '@mui/material'
import {
  Search as SearchIcon,
  Edit as EditIcon,
  Visibility as ViewIcon,
  Add as AddIcon,
  FilterList as FilterIcon,
  Download as DownloadIcon,
  Assessment as AssessmentIcon,
  Warning as WarningIcon,
  CheckCircle as CheckCircleIcon,
  Description as ReportIcon,
} from '@mui/icons-material'
import axios from 'axios'
import { assessRisk } from '../utils/riskAssessment'
import { RiskBadge } from '../components/RiskAssessment'
import { generatePatientIntakeReport, downloadPDF } from '../services/api'

interface PatientIntake {
  intake_id: string
  name: string
  age: string
  gender: string
  blood_type: string
  created_at: string
  updated_at: string
  travel_history_count?: number
  family_history_count?: number
  risk_level?: 'low' | 'medium' | 'high' | 'critical'
}

interface PatientStats {
  total_patients: number
  today_patients: number
  high_risk: number
  pending_review: number
}

export default function PatientList() {
  const navigate = useNavigate()
  
  const [patients, setPatients] = useState<PatientIntake[]>([])
  const [filteredPatients, setFilteredPatients] = useState<PatientIntake[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  
  // Pagination
  const [page, setPage] = useState(0)
  const [rowsPerPage, setRowsPerPage] = useState(10)
  
  // Filters
  const [searchTerm, setSearchTerm] = useState('')
  const [genderFilter, setGenderFilter] = useState<string>('all')
  const [bloodTypeFilter, setBloodTypeFilter] = useState<string>('all')
  const [riskFilter, setRiskFilter] = useState<string>('all')
  
  // Stats
  const [stats, setStats] = useState<PatientStats>({
    total_patients: 0,
    today_patients: 0,
    high_risk: 0,
    pending_review: 0,
  })

  useEffect(() => {
    fetchPatients()
  }, [])

  useEffect(() => {
    applyFilters()
  }, [patients, searchTerm, genderFilter, bloodTypeFilter, riskFilter])

  const fetchPatients = async () => {
    setLoading(true)
    setError(null)
    try {
      const response = await axios.get('http://localhost:8001/api/medical/patient-intake')
      const patientsData = response.data.patients || []
      
      // Calculate risk levels (basic algorithm)
      const patientsWithRisk = patientsData.map((p: any) => ({
        ...p,
        travel_history_count: p.travel_history?.length || 0,
        family_history_count: p.family_history?.length || 0,
        risk_level: calculateRiskLevel(p),
      }))
      
      setPatients(patientsWithRisk)
      calculateStats(patientsWithRisk)
    } catch (err: any) {
      console.error('Failed to fetch patients:', err)
      setError(err.response?.data?.detail || 'Failed to load patients')
    } finally {
      setLoading(false)
    }
  }

  const calculateRiskLevel = (patient: any): 'low' | 'medium' | 'high' | 'critical' => {
    const riskAssessment = assessRisk({
      age: patient.age,
      travelHistory: patient.travel_history || [],
      familyHistory: patient.family_history || [],
    })
    return riskAssessment.level
  }

  const calculateStats = (patientsData: PatientIntake[]) => {
    const today = new Date().toISOString().split('T')[0]
    
    setStats({
      total_patients: patientsData.length,
      today_patients: patientsData.filter(p => 
        p.created_at.startsWith(today)
      ).length,
      high_risk: patientsData.filter(p => p.risk_level === 'high' || p.risk_level === 'critical').length,
      pending_review: patientsData.filter(p => {
        const createdDate = new Date(p.created_at)
        const hoursSinceCreation = (Date.now() - createdDate.getTime()) / (1000 * 60 * 60)
        return hoursSinceCreation < 24
      }).length,
    })
  }

  const applyFilters = () => {
    let filtered = [...patients]
    
    // Search filter
    if (searchTerm) {
      filtered = filtered.filter(p =>
        p.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        p.intake_id.toLowerCase().includes(searchTerm.toLowerCase())
      )
    }
    
    // Gender filter
    if (genderFilter !== 'all') {
      filtered = filtered.filter(p => p.gender === genderFilter)
    }
    
    // Blood type filter
    if (bloodTypeFilter !== 'all') {
      filtered = filtered.filter(p => p.blood_type === bloodTypeFilter)
    }
    
    // Risk filter
    if (riskFilter !== 'all') {
      filtered = filtered.filter(p => p.risk_level === riskFilter)
    }
    
    setFilteredPatients(filtered)
    setPage(0) // Reset to first page when filters change
  }

  const handleChangePage = (_event: unknown, newPage: number) => {
    setPage(newPage)
  }

  const handleChangeRowsPerPage = (event: React.ChangeEvent<HTMLInputElement>) => {
    setRowsPerPage(parseInt(event.target.value, 10))
    setPage(0)
  }

  const handleViewPatient = (intakeId: string) => {
    navigate(`/patient-intake/view/${intakeId}`)
  }

  const handleEditPatient = (intakeId: string) => {
    navigate(`/patient-intake/edit/${intakeId}`)
  }

  const handleNewPatient = () => {
    navigate('/patient-intake')
  }

  const handleStartDiagnosis = (intakeId: string) => {
    // Open diagnosis page in new tab with patient ID in URL (to be loaded via patient selector)
    window.open(`/diagnosis?patientId=${intakeId}`, '_blank')
  }

  const handleGenerateReport = async (intakeId: string, patientName: string) => {
    try {
      const blob = await generatePatientIntakeReport(intakeId)
      downloadPDF(blob, `patient_report_${patientName.replace(/\s+/g, '_')}.pdf`)
    } catch (error) {
      console.error('Error generating report:', error)
      alert('Failed to generate report. Please try again.')
    }
  }

  // Using RiskBadge component from ../components/RiskAssessment

  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    })
  }

  const exportToCSV = () => {
    const headers = ['Intake ID', 'Name', 'Age', 'Gender', 'Blood Type', 'Travel History', 'Family History', 'Risk Level', 'Created At']
    const rows = filteredPatients.map(p => [
      p.intake_id,
      p.name,
      p.age,
      p.gender,
      p.blood_type,
      p.travel_history_count || 0,
      p.family_history_count || 0,
      p.risk_level || 'unknown',
      formatDate(p.created_at),
    ])
    
    const csvContent = [
      headers.join(','),
      ...rows.map(row => row.map(cell => `"${cell}"`).join(',')),
    ].join('\n')
    
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
    const link = document.createElement('a')
    const url = URL.createObjectURL(blob)
    link.setAttribute('href', url)
    link.setAttribute('download', `patients_${new Date().toISOString().split('T')[0]}.csv`)
    link.style.visibility = 'hidden'
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  }

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '80vh' }}>
        <CircularProgress size={60} />
      </Box>
    )
  }

  return (
    <Box>
      {/* Header */}
      <Box sx={{ mb: 3, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Box>
          <Typography variant="h4" fontWeight={700} gutterBottom>
            Patient Management
          </Typography>
          <Typography variant="body1" color="text.secondary">
            View, search, and manage all patient intake records
          </Typography>
        </Box>
        <Button
          variant="contained"
          size="large"
          startIcon={<AddIcon />}
          onClick={handleNewPatient}
          sx={{
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            boxShadow: '0 4px 12px rgba(102, 126, 234, 0.4)',
            '&:hover': {
              background: 'linear-gradient(135deg, #5568d3 0%, #6a3f8f 100%)',
              transform: 'translateY(-2px)',
              boxShadow: '0 6px 16px rgba(102, 126, 234, 0.5)',
            },
            transition: 'all 0.3s',
          }}
        >
          New Patient Intake
        </Button>
      </Box>

      {/* Stats Cards */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', color: 'white' }}>
            <CardContent>
              <Typography variant="h3" fontWeight={700}>{stats.total_patients}</Typography>
              <Typography variant="body2" sx={{ opacity: 0.9 }}>Total Patients</Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ background: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)', color: 'white' }}>
            <CardContent>
              <Typography variant="h3" fontWeight={700}>{stats.today_patients}</Typography>
              <Typography variant="body2" sx={{ opacity: 0.9 }}>Today's Admissions</Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ background: 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)', color: 'white' }}>
            <CardContent>
              <Typography variant="h3" fontWeight={700}>{stats.high_risk}</Typography>
              <Typography variant="body2" sx={{ opacity: 0.9 }}>High Risk Patients</Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ background: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)', color: 'white' }}>
            <CardContent>
              <Typography variant="h3" fontWeight={700}>{stats.pending_review}</Typography>
              <Typography variant="body2" sx={{ opacity: 0.9 }}>Pending Review (24h)</Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {/* Filters */}
      <Paper sx={{ p: 3, mb: 3 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
          <FilterIcon color="primary" />
          <Typography variant="h6" fontWeight={600}>Filters & Search</Typography>
        </Box>
        
        <Grid container spacing={2}>
          <Grid item xs={12} md={4}>
            <TextField
              fullWidth
              placeholder="Search by name or ID..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              InputProps={{
                startAdornment: (
                  <InputAdornment position="start">
                    <SearchIcon />
                  </InputAdornment>
                ),
              }}
            />
          </Grid>
          
          <Grid item xs={12} md={2}>
            <FormControl fullWidth>
              <InputLabel>Gender</InputLabel>
              <Select
                value={genderFilter}
                label="Gender"
                onChange={(e) => setGenderFilter(e.target.value)}
              >
                <MenuItem value="all">All Genders</MenuItem>
                <MenuItem value="Male">Male</MenuItem>
                <MenuItem value="Female">Female</MenuItem>
                <MenuItem value="Other">Other</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          
          <Grid item xs={12} md={2}>
            <FormControl fullWidth>
              <InputLabel>Blood Type</InputLabel>
              <Select
                value={bloodTypeFilter}
                label="Blood Type"
                onChange={(e) => setBloodTypeFilter(e.target.value)}
              >
                <MenuItem value="all">All Types</MenuItem>
                <MenuItem value="A+">A+</MenuItem>
                <MenuItem value="A-">A-</MenuItem>
                <MenuItem value="B+">B+</MenuItem>
                <MenuItem value="B-">B-</MenuItem>
                <MenuItem value="AB+">AB+</MenuItem>
                <MenuItem value="AB-">AB-</MenuItem>
                <MenuItem value="O+">O+</MenuItem>
                <MenuItem value="O-">O-</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          
          <Grid item xs={12} md={2}>
            <FormControl fullWidth>
              <InputLabel>Risk Level</InputLabel>
              <Select
                value={riskFilter}
                label="Risk Level"
                onChange={(e) => setRiskFilter(e.target.value)}
              >
                <MenuItem value="all">All Levels</MenuItem>
                <MenuItem value="low">✓ Low Risk</MenuItem>
                <MenuItem value="medium">⚠ Medium Risk</MenuItem>
                <MenuItem value="high">⚠ High Risk</MenuItem>
                <MenuItem value="critical">🚨 Critical</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          
          <Grid item xs={12} md={2}>
            <Button
              fullWidth
              variant="outlined"
              startIcon={<DownloadIcon />}
              onClick={exportToCSV}
              sx={{ height: '56px' }}
            >
              Export CSV
            </Button>
          </Grid>
        </Grid>
        
        <Box sx={{ mt: 2, display: 'flex', gap: 1, flexWrap: 'wrap' }}>
          <Chip label={`${filteredPatients.length} patients found`} color="primary" />
          {searchTerm && <Chip label={`Search: "${searchTerm}"`} onDelete={() => setSearchTerm('')} />}
          {genderFilter !== 'all' && <Chip label={`Gender: ${genderFilter}`} onDelete={() => setGenderFilter('all')} />}
          {bloodTypeFilter !== 'all' && <Chip label={`Blood: ${bloodTypeFilter}`} onDelete={() => setBloodTypeFilter('all')} />}
          {riskFilter !== 'all' && <Chip label={`Risk: ${riskFilter}`} onDelete={() => setRiskFilter('all')} />}
        </Box>
      </Paper>

      {/* Patient Table */}
      <Paper sx={{ width: '100%', overflow: 'hidden' }}>
        <TableContainer sx={{ maxHeight: 600 }}>
          <Table stickyHeader>
            <TableHead>
              <TableRow>
                <TableCell sx={{ fontWeight: 700, bgcolor: '#f5f7fa' }}>Intake ID</TableCell>
                <TableCell sx={{ fontWeight: 700, bgcolor: '#f5f7fa' }}>Patient Name</TableCell>
                <TableCell sx={{ fontWeight: 700, bgcolor: '#f5f7fa' }}>Age</TableCell>
                <TableCell sx={{ fontWeight: 700, bgcolor: '#f5f7fa' }}>Gender</TableCell>
                <TableCell sx={{ fontWeight: 700, bgcolor: '#f5f7fa' }}>Blood Type</TableCell>
                <TableCell sx={{ fontWeight: 700, bgcolor: '#f5f7fa' }}>History</TableCell>
                <TableCell sx={{ fontWeight: 700, bgcolor: '#f5f7fa' }}>Risk Level</TableCell>
                <TableCell sx={{ fontWeight: 700, bgcolor: '#f5f7fa' }}>Created</TableCell>
                <TableCell align="center" sx={{ fontWeight: 700, bgcolor: '#f5f7fa' }}>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {filteredPatients.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={9} align="center" sx={{ py: 4 }}>
                    <Typography variant="body1" color="text.secondary">
                      No patients found. Try adjusting your filters or add a new patient.
                    </Typography>
                  </TableCell>
                </TableRow>
              ) : (
                filteredPatients
                  .slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage)
                  .map((patient) => (
                    <TableRow key={patient.intake_id} hover>
                      <TableCell>
                        <Typography variant="body2" fontWeight={600} color="primary">
                          {patient.intake_id}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2" fontWeight={600}>
                          {patient.name}
                        </Typography>
                      </TableCell>
                      <TableCell>{patient.age}</TableCell>
                      <TableCell>{patient.gender}</TableCell>
                      <TableCell>
                        <Chip label={patient.blood_type} size="small" variant="outlined" />
                      </TableCell>
                      <TableCell>
                        <Box sx={{ display: 'flex', gap: 1 }}>
                          {patient.travel_history_count! > 0 && (
                            <Chip
                              label={`${patient.travel_history_count} Travel`}
                              size="small"
                              color="info"
                            />
                          )}
                          {patient.family_history_count! > 0 && (
                            <Chip
                              label={`${patient.family_history_count} Family`}
                              size="small"
                              color="secondary"
                            />
                          )}
                        </Box>
                      </TableCell>
                      <TableCell><RiskBadge level={patient.risk_level!} size="small" /></TableCell>
                      <TableCell>
                        <Typography variant="body2" color="text.secondary">
                          {formatDate(patient.created_at)}
                        </Typography>
                      </TableCell>
                      <TableCell align="center">
                        <Box sx={{ display: 'flex', justifyContent: 'center', gap: 1 }}>
                          <Tooltip title="View Details">
                            <IconButton
                              size="small"
                              color="primary"
                              onClick={() => handleViewPatient(patient.intake_id)}
                            >
                              <ViewIcon />
                            </IconButton>
                          </Tooltip>
                          <Tooltip title="Edit Patient">
                            <IconButton
                              size="small"
                              color="secondary"
                              onClick={() => handleEditPatient(patient.intake_id)}
                            >
                              <EditIcon />
                            </IconButton>
                          </Tooltip>
                          <Tooltip title="Start Diagnosis">
                            <IconButton
                              size="small"
                              sx={{ color: '#667eea' }}
                              onClick={() => handleStartDiagnosis(patient.intake_id)}
                            >
                              <AssessmentIcon />
                            </IconButton>
                          </Tooltip>
                          <Tooltip title="Generate Report">
                            <IconButton
                              size="small"
                              sx={{ color: '#10b981' }}
                              onClick={() => handleGenerateReport(patient.intake_id, patient.name)}
                            >
                              <ReportIcon />
                            </IconButton>
                          </Tooltip>
                        </Box>
                      </TableCell>
                    </TableRow>
                  ))
              )}
            </TableBody>
          </Table>
        </TableContainer>
        <TablePagination
          rowsPerPageOptions={[5, 10, 25, 50]}
          component="div"
          count={filteredPatients.length}
          rowsPerPage={rowsPerPage}
          page={page}
          onPageChange={handleChangePage}
          onRowsPerPageChange={handleChangeRowsPerPage}
        />
      </Paper>
    </Box>
  )
}
