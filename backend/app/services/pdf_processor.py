"""
Medical Report PDF Processor
Extracts structured medical information from PDF documents
"""

import re
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

try:
    import fitz  # PyMuPDF
    PYMUPDF_AVAILABLE = True
except ImportError:
    logger.warning("PyMuPDF not available. Install with: pip install PyMuPDF")
    PYMUPDF_AVAILABLE = False

try:
    import PyPDF2
    PYPDF2_AVAILABLE = True
except ImportError:
    logger.warning("PyPDF2 not available. Install with: pip install PyPDF2")
    PYPDF2_AVAILABLE = False


class MedicalReportProcessor:
    """
    Extracts structured medical data from PDF reports including:
    - Vital signs (BP, HR, temperature, SpO2, etc.)
    - Medications and prescriptions
    - Laboratory results (CBC, metabolic panel, etc.)
    - Diagnoses and ICD codes
    - Allergies and adverse reactions
    """
    
    def __init__(self):
        """Initialize the medical report processor"""
        self.vitals_patterns = {
            'blood_pressure': r'(?:BP|Blood Pressure)[:\s]*(\d{2,3})/(\d{2,3})',
            'heart_rate': r'(?:HR|Heart Rate)[:\s]*(\d{2,3})\s*(?:bpm|beats)',
            'temperature': r'(?:Temp|Temperature)[:\s]*(\d{2,3}\.?\d*)\s*°?[CF]',
            'respiratory_rate': r'(?:RR|Respiratory Rate)[:\s]*(\d{1,3})\s*(?:breaths|/min)',
            'oxygen_saturation': r'(?:SpO2|O2 Sat|Oxygen Saturation)[:\s]*(\d{2,3})\s*%',
            'height': r'(?:Height)[:\s]*(\d{2,3}\.?\d*)\s*(?:cm|in)',
            'weight': r'(?:Weight)[:\s]*(\d{2,3}\.?\d*)\s*(?:kg|lbs)',
            'bmi': r'(?:BMI)[:\s]*(\d{1,2}\.?\d*)'
        }
        
        self.medication_pattern = r'(?:^|\n)\d+\.\s*([A-Z][a-z]+(?:\s+[A-Z]?[a-z]+)*)\s+(\d+\s*(?:mg|mcg|g|ml|units?))\s*(?:PO|IV|IM|SC|SL|PR)?'
        
        self.icd_pattern = r'([A-Z]\d{2}(?:\.\d{1,2})?)'
        
    def extract_text_from_pdf(self, file_path: str) -> str:
        """
        Extract text from PDF using available library.
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            Extracted text content
        """
        if not Path(file_path).exists():
            raise FileNotFoundError(f"PDF file not found: {file_path}")
        
        # Try PyMuPDF first (better text extraction)
        if PYMUPDF_AVAILABLE:
            try:
                doc = fitz.open(file_path)
                text = ""
                for page in doc:
                    text += page.get_text()
                doc.close()
                return text
            except Exception as e:
                logger.error(f"PyMuPDF extraction failed: {e}")
        
        # Fallback to PyPDF2
        if PYPDF2_AVAILABLE:
            try:
                with open(file_path, 'rb') as file:
                    reader = PyPDF2.PdfReader(file)
                    text = ""
                    for page in reader.pages:
                        text += page.extract_text()
                    return text
            except Exception as e:
                logger.error(f"PyPDF2 extraction failed: {e}")
        
        raise RuntimeError("No PDF library available. Install PyMuPDF or PyPDF2.")
    
    def extract_vitals(self, text: str) -> Dict[str, Any]:
        """
        Extract vital signs from medical report text.
        
        Args:
            text: Medical report text content
            
        Returns:
            Dictionary of vital signs
        """
        vitals = {}
        
        for vital_name, pattern in self.vitals_patterns.items():
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                if vital_name == 'blood_pressure':
                    vitals[vital_name] = f"{match.group(1)}/{match.group(2)}"
                else:
                    value = match.group(1)
                    try:
                        # Try to convert to appropriate type
                        if '.' in value:
                            vitals[vital_name] = float(value)
                        else:
                            vitals[vital_name] = int(value)
                    except ValueError:
                        vitals[vital_name] = value
        
        return vitals
    
    def extract_medications(self, text: str) -> List[Dict[str, str]]:
        """
        Extract medications from medical report text.
        
        Args:
            text: Medical report text content
            
        Returns:
            List of medication dictionaries
        """
        medications = []
        
        # Look for medication sections
        med_section_pattern = r'(?:Medications?|Current Medications?|Prescriptions?)[:\s]*(.*?)(?:\n\n|\Z)'
        med_section_match = re.search(med_section_pattern, text, re.IGNORECASE | re.DOTALL)
        
        if med_section_match:
            med_text = med_section_match.group(1)
            
            # Extract individual medications
            for match in re.finditer(self.medication_pattern, med_text, re.MULTILINE):
                med = {
                    'name': match.group(1).strip(),
                    'dose': match.group(2).strip()
                }
                
                # Try to extract frequency
                med_line = match.group(0)
                freq_pattern = r'(?:once|twice|three times|four times|QD|BID|TID|QID|PRN)\s*(?:daily|a day)?'
                freq_match = re.search(freq_pattern, med_line, re.IGNORECASE)
                if freq_match:
                    med['frequency'] = freq_match.group(0).strip()
                
                medications.append(med)
        
        return medications
    
    def extract_lab_results(self, text: str) -> Dict[str, Dict[str, Any]]:
        """
        Extract laboratory results from medical report text.
        
        Args:
            text: Medical report text content
            
        Returns:
            Dictionary of lab results organized by test type
        """
        lab_results = {
            'cbc': {},
            'metabolic': {},
            'lipid': {},
            'other': {}
        }
        
        # CBC patterns
        cbc_patterns = {
            'wbc': r'(?:WBC|White Blood Cell)[:\s]*(\d+\.?\d*)',
            'rbc': r'(?:RBC|Red Blood Cell)[:\s]*(\d+\.?\d*)',
            'hemoglobin': r'(?:Hb|Hemoglobin|Hgb)[:\s]*(\d+\.?\d*)',
            'hematocrit': r'(?:Hct|Hematocrit)[:\s]*(\d+\.?\d*)',
            'platelets': r'(?:Plt|Platelets?)[:\s]*(\d+\.?\d*)'
        }
        
        # Metabolic panel patterns
        metabolic_patterns = {
            'glucose': r'(?:Glucose|Blood Sugar)[:\s]*(\d+\.?\d*)',
            'sodium': r'(?:Na|Sodium)[:\s]*(\d+\.?\d*)',
            'potassium': r'(?:K|Potassium)[:\s]*(\d+\.?\d*)',
            'chloride': r'(?:Cl|Chloride)[:\s]*(\d+\.?\d*)',
            'creatinine': r'(?:Creatinine|Cr)[:\s]*(\d+\.?\d*)',
            'bun': r'(?:BUN|Blood Urea Nitrogen)[:\s]*(\d+\.?\d*)'
        }
        
        # Lipid panel patterns
        lipid_patterns = {
            'total_cholesterol': r'(?:Total Cholesterol|Cholesterol)[:\s]*(\d+\.?\d*)',
            'hdl': r'(?:HDL|HDL Cholesterol)[:\s]*(\d+\.?\d*)',
            'ldl': r'(?:LDL|LDL Cholesterol)[:\s]*(\d+\.?\d*)',
            'triglycerides': r'(?:Triglycerides|TG)[:\s]*(\d+\.?\d*)'
        }
        
        # Extract CBC values
        for test, pattern in cbc_patterns.items():
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    lab_results['cbc'][test] = float(match.group(1))
                except ValueError:
                    lab_results['cbc'][test] = match.group(1)
        
        # Extract metabolic panel values
        for test, pattern in metabolic_patterns.items():
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    lab_results['metabolic'][test] = float(match.group(1))
                except ValueError:
                    lab_results['metabolic'][test] = match.group(1)
        
        # Extract lipid panel values
        for test, pattern in lipid_patterns.items():
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    lab_results['lipid'][test] = float(match.group(1))
                except ValueError:
                    lab_results['lipid'][test] = match.group(1)
        
        return lab_results
    
    def extract_diagnoses(self, text: str) -> List[Dict[str, str]]:
        """
        Extract diagnoses and ICD codes from medical report text.
        
        Args:
            text: Medical report text content
            
        Returns:
            List of diagnosis dictionaries with codes and descriptions
        """
        diagnoses = []
        
        # Look for diagnosis sections
        dx_section_pattern = r'(?:Diagnos[ie]s?|Impression|Assessment)[:\s]*(.*?)(?:\n\n|\Z)'
        dx_section_match = re.search(dx_section_pattern, text, re.IGNORECASE | re.DOTALL)
        
        if dx_section_match:
            dx_text = dx_section_match.group(1)
            
            # Find all lines with potential diagnoses
            lines = dx_text.split('\n')
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Look for ICD codes
                icd_match = re.search(self.icd_pattern, line)
                code = icd_match.group(1) if icd_match else None
                
                # Extract description (remove numbering, ICD codes)
                description = re.sub(r'^\d+\.?\s*', '', line)
                description = re.sub(self.icd_pattern, '', description).strip()
                description = re.sub(r'[(\[].*?[)\]]', '', description).strip()
                
                if description:
                    diagnoses.append({
                        'code': code or 'Unknown',
                        'description': description
                    })
        
        return diagnoses
    
    def extract_allergies(self, text: str) -> List[Dict[str, str]]:
        """
        Extract allergies from medical report text.
        
        Args:
            text: Medical report text content
            
        Returns:
            List of allergy dictionaries
        """
        allergies = []
        
        # Look for allergy sections
        allergy_section_pattern = r'(?:Allergies?|Adverse Reactions?)[:\s]*(.*?)(?:\n\n|\Z)'
        allergy_section_match = re.search(allergy_section_pattern, text, re.IGNORECASE | re.DOTALL)
        
        if allergy_section_match:
            allergy_text = allergy_section_match.group(1)
            
            # Common allergy formats
            lines = allergy_text.split('\n')
            for line in lines:
                line = line.strip()
                if not line or line.lower() in ['none', 'nkda', 'no known allergies']:
                    continue
                
                # Remove numbering
                line = re.sub(r'^\d+\.?\s*', '', line)
                
                allergy = {'allergen': line}
                
                # Try to extract reaction
                if '-' in line or ':' in line:
                    parts = re.split(r'[-:]', line, maxsplit=1)
                    if len(parts) == 2:
                        allergy['allergen'] = parts[0].strip()
                        allergy['reaction'] = parts[1].strip()
                
                # Try to extract severity
                severity_pattern = r'\b(mild|moderate|severe)\b'
                severity_match = re.search(severity_pattern, line, re.IGNORECASE)
                if severity_match:
                    allergy['severity'] = severity_match.group(1).capitalize()
                
                allergies.append(allergy)
        
        return allergies
    
    def process_report(self, file_path: str) -> Dict[str, Any]:
        """
        Process a complete medical report and extract all structured data.
        
        Args:
            file_path: Path to PDF medical report
            
        Returns:
            Dictionary containing all extracted medical data
        """
        # Extract text
        text = self.extract_text_from_pdf(file_path)
        
        # Extract all components
        report_data = {
            'vitals': self.extract_vitals(text),
            'medications': self.extract_medications(text),
            'lab_results': self.extract_lab_results(text),
            'diagnoses': self.extract_diagnoses(text),
            'allergies': self.extract_allergies(text),
            'raw_text': text[:5000]  # First 5000 chars for reference
        }
        
        return report_data


# Singleton instance
pdf_processor = MedicalReportProcessor()
