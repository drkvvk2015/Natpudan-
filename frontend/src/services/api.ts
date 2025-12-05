import apiClient from './apiClient'
import { AxiosError, AxiosResponse } from 'axios'

// Note: apiClient is imported from ./apiClient and already has:
// - Configured baseURL, timeout, headers
// - Request interceptor that adds Authorization header from localStorage
// - Response interceptor with retry logic
// DO NOT create a duplicate apiClient here!

// API Base URL for fetch calls (not using apiClient)
const API_BASE_URL = import.meta.env.VITE_API_URL || import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';

// API Service Types
export interface HealthStatus {
  status: string
  assistant_status: string
  knowledge_base_status: string
}

export interface DetailedHealthStatus {
  status: string;
  uptime: number;
  cpu_usage: number;
  memory_usage: {
    total: number;
    available: number;
    percent: number;
    used: number;
  };
  disk_usage: {
    total: number;
    used: number;
    free: number;
    percent: number;
  };
  database_status: string;
  cache_status: string;
  assistant_status: string;
  knowledge_base_status: string;
  last_check_in: string;
}

export interface ChatMessage {
  role: 'user' | 'assistant' | 'system'
  content: string
  timestamp?: string
}

export interface DiagnosisRequest {
  complaint: string
  symptoms: string[]
  vitalSigns?: {
    temperature?: number
    bloodPressure?: string
    heartRate?: number
    respiratoryRate?: number
  }
}

export interface DiagnosisResponse {
  diagnosis: string
  confidence: number
  recommendations: string[]
  differentials: string[]
}

export interface DrugCheckRequest {
  drugs: string[]
}

export interface DrugInteraction {
  drug1: string
  drug2: string
  severity: 'minor' | 'moderate' | 'major'
  description: string
}

export interface DrugCheckResponse {
  interactions: DrugInteraction[]
  warnings: string[]
}

export interface KnowledgeDocument {
  id: string
  filename: string
  uploadDate: string
  chunks: number
}

// API Service Functions

/**
 * Health Check
 */
export const checkHealth = async (): Promise<HealthStatus> => {
  const response = await apiClient.get<HealthStatus>('/health')
  return response.data
}

export const checkDetailedHealth = async (): Promise<DetailedHealthStatus> => {
  const response = await apiClient.get<DetailedHealthStatus>('/health/detailed');
  return response.data;
};


export interface Conversation {
  id: number;
  title: string;
  created_at: string;
}

export interface ConversationMessage extends ChatMessage {
  id: number;
  conversation_id: number;
}

export interface ConversationDetails extends Conversation {
  messages: ConversationMessage[];
}

/**
 * Chat API
 */
export const sendChatMessage = async (message: string, conversationId?: number): Promise<{ message: ConversationMessage, conversation_id: number }> => {
  const response = await apiClient.post('/api/chat/message', { message, conversation_id: conversationId });
  return response.data;
}

export const getConversations = async (): Promise<Conversation[]> => {
  const response = await apiClient.get<Conversation[]>('/api/chat/history');
  return response.data;
};

export const getConversationMessages = async (conversationId: number): Promise<ConversationDetails> => {
  const response = await apiClient.get<ConversationDetails>(`/api/chat/history/${conversationId}`);
  return response.data;
};


/**
 * Diagnosis API
 */
export const getDiagnosis = async (request: DiagnosisRequest): Promise<DiagnosisResponse> => {
  const response = await apiClient.post<DiagnosisResponse>('/api/medical/diagnosis', request)
  return response.data
}

export const getLiveDiagnosis = async (symptoms: string): Promise<ReadableStream> => {
  const response = await fetch(`${API_BASE_URL}/api/medical/live-diagnosis`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ symptoms }),
  })

  if (!response.ok) {
    throw new Error(`Diagnosis API error: ${response.statusText}`)
  }

  return response.body!
}

/**
 * Drug Checker API
 */
export const checkDrugInteractions = async (request: DrugCheckRequest): Promise<DrugCheckResponse> => {
  const response = await apiClient.post<DrugCheckResponse>('/api/prescription/drugs/check', request)
  return response.data
}

