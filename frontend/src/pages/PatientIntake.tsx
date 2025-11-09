import React, { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import {
  Box,
  Container,
  Typography,
  Paper,
  Button,
  Grid,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  IconButton,
  Card,
  CardContent,
  Divider,
  Stack,
  Autocomplete,
  FormControlLabel,
  Checkbox,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  CircularProgress,
  Alert,
  Snackbar,
  Tooltip,
} from '@mui/material'
import {
  Add as AddIcon,
  Delete as DeleteIcon,
  Person,
  Flight,
  FamilyRestroom,
  CalendarToday,
  Save,
  Clear,
  ArrowBack,
  Edit as EditIcon,
  Assessment as AssessmentIcon,
  Description as ReportIcon,
} from '@mui/icons-material'
import { savePatientIntake, getPatientIntake, updatePatientIntake, generatePatientIntakeReport, downloadPDF } from '../services/api'
import RiskAssessment from '../components/RiskAssessment'
import MedicalTimeline from '../components/MedicalTimeline'

interface TravelHistory {
  id: string
  destination: string
  departureDate: string
  returnDate: string
  duration: string
  purpose: string
  activities: string[]
}

interface FamilyHistory {
  id: string
  relationship: string
  condition: string
  ageOfOnset: string
  duration: string
  status: 'ongoing' | 'resolved' | 'deceased'
  notes: string
}

interface PatientDetails {
  name: string
  age: string
  gender: string
  bloodType: string
  travelHistory: TravelHistory[]
  familyHistory: FamilyHistory[]
}

const PatientIntake: React.FC = () => {
  const { intakeId } = useParams<{ intakeId: string }>()
  const navigate = useNavigate()
  const isViewMode = window.location.pathname.includes('/view/')
  const isEditMode = window.location.pathname.includes('/edit/') || !!intakeId
  const isCreateMode = !intakeId
  
  const [loading, setLoading] = useState(false)
  const [patientDetails, setPatientDetails] = useState<PatientDetails>({
    name: '',
    age: '',
    gender: '',
    bloodType: '',
    travelHistory: [],
    familyHistory: [],
  })

  const [showTravelDialog, setShowTravelDialog] = useState(false)
  const [showFamilyDialog, setShowFamilyDialog] = useState(false)
  const [currentTravel, setCurrentTravel] = useState<Partial<TravelHistory>>({})
  const [currentFamily, setCurrentFamily] = useState<Partial<FamilyHistory>>({})
  const [saving, setSaving] = useState(false)
  const [generatingReport, setGeneratingReport] = useState(false)
  const [snackbar, setSnackbar] = useState<{ open: boolean; message: string; severity: 'success' | 'error' }>({
    open: false,
    message: '',
    severity: 'success',
  })

  const handleGenerateReport = async () => {
    if (!intakeId) return
    setGeneratingReport(true)
    try {
      const blob = await generatePatientIntakeReport(intakeId)
      downloadPDF(blob, `patient_intake_${patientDetails.name.replace(/\s+/g, '_')}.pdf`)
      setSnackbar({ open: true, message: 'Report generated successfully!', severity: 'success' })
    } catch (error) {
      console.error('Error generating report:', error)
      setSnackbar({ open: true, message: 'Failed to generate report', severity: 'error' })
    } finally {
      setGeneratingReport(false)
    }
  }

  // Load patient data if in edit/view mode
  useEffect(() => {
    if (intakeId) {
      loadPatientData(intakeId)
    }
  }, [intakeId])

  const loadPatientData = async (id: string) => {
    setLoading(true)
    try {
      const data = await getPatientIntake(id)
      setPatientDetails({
        name: data.name,
        age: data.age,
        gender: data.gender,
        bloodType: data.bloodType,
        travelHistory: data.travelHistory,
        familyHistory: data.familyHistory as FamilyHistory[],
      })
    } catch (error) {
      console.error('Failed to load patient data:', error)
      setSnackbar({
        open: true,
        message: 'Failed to load patient data',
        severity: 'error',
      })
    } finally {
      setLoading(false)
    }
  }

  // Quick selection options
  const commonDestinations = [
    'Asia - China',
    'Asia - India',
    'Asia - Thailand',
    'Asia - Philippines',
    'Europe - Italy',
    'Europe - Spain',
    'Europe - France',
    'Europe - UK',
    'Africa - Kenya',
    'Africa - South Africa',
    'Africa - Egypt',
    'South America - Brazil',
    'South America - Argentina',
    'Middle East - UAE',
    'Middle East - Saudi Arabia',
  ]

  const travelPurposes = ['Tourism', 'Business', 'Medical', 'Education', 'Family Visit', 'Other']

  const travelActivities = [
    'Hiking/Trekking',
    'Swimming',
    'Wildlife Safari',
    'Urban Tourism',
    'Beach Activities',
    'Water Sports',
    'Camping',
    'Cave Exploration',
    'Street Food',
    'Hospital/Clinic Visit',
    'Rural Areas',
    'Crowded Events',
  ]

  const familyRelationships = [
    'Father',
    'Mother',
    'Brother',
    'Sister',
    'Son',
    'Daughter',
    'Paternal Grandfather',
    'Paternal Grandmother',
    'Maternal Grandfather',
    'Maternal Grandmother',
    'Uncle (Paternal)',
    'Uncle (Maternal)',
    'Aunt (Paternal)',
    'Aunt (Maternal)',
    'Cousin',
  ]

  const commonConditions = [
    'Diabetes Type 2',
    'Hypertension',
    'Heart Disease',
    'Stroke',
    'Cancer - Breast',
    'Cancer - Lung',
    'Cancer - Colon',
    'Cancer - Prostate',
    'Asthma',
    'COPD',
    'Kidney Disease',
    'Liver Disease',
    'Alzheimer\'s Disease',
    'Depression',
    'Anxiety Disorder',
    'Thyroid Disease',
    'Arthritis',
    'Osteoporosis',
    'Epilepsy',
    'Multiple Sclerosis',
  ]

  const calculateDuration = (startDate: string, endDate: string): string => {
    if (!startDate || !endDate) return ''
    const start = new Date(startDate)
    const end = new Date(endDate)
    const diffTime = Math.abs(end.getTime() - start.getTime())
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24))
    
    if (diffDays === 0) return '1 day'
    if (diffDays === 1) return '1 day'
    if (diffDays < 7) return `${diffDays} days`
    if (diffDays < 30) return `${Math.floor(diffDays / 7)} weeks`
    if (diffDays < 365) return `${Math.floor(diffDays / 30)} months`
    return `${Math.floor(diffDays / 365)} years`
  }

  const handleAddTravel = () => {
    if (!currentTravel.destination || !currentTravel.departureDate || !currentTravel.returnDate) {
      return
    }

    const duration = calculateDuration(currentTravel.departureDate!, currentTravel.returnDate!)
    const newTravel: TravelHistory = {
      id: Date.now().toString(),
      destination: currentTravel.destination!,
      departureDate: currentTravel.departureDate!,
      returnDate: currentTravel.returnDate!,
      duration,
      purpose: currentTravel.purpose || 'Not specified',
      activities: currentTravel.activities || [],
    }

    setPatientDetails({
      ...patientDetails,
      travelHistory: [...patientDetails.travelHistory, newTravel],
    })

    setCurrentTravel({})
    setShowTravelDialog(false)
  }

  const handleAddFamily = () => {
    if (!currentFamily.relationship || !currentFamily.condition) {
      return
    }

    const newFamily: FamilyHistory = {
      id: Date.now().toString(),
      relationship: currentFamily.relationship!,
      condition: currentFamily.condition!,
      ageOfOnset: currentFamily.ageOfOnset || 'Unknown',
      duration: currentFamily.duration || 'Unknown',
      status: currentFamily.status || 'ongoing',
      notes: currentFamily.notes || '',
    }

    setPatientDetails({
      ...patientDetails,
      familyHistory: [...patientDetails.familyHistory, newFamily],
    })

    setCurrentFamily({})
    setShowFamilyDialog(false)
  }

  const handleDeleteTravel = (id: string) => {
    setPatientDetails({
      ...patientDetails,
      travelHistory: patientDetails.travelHistory.filter((t) => t.id !== id),
    })
  }

  const handleDeleteFamily = (id: string) => {
    setPatientDetails({
      ...patientDetails,
      familyHistory: patientDetails.familyHistory.filter((f) => f.id !== id),
    })
  }

  const handleSave = async () => {
    // Validation
    if (!patientDetails.name || !patientDetails.age || !patientDetails.gender) {
      setSnackbar({
        open: true,
        message: 'Please fill in all required fields (Name, Age, Gender)',
        severity: 'error',
      })
      return
    }

    setSaving(true)
    try {
      if (intakeId) {
        // Update existing patient
        await updatePatientIntake(intakeId, patientDetails)
        console.log('Patient intake updated:', intakeId)
        setSnackbar({
          open: true,
          message: `Patient ${intakeId} updated successfully!`,
          severity: 'success',
        })
      } else {
        // Create new patient
        const response = await savePatientIntake(patientDetails)
        console.log('Patient intake created:', response)
        setSnackbar({
          open: true,
          message: `Patient intake saved successfully! ID: ${response.intake_id}`,
          severity: 'success',
        })
      }
      
      // Navigate back to patient list after 2 seconds
      setTimeout(() => {
        navigate('/patients')
      }, 2000)
    } catch (error) {
      console.error('Error saving patient intake:', error)
      setSnackbar({
        open: true,
        message: `Failed to ${intakeId ? 'update' : 'save'} patient intake. Please try again.`,
        severity: 'error',
      })
    } finally {
      setSaving(false)
    }
  }

  const handleCloseSnackbar = () => {
    setSnackbar({ ...snackbar, open: false })
  }

  const handleClear = () => {
    setPatientDetails({
      name: '',
      age: '',
      gender: '',
      bloodType: '',
      travelHistory: [],
      familyHistory: [],
    })
  }

  return (
    <Container maxWidth="xl" sx={{ py: 4 }}>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
          <Tooltip title="Back to Patient List">
            <IconButton 
              onClick={() => navigate('/patients')}
              sx={{
                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                color: 'white',
                '&:hover': {
                  background: 'linear-gradient(135deg, #764ba2 0%, #667eea 100%)',
                },
              }}
            >
              <ArrowBack />
            </IconButton>
          </Tooltip>
          <Typography
            variant="h3"
            sx={{
              fontWeight: 700,
              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              backgroundClip: 'text',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
            }}
          >
            👤 {intakeId ? (isViewMode ? 'View Patient' : 'Edit Patient') : 'Patient Intake Form'}
          </Typography>
        </Box>
        <Typography variant="body1" color="text.secondary" sx={{ maxWidth: 800 }}>
          Complete patient information including basic details, travel history, and family medical history
        </Typography>
      </Box>
      
      {/* Loading Spinner */}
      {loading && (
        <Box sx={{ display: 'flex', justifyContent: 'center', my: 4 }}>
          <CircularProgress />
        </Box>
      )}

      {/* Basic Information */}
      <Paper sx={{ p: 4, mb: 3 }}>
        <Typography variant="h5" gutterBottom sx={{ mb: 3, display: 'flex', alignItems: 'center', gap: 1 }}>
          <Person color="primary" />
          Basic Information
        </Typography>
        <Grid container spacing={3}>
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="Full Name"
              value={patientDetails.name}
              onChange={(e) => setPatientDetails({ ...patientDetails, name: e.target.value })}
              required
              disabled={isViewMode}
            />
          </Grid>
          <Grid item xs={12} md={3}>
            <TextField
              fullWidth
              label="Age"
              type="number"
              value={patientDetails.age}
              onChange={(e) => setPatientDetails({ ...patientDetails, age: e.target.value })}
              required
              disabled={isViewMode}
            />
          </Grid>
          <Grid item xs={12} md={3}>
            <FormControl fullWidth>
              <InputLabel>Gender</InputLabel>
              <Select
                value={patientDetails.gender}
                label="Gender"
                onChange={(e) => setPatientDetails({ ...patientDetails, gender: e.target.value })}
                disabled={isViewMode}
              >
                <MenuItem value="male">Male</MenuItem>
                <MenuItem value="female">Female</MenuItem>
                <MenuItem value="other">Other</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} md={3}>
            <FormControl fullWidth>
              <InputLabel>Blood Type</InputLabel>
              <Select
                value={patientDetails.bloodType}
                label="Blood Type"
                onChange={(e) => setPatientDetails({ ...patientDetails, bloodType: e.target.value })}
                disabled={isViewMode}
              >
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
        </Grid>
      </Paper>

      {/* Travel History */}
      <Paper sx={{ p: 4, mb: 3 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Typography variant="h5" sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Flight color="secondary" />
            Travel History (Last 2 Years)
          </Typography>
          {!isViewMode && (
            <Button
              variant="contained"
              startIcon={<AddIcon />}
              onClick={() => setShowTravelDialog(true)}
            >
              Add Travel
            </Button>
          )}
        </Box>

        {patientDetails.travelHistory.length === 0 ? (
          <Typography color="text.secondary" sx={{ textAlign: 'center', py: 4 }}>
            No travel history recorded. Click "Add Travel" to add travel details.
          </Typography>
        ) : (
          <Grid container spacing={2}>
            {patientDetails.travelHistory.map((travel) => (
              <Grid item xs={12} key={travel.id}>
                <Card variant="outlined">
                  <CardContent>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                      <Box sx={{ flex: 1 }}>
                        <Typography variant="h6" gutterBottom>
                          {travel.destination}
                        </Typography>
                        <Stack direction="row" spacing={1} sx={{ mb: 1, flexWrap: 'wrap', gap: 1 }}>
                          <Chip
                            icon={<CalendarToday />}
                            label={`${travel.departureDate} to ${travel.returnDate}`}
                            size="small"
                            color="primary"
                            variant="outlined"
                          />
                          <Chip label={`Duration: ${travel.duration}`} size="small" color="secondary" />
                          <Chip label={travel.purpose} size="small" />
                        </Stack>
                        {travel.activities.length > 0 && (
                          <Box sx={{ mt: 1 }}>
                            <Typography variant="caption" color="text.secondary">
                              Activities:
                            </Typography>
                            <Stack direction="row" spacing={0.5} sx={{ mt: 0.5, flexWrap: 'wrap', gap: 0.5 }}>
                              {travel.activities.map((activity, idx) => (
                                <Chip key={idx} label={activity} size="small" variant="outlined" />
                              ))}
                            </Stack>
                          </Box>
                        )}
                      </Box>
                      {!isViewMode && (
                        <IconButton color="error" onClick={() => handleDeleteTravel(travel.id)}>
                          <DeleteIcon />
                        </IconButton>
                      )}
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        )}
      </Paper>

      {/* Family History */}
      <Paper sx={{ p: 4, mb: 3 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Typography variant="h5" sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <FamilyRestroom color="success" />
            Family Medical History
          </Typography>
          {!isViewMode && (
            <Button
              variant="contained"
              color="success"
              startIcon={<AddIcon />}
              onClick={() => setShowFamilyDialog(true)}
            >
              Add Family History
            </Button>
          )}
        </Box>

        {patientDetails.familyHistory.length === 0 ? (
          <Typography color="text.secondary" sx={{ textAlign: 'center', py: 4 }}>
            No family history recorded. Click "Add Family History" to add medical conditions.
          </Typography>
        ) : (
          <Grid container spacing={2}>
            {patientDetails.familyHistory.map((family) => (
              <Grid item xs={12} md={6} key={family.id}>
                <Card variant="outlined">
                  <CardContent>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                      <Box sx={{ flex: 1 }}>
                        <Typography variant="h6" gutterBottom>
                          {family.relationship}
                        </Typography>
                        <Typography variant="body1" color="text.primary" gutterBottom>
                          {family.condition}
                        </Typography>
                        <Stack direction="row" spacing={1} sx={{ mb: 1, flexWrap: 'wrap', gap: 1 }}>
                          <Chip
                            label={`Age of Onset: ${family.ageOfOnset}`}
                            size="small"
                            variant="outlined"
                          />
                          <Chip label={`Duration: ${family.duration}`} size="small" variant="outlined" />
                          <Chip
                            label={family.status}
                            size="small"
                            color={
                              family.status === 'ongoing'
                                ? 'warning'
                                : family.status === 'resolved'
                                ? 'success'
                                : 'default'
                            }
                          />
                        </Stack>
                        {family.notes && (
                          <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                            Notes: {family.notes}
                          </Typography>
                        )}
                      </Box>
                      {!isViewMode && (
                        <IconButton color="error" onClick={() => handleDeleteFamily(family.id)}>
                          <DeleteIcon />
                        </IconButton>
                      )}
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            ))}
          </Grid>
        )}
      </Paper>

      {/* Risk Assessment */}
      {(patientDetails.name || patientDetails.age) && (
        <Box sx={{ mb: 3 }}>
          <RiskAssessment
            patientData={{
              age: patientDetails.age,
              travelHistory: patientDetails.travelHistory,
              familyHistory: patientDetails.familyHistory,
            }}
            showDetails={true}
          />
        </Box>
      )}

      {/* Medical History Timeline (View Mode Only) */}
      {isViewMode && intakeId && (
        <Box sx={{ mb: 3 }}>
          <MedicalTimeline patientIntakeId={intakeId} />
        </Box>
      )}

      {/* Action Buttons */}
      <Box sx={{ display: 'flex', justifyContent: 'flex-end', gap: 2 }}>
        {isViewMode ? (
          <>
            <Button
              variant="outlined"
              startIcon={<ReportIcon />}
              onClick={handleGenerateReport}
              size="large"
              sx={{ color: '#10b981', borderColor: '#10b981' }}
              disabled={generatingReport}
            >
              {generatingReport ? 'Generating...' : 'Download Report'}
            </Button>
            <Button
              variant="outlined"
              startIcon={<AssessmentIcon />}
              onClick={() => window.open(`/diagnosis?patientId=${intakeId}`, '_blank')}
              size="large"
              sx={{ color: '#667eea', borderColor: '#667eea' }}
            >
              Start Diagnosis
            </Button>
            <Button
              variant="contained"
              startIcon={<EditIcon />}
              onClick={() => navigate(`/patient-intake/edit/${intakeId}`)}
              size="large"
            >
              Edit Patient
            </Button>
          </>
        ) : (
          <>
            <Button variant="outlined" startIcon={<Clear />} onClick={handleClear} size="large" disabled={saving}>
              Clear All
            </Button>
            <Button
              variant="contained"
              startIcon={saving ? <CircularProgress size={20} color="inherit" /> : <Save />}
              onClick={handleSave}
              size="large"
              disabled={saving}
            >
              {saving ? 'Saving...' : intakeId ? 'Update Patient Details' : 'Save Patient Details'}
            </Button>
          </>
        )}
      </Box>

      {/* Travel Dialog */}
      <Dialog open={showTravelDialog} onClose={() => setShowTravelDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>Add Travel History</DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 2 }}>
            <Grid container spacing={3}>
              <Grid item xs={12}>
                <Autocomplete
                  freeSolo
                  options={commonDestinations}
                  value={currentTravel.destination || ''}
                  onChange={(_, newValue) =>
                    setCurrentTravel({ ...currentTravel, destination: newValue || '' })
                  }
                  renderInput={(params) => (
                    <TextField {...params} label="Destination" required fullWidth />
                  )}
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  label="Departure Date"
                  type="date"
                  InputLabelProps={{ shrink: true }}
                  value={currentTravel.departureDate || ''}
                  onChange={(e) => setCurrentTravel({ ...currentTravel, departureDate: e.target.value })}
                  required
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  label="Return Date"
                  type="date"
                  InputLabelProps={{ shrink: true }}
                  value={currentTravel.returnDate || ''}
                  onChange={(e) => setCurrentTravel({ ...currentTravel, returnDate: e.target.value })}
                  required
                />
              </Grid>
              {currentTravel.departureDate && currentTravel.returnDate && (
                <Grid item xs={12}>
                  <Chip
                    label={`Duration: ${calculateDuration(
                      currentTravel.departureDate,
                      currentTravel.returnDate
                    )}`}
                    color="secondary"
                  />
                </Grid>
              )}
              <Grid item xs={12}>
                <FormControl fullWidth>
                  <InputLabel>Purpose</InputLabel>
                  <Select
                    value={currentTravel.purpose || ''}
                    label="Purpose"
                    onChange={(e) => setCurrentTravel({ ...currentTravel, purpose: e.target.value })}
                  >
                    {travelPurposes.map((purpose) => (
                      <MenuItem key={purpose} value={purpose}>
                        {purpose}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12}>
                <Autocomplete
                  multiple
                  options={travelActivities}
                  value={currentTravel.activities || []}
                  onChange={(_, newValue) => setCurrentTravel({ ...currentTravel, activities: newValue })}
                  renderInput={(params) => (
                    <TextField {...params} label="Activities During Travel" placeholder="Select activities" />
                  )}
                />
              </Grid>
            </Grid>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowTravelDialog(false)}>Cancel</Button>
          <Button onClick={handleAddTravel} variant="contained">
            Add Travel
          </Button>
        </DialogActions>
      </Dialog>

      {/* Family History Dialog */}
      <Dialog open={showFamilyDialog} onClose={() => setShowFamilyDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>Add Family Medical History</DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 2 }}>
            <Grid container spacing={3}>
              <Grid item xs={12} md={6}>
                <Autocomplete
                  freeSolo
                  options={familyRelationships}
                  value={currentFamily.relationship || ''}
                  onChange={(_, newValue) =>
                    setCurrentFamily({ ...currentFamily, relationship: newValue || '' })
                  }
                  renderInput={(params) => (
                    <TextField {...params} label="Relationship" required fullWidth />
                  )}
                />
              </Grid>
              <Grid item xs={12} md={6}>
                <Autocomplete
                  freeSolo
                  options={commonConditions}
                  value={currentFamily.condition || ''}
                  onChange={(_, newValue) => setCurrentFamily({ ...currentFamily, condition: newValue || '' })}
                  renderInput={(params) => <TextField {...params} label="Condition" required fullWidth />}
                />
              </Grid>
              <Grid item xs={12} md={4}>
                <TextField
                  fullWidth
                  label="Age of Onset"
                  placeholder="e.g., 45 years"
                  value={currentFamily.ageOfOnset || ''}
                  onChange={(e) => setCurrentFamily({ ...currentFamily, ageOfOnset: e.target.value })}
                />
              </Grid>
              <Grid item xs={12} md={4}>
                <TextField
                  fullWidth
                  label="Duration"
                  placeholder="e.g., 10 years"
                  value={currentFamily.duration || ''}
                  onChange={(e) => setCurrentFamily({ ...currentFamily, duration: e.target.value })}
                />
              </Grid>
              <Grid item xs={12} md={4}>
                <FormControl fullWidth>
                  <InputLabel>Status</InputLabel>
                  <Select
                    value={currentFamily.status || 'ongoing'}
                    label="Status"
                    onChange={(e) =>
                      setCurrentFamily({
                        ...currentFamily,
                        status: e.target.value as 'ongoing' | 'resolved' | 'deceased',
                      })
                    }
                  >
                    <MenuItem value="ongoing">Ongoing</MenuItem>
                    <MenuItem value="resolved">Resolved</MenuItem>
                    <MenuItem value="deceased">Deceased</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Additional Notes"
                  multiline
                  rows={3}
                  value={currentFamily.notes || ''}
                  onChange={(e) => setCurrentFamily({ ...currentFamily, notes: e.target.value })}
                />
              </Grid>
            </Grid>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowFamilyDialog(false)}>Cancel</Button>
          <Button onClick={handleAddFamily} variant="contained" color="success">
            Add Family History
          </Button>
        </DialogActions>
      </Dialog>

      {/* Snackbar for notifications */}
      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={handleCloseSnackbar}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      >
        <Alert onClose={handleCloseSnackbar} severity={snackbar.severity} sx={{ width: '100%' }}>
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Container>
  )
}

export default PatientIntake
