import React, { useCallback, useEffect, useState } from 'react'
import {
  Alert,
  Accordion,
  AccordionDetails,
  AccordionSummary,
  Box,
  Button,
  FormControl,
  Grid,
  InputLabel,
  MenuItem,
  Paper,
  Select,
  Snackbar,
  Stack,
  TextField,
  Typography,
} from '@mui/material'
import {
  Air as LungsIcon,
  ExpandMore as ExpandMoreIcon,
  Favorite as HeartIcon,
  Psychology as NeuroIcon,
  Restaurant as AbdomenIcon,
  Search as SearchIcon,
  Visibility as VisibilityIcon,
} from '@mui/icons-material'

import PatientSelector from '../components/PatientSelector'
import { RiskBadge } from '../components/RiskAssessment'
import { useLiveDiagnosis } from '../hooks/useLiveDiagnosis'
import { getPatientIntake } from '../services/api'
import { ComplaintForm, type Complaint } from '../components/diagnosis/ComplaintForm'
import { DiagnosticOutput } from '../components/diagnosis/DiagnosticOutput'
import { InvestigationHub, type InvestigationAdvice, type LabTest, type UploadedReport } from '../components/diagnosis/InvestigationHub'
import { PhysicalExam } from '../components/diagnosis/PhysicalExam'
import { ResearchDashboard } from '../components/diagnosis/ResearchDashboard'
import { VitalsPanel } from '../components/diagnosis/VitalsPanel'
import apiClient from '../services/apiClient'

const COMPLAINT_TEMPLATES = {
  Pain: ['chest pain', 'abdominal pain', 'headache', 'back pain', 'joint pain', 'muscle pain'],
  Respiratory: ['cough', 'shortness of breath', 'wheezing', 'chest tightness'],
  GI: ['nausea', 'vomiting', 'diarrhea', 'constipation', 'heartburn', 'loss of appetite'],
  Neuro: ['dizziness', 'headache', 'confusion', 'weakness', 'numbness', 'tingling'],
  Cardio: ['chest pain', 'palpitations', 'syncope', 'edema'],
  General: ['fever', 'fatigue', 'weight loss', 'weight gain', 'night sweats'],
}

const DURATION_OPTIONS = [
  '1 hour', '2-6 hours', '12 hours', '1 day', '2-3 days', '1 week',
  '2 weeks', '1 month', '2-3 months', '6 months', '1 year', 'chronic (>1 year)',
]

const SEVERITY_OPTIONS = ['Mild', 'Moderate', 'Severe', 'Very Severe']

const INVESTIGATION_CATEGORIES = {
  Hematology: ['CBC with differential', 'Platelet count', 'PT/INR', 'PTT', 'ESR', 'Blood type & crossmatch'],
  Chemistry: ['Basic metabolic panel', 'Comprehensive metabolic panel', 'Liver function tests', 'Lipid panel', 'HbA1c', 'Thyroid function'],
  Cardiology: ['Troponins', 'BNP/NT-proBNP', 'CK-MB', 'Lipid profile', 'ECG', 'Echocardiogram'],
  Microbiology: ['Blood cultures', 'Urine culture', 'Wound culture', 'Rapid strep', 'COVID-19 test', 'Hepatitis panel'],
  Radiology: ['Chest X-ray', 'CT chest', 'CT abdomen', 'MRI brain', 'Ultrasound abdomen', 'Bone scan'],
  Specialized: ['Arterial blood gas', 'Pleural fluid analysis', 'CSF analysis', 'Tumor markers', 'Autoimmune panel'],
}

const COMMON_LAB_TESTS = [
  { test: 'Hemoglobin', normalRange: '12-16 g/dL (F), 14-18 g/dL (M)', units: 'g/dL' },
  { test: 'White Blood Cell Count', normalRange: '4.5-11.0', units: 'x10^3/uL' },
  { test: 'Platelet Count', normalRange: '150-450', units: 'x10^3/uL' },
  { test: 'Glucose', normalRange: '70-100 (fasting)', units: 'mg/dL' },
  { test: 'Creatinine', normalRange: '0.6-1.2', units: 'mg/dL' },
]

const EXAMINATION_SYSTEMS = {
  General: { icon: <VisibilityIcon />, findings: ['Well-appearing', 'Ill-appearing', 'Febrile', 'Pale', 'Jaundiced'] },
  HEENT: { icon: <VisibilityIcon />, findings: ['PERRL', 'Sclera anicteric', 'Oral mucosa moist', 'Neck supple'] },
  Cardiovascular: { icon: <HeartIcon />, findings: ['Regular rate and rhythm', 'No murmurs', 'No peripheral edema'] },
  Pulmonary: { icon: <LungsIcon />, findings: ['Clear to auscultation', 'No wheezes', 'No rales', 'Normal effort'] },
  Abdominal: { icon: <AbdomenIcon />, findings: ['Soft', 'Non-tender', 'Bowel sounds normal', 'No masses'] },
  Neurological: { icon: <NeuroIcon />, findings: ['Alert and oriented x3', 'Motor strength 5/5', 'Gait normal'] },
}