export const searchDrug = async (query: string): Promise<string[]> => {
  const response = await apiClient.get<string[]>(`/api/prescription/drugs/search`, {
    params: { q: query },
  })
  return response.data
}

/**
 * Knowledge Base API
 */
export const uploadDocument = async (file: File, onProgress?: (progress: number) => void): Promise<void> => {
  const formData = new FormData()
  formData.append('file', file)

  await apiClient.post('/api/upload/pdf', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
    onUploadProgress: (progressEvent) => {
      if (progressEvent.total && onProgress) {
        const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total)
        onProgress(percentCompleted)
      }
    },
  })
}

export const getDocuments = async (): Promise<KnowledgeDocument[]> => {
  const response = await apiClient.get<KnowledgeDocument[]>('/api/upload/documents')
  return response.data
}

export const deleteDocument = async (documentId: string): Promise<void> => {
  await apiClient.delete(`/api/upload/documents/${documentId}`)
}

export const searchKnowledge = async (query: string): Promise<any> => {
  const response = await apiClient.get('/api/medical/knowledge/search', {
    params: { q: query },
  })
  return response.data
}

export const getKnowledgeStats = async (): Promise<any> => {
  const response = await apiClient.get('/api/medical/knowledge/statistics')
  return response.data
}

/**
 * Medical Report Parser API
 */
export interface ParsedMedicalReport {
  vitals: {
    blood_pressure?: string
    heart_rate?: number
    temperature?: number
    respiratory_rate?: number
    oxygen_saturation?: number
    height?: string
    weight?: number
    bmi?: number
  }
  medications: Array<{
    name: string
    dose?: string
    frequency?: string
    route?: string
  }>
  lab_results: Array<{
    test: string
    value: string
    unit?: string
    reference_range?: string
  }>
  diagnoses: Array<{
    description: string
    icd10_code?: string
  }>
  allergies: Array<{
    allergen: string
    reaction?: string
    severity?: string
  }>
}

export const parseMedicalReport = async (file: File): Promise<ParsedMedicalReport> => {
  const formData = new FormData()
  formData.append('file', file)

  const response = await apiClient.post<ParsedMedicalReport>(
    '/api/medical/parse-medical-report',
    formData,
    {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    }
  )
  return response.data
}

/**
 * Patient Intake API
 */
export interface TravelHistoryItem {
  id: string
  destination: string
  departureDate: string
  returnDate: string
  duration: string
  purpose: string
  activities: string[]
}

export interface FamilyHistoryItem {
  id: string
  relationship: string
  condition: string
  ageOfOnset: string
  duration: string
  status: string
  notes: string
}

export interface PatientIntakeData {
  name: string
  age: string
  gender: string
  bloodType: string
  travelHistory: TravelHistoryItem[]
  familyHistory: FamilyHistoryItem[]
  // Extended Anthropometry
  heightCm?: number
  weightKg?: number
  bmi?: number
  waistCm?: number
  hipCm?: number
  whr?: number
  muacCm?: number
  headCircumferenceCm?: number
  chestExpansionCm?: number
  sittingHeightCm?: number
  standingHeightCm?: number
  armSpanCm?: number
  bodyFatPercent?: number
  bpSystolic?: number
  bpDiastolic?: number
  pulsePerMin?: number
  respRatePerMin?: number
  temperatureC?: number
  // Complaints
  chiefComplaints?: Array<{ complaint: string; duration: string }>
  presentHistory?: Array<{
    id: string
    title: string
    duration: string
    associationFactors: string[]
    relievingFactors: string[]
    aggravatingFactors: string[]
  }>
}

export interface PatientIntakeResponse extends PatientIntakeData {
  intake_id: string
  created_at: string
  updated_at: string
}

export const savePatientIntake = async (data: PatientIntakeData): Promise<PatientIntakeResponse> => {
  const response = await apiClient.post<PatientIntakeResponse>('/api/medical/patient-intake', data)
  return response.data
}

export const getPatientIntake = async (intakeId: string): Promise<PatientIntakeResponse> => {
  const response = await apiClient.get<PatientIntakeResponse>(`/api/medical/patient-intake/${intakeId}`)
  return response.data
}

