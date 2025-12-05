import { useState, useEffect, useCallback, useRef } from 'react'
import {
  Box,
  Paper,
  TextField,
  Button,
  Typography,
  Grid,
  Card,
  CardContent,
  CircularProgress,
  Chip,
  LinearProgress,
  Alert,
  Stack,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Autocomplete,
  ButtonGroup,
  Divider,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  FormGroup,
  FormControlLabel,
  Checkbox,
  Radio,
  RadioGroup,
  Slider,
  IconButton,
} from '@mui/material'
import {
  Search as SearchIcon,
  Psychology as PsychologyIcon,
  AutoAwesome as AutoAwesomeIcon,
  PictureAsPdf as PictureAsPdfIcon,
  Description as DescriptionIcon,
  ExpandMore as ExpandMoreIcon,
  Add as AddIcon,
  AccessTime as AccessTimeIcon,
  Assignment as AssignmentIcon,
  Visibility as VisibilityIcon,
  Hearing as HearingIcon,
  Favorite as HeartIcon,
  Air as LungsIcon,
  Restaurant as AbdomenIcon,
  Psychology as NeuroIcon,
  FitnessCenter as MusculoskeletalIcon,
  Spa as SkinIcon,
  ClearAll as ClearIcon,
  Upload as UploadIcon,
  GetApp as DownloadIcon,
  Science as LabIcon,
  Biotech as BiologyIcon,
} from '@mui/icons-material'
import axios from 'axios'
import PatientSelector from '../components/PatientSelector'
import EnhancedMedicalHistory, { type MedicalHistoryItem, type SmokingHistory } from '../components/EnhancedMedicalHistory'
import { OPDCaseSheetService } from '../services/opdCaseSheetService'
import { getPatientIntake, generateDiagnosisReport, downloadPDF, type DiagnosisReportData } from '../services/api'
import { RiskBadge } from '../components/RiskAssessment'

// Pre-defined complaint templates with duration options
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

const SEVERITY_OPTIONS = [
  'Mild', 'Moderate', 'Severe', 'Very Severe'
]

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
  { test: 'ALT/SGPT', normalRange: '7-35', units: 'U/L' },
  { test: 'AST/SGOT', normalRange: '8-35', units: 'U/L' },
  { test: 'Total Bilirubin', normalRange: '0.2-1.2', units: 'mg/dL' }
]

// Clinical examination templates
const EXAMINATION_SYSTEMS = {
  'General': {
    icon: <VisibilityIcon />,
    findings: [
      'Well-appearing', 'Ill-appearing', 'In distress', 'Alert and oriented',
      'Febrile', 'Afebrile', 'Pale', 'Jaundiced', 'Cyanotic', 'Diaphoretic'
    ]
  },
  'HEENT': {
    icon: <VisibilityIcon />,
    findings: [
      'PERRL', 'Sclera anicteric', 'Conjunctiva pale/pink', 'Oral mucosa moist',
      'No lymphadenopathy', 'Thyroid normal', 'Neck supple', 'JVD absent/present'
    ]
  },
  'Cardiovascular': {
    icon: <HeartIcon />,
    findings: [
      'Regular rate and rhythm', 'No murmurs', 'S1/S2 normal', 'No S3/S4',
      'No peripheral edema', 'Pulses 2+ bilaterally', 'Capillary refill <2s'
    ]
  },
  'Pulmonary': {
    icon: <LungsIcon />,
    findings: [
      'Clear to auscultation bilaterally', 'No wheezes', 'No rales', 'No rhonchi',
      'No chest wall tenderness', 'Respiratory effort normal', 'No accessory muscle use'
    ]
  },
  'Abdominal': {
    icon: <AbdomenIcon />,
    findings: [
      'Soft', 'Non-tender', 'Non-distended', 'Bowel sounds normal',
      'No hepatomegaly', 'No splenomegaly', 'No masses', 'No rebound tenderness'
    ]
  },
  'Neurological': {
    icon: <NeuroIcon />,
    findings: [
      'Alert and oriented x3', 'CN II-XII intact', 'Motor strength 5/5',
      'Reflexes 2+ symmetric', 'Sensation intact', 'Gait normal', 'Cerebellar function normal'
    ]
  },
  'Musculoskeletal': {
    icon: <MusculoskeletalIcon />,
    findings: [
      'No joint swelling', 'Full range of motion', 'No deformities',
      'Muscle strength normal', 'No tenderness', 'Gait normal'
    ]
  },
  'Skin': {
    icon: <SkinIcon />,
    findings: [
      'Warm and dry', 'No rash', 'No lesions', 'Good turgor',
      'No ulcers', 'No bruising', 'Normal color'
    ]
  }
}

interface Complaint {
  id: string
  complaint: string
  duration: string
  severity: string
  details: string
}

interface ClinicalFinding {
  system: string
  finding: string
  normal: boolean
  details: string
}

interface LabTest {
  id: string
  test: string
  result: string
  normalRange: string
  units: string
  date: string
  status: 'normal' | 'abnormal' | 'critical' | 'pending'
}

interface UploadedReport {
  id: string
  name: string
  type: 'lab' | 'radiology' | 'pathology' | 'other'
  date: string
  url?: string
  summary?: string
}

interface InvestigationAdvice {
  category: string
  tests: string[]
  reason: string
  urgency: 'routine' | 'urgent' | 'stat'
}

interface LiveDiagnosisResponse {
  differential_diagnoses: Array<{
    diagnosis?: string
    disease_name?: string
    confidence: number
    icd_code: string
    supporting_evidence: string[]
  }>
  recommended_tests: string[]
  clinical_summary: string
  data_completeness: number
}

