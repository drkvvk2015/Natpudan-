"""Feature 4: Discharge Planning AI - Readmission prevention"""
import logging
logger = logging.getLogger(__name__)
_discharge_engine = None

class DischargePlanningEngine:
    """Creates personalized discharge plans to prevent readmission"""
    
    def generate_discharge_plan(self, patient_id: int, readmission_risk: float) -> dict:
        """Generate personalized discharge checklist"""
        urgency = "URGENT" if readmission_risk > 0.7 else "HIGH" if readmission_risk > 0.5 else "STANDARD"
        
        return {
            "urgency": urgency,
            "follow_up_timeline": {
                "day_1": ["Call patient", "Confirm pharmacy filled meds"],
                "day_3": ["Telehealth check-in", "Monitor vitals"],
                "day_7": ["In-person follow-up"],
                "day_14": ["Routine follow-up"],
                "day_30": ["Post-discharge assessment"]
            },
            "home_health": "YES" if readmission_risk > 0.6 else "NO",
            "medication_review": "YES" if readmission_risk > 0.5 else "NO",
            "specialist_referrals": ["Cardiology" if readmission_risk > 0.6 else None],
            "patient_education": ["Medication compliance", "Diet restrictions", "Warning signs"],
            "social_support": ["Case manager", "Community resources"],
            "predicted_readmission_reduction": f"{(1 - readmission_risk) * 100:.1f}%"
        }

def get_discharge_planning_engine() -> DischargePlanningEngine:
    global _discharge_engine
    if _discharge_engine is None:
        _discharge_engine = DischargePlanningEngine()
    return _discharge_engine
