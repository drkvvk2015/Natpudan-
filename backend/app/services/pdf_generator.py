"""
PDF Report Generation Service
Generates professional medical reports in PDF format
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
import io
import fitz  # PyMuPDF
from fastapi import HTTPException

class PDFReportGenerator:
    """Generate professional PDF medical reports"""
    
    def __init__(self):
        self.page_width = 595  # A4 width in points
        self.page_height = 842  # A4 height in points
        self.margin = 50
        self.content_width = self.page_width - (2 * self.margin)
        
    def create_header(self, page, title: str, subtitle: str = None):
        """Create report header with title and logo placeholder"""
        # Hospital/Clinic Name
        page.insert_text(
            (self.margin, 40),
            "Medical AI Assistant",
            fontsize=20,
            fontname="helv-bold",
            color=(0.2, 0.3, 0.6)
        )
        
        # Report Title
        page.insert_text(
            (self.margin, 70),
            title,
            fontsize=16,
            fontname="helv-bold",
            color=(0.1, 0.1, 0.1)
        )
        
        if subtitle:
            page.insert_text(
                (self.margin, 90),
                subtitle,
                fontsize=10,
                fontname="helv",
                color=(0.4, 0.4, 0.4)
            )
        
        # Header line
        page.draw_line(
            (self.margin, 100),
            (self.page_width - self.margin, 100),
            color=(0.7, 0.7, 0.7),
            width=1
        )
        
        return 120  # Return Y position for next content
    
    def create_footer(self, page, page_num: int, total_pages: int):
        """Create report footer with page number"""
        footer_y = self.page_height - 30
        
        # Footer line
        page.draw_line(
            (self.margin, footer_y - 10),
            (self.page_width - self.margin, footer_y - 10),
            color=(0.7, 0.7, 0.7),
            width=0.5
        )
        
        # Page number
        page.insert_text(
            (self.page_width / 2 - 20, footer_y),
            f"Page {page_num} of {total_pages}",
            fontsize=8,
            fontname="helv",
            color=(0.5, 0.5, 0.5)
        )
        
        # Generation timestamp
        page.insert_text(
            (self.margin, footer_y),
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            fontsize=8,
            fontname="helv",
            color=(0.5, 0.5, 0.5)
        )
    
    def add_section(self, page, y: float, title: str, content: str, bold: bool = False) -> float:
        """Add a section with title and content"""
        if y > self.page_height - 100:
            return -1  # Signal new page needed
        
        # Section title
        page.insert_text(
            (self.margin, y),
            title,
            fontsize=11,
            fontname="helv-bold",
            color=(0.2, 0.3, 0.6)
        )
        y += 20
        
        # Section content with word wrap
        font = "helv-bold" if bold else "helv"
        lines = self._wrap_text(content, self.content_width - 20, fontsize=9)
        
        for line in lines:
            if y > self.page_height - 80:
                return -1  # Signal new page needed
            page.insert_text(
                (self.margin + 10, y),
                line,
                fontsize=9,
                fontname=font,
                color=(0.2, 0.2, 0.2)
            )
            y += 15
        
        y += 10  # Space after section
        return y
    
    def add_table(self, page, y: float, headers: List[str], rows: List[List[str]], col_widths: List[int] = None) -> float:
        """Add a simple table"""
        if not col_widths:
            col_widths = [self.content_width // len(headers)] * len(headers)
        
        # Header row
        x = self.margin
        for i, header in enumerate(headers):
            page.draw_rect(
                fitz.Rect(x, y, x + col_widths[i], y + 20),
                color=(0.8, 0.8, 0.8),
                fill=(0.9, 0.9, 0.9)
            )
            page.insert_text(
                (x + 5, y + 14),
                header,
                fontsize=9,
                fontname="helv-bold",
                color=(0.1, 0.1, 0.1)
            )
            x += col_widths[i]
        
        y += 20
        
        # Data rows
        for row in rows:
            if y > self.page_height - 100:
                return -1  # Signal new page needed
            
            x = self.margin
            for i, cell in enumerate(row):
                page.draw_rect(
                    fitz.Rect(x, y, x + col_widths[i], y + 18),
                    color=(0.8, 0.8, 0.8)
                )
                # Truncate long text
                cell_text = str(cell)[:30] if len(str(cell)) > 30 else str(cell)
                page.insert_text(
                    (x + 5, y + 13),
                    cell_text,
                    fontsize=8,
                    fontname="helv",
                    color=(0.2, 0.2, 0.2)
                )
                x += col_widths[i]
            y += 18
        
        y += 15  # Space after table
        return y
    
    def _wrap_text(self, text: str, max_width: float, fontsize: int = 9) -> List[str]:
        """Wrap text to fit within max width"""
        words = text.split()
        lines = []
        current_line = []
        
        # Approximate character width (rough estimation)
        char_width = fontsize * 0.5
        max_chars = int(max_width / char_width)
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            if len(test_line) <= max_chars:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines if lines else [text]
    
    def generate_patient_intake_report(self, patient_data: Dict[str, Any]) -> bytes:
        """Generate Patient Intake Summary Report"""
        doc = fitz.open()
        page = doc.new_page(width=self.page_width, height=self.page_height)
        
        y = self.create_header(page, "Patient Intake Summary", f"Patient ID: {patient_data.get('intake_id', 'N/A')}")
        
        # Patient Demographics
        y = self.add_section(page, y, "Patient Demographics", "")
        demo_data = [
            ["Full Name:", patient_data.get('name', 'N/A')],
            ["Age:", f"{patient_data.get('age', 'N/A')} years"],
            ["Gender:", patient_data.get('gender', 'N/A').title()],
            ["Blood Type:", patient_data.get('blood_type', 'Unknown')],
            ["Date Recorded:", patient_data.get('created_at', 'N/A')[:10]],
        ]
        
        for label, value in demo_data:
            page.insert_text((self.margin + 10, y), f"{label} {value}", fontsize=9, fontname="helv", color=(0.2, 0.2, 0.2))
            y += 15
        
        y += 10
        
        # Travel History
        travel_history = patient_data.get('travel_history', [])
        if travel_history:
            y = self.add_section(page, y, "Travel History", f"Total trips recorded: {len(travel_history)}")
            
            for i, travel in enumerate(travel_history[:5], 1):  # Limit to 5
                travel_text = f"{i}. {travel.get('destination', 'N/A')} ({travel.get('departure_date', '')} to {travel.get('return_date', '')})"
                if travel.get('purpose'):
                    travel_text += f" - Purpose: {travel['purpose']}"
                y = self.add_section(page, y, "", travel_text)
        
        # Family History
        family_history = patient_data.get('family_history', [])
        if family_history:
            if y > self.page_height - 200:
                page = doc.new_page(width=self.page_width, height=self.page_height)
                y = 50
            
            y = self.add_section(page, y, "Family Medical History", f"Total conditions recorded: {len(family_history)}")
            
            for i, family in enumerate(family_history[:10], 1):  # Limit to 10
                family_text = f"{i}. {family.get('relationship', 'N/A')}: {family.get('condition', 'N/A')}"
                if family.get('age_of_onset'):
                    family_text += f" (Onset: age {family['age_of_onset']})"
                family_text += f" - Status: {family.get('status', 'Unknown')}"
                y = self.add_section(page, y, "", family_text)
        
        # Add footers to all pages
        for i, page in enumerate(doc, 1):
            self.create_footer(page, i, len(doc))
        
        # Save to bytes
        pdf_bytes = doc.write()
        doc.close()
        
        return pdf_bytes
    
    def generate_diagnosis_report(self, diagnosis_data: Dict[str, Any]) -> bytes:
        """Generate Diagnosis Report"""
        doc = fitz.open()
        page = doc.new_page(width=self.page_width, height=self.page_height)
        
        patient_name = diagnosis_data.get('patient_name', 'Unknown Patient')
        y = self.create_header(page, "Medical Diagnosis Report", f"Patient: {patient_name}")
        
        # Patient Information
        y = self.add_section(page, y, "Patient Information", "")
        patient_info = [
            ["Name:", patient_name],
            ["Age:", f"{diagnosis_data.get('age', 'N/A')} years"],
            ["Sex:", diagnosis_data.get('sex', 'N/A')],
            ["Hospital ID:", diagnosis_data.get('uhid', 'N/A')],
        ]
        
        for label, value in patient_info:
            page.insert_text((self.margin + 10, y), f"{label} {value}", fontsize=9, fontname="helv", color=(0.2, 0.2, 0.2))
            y += 15
        
        y += 10
        
        # Chief Complaints
        complaints = diagnosis_data.get('complaints', [])
        if complaints:
            complaints_text = "; ".join([f"{c.get('complaint', '')} ({c.get('duration', '')})" for c in complaints if c.get('complaint')])
            y = self.add_section(page, y, "Chief Complaints", complaints_text)
        
        # Vital Signs
        vitals = diagnosis_data.get('vitals', {})
        if vitals:
            vital_text = ", ".join([f"{k}: {v}" for k, v in vitals.items() if v])
            y = self.add_section(page, y, "Vital Signs", vital_text)
        
        # Differential Diagnoses
        diagnoses = diagnosis_data.get('differential_diagnoses', [])
        if diagnoses:
            if y > self.page_height - 250:
                page = doc.new_page(width=self.page_width, height=self.page_height)
                y = 50
            
            y = self.add_section(page, y, "Differential Diagnoses", "")
            
            for i, diag in enumerate(diagnoses[:5], 1):
                diag_text = f"{i}. {diag.get('name', 'Unknown')} - Confidence: {diag.get('confidence', 0)}%"
                page.insert_text((self.margin + 10, y), diag_text, fontsize=10, fontname="helv-bold", color=(0.1, 0.1, 0.5))
                y += 18
                
                if diag.get('icd_code'):
                    page.insert_text((self.margin + 20, y), f"ICD Code: {diag['icd_code']}", fontsize=8, fontname="helv", color=(0.3, 0.3, 0.3))
                    y += 15
                
                if diag.get('supporting_findings'):
                    findings_text = ", ".join(diag['supporting_findings'][:3])
                    page.insert_text((self.margin + 20, y), f"Key Findings: {findings_text}", fontsize=8, fontname="helv", color=(0.3, 0.3, 0.3))
                    y += 15
                
                y += 5
        
        # Recommended Tests
        tests = diagnosis_data.get('recommended_tests', [])
        if tests:
            if y > self.page_height - 150:
                page = doc.new_page(width=self.page_width, height=self.page_height)
                y = 50
            
            tests_text = "; ".join(tests[:10])
            y = self.add_section(page, y, "Recommended Investigations", tests_text)
        
        # Clinical Summary
        summary = diagnosis_data.get('clinical_summary', '')
        if summary:
            if y > self.page_height - 150:
                page = doc.new_page(width=self.page_width, height=self.page_height)
                y = 50
            
            y = self.add_section(page, y, "Clinical Summary", summary)
        
        # Add footers
        for i, page in enumerate(doc, 1):
            self.create_footer(page, i, len(doc))
        
        pdf_bytes = doc.write()
        doc.close()
        
        return pdf_bytes
    
    def generate_combined_report(self, patient_data: Dict[str, Any], diagnosis_data: Dict[str, Any], risk_assessment: Dict[str, Any] = None) -> bytes:
        """Generate Combined Medical Report"""
        doc = fitz.open()
        page = doc.new_page(width=self.page_width, height=self.page_height)
        
        patient_name = patient_data.get('name', 'Unknown Patient')
        y = self.create_header(page, "Comprehensive Medical Report", f"Patient: {patient_name}")
        
        # Executive Summary Box
        page.draw_rect(fitz.Rect(self.margin, y, self.page_width - self.margin, y + 80), color=(0.2, 0.3, 0.6), width=2)
        page.insert_text((self.margin + 10, y + 20), "EXECUTIVE SUMMARY", fontsize=12, fontname="helv-bold", color=(0.2, 0.3, 0.6))
        
        summary_text = f"Patient {patient_name}, {patient_data.get('age', 'N/A')} years old"
        if risk_assessment:
            summary_text += f", Risk Level: {risk_assessment.get('level', 'Unknown').upper()}"
        
        page.insert_text((self.margin + 10, y + 40), summary_text, fontsize=10, fontname="helv", color=(0.1, 0.1, 0.1))
        
        if diagnosis_data.get('primary_diagnosis'):
            page.insert_text((self.margin + 10, y + 60), f"Primary Diagnosis: {diagnosis_data['primary_diagnosis']}", 
                           fontsize=10, fontname="helv-bold", color=(0.5, 0.1, 0.1))
        
        y += 100
        
        # Patient Demographics
        y = self.add_section(page, y, "PATIENT INFORMATION", "")
        demo_lines = [
            f"Patient ID: {patient_data.get('intake_id', 'N/A')}",
            f"Blood Type: {patient_data.get('blood_type', 'Unknown')}",
            f"Date of Assessment: {datetime.now().strftime('%Y-%m-%d')}"
        ]
        for line in demo_lines:
            page.insert_text((self.margin + 10, y), line, fontsize=9, fontname="helv", color=(0.2, 0.2, 0.2))
            y += 15
        
        y += 10
        
        # Risk Assessment
        if risk_assessment:
            if y > self.page_height - 200:
                page = doc.new_page(width=self.page_width, height=self.page_height)
                y = 50
            
            risk_level = risk_assessment.get('level', 'unknown').upper()
            risk_color = (0.8, 0.1, 0.1) if risk_level in ['HIGH', 'CRITICAL'] else (0.8, 0.5, 0.0) if risk_level == 'MEDIUM' else (0.1, 0.6, 0.1)
            
            y = self.add_section(page, y, "RISK ASSESSMENT", "")
            page.insert_text((self.margin + 10, y), f"Risk Level: {risk_level}", fontsize=11, fontname="helv-bold", color=risk_color)
            y += 20
            
            page.insert_text((self.margin + 10, y), f"Risk Score: {risk_assessment.get('total', 0)} / 45", fontsize=9, fontname="helv", color=(0.2, 0.2, 0.2))
            y += 20
            
            # Risk factors
            factors = risk_assessment.get('factors', {})
            for factor, score in factors.items():
                if score > 0:
                    page.insert_text((self.margin + 20, y), f"- {factor.replace('_', ' ').title()}: {score} points", 
                                   fontsize=8, fontname="helv", color=(0.3, 0.3, 0.3))
                    y += 15
            
            y += 10
        
        # Diagnosis Summary
        if diagnosis_data.get('differential_diagnoses'):
            if y > self.page_height - 200:
                page = doc.new_page(width=self.page_width, height=self.page_height)
                y = 50
            
            y = self.add_section(page, y, "DIAGNOSIS", "")
            for i, diag in enumerate(diagnosis_data['differential_diagnoses'][:3], 1):
                page.insert_text((self.margin + 10, y), f"{i}. {diag.get('name', 'Unknown')} ({diag.get('confidence', 0)}%)", 
                               fontsize=9, fontname="helv-bold", color=(0.1, 0.1, 0.5))
                y += 20
        
        # Recommendations
        if y > self.page_height - 150:
            page = doc.new_page(width=self.page_width, height=self.page_height)
            y = 50
        
        y = self.add_section(page, y, "RECOMMENDATIONS", "")
        recommendations = risk_assessment.get('recommendations', []) if risk_assessment else []
        if not recommendations:
            recommendations = ["Follow up with healthcare provider", "Continue monitoring symptoms", "Maintain healthy lifestyle"]
        
        for rec in recommendations[:5]:
            page.insert_text((self.margin + 10, y), f"- {rec}", fontsize=9, fontname="helv", color=(0.2, 0.2, 0.2))
            y += 18
        
        # Add footers
        for i, page in enumerate(doc, 1):
            self.create_footer(page, i, len(doc))
        
        pdf_bytes = doc.write()
        doc.close()
        
        return pdf_bytes


# Singleton instance
pdf_generator = PDFReportGenerator()