export const updatePatientIntake = async (intakeId: string, data: PatientIntakeData): Promise<PatientIntakeResponse> => {
  const response = await apiClient.put<PatientIntakeResponse>(`/api/medical/patient-intake/${intakeId}`, data)
  return response.data
}

export const listPatientIntakes = async (params?: {
  skip?: number
  limit?: number
  sort_by?: string
  order?: string
}): Promise<{
  patients: Array<PatientIntakeResponse & { travel_history: any[], family_history: any[] }>
  total: number
  skip: number
  limit: number
}> => {
  const queryParams = new URLSearchParams()
  if (params?.skip !== undefined) queryParams.append('skip', params.skip.toString())
  if (params?.limit !== undefined) queryParams.append('limit', params.limit.toString())
  if (params?.sort_by) queryParams.append('sort_by', params.sort_by)
  if (params?.order) queryParams.append('order', params.order)
  
  const response = await apiClient.get(
    `/api/medical/patient-intake?${queryParams.toString()}`
  )
  return response.data
}

// ========================= PDF REPORT GENERATION =========================

export interface DiagnosisReportData {
  patient_name?: string
  age?: number
  sex?: string
  uhid?: string
  complaints?: Array<{ complaint: string; duration: string }>
  vitals?: Record<string, string>
  differential_diagnoses?: Array<{
    name: string
    confidence: number
    icd_code?: string
    supporting_findings?: string[]
  }>
  recommended_tests?: string[]
  clinical_summary?: string
  primary_diagnosis?: string
}

export const generatePatientIntakeReport = async (intakeId: string): Promise<Blob> => {
  const response = await apiClient.get(`/api/medical/reports/patient-intake/${intakeId}`, {
    responseType: 'blob'
  })
  return response.data
}

export const generateDiagnosisReport = async (data: DiagnosisReportData): Promise<Blob> => {
  const response = await apiClient.post('/api/medical/reports/diagnosis', data, {
    responseType: 'blob'
  })
  return response.data
}

export const generateCombinedReport = async (intakeId: string, diagnosisData: DiagnosisReportData): Promise<Blob> => {
  const response = await apiClient.post(`/api/medical/reports/combined/${intakeId}`, diagnosisData, {
    responseType: 'blob'
  })
  return response.data
}

export const downloadPDF = (blob: Blob, filename: string) => {
  const url = window.URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  window.URL.revokeObjectURL(url)
}

// ========================= TREATMENT PLAN MANAGEMENT =========================

export interface MedicationData {
  medication_name: string
  generic_name?: string
  dosage: string
  route?: string
  frequency?: string
  duration_days?: number
  instructions?: string
  precautions?: string
  side_effects?: string
  refills_remaining?: number
}

export interface FollowUpData {
  scheduled_date: string
  appointment_type?: string
  location?: string
  provider?: string
  pre_appointment_instructions?: string
}

export interface TreatmentPlanData {
  patient_intake_id: string
  diagnosis_id?: string
  primary_diagnosis: string
  icd_code?: string
  treatment_goals?: string
  clinical_notes?: string
  created_by?: string
  medications: MedicationData[]
  follow_ups: FollowUpData[]
}

export interface TreatmentPlanResponse {
  id: number
  plan_id: string
  patient_intake_id: string
  diagnosis_id?: string
  primary_diagnosis: string
  icd_code?: string
  treatment_goals?: string
  clinical_notes?: string
  status: string
  start_date: string
  end_date?: string
  last_review_date?: string
  next_review_date?: string
  created_by?: string
  created_at: string
  updated_at: string
  medications: any[]
  follow_ups: any[]
  monitoring_records: any[]
}

export const createTreatmentPlan = async (data: TreatmentPlanData): Promise<TreatmentPlanResponse> => {
  const response = await apiClient.post<TreatmentPlanResponse>('/api/treatment/treatment-plans', data)
  return response.data
}

export const getTreatmentPlansByPatient = async (patientIntakeId: string): Promise<TreatmentPlanResponse[]> => {
  const response = await apiClient.get<TreatmentPlanResponse[]>(`/api/treatment/treatment-plans/patient/${patientIntakeId}`)
  return response.data
}