type ToastSeverity = 'success' | 'error' | 'info'

interface ToastState {
  open: boolean
  message: string
  severity: ToastSeverity
}

export default function ClinicalCaseSheet() {
  const [firstName, setFirstName] = useState('')
  const [lastName, setLastName] = useState('')
  const [age, setAge] = useState('')
  const [sex, setSex] = useState('')
  const [uhid, setUhid] = useState('')
  const [showPatientSelector, setShowPatientSelector] = useState(false)
  const [selectedPatientId, setSelectedPatientId] = useState<string | null>(null)
  const [selectedPatientRisk, setSelectedPatientRisk] = useState<'low' | 'medium' | 'high' | 'critical' | null>(null)
  const [generatingReport, setGeneratingReport] = useState(false)
  const [complaints, setComplaints] = useState<Complaint[]>([{ id: '1', complaint: '', duration: '', severity: '', details: '' }])
  const [presentHistory] = useState({ onset: '', chronology: [] as string[] })
  const [vitalSigns, setVitalSigns] = useState({ temperature: '', pulse: '', bloodPressure: '', respiratoryRate: '', oxygenSaturation: '', height: '', weight: '', bmi: '' })
  const [clinicalFindings, setClinicalFindings] = useState<Array<{ system: string; finding: string; normal: boolean; details: string }>>([])
  const [labTests, setLabTests] = useState<LabTest[]>([])
  const [uploadedReports, setUploadedReports] = useState<UploadedReport[]>([])
  const [investigationAdvice, setInvestigationAdvice] = useState<InvestigationAdvice[]>([])
  const [treatmentPlan, setTreatmentPlan] = useState<any | null>(null)
  const [prescriptionPlan, setPrescriptionPlan] = useState<any | null>(null)
  const [toast, setToast] = useState<ToastState>({ open: false, message: '', severity: 'success' })

  const showToast = useCallback((message: string, severity: ToastSeverity = 'success') => {
    setToast({ open: true, message, severity })
  }, [])

  useEffect(() => {
    if (vitalSigns.height && vitalSigns.weight) {
      const heightMeters = parseFloat(vitalSigns.height) / 100
      const weightKg = parseFloat(vitalSigns.weight)
      if (heightMeters > 0 && weightKg > 0) {
        setVitalSigns((prev) => ({ ...prev, bmi: (weightKg / (heightMeters * heightMeters)).toFixed(1) }))
      }
    }
  }, [vitalSigns.height, vitalSigns.weight])

  const updateComplaint = (id: string, field: keyof Complaint, value: string) => {
    setComplaints((prev) => prev.map((complaint) => (complaint.id === id ? { ...complaint, [field]: value } : complaint)))
  }

  const handleQuickSelect = (template: string) => {
    const lastComplaint = complaints[complaints.length - 1]
    if (lastComplaint && !lastComplaint.complaint) {
      updateComplaint(lastComplaint.id, 'complaint', template)
      return
    }

    setComplaints((prev) => [
      ...prev,
      { id: Date.now().toString(), complaint: template, duration: '', severity: '', details: '' },
    ])
  }

  const toggleClinicalFinding = (system: string, finding: string, normal: boolean = true) => {
    const existingIndex = clinicalFindings.findIndex(
      (clinicalFinding) => clinicalFinding.system === system && clinicalFinding.finding === finding,
    )

    if (existingIndex >= 0) {
      setClinicalFindings((prev) => prev.map((item, index) => (
        index === existingIndex ? { ...item, normal: !item.normal } : item
      )))
      return
    }

    setClinicalFindings((prev) => [...prev, { system, finding, normal, details: '' }])
  }

  const handlePatientSelection = async (patient: any) => {
    try {
      const patientData = await getPatientIntake(patient.intake_id) as any
      setFirstName(patientData.first_name || patientData.name?.split(' ')[0] || '')
      setLastName(patientData.last_name || patientData.name?.split(' ').slice(1).join(' ') || '')
      setAge(patientData.age?.toString() || patientData.age?.toString() || '')
      setSex(patientData.gender || '')
      setUhid(patientData.uhid || patient.intake_id)
      setSelectedPatientId(patient.intake_id)
      setSelectedPatientRisk(patientData.risk_level || null)
      setShowPatientSelector(false)
      showToast('Patient loaded successfully')
    } catch (error) {
      console.error('Failed to load patient data:', error)
      showToast('Failed to load patient data', 'error')
    }
  }

  const buildLiveDiagnosisPayload = useCallback(() => ({
    complaints: complaints
      .filter((complaint) => complaint.complaint?.trim())
      .map((complaint) => ({
        complaint: complaint.complaint,
        duration: complaint.duration,
        severity: complaint.severity,
      })),
    patient_history: `Onset: ${presentHistory.onset}\nTimeline: ${presentHistory.chronology.join(' -> ')}`,
    vital_signs: {
      BP: vitalSigns.bloodPressure,
      HR: vitalSigns.pulse,
      TEMP: vitalSigns.temperature,
      RR: vitalSigns.respiratoryRate,
      SPO2: vitalSigns.oxygenSaturation,
    },
    anthropometry: {
      height: vitalSigns.height,
      weight: vitalSigns.weight,
      bmi: vitalSigns.bmi,
    },
    clinical_findings: clinicalFindings,
  }), [clinicalFindings, complaints, presentHistory, vitalSigns])

  const { liveDiagnosis, isAnalyzing } = useLiveDiagnosis<any>({
    isEnabled: complaints.some((complaint) => complaint.complaint?.trim()),
    buildPayload: buildLiveDiagnosisPayload,
    delayMs: 1500,
  })

  const handleSuggestTreatment = async () => {
    const primaryDiagnosis = liveDiagnosis?.differential_diagnoses?.[0]
    if (!primaryDiagnosis) {
      showToast('No diagnosis generated yet', 'info')
      return
    }

    try {
      const response = await apiClient.post('/api/medical/live-diagnosis/suggest-treatment', {
        diagnosis: primaryDiagnosis.diagnosis || primaryDiagnosis.disease_name,
        patient_age: age ? parseInt(age, 10) : undefined,
        patient_gender: sex,
      })

      setTreatmentPlan(response.data)
      showToast('Treatment plan generated successfully')
    } catch (error) {
      showToast('Failed to generate treatment plan', 'error')
    }
  }

  return (
    <Box sx={{ p: 2 }}>
      <Typography variant="h4" gutterBottom fontWeight={600}>
        Clinical Case Sheet
      </Typography>

      {selectedPatientId && (
        <Alert severity="info" sx={{ mb: 2 }} action={selectedPatientRisk && <RiskBadge level={selectedPatientRisk} size="small" />}>
          Linked patient: <strong>{selectedPatientId}</strong>
        </Alert>
      )}

      <Grid container spacing={3}>
        <Grid item xs={12} md={7}>
          <Paper elevation={3} sx={{ p: 3, maxHeight: '85vh', overflow: 'auto' }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
              <Typography variant="h6">Patient Information</Typography>
              <Button variant="outlined" startIcon={<SearchIcon />} onClick={() => setShowPatientSelector(true)}>
                Load Patient
              </Button>
            </Box>

            <Accordion defaultExpanded sx={{ mb: 2 }}>
              <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                <Typography variant="subtitle1" fontWeight={600}>[P] Patient Demographics</Typography>
              </AccordionSummary>
              <AccordionDetails>
                <Grid container spacing={2}>
                  <Grid item xs={6}>
                    <TextField fullWidth label="First Name" value={firstName} onChange={(event) => setFirstName(event.target.value)} size="small" />
                  </Grid>
                  <Grid item xs={6}>
                    <TextField fullWidth label="Last Name" value={lastName} onChange={(event) => setLastName(event.target.value)} size="small" />
                  </Grid>
                  <Grid item xs={4}>
                    <TextField fullWidth label="Age" type="number" value={age} onChange={(event) => setAge(event.target.value)} size="small" />
                  </Grid>
                  <Grid item xs={4}>
                    <FormControl fullWidth size="small">
                      <InputLabel>Sex</InputLabel>
                      <Select value={sex} onChange={(event) => setSex(event.target.value)} label="Sex">
                        <MenuItem value="Male">Male</MenuItem>
                        <MenuItem value="Female">Female</MenuItem>
                        <MenuItem value="Other">Other</MenuItem>
                      </Select>
                    </FormControl>
                  </Grid>
                  <Grid item xs={4}>
                    <TextField fullWidth label="UHID" value={uhid} onChange={(event) => setUhid(event.target.value)} size="small" />
                  </Grid>
                </Grid>
              </AccordionDetails>
            </Accordion>

            <Accordion defaultExpanded sx={{ mb: 2 }}>
              <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                <Typography variant="subtitle1" fontWeight={600}>[LIST] Chief Complaints</Typography>
              </AccordionSummary>
              <AccordionDetails>
                <ComplaintForm
                  complaints={complaints}
                  updateComplaint={updateComplaint}
                  addComplaint={() => setComplaints((prev) => [...prev, { id: Date.now().toString(), complaint: '', duration: '', severity: '', details: '' }])}
                  removeComplaint={(id) => setComplaints((prev) => prev.filter((complaint) => complaint.id !== id))}
                  templates={COMPLAINT_TEMPLATES}
                  durationOptions={DURATION_OPTIONS}
                  severityOptions={SEVERITY_OPTIONS}
                  onQuickSelect={handleQuickSelect}
                />
              </AccordionDetails>
            </Accordion>

            <Accordion sx={{ mb: 2 }}>
              <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                <Typography variant="subtitle1" fontWeight={600}>[HEARTBEAT] Vital Signs</Typography>
              </AccordionSummary>
              <AccordionDetails>
                <VitalsPanel
                  vitalSigns={vitalSigns}
                  onVitalChange={(field, value) => setVitalSigns((prev) => ({ ...prev, [field]: value }))}
                  isLoading={false}
                />
              </AccordionDetails>
            </Accordion>

            <Accordion sx={{ mb: 2 }}>
              <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                <Typography variant="subtitle1" fontWeight={600}>[SEARCH] Clinical Examination</Typography>
              </AccordionSummary>
              <AccordionDetails>
                <PhysicalExam
                  systems={EXAMINATION_SYSTEMS}
                  clinicalFindings={clinicalFindings}
                  toggleClinicalFinding={toggleClinicalFinding}
                  onRemoveFinding={(system, finding) => setClinicalFindings((prev) => prev.filter((item) => !(item.system === system && item.finding === finding)))}
                  isLoading={false}
                />
              </AccordionDetails>
            </Accordion>

            <Accordion sx={{ mb: 2 }}>
              <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                <Typography variant="subtitle1" fontWeight={600}>[MICROSCOPE] Investigations</Typography>
              </AccordionSummary>
              <AccordionDetails>
                <InvestigationHub
                  investigationAdvice={investigationAdvice}
                  labTests={labTests}
                  uploadedReports={uploadedReports}
                  categories={INVESTIGATION_CATEGORIES}
                  commonTests={COMMON_LAB_TESTS}
                  onAddAdvice={(category, tests, reason, urgency) => setInvestigationAdvice((prev) => [...prev, { category, tests, reason, urgency: urgency || 'routine' }])}
                  onRemoveAdvice={(index) => setInvestigationAdvice((prev) => prev.filter((_, itemIndex) => itemIndex !== index))}
                  onUpdateLabTest={(id, field, value) => setLabTests((prev) => prev.map((test) => (test.id === id ? { ...test, [field]: value } : test)))}
                  onAddLabTest={(data) => setLabTests((prev) => [...prev, { id: Date.now().toString(), test: '', result: '', normalRange: '', units: '', date: '', status: 'pending', ...data }])}
                  onRemoveLabTest={(id) => setLabTests((prev) => prev.filter((test) => test.id !== id))}
                  onUploadReport={(_event) => {}}
                  onRemoveReport={(id) => setUploadedReports((prev) => prev.filter((report) => report.id !== id))}
                />
              </AccordionDetails>
            </Accordion>
          </Paper>
        </Grid>

        <Grid item xs={12} md={5}>
          <Stack spacing={3}>
            <DiagnosticOutput
              liveDiagnosis={liveDiagnosis}
              isAnalyzing={isAnalyzing}
              treatmentPlan={treatmentPlan}
              prescriptionPlan={prescriptionPlan}
              generatingReport={generatingReport}
              onSuggestTreatment={handleSuggestTreatment}
              onGeneratePrescription={() => showToast('Prescription generation is not wired yet', 'info')}
              onGenerateReport={() => {
                setGeneratingReport(true)
                showToast('Report export is not wired yet', 'info')
                setGeneratingReport(false)
              }}
              onExportCaseSheet={() => showToast('Case sheet export is not wired yet', 'info')}
            />

            {liveDiagnosis && (
              <ResearchDashboard
                diagnosis={liveDiagnosis.differential_diagnoses?.[0]?.diagnosis || liveDiagnosis.differential_diagnoses?.[0]?.disease_name || ''}
                topic={complaints[0]?.complaint || ''}
              />
            )}
          </Stack>
        </Grid>
      </Grid>

      <PatientSelector
        open={showPatientSelector}
        onClose={() => setShowPatientSelector(false)}
        onSelectPatient={handlePatientSelection}
      />

      <Snackbar
        open={toast.open}
        autoHideDuration={4000}
        onClose={() => setToast((prev) => ({ ...prev, open: false }))}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
      >
        <Alert onClose={() => setToast((prev) => ({ ...prev, open: false }))} severity={toast.severity} sx={{ width: '100%' }}>
          {toast.message}
        </Alert>
      </Snackbar>
    </Box>
  )
}

