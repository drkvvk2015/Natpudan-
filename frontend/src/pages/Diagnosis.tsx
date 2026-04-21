import { useState, useEffect, useCallback } from 'react'
import {
  Box,
  Paper,
  TextField,
  Button,
  Typography,
  Grid,
  CircularProgress,
  Alert,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  IconButton,
  Chip,
} from '@mui/material'
import {
  Visibility as VisibilityIcon,
  Favorite as HeartIcon,
  Air as LungsIcon,
  Restaurant as AbdomenIcon,
  Psychology as NeuroIcon,
  FitnessCenter as MusculoskeletalIcon,
  Spa as SkinIcon,
  Search as SearchIcon,
  ExpandMore as ExpandMoreIcon,
} from '@mui/icons-material'

import apiClient from '../services/apiClient'
import { useLiveDiagnosis } from '../hooks/useLiveDiagnosis'
import PatientSelector from '../components/PatientSelector'
import EnhancedMedicalHistory, { type MedicalHistoryItem, type SmokingHistory } from '../components/EnhancedMedicalHistory'
import { OPDCaseSheetService } from '../services/opdCaseSheetService'
import { getPatientIntake, generateDiagnosisReport, downloadPDF, type DiagnosisReportData } from '../services/api'
import { RiskBadge } from '../components/RiskAssessment'

// Modular Components
import { ComplaintForm, type Complaint } from '../components/diagnosis/ComplaintForm'
import { VitalsPanel } from '../components/diagnosis/VitalsPanel'
import { PhysicalExam } from '../components/diagnosis/PhysicalExam'
import { InvestigationHub, type LabTest, type UploadedReport, type InvestigationAdvice } from '../components/diagnosis/InvestigationHub'
import { DiagnosticOutput } from '../components/diagnosis/DiagnosticOutput'
import { ResearchDashboard } from '../components/diagnosis/ResearchDashboard'

// Constants
const COMPLAINT_TEMPLATES = {
  'Pain': ['chest pain', 'abdominal pain', 'headache', 'back pain', 'joint pain', 'muscle pain'],
  'Respiratory': ['cough', 'shortness of breath', 'wheezing', 'chest tightness'],
  'GI': ['nausea', 'vomiting', 'diarrhea', 'constipation', 'heartburn', 'loss of appetite'],
  'Neuro': ['dizziness', 'headache', 'confusion', 'weakness', 'numbness', 'tingling'],
  'Cardio': ['chest pain', 'palpitations', 'syncope', 'edema'],
  'General': ['fever', 'fatigue', 'weight loss', 'weight gain', 'night sweats']
}

const DURATION_OPTIONS = [
  '1 hour', '2-6 hours', '12 hours', '1 day', '2-3 days', '1 week',
  '2 weeks', '1 month', '2-3 months', '6 months', '1 year', 'chronic (>1 year)'
]

const SEVERITY_OPTIONS = ['Mild', 'Moderate', 'Severe', 'Very Severe']

const INVESTIGATION_CATEGORIES = {
  'Hematology': ['CBC with differential', 'Platelet count', 'PT/INR', 'PTT', 'ESR', 'Blood type & crossmatch'],
  'Chemistry': ['Basic metabolic panel', 'Comprehensive metabolic panel', 'Liver function tests', 'Lipid panel', 'HbA1c', 'Thyroid function'],
  'Cardiology': ['Troponins', 'BNP/NT-proBNP', 'CK-MB', 'Lipid profile', 'ECG', 'Echocardiogram'],
  'Microbiology': ['Blood cultures', 'Urine culture', 'Wound culture', 'Rapid strep', 'COVID-19 test', 'Hepatitis panel'],
  'Radiology': ['Chest X-ray', 'CT chest', 'CT abdomen', 'MRI brain', 'Ultrasound abdomen', 'Bone scan'],
  'Specialized': ['Arterial blood gas', 'Pleural fluid analysis', 'CSF analysis', 'Tumor markers', 'Autoimmune panel']
}

const COMMON_LAB_TESTS = [
  { test: 'Hemoglobin', normalRange: '12-16 g/dL (F), 14-18 g/dL (M)', units: 'g/dL' },
  { test: 'White Blood Cell Count', normalRange: '4.5-11.0', units: 'x10^3/uL' },
  { test: 'Platelet Count', normalRange: '150-450', units: 'x10^3/uL' },
  { test: 'Glucose', normalRange: '70-100 (fasting)', units: 'mg/dL' },
  { test: 'Creatinine', normalRange: '0.6-1.2', units: 'mg/dL' },
]

