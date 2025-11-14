"""
ICD-10 Code Service - Comprehensive ICD-10 CM database and search functionality
"""

import logging
from typing import List, Dict, Optional, Tuple
import re
from sqlalchemy.orm import Session
from sqlalchemy import or_, func

logger = logging.getLogger(__name__)


class ICD10Service:
    """
    Service for searching and managing ICD-10-CM codes.
    Provides comprehensive medical diagnosis code lookup with fuzzy search.
    """
    
    # Comprehensive ICD-10 code database (sample - can be extended)
    ICD10_DATABASE = {
        # Infectious and parasitic diseases (A00-B99)
        "A00": "Cholera",
        "A00.0": "Cholera due to Vibrio cholerae 01, biovar cholerae",
        "A00.1": "Cholera due to Vibrio cholerae 01, biovar eltor",
        "A00.9": "Cholera, unspecified",
        "A01": "Typhoid and paratyphoid fevers",
        "A01.0": "Typhoid fever",
        "A01.1": "Paratyphoid fever A",
        "A01.2": "Paratyphoid fever B",
        "A01.3": "Paratyphoid fever C",
        "A01.4": "Paratyphoid fever, unspecified",
        "A02": "Other salmonella infections",
        "A09": "Infectious gastroenteritis and colitis, unspecified",
        "A15": "Respiratory tuberculosis",
        "A15.0": "Tuberculosis of lung",
        "A15.4": "Tuberculosis of intrathoracic lymph nodes",
        "A15.5": "Tuberculosis of larynx, trachea and bronchus",
        "A15.6": "Tuberculous pleurisy",
        "A15.7": "Primary respiratory tuberculosis",
        "A15.8": "Other respiratory tuberculosis",
        "A15.9": "Respiratory tuberculosis unspecified",
        "B00": "Herpesviral [herpes simplex] infections",
        "B01": "Varicella [chickenpox]",
        "B02": "Zoster [herpes zoster]",
        "B05": "Measles",
        "B06": "Rubella [German measles]",
        "B15": "Acute hepatitis A",
        "B16": "Acute hepatitis B",
        "B17": "Other acute viral hepatitis",
        "B18": "Chronic viral hepatitis",
        "B19": "Unspecified viral hepatitis",
        "B20": "Human immunodeficiency virus [HIV] disease",
        "B25": "Cytomegaloviral disease",
        "B34": "Viral infection of unspecified site",
        "B34.9": "Viral infection, unspecified",
        "B95": "Streptococcus, Staphylococcus, and Enterococcus as the cause of diseases",
        "B96": "Other bacterial agents as the cause of diseases",
        "B97": "Viral agents as the cause of diseases",
        
        # Neoplasms (C00-D49)
        "C34": "Malignant neoplasm of bronchus and lung",
        "C34.90": "Malignant neoplasm of unspecified part of unspecified bronchus or lung",
        "C50": "Malignant neoplasm of breast",
        "C61": "Malignant neoplasm of prostate",
        "C80": "Malignant neoplasm without specification of site",
        "C80.1": "Malignant (primary) neoplasm, unspecified",
        "D50": "Iron deficiency anemia",
        "D50.0": "Iron deficiency anemia secondary to blood loss (chronic)",
        "D50.9": "Iron deficiency anemia, unspecified",
        
        # Diseases of the blood (D50-D89)
        "D64": "Other anemias",
        "D68": "Other coagulation defects",
        "D69": "Purpura and other hemorrhagic conditions",
        
        # Endocrine, nutritional and metabolic diseases (E00-E89)
        "E10": "Type 1 diabetes mellitus",
        "E10.9": "Type 1 diabetes mellitus without complications",
        "E10.65": "Type 1 diabetes mellitus with hyperglycemia",
        "E11": "Type 2 diabetes mellitus",
        "E11.9": "Type 2 diabetes mellitus without complications",
        "E11.65": "Type 2 diabetes mellitus with hyperglycemia",
        "E11.21": "Type 2 diabetes mellitus with diabetic nephropathy",
        "E11.22": "Type 2 diabetes mellitus with diabetic chronic kidney disease",
        "E11.36": "Type 2 diabetes mellitus with diabetic cataract",
        "E11.40": "Type 2 diabetes mellitus with diabetic neuropathy, unspecified",
        "E11.51": "Type 2 diabetes mellitus with diabetic peripheral angiopathy without gangrene",
        "E66": "Overweight and obesity",
        "E66.01": "Morbid (severe) obesity due to excess calories",
        "E66.09": "Other obesity due to excess calories",
        "E66.9": "Obesity, unspecified",
        "E78": "Disorders of lipoprotein metabolism and other lipidemias",
        "E78.0": "Pure hypercholesterolemia",
        "E78.1": "Pure hyperglyceridemia",
        "E78.2": "Mixed hyperlipidemia",
        "E78.5": "Hyperlipidemia, unspecified",
        "E86": "Volume depletion",
        "E86.0": "Dehydration",
        "E87": "Other disorders of fluid, electrolyte and acid-base balance",
        "E87.6": "Hypokalemia",
        
        # Mental, behavioral and neurodevelopmental disorders (F01-F99)
        "F10": "Alcohol related disorders",
        "F10.10": "Alcohol abuse, uncomplicated",
        "F10.20": "Alcohol dependence, uncomplicated",
        "F17": "Nicotine dependence",
        "F17.200": "Nicotine dependence, unspecified, uncomplicated",
        "F17.210": "Nicotine dependence, cigarettes, uncomplicated",
        "F20": "Schizophrenia",
        "F31": "Bipolar disorder",
        "F32": "Major depressive disorder, single episode",
        "F32.0": "Major depressive disorder, single episode, mild",
        "F32.1": "Major depressive disorder, single episode, moderate",
        "F32.2": "Major depressive disorder, single episode, severe without psychotic features",
        "F32.9": "Major depressive disorder, single episode, unspecified",
        "F33": "Major depressive disorder, recurrent",
        "F33.0": "Major depressive disorder, recurrent, mild",
        "F33.1": "Major depressive disorder, recurrent, moderate",
        "F33.2": "Major depressive disorder, recurrent severe without psychotic features",
        "F33.9": "Major depressive disorder, recurrent, unspecified",
        "F41": "Other anxiety disorders",
        "F41.0": "Panic disorder [episodic paroxysmal anxiety]",
        "F41.1": "Generalized anxiety disorder",
        "F41.9": "Anxiety disorder, unspecified",
        "F43": "Reaction to severe stress, and adjustment disorders",
        "F43.10": "Post-traumatic stress disorder, unspecified",
        "F43.20": "Adjustment disorder, unspecified",
        
        # Diseases of the nervous system (G00-G99)
        "G20": "Parkinson's disease",
        "G30": "Alzheimer's disease",
        "G30.0": "Alzheimer's disease with early onset",
        "G30.1": "Alzheimer's disease with late onset",
        "G30.9": "Alzheimer's disease, unspecified",
        "G35": "Multiple sclerosis",
        "G40": "Epilepsy and recurrent seizures",
        "G40.909": "Epilepsy, unspecified, not intractable, without status epilepticus",
        "G43": "Migraine",
        "G43.909": "Migraine, unspecified, not intractable, without status migrainosus",
        "G47": "Sleep disorders",
        "G47.00": "Insomnia, unspecified",
        "G47.30": "Sleep apnea, unspecified",
        "G89": "Pain, not elsewhere classified",
        "G89.29": "Other chronic pain",
        
        # Diseases of the eye and adnexa (H00-H59)
        "H10": "Conjunctivitis",
        "H10.9": "Unspecified conjunctivitis",
        "H25": "Age-related cataract",
        "H26": "Other cataract",
        "H35": "Other retinal disorders",
        "H40": "Glaucoma",
        "H52": "Disorders of refraction and accommodation",
        "H52.4": "Presbyopia",
        
        # Diseases of the ear and mastoid process (H60-H95)
        "H60": "Otitis externa",
        "H65": "Nonsuppurative otitis media",
        "H66": "Suppurative and unspecified otitis media",
        "H66.90": "Otitis media, unspecified, unspecified ear",
        "H91": "Other and unspecified hearing loss",
        
        # Diseases of the circulatory system (I00-I99)
        "I10": "Essential (primary) hypertension",
        "I11": "Hypertensive heart disease",
        "I11.0": "Hypertensive heart disease with heart failure",
        "I11.9": "Hypertensive heart disease without heart failure",
        "I20": "Angina pectoris",
        "I20.0": "Unstable angina",
        "I20.9": "Angina pectoris, unspecified",
        "I21": "Acute myocardial infarction",
        "I21.9": "Acute myocardial infarction, unspecified",
        "I25": "Chronic ischemic heart disease",
        "I25.10": "Atherosclerotic heart disease of native coronary artery without angina pectoris",
        "I25.2": "Old myocardial infarction",
        "I48": "Atrial fibrillation and flutter",
        "I48.0": "Paroxysmal atrial fibrillation",
        "I48.91": "Unspecified atrial fibrillation",
        "I50": "Heart failure",
        "I50.1": "Left ventricular failure",
        "I50.9": "Heart failure, unspecified",
        "I63": "Cerebral infarction",
        "I63.9": "Cerebral infarction, unspecified",
        "I64": "Stroke, not specified as hemorrhage or infarction",
        "I70": "Atherosclerosis",
        "I73": "Other peripheral vascular diseases",
        "I74": "Arterial embolism and thrombosis",
        
        # Diseases of the respiratory system (J00-J99)
        "J00": "Acute nasopharyngitis [common cold]",
        "J01": "Acute sinusitis",
        "J01.90": "Acute sinusitis, unspecified",
        "J02": "Acute pharyngitis",
        "J02.9": "Acute pharyngitis, unspecified",
        "J03": "Acute tonsillitis",
        "J06": "Acute upper respiratory infections of multiple and unspecified sites",
        "J06.9": "Acute upper respiratory infection, unspecified",
        "J11": "Influenza due to unidentified influenza virus",
        "J11.1": "Influenza due to unidentified influenza virus with other respiratory manifestations",
        "J12": "Viral pneumonia, not elsewhere classified",
        "J13": "Pneumonia due to Streptococcus pneumoniae",
        "J15": "Bacterial pneumonia, not elsewhere classified",
        "J18": "Pneumonia, unspecified organism",
        "J18.9": "Pneumonia, unspecified organism",
        "J20": "Acute bronchitis",
        "J20.9": "Acute bronchitis, unspecified",
        "J30": "Vasomotor and allergic rhinitis",
        "J30.1": "Allergic rhinitis due to pollen",
        "J30.9": "Allergic rhinitis, unspecified",
        "J40": "Bronchitis, not specified as acute or chronic",
        "J42": "Unspecified chronic bronchitis",
        "J44": "Other chronic obstructive pulmonary disease",
        "J44.0": "Chronic obstructive pulmonary disease with acute lower respiratory infection",
        "J44.1": "Chronic obstructive pulmonary disease with (acute) exacerbation",
        "J44.9": "Chronic obstructive pulmonary disease, unspecified",
        "J45": "Asthma",
        "J45.20": "Mild intermittent asthma, uncomplicated",
        "J45.40": "Moderate persistent asthma, uncomplicated",
        "J45.50": "Severe persistent asthma, uncomplicated",
        "J45.901": "Unspecified asthma with (acute) exacerbation",
        "J45.909": "Unspecified asthma, uncomplicated",
        "J98": "Other respiratory disorders",
        
        # Diseases of the digestive system (K00-K95)
        "K21": "Gastro-esophageal reflux disease",
        "K21.0": "Gastro-esophageal reflux disease with esophagitis",
        "K21.9": "Gastro-esophageal reflux disease without esophagitis",
        "K25": "Gastric ulcer",
        "K26": "Duodenal ulcer",
        "K29": "Gastritis and duodenitis",
        "K29.70": "Gastritis, unspecified, without bleeding",
        "K50": "Crohn's disease [regional enteritis]",
        "K51": "Ulcerative colitis",
        "K52": "Other and unspecified gastroenteritis and colitis",
        "K52.9": "Gastroenteritis and colitis of unspecified origin",
        "K58": "Irritable bowel syndrome",
        "K58.0": "Irritable bowel syndrome with diarrhea",
        "K58.9": "Irritable bowel syndrome without diarrhea",
        "K59": "Other functional intestinal disorders",
        "K59.00": "Constipation, unspecified",
        "K70": "Alcoholic liver disease",
        "K74": "Fibrosis and cirrhosis of liver",
        "K80": "Cholelithiasis",
        
        # Diseases of the skin (L00-L99)
        "L20": "Atopic dermatitis",
        "L30": "Other and unspecified dermatitis",
        "L40": "Psoriasis",
        "L50": "Urticaria",
        "L50.9": "Urticaria, unspecified",
        "L60": "Nail disorders",
        "L70": "Acne",
        "L71": "Rosacea",
        "L89": "Pressure ulcer",
        "L97": "Non-pressure chronic ulcer of lower limb",
        
        # Diseases of the musculoskeletal system (M00-M99)
        "M05": "Rheumatoid arthritis with rheumatoid factor",
        "M06": "Other rheumatoid arthritis",
        "M10": "Gout",
        "M10.9": "Gout, unspecified",
        "M15": "Polyosteoarthritis",
        "M16": "Osteoarthritis of hip",
        "M17": "Osteoarthritis of knee",
        "M19": "Other and unspecified osteoarthritis",
        "M19.90": "Unspecified osteoarthritis, unspecified site",
        "M25": "Other joint disorder, not elsewhere classified",
        "M25.50": "Pain in unspecified joint",
        "M47": "Spondylosis",
        "M48": "Other spondylopathies",
        "M51": "Thoracic, thoracolumbar, and lumbosacral intervertebral disc disorders",
        "M54": "Dorsalgia",
        "M54.5": "Low back pain",
        "M54.9": "Dorsalgia, unspecified",
        "M62": "Other disorders of muscle",
        "M79": "Other and unspecified soft tissue disorders",
        "M79.3": "Panniculitis, unspecified",
        "M81": "Osteoporosis without current pathological fracture",
        
        # Diseases of the genitourinary system (N00-N99)
        "N10": "Acute tubulo-interstitial nephritis",
        "N17": "Acute kidney failure",
        "N18": "Chronic kidney disease (CKD)",
        "N18.1": "Chronic kidney disease, stage 1",
        "N18.2": "Chronic kidney disease, stage 2 (mild)",
        "N18.3": "Chronic kidney disease, stage 3 (moderate)",
        "N18.4": "Chronic kidney disease, stage 4 (severe)",
        "N18.5": "Chronic kidney disease, stage 5",
        "N18.6": "End stage renal disease",
        "N18.9": "Chronic kidney disease, unspecified",
        "N20": "Calculus of kidney and ureter",
        "N30": "Cystitis",
        "N30.00": "Acute cystitis without hematuria",
        "N30.90": "Cystitis, unspecified without hematuria",
        "N39": "Other disorders of urinary system",
        "N39.0": "Urinary tract infection, site not specified",
        "N40": "Benign prostatic hyperplasia",
        "N73": "Other female pelvic inflammatory diseases",
        "N76": "Other inflammation of vagina and vulva",
        "N92": "Excessive, frequent and irregular menstruation",
        "N95": "Menopausal and other perimenopausal disorders",
        
        # Pregnancy, childbirth and puerperium (O00-O9A)
        "O00": "Ectopic pregnancy",
        "O10": "Pre-existing hypertension complicating pregnancy, childbirth and the puerperium",
        "O24": "Diabetes mellitus in pregnancy, childbirth, and the puerperium",
        "O80": "Encounter for full-term uncomplicated delivery",
        
        # Symptoms, signs and abnormal findings (R00-R99)
        "R00": "Abnormalities of heart beat",
        "R05": "Cough",
        "R06": "Abnormalities of breathing",
        "R06.02": "Shortness of breath",
        "R07": "Pain in throat and chest",
        "R07.9": "Chest pain, unspecified",
        "R10": "Abdominal and pelvic pain",
        "R10.0": "Acute abdomen",
        "R10.9": "Unspecified abdominal pain",
        "R11": "Nausea and vomiting",
        "R11.0": "Nausea",
        "R11.10": "Vomiting, unspecified",
        "R19": "Other symptoms and signs involving the digestive system and abdomen",
        "R19.7": "Diarrhea, unspecified",
        "R42": "Dizziness and giddiness",
        "R50": "Fever of other and unknown origin",
        "R50.9": "Fever, unspecified",
        "R51": "Headache",
        "R53": "Malaise and fatigue",
        "R53.83": "Other fatigue",
        "R60": "Edema, not elsewhere classified",
        "R63": "Symptoms and signs concerning food and fluid intake",
        "R68": "Other general symptoms and signs",
        "R73": "Elevated blood glucose level",
        "R73.03": "Prediabetes",
        
        # Injury, poisoning (S00-T88)
        "S06": "Intracranial injury",
        "S22": "Fracture of rib(s), sternum and thoracic spine",
        "S42": "Fracture of shoulder and upper arm",
        "S52": "Fracture of forearm",
        "S72": "Fracture of femur",
        "S82": "Fracture of lower leg, including ankle",
        "T14": "Injury of unspecified body region",
        "T78": "Adverse effects, not elsewhere classified",
        "T88": "Other complications of surgical and medical care",
        
        # External causes (V00-Y99)
        "V89": "Motor- or nonmotor-vehicle accident, type of vehicle unspecified",
        "W19": "Unspecified fall",
        
        # Factors influencing health status (Z00-Z99)
        "Z00": "Encounter for general examination without complaint, suspected or reported diagnosis",
        "Z01": "Encounter for other special examination without complaint, suspected or reported diagnosis",
        "Z11": "Encounter for screening for infectious and parasitic diseases",
        "Z12": "Encounter for screening for malignant neoplasms",
        "Z13": "Encounter for screening for other diseases and disorders",
        "Z20": "Contact with and (suspected) exposure to communicable diseases",
        "Z23": "Encounter for immunization",
        "Z71": "Persons encountering health services for other counseling and medical advice",
        "Z79": "Long term (current) drug therapy",
        "Z79.4": "Long term (current) use of insulin",
        "Z79.84": "Long term (current) use of oral hypoglycemic drugs",
        "Z85": "Personal history of malignant neoplasm",
        "Z86": "Personal history of certain other diseases",
        "Z87": "Personal history of other diseases and conditions",
        "Z90": "Acquired absence of organs, not elsewhere classified",
        "Z98": "Other postprocedural states",
    }
    
    # ICD-10 Categories (chapters)
    ICD10_CATEGORIES = [
        "Certain infectious and parasitic diseases (A00-B99)",
        "Neoplasms (C00-D49)",
        "Diseases of the blood and blood-forming organs (D50-D89)",
        "Endocrine, nutritional and metabolic diseases (E00-E89)",
        "Mental, behavioral and neurodevelopmental disorders (F01-F99)",
        "Diseases of the nervous system (G00-G99)",
        "Diseases of the eye and adnexa (H00-H59)",
        "Diseases of the ear and mastoid process (H60-H95)",
        "Diseases of the circulatory system (I00-I99)",
        "Diseases of the respiratory system (J00-J99)",
        "Diseases of the digestive system (K00-K95)",
        "Diseases of the skin and subcutaneous tissue (L00-L99)",
        "Diseases of the musculoskeletal system and connective tissue (M00-M99)",
        "Diseases of the genitourinary system (N00-N99)",
        "Pregnancy, childbirth and the puerperium (O00-O9A)",
        "Certain conditions originating in the perinatal period (P00-P96)",
        "Congenital malformations, deformations and chromosomal abnormalities (Q00-Q99)",
        "Symptoms, signs and abnormal clinical and laboratory findings (R00-R99)",
        "Injury, poisoning and certain other consequences of external causes (S00-T88)",
        "External causes of morbidity (V00-Y99)",
        "Factors influencing health status and contact with health services (Z00-Z99)"
    ]
    
    def __init__(self):
        """Initialize ICD-10 service"""
        logger.info(f"ICD-10 service initialized with {len(self.ICD10_DATABASE)} codes")
    
    def search_codes(
        self,
        query: str,
        max_results: int = 20,
        exact_match: bool = False
    ) -> List[Dict[str, str]]:
        """
        Search ICD-10 codes by code or description.
        
        Args:
            query: Search query (code or description)
            max_results: Maximum number of results to return
            exact_match: If True, only return exact code matches
            
        Returns:
            List of matching ICD-10 codes with descriptions
        """
        query = query.strip().upper()
        results = []
        
        # Exact code match
        if query in self.ICD10_DATABASE:
            if exact_match:
                return [{
                    "code": query,
                    "description": self.ICD10_DATABASE[query]
                }]
            results.append({
                "code": query,
                "description": self.ICD10_DATABASE[query]
            })
        
        # Search in descriptions (case-insensitive)
        query_lower = query.lower()
        for code, description in self.ICD10_DATABASE.items():
            if code in [r["code"] for r in results]:
                continue
            
            # Match description
            if query_lower in description.lower():
                results.append({
                    "code": code,
                    "description": description
                })
            
            # Match partial code
            elif not exact_match and query in code:
                results.append({
                    "code": code,
                    "description": description
                })
            
            if len(results) >= max_results:
                break
        
        return results[:max_results]
    
    def get_code(self, code: str) -> Optional[Dict[str, str]]:
        """
        Get specific ICD-10 code details.
        
        Args:
            code: ICD-10 code
            
        Returns:
            Code details or None if not found
        """
        code = code.strip().upper()
        if code in self.ICD10_DATABASE:
            return {
                "code": code,
                "description": self.ICD10_DATABASE[code],
                "category": self._get_category(code)
            }
        return None
    
    def get_categories(self) -> List[str]:
        """
        Get all ICD-10 categories.
        
        Returns:
            List of category names
        """
        return self.ICD10_CATEGORIES
    
    def _get_category(self, code: str) -> str:
        """
        Determine the category for a given ICD-10 code.
        
        Args:
            code: ICD-10 code
            
        Returns:
            Category name
        """
        if not code:
            return "Unknown"
        
        # Extract the first letter
        first_letter = code[0].upper()
        
        category_map = {
            'A': "Certain infectious and parasitic diseases (A00-B99)",
            'B': "Certain infectious and parasitic diseases (A00-B99)",
            'C': "Neoplasms (C00-D49)",
            'D': "Neoplasms (C00-D49)" if code[1:3] < "50" else "Diseases of the blood (D50-D89)",
            'E': "Endocrine, nutritional and metabolic diseases (E00-E89)",
            'F': "Mental, behavioral and neurodevelopmental disorders (F01-F99)",
            'G': "Diseases of the nervous system (G00-G99)",
            'H': "Diseases of the eye and adnexa (H00-H59)" if int(code[1:3] if len(code) > 2 else 0) < 60 else "Diseases of the ear (H60-H95)",
            'I': "Diseases of the circulatory system (I00-I99)",
            'J': "Diseases of the respiratory system (J00-J99)",
            'K': "Diseases of the digestive system (K00-K95)",
            'L': "Diseases of the skin (L00-L99)",
            'M': "Diseases of the musculoskeletal system (M00-M99)",
            'N': "Diseases of the genitourinary system (N00-N99)",
            'O': "Pregnancy, childbirth and the puerperium (O00-O9A)",
            'P': "Perinatal conditions (P00-P96)",
            'Q': "Congenital malformations (Q00-Q99)",
            'R': "Symptoms, signs and abnormal findings (R00-R99)",
            'S': "Injury and poisoning (S00-T88)",
            'T': "Injury and poisoning (S00-T88)",
            'V': "External causes of morbidity (V00-Y99)",
            'W': "External causes of morbidity (V00-Y99)",
            'X': "External causes of morbidity (V00-Y99)",
            'Y': "External causes of morbidity (V00-Y99)",
            'Z': "Factors influencing health status (Z00-Z99)"
        }
        
        return category_map.get(first_letter, "Unknown")
    
    def suggest_codes(self, symptoms: List[str]) -> List[Dict[str, str]]:
        """
        Suggest ICD-10 codes based on symptoms.
        
        Args:
            symptoms: List of symptom descriptions
            
        Returns:
            List of suggested ICD-10 codes
        """
        suggestions = []
        seen_codes = set()
        
        # Symptom to ICD-10 mapping
        symptom_mappings = {
            "fever": ["R50.9", "J11.1"],
            "cough": ["R05", "J20.9"],
            "shortness of breath": ["R06.02", "J44.9"],
            "chest pain": ["R07.9", "I20.9"],
            "headache": ["R51", "G43.909"],
            "nausea": ["R11.0", "K52.9"],
            "vomiting": ["R11.10", "K52.9"],
            "diarrhea": ["R19.7", "K52.9"],
            "abdominal pain": ["R10.9", "K29.70"],
            "back pain": ["M54.5", "M54.9"],
            "fatigue": ["R53.83"],
            "dizziness": ["R42"],
            "diabetes": ["E11.9", "E10.9"],
            "hypertension": ["I10"],
            "high blood pressure": ["I10"],
            "asthma": ["J45.909"],
            "copd": ["J44.9"],
            "pneumonia": ["J18.9"],
            "depression": ["F32.9", "F33.9"],
            "anxiety": ["F41.9"],
            "arthritis": ["M19.90"],
            "uti": ["N39.0"],
            "kidney": ["N18.9"],
            "heart failure": ["I50.9"],
            "stroke": ["I64"],
            "migraine": ["G43.909"],
        }
        
        for symptom in symptoms:
            symptom_lower = symptom.lower().strip()
            
            # Check for direct mappings
            for keyword, codes in symptom_mappings.items():
                if keyword in symptom_lower:
                    for code in codes:
                        if code not in seen_codes:
                            code_info = self.get_code(code)
                            if code_info:
                                suggestions.append(code_info)
                                seen_codes.add(code)
            
            # Fallback: search in database
            if len(suggestions) < 5:
                search_results = self.search_codes(symptom, max_results=3)
                for result in search_results:
                    if result["code"] not in seen_codes:
                        suggestions.append(result)
                        seen_codes.add(result["code"])
        
        return suggestions[:10]


# Global instance
_icd10_service = None

def get_icd10_service() -> ICD10Service:
    """Get or create ICD-10 service instance"""
    global _icd10_service
    if _icd10_service is None:
        _icd10_service = ICD10Service()
    return _icd10_service
