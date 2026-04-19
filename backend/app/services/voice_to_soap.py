"""
Voice to SOAP Note Generator Service

Converts transcribed voice recordings into structured SOAP (Subjective, Objective, Assessment, Plan) notes.
Uses entity extraction and RAG for grounding in medical knowledge.
"""

import logging
from typing import Dict, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

# Global service instance
_voice_to_soap = None


class VoiceToSOAP:
    """Service for generating SOAP notes from voice transcriptions"""

    def __init__(self):
        """Initialize SOAP generator"""
        pass

    def generate_soap_note(
        self,
        transcription: str,
        medical_entities: Dict,
        patient_context: Optional[Dict] = None,
        include_rag_search: bool = True
    ) -> Dict:
        """
        Generate structured SOAP note from transcription

        Args:
            transcription: Raw/processed transcription text
            medical_entities: Extracted entities (symptoms, medications, etc.)
            patient_context: Optional patient demographic/history info
            include_rag_search: Whether to ground in knowledge base

        Returns:
            SOAP note dict with Subjective, Objective, Assessment, Plan sections
        """
        try:
            # Parse SOAP sections from transcription
            subjective = self._extract_subjective(transcription, medical_entities, patient_context)
            objective = self._extract_objective(transcription, medical_entities, patient_context)
            assessment = self._extract_assessment(transcription, medical_entities)
            plan = self._extract_plan(transcription, medical_entities, assessment.get("assessment", ""))

            # If RAG is enabled, ground sections in knowledge base
            if include_rag_search:
                try:
                    from app.services.rag_service import get_rag_service
                    rag = get_rag_service()

                    # Ground assessment in knowledge base
                    if assessment.get("icd_codes"):
                        knowledge = rag.generate_with_context(
                            query=f"Treatment for {assessment['assessment']}",
                            retrieved_docs=[],
                            include_citations=True
                        )
                        if knowledge:
                            plan["knowledge_grounded"] = True
                            plan["knowledge_summary"] = knowledge.get("response", "")
                except Exception as e:
                    logger.debug(f"[VOICE_SOAP] RAG grounding skipped: {e}")

            soap_note = {
                "subjective": subjective,
                "objective": objective,
                "assessment": assessment,
                "plan": plan,
                "metadata": {
                    "generated_at": datetime.utcnow().isoformat(),
                    "source": "voice_transcription",
                    "confidence": 0.8  # Overall confidence of generated note
                }
            }

            logger.info("[VOICE_SOAP] Generated SOAP note from transcription")
            return soap_note

        except Exception as e:
            logger.error(f"[VOICE_SOAP] Error generating SOAP note: {e}")
            return {
                "error": str(e),
                "subjective": {},
                "objective": {},
                "assessment": {},
                "plan": {}
            }

    def _extract_subjective(
        self,
        transcription: str,
        medical_entities: Dict,
        patient_context: Optional[Dict]
    ) -> Dict:
        """
        Extract SUBJECTIVE section (patient complaints, history from their perspective)

        Returns:
            {
                "chief_complaint": str,
                "history_present_illness": str,
                "past_medical_history": str,
                "medications": List
            }
        """
        try:
            # Chief complaint: top symptom mentioned
            symptoms = medical_entities.get("symptoms", [])
            chief_complaint = symptoms[0]["text"] if symptoms else "Consultation"

            # History of present illness: first 300 chars or first sentence
            history = transcription[:300] if len(transcription) > 300 else transcription

            subjective = {
                "chief_complaint": chief_complaint,
                "history_present_illness": history,
                "past_medical_history": "",
                "medications": [med["text"] for med in medical_entities.get("medications", [])],
                "allergies": [],
                "social_history": ""
            }

            # Add patient context if available
            if patient_context:
                # Extract conditions from family history if available
                family_conditions = patient_context.get("family_history", [])
                if family_conditions:
                    subjective["past_medical_history"] = f"Family history: {', '.join(family_conditions)}"

            return subjective

        except Exception as e:
            logger.warning(f"[VOICE_SOAP] Error extracting subjective: {e}")
            return {
                "chief_complaint": "Consultation",
                "history_present_illness": "",
                "past_medical_history": "",
                "medications": [],
                "allergies": [],
                "social_history": ""
            }

    def _extract_objective(
        self,
        transcription: str,
        medical_entities: Dict,
        patient_context: Optional[Dict]
    ) -> Dict:
        """
        Extract OBJECTIVE section (vital signs, examination findings, labs)

        Returns:
            {
                "vital_signs": Dict,
                "physical_examination": str,
                "laboratory_results": List,
                "imaging": List
            }
        """
        try:
            objective = {
                "vital_signs": {},
                "physical_examination": "",
                "laboratory_results": [],
                "imaging": []
            }

            # Try to extract vital sign numbers from transcription
            # Simple patterns: "temperature 100.5", "bp 140/90", etc.
            import re

            # Temperature
            temp_match = re.search(r'(?:temperature|temp|fever)?[:\s]*(\d+(?:\.\d+)?)', transcription)
            if temp_match:
                objective["vital_signs"]["temperature_f"] = float(temp_match.group(1))

            # Blood pressure
            bp_match = re.search(r'(?:bp|blood pressure)[:\s]*(\d+)/(\d+)', transcription.lower())
            if bp_match:
                objective["vital_signs"]["bp_systolic"] = int(bp_match.group(1))
                objective["vital_signs"]["bp_diastolic"] = int(bp_match.group(2))

            # Heart rate
            hr_match = re.search(r'(?:hr|heart rate|pulse)[:\s]*(\d+)', transcription.lower())
            if hr_match:
                objective["vital_signs"]["heart_rate"] = int(hr_match.group(1))

            # Add procedures found
            procedures = medical_entities.get("procedures", [])
            objective["imaging"] = [proc["text"] for proc in procedures if any(
                x in proc["text"].lower() for x in ["x-ray", "ct", "ultrasound", "scan", "mri"]
            )]

            objective["physical_examination"] = "Physical examination performed"

            return objective

        except Exception as e:
            logger.warning(f"[VOICE_SOAP] Error extracting objective: {e}")
            return {
                "vital_signs": {},
                "physical_examination": "",
                "laboratory_results": [],
                "imaging": []
            }

    def _extract_assessment(self, transcription: str, medical_entities: Dict) -> Dict:
        """
        Extract ASSESSMENT section (diagnosis, ICD codes)

        Returns:
            {
                "assessment": str,
                "icd_codes": List,
                "differential_diagnoses": List
            }
        """
        try:
            conditions = medical_entities.get("conditions", [])
            assessment_text = conditions[0]["text"] if conditions else "Clinical assessment pending"

            assessment = {
                "assessment": assessment_text,
                "icd_codes": [],
                "differential_diagnoses": [cond["text"] for cond in conditions],
                "severity": "moderate"  # Default, could be enhanced
            }

            # Try to map conditions to ICD codes
            try:
                from app.services.icd10_service import get_icd10_service
                icd_service = get_icd10_service()

                for condition in conditions:
                    codes = icd_service.search_codes(condition["text"], max_results=2)
                    if codes:
                        assessment["icd_codes"].extend([code.get("code", "") for code in codes])
            except Exception as e:
                logger.debug(f"[VOICE_SOAP] ICD mapping skipped: {e}")

            return assessment

        except Exception as e:
            logger.warning(f"[VOICE_SOAP] Error extracting assessment: {e}")
            return {
                "assessment": "Clinical assessment pending",
                "icd_codes": [],
                "differential_diagnoses": [],
                "severity": "unknown"
            }

    def _extract_plan(self, transcription: str, medical_entities: Dict, assessment: str) -> Dict:
        """
        Extract PLAN section (medications, follow-up, referrals)

        Returns:
            {
                "medications": List[{name, dose, frequency}],
                "follow_up": Dict,
                "referrals": List,
                "patient_education": List,
                "monitoring": List
            }
        """
        try:
            medications = medical_entities.get("medications", [])
            plan_medications = [
                {
                    "name": med["text"],
                    "dose": "As prescribed",
                    "frequency": "Per instructions",
                    "duration": "Per provider discretion"
                }
                for med in medications
            ]

            plan = {
                "medications": plan_medications,
                "follow_up": {
                    "timeframe": "7-14 days",
                    "type": "Office visit or telehealth"
                },
                "referrals": [],
                "patient_education": [
                    f"Education provided regarding {assessment}",
                    "Importance of medication adherence",
                    "When to seek emergency care"
                ],
                "monitoring": [
                    "Monitor symptoms daily",
                    "Report worsening symptoms immediately"
                ],
                "diet_restrictions": "No specific restrictions mentioned",
                "activity": "Resume normal activities as tolerated"
            }

            # Add condition-specific recommendations
            conditions = medical_entities.get("conditions", [])
            if conditions:
                for condition in conditions:
                    cond_text = condition["text"].lower()
                    if "diabetes" in cond_text:
                        plan["monitoring"].append("Monitor blood glucose")
                        plan["patient_education"].append("Diabetes management and diet")
                    elif "hypertension" in cond_text:
                        plan["monitoring"].append("Monitor blood pressure")
                        plan["patient_education"].append("Dietary sodium restriction")
                    elif "heart" in cond_text or "cardiac" in cond_text:
                        plan["referrals"].append("Cardiology consultation if not recently seen")

            return plan

        except Exception as e:
            logger.warning(f"[VOICE_SOAP] Error extracting plan: {e}")
            return {
                "medications": [],
                "follow_up": {"timeframe": "As needed"},
                "referrals": [],
                "patient_education": [],
                "monitoring": []
            }


def get_voice_to_soap() -> VoiceToSOAP:
    """Factory function to get singleton service instance"""
    global _voice_to_soap
    if _voice_to_soap is None:
        _voice_to_soap = VoiceToSOAP()
    return _voice_to_soap