const EXAMINATION_SYSTEMS = {
  'General': { icon: <VisibilityIcon />, findings: ['Well-appearing', 'Ill-appearing', 'Febrile', 'Pale', 'Jaundiced'] },
  'HEENT': { icon: <VisibilityIcon />, findings: ['PERRL', 'Sclera anicteric', 'Oral mucosa moist', 'Neck supple'] },
  'Cardiovascular': { icon: <HeartIcon />, findings: ['Regular rate and rhythm', 'No murmurs', 'No peripheral edema'] },
  'Pulmonary': { icon: <LungsIcon />, findings: ['Clear to auscultation', 'No wheezes', 'No rales', 'Normal effort'] },
  'Abdominal': { icon: <AbdomenIcon />, findings: ['Soft', 'Non-tender', 'Bowel sounds normal', 'No masses'] },
  'Neurological': { icon: <NeuroIcon />, findings: ['Alert and oriented x3', 'Motor strength 5/5', 'Gait normal'] },
}

export default function ClinicalCaseSheet() {
  // --- State ---
  const [firstName, setFirstName] = useState('')
  const [lastName, setLastName] = useState('')
  const [age, setAge] = useState('')
  const [sex, setSex] = useState('')
  const [address, setAddress] = useState('')
  const [uhid, setUhid] = useState('')

  const [showPatientSelector, setShowPatientSelector] = useState(false)
  const [selectedPatientId, setSelectedPatientId] = useState<string | null>(null)
  const [selectedPatientRisk, setSelectedPatientRisk] = useState<'low' | 'medium' | 'high' | 'critical' | null>(null)
  const [generatingReport, setGeneratingReport] = useState(false)

  const [complaints, setComplaints] = useState<Complaint[]>([{ id: '1', complaint: '', duration: '', severity: '', details: '' }])
  const [presentHistory, setPresentHistory] = useState({ onset: '', chronology: [], associatedSymptoms: [], relievingFactors: [], aggravatingFactors: [] })
  const [enhancedHistory, setEnhancedHistory] = useState({ medicalHistory: [], smokingHistory: { isSmoker: false } })
  const [familyHistory, setFamilyHistory] = useState<string[]>([])
  const [reviewOfSystems, setReviewOfSystems] = useState<{[key: string]: string[]}>({ constitutional: [], cardiovascular: [], respiratory: [] })
  const [vitalSigns, setVitalSigns] = useState({ temperature: '', pulse: '', bloodPressure: '', respiratoryRate: '', oxygenSaturation: '', height: '', weight: '', bmi: '' })
  const [clinicalFindings, setClinicalFindings] = useState<any[]>([])
  const [labTests, setLabTests] = useState<LabTest[]>([])
  const [uploadedReports, setUploadedReports] = useState<UploadedReport[]>([])
  const [investigationAdvice, setInvestigationAdvice] = useState<InvestigationAdvice[]>([])
  const [assessment, setAssessment] = useState('')
  const [plan, setPlan] = useState('')
  const [treatmentPlan, setTreatmentPlan] = useState<any | null>(null)
  const [prescriptionPlan, setPrescriptionPlan] = useState<any | null>(null)

  // --- Feedback ---
  const [toast, setToast] = useState({ open: false, message: '', severity: 'success' as 'success' | 'error' | 'info' })
  const showToast = (message: string, severity: 'success' | 'error' | 'info' = 'success') => {
    setToast({ open: true, message, severity })
  }

  // --- BMI Calc ---
  useEffect(() => {
    if (vitalSigns.height && vitalSigns.weight) {
      const h = parseFloat(vitalSigns.height) / 100, w = parseFloat(vitalSigns.weight)
      if (h > 0 && w > 0) setVitalSigns(prev => ({ ...prev, bmi: (w / (h * h)).toFixed(1) }))
    }
  }, [vitalSigns.height, vitalSigns.weight])

  // --- Handlers ---
  const updateComplaint = (id: string, field: keyof Complaint, value: string) => {
    setComplaints(prev => prev.map(c => c.id === id ? { ...c, [field]: value } : c))
  }

  const handleQuickSelect = (template: string) => {
    const last = complaints[complaints.length - 1]
    if (last && !last.complaint) updateComplaint(last.id, 'complaint', template)
    else setComplaints([...complaints, { id: Date.now().toString(), complaint: template, duration: '', severity: '', details: '' }])
  }

  const toggleClinicalFinding = (system: string, finding: string, normal: boolean = true) => {
    const idx = clinicalFindings.findIndex(f => f.system === system && f.finding === finding)
    if (idx >= 0) setClinicalFindings(prev => prev.map((f, i) => i === idx ? { ...f, normal: !f.normal } : f))
    else setClinicalFindings(prev => [...prev, { system, finding, normal, details: '' }])
  }

  const handlePatientSelection = async (patient: any) => {
    try {
      const data = await getPatientIntake(patient.intake_id) as any
      setFirstName(data.first_name || data.name?.split(' ')[0] || '')
      setLastName(data.last_name || data.name?.split(' ').slice(1).join(' ') || '')
      setAge(data.age?.toString() || '')
      setSex(data.gender || '')
      setUhid(data.uhid || patient.intake_id)
      setSelectedPatientId(patient.intake_id)
      setShowPatientSelector(false)
    } catch (e) { alert('Failed to load patient data') }
  }

  // --- AI Integration ---
  const buildLiveDiagnosisPayload = useCallback(() => ({
    complaints: complaints.filter(c => c.complaint?.trim()).map(c => ({ complaint: c.complaint, duration: c.duration, severity: c.severity })),
    patient_history: `Onset: ${presentHistory.onset}\nTimeline: ${presentHistory.chronology.join(' -> ')}`,
    vital_signs: { BP: vitalSigns.bloodPressure, HR: vitalSigns.pulse, TEMP: vitalSigns.temperature },
    anthropometry: { height: vitalSigns.height, weight: vitalSigns.weight, bmi: vitalSigns.bmi },
    clinical_findings: clinicalFindings,
  }), [clinicalFindings, complaints, presentHistory, vitalSigns])

  const { liveDiagnosis, isAnalyzing } = useLiveDiagnosis<any>({
    isEnabled: complaints.some(c => c.complaint?.trim()),
    buildPayload: buildLiveDiagnosisPayload,
    delayMs: 1500,
  })

  const handleSuggestTreatment = async () => {
    const diag = liveDiagnosis?.differential_diagnoses?.[0]
    if (!diag) return alert('No diagnosis generated')
    const res = await apiClient.post('/api/medical/live-diagnosis/suggest-treatment', {
      diagnosis: diag.diagnosis || diag.disease_name,
      patient_age: parseInt(age), patient_gender: sex
    })
    setTreatmentPlan(res.data)
  }

  return (
    <Box sx={{ p: 2 }}>
      <Typography variant="h4" gutterBottom fontWeight={600}>Clinical Case Sheet</Typography>

      <Grid container spacing={3}>
        <Grid item xs={12} md={7}>
          <Paper elevation={3} sx={{ p: 3, maxHeight: '85vh', overflow: 'auto' }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
              <Typography variant="h6">Patient Information</Typography>
              <Button variant="outlined" startIcon={<SearchIcon />} onClick={() => setShowPatientSelector(true)}>Load Patient</Button>
            </Box>

            <Accordion defaultExpanded sx={{ mb: 2 }}>
              <AccordionSummary expandIcon={<ExpandMoreIcon />}><Typography variant="subtitle1" fontWeight={600}>[P] Patient Demographics</Typography></AccordionSummary>
              <AccordionDetails>
                <Grid container spacing={2}>
                  <Grid item xs={6}><TextField fullWidth label="First Name" value={firstName} onChange={e => setFirstName(e.target.value)} size="small" /></Grid>
                  <Grid item xs={6}><TextField fullWidth label="Last Name" value={lastName} onChange={e => setLastName(e.target.value)} size="small" /></Grid>
                  <Grid item xs={4}><TextField fullWidth label="Age" type="number" value={age} onChange={e => setAge(e.target.value)} size="small" /></Grid>
                  <Grid item xs={4}>
                    <FormControl fullWidth size="small">
                      <InputLabel>Sex</InputLabel>
                      <Select value={sex} onChange={e => setSex(e.target.value)} label="Sex">
                        <MenuItem value="Male">Male</MenuItem><MenuItem value="Female">Female</MenuItem>
                      </Select>
                    </FormControl>
                  </Grid>
                  <Grid item xs={4}><TextField fullWidth label="UHID" value={uhid} onChange={e => setUhid(e.target.value)} size="small" /></Grid>
                </Grid>
              </AccordionDetails>
            </Accordion>

            <Accordion defaultExpanded sx={{ mb: 2 }}>
              <AccordionSummary expandIcon={<ExpandMoreIcon />}><Typography variant="subtitle1" fontWeight={600}>[LIST] Chief Complaints</Typography></AccordionSummary>
              <AccordionDetails>
                <ComplaintForm
                  complaints={complaints}
                  updateComplaint={updateComplaint}
                  addComplaint={() => setComplaints([...complaints, { id: Date.now().toString(), complaint: '', duration: '', severity: '', details: '' }])}
                  removeComplaint={id => setComplaints(prev => prev.filter(c => c.id !== id))}
                  templates={COMPLAINT_TEMPLATES}
                  durationOptions={DURATION_OPTIONS}
                  severityOptions={SEVERITY_OPTIONS}
                  onQuickSelect={handleQuickSelect}
                />
              </AccordionDetails>
            </Accordion>

            <Accordion sx={{ mb: 2 }}>
              <AccordionSummary expandIcon={<ExpandMoreIcon />}><Typography variant="subtitle1" fontWeight={600}>[HEARTBEAT] Vital Signs</Typography></AccordionSummary>
              <AccordionDetails>
                <VitalsPanel
                  vitalSigns={vitalSigns}
                  onVitalChange={(f, v) => setVitalSigns(prev => ({ ...prev, [f]: v }))}
                />
              </AccordionDetails>
            </Accordion>

            <Accordion sx={{ mb: 2 }}>
              <AccordionSummary expandIcon={<ExpandMoreIcon />}><Typography variant="subtitle1" fontWeight={600}>[SEARCH] Clinical Examination</Typography></AccordionSummary>
              <AccordionDetails>
                <PhysicalExam
                  systems={EXAMINATION_SYSTEMS}
                  clinicalFindings={clinicalFindings}
                  toggleClinicalFinding={toggleClinicalFinding}
                  onRemoveFinding={(s, f) => setClinicalFindings(prev => prev.filter(x => !(x.system === s && x.finding === f)))}
                />
              </AccordionDetails>
            </Accordion>

            <Accordion sx={{ mb: 2 }}>
              <AccordionSummary expandIcon={<ExpandMoreIcon />}><Typography variant="subtitle1" fontWeight={600}>[MICROSCOPE] Investigations</Typography></AccordionSummary>
              <AccordionDetails>
                <InvestigationHub
                  investigationAdvice={investigationAdvice}
                  labTests={labTests}
                  uploadedReports={uploadedReports}
                  categories={INVESTIGATION_CATEGORIES}
                  commonTests={COMMON_LAB_TESTS}
                  onAddAdvice={(c, t, r, u) => setInvestigationAdvice([...investigationAdvice, { category: c, tests: t, reason: r, urgency: u || 'routine' }])}
                  onRemoveAdvice={idx => setInvestigationAdvice(prev => prev.filter((_, i) => i !== idx))}
                  onUpdateLabTest={(id, f, v) => setLabTests(prev => prev.map(t => t.id === id ? { ...t, [f]: v } : t))}
                  onAddLabTest={data => setLabTests([...labTests, { id: Date.now().toString(), test: '', result: '', normalRange: '', units: '', date: '', status: 'pending', ...data }])}
                  onRemoveLabTest={id => setLabTests(prev => prev.filter(t => t.id !== id))}
                  onUploadReport={() => {}} // Placeholder
                  onRemoveReport={id => setUploadedReports(prev => prev.filter(r => r.id !== id))}
                />
              </AccordionDetails>
            </Accordion>
          </Paper>
        </Grid>

        <Grid item xs={12} md={5}>
          <DiagnosticOutput
            liveDiagnosis={liveDiagnosis}
            isAnalyzing={isAnalyzing}
            treatmentPlan={treatmentPlan}
            prescriptionPlan={prescriptionPlan}
            generatingReport={generatingReport}
            onSuggestTreatment={handleSuggestTreatment}
            onGeneratePrescription={() => {}}
            onGenerateReport={() => {}}
            onExportCaseSheet={() => {}}
          />
        </Grid>
      </Grid>

      {showPatientSelector && (
        <PatientSelector
          open={showPatientSelector}
          onClose={() => setShowPatientSelector(false)}
          onSelectPatient={handlePatientSelection}
        />
      )}
    </Box>
  )
}
