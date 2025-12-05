import apiClient from './apiClient';
import { saveAs } from 'file-saver';

export interface PatientData {
  id: string;
  name: string;
  age: number;
  gender: string;
  contactNumber: string;
  address: string;
}

export interface MedicalHistoryItem {
  id: string;
  condition: string;
  duration: string;
  severity: 'Mild' | 'Moderate' | 'Severe';
  onset: Date;
  status: 'Active' | 'Resolved' | 'Chronic';
  notes: string;
}

export interface PersonalHistory {
  smoking: {
    status: 'Never' | 'Former' | 'Current';
    packsPerDay: number;
    years: number;
    quitDate?: Date;
    smokingIndex: number;
  };
  alcohol: {
    status: 'Never' | 'Occasional' | 'Regular' | 'Heavy';
    unitsPerWeek: number;
    years: number;
  };
  exercise: {
    frequency: 'None' | 'Rarely' | 'Weekly' | 'Daily';
    type: string[];
    duration: number;
  };
  occupation: string;
  allergies: string[];
}

export interface ClinicalExamination {
  vitalSigns: {
    bloodPressure: { systolic: number; diastolic: number };
    heartRate: number;
    temperature: number;
    respiratoryRate: number;
    oxygenSaturation: number;
    weight: number;
    height: number;
    bmi: number;
  };
  generalExamination: {
    consciousness: string;
    pallor: boolean;
    jaundice: boolean;
    cyanosis: boolean;
    clubbing: boolean;
    lymphadenopathy: boolean;
    edema: boolean;
  };
  systemicExamination: {
    cardiovascular: string;
    respiratory: string;
    abdominal: string;
    neurological: string;
    musculoskeletal: string;
  };
}

export interface DiagnosisData {
  chiefComplaints: string[];
  historyOfPresentIllness: string;
  diagnosis: {
    primary: string;
    secondary: string[];
    icdCodes: string[];
    confidence: string;
  };
  investigations: {
    laboratory: string[];
    imaging: string[];
    specialTests: string[];
  };
}

export interface TreatmentPlan {
  medications: Array<{
    name: string;
    dosage: string;
    frequency: string;
    duration: string;
    route: string;
    instructions: string;
  }>;
  advice: string[];
  followUp: {
    date: Date;
    instructions: string;
  };
  lifestyle: string[];
  redFlags: string[];
}

export interface OPDCaseSheet {
  patient: PatientData;
  visitDate: Date;
  medicalHistory: MedicalHistoryItem[];
  personalHistory: PersonalHistory;
  clinicalExamination: ClinicalExamination;
  diagnosis: DiagnosisData;
  treatmentPlan: TreatmentPlan;
  doctorNotes: string;
  doctorName: string;
  hospitalName: string;
}

export class OPDCaseSheetService {
  /**
   * Generate comprehensive OPD case sheet PDF
   */
  static async generateOPDCaseSheetPDF(caseSheet: OPDCaseSheet): Promise<void> {
    try {
      console.log('[MEDICAL] Generating OPD Case Sheet PDF...');
      
      const response = await apiClient.post('/api/reports/opd-case-sheet', caseSheet, {
        responseType: 'blob',
        timeout: 60000, // 60 seconds for PDF generation
      });

      if (response.status === 200) {
        const blob = new Blob([response.data], { type: 'application/pdf' });
        const fileName = `OPD_CaseSheet_${caseSheet.patient.name.replace(/\s+/g, '_')}_${new Date().toISOString().split('T')[0]}.pdf`;
        
        saveAs(blob, fileName);
        console.log('[OK] OPD Case Sheet PDF downloaded successfully');
        return;
      }
      
      throw new Error('PDF generation failed');
    } catch (error: any) {
      console.error('[ERROR] OPD Case Sheet PDF generation failed:', error);
      
      if (error.response?.status === 413) {
        throw new Error('Case sheet data too large. Please reduce content size.');
      } else if (error.response?.status === 500) {
        throw new Error('Server error during PDF generation. Please try again.');
      } else if (error.code === 'ECONNABORTED') {
        throw new Error('PDF generation timeout. Please try again with smaller content.');
      } else {
        throw new Error(error.response?.data?.detail || error.message || 'Failed to generate OPD case sheet');
      }
    }
  }

