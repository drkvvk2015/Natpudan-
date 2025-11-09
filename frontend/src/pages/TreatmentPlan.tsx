import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import {
  Box,
  Paper,
  Typography,
  Button,
  TextField,
  Grid,
  Card,
  CardContent,
  Chip,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Alert,
  Divider,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Tabs,
  Tab,
  Tooltip,
} from '@mui/material'
import {
  Add as AddIcon,
  Delete as DeleteIcon,
  Edit as EditIcon,
  LocalHospital as HospitalIcon,
  Medication as MedicationIcon,
  Event as EventIcon,
  Timeline as TimelineIcon,
  ArrowBack,
  Save,
  CheckCircle,
  Cancel,
} from '@mui/icons-material'
import {
  createTreatmentPlan,
  getTreatmentPlansByPatient,
  getTreatmentPlan,
  addMedication,
  updateMedication,
  addFollowUp,
  updateFollowUp,
  type MedicationData,
  type FollowUpData,
  type TreatmentPlanData,
} from '../services/api'

interface TabPanelProps {
  children?: React.ReactNode
  index: number
  value: number
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props
  return (
    <div role="tabpanel" hidden={value !== index} {...other}>
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  )
}

export default function TreatmentPlan() {
  const { patientId, planId } = useParams()
  const navigate = useNavigate()
  const [activeTab, setActiveTab] = useState(0)
  const [loading, setLoading] = useState(false)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<string | null>(null)

  // Treatment plan data
  const [diagnosis, setDiagnosis] = useState('')
  const [icdCode, setIcdCode] = useState('')
  const [treatmentGoals, setTreatmentGoals] = useState('')
  const [clinicalNotes, setClinicalNotes] = useState('')
  const [status, setStatus] = useState('active')

  // Medications
  const [medications, setMedications] = useState<MedicationData[]>([])
  const [showMedicationDialog, setShowMedicationDialog] = useState(false)
  const [currentMedication, setCurrentMedication] = useState<Partial<MedicationData>>({})

  // Follow-ups
  const [followUps, setFollowUps] = useState<FollowUpData[]>([])
  const [showFollowUpDialog, setShowFollowUpDialog] = useState(false)
  const [currentFollowUp, setCurrentFollowUp] = useState<Partial<FollowUpData>>({})

  // Existing plans (for viewing)
  const [existingPlans, setExistingPlans] = useState<any[]>([])
  const [selectedPlan, setSelectedPlan] = useState<any>(null)

  useEffect(() => {
    if (patientId && !planId) {
      loadExistingPlans()
    } else if (planId) {
      loadPlan(planId)
    }
  }, [patientId, planId])

  const loadExistingPlans = async () => {
    if (!patientId) return
    setLoading(true)
    try {
      const plans = await getTreatmentPlansByPatient(patientId)
      setExistingPlans(plans)
      if (plans.length > 0) {
        setSelectedPlan(plans[0])
      }
    } catch (err) {
      console.error('Error loading treatment plans:', err)
      setError('Failed to load treatment plans')
    } finally {
      setLoading(false)
    }
  }

  const loadPlan = async (id: string) => {
    setLoading(true)
    try {
      const plan = await getTreatmentPlan(id)
      setSelectedPlan(plan)
      setDiagnosis(plan.primary_diagnosis)
      setIcdCode(plan.icd_code || '')
      setTreatmentGoals(plan.treatment_goals || '')
      setClinicalNotes(plan.clinical_notes || '')
      setStatus(plan.status)
      setMedications(plan.medications || [])
      setFollowUps(plan.follow_ups || [])
    } catch (err) {
      console.error('Error loading treatment plan:', err)
      setError('Failed to load treatment plan')
    } finally {
      setLoading(false)
    }
  }

  const handleSaveTreatmentPlan = async () => {
    if (!patientId || !diagnosis) {
      setError('Patient ID and diagnosis are required')
      return
    }

    setSaving(true)
    setError(null)
    try {
      const planData: TreatmentPlanData = {
        patient_intake_id: patientId,
        primary_diagnosis: diagnosis,
        icd_code: icdCode,
        treatment_goals: treatmentGoals,
        clinical_notes: clinicalNotes,
        medications,
        follow_ups,
      }

      const newPlan = await createTreatmentPlan(planData)
      setSuccess('Treatment plan created successfully!')
      setTimeout(() => {
        navigate(`/treatment-plan/${patientId}/${newPlan.plan_id}`)
      }, 1500)
    } catch (err) {
      console.error('Error saving treatment plan:', err)
      setError('Failed to save treatment plan')
    } finally {
      setSaving(false)
    }
  }

  const handleAddMedication = () => {
    if (!currentMedication.medication_name || !currentMedication.dosage) {
      alert('Medication name and dosage are required')
      return
    }

    setMedications([...medications, currentMedication as MedicationData])
    setCurrentMedication({})
    setShowMedicationDialog(false)
  }

  const handleRemoveMedication = (index: number) => {
    setMedications(medications.filter((_, i) => i !== index))
  }

  const handleAddFollowUp = () => {
    if (!currentFollowUp.scheduled_date) {
      alert('Follow-up date is required')
      return
    }

    setFollowUps([...followUps, currentFollowUp as FollowUpData])
    setCurrentFollowUp({})
    setShowFollowUpDialog(false)
  }

  const handleRemoveFollowUp = (index: number) => {
    setFollowUps(followUps.filter((_, i) => i !== index))
  }

  return (
    <Box sx={{ maxWidth: 1400, mx: 'auto', p: 3 }}>
      {/* Header */}
      <Box display="flex" alignItems="center" justifyContent="space-between" mb={3}>
        <Box display="flex" alignItems="center" gap={2}>
          <IconButton onClick={() => navigate(-1)}>
            <ArrowBack />
          </IconButton>
          <HospitalIcon sx={{ fontSize: 32, color: '#667eea' }} />
          <Typography variant="h4" fontWeight={600}>
            Treatment Plan Management
          </Typography>
        </Box>
        {!planId && (
          <Button
            variant="contained"
            startIcon={<Save />}
            onClick={handleSaveTreatmentPlan}
            disabled={saving || !diagnosis}
            size="large"
          >
            {saving ? 'Saving...' : 'Save Treatment Plan'}
          </Button>
        )}
      </Box>

      {/* Alerts */}
      {error && (
        <Alert severity="error" onClose={() => setError(null)} sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}
      {success && (
        <Alert severity="success" onClose={() => setSuccess(null)} sx={{ mb: 2 }}>
          {success}
        </Alert>
      )}

      {/* Tabs */}
      <Paper elevation={2}>
        <Tabs value={activeTab} onChange={(_, v) => setActiveTab(v)} sx={{ borderBottom: 1, borderColor: 'divider' }}>
          <Tab label="Overview" />
          <Tab label="Medications" icon={<MedicationIcon />} iconPosition="start" />
          <Tab label="Follow-ups" icon={<EventIcon />} iconPosition="start" />
          <Tab label="Monitoring" icon={<TimelineIcon />} iconPosition="start" />
        </Tabs>

        {/* Overview Tab */}
        <TabPanel value={activeTab} index={0}>
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <Typography variant="h6" gutterBottom>
                Primary Diagnosis
              </Typography>
              <TextField
                fullWidth
                label="Diagnosis"
                value={diagnosis}
                onChange={(e) => setDiagnosis(e.target.value)}
                disabled={!!planId}
                required
              />
            </Grid>

            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="ICD Code"
                value={icdCode}
                onChange={(e) => setIcdCode(e.target.value)}
                disabled={!!planId}
              />
            </Grid>

            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel>Status</InputLabel>
                <Select value={status} onChange={(e) => setStatus(e.target.value)} label="Status">
                  <MenuItem value="active">Active</MenuItem>
                  <MenuItem value="completed">Completed</MenuItem>
                  <MenuItem value="discontinued">Discontinued</MenuItem>
                  <MenuItem value="on_hold">On Hold</MenuItem>
                </Select>
              </FormControl>
            </Grid>

            <Grid item xs={12}>
              <TextField
                fullWidth
                multiline
                rows={3}
                label="Treatment Goals"
                value={treatmentGoals}
                onChange={(e) => setTreatmentGoals(e.target.value)}
                placeholder="e.g., Reduce symptoms, prevent complications, improve quality of life"
              />
            </Grid>

            <Grid item xs={12}>
              <TextField
                fullWidth
                multiline
                rows={4}
                label="Clinical Notes"
                value={clinicalNotes}
                onChange={(e) => setClinicalNotes(e.target.value)}
                placeholder="Additional clinical observations and treatment rationale"
              />
            </Grid>
          </Grid>
        </TabPanel>

        {/* Medications Tab */}
        <TabPanel value={activeTab} index={1}>
          <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
            <Typography variant="h6">Medications ({medications.length})</Typography>
            <Button variant="contained" startIcon={<AddIcon />} onClick={() => setShowMedicationDialog(true)}>
              Add Medication
            </Button>
          </Box>

          {medications.length === 0 ? (
            <Alert severity="info">No medications added yet. Click "Add Medication" to prescribe.</Alert>
          ) : (
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Medication</TableCell>
                    <TableCell>Dosage</TableCell>
                    <TableCell>Route</TableCell>
                    <TableCell>Frequency</TableCell>
                    <TableCell>Duration</TableCell>
                    <TableCell>Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {medications.map((med, index) => (
                    <TableRow key={index}>
                      <TableCell>
                        <Typography fontWeight={600}>{med.medication_name}</Typography>
                        {med.generic_name && (
                          <Typography variant="caption" color="text.secondary">
                            {med.generic_name}
                          </Typography>
                        )}
                      </TableCell>
                      <TableCell>{med.dosage}</TableCell>
                      <TableCell>{med.route || 'oral'}</TableCell>
                      <TableCell>{med.frequency || 'once_daily'}</TableCell>
                      <TableCell>{med.duration_days ? `${med.duration_days} days` : 'Ongoing'}</TableCell>
                      <TableCell>
                        <IconButton size="small" color="error" onClick={() => handleRemoveMedication(index)}>
                          <DeleteIcon />
                        </IconButton>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          )}
        </TabPanel>

        {/* Follow-ups Tab */}
        <TabPanel value={activeTab} index={2}>
          <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
            <Typography variant="h6">Scheduled Follow-ups ({followUps.length})</Typography>
            <Button variant="contained" startIcon={<AddIcon />} onClick={() => setShowFollowUpDialog(true)}>
              Schedule Follow-up
            </Button>
          </Box>

          {followUps.length === 0 ? (
            <Alert severity="info">No follow-ups scheduled. Click "Schedule Follow-up" to add.</Alert>
          ) : (
            <Grid container spacing={2}>
              {followUps.map((followUp, index) => (
                <Grid item xs={12} md={6} key={index}>
                  <Card>
                    <CardContent>
                      <Box display="flex" justifyContent="space-between" alignItems="start">
                        <Box>
                          <Typography variant="h6">{followUp.appointment_type || 'Follow-up'}</Typography>
                          <Typography color="text.secondary">
                            {new Date(followUp.scheduled_date).toLocaleString()}
                          </Typography>
                          {followUp.location && <Chip label={followUp.location} size="small" sx={{ mt: 1 }} />}
                        </Box>
                        <IconButton size="small" color="error" onClick={() => handleRemoveFollowUp(index)}>
                          <DeleteIcon />
                        </IconButton>
                      </Box>
                    </CardContent>
                  </Card>
                </Grid>
              ))}
            </Grid>
          )}
        </TabPanel>

        {/* Monitoring Tab */}
        <TabPanel value={activeTab} index={3}>
          <Alert severity="info">
            Monitoring features will be available after creating the treatment plan.
          </Alert>
        </TabPanel>
      </Paper>

      {/* Medication Dialog */}
      <Dialog open={showMedicationDialog} onClose={() => setShowMedicationDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>Add Medication</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Medication Name"
                value={currentMedication.medication_name || ''}
                onChange={(e) => setCurrentMedication({ ...currentMedication, medication_name: e.target.value })}
                required
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Generic Name"
                value={currentMedication.generic_name || ''}
                onChange={(e) => setCurrentMedication({ ...currentMedication, generic_name: e.target.value })}
              />
            </Grid>
            <Grid item xs={12} md={4}>
              <TextField
                fullWidth
                label="Dosage"
                value={currentMedication.dosage || ''}
                onChange={(e) => setCurrentMedication({ ...currentMedication, dosage: e.target.value })}
                required
                placeholder="e.g., 500mg"
              />
            </Grid>
            <Grid item xs={12} md={4}>
              <FormControl fullWidth>
                <InputLabel>Route</InputLabel>
                <Select
                  value={currentMedication.route || 'oral'}
                  onChange={(e) => setCurrentMedication({ ...currentMedication, route: e.target.value })}
                  label="Route"
                >
                  <MenuItem value="oral">Oral</MenuItem>
                  <MenuItem value="intravenous">IV</MenuItem>
                  <MenuItem value="intramuscular">IM</MenuItem>
                  <MenuItem value="subcutaneous">SC</MenuItem>
                  <MenuItem value="topical">Topical</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={4}>
              <FormControl fullWidth>
                <InputLabel>Frequency</InputLabel>
                <Select
                  value={currentMedication.frequency || 'once_daily'}
                  onChange={(e) => setCurrentMedication({ ...currentMedication, frequency: e.target.value })}
                  label="Frequency"
                >
                  <MenuItem value="once_daily">Once Daily</MenuItem>
                  <MenuItem value="twice_daily">Twice Daily</MenuItem>
                  <MenuItem value="three_times_daily">Three Times Daily</MenuItem>
                  <MenuItem value="as_needed">As Needed</MenuItem>
                  <MenuItem value="before_meals">Before Meals</MenuItem>
                  <MenuItem value="after_meals">After Meals</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                multiline
                rows={2}
                label="Instructions"
                value={currentMedication.instructions || ''}
                onChange={(e) => setCurrentMedication({ ...currentMedication, instructions: e.target.value })}
                placeholder="Special instructions for taking this medication"
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowMedicationDialog(false)}>Cancel</Button>
          <Button variant="contained" onClick={handleAddMedication}>
            Add
          </Button>
        </DialogActions>
      </Dialog>

      {/* Follow-up Dialog */}
      <Dialog open={showFollowUpDialog} onClose={() => setShowFollowUpDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Schedule Follow-up</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                type="datetime-local"
                label="Scheduled Date"
                value={currentFollowUp.scheduled_date || ''}
                onChange={(e) => setCurrentFollowUp({ ...currentFollowUp, scheduled_date: e.target.value })}
                InputLabelProps={{ shrink: true }}
                required
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Appointment Type"
                value={currentFollowUp.appointment_type || ''}
                onChange={(e) => setCurrentFollowUp({ ...currentFollowUp, appointment_type: e.target.value })}
                placeholder="e.g., Routine Check-up, Lab Review"
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Location"
                value={currentFollowUp.location || ''}
                onChange={(e) => setCurrentFollowUp({ ...currentFollowUp, location: e.target.value })}
                placeholder="Clinic, Hospital, etc."
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowFollowUpDialog(false)}>Cancel</Button>
          <Button variant="contained" onClick={handleAddFollowUp}>
            Schedule
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  )
}
