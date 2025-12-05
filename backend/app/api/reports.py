"""
Enhanced PDF Report Generation for OPD Case Sheets
Comprehensive medical documentation with clinical history, examination, and treatment plans
"""

import io
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
import fitz  # PyMuPDF

router = APIRouter()

class VitalSigns(BaseModel):
    blood_pressure_systolic: int
    blood_pressure_diastolic: int
    heart_rate: int
    temperature: float
    respiratory_rate: int
    oxygen_saturation: int
    weight: float
    height: float
    bmi: float

class GeneralExamination(BaseModel):
    consciousness: str
    pallor: bool
    jaundice: bool
    cyanosis: bool
    clubbing: bool
    lymphadenopathy: bool
    edema: bool

class SystemicExamination(BaseModel):
    cardiovascular: str
    respiratory: str
    abdominal: str
    neurological: str
    musculoskeletal: str

class ClinicalExamination(BaseModel):
    vital_signs: VitalSigns
    general_examination: GeneralExamination
    systemic_examination: SystemicExamination

class SmokingHistory(BaseModel):
    status: str
    packs_per_day: float
    years: int
    quit_date: Optional[datetime]
    smoking_index: float

class AlcoholHistory(BaseModel):
    status: str
    units_per_week: int
    years: int

class ExerciseHistory(BaseModel):
    frequency: str
    type: List[str]
    duration: int

class PersonalHistory(BaseModel):
    smoking: SmokingHistory
    alcohol: AlcoholHistory
    exercise: ExerciseHistory
    occupation: str
    allergies: List[str]

class MedicalHistoryItem(BaseModel):
    condition: str
    duration: str
    severity: str
    onset: datetime
    status: str
    notes: str

class DiagnosisData(BaseModel):
    chief_complaints: List[str]
    history_of_present_illness: str
    primary_diagnosis: str
    secondary_diagnosis: List[str]
    icd_codes: List[str]
    confidence: str

class Medication(BaseModel):
    name: str
    dosage: str
    frequency: str
    duration: str
    route: str
    instructions: str

class FollowUp(BaseModel):
    date: datetime
    instructions: str

class TreatmentPlan(BaseModel):
    medications: List[Medication]
    advice: List[str]
    follow_up: FollowUp
    lifestyle: List[str]
    red_flags: List[str]

class PatientData(BaseModel):
    id: str
    name: str
    age: int
    gender: str
    contact_number: str
    address: str

class OPDCaseSheetRequest(BaseModel):
    patient: PatientData
    visit_date: datetime
    medical_history: List[MedicalHistoryItem]
    personal_history: PersonalHistory
    clinical_examination: ClinicalExamination
    diagnosis: DiagnosisData
    treatment_plan: TreatmentPlan
    doctor_notes: str
    doctor_name: str
    hospital_name: str