  /**
   * Generate prescription PDF only
   */
  static async generatePrescriptionPDF(
    patient: PatientData, 
    treatmentPlan: TreatmentPlan, 
    doctorInfo: { name: string; registration: string; hospital: string }
  ): Promise<void> {
    try {
      console.log('[PILL] Generating Prescription PDF...');
      
      const prescriptionData = {
        patient,
        treatmentPlan,
        doctorInfo,
        date: new Date(),
      };

      const response = await apiClient.post('/api/reports/prescription', prescriptionData, {
        responseType: 'blob',
        timeout: 30000,
      });

      if (response.status === 200) {
        const blob = new Blob([response.data], { type: 'application/pdf' });
        const fileName = `Prescription_${patient.name.replace(/\s+/g, '_')}_${new Date().toISOString().split('T')[0]}.pdf`;
        
        saveAs(blob, fileName);
        console.log('[OK] Prescription PDF downloaded successfully');
        return;
      }
      
      throw new Error('Prescription PDF generation failed');
    } catch (error: any) {
      console.error('[ERROR] Prescription PDF generation failed:', error);
      throw new Error(error.response?.data?.detail || error.message || 'Failed to generate prescription');
    }
  }

  /**
   * Generate medical history summary PDF
   */
  static async generateMedicalHistoryPDF(
    patient: PatientData,
    medicalHistory: MedicalHistoryItem[],
    personalHistory: PersonalHistory
  ): Promise<void> {
    try {
      console.log('[LIST] Generating Medical History PDF...');
      
      const historyData = {
        patient,
        medicalHistory,
        personalHistory,
        generatedDate: new Date(),
      };

      const response = await apiClient.post('/api/reports/medical-history', historyData, {
        responseType: 'blob',
        timeout: 30000,
      });

      if (response.status === 200) {
        const blob = new Blob([response.data], { type: 'application/pdf' });
        const fileName = `Medical_History_${patient.name.replace(/\s+/g, '_')}_${new Date().toISOString().split('T')[0]}.pdf`;
        
        saveAs(blob, fileName);
        console.log('[OK] Medical History PDF downloaded successfully');
        return;
      }
      
      throw new Error('Medical History PDF generation failed');
    } catch (error: any) {
      console.error('[ERROR] Medical History PDF generation failed:', error);
      throw new Error(error.response?.data?.detail || error.message || 'Failed to generate medical history');
    }
  }

  /**
   * Preview case sheet data before PDF generation
   */
  static validateCaseSheet(caseSheet: OPDCaseSheet): { isValid: boolean; errors: string[] } {
    const errors: string[] = [];

    // Validate patient information
    if (!caseSheet.patient.name.trim()) {
      errors.push('Patient name is required');
    }
    if (!caseSheet.patient.age || caseSheet.patient.age <= 0) {
      errors.push('Valid patient age is required');
    }
    if (!caseSheet.patient.gender) {
      errors.push('Patient gender is required');
    }

    // Validate diagnosis
    if (!caseSheet.diagnosis.diagnosis.primary.trim()) {
      errors.push('Primary diagnosis is required');
    }

    // Validate treatment plan
    if (!caseSheet.treatmentPlan.medications.length) {
      errors.push('At least one medication should be prescribed');
    }

    // Validate doctor information
    if (!caseSheet.doctorName.trim()) {
      errors.push('Doctor name is required');
    }

    return {
      isValid: errors.length === 0,
      errors,
    };
  }

  /**
   * Calculate smoking index and risk assessment
   */
  static calculateSmokingRisk(smokingHistory: PersonalHistory['smoking']): {
    index: number;
    riskLevel: 'None' | 'Low' | 'Moderate' | 'High' | 'Very High';
    recommendations: string[];
  } {
    const index = smokingHistory.smokingIndex;
    let riskLevel: 'None' | 'Low' | 'Moderate' | 'High' | 'Very High';
    let recommendations: string[] = [];

    if (index === 0) {
      riskLevel = 'None';
      recommendations = ['Maintain smoke-free lifestyle'];
    } else if (index < 10) {
      riskLevel = 'Low';
      recommendations = [
        'Consider smoking cessation programs',
        'Regular health monitoring recommended',
      ];
    } else if (index < 20) {
      riskLevel = 'Moderate';
      recommendations = [
        'Smoking cessation strongly recommended',
        'Annual lung function tests',
        'Chest X-ray screening',
      ];
    } else if (index < 30) {
      riskLevel = 'High';
      recommendations = [
        'Immediate smoking cessation required',
        'Annual CT chest screening',
        'Pulmonary function assessment',
        'Cardiovascular risk evaluation',
      ];
    } else {
      riskLevel = 'Very High';
      recommendations = [
        'Urgent smoking cessation with medical support',
        'Comprehensive lung cancer screening',
        'Cardiopulmonary assessment',
        'Smoking cessation counseling and medications',
      ];
    }

    return { index, riskLevel, recommendations };
  }
}

export default OPDCaseSheetService;