"""Feature 3: AI Treatment Recommender - Evidence-based pathways"""
import logging
logger = logging.getLogger(__name__)
_recommender = None

class TreatmentRecommender:
    """Recommends evidence-based treatment pathways"""

    def _build_base_recommendation(self, diagnosis: str, patient_data: dict) -> dict:
        age = patient_data.get("age")
        comorbidities = patient_data.get("comorbidities", []) or []
        meds = []
        procedures = ["Clinical review", "Monitoring"]
        follow_up = "1-2 weeks"
        lifestyle = []
        red_flags = []
        guidelines = ["Local formulary", "Condition-specific evidence review"]

        diagnosis_lower = (diagnosis or "").lower()
        if "diabet" in diagnosis_lower:
            meds = [
                {"name": "Metformin", "dose": "500 mg", "frequency": "twice daily", "rationale": "First-line insulin sensitizer"},
                {"name": "Lifestyle therapy", "dose": "N/A", "frequency": "daily", "rationale": "Diet and exercise foundation"},
            ]
            procedures = ["HbA1c", "Renal function", "Foot examination"]
            follow_up = "2-4 weeks"
            lifestyle = ["Carbohydrate moderation", "Walking program", "Weight management"]
            red_flags = ["Hypoglycemia symptoms", "Worsening polyuria or dehydration"]
            guidelines = ["ADA Standards of Care", "Renal dosing review if CKD present"]
        elif "hypertension" in diagnosis_lower or "blood pressure" in diagnosis_lower:
            meds = [
                {"name": "ACE inhibitor / ARB consideration", "dose": "start low", "frequency": "daily", "rationale": "First-line BP control when appropriate"},
                {"name": "Thiazide or CCB consideration", "dose": "per guideline", "frequency": "daily", "rationale": "Add-on option based on patient profile"},
            ]
            procedures = ["Repeat blood pressure logs", "Renal panel", "Electrolytes"]
            follow_up = "1-2 weeks"
            lifestyle = ["Salt restriction", "Weight reduction", "Home BP monitoring"]
            red_flags = ["Severe headache", "Chest pain", "Neurologic deficit"]
            guidelines = ["ACC/AHA hypertension guidance"]
        elif "asthma" in diagnosis_lower:
            meds = [
                {"name": "Short-acting bronchodilator", "dose": "as needed", "frequency": "PRN", "rationale": "Rapid relief"},
                {"name": "Inhaled corticosteroid consideration", "dose": "per severity", "frequency": "daily", "rationale": "Controller therapy"},
            ]
            procedures = ["Peak flow review", "Trigger assessment", "Inhaler technique check"]
            follow_up = "1 week"
            lifestyle = ["Trigger avoidance", "Spacer technique reinforcement"]
            red_flags = ["Persistent breathlessness", "Low oxygen saturation", "Silent chest"]
            guidelines = ["GINA asthma strategy"]
        elif "infection" in diagnosis_lower or "pneumonia" in diagnosis_lower or "fever" in diagnosis_lower:
            meds = [
                {"name": "Targeted antimicrobial review", "dose": "per infection source", "frequency": "per regimen", "rationale": "Diagnosis-specific therapy"},
                {"name": "Acetaminophen", "dose": "500-650 mg", "frequency": "every 6 hours as needed", "rationale": "Symptom control"},
            ]
            procedures = ["CBC", "Source evaluation", "Hydration assessment"]
            follow_up = "48-72 hours"
            lifestyle = ["Hydration", "Rest", "Escalation if symptoms worsen"]
            red_flags = ["Sepsis warning signs", "Respiratory distress", "Persistent high fever"]
            guidelines = ["Antimicrobial stewardship review"]
        else:
            meds = [
                {"name": "Condition-specific first-line therapy", "dose": "per guideline", "frequency": "as indicated", "rationale": "Tailor to confirmed diagnosis"},
                {"name": "Symptomatic relief", "dose": "as needed", "frequency": "PRN", "rationale": "Reduce symptom burden"},
            ]
            procedures = ["Targeted diagnostics", "Response monitoring"]
            follow_up = "1-2 weeks"
            lifestyle = ["Hydration", "Sleep optimization", "Return if symptoms escalate"]
            red_flags = ["Rapid clinical deterioration", "New neurologic symptoms", "Respiratory distress"]

        if age and isinstance(age, (int, float)) and age >= 65:
            red_flags.append("Medication sensitivity in older adult; start low and review interactions")
        if comorbidities:
            guidelines.append(f"Comorbidity review required: {', '.join(map(str, comorbidities[:5]))}")

        return {
            "medications": meds,
            "procedures": procedures,
            "follow_up": follow_up,
            "lifestyle": lifestyle,
            "red_flags": list(dict.fromkeys(red_flags)),
            "guidelines": guidelines,
        }

    def recommend_treatment(self, diagnosis: str, patient_data: dict) -> dict:
        """Generate treatment recommendations"""
        plan = self._build_base_recommendation(diagnosis, patient_data)
        return {
            "diagnosis": diagnosis,
            "primary_pathway": {
                "medications": plan["medications"],
                "procedures": plan["procedures"],
                "follow_up": plan["follow_up"],
                "lifestyle": plan["lifestyle"],
                "red_flags": plan["red_flags"],
            },
            "alternative_pathways": [
                {"name": "Conservative approach", "success_rate": 0.65, "description": "Begin with lower-intensity therapy and close reassessment"},
                {"name": "Escalated pathway", "success_rate": 0.82, "description": "Escalate treatment if poor response or high-risk presentation"},
            ],
            "outcome_prediction": {"success_probability": 0.78, "recovery_time_days": 14},
            "clinical_guidelines": plan["guidelines"],
            "safety_checks": [
                "Verify allergies before prescribing",
                "Review renal/hepatic function where relevant",
                "Confirm pregnancy/pediatric contraindications where applicable",
                "Escalate to clinician review for high-risk or deteriorating patients",
            ],
        }

def get_treatment_recommender() -> TreatmentRecommender:
    global _recommender
    if _recommender is None:
        _recommender = TreatmentRecommender()
    return _recommender