export const getTreatmentPlan = async (planId: string): Promise<TreatmentPlanResponse> => {
  const response = await apiClient.get<TreatmentPlanResponse>(`/api/treatment/treatment-plans/${planId}`)
  return response.data
}

export const updateTreatmentPlan = async (planId: string, data: Partial<TreatmentPlanData>): Promise<TreatmentPlanResponse> => {
  const response = await apiClient.put<TreatmentPlanResponse>(`/api/treatment/treatment-plans/${planId}`, data)
  return response.data
}

export const addMedication = async (planId: string, medication: MedicationData) => {
  const response = await apiClient.post(`/api/treatment/treatment-plans/${planId}/medications`, medication)
  return response.data
}

export const updateMedication = async (medicationId: number, isActive: boolean, reason?: string) => {
  const response = await apiClient.put(`/api/treatment/medications/${medicationId}`, null, {
    params: { is_active: isActive, discontinuation_reason: reason }
  })
  return response.data
}

export const addFollowUp = async (planId: string, followUp: FollowUpData) => {
  const response = await apiClient.post(`/api/treatment/treatment-plans/${planId}/follow-ups`, followUp)
  return response.data
}

export const updateFollowUp = async (followUpId: number, status?: string, notes?: string, outcome?: string) => {
  const response = await apiClient.put(`/api/treatment/follow-ups/${followUpId}`, null, {
    params: { status, post_appointment_notes: notes, outcome }
  })
  return response.data
}

export const addMonitoringRecord = async (planId: string, record: any) => {
  const response = await apiClient.post(`/api/treatment/treatment-plans/${planId}/monitoring`, record)
  return response.data
}

export const listAllTreatmentPlans = async (params?: { skip?: number; limit?: number; status?: string }) => {
  const queryParams = new URLSearchParams()
  if (params?.skip !== undefined) queryParams.append('skip', params.skip.toString())
  if (params?.limit !== undefined) queryParams.append('limit', params.limit.toString())
  if (params?.status) queryParams.append('status', params.status)
  
  const response = await apiClient.get(`/api/treatment/treatment-plans?${queryParams.toString()}`)
  return response.data
}

// ===================== MEDICAL HISTORY TIMELINE =====================

export interface TimelineEvent {
  id: string
  event_type: 'intake' | 'travel' | 'family_history' | 'treatment_plan' | 'medication' | 'follow_up' | 'monitoring'
  date: string
  title: string
  description: string
  status?: string
  related_id?: string
  metadata?: Record<string, any>
}

export interface PatientTimelineResponse {
  patient_intake_id: string
  patient_name: string
  total_events: number
  events: TimelineEvent[]
}

export interface EventType {
  value: string
  label: string
  icon: string
}

export const getPatientTimeline = async (
  patientIntakeId: string,
  filters?: {
    eventTypes?: string[]
    startDate?: string
    endDate?: string
  }
): Promise<PatientTimelineResponse> => {
  const queryParams = new URLSearchParams()
  if (filters?.eventTypes && filters.eventTypes.length > 0) {
    queryParams.append('event_types', filters.eventTypes.join(','))
  }
  if (filters?.startDate) queryParams.append('start_date', filters.startDate)
  if (filters?.endDate) queryParams.append('end_date', filters.endDate)
  
  const response = await apiClient.get(
    `/api/timeline/patient/${patientIntakeId}?${queryParams.toString()}`
  )
  return response.data
}

export const getEventTypes = async (): Promise<{ event_types: EventType[] }> => {
  const response = await apiClient.get('/api/timeline/event-types')
  return response.data
}

// ===================== ANALYTICS DASHBOARD =====================

export interface DemographicsData {
  total_patients: number
  age_distribution: Record<string, number>
  gender_distribution: Record<string, number>
  blood_type_distribution: Record<string, number>
  average_age: number
}

export interface DiseaseTrendsData {
  total_diagnoses: number
  top_diagnoses: Array<{ diagnosis: string; count: number; percentage: number }>
  diagnoses_by_month: Array<{ month: string; count: number }>
  icd_code_distribution: Array<{ icd_code: string; diagnosis: string; count: number }>
}

