"""
MIMIC-III Data Loader Service
Handles loading and ingestion of MIMIC-III medical dataset with clinical notes.

MIMIC-III: Large, freely-available database of de-identified ICU stays
- Clinical notes (discharge summaries, radiology reports, nursing notes)
- Medical procedures, medications, diagnoses, lab results
- High-quality, real clinical data for training medical AI models

Free access: Requires PhysioNet credentialed access (free upon signup)
Location: https://physionet.org/content/mimiciii/

Usage:
    loader = MIMIC3Loader(mimic_data_dir="/path/to/mimic3")
    loader.load_discharge_summaries(limit=1000)  # Load first 1000 discharge summaries
    loader.load_radiology_reports(limit=500)      # Load first 500 radiology reports
    docs = loader.get_loaded_documents()           # Get all loaded documents
"""

import os
import json
import csv
import gzip
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path
import asyncio

logger = logging.getLogger(__name__)


class MIMIC3Loader:
    """Load and process MIMIC-III clinical data for medical KB ingestion"""
    
    def __init__(self, mimic_data_dir: str = "/data/mimic-iii"):
        """
        Initialize MIMIC-III loader.
        
        Args:
            mimic_data_dir: Path to MIMIC-III data directory
        """
        self.data_dir = Path(mimic_data_dir)
        self.loaded_documents = []
        self.stats = {
            "discharge_summaries": 0,
            "radiology_reports": 0,
            "lab_events": 0,
            "medication_events": 0,
            "total_documents": 0
        }
        
    def load_discharge_summaries(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Load discharge summaries from MIMIC-III.
        
        These are the highest-quality clinical notes, typically 500-2000 words,
        summarizing patient's hospital course, diagnoses, and treatment.
        
        Args:
            limit: Maximum number of discharge summaries to load
            
        Returns:
            List of discharge summary documents
        """
        documents = []
        file_path = self.data_dir / "NOTEEVENTS.csv.gz"
        
        if not file_path.exists():
            logger.warning(f"MIMIC-III discharge summaries file not found: {file_path}")
            return documents
        
        try:
            count = 0
            with gzip.open(file_path, 'rt', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # Filter for discharge summaries (CATEGORY='Discharge summary')
                    if row.get('CATEGORY', '').lower() == 'discharge summary':
                        doc = {
                            "document_id": f"mimic3_discharge_{row.get('ROW_ID')}",
                            "filename": f"discharge_summary_{row.get('HADM_ID')}.txt",
                            "content": row.get('TEXT', ''),
                            "category": "discharge_summary",
                            "source": "MIMIC-III",
                            "hadm_id": row.get('HADM_ID'),
                            "note_id": row.get('NOTE_ID'),
                            "subject_id": row.get('SUBJECT_ID'),
                            "chartdate": row.get('CHARTDATE'),
                            "charttime": row.get('CHARTTIME'),
                            "metadata": {
                                "source": "MIMIC-III",
                                "note_type": "Discharge Summary",
                                "hadm_id": row.get('HADM_ID'),
                                "date": row.get('CHARTDATE')
                            }
                        }
                        documents.append(doc)
                        count += 1
                        
                        if limit and count >= limit:
                            break
            
            self.stats["discharge_summaries"] += len(documents)
            self.loaded_documents.extend(documents)
            logger.info(f"✅ Loaded {len(documents)} MIMIC-III discharge summaries")
            
        except Exception as e:
            logger.error(f"❌ Error loading discharge summaries: {e}")
        
        return documents
    
    def load_radiology_reports(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Load radiology reports from MIMIC-III.
        
        Radiology reports contain imaging findings and clinical interpretations.
        
        Args:
            limit: Maximum number of radiology reports to load
            
        Returns:
            List of radiology report documents
        """
        documents = []
        file_path = self.data_dir / "NOTEEVENTS.csv.gz"
        
        if not file_path.exists():
            logger.warning(f"MIMIC-III radiology reports file not found: {file_path}")
            return documents
        
        try:
            count = 0
            with gzip.open(file_path, 'rt', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # Filter for radiology reports
                    if row.get('CATEGORY', '').lower() == 'radiology':
                        doc = {
                            "document_id": f"mimic3_radiology_{row.get('ROW_ID')}",
                            "filename": f"radiology_report_{row.get('HADM_ID')}.txt",
                            "content": row.get('TEXT', ''),
                            "category": "radiology_report",
                            "source": "MIMIC-III",
                            "hadm_id": row.get('HADM_ID'),
                            "metadata": {
                                "source": "MIMIC-III",
                                "note_type": "Radiology Report",
                                "hadm_id": row.get('HADM_ID'),
                                "date": row.get('CHARTDATE')
                            }
                        }
                        documents.append(doc)
                        count += 1
                        
                        if limit and count >= limit:
                            break
            
            self.stats["radiology_reports"] += len(documents)
            self.loaded_documents.extend(documents)
            logger.info(f"✅ Loaded {len(documents)} MIMIC-III radiology reports")
            
        except Exception as e:
            logger.error(f"❌ Error loading radiology reports: {e}")
        
        return documents
    
    def load_lab_events(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Load lab events (test results) from MIMIC-III.
        
        Lab events contain quantitative medical test results with clinical significance.
        
        Args:
            limit: Maximum number of lab events to load
            
        Returns:
            List of lab event documents
        """
        documents = []
        file_path = self.data_dir / "LABEVENTS.csv.gz"
        
        if not file_path.exists():
            logger.warning(f"MIMIC-III lab events file not found: {file_path}")
            return documents
        
        try:
            count = 0
            with gzip.open(file_path, 'rt', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # Create structured lab result documents
                    itemid = row.get('ITEMID', '')
                    value = row.get('VALUE', '')
                    uom = row.get('VALUEUOM', '')
                    
                    if value and itemid:  # Only include rows with actual values
                        doc = {
                            "document_id": f"mimic3_lab_{row.get('ROW_ID')}",
                            "filename": f"lab_event_{row.get('HADM_ID')}.txt",
                            "content": f"Lab Test {itemid}: {value} {uom}. Result date: {row.get('CHARTTIME')}",
                            "category": "lab_result",
                            "source": "MIMIC-III",
                            "hadm_id": row.get('HADM_ID'),
                            "metadata": {
                                "source": "MIMIC-III",
                                "lab_item_id": itemid,
                                "value": value,
                                "unit": uom,
                                "date": row.get('CHARTTIME')
                            }
                        }
                        documents.append(doc)
                        count += 1
                        
                        if limit and count >= limit:
                            break
            
            self.stats["lab_events"] += len(documents)
            self.loaded_documents.extend(documents)
            logger.info(f"✅ Loaded {len(documents)} MIMIC-III lab events")
            
        except Exception as e:
            logger.error(f"❌ Error loading lab events: {e}")
        
        return documents
    
    def load_medications(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Load medication prescriptions from MIMIC-III.
        
        Medication data includes drug names, dosages, routes, frequencies.
        
        Args:
            limit: Maximum number of medication records to load
            
        Returns:
            List of medication documents
        """
        documents = []
        file_path = self.data_dir / "PRESCRIPTIONS.csv.gz"
        
        if not file_path.exists():
            logger.warning(f"MIMIC-III medications file not found: {file_path}")
            return documents
        
        try:
            count = 0
            with gzip.open(file_path, 'rt', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    drug = row.get('DRUG', '')
                    dose = row.get('DOSE_VAL_RX', '')
                    route = row.get('ROUTE', '')
                    
                    if drug:
                        doc = {
                            "document_id": f"mimic3_medication_{row.get('ROW_ID')}",
                            "filename": f"medication_{row.get('HADM_ID')}.txt",
                            "content": f"Medication: {drug}. Dose: {dose}. Route: {route}",
                            "category": "medication",
                            "source": "MIMIC-III",
                            "hadm_id": row.get('HADM_ID'),
                            "metadata": {
                                "source": "MIMIC-III",
                                "drug": drug,
                                "dose": dose,
                                "route": route,
                                "start_date": row.get('STARTDATE'),
                                "end_date": row.get('ENDDATE')
                            }
                        }
                        documents.append(doc)
                        count += 1
                        
                        if limit and count >= limit:
                            break
            
            self.stats["medication_events"] += len(documents)
            self.loaded_documents.extend(documents)
            logger.info(f"✅ Loaded {len(documents)} MIMIC-III medications")
            
        except Exception as e:
            logger.error(f"❌ Error loading medications: {e}")
        
        return documents
    
    def get_loaded_documents(self) -> List[Dict[str, Any]]:
        """Get all loaded documents"""
        return self.loaded_documents
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get loading statistics"""
        self.stats["total_documents"] = len(self.loaded_documents)
        return self.stats
    
    def clear(self):
        """Clear loaded documents"""
        self.loaded_documents = []
        self.stats = {k: 0 for k in self.stats.keys()}


def get_mimic3_loader(data_dir: str = "/data/mimic-iii") -> MIMIC3Loader:
    """Factory function to get MIMIC3 loader instance"""
    return MIMIC3Loader(mimic_data_dir=data_dir)