class EnhancedPDFGenerator:
    def __init__(self):
        self.page_width = 595  # A4 width
        self.page_height = 842  # A4 height
        self.margin = 40
        self.content_width = self.page_width - (2 * self.margin)
        self.current_y = 0
        self.line_height = 15
        
    def create_opd_case_sheet(self, data: OPDCaseSheetRequest) -> bytes:
        """Generate comprehensive OPD case sheet PDF"""
        doc = fitz.open()
        page = doc.new_page(width=self.page_width, height=self.page_height)
        self.current_y = 50
        
        # Header
        self._add_header(page, data.hospital_name, data.patient.name)
        
        # Patient Information
        self._add_patient_info(page, data.patient, data.visit_date)
        
        # Chief Complaints
        self._add_section(page, "CHIEF COMPLAINTS", data.diagnosis.chief_complaints)
        
        # History of Present Illness
        self._add_text_section(page, "HISTORY OF PRESENT ILLNESS", data.diagnosis.history_of_present_illness)
        
        # Medical History with timestamps
        self._add_medical_history(page, data.medical_history)
        
        # Personal History with smoking index
        self._add_personal_history(page, data.personal_history)
        
        # Clinical Examination
        self._add_clinical_examination(page, data.clinical_examination)
        
        # Check if we need a new page
        if self.current_y > 700:
            page = doc.new_page(width=self.page_width, height=self.page_height)
            self.current_y = 50
        
        # Diagnosis and Assessment
        self._add_diagnosis_section(page, data.diagnosis)
        
        # Treatment Plan
        self._add_treatment_plan(page, data.treatment_plan)
        
        # Doctor's Notes
        if data.doctor_notes:
            self._add_text_section(page, "DOCTOR'S NOTES", data.doctor_notes)
        
        # Footer
        self._add_footer(page, data.doctor_name, data.visit_date)
        
        # Convert to bytes
        pdf_bytes = doc.tobytes()
        doc.close()
        
        return pdf_bytes
    
    def _add_header(self, page, hospital_name: str, patient_name: str):
        """Add professional header with hospital info"""
        # Hospital name
        page.insert_text(
            (self.margin, self.current_y),
            hospital_name.upper(),
            fontsize=16,
            fontname="helv-bold",
            color=(0.2, 0.3, 0.6)
        )
        
        self.current_y += 25
        
        # Document title
        page.insert_text(
            (self.margin, self.current_y),
            "OUTPATIENT DEPARTMENT - CASE SHEET",
            fontsize=14,
            fontname="helv-bold",
            color=(0.1, 0.1, 0.1)
        )
        
        # Date and time on right
        date_str = datetime.now().strftime("%d/%m/%Y %H:%M")
        page.insert_text(
            (self.page_width - 150, self.current_y),
            f"Generated: {date_str}",
            fontsize=10,
            fontname="helv",
            color=(0.4, 0.4, 0.4)
        )
        
        self.current_y += 30
        
        # Horizontal line
        page.draw_line(
            (self.margin, self.current_y),
            (self.page_width - self.margin, self.current_y),
            color=(0.5, 0.5, 0.5),
            width=0.5
        )
        self.current_y += 15
    
    def _add_patient_info(self, page, patient: PatientData, visit_date: datetime):
        """Add patient demographic information"""
        info_box_height = 80
        
        # Background box
        rect = fitz.Rect(self.margin, self.current_y, self.page_width - self.margin, self.current_y + info_box_height)
        page.draw_rect(rect, color=(0.95, 0.95, 0.95), fill=True)
        
        # Patient info in two columns
        col1_x = self.margin + 10
        col2_x = self.margin + 280
        info_y = self.current_y + 15
        
        # Column 1
        page.insert_text((col1_x, info_y), "Patient Name:", fontsize=10, fontname="helv-bold")
        page.insert_text((col1_x + 80, info_y), patient.name, fontsize=10, fontname="helv")
        
        info_y += 15
        page.insert_text((col1_x, info_y), "Age/Gender:", fontsize=10, fontname="helv-bold")
        page.insert_text((col1_x + 80, info_y), f"{patient.age} years / {patient.gender}", fontsize=10, fontname="helv")
        
        info_y += 15
        page.insert_text((col1_x, info_y), "Contact:", fontsize=10, fontname="helv-bold")
        page.insert_text((col1_x + 80, info_y), patient.contact_number, fontsize=10, fontname="helv")
        
        # Column 2
        info_y = self.current_y + 15
        page.insert_text((col2_x, info_y), "Patient ID:", fontsize=10, fontname="helv-bold")
        page.insert_text((col2_x + 80, info_y), patient.id, fontsize=10, fontname="helv")
        
        info_y += 15
        page.insert_text((col2_x, info_y), "Visit Date:", fontsize=10, fontname="helv-bold")
        page.insert_text((col2_x + 80, info_y), visit_date.strftime("%d/%m/%Y"), fontsize=10, fontname="helv")
        
        info_y += 15
        page.insert_text((col2_x, info_y), "Address:", fontsize=10, fontname="helv-bold")
        # Truncate address if too long
        address = patient.address[:30] + "..." if len(patient.address) > 30 else patient.address
        page.insert_text((col2_x + 80, info_y), address, fontsize=10, fontname="helv")
        
        self.current_y += info_box_height + 20
    
    def _add_medical_history(self, page, medical_history: List[MedicalHistoryItem]):
        """Add medical history with duration timestamps"""
        if not medical_history:
            return
            
        self._add_section_header(page, "PAST MEDICAL HISTORY")
        
        # Table headers
        headers = ["Condition", "Duration", "Onset", "Severity", "Status"]
        col_widths = [150, 80, 80, 70, 70]
        
        # Header row
        x_pos = self.margin
        for i, (header, width) in enumerate(zip(headers, col_widths)):
            page.insert_text(
                (x_pos, self.current_y),
                header,
                fontsize=9,
                fontname="helv-bold"
            )
            x_pos += width
        
        self.current_y += 15
        
        # Draw header underline
        page.draw_line(
            (self.margin, self.current_y - 3),
            (self.page_width - self.margin, self.current_y - 3),
            color=(0.3, 0.3, 0.3),
            width=0.5
        )
        
        # Data rows
        for condition in medical_history:
            x_pos = self.margin
            
            # Condition name
            condition_text = condition.condition[:20] + "..." if len(condition.condition) > 20 else condition.condition
            page.insert_text((x_pos, self.current_y), condition_text, fontsize=9, fontname="helv")
            x_pos += col_widths[0]
            
            # Duration
            page.insert_text((x_pos, self.current_y), condition.duration, fontsize=9, fontname="helv")
            x_pos += col_widths[1]
            
            # Onset date
            onset_str = condition.onset.strftime("%m/%Y") if condition.onset else "Unknown"
            page.insert_text((x_pos, self.current_y), onset_str, fontsize=9, fontname="helv")
            x_pos += col_widths[2]
            
            # Severity
            page.insert_text((x_pos, self.current_y), condition.severity, fontsize=9, fontname="helv")
            x_pos += col_widths[3]
            
            # Status
            page.insert_text((x_pos, self.current_y), condition.status, fontsize=9, fontname="helv")
            
            self.current_y += 12
            
            # Add notes if present
            if condition.notes:
                notes_text = f"Notes: {condition.notes[:60]}..." if len(condition.notes) > 60 else f"Notes: {condition.notes}"
                page.insert_text(
                    (self.margin + 10, self.current_y),
                    notes_text,
                    fontsize=8,
                    fontname="helv-ita",
                    color=(0.4, 0.4, 0.4)
                )
                self.current_y += 10
        
        self.current_y += 15
    
    def _add_personal_history(self, page, personal_history: PersonalHistory):
        """Add personal history with smoking index calculation"""
        self._add_section_header(page, "PERSONAL HISTORY")
        
        # Smoking history with pack-years index
        smoking = personal_history.smoking
        smoking_text = f"Smoking: {smoking.status}"
        if smoking.status != "Never":
            smoking_text += f" - {smoking.packs_per_day} packs/day × {smoking.years} years = {smoking.smoking_index} pack-years"
            
            # Add risk assessment
            if smoking.smoking_index >= 20:
                risk = "HIGH RISK"
                color = (0.8, 0.2, 0.2)
            elif smoking.smoking_index >= 10:
                risk = "MODERATE RISK"
                color = (0.8, 0.6, 0.2)
            else:
                risk = "LOW RISK"
                color = (0.2, 0.6, 0.2)
                
            smoking_text += f" ({risk})"
            
        page.insert_text((self.margin, self.current_y), smoking_text, fontsize=10, fontname="helv")
        if smoking.status != "Never":
            # Highlight risk level
            risk_x = self.margin + len(smoking_text.split("(")[0]) * 6
            page.insert_text((risk_x, self.current_y), f"({risk})", fontsize=10, fontname="helv-bold", color=color)
        
        self.current_y += 15
        
        # Alcohol history
        alcohol = personal_history.alcohol
        alcohol_text = f"Alcohol: {alcohol.status}"
        if alcohol.status != "Never":
            alcohol_text += f" - {alcohol.units_per_week} units/week for {alcohol.years} years"
        page.insert_text((self.margin, self.current_y), alcohol_text, fontsize=10, fontname="helv")
        self.current_y += 15
        
        # Exercise and occupation
        exercise = personal_history.exercise
        exercise_text = f"Exercise: {exercise.frequency}"
        if exercise.type:
            exercise_text += f" ({', '.join(exercise.type[:3])})"
        page.insert_text((self.margin, self.current_y), exercise_text, fontsize=10, fontname="helv")
        self.current_y += 15
        
        if personal_history.occupation:
            page.insert_text((self.margin, self.current_y), f"Occupation: {personal_history.occupation}", fontsize=10, fontname="helv")
            self.current_y += 15
        
        # Allergies
        if personal_history.allergies:
            allergies_text = f"Allergies: {', '.join(personal_history.allergies)}"
            page.insert_text((self.margin, self.current_y), allergies_text, fontsize=10, fontname="helv", color=(0.8, 0.2, 0.2))
            self.current_y += 15
        
        self.current_y += 10
    
    def _add_clinical_examination(self, page, examination: ClinicalExamination):
        """Add clinical examination findings"""
        self._add_section_header(page, "CLINICAL EXAMINATION")
        
        # Vital signs in a structured format
        vitals = examination.vital_signs
        page.insert_text((self.margin, self.current_y), "Vital Signs:", fontsize=10, fontname="helv-bold")
        self.current_y += 12
        
        vitals_text = [
            f"BP: {vitals.blood_pressure_systolic}/{vitals.blood_pressure_diastolic} mmHg",
            f"HR: {vitals.heart_rate} bpm",
            f"Temp: {vitals.temperature}°C",
            f"RR: {vitals.respiratory_rate}/min",
            f"SpO2: {vitals.oxygen_saturation}%",
            f"Weight: {vitals.weight} kg",
            f"Height: {vitals.height} cm",
            f"BMI: {vitals.bmi:.1f}"
        ]
        
        # Display vitals in two columns
        for i, vital in enumerate(vitals_text):
            x_pos = self.margin + 10 if i % 2 == 0 else self.margin + 250
            if i % 2 == 0 and i > 0:
                self.current_y += 12
            page.insert_text((x_pos, self.current_y), vital, fontsize=9, fontname="helv")
        
        self.current_y += 20
        
        # General examination
        general = examination.general_examination
        page.insert_text((self.margin, self.current_y), "General Examination:", fontsize=10, fontname="helv-bold")
        self.current_y += 12
        
        findings = []
        if general.pallor: findings.append("Pallor")
        if general.jaundice: findings.append("Jaundice")
        if general.cyanosis: findings.append("Cyanosis")
        if general.clubbing: findings.append("Clubbing")
        if general.lymphadenopathy: findings.append("Lymphadenopathy")
        if general.edema: findings.append("Edema")
        
        if findings:
            findings_text = f"Positive findings: {', '.join(findings)}"
        else:
            findings_text = "No significant abnormalities detected"
            
        page.insert_text((self.margin + 10, self.current_y), findings_text, fontsize=9, fontname="helv")
        self.current_y += 15
        
        # Systemic examination
        systemic = examination.systemic_examination
        systems = [
            ("Cardiovascular", systemic.cardiovascular),
            ("Respiratory", systemic.respiratory),
            ("Abdominal", systemic.abdominal),
            ("Neurological", systemic.neurological),
        ]
        
        for system, findings in systems:
            if findings:
                page.insert_text((self.margin, self.current_y), f"{system}:", fontsize=9, fontname="helv-bold")
                page.insert_text((self.margin + 100, self.current_y), findings, fontsize=9, fontname="helv")
                self.current_y += 12
        
        self.current_y += 10
    
    def _add_diagnosis_section(self, page, diagnosis: DiagnosisData):
        """Add diagnosis and assessment"""
        self._add_section_header(page, "DIAGNOSIS & ASSESSMENT")
        
        # Primary diagnosis
        page.insert_text((self.margin, self.current_y), "Primary Diagnosis:", fontsize=10, fontname="helv-bold")
        page.insert_text((self.margin + 120, self.current_y), diagnosis.primary_diagnosis, fontsize=10, fontname="helv")
        self.current_y += 15
        
        # Secondary diagnoses
        if diagnosis.secondary_diagnosis:
            page.insert_text((self.margin, self.current_y), "Secondary Diagnosis:", fontsize=10, fontname="helv-bold")
            secondary_text = ", ".join(diagnosis.secondary_diagnosis)
            page.insert_text((self.margin + 120, self.current_y), secondary_text, fontsize=10, fontname="helv")
            self.current_y += 15
        
        # ICD codes
        if diagnosis.icd_codes:
            page.insert_text((self.margin, self.current_y), "ICD Codes:", fontsize=10, fontname="helv-bold")
            icd_text = ", ".join(diagnosis.icd_codes)
            page.insert_text((self.margin + 120, self.current_y), icd_text, fontsize=10, fontname="helv")
            self.current_y += 15
        
        # Confidence level
        page.insert_text((self.margin, self.current_y), "Confidence Level:", fontsize=10, fontname="helv-bold")
        page.insert_text((self.margin + 120, self.current_y), diagnosis.confidence, fontsize=10, fontname="helv")
        self.current_y += 20
    
    def _add_treatment_plan(self, page, treatment: TreatmentPlan):
        """Add treatment plan and prescriptions"""
        # Check if we need a new page
        if self.current_y > 600:
            page = page.parent.new_page(width=self.page_width, height=self.page_height)
            self.current_y = 50
        
        self._add_section_header(page, "TREATMENT PLAN")
        
        # Medications
        if treatment.medications:
            page.insert_text((self.margin, self.current_y), "Medications:", fontsize=10, fontname="helv-bold")
            self.current_y += 15
            
            for i, med in enumerate(treatment.medications):
                med_text = f"{i+1}. {med.name} {med.dosage} - {med.frequency} for {med.duration} ({med.route})"
                page.insert_text((self.margin + 10, self.current_y), med_text, fontsize=9, fontname="helv")
                self.current_y += 12
                
                if med.instructions:
                    page.insert_text(
                        (self.margin + 20, self.current_y),
                        f"Instructions: {med.instructions}",
                        fontsize=8,
                        fontname="helv-ita",
                        color=(0.4, 0.4, 0.4)
                    )
                    self.current_y += 10
        
        # Advice
        if treatment.advice:
            self.current_y += 10
            page.insert_text((self.margin, self.current_y), "Medical Advice:", fontsize=10, fontname="helv-bold")
            self.current_y += 15
            
            for advice in treatment.advice:
                page.insert_text((self.margin + 10, self.current_y), f"- {advice}", fontsize=9, fontname="helv")
                self.current_y += 12
        
        # Follow-up
        if treatment.follow_up:
            self.current_y += 10
            follow_up_date = treatment.follow_up.date.strftime("%d/%m/%Y")
            page.insert_text((self.margin, self.current_y), f"Follow-up: {follow_up_date}", fontsize=10, fontname="helv-bold")
            self.current_y += 12
            
            if treatment.follow_up.instructions:
                page.insert_text((self.margin + 10, self.current_y), treatment.follow_up.instructions, fontsize=9, fontname="helv")
                self.current_y += 12
    
    def _add_section_header(self, page, title: str):
        """Add a section header with underline"""
        page.insert_text((self.margin, self.current_y), title, fontsize=12, fontname="helv-bold", color=(0.2, 0.2, 0.6))
        self.current_y += 15
        
        # Underline
        page.draw_line(
            (self.margin, self.current_y - 3),
            (self.margin + len(title) * 7, self.current_y - 3),
            color=(0.2, 0.2, 0.6),
            width=1
        )
        self.current_y += 5
    
    def _add_section(self, page, title: str, items: List[str]):
        """Add a section with bullet points"""
        self._add_section_header(page, title)
        
        for item in items:
            page.insert_text((self.margin + 10, self.current_y), f"- {item}", fontsize=10, fontname="helv")
            self.current_y += 12
        
        self.current_y += 10
    
    def _add_text_section(self, page, title: str, content: str):
        """Add a text section with wrapping"""
        self._add_section_header(page, title)
        
        # Simple text wrapping
        words = content.split()
        line = ""
        for word in words:
            if len(line + word) < 80:  # Approximate character limit
                line += word + " "
            else:
                if line:
                    page.insert_text((self.margin + 10, self.current_y), line.strip(), fontsize=10, fontname="helv")
                    self.current_y += 12
                line = word + " "
        
        if line:
            page.insert_text((self.margin + 10, self.current_y), line.strip(), fontsize=10, fontname="helv")
            self.current_y += 12
        
        self.current_y += 10
    
    def _add_footer(self, page, doctor_name: str, visit_date: datetime):
        """Add footer with doctor signature and date"""
        footer_y = self.page_height - 80
        
        # Doctor signature section
        page.insert_text((self.margin, footer_y), "Doctor's Signature:", fontsize=10, fontname="helv-bold")
        page.insert_text((self.margin, footer_y + 20), doctor_name, fontsize=10, fontname="helv")
        page.insert_text((self.margin, footer_y + 35), f"Date: {visit_date.strftime('%d/%m/%Y')}", fontsize=9, fontname="helv")
        
        # Hospital stamp area
        page.insert_text((self.page_width - 200, footer_y), "Hospital Seal:", fontsize=10, fontname="helv-bold")
        
        # Footer line
        page.draw_line(
            (self.margin, footer_y - 10),
            (self.page_width - self.margin, footer_y - 10),
            color=(0.5, 0.5, 0.5),
            width=0.5
        )

@router.post("/opd-case-sheet")
async def generate_opd_case_sheet(request: OPDCaseSheetRequest):
    """Generate comprehensive OPD case sheet PDF"""
    try:
        generator = EnhancedPDFGenerator()
        pdf_bytes = generator.create_opd_case_sheet(request)
        
        filename = f"OPD_CaseSheet_{request.patient.name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.pdf"
        
        return StreamingResponse(
            io.BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate OPD case sheet: {str(e)}")

@router.post("/prescription")
async def generate_prescription(request: dict):
    """Generate prescription PDF"""
    try:
        # Implementation for prescription-only PDF
        generator = EnhancedPDFGenerator()
        # Add prescription-specific generation logic here
        
        return {"message": "Prescription PDF generation endpoint - to be implemented"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate prescription: {str(e)}")

@router.post("/medical-history")
async def generate_medical_history(request: dict):
    """Generate medical history PDF"""
    try:
        # Implementation for medical history PDF
        generator = EnhancedPDFGenerator()
        # Add medical history-specific generation logic here
        
        return {"message": "Medical history PDF generation endpoint - to be implemented"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate medical history: {str(e)}")