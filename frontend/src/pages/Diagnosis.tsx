 
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
  Divider,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  LinearProgress,
  Alert,
  Stack,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
} from '@mui/material'
import {
  Search as SearchIcon,
  LocalHospital as HospitalIcon,
  ExpandMore as ExpandMoreIcon,
  TrendingUp as TrendingUpIcon,
  Science as ScienceIcon,
  Psychology as PsychologyIcon,
  AutoAwesome as AutoAwesomeIcon,
  PictureAsPdf as PictureAsPdfIcon,
  UploadFile as UploadFileIcon,
  Insights as InsightsIcon,
  Warning as WarningIcon,
  Description as DescriptionIcon,
} from '@mui/icons-material'
import axios from 'axios'
import PatientSelector from '../components/PatientSelector'
import { getPatientIntake, generateDiagnosisReport, generateCombinedReport, downloadPDF, type DiagnosisReportData } from '../services/api'
import { RiskBadge } from '../components/RiskAssessment'

interface DiagnosisResult {
  diagnosis: string
  confidence: string
  icd_code: string
  supporting_evidence: string[]
  recommended_tests: string[]
  differential_diagnoses: string[]
}

interface LiveDiagnosis {
  name: string
  confidence: number
  icd_code: string
  supporting_findings: string[]
  interpretation: string
  next_steps: string[]
}

interface LiveDiagnosisResponse {
  differential_diagnoses: LiveDiagnosis[]
  data_completeness: number
  sources: any[]
  clinical_summary: string
  has_sufficient_data: boolean
}

interface LabPdfInsights {
  extracted_values?: string
  abnormal_tests?: string[]
  insights?: string
  abnormal_findings?: string[]
}

interface RadiologyPdfInsights {
  extracted_findings?: string
  critical_findings?: string[]
  modality?: string
  impression?: string
  insights?: string
}

// Common complaint templates with associated history prompts
const complaintTemplates: {[key: string]: {
  patterns: string[]
  associatedFactors: string[]
  characteristics: string[]
}} = {
  fever: {
    patterns: ['Intermittent', 'Continuous', 'Remittent', 'Relapsing'],
    associatedFactors: ['Chills', 'Rigors', 'Night sweats', 'Malaise', 'Body ache'],
    characteristics: ['High grade (>101°F)', 'Low grade', 'Evening rise', 'Morning rise', 'No diurnal variation']
  },
  pain: {
    patterns: ['Continuous', 'Intermittent', 'Colicky', 'Throbbing', 'Sharp', 'Dull ache'],
    associatedFactors: ['Radiation', 'Relieved by rest', 'Relieved by position', 'Aggravated by movement', 'Aggravated by food'],
    characteristics: ['Severe', 'Moderate', 'Mild', 'Progressive', 'Non-progressive']
  },
  headache: {
    patterns: ['Continuous', 'Intermittent', 'Throbbing', 'Band-like', 'Unilateral', 'Bilateral'],
    associatedFactors: ['Nausea', 'Vomiting', 'Photophobia', 'Phonophobia', 'Aura', 'Visual disturbances'],
    characteristics: ['Severe', 'Moderate', 'Mild', 'Morning worse', 'Evening worse', 'Worse on straining']
  },
  cough: {
    patterns: ['Dry', 'Productive', 'Paroxysmal', 'Nocturnal', 'Morning worse'],
    associatedFactors: ['Sputum', 'Hemoptysis', 'Chest pain', 'Breathlessness', 'Wheeze'],
    characteristics: ['Yellow sputum', 'White sputum', 'Blood-tinged', 'Frothy', 'Foul smelling']
  },
  breathlessness: {
    patterns: ['At rest', 'On exertion', 'Orthopnea', 'PND', 'Nocturnal'],
    associatedFactors: ['Chest pain', 'Cough', 'Wheeze', 'Palpitations', 'Leg swelling'],
    characteristics: ['Progressive', 'Sudden onset', 'Gradual onset', 'Grade I-IV', 'Relieved by rest']
  },
  vomiting: {
    patterns: ['Projectile', 'Effortless', 'After meals', 'Morning', 'Throughout day'],
    associatedFactors: ['Nausea', 'Abdominal pain', 'Fever', 'Diarrhea', 'Hematemesis'],
    characteristics: ['Bilious', 'Non-bilious', 'Blood-stained', 'Food particles', 'Coffee ground']
  },
  diarrhea: {
    patterns: ['Acute', 'Chronic', 'Intermittent', 'Continuous'],
    associatedFactors: ['Abdominal pain', 'Fever', 'Vomiting', 'Blood in stool', 'Mucus'],
    characteristics: ['Watery', 'Loose', 'Frequent (>3/day)', 'Tenesmus', 'Urgency']
  },
  weakness: {
    patterns: ['Generalized', 'Localized', 'Progressive', 'Sudden onset', 'Gradual'],
    associatedFactors: ['Fatigue', 'Weight loss', 'Fever', 'Loss of appetite', 'Numbness'],
    characteristics: ['Constant', 'Worse in morning', 'Worse in evening', 'After exertion']
  }
}

// Past Medical History templates
const pastHistoryOptions = [
  'Diabetes Mellitus', 'Hypertension', 'Asthma', 'COPD', 'IHD', 'CVA',
  'CKD', 'Thyroid disorder', 'Tuberculosis', 'Epilepsy', 'Cancer',
  'Liver disease', 'Peptic ulcer', 'Rheumatic fever', 'None'
]

// Surgical History templates
const surgicalHistoryOptions = [
  'Appendectomy', 'Cholecystectomy', 'Hernia repair', 'C-section',
  'Hysterectomy', 'CABG', 'Joint replacement', 'Cataract surgery',
  'Fracture fixation', 'Other surgery', 'None'
]

// Social History templates
const socialHistoryOptions = [
  'Student', 'Employed', 'Unemployed', 'Retired', 'Homemaker',
  'Lives alone', 'Lives with family', 'Good support system',
  'Rural area', 'Urban area', 'Adequate housing'
]

// Clinical Examination - Head to Toe
const clinicalExamTemplates: {[key: string]: {
  findings: string[]
}} = {
  general: {
    findings: ['Conscious & alert', 'Oriented to time/place/person', 'Febrile', 'Afebrile', 
              'Pallor present', 'No pallor', 'Icterus present', 'No icterus', 
              'Cyanosis present', 'No cyanosis', 'Clubbing present', 'No clubbing',
              'Lymphadenopathy present', 'No lymphadenopathy', 'Edema present', 'No edema',
              'Well nourished', 'Malnourished', 'Dehydrated', 'Well hydrated']
  },
  head: {
    findings: ['Normocephalic', 'No abnormality detected', 'Scalp normal', 'Hair normal',
              'Facial asymmetry', 'TMJ tenderness', 'Frontal bossing', 'Depressed fontanelle']
  },
  eyes: {
    findings: ['Conjunctiva normal', 'Conjunctival pallor', 'Conjunctival injection',
              'Sclera normal', 'Icterus', 'PERRLA', 'Pupils equal & reactive',
              'Fundus normal', 'Vision normal', 'Squint', 'Nystagmus']
  },
  ent: {
    findings: ['Ears NAD', 'Hearing normal', 'Tympanic membrane normal', 'Discharge present',
              'Nose NAD', 'Nasal discharge', 'DNS', 'Throat normal', 'Pharyngeal congestion',
              'Tonsils normal', 'Tonsillar enlargement', 'Oral cavity normal', 'Tongue normal']
  },
  neck: {
    findings: ['Neck supple', 'No lymphadenopathy', 'Cervical LN enlarged', 
              'Thyroid normal', 'Thyroid enlarged', 'Goiter', 'JVP not raised',
              'JVP raised', 'Trachea central', 'No meningeal signs', 'Neck stiffness']
  },
  chest: {
    findings: ['Chest symmetrical', 'Normal expansion', 'No deformity',
              'Clear breath sounds bilaterally', 'Wheeze present', 'Rhonchi present',
              'Crepitations present', 'Reduced air entry', 'Bronchial breathing',
              'Pleural rub', 'VR normal', 'TVF normal']
  },
  cvs: {
    findings: ['S1 S2 normal', 'No murmur', 'Systolic murmur', 'Diastolic murmur',
              'Regular rhythm', 'Irregular rhythm', 'Apex beat normal', 'Displaced apex',
              'Palpitations absent', 'Peripheral pulses palpable', 'BP normal']
  },
  abdomen: {
    findings: ['Soft', 'Non-tender', 'No distension', 'Distended',
              'No organomegaly', 'Hepatomegaly', 'Splenomegaly', 'Hepatosplenomegaly',
              'Bowel sounds normal', 'Bowel sounds absent', 'Rigidity', 'Guarding',
              'Rebound tenderness', 'Shifting dullness', 'Free fluid', 'No mass palpable',
              'Hernia present', 'Ascites present']
  },
  genitourinary: {
    findings: ['External genitalia normal', 'No discharge', 'Catheterized',
              'CVA tenderness absent', 'CVA tenderness present', 'Bladder not palpable',
              'Bladder palpable', 'Urine output adequate']
  },
  musculoskeletal: {
    findings: ['Normal gait', 'Full ROM all joints', 'No joint swelling', 'Joint swelling present',
              'No deformity', 'Deformity present', 'Muscle power 5/5', 'Reduced power',
              'No tenderness', 'Tenderness present', 'Spine normal', 'SLR negative']
  },
  neurological: {
    findings: ['Conscious & oriented', 'GCS 15/15', 'Higher functions normal',
              'Cranial nerves intact', 'Motor system normal', 'Sensory system normal',
              'Reflexes normal', 'Plantar flexor bilaterally', 'Plantar extensor',
              'Cerebellar signs absent', 'Meningeal signs absent', 'Speech normal',
              'Memory intact', 'Coordination normal']
  },
  skin: {
    findings: ['Normal', 'Rash present', 'Petechiae', 'Ecchymosis', 'Ulcer',
              'Dry skin', 'Moist', 'Warm', 'Cold extremities', 'No lesions',
              'Turgor normal', 'Poor turgor', 'Pigmentation', 'Scarring']
  }
}

// Laboratory Investigations
const labInvestigations: {[key: string]: {
  tests: string[]
}} = {
  hematology: {
    tests: ['CBC', 'Hemoglobin', 'WBC count', 'Platelet count', 'ESR', 'CRP',
            'Peripheral smear', 'Reticulocyte count', 'Blood indices', 'HbA1c',
            'Bleeding time', 'Clotting time', 'PT/INR', 'aPTT']
  },
  biochemistry: {
    tests: ['Blood glucose (F/PP/Random)', 'RBS', 'HbA1c', 'Lipid profile',
            'Renal function (Urea/Creatinine)', 'eGFR', 'Electrolytes (Na/K/Cl)',
            'Liver function tests', 'Bilirubin', 'SGOT/SGPT', 'ALP', 'GGT',
            'Total protein', 'Albumin', 'Calcium', 'Phosphorus', 'Uric acid',
            'Amylase', 'Lipase', 'LDH', 'CPK', 'Troponin']
  },
  serology: {
    tests: ['HIV', 'HBsAg', 'Anti-HCV', 'VDRL', 'Dengue NS1/IgM/IgG',
            'Malaria antigen/smear', 'Typhoid IgM', 'Widal test',
            'ASO titre', 'RA factor', 'ANA', 'Anti-dsDNA', 'CCP antibody',
            'Thyroid (TSH/T3/T4)', 'Vitamin D', 'Vitamin B12', 'Ferritin']
  },
  microbiology: {
    tests: ['Blood culture', 'Urine culture', 'Sputum culture', 'Stool culture',
            'Wound swab', 'Pus culture', 'CSF analysis', 'Throat swab',
            'Gram stain', 'AFB stain', 'KOH mount', 'Sensitivity report']
  },
  urine: {
    tests: ['Routine & microscopy', 'Albumin', 'Sugar', 'Pus cells', 'RBCs',
            'Casts', 'Crystals', '24hr protein', 'Microalbumin', 'ACR',
            'Urine culture', 'Pregnancy test']
  },
  stool: {
    tests: ['Routine & microscopy', 'Occult blood', 'Ova & cysts',
            'Stool culture', 'Reducing substances', 'Fat globules']
  },
  other: {
    tests: ['ABG', 'Sputum AFB', 'Pleural fluid analysis', 'Ascitic fluid',
            'Synovial fluid', 'CSF analysis', 'Bone marrow', 'FNAC',
            'Biopsy', 'ECG', 'Echocardiography', 'Holter monitoring',
            'Stress test', 'PFT', 'Sleep study']
  }
}