export default function ClinicalCaseSheet() {
  // Patient Demographics
  const [firstName, setFirstName] = useState('')
  const [lastName, setLastName] = useState('')
  const [age, setAge] = useState('')
  const [sex, setSex] = useState('')
  const [address, setAddress] = useState('')
  const [uhid, setUhid] = useState('')
  
  // Patient selector state
  const [showPatientSelector, setShowPatientSelector] = useState(false)
  const [selectedPatientId, setSelectedPatientId] = useState<string | null>(null)
  const [selectedPatientRisk, setSelectedPatientRisk] = useState<'low' | 'medium' | 'high' | 'critical' | null>(null)
  const [generatingReport, setGeneratingReport] = useState(false)
  
  // Chief Complaints with enhanced structure
  const [complaints, setComplaints] = useState<Complaint[]>([
    { id: '1', complaint: '', duration: '', severity: '', details: '' }
  ])
  
  // Present History with chronological ordering
  const [presentHistory, setPresentHistory] = useState<{
    onset: string
    chronology: string[]
    associatedSymptoms: string[]
    relievingFactors: string[]
    aggravatingFactors: string[]
  }>({
    onset: '',
    chronology: [],
    associatedSymptoms: [],
    relievingFactors: [],
    aggravatingFactors: []
  })
  
  // Past Medical History
  const [enhancedHistory, setEnhancedHistory] = useState<{
    medicalHistory: MedicalHistoryItem[];
    smokingHistory: SmokingHistory;
  }>({
    medicalHistory: [],
    smokingHistory: { isSmoker: false }
  })
  
  // Family History
  const [familyHistory, setFamilyHistory] = useState<string[]>([])
  
  // Social History
  const [socialHistory, setSocialHistory] = useState<{
    occupation: string
    alcohol: string
    drugs: string
    travel: string
  }>({
    occupation: '',
    alcohol: '',
    drugs: '',
    travel: ''
  })
  
  // Review of Systems
  const [reviewOfSystems, setReviewOfSystems] = useState<{[key: string]: string[]}>({
    constitutional: [],
    cardiovascular: [],
    respiratory: [],
    gastrointestinal: [],
    genitourinary: [],
    neurological: [],
    musculoskeletal: [],
    dermatological: []
  })
  
  // Vital Signs
  const [vitalSigns, setVitalSigns] = useState({
    temperature: '',
    pulse: '',
    bloodPressure: '',
    respiratoryRate: '',
    oxygenSaturation: '',
    height: '',
    weight: '',
    bmi: ''
  })
  
  // Clinical Examination
  const [clinicalFindings, setClinicalFindings] = useState<ClinicalFinding[]>([])
  
  // Lab Investigations and Reports
  const [labTests, setLabTests] = useState<LabTest[]>([])
  const [uploadedReports, setUploadedReports] = useState<UploadedReport[]>([])
  const [investigationAdvice, setInvestigationAdvice] = useState<InvestigationAdvice[]>([])
  
  // Assessment and Plan
  const [assessment, setAssessment] = useState('')
  const [plan, setPlan] = useState('')

  // AI Diagnosis state
  const [liveDiagnosis, setLiveDiagnosis] = useState<LiveDiagnosisResponse | null>(null)
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const debounceTimerRef = useRef<number | null>(null)

  // Helper functions for complaints
  const addComplaint = () => {
    const newComplaint: Complaint = {
      id: Date.now().toString(),
      complaint: '',
      duration: '',
      severity: '',
      details: ''
    }
    setComplaints([...complaints, newComplaint])
  }

  const updateComplaint = (id: string, field: keyof Complaint, value: string) => {
    setComplaints((complaints || []).map(c => 
      c.id === id ? { ...c, [field]: value } : c
    ))
    
    // Auto-populate present history when complaint and duration are both filled
    const updatedComplaint = (complaints || []).find(c => c.id === id)
    if (updatedComplaint && field === 'duration' && value && updatedComplaint.complaint) {
      const historyEntry = `${updatedComplaint.complaint} for ${value}`
      if (!(presentHistory.chronology || []).includes(historyEntry)) {
        setPresentHistory(prev => ({
          ...prev,
          chronology: [...(prev.chronology || []), historyEntry]
        }))
      }
    }
    
    // Also update when complaint is changed and duration exists
    if (field === 'complaint' && value) {
      const complaint = (complaints || []).find(c => c.id === id)
      if (complaint?.duration) {
        const historyEntry = `${value} for ${complaint.duration}`
        if (!(presentHistory.chronology || []).includes(historyEntry)) {
          setPresentHistory(prev => ({
            ...prev,
            chronology: [...(prev.chronology || []), historyEntry]
          }))
        }
      }
    }
  }

  const removeComplaint = (id: string) => {
    setComplaints((complaints || []).filter(c => c.id !== id))
  }

  // Helper functions for clinical findings
  const toggleClinicalFinding = (system: string, finding: string, normal: boolean = true) => {
    const existingIndex = (clinicalFindings || []).findIndex(f => f.system === system && f.finding === finding)

    if (existingIndex >= 0) {
      // If exists, toggle the 'normal' flag (positive <-> negative)
      setClinicalFindings((clinicalFindings || []).map((f, i) => {
        if (i === existingIndex) {
          return { ...f, normal: !f.normal }
        }
        return f
      }))
    } else {
      // Add new finding as positive/normal by default
      const newFinding: ClinicalFinding = {
        system,
        finding,
        normal,
        details: ''
      }
      setClinicalFindings([...(clinicalFindings || []), newFinding])
    }
  }

  const addChronologyItem = (item: string) => {
    setPresentHistory(prev => ({
      ...prev,
      chronology: [...(prev.chronology || []), item]
    }))
  }

  const removeChronologyItem = (index: number) => {
    setPresentHistory(prev => ({
      ...prev,
      chronology: (prev.chronology || []).filter((_, i) => i !== index)
    }))
  }

  // Helper functions for lab investigations
  const addLabTest = () => {
    const newLabTest: LabTest = {
      id: Date.now().toString(),
      test: '',
      result: '',
      normalRange: '',
      units: '',
      date: new Date().toISOString().split('T')[0],
      status: 'pending'
    }
    setLabTests([...labTests, newLabTest])
  }

  const updateLabTest = (id: string, field: keyof LabTest, value: string) => {
    setLabTests((labTests || []).map(test => 
      test.id === id ? { ...test, [field]: value } : test
    ))
  }

  const removeLabTest = (id: string) => {
    setLabTests((labTests || []).filter(test => test.id !== id))
  }

  const addInvestigationAdvice = (category: string, tests: string[], reason: string, urgency: 'routine' | 'urgent' | 'stat' = 'routine') => {
    const newAdvice: InvestigationAdvice = {
      category,
      tests,
      reason,
      urgency
    }
    setInvestigationAdvice([...investigationAdvice, newAdvice])
  }

  const handleReportUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files
    if (!files) return

    for (let i = 0; i < (files || []).length; i++) {
      const file = files[i]
      const newReport: UploadedReport = {
        id: Date.now().toString() + i,
        name: file.name,
        type: file.name.toLowerCase().includes('lab') ? 'lab' : 
              file.name.toLowerCase().includes('rad') || file.name.toLowerCase().includes('xray') || file.name.toLowerCase().includes('ct') || file.name.toLowerCase().includes('mri') ? 'radiology' :
              file.name.toLowerCase().includes('path') || file.name.toLowerCase().includes('biopsy') ? 'pathology' : 'other',
        date: new Date().toISOString().split('T')[0],
        summary: `Uploaded ${file.type} file`
      }
      setUploadedReports(prev => [...prev, newReport])
    }
  }

  const removeReport = (id: string) => {
    setUploadedReports((uploadedReports || []).filter(report => report.id !== id))
  }

  // Patient selection handler
  const handlePatientSelection = async (patient: any) => {
    try {
      const patientData = await getPatientIntake(patient.intake_id)
      
      // Populate form with patient data
      setFirstName(patientData.first_name || '')
      setLastName(patientData.last_name || '')
      setAge(patientData.age?.toString() || '')
      setSex(patientData.gender || '')
      setAddress(patientData.address || '')
      setUhid(patientData.uhid || '')
      
      // Set risk level for badge display
      setSelectedPatientRisk(patientData.risk_level || 'medium')
      
      setSelectedPatientId(patient.intake_id)
      setShowPatientSelector(false)
    } catch (error) {
      console.error('Error loading patient:', error)
      alert('Failed to load patient data')
    }
  }

  // BMI calculation
  useEffect(() => {
    if (vitalSigns.height && vitalSigns.weight) {
      const heightM = parseFloat(vitalSigns.height) / 100
      const weightKg = parseFloat(vitalSigns.weight)
      if (heightM > 0 && weightKg > 0) {
        const bmiValue = (weightKg / (heightM * heightM)).toFixed(1)
        setVitalSigns(prev => ({ ...prev, bmi: bmiValue }))
      }
    }
  }, [vitalSigns.height, vitalSigns.weight])

  // Live diagnosis with debouncing
  const fetchLiveDiagnosis = useCallback(async () => {
    // Only fetch if we have at least one complaint
    if (complaints.every(c => !c.complaint.trim())) {
      setLiveDiagnosis(null)
      return
    }

    setIsAnalyzing(true)
    try {
      // Prepare vital signs
      const vitalSignsObj: any = {}
      if (vitalSigns.bloodPressure) vitalSignsObj.BP = vitalSigns.bloodPressure
      if (vitalSigns.pulse) vitalSignsObj.HR = vitalSigns.pulse
      if (vitalSigns.temperature) vitalSignsObj.TEMP = vitalSigns.temperature
      if (vitalSigns.oxygenSaturation) vitalSignsObj.SPO2 = vitalSigns.oxygenSaturation
      if (vitalSigns.respiratoryRate) vitalSignsObj.RR = vitalSigns.respiratoryRate

      const anthropometry: any = {}
      if (vitalSigns.height) anthropometry.height = vitalSigns.height
      if (vitalSigns.weight) anthropometry.weight = vitalSigns.weight
      if (vitalSigns.bmi) anthropometry.bmi = vitalSigns.bmi

      // Build comprehensive history string
      const fullHistory = [
        presentHistory.onset && `Onset: ${presentHistory.onset}`,
        presentHistory.chronology?.length && `Timeline: ${presentHistory.chronology.join(' -> ')}`,
        enhancedHistory.medicalHistory?.length && `Past Medical History: ${enhancedHistory.medicalHistory.map(h => `${h.condition} (${h.diagnosedYear})`).join(', ')}`,
        enhancedHistory.smokingHistory?.isSmoker && `Smoking: ${enhancedHistory.smokingHistory.packsPerDay} packs/day for ${enhancedHistory.smokingHistory.yearsSmoked} years (${enhancedHistory.smokingHistory.packYears} pack-years)`,
        familyHistory?.length && `Family History: ${familyHistory.join(', ')}`,
        Object.values(reviewOfSystems).some(arr => arr?.length) && `Review of Systems: ${Object.entries(reviewOfSystems).filter(([_, symptoms]) => symptoms?.length).map(([system, symptoms]) => `${system}: ${symptoms.join(', ')}`).join('; ')}`
      ].filter(Boolean).join('\n\n')

      const response = await axios.post('/api/medical/live-diagnosis', {
        complaints: (complaints || []).filter(c => c.complaint?.trim()).map(c => ({
          complaint: c.complaint,
          duration: c.duration,
          severity: c.severity
        })),
        patient_history: fullHistory,
        vital_signs: vitalSignsObj,
        anthropometry: anthropometry,
        clinical_findings: clinicalFindings
      })

      setLiveDiagnosis(response.data)
    } catch (error) {
      console.error('Error in live diagnosis:', error)
      setLiveDiagnosis(null)
    } finally {
      setIsAnalyzing(false)
    }
  }, [complaints, presentHistory, enhancedHistory, familyHistory, reviewOfSystems, vitalSigns, clinicalFindings])

  // Debounce live diagnosis
  useEffect(() => {
    if (debounceTimerRef.current) {
      clearTimeout(debounceTimerRef.current)
    }

    debounceTimerRef.current = window.setTimeout(() => {
      fetchLiveDiagnosis()
    }, 1500)

    return () => {
      if (debounceTimerRef.current) {
        clearTimeout(debounceTimerRef.current)
      }
    }
  }, [fetchLiveDiagnosis])

  // Missing state and functions needed for the complete functionality
  const [treatmentPlan, setTreatmentPlan] = useState<any | null>(null)
  const [prescriptionPlan, setPrescriptionPlan] = useState<any | null>(null)

  const handleSuggestTreatment = async () => {
    if (!liveDiagnosis?.differential_diagnoses?.length) {
      alert('Please generate a diagnosis first')
      return
    }

    try {
      const primaryDiagnosis = liveDiagnosis.differential_diagnoses[0]
      const response = await axios.post('/api/treatment-plans/suggest', {
        diagnosis: primaryDiagnosis.diagnosis || primaryDiagnosis.disease_name,
        patient_age: parseInt(age) || undefined,
        patient_gender: sex,
        comorbidities: (enhancedHistory.medicalHistory || []).map(h => h.condition)
      })
      
      setTreatmentPlan(response.data)
    } catch (error) {
      console.error('Error suggesting treatment:', error)
      alert('Error generating treatment plan')
    }
  }

  const handleGeneratePrescription = async () => {
    if (!liveDiagnosis?.differential_diagnoses?.length) {
      alert('Please generate a diagnosis first')
      return
    }

    try {
      const primaryDiagnosis = liveDiagnosis.differential_diagnoses[0]
      const response = await axios.post('/api/prescription/generate', {
        diagnosis: primaryDiagnosis.diagnosis || primaryDiagnosis.disease_name,
        patient_age: parseInt(age) || undefined,
        patient_weight: parseFloat(vitalSigns.weight) || undefined,
        allergies: (enhancedHistory.medicalHistory || []).filter(h => h.condition?.toLowerCase().includes('allerg')).map(h => h.condition)
      })
      
      setPrescriptionPlan(response.data)
    } catch (error) {
      console.error('Error generating prescription:', error)
      alert('Error generating prescription')
    }
  }

  // PDF Export Functions
  const handleGenerateReport = async () => {
    if (!liveDiagnosis || !liveDiagnosis.differential_diagnoses) {
      alert('Please generate a diagnosis first')
      return
    }

    setGeneratingReport(true)
    try {
      const reportData: DiagnosisReportData = {
        patient_name: `${firstName} ${lastName}`.trim() || 'Unknown Patient',
        age: parseInt(age) || undefined,
        sex: sex,
        uhid: uhid,
        complaints: (complaints || []).filter(c => c.complaint?.trim()).map(c => ({ 
          complaint: c.complaint, 
          duration: c.duration,
          severity: c.severity
        })),
        vitals: {
          temperature: vitalSigns.temperature,
          pulse: vitalSigns.pulse,
          bp: vitalSigns.bloodPressure,
          rr: vitalSigns.respiratoryRate,
          spo2: vitalSigns.oxygenSaturation,
        },
        differential_diagnoses: (liveDiagnosis.differential_diagnoses || []).map(d => ({
          name: d.diagnosis || d.disease_name,
          confidence: d.confidence || 0,
          icd_code: d.icd_code,
          supporting_findings: d.supporting_evidence || [],
        })),
        recommended_tests: liveDiagnosis.recommended_tests || [],
        clinical_summary: liveDiagnosis.clinical_summary,
        primary_diagnosis: liveDiagnosis.differential_diagnoses[0]?.diagnosis || liveDiagnosis.differential_diagnoses[0]?.disease_name,
      }

      const blob = await generateDiagnosisReport(reportData)
      downloadPDF(blob, `clinical_case_sheet_${firstName || 'patient'}_${new Date().toISOString().split('T')[0]}.pdf`)
    } catch (error) {
      console.error('Error generating report:', error)
      alert('Failed to generate report. Please try again.')
    } finally {
      setGeneratingReport(false)
    }
  }

  const handleExportOPDCaseSheet = async () => {
    try {
      setGeneratingReport(true)
      
      const caseSheetData = {
        patientInfo: {
          name: `${firstName} ${lastName}`.trim() || 'Unknown Patient',
          age: parseInt(age) || 0,
          gender: sex,
          uhid: uhid,
          address: address,
          date: new Date().toLocaleDateString()
        },
        chiefComplaints: (complaints || []).filter(c => c.complaint?.trim()),
        presentHistory: {
          onset: presentHistory.onset,
          chronology: presentHistory.chronology,
          associatedSymptoms: presentHistory.associatedSymptoms,
          relievingFactors: presentHistory.relievingFactors,
          aggravatingFactors: presentHistory.aggravatingFactors
        },
        pastMedicalHistory: enhancedHistory.medicalHistory,
        smokingIndex: {
          packsPerDay: enhancedHistory.smokingHistory.packsPerDay || 0,
          yearsSmoked: enhancedHistory.smokingHistory.yearsSmoked || 0,
          packYears: enhancedHistory.smokingHistory.packYears || 0,
          riskLevel: enhancedHistory.smokingHistory.packYears 
            ? enhancedHistory.smokingHistory.packYears > 20 ? 'High' 
              : enhancedHistory.smokingHistory.packYears > 10 ? 'Moderate' : 'Low'
            : 'None'
        },
        vitalSigns: vitalSigns,
        clinicalFindings: clinicalFindings,
        assessment: assessment,
        plan: plan
      }
      
      await OPDCaseSheetService.generateOPDCaseSheetPDF(caseSheetData as any)
      
    } catch (error) {
      console.error('Error generating case sheet:', error)
      alert('Failed to generate case sheet. Please try again.')
    } finally {
      setGeneratingReport(false)
    }
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom fontWeight={600}>
        Clinical Case Sheet
      </Typography>
      <Typography variant="body1" color="text.secondary" paragraph>
        Comprehensive medical assessment with pre-defined options and easy-click interface
      </Typography>

      <Grid container spacing={3}>
        {/* Left Side - Patient Data Input */}
        <Grid item xs={12} md={7}>
          <Paper elevation={3} sx={{ p: 3, maxHeight: '85vh', overflow: 'auto' }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
              <Typography variant="h6">Patient Information</Typography>
              <Button
                variant="outlined"
                size="small"
                startIcon={<SearchIcon />}
                onClick={() => setShowPatientSelector(true)}
                sx={{ textTransform: 'none' }}
              >
                Load Patient
              </Button>
            </Box>
            
            {/* Selected Patient Info */}
            {selectedPatientId && (
              <Alert 
                severity="info" 
                sx={{ mb: 2 }}
                action={selectedPatientRisk && <RiskBadge level={selectedPatientRisk} size="small" />}
              >
                <strong>Linked Patient:</strong> {selectedPatientId}
              </Alert>
            )}
            
            {/* Patient Demographics */}
            <Accordion defaultExpanded sx={{ mb: 2 }}>
              <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                <Typography variant="subtitle1" fontWeight={600}>
                  [P] Patient Demographics
                </Typography>
              </AccordionSummary>
              <AccordionDetails>
                <Grid container spacing={2}>
                  <Grid item xs={6}>
                    <TextField
                      fullWidth
                      label="First Name"
                      value={firstName}
                      onChange={(e) => setFirstName(e.target.value)}
                      size="small"
                    />
                  </Grid>
                  <Grid item xs={6}>
                    <TextField
                      fullWidth
                      label="Last Name"
                      value={lastName}
                      onChange={(e) => setLastName(e.target.value)}
                      size="small"
                    />
                  </Grid>
                  <Grid item xs={4}>
                    <TextField
                      fullWidth
                      label="Age"
                      type="number"
                      value={age}
                      onChange={(e) => setAge(e.target.value)}
                      size="small"
                    />
                  </Grid>
                  <Grid item xs={4}>
                    <FormControl fullWidth size="small">
                      <InputLabel>Sex</InputLabel>
                      <Select value={sex} onChange={(e) => setSex(e.target.value)} label="Sex">
                        <MenuItem value="Male">Male</MenuItem>
                        <MenuItem value="Female">Female</MenuItem>
                        <MenuItem value="Other">Other</MenuItem>
                      </Select>
                    </FormControl>
                  </Grid>
                  <Grid item xs={4}>
                    <TextField
                      fullWidth
                      label="UHID"
                      value={uhid}
                      onChange={(e) => setUhid(e.target.value)}
                      size="small"
                    />
                  </Grid>
                  <Grid item xs={12}>
                    <TextField
                      fullWidth
                      label="Address"
                      value={address}
                      onChange={(e) => setAddress(e.target.value)}
                      size="small"
                      multiline
                      rows={2}
                    />
                  </Grid>
                </Grid>
              </AccordionDetails>
            </Accordion>

            {/* Chief Complaints with Pre-text Functions */}
            <Accordion defaultExpanded sx={{ mb: 2 }}>
              <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                <Typography variant="subtitle1" fontWeight={600}>
                  [LIST] Chief Complaints
                </Typography>
              </AccordionSummary>
              <AccordionDetails>
                {/* Quick Complaint Categories */}
                <Typography variant="body2" gutterBottom>Quick Select:</Typography>
                <Box sx={{ mb: 2 }}>
                  {Object.entries(COMPLAINT_TEMPLATES).map(([category, templates]) => (
                    <Box key={category} sx={{ mb: 1 }}>
                      <Typography variant="caption" fontWeight={600}>{category}:</Typography>
                      <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5, mt: 0.5 }}>
                        {templates.map(template => (
                          <Chip
                            key={template}
                            label={template}
                            size="small"
                            onClick={() => {
                              const lastComplaint = (complaints || [])[Math.max(0, (complaints || []).length - 1)]
                              if (lastComplaint && !lastComplaint.complaint) {
                                updateComplaint(lastComplaint.id, 'complaint', template)
                                // Auto-add to present history chronology
                                const historyEntry = `${template} (onset)`
                                if (!(presentHistory.chronology || []).includes(historyEntry)) {
                                  setPresentHistory(prev => ({
                                    ...prev,
                                    chronology: [...(prev.chronology || []), historyEntry],
                                    onset: presentHistory.onset || 'Recent onset'
                                  }))
                                }
                              } else {
                                addComplaint()
                                setTimeout(() => {
                                  const newComplaints = [...complaints]
                                  const newComplaint = {
                                    id: Date.now().toString(),
                                    complaint: template,
                                    duration: '',
                                    severity: '',
                                    details: ''
                                  }
                                  setComplaints([...newComplaints, newComplaint])
                                  // Auto-add to present history
                                  const historyEntry = `${template} (onset)`
                                  if (!presentHistory.chronology.includes(historyEntry)) {
                                    setPresentHistory(prev => ({
                                      ...prev,
                                      chronology: [...prev.chronology, historyEntry]
                                    }))
                                  }
                                }, 100)
                              }
                            }}
                            sx={{ cursor: 'pointer' }}
                          />
                        ))}
                      </Box>
                    </Box>
                  ))}
                </Box>
                
                <Divider sx={{ my: 2 }} />
                
                {/* Individual Complaints */}
                {(complaints || []).map((complaint, index) => (
                  <Card key={complaint.id} variant="outlined" sx={{ mb: 2, p: 2 }}>
                    <Grid container spacing={2}>
                      <Grid item xs={12} md={6}>
                        <TextField
                          fullWidth
                          label={`Chief Complaint ${index + 1}`}
                          value={complaint.complaint}
                          onChange={(e) => updateComplaint(complaint.id, 'complaint', e.target.value)}
                          size="small"
                        />
                      </Grid>
                      <Grid item xs={6} md={3}>
                        <FormControl fullWidth size="small">
                          <InputLabel>Duration</InputLabel>
                          <Select
                            value={complaint.duration}
                            onChange={(e) => updateComplaint(complaint.id, 'duration', e.target.value)}
                            label="Duration"
                          >
                            {DURATION_OPTIONS.map(duration => (
                              <MenuItem key={duration} value={duration}>{duration}</MenuItem>
                            ))}
                          </Select>
                        </FormControl>
                      </Grid>
                      <Grid item xs={6} md={3}>
                        <FormControl fullWidth size="small">
                          <InputLabel>Severity</InputLabel>
                          <Select
                            value={complaint.severity}
                            onChange={(e) => updateComplaint(complaint.id, 'severity', e.target.value)}
                            label="Severity"
                          >
                            {SEVERITY_OPTIONS.map(severity => (
                              <MenuItem key={severity} value={severity}>{severity}</MenuItem>
                            ))}
                          </Select>
                        </FormControl>
                      </Grid>
                      <Grid item xs={12}>
                        <TextField
                          fullWidth
                          label="Additional Details"
                          value={complaint.details}
                          onChange={(e) => updateComplaint(complaint.id, 'details', e.target.value)}
                          size="small"
                          multiline
                          rows={2}
                          placeholder="Character, location, radiation, triggers..."
                        />
                      </Grid>
                      <Grid item xs={12}>
                        <Box sx={{ display: 'flex', justifyContent: 'flex-end' }}>
                          <IconButton
                            color="error"
                            onClick={() => removeComplaint(complaint.id)}
                            disabled={(complaints || []).length === 1}
                          >
                            <ClearIcon />
                          </IconButton>
                        </Box>
                      </Grid>
                    </Grid>
                  </Card>
                ))}
                <Button
                  variant="outlined"
                  onClick={addComplaint}
                  startIcon={<AddIcon />}
                  size="small"
                  sx={{ mt: 1 }}
                >
                  Add Complaint
                </Button>
              </AccordionDetails>
            </Accordion>
            {/* Present History with Chronological Timeline */}
            <Accordion sx={{ mb: 2 }}>
              <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                <Typography variant="subtitle1" fontWeight={600}>
                  [HPI] History of Present Illness
                </Typography>
              </AccordionSummary>
              <AccordionDetails>
                <Grid container spacing={2}>
                  <Grid item xs={12}>
                    <TextField
                      fullWidth
                      label="Onset"
                      value={presentHistory.onset}
                      onChange={(e) => setPresentHistory(prev => ({ ...prev, onset: e.target.value }))}
                      placeholder="When did it start?"
                      size="small"
                    />
                  </Grid>
                  
                  <Grid item xs={12}>
                    <Typography variant="body2" gutterBottom>
                      <AccessTimeIcon fontSize="small" sx={{ mr: 1, verticalAlign: 'middle' }} />
                      Chronological Timeline:
                    </Typography>
                    <Box sx={{ mb: 2 }}>
                      {(presentHistory.chronology || []).map((item, index) => (
                        <Chip
                          key={index}
                          label={`${index + 1}. ${item}`}
                          onDelete={() => removeChronologyItem(index)}
                          sx={{ m: 0.5 }}
                        />
                      ))}
                      <TextField
                        fullWidth
                        placeholder="Add chronological event (e.g., 'Started as mild pain')"
                        size="small"
                        onKeyPress={(e) => {
                          if (e.key === 'Enter') {
                            const target = e.target as HTMLInputElement
                            if (target.value.trim()) {
                              addChronologyItem(target.value.trim())
                              target.value = ''
                            }
                          }
                        }}
                        sx={{ mt: 1 }}
                      />
                    </Box>
                  </Grid>

                  <Grid item xs={12} md={6}>
                    <Typography variant="body2" gutterBottom>Associated Symptoms:</Typography>
                    <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5, mb: 1 }}>
                      {['nausea', 'vomiting', 'fever', 'chills', 'sweating', 'dizziness', 'fatigue', 'anxiety'].map(symptom => (
                        <Chip
                          key={symptom}
                          label={symptom}
                          size="small"
                          variant={presentHistory.associatedSymptoms.includes(symptom) ? 'filled' : 'outlined'}
                          onClick={() => {
                            setPresentHistory(prev => ({
                              ...prev,
                              associatedSymptoms: prev.associatedSymptoms.includes(symptom)
                                ? prev.associatedSymptoms.filter(s => s !== symptom)
                                : [...prev.associatedSymptoms, symptom]
                            }))
                          }}
                          sx={{ cursor: 'pointer' }}
                        />
                      ))}
                    </Box>
                  </Grid>

                  <Grid item xs={12} md={6}>
                    <Typography variant="body2" gutterBottom>Relieving Factors:</Typography>
                    <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5, mb: 1 }}>
                      {['rest', 'heat', 'cold', 'position change', 'medication', 'food'].map(factor => (
                        <Chip
                          key={factor}
                          label={factor}
                          size="small"
                          variant={presentHistory.relievingFactors.includes(factor) ? 'filled' : 'outlined'}
                          onClick={() => {
                            setPresentHistory(prev => ({
                              ...prev,
                              relievingFactors: prev.relievingFactors.includes(factor)
                                ? prev.relievingFactors.filter(f => f !== factor)
                                : [...prev.relievingFactors, factor]
                            }))
                          }}
                          sx={{ cursor: 'pointer' }}
                          color="success"
                        />
                      ))}
                    </Box>
                  </Grid>

                  <Grid item xs={12}>
                    <Typography variant="body2" gutterBottom>Aggravating Factors:</Typography>
                    <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                      {['movement', 'eating', 'stress', 'cold weather', 'hot weather', 'exercise', 'lying down'].map(factor => (
                        <Chip
                          key={factor}
                          label={factor}
                          size="small"
                          variant={presentHistory.aggravatingFactors.includes(factor) ? 'filled' : 'outlined'}
                          onClick={() => {
                            setPresentHistory(prev => ({
                              ...prev,
                              aggravatingFactors: prev.aggravatingFactors.includes(factor)
                                ? prev.aggravatingFactors.filter(f => f !== factor)
                                : [...prev.aggravatingFactors, factor]
                            }))
                          }}
                          sx={{ cursor: 'pointer' }}
                          color="error"
                        />
                      ))}
                    </Box>
                  </Grid>
                </Grid>
              </AccordionDetails>
            </Accordion>

            {/* Enhanced Medical History */}
            <Accordion sx={{ mb: 2 }}>
              <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                <Typography variant="subtitle1" fontWeight={600}>
                  [MEDICAL] Past Medical History
                </Typography>
              </AccordionSummary>
              <AccordionDetails>
                <EnhancedMedicalHistory
                  initialHistory={enhancedHistory}
                  onHistoryChange={setEnhancedHistory}
                />
              </AccordionDetails>
            </Accordion>

            {/* Vital Signs */}
            <Accordion defaultExpanded sx={{ mb: 2 }}>
              <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                <Typography variant="subtitle1" fontWeight={600}>
                  [HEARTBEAT] Vital Signs
                </Typography>
              </AccordionSummary>
              <AccordionDetails>
                <Grid container spacing={2}>
                  <Grid item xs={6} md={4}>
                    <TextField
                      fullWidth
                      label="Temperature (°F)"
                      type="number"
                      value={vitalSigns.temperature}
                      onChange={(e) => setVitalSigns(prev => ({ ...prev, temperature: e.target.value }))}
                      size="small"
                      placeholder="98.6"
                    />
                  </Grid>
                  <Grid item xs={6} md={4}>
                    <TextField
                      fullWidth
                      label="Pulse (bpm)"
                      type="number"
                      value={vitalSigns.pulse}
                      onChange={(e) => setVitalSigns(prev => ({ ...prev, pulse: e.target.value }))}
                      size="small"
                      placeholder="72"
                    />
                  </Grid>
                  <Grid item xs={6} md={4}>
                    <TextField
                      fullWidth
                      label="BP (mmHg)"
                      value={vitalSigns.bloodPressure}
                      onChange={(e) => setVitalSigns(prev => ({ ...prev, bloodPressure: e.target.value }))}
                      size="small"
                      placeholder="120/80"
                    />
                  </Grid>
                  <Grid item xs={6} md={4}>
                    <TextField
                      fullWidth
                      label="RR (/min)"
                      type="number"
                      value={vitalSigns.respiratoryRate}
                      onChange={(e) => setVitalSigns(prev => ({ ...prev, respiratoryRate: e.target.value }))}
                      size="small"
                      placeholder="16"
                    />
                  </Grid>
                  <Grid item xs={6} md={4}>
                    <TextField
                      fullWidth
                      label="SpO2 (%)"
                      type="number"
                      value={vitalSigns.oxygenSaturation}
                      onChange={(e) => setVitalSigns(prev => ({ ...prev, oxygenSaturation: e.target.value }))}
                      size="small"
                      placeholder="98"
                    />
                  </Grid>
                  <Grid item xs={6} md={4}>
                    <TextField
                      fullWidth
                      label="Height (cm)"
                      type="number"
                      value={vitalSigns.height}
                      onChange={(e) => setVitalSigns(prev => ({ ...prev, height: e.target.value }))}
                      size="small"
                    />
                  </Grid>
                  <Grid item xs={6} md={4}>
                    <TextField
                      fullWidth
                      label="Weight (kg)"
                      type="number"
                      value={vitalSigns.weight}
                      onChange={(e) => setVitalSigns(prev => ({ ...prev, weight: e.target.value }))}
                      size="small"
                    />
                  </Grid>
                  <Grid item xs={6} md={4}>
                    <TextField
                      fullWidth
                      label="BMI"
                      value={vitalSigns.bmi}
                      size="small"
                      disabled
                    />
                  </Grid>
                </Grid>
              </AccordionDetails>
            </Accordion>

            {/* Clinical Examination - Head to Toe */}
            <Accordion sx={{ mb: 2 }}>
              <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                <Typography variant="subtitle1" fontWeight={600}>
                  [SEARCH] Clinical Examination (Head to Toe)
                </Typography>
              </AccordionSummary>
              <AccordionDetails>
                {Object.entries(EXAMINATION_SYSTEMS).map(([system, { icon, findings }]) => (
                  <Card key={system} variant="outlined" sx={{ mb: 2 }}>
                    <CardContent>
                      <Typography variant="subtitle2" gutterBottom sx={{ display: 'flex', alignItems: 'center' }}>
                        {icon}
                        <Box sx={{ ml: 1 }}>{system}</Box>
                      </Typography>
                      <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                        {findings.map(finding => {
                          const existing = clinicalFindings.find(f => f.system === system && f.finding === finding)
                          const isSelected = !!existing
                          const isNormal = existing ? existing.normal : true
                          return (
                            <Chip
                              key={finding}
                              label={finding}
                              size="small"
                              variant={isSelected ? 'filled' : 'outlined'}
                              onClick={() => toggleClinicalFinding(system, finding, true)}
                              onDelete={() => {
                                // remove specific finding
                                setClinicalFindings((clinicalFindings || []).filter(f => !(f.system === system && f.finding === finding)))
                              }}
                              sx={{ cursor: 'pointer' }}
                              color={isSelected ? (isNormal ? 'success' : 'error') : 'default'}
                            />
                          )
                        })}
                      </Box>
                      
                      {/* Custom findings input */}
                      <TextField
                        fullWidth
                        placeholder={`Add custom ${system.toLowerCase()} findings...`}
                        size="small"
                        sx={{ mt: 1 }}
                        onKeyPress={(e) => {
                          if (e.key === 'Enter') {
                            const target = e.target as HTMLInputElement
                            if (target.value.trim()) {
                              toggleClinicalFinding(system, target.value.trim(), true)
                              target.value = ''
                            }
                          }
                        }}
                      />
                      
                      {/* Show selected abnormal findings */}
                      {(clinicalFindings || []).filter(f => f.system === system).length > 0 && (
                        <Box sx={{ mt: 2 }}>
                          <Typography variant="caption" color="text.secondary">
                            Selected findings:
                          </Typography>
                          {(clinicalFindings || [])
                            .filter(f => f.system === system)
                            .map((finding, index) => (
                              <Chip
                                key={index}
                                label={finding.finding}
                                onDelete={() => toggleClinicalFinding(finding.system, finding.finding)}
                                sx={{ m: 0.5 }}
                                size="small"
                                color="primary"
                              />
                            ))}
                        </Box>
                      )}
                    </CardContent>
                  </Card>
                ))}
              </AccordionDetails>
            </Accordion>

            {/* Lab Investigations and Reports */}
            <Accordion sx={{ mb: 2 }}>
              <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                <Typography variant="subtitle1" fontWeight={600}>
                  [MICROSCOPE] Lab Investigations & Reports
                </Typography>
              </AccordionSummary>
              <AccordionDetails>
                {/* Investigation Advice */}
                <Box sx={{ mb: 3 }}>
                  <Typography variant="subtitle2" gutterBottom sx={{ display: 'flex', alignItems: 'center' }}>
                    <LabIcon sx={{ mr: 1 }} />
                    Suggested Investigations
                  </Typography>
                  
                  {/* Quick Investigation Categories */}
                  <Box sx={{ mb: 2 }}>
                    {Object.entries(INVESTIGATION_CATEGORIES).map(([category, tests]) => (
                      <Card key={category} variant="outlined" sx={{ mb: 1, p: 1 }}>
                        <Typography variant="caption" fontWeight={600} color="primary">
                          {category}:
                        </Typography>
                        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5, mt: 0.5 }}>
                          {tests.map(test => (
                            <Chip
                              key={test}
                              label={test}
                              size="small"
                              onClick={() => addInvestigationAdvice(category, [test], `${category} workup indicated`, 'routine')}
                              sx={{ cursor: 'pointer' }}
                              variant="outlined"
                            />
                          ))}
                        </Box>
                      </Card>
                    ))}
                  </Box>

                  {/* Selected Investigation Advice */}
                  {(investigationAdvice || []).length > 0 && (
                    <Box sx={{ mb: 2 }}>
                      <Typography variant="body2" gutterBottom>Selected Investigations:</Typography>
                      {investigationAdvice.map((advice, index) => (
                        <Card key={index} variant="outlined" sx={{ mb: 1, p: 2 }}>
                          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start' }}>
                            <Box>
                              <Typography variant="subtitle2" color="primary">
                                {advice.category}
                              </Typography>
                              <Typography variant="body2">
                                Tests: {advice.tests.join(', ')}
                              </Typography>
                              <Typography variant="caption" color="text.secondary">
                                Reason: {advice.reason} | Urgency: {advice.urgency}
                              </Typography>
                            </Box>
                            <IconButton 
                              size="small" 
                              onClick={() => setInvestigationAdvice(investigationAdvice.filter((_, i) => i !== index))}
                            >
                              <ClearIcon />
                            </IconButton>
                          </Box>
                        </Card>
                      ))}
                    </Box>
                  )}
                </Box>

                <Divider sx={{ my: 2 }} />

                {/* Lab Results Entry */}
                <Box sx={{ mb: 3 }}>
                  <Typography variant="subtitle2" gutterBottom sx={{ display: 'flex', alignItems: 'center' }}>
                    <BiologyIcon sx={{ mr: 1 }} />
                    Lab Results
                  </Typography>
                  
                  {/* Quick Lab Test Entry */}
                  <Box sx={{ mb: 2 }}>
                    <Typography variant="caption" gutterBottom>Quick Add Common Tests:</Typography>
                    <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5, mb: 2 }}>
                      {COMMON_LAB_TESTS.map(labTest => (
                        <Chip
                          key={labTest.test}
                          label={labTest.test}
                          size="small"
                          onClick={() => {
                            const newTest: LabTest = {
                              id: Date.now().toString(),
                              test: labTest.test,
                              result: '',
                              normalRange: labTest.normalRange,
                              units: labTest.units,
                              date: new Date().toISOString().split('T')[0],
                              status: 'pending'
                            }
                            setLabTests([...labTests, newTest])
                          }}
                          sx={{ cursor: 'pointer' }}
                          variant="outlined"
                        />
                      ))}
                    </Box>
                  </Box>

                  {/* Lab Test Results Table */}
                  {labTests.map((test) => (
                    <Card key={test.id} variant="outlined" sx={{ mb: 2, p: 2 }}>
                      <Grid container spacing={2}>
                        <Grid item xs={12} md={3}>
                          <TextField
                            fullWidth
                            label="Test Name"
                            value={test.test}
                            onChange={(e) => updateLabTest(test.id, 'test', e.target.value)}
                            size="small"
                          />
                        </Grid>
                        <Grid item xs={6} md={2}>
                          <TextField
                            fullWidth
                            label="Result"
                            value={test.result}
                            onChange={(e) => updateLabTest(test.id, 'result', e.target.value)}
                            size="small"
                          />
                        </Grid>
                        <Grid item xs={6} md={2}>
                          <TextField
                            fullWidth
                            label="Units"
                            value={test.units}
                            onChange={(e) => updateLabTest(test.id, 'units', e.target.value)}
                            size="small"
                          />
                        </Grid>
                        <Grid item xs={12} md={2}>
                          <TextField
                            fullWidth
                            label="Normal Range"
                            value={test.normalRange}
                            onChange={(e) => updateLabTest(test.id, 'normalRange', e.target.value)}
                            size="small"
                          />
                        </Grid>
                        <Grid item xs={6} md={2}>
                          <FormControl fullWidth size="small">
                            <InputLabel>Status</InputLabel>
                            <Select
                              value={test.status}
                              onChange={(e) => updateLabTest(test.id, 'status', e.target.value as any)}
                              label="Status"
                            >
                              <MenuItem value="normal">Normal</MenuItem>
                              <MenuItem value="abnormal">Abnormal</MenuItem>
                              <MenuItem value="critical">Critical</MenuItem>
                              <MenuItem value="pending">Pending</MenuItem>
                            </Select>
                          </FormControl>
                        </Grid>
                        <Grid item xs={6} md={1}>
                          <IconButton 
                            color="error" 
                            onClick={() => removeLabTest(test.id)}
                            size="small"
                          >
                            <ClearIcon />
                          </IconButton>
                        </Grid>
                      </Grid>
                    </Card>
                  ))}
                  
                  <Button
                    variant="outlined"
                    onClick={addLabTest}
                    startIcon={<AddIcon />}
                    size="small"
                  >
                    Add Lab Test
                  </Button>
                </Box>

                <Divider sx={{ my: 2 }} />

                {/* Report Upload */}
                <Box>
                  <Typography variant="subtitle2" gutterBottom sx={{ display: 'flex', alignItems: 'center' }}>
                    <UploadIcon sx={{ mr: 1 }} />
                    Previous Reports Upload
                  </Typography>
                  
                  <Box sx={{ mb: 2 }}>
                    <Box
                      component="input"
                      type="file"
                      multiple
                      accept=".pdf,.jpg,.jpeg,.png,.doc,.docx"
                      onChange={handleReportUpload}
                      sx={{ display: 'none' }}
                      id="report-upload"
                    />
                    <label htmlFor="report-upload">
                      <Button
                        variant="outlined"
                        component="span"
                        startIcon={<UploadIcon />}
                        size="small"
                      >
                        Upload Lab/Radiology Reports
                      </Button>
                    </label>
                  </Box>

                  {/* Uploaded Reports List */}
                  {(uploadedReports || []).length > 0 && (
                    <Box>
                      <Typography variant="body2" gutterBottom>Uploaded Reports:</Typography>
                      {uploadedReports.map((report) => (
                        <Card key={report.id} variant="outlined" sx={{ mb: 1, p: 2 }}>
                          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                            <Box>
                              <Typography variant="subtitle2">
                                {report.name}
                              </Typography>
                              <Typography variant="caption" color="text.secondary">
                                Type: {report.type} | Date: {report.date}
                              </Typography>
                              {report.summary && (
                                <Typography variant="body2" sx={{ mt: 0.5 }}>
                                  {report.summary}
                                </Typography>
                              )}
                            </Box>
                            <Box>
                              <IconButton size="small" color="primary">
                                <DownloadIcon />
                              </IconButton>
                              <IconButton 
                                size="small" 
                                color="error"
                                onClick={() => removeReport(report.id)}
                              >
                                <ClearIcon />
                              </IconButton>
                            </Box>
                          </Box>
                        </Card>
                      ))}
                    </Box>
                  )}
                </Box>
              </AccordionDetails>
            </Accordion>

            {/* Assessment and Plan */}
            <Accordion sx={{ mb: 2 }}>
              <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                <Typography variant="subtitle1" fontWeight={600}>
                  [LIST] Assessment & Plan
                </Typography>
              </AccordionSummary>
              <AccordionDetails>
                <Grid container spacing={2}>
                  <Grid item xs={12}>
                    <TextField
                      fullWidth
                      label="Clinical Assessment"
                      value={assessment}
                      onChange={(e) => setAssessment(e.target.value)}
                      multiline
                      rows={3}
                      placeholder="Clinical impression and differential diagnosis..."
                      size="small"
                    />
                  </Grid>
                  <Grid item xs={12}>
                    <TextField
                      fullWidth
                      label="Treatment Plan"
                      value={plan}
                      onChange={(e) => setPlan(e.target.value)}
                      multiline
                      rows={3}
                      placeholder="Investigations, treatment, and follow-up plan..."
                      size="small"
                    />
                  </Grid>
                </Grid>
              </AccordionDetails>
            </Accordion>

            {/* Export Buttons */}
            <Grid container spacing={2} sx={{ mt: 2 }}>
              <Grid item xs={6}>
                <Button
                  variant="outlined"
                  color="primary"
                  size="large"
                  onClick={handleGenerateReport}
                  disabled={generatingReport || !liveDiagnosis}
                  startIcon={<PictureAsPdfIcon />}
                  fullWidth
                >
                  {generatingReport ? 'Generating...' : 'Export PDF Report'}
                </Button>
              </Grid>
              <Grid item xs={6}>
                <Button
                  variant="outlined"
                  color="secondary"
                  size="large"
                  onClick={handleExportOPDCaseSheet}
                  disabled={generatingReport}
                  startIcon={<DescriptionIcon />}
                  fullWidth
                >
                  {generatingReport ? 'Generating...' : 'Clinical Case Sheet'}
                </Button>
              </Grid>
            </Grid>
          </Paper>
        </Grid>

        {/* Right Side - Real-time Analysis */}
        <Grid item xs={12} md={5}>
          <Paper elevation={3} sx={{ p: 3, height: '85vh', overflow: 'auto' }}>
            <Typography variant="h6" gutterBottom>
              [AI] AI Real-time Analysis
            </Typography>

            {/* Live Diagnosis Results */}
            {liveDiagnosis && (
              <Box>
                {/* Data Completeness */}
                <Box sx={{ mb: 2 }}>
                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    Data Completeness: {Math.round((liveDiagnosis.data_completeness || 0) * 100)}%
                  </Typography>
                  <LinearProgress 
                    variant="determinate" 
                    value={(liveDiagnosis.data_completeness || 0) * 100} 
                    sx={{ height: 8, borderRadius: 1 }}
                  />
                </Box>

                {/* Clinical Summary */}
                {liveDiagnosis.clinical_summary && (
                  <Alert severity="info" sx={{ mb: 2 }}>
                    <Typography variant="body2">
                      <strong>Clinical Summary:</strong><br />
                      {liveDiagnosis.clinical_summary}
                    </Typography>
                  </Alert>
                )}

                {/* Differential Diagnoses */}
                <Typography variant="subtitle1" fontWeight={600} gutterBottom>
                  Differential Diagnoses
                </Typography>
                <Stack spacing={1} sx={{ mb: 2 }}>
                  {liveDiagnosis.differential_diagnoses.map((diff, index) => (
                    <Card key={index} variant="outlined">
                      <CardContent sx={{ p: 2 }}>
                        <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
                          <Typography variant="subtitle2" fontWeight={600}>
                            {diff.diagnosis || diff.disease_name}
                          </Typography>
                          <Chip 
                            label={`${Math.round(diff.confidence * 100)}%`} 
                            size="small" 
                            color={diff.confidence > 0.8 ? 'success' : diff.confidence > 0.6 ? 'warning' : 'default'}
                          />
                        </Box>
                        {diff.icd_code && (
                          <Chip label={`ICD-10: ${diff.icd_code}`} size="small" sx={{ mb: 1 }} />
                        )}
                        {diff.supporting_evidence?.length > 0 && (
                          <Typography variant="body2" color="text.secondary">
                            Supporting evidence: {diff.supporting_evidence.join(', ')}
                          </Typography>
                        )}
                      </CardContent>
                    </Card>
                  ))}
                </Stack>

                {/* Recommended Tests */}
                {liveDiagnosis.recommended_tests?.length > 0 && (
                  <Box>
                    <Typography variant="subtitle1" fontWeight={600} gutterBottom>
                      Recommended Tests
                    </Typography>
                    <Stack direction="row" spacing={1} flexWrap="wrap" gap={1}>
                      {liveDiagnosis.recommended_tests.map((test, index) => (
                        <Chip key={index} label={test} size="small" variant="outlined" />
                      ))}
                    </Stack>
                  </Box>
                )}
              </Box>
            )}

            {/* Loading State */}
            {isAnalyzing && !liveDiagnosis && (
              <Box display="flex" flexDirection="column" alignItems="center" py={4}>
                <CircularProgress size={40} sx={{ mb: 2 }} />
                <Typography variant="body2" color="text.secondary">
                  Analyzing patient data...
                </Typography>
              </Box>
            )}

            {/* Empty State */}
            {!liveDiagnosis && !isAnalyzing && (
              <Box display="flex" flexDirection="column" alignItems="center" py={4}>
                <Typography variant="body2" color="text.secondary" textAlign="center">
                  Enter patient complaints to see real-time AI analysis
                </Typography>
              </Box>
            )}
          </Paper>
        </Grid>
      </Grid>

      {/* Treatment & Prescription */}
      <Paper elevation={3} sx={{ p: 3, mt: 3 }}>
        <Box display="flex" alignItems="center" gap={1} mb={2}>
          <PsychologyIcon color="secondary" />
          <Typography variant="h6">Treatment & Prescription</Typography>
        </Box>
        <Box display="flex" gap={1} mb={2}>
          <Button variant="contained" color="success" onClick={handleSuggestTreatment}>
            Suggest Treatment Plan
          </Button>
          <Button variant="outlined" color="secondary" onClick={handleGeneratePrescription}>
            Generate Prescription
          </Button>
        </Box>
        
        {treatmentPlan && (
          <Box sx={{ mb: 2 }}>
            <Typography variant="subtitle1" fontWeight={600}>AI Treatment Plan</Typography>
            <Box component="pre" sx={{ whiteSpace: 'pre-wrap', fontFamily: 'monospace', background:'#fafafa', p:1.5, borderRadius:2 }}>
              {JSON.stringify(treatmentPlan, null, 2)}
            </Box>
          </Box>
        )}
        
        {prescriptionPlan && (
          <Box>
            <Typography variant="subtitle1" fontWeight={600}>AI Prescription</Typography>
            <Box component="pre" sx={{ whiteSpace: 'pre-wrap', fontFamily: 'monospace', background:'#fff8e1', p:1.5, borderRadius:2 }}>
              {JSON.stringify(prescriptionPlan, null, 2)}
            </Box>
          </Box>
        )}
      </Paper>
      
      {/* Patient Selector Modal */}
      <PatientSelector
        open={showPatientSelector}
        onClose={() => setShowPatientSelector(false)}
        onSelectPatient={handlePatientSelection}
      />
    </Box>
  )
}