export interface TreatmentOutcomesData {
  total_treatment_plans: number
  active_treatments: number
  completed_treatments: number
  discontinued_treatments: number
  on_hold_treatments: number
  treatment_status_distribution: Record<string, number>
  average_treatment_duration: number
  medication_statistics: {
    total: number
    active: number
    discontinued: number
    discontinuation_rate: number
  }
  follow_up_statistics: {
    total: number
    scheduled: number
    completed: number
    missed: number
    cancelled: number
    completion_rate: number
  }
}

export interface PerformanceMetricsData {
  patient_intake_rate: {
    monthly_data: Array<{ month: string; count: number }>
    average_monthly: number
    total_last_year: number
  }
  risk_assessment_summary: Record<string, number>
  travel_history_summary: {
    total_records: number
    unique_countries: number
    top_destinations: Array<{ destination: string; country: string; count: number }>
  }
  family_history_summary: {
    total_records: number
    common_conditions: Array<{ condition: string; count: number }>
  }
}

export interface AnalyticsDashboardResponse {
  demographics: DemographicsData
  disease_trends: DiseaseTrendsData
  treatment_outcomes: TreatmentOutcomesData
  performance_metrics: PerformanceMetricsData
  generated_at: string
}

export const getAnalyticsDashboard = async (): Promise<AnalyticsDashboardResponse> => {
  const response = await apiClient.get('/api/analytics/dashboard')
  return response.data
}

export const getDemographics = async (): Promise<DemographicsData> => {
  const response = await apiClient.get('/api/analytics/demographics')
  return response.data
}

export const getDiseaseTrends = async (): Promise<DiseaseTrendsData> => {
  const response = await apiClient.get('/api/analytics/disease-trends')
  return response.data
}

export const getTreatmentOutcomes = async (): Promise<TreatmentOutcomesData> => {
  const response = await apiClient.get('/api/analytics/treatment-outcomes')
  return response.data
}

export const getPerformanceMetrics = async (): Promise<PerformanceMetricsData> => {
  const response = await apiClient.get('/api/analytics/performance-metrics')
  return response.data
}

// ===================== FHIR API INTEGRATION =====================

export interface FHIRPatient {
  resourceType: string
  id: string
  identifier: Array<{ system: string; value: string }>
  name: Array<any>
  telecom: Array<any>
  gender?: string
  birthDate?: string
  address?: Array<any>
}

export interface FHIRBundle {
  resourceType: string
  type: string
  total: number
  entry: Array<{ resource: any; fullUrl?: string }>
}

export const getFHIRPatient = async (patientId: string): Promise<FHIRPatient> => {
  const response = await apiClient.get(`/api/fhir/Patient/${patientId}`)
  return response.data
}

export const searchFHIRPatients = async (params?: { name?: string; identifier?: string }): Promise<FHIRBundle> => {
  const queryParams = new URLSearchParams()
  if (params?.name) queryParams.append('name', params.name)
  if (params?.identifier) queryParams.append('identifier', params.identifier)
  const response = await apiClient.get(`/api/fhir/Patient?${queryParams.toString()}`)
  return response.data
}

export const searchFHIRConditions = async (patientId?: string): Promise<FHIRBundle> => {
  const params = patientId ? `?patient=${patientId}` : ''
  const response = await apiClient.get(`/api/fhir/Condition${params}`)
  return response.data
}

export const searchFHIRMedications = async (patientId?: string): Promise<FHIRBundle> => {
  const params = patientId ? `?patient=${patientId}` : ''
  const response = await apiClient.get(`/api/fhir/MedicationRequest${params}`)
  return response.data
}

export const getFHIRCapabilityStatement = async () => {
  const response = await apiClient.get('/api/fhir/metadata')
  return response.data
}

// Export the axios instance for custom requests
export default apiClient

// ===================== AUTH =====================
export const login = async (data: { email: string; password: string }) => {
  const response = await apiClient.post('/api/auth/login', data)
  return response.data
}

export const register = async (data: { email: string; password: string; full_name: string; role?: string; license_number?: string }) => {
  const response = await apiClient.post('/api/auth/register', data)
  return response.data
}