// Radiological Investigations
const radiologyInvestigations: {[key: string]: {
  studies: string[]
}} = {
  xray: {
    studies: ['Chest X-ray PA view', 'Chest X-ray lateral', 'Chest X-ray AP',
              'Abdomen X-ray erect', 'Abdomen X-ray supine', 'KUB X-ray',
              'Spine X-ray (Cervical/Thoracic/Lumbar)', 'Pelvis X-ray',
              'Skull X-ray', 'PNS X-ray', 'Long bones X-ray',
              'Joint X-ray (Knee/Hip/Shoulder)', 'Hand/Foot X-ray',
              'Mammography']
  },
  ultrasound: {
    studies: ['USG Abdomen', 'USG Pelvis', 'USG KUB', 'USG Whole abdomen',
              'USG Abdomen & Pelvis', 'USG Neck', 'USG Thyroid',
              'USG Breast', 'USG Scrotum', 'USG Soft tissue',
              'USG Doppler (Arterial/Venous)', 'Carotid Doppler',
              'Renal Doppler', 'DVT study', 'Obstetric scan',
              'Anomaly scan', 'Growth scan', 'Transvaginal scan']
  },
  ct: {
    studies: ['CT Brain plain', 'CT Brain with contrast', 'NCCT Head',
              'CT Chest', 'HRCT Chest', 'CT Abdomen', 'CT Pelvis',
              'CT Abdomen & Pelvis', 'CT KUB', 'CT Angiography',
              'CT Spine (Cervical/Thoracic/Lumbar)', 'CT PNS',
              'CT Neck', 'CT Guided biopsy']
  },
  mri: {
    studies: ['MRI Brain', 'MRI Brain with contrast', 'MRI Spine',
              'MRI Cervical spine', 'MRI Lumbar spine', 'MRI Knee',
              'MRI Shoulder', 'MRI Abdomen', 'MRI Pelvis',
              'MRCP', 'MR Angiography', 'MR Venography',
              'Functional MRI', 'MRI whole spine']
  },
  nuclear: {
    studies: ['Bone scan', 'Thyroid scan', 'Renal scan', 'PET scan',
              'PET-CT', 'Gallium scan', 'MIBG scan', 'Ventilation-perfusion scan']
  },
  interventional: {
    studies: ['Fluoroscopy', 'Barium swallow', 'Barium meal',
              'Barium follow through', 'Barium enema', 'IVP',
              'MCU', 'HSG', 'Sialography', 'Fistulogram',
              'Sinogram', 'Arthrography']
  },
  special: {
    studies: ['Mammography', 'DEXA scan', 'OPG', 'Contrast studies',
              'Angiography', 'Venography', 'Lymphangiography']
  }
}

export default function Diagnosis() {
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
  
  // Chief Complaints
  const [complaints, setComplaints] = useState<{complaint: string, duration: string}[]>([
    {complaint: '', duration: ''}
  ])
  
  // HPI details for each complaint (stores selected options)
  const [hpiDetails, setHpiDetails] = useState<{[key: number]: {
    pattern: string[]
    associated: string[]
    characteristics: string[]
  }}>({})
  
  // History sections
  const [hpi, setHpi] = useState('') // History of Presenting Illness
  const [pastHistory, setPastHistory] = useState<string[]>([])
  const [surgicalHistory, setSurgicalHistory] = useState<string[]>([])
  const [socialHistory, setSocialHistory] = useState<string[]>([])
  const [personalHistory, setPersonalHistory] = useState('')
  
  // Clinical Examination findings
  const [clinicalFindings, setClinicalFindings] = useState<{[key: string]: string[]}>({})
  
  // Laboratory & Radiology
  const [labFindings, setLabFindings] = useState<{[key: string]: string[]}>({})
  const [labResults, setLabResults] = useState('')
  const [radiologyFindings, setRadiologyFindings] = useState<{[key: string]: string[]}>({})
  const [radiologyResults, setRadiologyResults] = useState('')
  // PDF upload states (AI extraction)
  const [labPdfFile, setLabPdfFile] = useState<File | null>(null)
  const [labPdfUploading, setLabPdfUploading] = useState(false)
  const [labPdfInsights, setLabPdfInsights] = useState<LabPdfInsights | null>(null)
  const [radiologyPdfFile, setRadiologyPdfFile] = useState<File | null>(null)
  const [radiologyPdfUploading, setRadiologyPdfUploading] = useState(false)
  const [radiologyPdfInsights, setRadiologyPdfInsights] = useState<RadiologyPdfInsights | null>(null)
  
  const [symptoms, setSymptoms] = useState('')
  const [patientHistory] = useState('')
  
  // Vital Signs - separate fields
  const [bp, setBp] = useState('')
  const [hr, setHr] = useState('')
  const [temp, setTemp] = useState('')
  const [spo2, setSpo2] = useState('')
  const [rr, setRr] = useState('')
  
  // Anthropometry
  const [height, setHeight] = useState('')
  const [weight, setWeight] = useState('')
  const [bmi, setBmi] = useState('')
  const [waistCirc, setWaistCirc] = useState('')
  const [hipCirc, setHipCirc] = useState('')
  
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<DiagnosisResult | null>(null)
  const [treatmentPlan, setTreatmentPlan] = useState<any | null>(null)
  const [prescriptionPlan, setPrescriptionPlan] = useState<any | null>(null)

  // Live diagnosis state
  const [liveDiagnosis, setLiveDiagnosis] = useState<LiveDiagnosisResponse | null>(null)
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const debounceTimerRef = useRef<number | null>(null)

  // Format Live Differential Diagnosis report as plain text
  const formatLiveDiagnosisReport = (): string => {
    if (!liveDiagnosis) return 'No differential diagnosis available.'
    const lines: string[] = []
    lines.push('AI Differential Diagnosis Report')
    lines.push(`Generated: ${new Date().toLocaleString()}`)
    lines.push('')
    if (liveDiagnosis.clinical_summary) {
      lines.push('Clinical Summary:')
      lines.push(liveDiagnosis.clinical_summary)
      lines.push('')
    }
    lines.push(`Data Completeness: ${Math.round((liveDiagnosis.data_completeness || 0) * 100)}%`)
    lines.push('')
    const vitals: string[] = []
    if (bp) vitals.push(`BP: ${bp}`)
    if (hr) vitals.push(`HR: ${hr}`)
    if (temp) vitals.push(`Temp: ${temp}`)
    if (spo2) vitals.push(`SpO2: ${spo2}`)
    if (rr) vitals.push(`RR: ${rr}`)
    if (vitals.length) {
      lines.push('Vital Signs:')
      lines.push(vitals.join(', '))
      lines.push('')
    }
    if (labResults) {
      lines.push('Laboratory Results:')
      lines.push(labResults)
      lines.push('')
    }
    if (radiologyResults) {
      lines.push('Radiology Findings:')
      lines.push(radiologyResults)
      lines.push('')
    }
    if (liveDiagnosis.differential_diagnoses?.length) {
      lines.push('Differential Diagnoses:')
      liveDiagnosis.differential_diagnoses.forEach((d, idx) => {
        lines.push(`${idx + 1}. ${d.name} (ICD: ${d.icd_code})`)
        lines.push(`   Confidence: ${Math.round((d.confidence || 0) * 100)}%`)
        if (d.supporting_findings?.length) {
          lines.push(`   Supporting: ${d.supporting_findings.join(', ')}`)
        }
        if (d.interpretation) {
          lines.push(`   Interpretation: ${d.interpretation}`)
        }
        if (d.next_steps?.length) {
          lines.push(`   Next steps: ${d.next_steps.join('; ')}`)
        }
      })
    }
    return lines.join('\n')
  }

  // Download TXT file for live differential diagnosis
  const handleDownloadTxt = () => {
    const content = formatLiveDiagnosisReport()
    const blob = new Blob([content], { type: 'text/plain;charset=utf-8' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    const ts = new Date().toISOString().replace(/[:.]/g, '-')
    link.download = `differential_diagnosis_${ts}.txt`
    document.body.appendChild(link)
    link.click()
    link.remove()
    URL.revokeObjectURL(url)
  }

  // Print (Save as PDF) using browser print dialog
  const handlePrintPdf = () => {
    const content = formatLiveDiagnosisReport()
    const w = window.open('', '_blank', 'noopener,noreferrer')
    if (!w) return
    const safeContent = content
      .split('\n')
      .map(line => line || '&nbsp;')
      .join('<br/>')
    w.document.write(`
      <html>
        <head>
          <title>Differential Diagnosis Report</title>
          <style>
            body { font-family: Arial, sans-serif; margin: 24px; color: #111; }
            h1 { font-size: 20px; margin: 0 0 12px 0; }
            .meta { color: #555; margin-bottom: 16px; }
            .content { white-space: pre-wrap; line-height: 1.4; font-size: 13px; }
            @media print { button { display: none; } }
          </style>
        </head>
        <body>
          <h1>AI Differential Diagnosis Report</h1>
          <div class="meta">Generated: ${new Date().toLocaleString()}</div>
          <div class="content">${safeContent}</div>
          <button onclick="window.print()" style="margin-top:16px;padding:8px 12px;">Print / Save as PDF</button>
        </body>
      </html>
    `)
    w.document.close()
    w.focus()
  }

  // Export Final Diagnosis Results (if present)
  const formatFinalDiagnosisReport = (): string => {
    if (!result) return 'No final diagnosis available.'
    const lines: string[] = []
    lines.push('Final Diagnosis Results')
    lines.push(`Generated: ${new Date().toLocaleString()}`)
    lines.push('')
    lines.push(`Primary Diagnosis: ${result.diagnosis}`)
    lines.push(`ICD-10: ${result.icd_code}`)
    lines.push(`Confidence: ${result.confidence}`)
    lines.push('')
    if (result.supporting_evidence?.length) {
      lines.push('Supporting Evidence:')
      result.supporting_evidence.forEach((e) => lines.push(`• ${e}`))
      lines.push('')
    }
    if (result.recommended_tests?.length) {
      lines.push('Recommended Tests:')
      result.recommended_tests.forEach((t) => lines.push(`• ${t}`))
      lines.push('')
    }
    if (result.differential_diagnoses?.length) {
      lines.push('Differential Diagnoses:')
      result.differential_diagnoses.forEach((d, i) => lines.push(`${i + 1}. ${d}`))
    }
    return lines.join('\n')
  }

  const downloadFinalTxt = () => {
    const content = formatFinalDiagnosisReport()
    const blob = new Blob([content], { type: 'text/plain;charset=utf-8' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    const ts = new Date().toISOString().replace(/[:.]/g, '-')
    link.download = `final_diagnosis_${ts}.txt`
    document.body.appendChild(link)
    link.click()
    link.remove()
    URL.revokeObjectURL(url)
  }

  const printFinalPdf = () => {
    const content = formatFinalDiagnosisReport()
    const w = window.open('', '_blank', 'noopener,noreferrer')
    if (!w) return
    const safeContent = content
      .split('\n')
      .map(line => line || '&nbsp;')
      .join('<br/>')
    w.document.write(`
      <html>
        <head>
          <title>Final Diagnosis</title>
          <style>
            body { font-family: Arial, sans-serif; margin: 24px; color: #111; }
            h1 { font-size: 20px; margin: 0 0 12px 0; }
            .meta { color: #555; margin-bottom: 16px; }
            .content { white-space: pre-wrap; line-height: 1.4; font-size: 13px; }
            @media print { button { display: none; } }
          </style>
        </head>
        <body>
          <h1>Final Diagnosis Results</h1>
          <div class="meta">Generated: ${new Date().toLocaleString()}</div>
          <div class="content">${safeContent}</div>
          <button onclick="window.print()" style="margin-top:16px;padding:8px 12px;">Print / Save as PDF</button>
        </body>
      </html>
    `)
    w.document.close()
    w.focus()
  }

  const handleSuggestTreatment = async () => {
    try {
      const vitals: any = {}
      if (bp) vitals.BP = bp
      if (hr) vitals.HR = hr
      if (temp) vitals.TEMP = temp
      if (spo2) vitals.SPO2 = spo2
      if (rr) vitals.RR = rr
      const patient_info = {
        vitals,
        anthropometry: { height, weight, bmi, waistCirc, hipCirc },
        lab_results: labResults,
        radiology: radiologyResults,
        history: { pastHistory, surgicalHistory, socialHistory, personalHistory },
      }
      const primaryDx = result?.diagnosis || liveDiagnosis?.differential_diagnoses?.[0]?.name || 'Undetermined'
      const resp = await axios.post('/api/medical/treatment-plan', {
        diagnosis: primaryDx,
        patient_info,
        allergies: [],
      })
      setTreatmentPlan(resp.data)
    } catch (e) {
      console.error('Treatment generation failed', e)
    }
  }

  const handleGeneratePrescription = async () => {
    try {
      const currentMeds: string[] = []
      const patient_info = {
        age: undefined,
        sex: undefined,
        conditions: [...pastHistory],
        vitals: { BP: bp, HR: hr, TEMP: temp, SPO2: spo2, RR: rr },
        labs_text: labResults,
        radiology_text: radiologyResults,
      }
      const diagnosisName = result?.diagnosis || liveDiagnosis?.differential_diagnoses?.[0]?.name || 'Undetermined'
      const resp = await axios.post('/api/prescription/generate-plan', {
        diagnosis: diagnosisName,
        patient_info,
        allergies: [],
        current_medications: currentMeds,
      })
      setPrescriptionPlan(resp.data)
    } catch (e) {
      console.error('Prescription generation failed', e)
    }
  }

  // ===== Export/Print: Treatment Plan =====
  const formatTreatmentPlanReport = (): string => {
    if (!treatmentPlan) return 'No treatment plan available.'
    const primaryDx = result?.diagnosis || liveDiagnosis?.differential_diagnoses?.[0]?.name || 'Undetermined'
    const lines: string[] = []
    lines.push('AI Treatment Plan')
    lines.push(`Generated: ${new Date().toLocaleString()}`)
    lines.push('')
    lines.push(`Diagnosis: ${primaryDx}`)
    lines.push('')
    const plan: any = treatmentPlan.plan || treatmentPlan
    const pushSection = (title: string, value: any) => {
      if (!value || (Array.isArray(value) && value.length === 0)) return
      lines.push(title + ':')
      if (Array.isArray(value)) {
        value.forEach((v: any) => lines.push(`• ${typeof v === 'string' ? v : JSON.stringify(v)}`))
      } else if (typeof value === 'object') {
        Object.entries(value).forEach(([k, v]: [string, any]) => {
          if (Array.isArray(v)) {
            lines.push(`- ${k}:`)
            v.forEach((vv: any) => lines.push(`  • ${typeof vv === 'string' ? vv : JSON.stringify(vv)}`))
          } else {
            lines.push(`- ${k}: ${typeof v === 'string' ? v : JSON.stringify(v)}`)
          }
        })
      } else {
        lines.push(String(value))
      }
      lines.push('')
    }
    pushSection('First-line', plan.first_line || plan.firstLine)
    pushSection('Alternatives', plan.alternatives)
    pushSection('Adjuncts', plan.adjuncts)
    pushSection('Non-pharmacologic', plan.non_pharmacologic || plan.nonPharmacologic)
    pushSection('Duration', plan.duration)
    pushSection('Follow-up', plan.follow_up || plan.followUp)
    pushSection('Monitoring', plan.monitoring)
    pushSection('Patient Education', plan.patient_education || plan.education)
    if (plan.notes) {
      pushSection('Notes', plan.notes)
    }
    if (lines.length <= 6) {
      // Fallback: dump JSON when unknown structure
      lines.push(JSON.stringify(treatmentPlan, null, 2))
    }
    return lines.join('\n')
  }

  const downloadTreatmentTxt = () => {
    const content = formatTreatmentPlanReport()
    const blob = new Blob([content], { type: 'text/plain;charset=utf-8' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    const ts = new Date().toISOString().replace(/[:.]/g, '-')
    link.download = `treatment_plan_${ts}.txt`
    document.body.appendChild(link)
    link.click()
    link.remove()
    URL.revokeObjectURL(url)
  }

  const printTreatmentPdf = () => {
    const content = formatTreatmentPlanReport()
    const w = window.open('', '_blank', 'noopener,noreferrer')
    if (!w) return
    const safeContent = content
      .split('\n')
      .map(line => line || '&nbsp;')
      .join('<br/>')
    w.document.write(`
      <html>
        <head>
          <title>Treatment Plan</title>
          <style>
            body { font-family: Arial, sans-serif; margin: 24px; color: #111; }
            h1 { font-size: 20px; margin: 0 0 12px 0; }
            .meta { color: #555; margin-bottom: 16px; }
            .content { white-space: pre-wrap; line-height: 1.4; font-size: 13px; }
            @media print { button { display: none; } }
          </style>
        </head>
        <body>
          <h1>AI Treatment Plan</h1>
          <div class="meta">Generated: ${new Date().toLocaleString()}</div>
          <div class="content">${safeContent}</div>
          <button onclick="window.print()" style="margin-top:16px;padding:8px 12px;">Print / Save as PDF</button>
        </body>
      </html>
    `)
    w.document.close()
    w.focus()
  }

  // ===== Export/Print: Prescription Plan =====
  const formatPrescriptionPlanReport = (): string => {
    if (!prescriptionPlan) return 'No prescription plan available.'
    const primaryDx = result?.diagnosis || liveDiagnosis?.differential_diagnoses?.[0]?.name || 'Undetermined'
    const lines: string[] = []
    lines.push('AI Prescription Plan')
    lines.push(`Generated: ${new Date().toLocaleString()}`)
    lines.push('')
    lines.push(`Diagnosis: ${primaryDx}`)
    lines.push('')
    const pp: any = prescriptionPlan
    const writeArray = (title: string, arr: any[]) => {
      if (!Array.isArray(arr) || arr.length === 0) return
      lines.push(title + ':')
      arr.forEach((item: any) => {
        if (typeof item === 'string') lines.push(`• ${item}`)
        else if (item && typeof item === 'object') {
          const med = item.medication || item.name
          const dose = item.dose || item.dosing || item.sig
          const note = item.note || item.notes
          const parts = [med, dose, note].filter(Boolean)
          if (parts.length) lines.push(`• ${parts.join(' — ')}`)
          else lines.push(`• ${JSON.stringify(item)}`)
        } else {
          lines.push(`• ${String(item)}`)
        }
      })
      lines.push('')
    }
    writeArray('Medications', pp.medications)
    writeArray('Contraindications', pp.contraindications)
    writeArray('Interactions', pp.interaction_warnings || pp.interactions)
    writeArray('Side Effects', pp.side_effects)
    writeArray('Monitoring', pp.monitoring_advice || pp.monitoring)
    if (pp.instructions) writeArray('Instructions', Array.isArray(pp.instructions) ? pp.instructions : [pp.instructions])
    if (lines.length <= 6) {
      lines.push(JSON.stringify(prescriptionPlan, null, 2))
    }
    return lines.join('\n')
  }

  const downloadPrescriptionTxt = () => {
    const content = formatPrescriptionPlanReport()
    const blob = new Blob([content], { type: 'text/plain;charset=utf-8' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    const ts = new Date().toISOString().replace(/[:.]/g, '-')
    link.download = `prescription_plan_${ts}.txt`
    document.body.appendChild(link)
    link.click()
    link.remove()
    URL.revokeObjectURL(url)
  }

  const printPrescriptionPdf = () => {
    const content = formatPrescriptionPlanReport()
    const w = window.open('', '_blank', 'noopener,noreferrer')
    if (!w) return
    const safeContent = content
      .split('\n')
      .map(line => line || '&nbsp;')
      .join('<br/>')
    w.document.write(`
      <html>
        <head>
          <title>Prescription Plan</title>
          <style>
            body { font-family: Arial, sans-serif; margin: 24px; color: #111; }
            h1 { font-size: 20px; margin: 0 0 12px 0; }
            .meta { color: #555; margin-bottom: 16px; }
            .content { white-space: pre-wrap; line-height: 1.4; font-size: 13px; }
            @media print { button { display: none; } }
          </style>
        </head>
        <body>
          <h1>AI Prescription Plan</h1>
          <div class="meta">Generated: ${new Date().toLocaleString()}</div>
          <div class="content">${safeContent}</div>
          <button onclick="window.print()" style="margin-top:16px;padding:8px 12px;">Print / Save as PDF</button>
        </body>
      </html>
    `)
    w.document.close()
    w.focus()
  }

  // Handle patient selection from patient intake
  const handlePatientSelection = async (patient: any) => {
    try {
      // Load full patient data
      const patientData = await getPatientIntake(patient.intake_id)
      
      // Populate basic demographics
      const nameParts = patientData.name.split(' ')
      setFirstName(nameParts[0] || '')
      setLastName(nameParts.slice(1).join(' ') || '')
      setAge(patientData.age)
      setSex(patientData.gender === 'male' ? 'Male' : patientData.gender === 'female' ? 'Female' : 'Other')
      setUhid(patientData.intake_id)
      
      // Store patient reference
      setSelectedPatientId(patientData.intake_id)
      setSelectedPatientRisk(patient.risk_level || null)
      
      // Populate family history if available
      if (patientData.familyHistory && patientData.familyHistory.length > 0) {
        const familyConditions = patientData.familyHistory.map(fh => 
          `${fh.relationship}: ${fh.condition}${fh.ageOfOnset ? ` (age ${fh.ageOfOnset})` : ''}`
        )
        setPastHistory(prev => [...prev, ...familyConditions])
      }
      
      // Populate travel history as social history
      if (patientData.travelHistory && patientData.travelHistory.length > 0) {
        const travelInfo = patientData.travelHistory.map(th => 
          `Recent travel to ${th.destination} (${th.departureDate} to ${th.returnDate})`
        )
        setSocialHistory(prev => [...prev, ...travelInfo])
      }
      
      // Show success message
      alert(`Patient data loaded: ${patientData.name}`)
    } catch (error) {
      console.error('Failed to load patient data:', error)
      alert('Failed to load patient data. Please try again.')
    }
  }

  const handleGenerateDiagnosisReport = async () => {
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
        complaints: complaints.filter(c => c.complaint),
        vitals: {
          temperature: temp,
          pulse: hr,
          bp,
          rr,
          spo2,
        },
        differential_diagnoses: liveDiagnosis.differential_diagnoses.map(d => ({
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
      downloadPDF(blob, `diagnosis_report_${firstName || 'patient'}_${new Date().toISOString().split('T')[0]}.pdf`)
    } catch (error) {
      console.error('Error generating report:', error)
      alert('Failed to generate report. Please try again.')
    } finally {
      setGeneratingReport(false)
    }
  }

  const handleGenerateCombinedReport = async () => {
    if (!selectedPatientId) {
      alert('No patient linked. Please load a patient first.')
      return
    }
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
        complaints: complaints.filter(c => c.complaint),
        vitals: {
          temperature: temp,
          pulse: hr,
          bp,
          rr,
          spo2,
        },
        differential_diagnoses: liveDiagnosis.differential_diagnoses.map(d => ({
          name: d.diagnosis || d.disease_name,
          confidence: d.confidence || 0,
          icd_code: d.icd_code,
          supporting_findings: d.supporting_evidence || [],
        })),
        recommended_tests: liveDiagnosis.recommended_tests || [],
        clinical_summary: liveDiagnosis.clinical_summary,
        primary_diagnosis: liveDiagnosis.differential_diagnoses[0]?.diagnosis || liveDiagnosis.differential_diagnoses[0]?.disease_name,
      }

      const blob = await generateCombinedReport(selectedPatientId, reportData)
      downloadPDF(blob, `combined_report_${selectedPatientId}.pdf`)
    } catch (error) {
      console.error('Error generating combined report:', error)
      alert('Failed to generate combined report. Please try again.')
    } finally {
      setGeneratingReport(false)
    }
  }

  const addComplaint = () => {
    setComplaints([...complaints, {complaint: '', duration: ''}])
  }

  const updateComplaint = (index: number, field: 'complaint' | 'duration', value: string) => {
    const newComplaints = [...complaints]
    newComplaints[index][field] = value
    setComplaints(newComplaints)
  }

  const removeComplaint = (index: number) => {
    if (complaints.length > 1) {
      setComplaints(complaints.filter((_, i) => i !== index))
      // Remove associated HPI details
      const newHpiDetails = {...hpiDetails}
      delete newHpiDetails[index]
      setHpiDetails(newHpiDetails)
    }
  }

  // Get template for complaint type
  const getComplaintTemplate = (complaint: string) => {
    const key = complaint.toLowerCase()
    for (const templateKey in complaintTemplates) {
      if (key.includes(templateKey)) {
        return complaintTemplates[templateKey]
      }
    }
    return null
  }

  // Toggle selection in HPI details
  const toggleHpiDetail = (complaintIndex: number, category: 'pattern' | 'associated' | 'characteristics', value: string) => {
    const current = hpiDetails[complaintIndex] || {pattern: [], associated: [], characteristics: []}
    const categoryArray = current[category]
    
    const newArray = categoryArray.includes(value)
      ? categoryArray.filter(item => item !== value)
      : [...categoryArray, value]
    
    setHpiDetails({
      ...hpiDetails,
      [complaintIndex]: {
        ...current,
        [category]: newArray
      }
    })
  }

  // Toggle history selections
  const toggleHistory = (category: 'past' | 'surgical' | 'social', value: string) => {
    const setter = category === 'past' ? setPastHistory : 
                   category === 'surgical' ? setSurgicalHistory : 
                   setSocialHistory
    const current = category === 'past' ? pastHistory : 
                    category === 'surgical' ? surgicalHistory : 
                    socialHistory
    
    if (current.includes(value)) {
      setter(current.filter(item => item !== value))
    } else {
      setter([...current, value])
    }
  }

  // Toggle clinical findings
  const toggleClinicalFinding = (system: string, finding: string) => {
    const current = clinicalFindings[system] || []
    const newFindings = current.includes(finding)
      ? current.filter(item => item !== finding)
      : [...current, finding]
    
    setClinicalFindings({
      ...clinicalFindings,
      [system]: newFindings
    })
  }

  // Toggle laboratory findings
  const toggleLabFinding = (category: string, test: string) => {
    const current = labFindings[category] || []
    const newTests = current.includes(test)
      ? current.filter(item => item !== test)
      : [...current, test]
    
    setLabFindings({
      ...labFindings,
      [category]: newTests
    })
  }

  // Toggle radiology findings
  const toggleRadiologyFinding = (category: string, study: string) => {
    const current = radiologyFindings[category] || []
    const newStudies = current.includes(study)
      ? current.filter(item => item !== study)
      : [...current, study]
    
    setRadiologyFindings({
      ...radiologyFindings,
      [category]: newStudies
    })
  }

  // Quick insert buttons for personal history
  const insertPersonalHistory = (text: string) => {
    setPersonalHistory(prev => prev ? `${prev}, ${text}` : text)
  }

  // Live diagnosis with debouncing
  const fetchLiveDiagnosis = useCallback(async () => {
    // Only fetch if we have at least one complaint
    if (complaints.every(c => !c.complaint.trim())) {
      setLiveDiagnosis(null)
      return
    }

    setIsAnalyzing(true)
    try {
      // Prepare data
      const vitalSignsObj: any = {}
      if (bp) vitalSignsObj.BP = bp
      if (hr) vitalSignsObj.HR = hr
      if (temp) vitalSignsObj.TEMP = temp
      if (spo2) vitalSignsObj.SPO2 = spo2
      if (rr) vitalSignsObj.RR = rr

      const anthropometry: any = {}
      if (height) anthropometry.height = height
      if (weight) anthropometry.weight = weight
      if (bmi) anthropometry.bmi = bmi
      if (waistCirc) anthropometry.waist = waistCirc
      if (hipCirc) anthropometry.hip = hipCirc

      // Build history strings
      const fullHistory = [
        hpi && `HPI: ${hpi}`,
        ...complaints.map((c, idx) => {
          const details = hpiDetails[idx]
          if (!details || (!details.pattern.length && !details.associated.length && !details.characteristics.length)) {
            return null
          }
          return `${c.complaint} (${c.duration}): ${[
            details.pattern.length && `Pattern: ${details.pattern.join(', ')}`,
            details.characteristics.length && `Characteristics: ${details.characteristics.join(', ')}`,
            details.associated.length && `Associated: ${details.associated.join(', ')}`
          ].filter(Boolean).join('; ')}`
        }).filter(Boolean),
        pastHistory.length && `Past History: ${pastHistory.join(', ')}`,
        surgicalHistory.length && `Surgical History: ${surgicalHistory.join(', ')}`,
        socialHistory.length && `Social History: ${socialHistory.join(', ')}`,
        personalHistory && `Personal History: ${personalHistory}`
      ].filter(Boolean).join('\\n')

      const clinicalExam = Object.entries(clinicalFindings)
        .filter(([_, findings]) => findings.length > 0)
        .map(([system, findings]) => `${system.toUpperCase()}: ${findings.join(', ')}`)
        .join('\\n')

      const labTests = Object.entries(labFindings)
        .filter(([_, tests]) => tests.length > 0)
        .map(([category, tests]) => `${category.toUpperCase()}: ${tests.join(', ')}`)
        .join('\\n')
      const combinedLabResults = [labTests, labResults].filter(Boolean).join('\\n')

      const radiologyStudies = Object.entries(radiologyFindings)
        .filter(([_, studies]) => studies.length > 0)
        .map(([category, studies]) => `${category.toUpperCase()}: ${studies.join(', ')}`)
        .join('\\n')
      const combinedRadiologyResults = [radiologyStudies, radiologyResults].filter(Boolean).join('\\n')

      const response = await axios.post('/api/medical/live-diagnosis', {
        patient: {
          first_name: firstName,
          last_name: lastName,
          age: age ? parseInt(age) : null,
          sex: sex,
          address: address,
          uhid: uhid
        },
        complaints: complaints.filter(c => c.complaint.trim()),
        hpi: hpi,
        past_history: fullHistory,
        clinical_examination: clinicalExam,
        laboratory_investigations: combinedLabResults,
        radiology_findings: combinedRadiologyResults,
        vital_signs: vitalSignsObj,
        anthropometry: anthropometry,
      })

      setLiveDiagnosis(response.data)
    } catch (error) {
      console.error('Failed to fetch live diagnosis:', error)
    } finally {
      setIsAnalyzing(false)
    }
  }, [complaints, hpi, hpiDetails, pastHistory, surgicalHistory, socialHistory, personalHistory, 
      clinicalFindings, labFindings, labResults, radiologyFindings, radiologyResults,
      bp, hr, temp, spo2, rr, height, weight, bmi, waistCirc, hipCirc])

  // Debounced live diagnosis trigger
  // Auto-load patient from URL parameter
  useEffect(() => {
    const params = new URLSearchParams(window.location.search)
    const patientId = params.get('patientId')
    
    if (patientId && !selectedPatientId) {
      // Load patient data automatically
      getPatientIntake(patientId)
        .then(patientData => {
          const nameParts = patientData.name.split(' ')
          setFirstName(nameParts[0] || '')
          setLastName(nameParts.slice(1).join(' ') || '')
          setAge(patientData.age)
          setSex(patientData.gender === 'male' ? 'Male' : patientData.gender === 'female' ? 'Female' : 'Other')
          setUhid(patientData.intake_id)
          setSelectedPatientId(patientData.intake_id)
          
          // Populate histories
          if (patientData.familyHistory && patientData.familyHistory.length > 0) {
            const familyConditions = patientData.familyHistory.map(fh => 
              `${fh.relationship}: ${fh.condition}${fh.ageOfOnset ? ` (age ${fh.ageOfOnset})` : ''}`
            )
            setPastHistory(familyConditions)
          }
          
          if (patientData.travelHistory && patientData.travelHistory.length > 0) {
            const travelInfo = patientData.travelHistory.map(th => 
              `Recent travel to ${th.destination} (${th.departureDate} to ${th.returnDate})`
            )
            setSocialHistory(travelInfo)
          }
        })
        .catch(err => {
          console.error('Failed to auto-load patient:', err)
        })
    }
  }, [])

  useEffect(() => {
    if (debounceTimerRef.current) {
      clearTimeout(debounceTimerRef.current)
    }

    debounceTimerRef.current = setTimeout(() => {
      fetchLiveDiagnosis()
    }, 1500) // 1.5 second debounce

    return () => {
      if (debounceTimerRef.current) {
        clearTimeout(debounceTimerRef.current)
      }
    }
  }, [fetchLiveDiagnosis])



  const handleDiagnosis = async () => {
    if (complaints.every(c => !c.complaint.trim())) return

    setLoading(true)
    try {
      // Construct vital signs object
      const vitalSignsObj: any = {}
      if (bp) vitalSignsObj.BP = bp
      if (hr) vitalSignsObj.HR = hr
      if (temp) vitalSignsObj.TEMP = temp
      if (spo2) vitalSignsObj.SPO2 = spo2
      if (rr) vitalSignsObj.RR = rr
      
      // Construct anthropometry object
      const anthropometry: any = {}
      if (height) anthropometry.height = height
      if (weight) anthropometry.weight = weight
      if (bmi) anthropometry.bmi = bmi
      if (waistCirc) anthropometry.waist = waistCirc
      if (hipCirc) anthropometry.hip = hipCirc
      
      // Combine all history sections
      const fullHistory = [
        hpi && `HPI: ${hpi}`,
        // Add structured HPI details from templates
        ...complaints.map((c, idx) => {
          const details = hpiDetails[idx]
          if (!details || (!details.pattern.length && !details.associated.length && !details.characteristics.length)) {
            return null
          }
          return `${c.complaint} (${c.duration}): ${[
            details.pattern.length && `Pattern: ${details.pattern.join(', ')}`,
            details.characteristics.length && `Characteristics: ${details.characteristics.join(', ')}`,
            details.associated.length && `Associated: ${details.associated.join(', ')}`
          ].filter(Boolean).join('; ')}`
        }).filter(Boolean),
        pastHistory.length && `Past History: ${pastHistory.join(', ')}`,
        surgicalHistory.length && `Surgical History: ${surgicalHistory.join(', ')}`,
        socialHistory.length && `Social History: ${socialHistory.join(', ')}`,
        personalHistory && `Personal History: ${personalHistory}`,
      ].filter(Boolean).join('\n\n')
      
      // Construct clinical examination findings
      const clinicalExam = Object.entries(clinicalFindings)
        .filter(([_, findings]) => findings.length > 0)
        .map(([system, findings]) => `${system.toUpperCase()}: ${findings.join(', ')}`)
        .join('\n')
      
      // Construct laboratory findings
      const labTests = Object.entries(labFindings)
        .filter(([_, tests]) => tests.length > 0)
        .map(([category, tests]) => `${category.toUpperCase()}: ${tests.join(', ')}`)
        .join('\n')
      const combinedLabResults = [labTests, labResults].filter(Boolean).join('\n')
      
      // Construct radiology findings
      const radiologyStudies = Object.entries(radiologyFindings)
        .filter(([_, studies]) => studies.length > 0)
        .map(([category, studies]) => `${category.toUpperCase()}: ${studies.join(', ')}`)
        .join('\n')
      const combinedRadiologyResults = [radiologyStudies, radiologyResults].filter(Boolean).join('\n')
      
      const response = await axios.post('/api/medical/diagnosis', {
        complaints: complaints.filter(c => c.complaint.trim()),
        symptoms: symptoms.split('\n').filter(s => s.trim()),
        patient_history: fullHistory || patientHistory,
        clinical_examination: clinicalExam,
        laboratory_investigations: combinedLabResults,
        radiology_findings: combinedRadiologyResults,
        vital_signs: vitalSignsObj,
        anthropometry: anthropometry,
      })

      setResult(response.data)
    } catch (error) {
      console.error('Failed to get diagnosis:', error)
    } finally {
      setLoading(false)
    }
  }

  // AI-Powered Lab PDF Upload Handler
  const handleLabPdfUpload = async (file: File | null) => {
    if (!file) return
    
    setLabPdfFile(file)
    setLabPdfUploading(true)
    setLabPdfInsights(null)
    
    try {
      const formData = new FormData()
      formData.append('file', file)
      formData.append('type', 'laboratory')
      
      const response = await axios.post('/api/medical/analyze-report-pdf', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      })
      
      const insights = response.data
      setLabPdfInsights(insights)
      
      // Auto-populate lab results with extracted data
      if (insights.extracted_values) {
        setLabResults((prev) => {
          const newValue = prev ? `${prev}\n\n[AI Extracted]\n${insights.extracted_values}` : `[AI Extracted]\n${insights.extracted_values}`
          return newValue
        })
      }
      
      // Auto-select abnormal tests in lab findings
      if (insights.abnormal_tests && Array.isArray(insights.abnormal_tests)) {
        insights.abnormal_tests.forEach((test: string) => {
          // Match test name to lab categories and auto-select
          Object.entries(labInvestigations).forEach(([category, data]: [string, any]) => {
            if (data.tests.some((t: string) => t.toLowerCase().includes(test.toLowerCase()) || test.toLowerCase().includes(t.toLowerCase()))) {
              setLabFindings((prev) => ({
                ...prev,
                [category]: [...new Set([...(prev[category as keyof typeof prev] || []), test])],
              }))
            }
          })
        })
      }
      
    } catch (error) {
      console.error('Failed to analyze lab PDF:', error)
      alert('Failed to analyze lab report. Please try again or enter values manually.')
    } finally {
      setLabPdfUploading(false)
    }
  }

  // AI-Powered Radiology PDF Upload Handler
  const handleRadiologyPdfUpload = async (file: File | null) => {
    if (!file) return
    
    setRadiologyPdfFile(file)
    setRadiologyPdfUploading(true)
    setRadiologyPdfInsights(null)
    
    try {
      const formData = new FormData()
      formData.append('file', file)
      formData.append('type', 'radiology')
      
      const response = await axios.post('/api/medical/analyze-report-pdf', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      })
      
      const insights = response.data
      setRadiologyPdfInsights(insights)
      
      // Auto-populate radiology results with extracted findings
      if (insights.extracted_findings) {
        setRadiologyResults((prev) => {
          const newValue = prev ? `${prev}\n\n[AI Extracted]\n${insights.extracted_findings}` : `[AI Extracted]\n${insights.extracted_findings}`
          return newValue
        })
      }
      
      // Auto-select radiology studies based on modality detection
      if (insights.modality) {
        const modalityLower = insights.modality.toLowerCase()
        Object.entries(radiologyInvestigations).forEach(([category, data]: [string, any]) => {
          if (category.toLowerCase().includes(modalityLower) || modalityLower.includes(category.toLowerCase())) {
            // Add common study from this modality
            if (data.studies.length > 0) {
              setRadiologyFindings((prev) => ({
                ...prev,
                [category]: [...new Set([...(prev[category as keyof typeof prev] || []), data.studies[0]])],
              }))
            }
          }
        })
      }
      
    } catch (error) {
      console.error('Failed to analyze radiology PDF:', error)
      alert('Failed to analyze radiology report. Please try again or enter findings manually.')
    } finally {
      setRadiologyPdfUploading(false)
    }
  }

  return (
    <Box>
      <Typography variant="h4" gutterBottom fontWeight={600}>
        AI Differential Diagnosis
      </Typography>
      <Typography variant="body1" color="text.secondary" paragraph>
        Enter patient symptoms and information for AI-powered diagnostic assistance with real-time analysis
      </Typography>



      <Grid container spacing={3}>
        {/* Left Side - Patient Data Input (60%) */}
        <Grid item xs={12} md={7}>
          <Paper elevation={3} sx={{ p: 3, maxHeight: '85vh', overflow: 'auto' }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
              <Typography variant="h6">
                Patient Information
              </Typography>
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
                action={
                  selectedPatientRisk && <RiskBadge level={selectedPatientRisk} size="small" />
                }
              >
                <strong>Linked Patient:</strong> {selectedPatientId}
              </Alert>
            )}
            
            {/* Patient Demographics Section */}
            <Box sx={{ 
              mb: 3, 
              p: 2, 
              borderRadius: 2, 
              background: 'linear-gradient(135deg, #667eea10 0%, #764ba210 100%)',
              border: '1px solid #667eea30'
            }}>
              <Typography variant="subtitle1" fontWeight={600} gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Box sx={{ fontSize: '20px' }}>👤</Box>
                Patient Demographics
              </Typography>
              <Grid container spacing={2}>
                <Grid item xs={6}>
                  <TextField
                    fullWidth
                    label="First Name"
                    value={firstName}
                    onChange={(e) => setFirstName(e.target.value)}
                    placeholder="Enter first name"
                    size="small"
                  />
                </Grid>
                <Grid item xs={6}>
                  <TextField
                    fullWidth
                    label="Last Name"
                    value={lastName}
                    onChange={(e) => setLastName(e.target.value)}
                    placeholder="Enter last name"
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
                    placeholder="Years"
                    size="small"
                  />
                </Grid>
                <Grid item xs={4}>
                  <FormControl fullWidth size="small">
                    <InputLabel id="sex-label">Sex</InputLabel>
                    <Select
                      labelId="sex-label"
                      id="sex"
                      label="Sex"
                      value={sex}
                      onChange={(e) => setSex(e.target.value as string)}
                    >
                      <MenuItem value=""><em>None</em></MenuItem>
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
                    placeholder="Hospital ID"
                    size="small"
                  />
                </Grid>
                <Grid item xs={12}>
                  <TextField
                    fullWidth
                    label="Address"
                    value={address}
                    onChange={(e) => setAddress(e.target.value)}
                    placeholder="Enter address"
                    size="small"
                    multiline
                    rows={2}
                  />
                </Grid>
              </Grid>
            </Box>
            
            {/* Chief Complaints with Duration */}
            <Box sx={{ 
              mb: 3, 
              p: 2, 
              borderRadius: 2, 
              background: 'linear-gradient(135deg, #667eea15 0%, #764ba215 100%)',
              border: '2px solid #667eea40'
            }}>
              <Typography variant="subtitle1" fontWeight={600} gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Box sx={{ fontSize: '24px' }}>🩺</Box>
                Chief Complaints - Quick Select
              </Typography>
              
              {/* Quick Select Common Complaints */}
              <Box sx={{ mb: 2, p: 2, bgcolor: 'white', borderRadius: 2, boxShadow: 1 }}>
                <Typography variant="caption" color="primary" fontWeight={600} gutterBottom sx={{ display: 'block' }}>
                  ⚡ Click to add common complaints:
                </Typography>
                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mt: 1 }}>
                  {['Fever', 'Pain', 'Headache', 'Cough', 'Breathlessness', 'Vomiting', 'Diarrhea', 'Weakness', 
                    'Chest pain', 'Abdominal pain', 'Joint pain', 'Back pain', 'Dizziness', 'Nausea', 
                    'Fatigue', 'Loss of appetite', 'Weight loss', 'Palpitations', 'Swelling'].map(complaint => (
                    <Chip
                      key={complaint}
                      label={complaint}
                      size="medium"
                      onClick={() => {
                        const lastIndex = complaints.length - 1
                        if (complaints[lastIndex].complaint === '') {
                          updateComplaint(lastIndex, 'complaint', complaint)
                        } else {
                          setComplaints([...complaints, {complaint: complaint, duration: ''}])
                        }
                      }}
                      sx={{
                        fontWeight: 600,
                        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                        color: 'white',
                        '&:hover': {
                          background: 'linear-gradient(135deg, #5568d3 0%, #6a3f8f 100%)',
                          transform: 'scale(1.05)',
                          boxShadow: '0 4px 12px rgba(102, 126, 234, 0.4)',
                        },
                        transition: 'all 0.2s',
                      }}
                    />
                  ))}
                </Box>
              </Box>
            </Box>

            {complaints.map((item, index) => {
              const template = getComplaintTemplate(item.complaint)
              return (
                <Box key={index} sx={{ mb: 2, p: 2, border: '1px solid #e0e0e0', borderRadius: 1 }}>
                  <Grid container spacing={1} sx={{ mb: 1 }}>
                    <Grid item xs={7}>
                      <TextField
                        fullWidth
                        label={`Complaint ${index + 1}`}
                        value={item.complaint}
                        onChange={(e) => updateComplaint(index, 'complaint', e.target.value)}
                        placeholder="e.g., Fever, Headache, Pain"
                        size="small"
                      />
                    </Grid>
                    <Grid item xs={4}>
                      <TextField
                        fullWidth
                        label="Duration"
                        value={item.duration}
                        onChange={(e) => updateComplaint(index, 'duration', e.target.value)}
                        placeholder="e.g., 3 days"
                        size="small"
                      />
                    </Grid>
                    <Grid item xs={1} sx={{ display: 'flex', alignItems: 'center' }}>
                      {complaints.length > 1 && (
                        <Button size="small" color="error" onClick={() => removeComplaint(index)}>×</Button>
                      )}
                    </Grid>
                  </Grid>

                  {/* Show template-based options if complaint matches */}
                  {template && item.complaint && (
                    <Box sx={{ mt: 2 }}>
                      <Typography variant="caption" fontWeight={600} color="primary">
                        Quick Select Details:
                      </Typography>
                      
                      {/* Pattern/Nature */}
                      <Box sx={{ mt: 1 }}>
                        <Typography variant="caption" color="text.secondary">Pattern:</Typography>
                        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5, mt: 0.5 }}>
                          {template.patterns.map(pattern => (
                            <Chip
                              key={pattern}
                              label={pattern}
                              size="small"
                              onClick={() => toggleHpiDetail(index, 'pattern', pattern)}
                              color={hpiDetails[index]?.pattern.includes(pattern) ? 'primary' : 'default'}
                              variant={hpiDetails[index]?.pattern.includes(pattern) ? 'filled' : 'outlined'}
                            />
                          ))}
                        </Box>
                      </Box>

                      {/* Characteristics */}
                      <Box sx={{ mt: 1 }}>
                        <Typography variant="caption" color="text.secondary">Characteristics:</Typography>
                        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5, mt: 0.5 }}>
                          {template.characteristics.map(char => (
                            <Chip
                              key={char}
                              label={char}
                              size="small"
                              onClick={() => toggleHpiDetail(index, 'characteristics', char)}
                              color={hpiDetails[index]?.characteristics.includes(char) ? 'secondary' : 'default'}
                              variant={hpiDetails[index]?.characteristics.includes(char) ? 'filled' : 'outlined'}
                            />
                          ))}
                        </Box>
                      </Box>

                      {/* Associated Factors */}
                      <Box sx={{ mt: 1 }}>
                        <Typography variant="caption" color="text.secondary">Associated Factors:</Typography>
                        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5, mt: 0.5 }}>
                          {template.associatedFactors.map(factor => (
                            <Chip
                              key={factor}
                              label={factor}
                              size="small"
                              onClick={() => toggleHpiDetail(index, 'associated', factor)}
                              color={hpiDetails[index]?.associated.includes(factor) ? 'success' : 'default'}
                              variant={hpiDetails[index]?.associated.includes(factor) ? 'filled' : 'outlined'}
                            />
                          ))}
                        </Box>
                      </Box>
                    </Box>
                  )}
                </Box>
              )
            })}
            <Button size="small" onClick={addComplaint} sx={{ mb: 2 }}>+ Add Complaint</Button>

            {/* History of Presenting Illness */}
            <Accordion sx={{ mb: 1 }}>
              <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                <Typography fontWeight={600}>History of Presenting Illness</Typography>
              </AccordionSummary>
              <AccordionDetails>
                <TextField
                  fullWidth
                  multiline
                  rows={4}
                  value={hpi}
                  onChange={(e) => setHpi(e.target.value)}
                  placeholder="Describe onset, progression, associated symptoms, relieving/aggravating factors..."
                />
              </AccordionDetails>
            </Accordion>

            {/* Past Medical History */}
            <Accordion sx={{ mb: 1 }}>
              <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                <Typography fontWeight={600}>Past Medical History</Typography>
              </AccordionSummary>
              <AccordionDetails>
                <Typography variant="caption" color="text.secondary" gutterBottom>Quick Select:</Typography>
                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5, mb: 2 }}>
                  {pastHistoryOptions.map(option => (
                    <Chip
                      key={option}
                      label={option}
                      size="small"
                      onClick={() => toggleHistory('past', option)}
                      color={pastHistory.includes(option) ? 'primary' : 'default'}
                      variant={pastHistory.includes(option) ? 'filled' : 'outlined'}
                    />
                  ))}
                </Box>
                <TextField
                  fullWidth
                  multiline
                  rows={2}
                  value={pastHistory.join(', ')}
                  onChange={(e) => setPastHistory(e.target.value.split(',').map(s => s.trim()).filter(Boolean))}
                  placeholder="Or type custom history..."
                />
              </AccordionDetails>
            </Accordion>

            {/* Surgical History */}
            <Accordion sx={{ mb: 1 }}>
              <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                <Typography fontWeight={600}>Surgical History</Typography>
              </AccordionSummary>
              <AccordionDetails>
                <Typography variant="caption" color="text.secondary" gutterBottom>Quick Select:</Typography>
                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5, mb: 2 }}>
                  {surgicalHistoryOptions.map(option => (
                    <Chip
                      key={option}
                      label={option}
                      size="small"
                      onClick={() => toggleHistory('surgical', option)}
                      color={surgicalHistory.includes(option) ? 'secondary' : 'default'}
                      variant={surgicalHistory.includes(option) ? 'filled' : 'outlined'}
                    />
                  ))}
                </Box>
                <TextField
                  fullWidth
                  multiline
                  rows={2}
                  value={surgicalHistory.join(', ')}
                  onChange={(e) => setSurgicalHistory(e.target.value.split(',').map(s => s.trim()).filter(Boolean))}
                  placeholder="Or type custom surgical history with dates..."
                />
              </AccordionDetails>
            </Accordion>

            {/* Social History */}
            <Accordion sx={{ mb: 1 }}>
              <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                <Typography fontWeight={600}>Social History</Typography>
              </AccordionSummary>
              <AccordionDetails>
                <Typography variant="caption" color="text.secondary" gutterBottom>Quick Select:</Typography>
                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5, mb: 2 }}>
                  {socialHistoryOptions.map(option => (
                    <Chip
                      key={option}
                      label={option}
                      size="small"
                      onClick={() => toggleHistory('social', option)}
                      color={socialHistory.includes(option) ? 'success' : 'default'}
                      variant={socialHistory.includes(option) ? 'filled' : 'outlined'}
                    />
                  ))}
                </Box>
                <TextField
                  fullWidth
                  multiline
                  rows={2}
                  value={socialHistory.join(', ')}
                  onChange={(e) => setSocialHistory(e.target.value.split(',').map(s => s.trim()).filter(Boolean))}
                  placeholder="Or type custom social history..."
                />
              </AccordionDetails>
            </Accordion>

            {/* Personal History with Quick Options */}
            <Accordion sx={{ mb: 2 }}>
              <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                <Typography fontWeight={600}>Personal History</Typography>
              </AccordionSummary>
              <AccordionDetails>
                <Box sx={{ mb: 2 }}>
                  <Typography variant="caption" color="text.secondary" gutterBottom>Quick Add:</Typography>
                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5, mb: 1 }}>
                    <Button size="small" variant="outlined" onClick={() => insertPersonalHistory('Non-smoker')}>Non-smoker</Button>
                    <Button size="small" variant="outlined" onClick={() => insertPersonalHistory('Smoker')}>Smoker</Button>
                    <Button size="small" variant="outlined" onClick={() => insertPersonalHistory('Ex-smoker')}>Ex-smoker</Button>
                  </Box>
                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5, mb: 1 }}>
                    <Button size="small" variant="outlined" onClick={() => insertPersonalHistory('Non-alcoholic')}>Non-alcoholic</Button>
                    <Button size="small" variant="outlined" onClick={() => insertPersonalHistory('Social drinker')}>Social drinker</Button>
                    <Button size="small" variant="outlined" onClick={() => insertPersonalHistory('Alcoholic')}>Alcoholic</Button>
                  </Box>
                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                    <Button size="small" variant="outlined" onClick={() => insertPersonalHistory('Vegetarian')}>Vegetarian</Button>
                    <Button size="small" variant="outlined" onClick={() => insertPersonalHistory('Non-vegetarian')}>Non-vegetarian</Button>
                    <Button size="small" variant="outlined" onClick={() => insertPersonalHistory('Married')}>Married</Button>
                    <Button size="small" variant="outlined" onClick={() => insertPersonalHistory('Single')}>Single</Button>
                  </Box>
                </Box>
                <TextField
                  fullWidth
                  multiline
                  rows={3}
                  value={personalHistory}
                  onChange={(e) => setPersonalHistory(e.target.value)}
                  placeholder="Smoking, alcohol, diet, marital status..."
                />
              </AccordionDetails>
            </Accordion>

            <TextField
              fullWidth
              label="Additional Symptoms (optional)"
              multiline
              rows={3}
              value={symptoms}
              onChange={(e) => setSymptoms(e.target.value)}
              placeholder="Additional symptoms not in chief complaints..."
              sx={{ mb: 2 }}
            />
            
            <Typography variant="subtitle1" fontWeight={600} gutterBottom sx={{ mt: 2 }}>
              Vital Signs
            </Typography>
            <Grid container spacing={2} sx={{ mb: 2 }}>
              <Grid item xs={6}>
                <TextField
                  fullWidth
                  label="Blood Pressure"
                  value={bp}
                  onChange={(e) => setBp(e.target.value)}
                  placeholder="120/80"
                  size="small"
                />
              </Grid>
              <Grid item xs={6}>
                <TextField
                  fullWidth
                  label="Heart Rate (bpm)"
                  value={hr}
                  onChange={(e) => setHr(e.target.value)}
                  placeholder="72"
                  size="small"
                />
              </Grid>
              <Grid item xs={6}>
                <TextField
                  fullWidth
                  label="Temperature (°F)"
                  value={temp}
                  onChange={(e) => setTemp(e.target.value)}
                  placeholder="98.6"
                  size="small"
                />
              </Grid>
              <Grid item xs={6}>
                <TextField
                  fullWidth
                  label="SpO2 (%)"
                  value={spo2}
                  onChange={(e) => setSpo2(e.target.value)}
                  placeholder="98"
                  size="small"
                />
              </Grid>
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Respiratory Rate (breaths/min)"
                  value={rr}
                  onChange={(e) => setRr(e.target.value)}
                  placeholder="16"
                  size="small"
                />
              </Grid>
            </Grid>
            
            <Typography variant="subtitle1" fontWeight={600} gutterBottom sx={{ mt: 2 }}>
              Anthropometry (Optional)
            </Typography>
            <Grid container spacing={2} sx={{ mb: 2 }}>
              <Grid item xs={6}>
                <TextField
                  fullWidth
                  label="Height (cm)"
                  value={height}
                  onChange={(e) => setHeight(e.target.value)}
                  placeholder="170"
                  size="small"
                />
              </Grid>
              <Grid item xs={6}>
                <TextField
                  fullWidth
                  label="Weight (kg)"
                  value={weight}
                  onChange={(e) => setWeight(e.target.value)}
                  placeholder="70"
                  size="small"
                />
              </Grid>
              <Grid item xs={4}>
                <TextField
                  fullWidth
                  label="BMI"
                  value={bmi}
                  onChange={(e) => setBmi(e.target.value)}
                  placeholder="24.2"
                  size="small"
                />
              </Grid>
              <Grid item xs={4}>
                <TextField
                  fullWidth
                  label="Waist (cm)"
                  value={waistCirc}
                  onChange={(e) => setWaistCirc(e.target.value)}
                  placeholder="85"
                  size="small"
                />
              </Grid>
              <Grid item xs={4}>
                <TextField
                  fullWidth
                  label="Hip (cm)"
                  value={hipCirc}
                  onChange={(e) => setHipCirc(e.target.value)}
                  placeholder="95"
                  size="small"
                />
              </Grid>
            </Grid>
            
            {/* Clinical Examination - Head to Toe */}
            <Accordion sx={{ mb: 2, mt: 2 }}>
              <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                <Typography fontWeight={600} color="primary">🔍 Clinical Examination (Head to Toe)</Typography>
              </AccordionSummary>
              <AccordionDetails>
                {/* General Examination */}
                <Box sx={{ mb: 2 }}>
                  <Typography variant="subtitle2" fontWeight={600} gutterBottom>General Examination</Typography>
                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                    {clinicalExamTemplates.general.findings.map(finding => (
                      <Chip
                        key={finding}
                        label={finding}
                        size="small"
                        onClick={() => toggleClinicalFinding('general', finding)}
                        color={clinicalFindings.general?.includes(finding) ? 'primary' : 'default'}
                        variant={clinicalFindings.general?.includes(finding) ? 'filled' : 'outlined'}
                      />
                    ))}
                  </Box>
                </Box>

                {/* Head */}
                <Box sx={{ mb: 2 }}>
                  <Typography variant="subtitle2" fontWeight={600} gutterBottom>Head</Typography>
                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                    {clinicalExamTemplates.head.findings.map(finding => (
                      <Chip
                        key={finding}
                        label={finding}
                        size="small"
                        onClick={() => toggleClinicalFinding('head', finding)}
                        color={clinicalFindings.head?.includes(finding) ? 'primary' : 'default'}
                        variant={clinicalFindings.head?.includes(finding) ? 'filled' : 'outlined'}
                      />
                    ))}
                  </Box>
                </Box>

                {/* Eyes */}
                <Box sx={{ mb: 2 }}>
                  <Typography variant="subtitle2" fontWeight={600} gutterBottom>Eyes</Typography>
                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                    {clinicalExamTemplates.eyes.findings.map(finding => (
                      <Chip
                        key={finding}
                        label={finding}
                        size="small"
                        onClick={() => toggleClinicalFinding('eyes', finding)}
                        color={clinicalFindings.eyes?.includes(finding) ? 'primary' : 'default'}
                        variant={clinicalFindings.eyes?.includes(finding) ? 'filled' : 'outlined'}
                      />
                    ))}
                  </Box>
                </Box>

                {/* ENT */}
                <Box sx={{ mb: 2 }}>
                  <Typography variant="subtitle2" fontWeight={600} gutterBottom>ENT</Typography>
                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                    {clinicalExamTemplates.ent.findings.map(finding => (
                      <Chip
                        key={finding}
                        label={finding}
                        size="small"
                        onClick={() => toggleClinicalFinding('ent', finding)}
                        color={clinicalFindings.ent?.includes(finding) ? 'primary' : 'default'}
                        variant={clinicalFindings.ent?.includes(finding) ? 'filled' : 'outlined'}
                      />
                    ))}
                  </Box>
                </Box>

                {/* Neck */}
                <Box sx={{ mb: 2 }}>
                  <Typography variant="subtitle2" fontWeight={600} gutterBottom>Neck</Typography>
                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                    {clinicalExamTemplates.neck.findings.map(finding => (
                      <Chip
                        key={finding}
                        label={finding}
                        size="small"
                        onClick={() => toggleClinicalFinding('neck', finding)}
                        color={clinicalFindings.neck?.includes(finding) ? 'primary' : 'default'}
                        variant={clinicalFindings.neck?.includes(finding) ? 'filled' : 'outlined'}
                      />
                    ))}
                  </Box>
                </Box>

                {/* Respiratory System */}
                <Box sx={{ mb: 2 }}>
                  <Typography variant="subtitle2" fontWeight={600} gutterBottom>Respiratory System (Chest)</Typography>
                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                    {clinicalExamTemplates.chest.findings.map(finding => (
                      <Chip
                        key={finding}
                        label={finding}
                        size="small"
                        onClick={() => toggleClinicalFinding('chest', finding)}
                        color={clinicalFindings.chest?.includes(finding) ? 'primary' : 'default'}
                        variant={clinicalFindings.chest?.includes(finding) ? 'filled' : 'outlined'}
                      />
                    ))}
                  </Box>
                </Box>

                {/* Cardiovascular System */}
                <Box sx={{ mb: 2 }}>
                  <Typography variant="subtitle2" fontWeight={600} gutterBottom>Cardiovascular System</Typography>
                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                    {clinicalExamTemplates.cvs.findings.map(finding => (
                      <Chip
                        key={finding}
                        label={finding}
                        size="small"
                        onClick={() => toggleClinicalFinding('cvs', finding)}
                        color={clinicalFindings.cvs?.includes(finding) ? 'primary' : 'default'}
                        variant={clinicalFindings.cvs?.includes(finding) ? 'filled' : 'outlined'}
                      />
                    ))}
                  </Box>
                </Box>

                {/* Abdomen */}
                <Box sx={{ mb: 2 }}>
                  <Typography variant="subtitle2" fontWeight={600} gutterBottom>Abdomen</Typography>
                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                    {clinicalExamTemplates.abdomen.findings.map(finding => (
                      <Chip
                        key={finding}
                        label={finding}
                        size="small"
                        onClick={() => toggleClinicalFinding('abdomen', finding)}
                        color={clinicalFindings.abdomen?.includes(finding) ? 'primary' : 'default'}
                        variant={clinicalFindings.abdomen?.includes(finding) ? 'filled' : 'outlined'}
                      />
                    ))}
                  </Box>
                </Box>

                {/* Genitourinary */}
                <Box sx={{ mb: 2 }}>
                  <Typography variant="subtitle2" fontWeight={600} gutterBottom>Genitourinary System</Typography>
                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                    {clinicalExamTemplates.genitourinary.findings.map(finding => (
                      <Chip
                        key={finding}
                        label={finding}
                        size="small"
                        onClick={() => toggleClinicalFinding('genitourinary', finding)}
                        color={clinicalFindings.genitourinary?.includes(finding) ? 'primary' : 'default'}
                        variant={clinicalFindings.genitourinary?.includes(finding) ? 'filled' : 'outlined'}
                      />
                    ))}
                  </Box>
                </Box>

                {/* Musculoskeletal */}
                <Box sx={{ mb: 2 }}>
                  <Typography variant="subtitle2" fontWeight={600} gutterBottom>Musculoskeletal System</Typography>
                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                    {clinicalExamTemplates.musculoskeletal.findings.map(finding => (
                      <Chip
                        key={finding}
                        label={finding}
                        size="small"
                        onClick={() => toggleClinicalFinding('musculoskeletal', finding)}
                        color={clinicalFindings.musculoskeletal?.includes(finding) ? 'primary' : 'default'}
                        variant={clinicalFindings.musculoskeletal?.includes(finding) ? 'filled' : 'outlined'}
                      />
                    ))}
                  </Box>
                </Box>

                {/* Neurological */}
                <Box sx={{ mb: 2 }}>
                  <Typography variant="subtitle2" fontWeight={600} gutterBottom>Neurological System</Typography>
                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                    {clinicalExamTemplates.neurological.findings.map(finding => (
                      <Chip
                        key={finding}
                        label={finding}
                        size="small"
                        onClick={() => toggleClinicalFinding('neurological', finding)}
                        color={clinicalFindings.neurological?.includes(finding) ? 'primary' : 'default'}
                        variant={clinicalFindings.neurological?.includes(finding) ? 'filled' : 'outlined'}
                      />
                    ))}
                  </Box>
                </Box>

                {/* Skin */}
                <Box sx={{ mb: 2 }}>
                  <Typography variant="subtitle2" fontWeight={600} gutterBottom>Skin</Typography>
                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                    {clinicalExamTemplates.skin.findings.map(finding => (
                      <Chip
                        key={finding}
                        label={finding}
                        size="small"
                        onClick={() => toggleClinicalFinding('skin', finding)}
                        color={clinicalFindings.skin?.includes(finding) ? 'primary' : 'default'}
                        variant={clinicalFindings.skin?.includes(finding) ? 'filled' : 'outlined'}
                      />
                    ))}
                  </Box>
                </Box>
              </AccordionDetails>
            </Accordion>

            {/* Laboratory Investigations */}
            <Accordion sx={{ mb: 2, mt: 2 }}>
              <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                <Typography variant="subtitle1" fontWeight={600} color="success.main">
                  🧪 Laboratory Investigations
                </Typography>
              </AccordionSummary>
              <AccordionDetails>
                {/* Hematology */}
                <Box sx={{ mb: 2 }}>
                  <Typography variant="subtitle2" fontWeight={600} gutterBottom>Hematology</Typography>
                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                    {labInvestigations.hematology.tests.map(test => (
                      <Chip
                        key={test}
                        label={test}
                        size="small"
                        onClick={() => toggleLabFinding('hematology', test)}
                        color={labFindings.hematology?.includes(test) ? 'success' : 'default'}
                        variant={labFindings.hematology?.includes(test) ? 'filled' : 'outlined'}
                      />
                    ))}
                  </Box>
                </Box>

                {/* Biochemistry */}
                <Box sx={{ mb: 2 }}>
                  <Typography variant="subtitle2" fontWeight={600} gutterBottom>Biochemistry</Typography>
                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                    {labInvestigations.biochemistry.tests.map(test => (
                      <Chip
                        key={test}
                        label={test}
                        size="small"
                        onClick={() => toggleLabFinding('biochemistry', test)}
                        color={labFindings.biochemistry?.includes(test) ? 'success' : 'default'}
                        variant={labFindings.biochemistry?.includes(test) ? 'filled' : 'outlined'}
                      />
                    ))}
                  </Box>
                </Box>

                {/* Serology */}
                <Box sx={{ mb: 2 }}>
                  <Typography variant="subtitle2" fontWeight={600} gutterBottom>Serology & Immunology</Typography>
                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                    {labInvestigations.serology.tests.map(test => (
                      <Chip
                        key={test}
                        label={test}
                        size="small"
                        onClick={() => toggleLabFinding('serology', test)}
                        color={labFindings.serology?.includes(test) ? 'success' : 'default'}
                        variant={labFindings.serology?.includes(test) ? 'filled' : 'outlined'}
                      />
                    ))}
                  </Box>
                </Box>

                {/* Microbiology */}
                <Box sx={{ mb: 2 }}>
                  <Typography variant="subtitle2" fontWeight={600} gutterBottom>Microbiology</Typography>
                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                    {labInvestigations.microbiology.tests.map(test => (
                      <Chip
                        key={test}
                        label={test}
                        size="small"
                        onClick={() => toggleLabFinding('microbiology', test)}
                        color={labFindings.microbiology?.includes(test) ? 'success' : 'default'}
                        variant={labFindings.microbiology?.includes(test) ? 'filled' : 'outlined'}
                      />
                    ))}
                  </Box>
                </Box>

                {/* Urine Tests */}
                <Box sx={{ mb: 2 }}>
                  <Typography variant="subtitle2" fontWeight={600} gutterBottom>Urine Examination</Typography>
                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                    {labInvestigations.urine.tests.map(test => (
                      <Chip
                        key={test}
                        label={test}
                        size="small"
                        onClick={() => toggleLabFinding('urine', test)}
                        color={labFindings.urine?.includes(test) ? 'success' : 'default'}
                        variant={labFindings.urine?.includes(test) ? 'filled' : 'outlined'}
                      />
                    ))}
                  </Box>
                </Box>

                {/* Stool Tests */}
                <Box sx={{ mb: 2 }}>
                  <Typography variant="subtitle2" fontWeight={600} gutterBottom>Stool Examination</Typography>
                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                    {labInvestigations.stool.tests.map(test => (
                      <Chip
                        key={test}
                        label={test}
                        size="small"
                        onClick={() => toggleLabFinding('stool', test)}
                        color={labFindings.stool?.includes(test) ? 'success' : 'default'}
                        variant={labFindings.stool?.includes(test) ? 'filled' : 'outlined'}
                      />
                    ))}
                  </Box>
                </Box>

                {/* Other Tests */}
                <Box sx={{ mb: 2 }}>
                  <Typography variant="subtitle2" fontWeight={600} gutterBottom>Other Investigations</Typography>
                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                    {labInvestigations.other.tests.map(test => (
                      <Chip
                        key={test}
                        label={test}
                        size="small"
                        onClick={() => toggleLabFinding('other', test)}
                        color={labFindings.other?.includes(test) ? 'success' : 'default'}
                        variant={labFindings.other?.includes(test) ? 'filled' : 'outlined'}
                      />
                    ))}
                  </Box>
                </Box>

                {/* Lab PDF Upload Section */}
                <Box sx={{ 
                  mt: 2, 
                  p: 2.5, 
                  borderRadius: 3,
                  background: 'linear-gradient(135deg, #667eea15 0%, #764ba215 100%)',
                  border: '2px dashed rgba(102, 126, 234, 0.4)',
                }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <AutoAwesomeIcon sx={{ color: '#667eea' }} />
                      <Typography variant="subtitle2" fontWeight={700} color="primary">
                        🤖 AI-Powered Lab Report Upload
                      </Typography>
                    </Box>
                    {labPdfFile && (
                      <Chip
                        label={labPdfFile.name}
                        size="small"
                        onDelete={() => {
                          setLabPdfFile(null)
                          setLabPdfInsights(null)
                        }}
                        icon={<PictureAsPdfIcon />}
                        color="success"
                      />
                    )}
                  </Box>
                  
                  <input
                    accept="application/pdf"
                    hidden
                    id="lab-pdf-upload"
                    type="file"
                    onChange={(e) => handleLabPdfUpload(e.target.files?.[0] || null)}
                  />
                  <label htmlFor="lab-pdf-upload">
                    <Button
                      variant="contained"
                      component="span"
                      fullWidth
                      startIcon={labPdfUploading ? <CircularProgress size={20} color="inherit" /> : <UploadFileIcon />}
                      disabled={labPdfUploading}
                      sx={{
                        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                        color: 'white',
                        fontWeight: 600,
                        py: 1.5,
                        '&:hover': {
                          background: 'linear-gradient(135deg, #5568d3 0%, #6a3f8f 100%)',
                          transform: 'scale(1.02)',
                        },
                        transition: 'all 0.2s',
                      }}
                    >
                      {labPdfUploading ? 'Analyzing with AI...' : 'Upload Lab Report PDF (AI Auto-Extract)'}
                    </Button>
                  </label>
                  
                  {labPdfInsights && (
                    <Box sx={{ mt: 2 }}>
                      <Alert 
                        severity="success" 
                        icon={<InsightsIcon />}
                        sx={{ 
                          mb: 2,
                          background: 'linear-gradient(135deg, #4caf5015 0%, #8bc34a15 100%)',
                          border: '1px solid #4caf50',
                        }}
                      >
                        <Typography variant="caption" fontWeight={700}>AI Extracted Lab Values:</Typography>
                        <Typography variant="body2" sx={{ mt: 0.5, fontFamily: 'monospace' }}>
                          {labPdfInsights.extracted_values}
                        </Typography>
                      </Alert>
                      
                      {labPdfInsights.insights && (
                        <Alert 
                          severity="info" 
                          icon={<PsychologyIcon />}
                          sx={{
                            background: 'linear-gradient(135deg, #2196f315 0%, #03a9f415 100%)',
                            border: '1px solid #2196f3',
                          }}
                        >
                          <Typography variant="caption" fontWeight={700}>AI Clinical Insights:</Typography>
                          <Typography variant="body2" sx={{ mt: 0.5 }}>
                            {labPdfInsights.insights}
                          </Typography>
                        </Alert>
                      )}
                      
                      {labPdfInsights.abnormal_findings && labPdfInsights.abnormal_findings.length > 0 && (
                        <Box sx={{ mt: 1.5 }}>
                          <Typography variant="caption" fontWeight={700} color="error" sx={{ display: 'flex', alignItems: 'center', gap: 0.5, mb: 0.5 }}>
                            <WarningIcon fontSize="small" /> Abnormal Findings:
                          </Typography>
                          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                            {labPdfInsights.abnormal_findings.map((finding: string, idx: number) => (
                              <Chip 
                                key={idx} 
                                label={finding} 
                                size="small" 
                                color="error" 
                                variant="outlined"
                              />
                            ))}
                          </Box>
                        </Box>
                      )}
                    </Box>
                  )}
                </Box>

                {/* Lab Results Text Area */}
                <TextField
                  fullWidth
                  label="Lab Results Details (Values, Interpretations)"
                  multiline
                  rows={3}
                  value={labResults}
                  onChange={(e) => setLabResults(e.target.value)}
                  placeholder="e.g., Hb: 10.5 g/dL (Low), WBC: 15,000 (Elevated), CRP: 45 mg/L (Raised)"
                  sx={{ mt: 2 }}
                />
              </AccordionDetails>
            </Accordion>

            {/* Radiological Investigations */}
            <Accordion sx={{ mb: 2 }}>
              <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                <Typography variant="subtitle1" fontWeight={600} color="info.main">
                  📷 Radiological Investigations
                </Typography>
              </AccordionSummary>
              <AccordionDetails>
                {/* X-Ray */}
                <Box sx={{ mb: 2 }}>
                  <Typography variant="subtitle2" fontWeight={600} gutterBottom>X-Ray Studies</Typography>
                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                    {radiologyInvestigations.xray.studies.map(study => (
                      <Chip
                        key={study}
                        label={study}
                        size="small"
                        onClick={() => toggleRadiologyFinding('xray', study)}
                        color={radiologyFindings.xray?.includes(study) ? 'info' : 'default'}
                        variant={radiologyFindings.xray?.includes(study) ? 'filled' : 'outlined'}
                      />
                    ))}
                  </Box>
                </Box>

                {/* Ultrasound */}
                <Box sx={{ mb: 2 }}>
                  <Typography variant="subtitle2" fontWeight={600} gutterBottom>Ultrasound</Typography>
                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                    {radiologyInvestigations.ultrasound.studies.map(study => (
                      <Chip
                        key={study}
                        label={study}
                        size="small"
                        onClick={() => toggleRadiologyFinding('ultrasound', study)}
                        color={radiologyFindings.ultrasound?.includes(study) ? 'info' : 'default'}
                        variant={radiologyFindings.ultrasound?.includes(study) ? 'filled' : 'outlined'}
                      />
                    ))}
                  </Box>
                </Box>

                {/* CT Scan */}
                <Box sx={{ mb: 2 }}>
                  <Typography variant="subtitle2" fontWeight={600} gutterBottom>CT Scan</Typography>
                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                    {radiologyInvestigations.ct.studies.map(study => (
                      <Chip
                        key={study}
                        label={study}
                        size="small"
                        onClick={() => toggleRadiologyFinding('ct', study)}
                        color={radiologyFindings.ct?.includes(study) ? 'info' : 'default'}
                        variant={radiologyFindings.ct?.includes(study) ? 'filled' : 'outlined'}
                      />
                    ))}
                  </Box>
                </Box>

                {/* MRI */}
                <Box sx={{ mb: 2 }}>
                  <Typography variant="subtitle2" fontWeight={600} gutterBottom>MRI</Typography>
                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                    {radiologyInvestigations.mri.studies.map(study => (
                      <Chip
                        key={study}
                        label={study}
                        size="small"
                        onClick={() => toggleRadiologyFinding('mri', study)}
                        color={radiologyFindings.mri?.includes(study) ? 'info' : 'default'}
                        variant={radiologyFindings.mri?.includes(study) ? 'filled' : 'outlined'}
                      />
                    ))}
                  </Box>
                </Box>

                {/* Nuclear Medicine */}
                <Box sx={{ mb: 2 }}>
                  <Typography variant="subtitle2" fontWeight={600} gutterBottom>Nuclear Medicine</Typography>
                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                    {radiologyInvestigations.nuclear.studies.map(study => (
                      <Chip
                        key={study}
                        label={study}
                        size="small"
                        onClick={() => toggleRadiologyFinding('nuclear', study)}
                        color={radiologyFindings.nuclear?.includes(study) ? 'info' : 'default'}
                        variant={radiologyFindings.nuclear?.includes(study) ? 'filled' : 'outlined'}
                      />
                    ))}
                  </Box>
                </Box>

                {/* Interventional Radiology */}
                <Box sx={{ mb: 2 }}>
                  <Typography variant="subtitle2" fontWeight={600} gutterBottom>Interventional & Contrast Studies</Typography>
                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                    {radiologyInvestigations.interventional.studies.map(study => (
                      <Chip
                        key={study}
                        label={study}
                        size="small"
                        onClick={() => toggleRadiologyFinding('interventional', study)}
                        color={radiologyFindings.interventional?.includes(study) ? 'info' : 'default'}
                        variant={radiologyFindings.interventional?.includes(study) ? 'filled' : 'outlined'}
                      />
                    ))}
                  </Box>
                </Box>

                {/* Special Studies */}
                <Box sx={{ mb: 2 }}>
                  <Typography variant="subtitle2" fontWeight={600} gutterBottom>Special Studies</Typography>
                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                    {radiologyInvestigations.special.studies.map(study => (
                      <Chip
                        key={study}
                        label={study}
                        size="small"
                        onClick={() => toggleRadiologyFinding('special', study)}
                        color={radiologyFindings.special?.includes(study) ? 'info' : 'default'}
                        variant={radiologyFindings.special?.includes(study) ? 'filled' : 'outlined'}
                      />
                    ))}
                  </Box>
                </Box>

                {/* Radiology PDF Upload Section */}
                <Box sx={{ 
                  mt: 2, 
                  p: 2.5, 
                  borderRadius: 3,
                  background: 'linear-gradient(135deg, #667eea15 0%, #764ba215 100%)',
                  border: '2px dashed rgba(102, 126, 234, 0.4)',
                }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <AutoAwesomeIcon sx={{ color: '#667eea' }} />
                      <Typography variant="subtitle2" fontWeight={700} color="primary">
                        🤖 AI-Powered Radiology Report Upload
                      </Typography>
                    </Box>
                    {radiologyPdfFile && (
                      <Chip
                        label={radiologyPdfFile.name}
                        size="small"
                        onDelete={() => {
                          setRadiologyPdfFile(null)
                          setRadiologyPdfInsights(null)
                        }}
                        icon={<PictureAsPdfIcon />}
                        color="info"
                      />
                    )}
                  </Box>
                  
                  <input
                    accept="application/pdf"
                    hidden
                    id="radiology-pdf-upload"
                    type="file"
                    onChange={(e) => handleRadiologyPdfUpload(e.target.files?.[0] || null)}
                  />
                  <label htmlFor="radiology-pdf-upload">
                    <Button
                      variant="contained"
                      component="span"
                      fullWidth
                      startIcon={radiologyPdfUploading ? <CircularProgress size={20} color="inherit" /> : <UploadFileIcon />}
                      disabled={radiologyPdfUploading}
                      sx={{
                        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                        color: 'white',
                        fontWeight: 600,
                        py: 1.5,
                        '&:hover': {
                          background: 'linear-gradient(135deg, #5568d3 0%, #6a3f8f 100%)',
                          transform: 'scale(1.02)',
                        },
                        transition: 'all 0.2s',
                      }}
                    >
                      {radiologyPdfUploading ? 'Analyzing with AI...' : 'Upload Radiology Report PDF (AI Auto-Extract)'}
                    </Button>
                  </label>
                  
                  {radiologyPdfInsights && (
                    <Box sx={{ mt: 2 }}>
                      <Alert 
                        severity="info" 
                        icon={<InsightsIcon />}
                        sx={{ 
                          mb: 2,
                          background: 'linear-gradient(135deg, #2196f315 0%, #03a9f415 100%)',
                          border: '1px solid #2196f3',
                        }}
                      >
                        <Typography variant="caption" fontWeight={700}>AI Extracted Findings:</Typography>
                        <Typography variant="body2" sx={{ mt: 0.5, fontFamily: 'monospace' }}>
                          {radiologyPdfInsights.extracted_findings}
                        </Typography>
                      </Alert>
                      
                      {radiologyPdfInsights.insights && (
                        <Alert 
                          severity="info" 
                          icon={<PsychologyIcon />}
                          sx={{
                            background: 'linear-gradient(135deg, #9c27b015 0%, #673ab715 100%)',
                            border: '1px solid #9c27b0',
                          }}
                        >
                          <Typography variant="caption" fontWeight={700}>AI Radiological Insights:</Typography>
                          <Typography variant="body2" sx={{ mt: 0.5 }}>
                            {radiologyPdfInsights.insights}
                          </Typography>
                        </Alert>
                      )}
                      
                      {radiologyPdfInsights.critical_findings && radiologyPdfInsights.critical_findings.length > 0 && (
                        <Box sx={{ mt: 1.5 }}>
                          <Typography variant="caption" fontWeight={700} color="error" sx={{ display: 'flex', alignItems: 'center', gap: 0.5, mb: 0.5 }}>
                            <WarningIcon fontSize="small" /> Critical Findings:
                          </Typography>
                          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                            {radiologyPdfInsights.critical_findings.map((finding: string, idx: number) => (
                              <Chip 
                                key={idx} 
                                label={finding} 
                                size="small" 
                                color="error" 
                                variant="filled"
                              />
                            ))}
                          </Box>
                        </Box>
                      )}
                      
                      {radiologyPdfInsights.impression && (
                        <Box sx={{ mt: 1.5, p: 1.5, bgcolor: '#f5f5f5', borderRadius: 2 }}>
                          <Typography variant="caption" fontWeight={700} color="text.secondary">
                            Impression:
                          </Typography>
                          <Typography variant="body2" sx={{ mt: 0.5 }}>
                            {radiologyPdfInsights.impression}
                          </Typography>
                        </Box>
                      )}
                    </Box>
                  )}
                </Box>

                {/* Radiology Results Text Area */}
                <TextField
                  fullWidth
                  label="Radiology Findings & Impressions"
                  multiline
                  rows={3}
                  value={radiologyResults}
                  onChange={(e) => setRadiologyResults(e.target.value)}
                  placeholder="e.g., Chest X-ray: Bilateral infiltrates, Right lower lobe consolidation. CT Brain: No acute findings."
                  sx={{ mt: 2 }}
                />
              </AccordionDetails>
            </Accordion>
            
            <Button
              fullWidth
              variant="contained"
              size="large"
              startIcon={loading ? <CircularProgress size={20} /> : <SearchIcon />}
              onClick={handleDiagnosis}
              disabled={loading || complaints.every(c => !c.complaint.trim())}
            >
              {loading ? 'Analyzing...' : 'Get Diagnosis'}
            </Button>
          </Paper>
        </Grid>

        {/* Right Side - Live Differential Diagnosis (40%) */}
        <Grid item xs={12} md={5}>
          <Paper elevation={3} sx={{ p: 3, position: 'sticky', top: 20, maxHeight: '85vh', overflow: 'auto' }}>
            <Box display="flex" alignItems="center" justifyContent="space-between" mb={2}>
              <Box display="flex" alignItems="center" gap={1}>
                <PsychologyIcon color="primary" />
                <Typography variant="h6">Live Differential Diagnosis</Typography>
                {isAnalyzing && <CircularProgress size={20} />}
              </Box>
              {selectedPatientId && (
                <Button
                  size="small"
                  variant="outlined"
                  onClick={() => window.open(`/patient-intake/view/${selectedPatientId}`, '_blank')}
                  sx={{ textTransform: 'none' }}
                >
                  View Patient Record
                </Button>
              )}
            </Box>

            {liveDiagnosis && liveDiagnosis.has_sufficient_data && (
              <>
                {/* Patient Demographics Display */}
                {liveDiagnosis.patient && (liveDiagnosis.patient.first_name || liveDiagnosis.patient.last_name || liveDiagnosis.patient.uhid) && (
                  <Paper sx={{ p: 2, mb: 3, background: 'linear-gradient(135deg, #667eea08 0%, #764ba208 100%)', border: '1px solid #667eea20' }}>
                    <Typography variant="subtitle2" fontWeight={600} gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <Box sx={{ fontSize: '18px' }}>👤</Box>
                      Patient Details
                    </Typography>
                    <Grid container spacing={1}>
                      {(liveDiagnosis.patient.first_name || liveDiagnosis.patient.last_name) && (
                        <Grid item xs={6}>
                          <Typography variant="caption" color="text.secondary">Name</Typography>
                          <Typography variant="body2" fontWeight={600}>
                            {[liveDiagnosis.patient.first_name, liveDiagnosis.patient.last_name].filter(Boolean).join(' ')}
                          </Typography>
                        </Grid>
                      )}
                      {liveDiagnosis.patient.age && (
                        <Grid item xs={3}>
                          <Typography variant="caption" color="text.secondary">Age</Typography>
                          <Typography variant="body2" fontWeight={600}>{liveDiagnosis.patient.age} years</Typography>
                        </Grid>
                      )}
                      {liveDiagnosis.patient.sex && (
                        <Grid item xs={3}>
                          <Typography variant="caption" color="text.secondary">Sex</Typography>
                          <Typography variant="body2" fontWeight={600}>{liveDiagnosis.patient.sex}</Typography>
                        </Grid>
                      )}
                      {liveDiagnosis.patient.uhid && (
                        <Grid item xs={6}>
                          <Typography variant="caption" color="text.secondary">UHID</Typography>
                          <Typography variant="body2" fontWeight={600}>{liveDiagnosis.patient.uhid}</Typography>
                        </Grid>
                      )}
                      {liveDiagnosis.patient.address && (
                        <Grid item xs={12}>
                          <Typography variant="caption" color="text.secondary">Address</Typography>
                          <Typography variant="body2">{liveDiagnosis.patient.address}</Typography>
                        </Grid>
                      )}
                    </Grid>
                  </Paper>
                )}

                {/* Data Completeness Indicator */}
                <Box mb={3}>
                  <Typography variant="caption" color="text.secondary" gutterBottom>
                    Data Completeness: {Math.round(liveDiagnosis.data_completeness * 100)}%
                  </Typography>
                  <LinearProgress 
                    variant="determinate" 
                    value={liveDiagnosis.data_completeness * 100}
                    sx={{ 
                      height: 8, 
                      borderRadius: 1,
                      backgroundColor: '#e0e0e0',
                      '& .MuiLinearProgress-bar': {
                        backgroundColor: liveDiagnosis.data_completeness > 0.7 ? '#4caf50' : '#ff9800'
                      }
                    }}
                  />
                </Box>

                {/* Export Actions */}
                <Box display="flex" gap={1} mb={2}>
                  <Button variant="outlined" size="small" startIcon={<DescriptionIcon />} onClick={handleDownloadTxt}>
                    Export TXT
                  </Button>
                  <Button variant="contained" size="small" startIcon={<PictureAsPdfIcon />} onClick={handlePrintPdf}>
                    Print PDF
                  </Button>
                </Box>

                {/* Action Buttons */}
                <Box display="flex" flexDirection="column" gap={1} mb={2}>
                  <Box display="flex" gap={1}>
                    <Button
                      variant="outlined"
                      size="small"
                      startIcon={<DescriptionIcon />}
                      onClick={handleGenerateDiagnosisReport}
                      disabled={generatingReport || !liveDiagnosis.differential_diagnoses?.length}
                      sx={{ flex: 1, textTransform: 'none' }}
                    >
                      {generatingReport ? 'Generating...' : 'Diagnosis Report'}
                    </Button>
                    {selectedPatientId && (
                      <Button
                        variant="contained"
                        size="small"
                        startIcon={<DescriptionIcon />}
                        onClick={handleGenerateCombinedReport}
                        disabled={generatingReport || !liveDiagnosis.differential_diagnoses?.length}
                        sx={{ flex: 1, textTransform: 'none', bgcolor: '#10b981', '&:hover': { bgcolor: '#059669' } }}
                      >
                        {generatingReport ? 'Generating...' : 'Full Report'}
                      </Button>
                    )}
                  </Box>
                  {selectedPatientId && liveDiagnosis.differential_diagnoses?.length > 0 && (
                    <Button
                      variant="contained"
                      size="small"
                      startIcon={<HospitalIcon />}
                      onClick={() => window.open(`/treatment-plan/${selectedPatientId}?diagnosis=${encodeURIComponent(liveDiagnosis.differential_diagnoses[0]?.diagnosis || liveDiagnosis.differential_diagnoses[0]?.disease_name)}&icd=${liveDiagnosis.differential_diagnoses[0]?.icd_code}`, '_blank')}
                      sx={{ textTransform: 'none', bgcolor: '#667eea', '&:hover': { bgcolor: '#5568d3' } }}
                    >
                      Create Treatment Plan
                    </Button>
                  )}
                </Box>

                {/* Clinical Summary */}
                {liveDiagnosis.clinical_summary && (
                  <Alert severity="info" sx={{ mb: 2 }} icon={<ScienceIcon />}>
                    <Typography variant="caption" fontWeight={600}>Clinical Summary:</Typography>
                    <Typography variant="body2">{liveDiagnosis.clinical_summary}</Typography>
                  </Alert>
                )}

                {/* Differential Diagnoses */}
                {liveDiagnosis.differential_diagnoses.length > 0 ? (
                  <Stack spacing={2}>
                    {liveDiagnosis.differential_diagnoses.map((diagnosis, index) => {
                      const confidenceColor = 
                        diagnosis.confidence >= 0.7 ? 'error' :
                        diagnosis.confidence >= 0.6 ? 'warning' :
                        'info'
                      
                      const confidenceLabel = 
                        diagnosis.confidence >= 0.7 ? 'High' :
                        diagnosis.confidence >= 0.6 ? 'Moderate' :
                        'Low'

                      return (
                        <Card 
                          key={index} 
                          elevation={2}
                          sx={{ 
                            border: index === 0 ? '2px solid #1976d2' : 'none',
                            backgroundColor: index === 0 ? '#f5f9ff' : 'white'
                          }}
                        >
                          <CardContent>
                            {/* Diagnosis Name and Rank */}
                            <Box display="flex" alignItems="center" justifyContent="space-between" mb={1}>
                              <Typography variant="h6" fontWeight={600} color="primary">
                                {index + 1}. {diagnosis.name}
                              </Typography>
                              <Chip 
                                label={`${Math.round(diagnosis.confidence * 100)}%`}
                                color={confidenceColor}
                                size="small"
                                icon={<TrendingUpIcon />}
                              />
                            </Box>

                            {/* ICD Code */}
                            <Chip 
                              label={`ICD: ${diagnosis.icd_code}`} 
                              size="small" 
                              variant="outlined"
                              sx={{ mb: 1 }}
                            />
                            <Chip 
                              label={confidenceLabel + ' Confidence'} 
                              size="small" 
                              color={confidenceColor}
                              variant="outlined"
                              sx={{ mb: 1, ml: 0.5 }}
                            />

                            <Divider sx={{ my: 1.5 }} />

                            {/* Supporting Findings */}
                            <Typography variant="subtitle2" fontWeight={600} gutterBottom color="text.secondary">
                              Supporting Findings:
                            </Typography>
                            <Box display="flex" flexWrap="wrap" gap={0.5} mb={1.5}>
                              {diagnosis.supporting_findings.map((finding, idx) => (
                                <Chip 
                                  key={idx} 
                                  label={finding} 
                                  size="small"
                                  color="success"
                                  variant="outlined"
                                />
                              ))}
                            </Box>

                            {/* AI Interpretation */}
                            <Alert severity="success" sx={{ mb: 1.5 }} icon={<PsychologyIcon />}>
                              <Typography variant="caption" fontWeight={600}>AI Interpretation:</Typography>
                              <Typography variant="body2">{diagnosis.interpretation}</Typography>
                            </Alert>

                            {/* Next Steps */}
                            <Typography variant="subtitle2" fontWeight={600} gutterBottom color="text.secondary">
                              Recommended Next Steps:
                            </Typography>
                            <Stack spacing={0.5}>
                              {diagnosis.next_steps.map((step, idx) => (
                                <Box key={idx} display="flex" alignItems="center">
                                  <Typography variant="body2" color="text.secondary">
                                    • {step}
                                  </Typography>
                                </Box>
                              ))}
                            </Stack>
                          </CardContent>
                        </Card>
                      )
                    })}
                  </Stack>
                ) : (
                  <Alert severity="info">
                    <Typography variant="body2">
                      No sufficient data for differential diagnosis yet. Continue entering patient information.
                    </Typography>
                  </Alert>
                )}
              </>
            )}

            {(!liveDiagnosis || !liveDiagnosis.has_sufficient_data) && !isAnalyzing && (
              <Alert severity="info" icon={<PsychologyIcon />}>
                <Typography variant="subtitle2" fontWeight={600} gutterBottom>
                  Waiting for Patient Data
                </Typography>
                <Typography variant="body2">
                  Start entering chief complaints, history, examination findings, and investigations. 
                  The AI will provide real-time differential diagnoses as you add more information.
                </Typography>
              </Alert>
            )}

            {isAnalyzing && !liveDiagnosis && (
              <Box display="flex" flexDirection="column" alignItems="center" py={4}>
                <CircularProgress size={40} sx={{ mb: 2 }} />
                <Typography variant="body2" color="text.secondary">
                  Analyzing patient data...
                </Typography>
              </Box>
            )}
          </Paper>
        </Grid>
      </Grid>

      {/* Final Diagnosis Results (Below both panels) */}
      {result && (
        <Paper elevation={3} sx={{ p: 3, mt: 3 }}>
          <Box display="flex" alignItems="center" gap={1} mb={2}>
            <HospitalIcon color="primary" />
            <Typography variant="h6">Final Diagnosis Results</Typography>
            <Box sx={{ ml: 'auto' }}>
              <Button variant="outlined" size="small" startIcon={<DescriptionIcon />} onClick={downloadFinalTxt} sx={{ mr: 1 }}>
                Export TXT
              </Button>
              <Button variant="contained" size="small" startIcon={<PictureAsPdfIcon />} onClick={printFinalPdf}>
                Print PDF
              </Button>
            </Box>
          </Box>

          <Card sx={{ mb: 2, backgroundColor: '#e3f2fd' }}>
            <CardContent>
              <Typography variant="subtitle2" color="text.secondary">
                Primary Diagnosis
              </Typography>
              <Typography variant="h5" fontWeight={600} gutterBottom>
                {result.diagnosis}
              </Typography>
              <Chip label={`ICD-10: ${result.icd_code}`} color="primary" size="small" />
              <Chip label={`Confidence: ${result.confidence}`} color="success" size="small" sx={{ ml: 1 }} />
            </CardContent>
          </Card>

          <Typography variant="subtitle1" fontWeight={600} gutterBottom>
            Supporting Evidence
          </Typography>
          <Box mb={2}>
            {result.supporting_evidence.map((evidence, index) => (
              <Chip key={index} label={evidence} sx={{ m: 0.5 }} />
            ))}
          </Box>

          <Divider sx={{ my: 2 }} />

          <Typography variant="subtitle1" fontWeight={600} gutterBottom>
            Recommended Tests
              </Typography>
              <Box mb={2}>
                {result.recommended_tests.map((test, index) => (
                  <Typography key={index} variant="body2" sx={{ mb: 0.5 }}>
                    • {test}
                  </Typography>
                ))}
              </Box>

              <Divider sx={{ my: 2 }} />

              <Typography variant="subtitle1" fontWeight={600} gutterBottom>
                Differential Diagnoses
              </Typography>
              {result.differential_diagnoses.map((diff, index) => (
                <Typography key={index} variant="body2" sx={{ mb: 0.5 }}>
                  {index + 1}. {diff}
                </Typography>
              ))}
        </Paper>
      )}

      {/* Treatment & Prescription */}
      <Paper elevation={3} sx={{ p: 3, mt: 3 }}>
        <Box display="flex" alignItems="center" gap={1} mb={2}>
          <PsychologyIcon color="secondary" />
          <Typography variant="h6">Treatment & Prescription</Typography>
        </Box>
        <Box display="flex" gap={1} mb={2}>
          <Button variant="contained" color="success" onClick={handleSuggestTreatment}>Suggest Treatment Plan</Button>
          <Button variant="outlined" color="secondary" onClick={handleGeneratePrescription}>Generate Prescription</Button>
        </Box>
        {treatmentPlan && (
          <Box sx={{ mb: 2 }}>
            <Typography variant="subtitle1" fontWeight={600}>AI Treatment Plan</Typography>
            <Box display="flex" gap={1} mb={1}>
              <Button variant="outlined" size="small" startIcon={<DescriptionIcon />} onClick={downloadTreatmentTxt}>
                Export TXT
              </Button>
              <Button variant="contained" size="small" startIcon={<PictureAsPdfIcon />} onClick={printTreatmentPdf}>
                Print PDF
              </Button>
            </Box>
            <Box component="pre" sx={{ whiteSpace: 'pre-wrap', fontFamily: 'monospace', background:'#fafafa', p:1.5, borderRadius:2 }}>
{JSON.stringify(treatmentPlan, null, 2)}
            </Box>
          </Box>
        )}
        {prescriptionPlan && (
          <Box>
            <Typography variant="subtitle1" fontWeight={600}>AI Prescription</Typography>
            <Box display="flex" gap={1} mb={1}>
              <Button variant="outlined" size="small" startIcon={<DescriptionIcon />} onClick={downloadPrescriptionTxt}>
                Export TXT
              </Button>
              <Button variant="contained" size="small" startIcon={<PictureAsPdfIcon />} onClick={printPrescriptionPdf}>
                Print PDF
              </Button>
            </Box>
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
