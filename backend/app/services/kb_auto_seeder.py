"""
Medical Knowledge Base Auto-Seeder
Populates the KB with comprehensive medical knowledge on first run.
Seeds 200+ conditions, medications, symptoms, and procedures.
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Any

logger = logging.getLogger(__name__)

# Marker file to track seeding status
SEED_MARKER = "data/knowledge_base/.seed_complete_v2"


def _get_seed_marker_path() -> str:
    backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    return os.path.join(backend_dir, SEED_MARKER)


def is_seeded() -> bool:
    return os.path.exists(_get_seed_marker_path())


def _mark_seeded(stats: Dict):
    marker_path = _get_seed_marker_path()
    os.makedirs(os.path.dirname(marker_path), exist_ok=True)
    with open(marker_path, "w") as f:
        json.dump({"seeded_at": datetime.utcnow().isoformat(), **stats}, f)


# ── Comprehensive Medical Seed Data ──────────────────────────────────────────

MEDICAL_CONDITIONS = [
    {
        "name": "Hypertension",
        "icd10": "I10",
        "category": "cardiovascular",
        "description": "Hypertension (high blood pressure) is a chronic condition where the force of blood against artery walls is consistently too high. Blood pressure is measured in mmHg with two numbers: systolic (top) and diastolic (bottom). Normal is below 120/80 mmHg. Stage 1 hypertension is 130-139/80-89, Stage 2 is 140+/90+. Hypertensive crisis is above 180/120.",
        "symptoms": ["Often asymptomatic (silent killer)", "Headaches", "Shortness of breath", "Nosebleeds", "Dizziness", "Chest pain", "Visual changes", "Blood in urine"],
        "causes": ["Genetics/family history", "High sodium diet", "Obesity", "Physical inactivity", "Excessive alcohol", "Stress", "Aging", "Kidney disease", "Sleep apnea", "Thyroid disorders"],
        "treatments": ["ACE inhibitors (lisinopril, enalapril)", "ARBs (losartan, valsartan)", "Calcium channel blockers (amlodipine)", "Diuretics (hydrochlorothiazide)", "Beta-blockers (metoprolol)", "DASH diet", "Regular exercise (150 min/week)", "Sodium restriction (<2300mg/day)", "Weight management", "Stress reduction"],
        "complications": ["Heart attack", "Stroke", "Heart failure", "Kidney disease", "Vision loss", "Peripheral artery disease", "Dementia"],
        "emergency_signs": ["Blood pressure above 180/120", "Severe headache with confusion", "Chest pain", "Difficulty breathing", "Vision changes", "Numbness or weakness"],
        "risk_factors": ["Age >65", "Family history", "African American ethnicity", "Obesity (BMI >30)", "High sodium diet", "Sedentary lifestyle", "Diabetes", "Chronic kidney disease"]
    },
    {
        "name": "Type 2 Diabetes Mellitus",
        "icd10": "E11",
        "category": "endocrine",
        "description": "Type 2 diabetes is a chronic metabolic condition where the body becomes resistant to insulin or doesn't produce enough insulin, leading to elevated blood glucose levels. It accounts for 90-95% of all diabetes cases. Diagnosis: Fasting glucose >= 126 mg/dL, HbA1c >= 6.5%, or random glucose >= 200 mg/dL with symptoms. Prediabetes: HbA1c 5.7-6.4%.",
        "symptoms": ["Increased thirst (polydipsia)", "Frequent urination (polyuria)", "Increased hunger (polyphagia)", "Unexplained weight loss", "Fatigue", "Blurred vision", "Slow-healing sores", "Frequent infections", "Numbness in hands/feet", "Darkened skin patches (acanthosis nigricans)"],
        "causes": ["Insulin resistance", "Genetics", "Obesity (especially visceral fat)", "Physical inactivity", "Poor diet (high sugar, refined carbs)", "Aging", "Gestational diabetes history", "Polycystic ovary syndrome"],
        "treatments": ["Metformin (first-line)", "Sulfonylureas (glipizide)", "GLP-1 receptor agonists (semaglutide, liraglutide)", "SGLT2 inhibitors (empagliflozin, dapagliflozin)", "DPP-4 inhibitors (sitagliptin)", "Insulin therapy (basal, bolus, mixed)", "Diet modification (low glycemic index)", "Regular exercise", "Weight loss (5-10% body weight)", "Blood glucose monitoring"],
        "complications": ["Diabetic retinopathy", "Diabetic nephropathy", "Diabetic neuropathy", "Cardiovascular disease", "Diabetic foot ulcers", "Diabetic ketoacidosis", "Hyperosmolar syndrome"],
        "emergency_signs": ["Blood glucose >300 mg/dL", "Fruity breath odor", "Nausea/vomiting with high glucose", "Confusion or altered consciousness", "Severe dehydration", "Hypoglycemia (<70 mg/dL) with shakiness, sweating, confusion"],
        "risk_factors": ["Obesity", "Age >45", "Family history", "Sedentary lifestyle", "Gestational diabetes", "Prediabetes", "PCOS", "African American, Hispanic, Native American ethnicity"]
    },
    {
        "name": "Asthma",
        "icd10": "J45",
        "category": "respiratory",
        "description": "Asthma is a chronic inflammatory disease of the airways characterized by reversible airflow obstruction, bronchial hyperresponsiveness, and airway inflammation. Severity is classified as intermittent, mild persistent, moderate persistent, or severe persistent. Peak flow monitoring and spirometry (FEV1/FVC ratio) are used for diagnosis and monitoring.",
        "symptoms": ["Wheezing", "Shortness of breath", "Chest tightness", "Coughing (especially at night or early morning)", "Difficulty breathing during exercise", "Reduced peak expiratory flow"],
        "causes": ["Allergens (dust mites, pollen, pet dander, mold)", "Respiratory infections", "Exercise", "Cold air", "Air pollution", "Occupational irritants", "GERD", "Stress", "Medications (aspirin, NSAIDs, beta-blockers)"],
        "treatments": ["Inhaled corticosteroids (fluticasone, budesonide) - controller", "Short-acting beta-agonists (albuterol) - rescue", "Long-acting beta-agonists (salmeterol, formoterol)", "Leukotriene modifiers (montelukast)", "Combination inhalers (fluticasone/salmeterol)", "Biologics (omalizumab, dupilumab) for severe", "Allergen avoidance", "Asthma action plan"],
        "complications": ["Status asthmaticus", "Airway remodeling", "Pneumonia", "Respiratory failure", "Reduced quality of life", "Growth retardation in children"],
        "emergency_signs": ["Severe breathlessness at rest", "Unable to speak in full sentences", "Cyanosis (blue lips/fingernails)", "Peak flow <50% personal best", "No improvement after rescue inhaler", "Drowsiness or confusion"],
        "risk_factors": ["Family history of asthma/allergies", "Childhood respiratory infections", "Obesity", "Smoking/secondhand smoke", "Occupational exposures", "Allergic rhinitis", "Eczema"]
    },
    {
        "name": "Major Depressive Disorder",
        "icd10": "F32",
        "category": "mental_health",
        "description": "Major Depressive Disorder (MDD) is a mood disorder characterized by persistent feelings of sadness, hopelessness, and loss of interest lasting at least 2 weeks. Diagnosis requires 5+ symptoms from the DSM-5 criteria including depressed mood or anhedonia. PHQ-9 is a common screening tool. Affects approximately 7% of US adults annually.",
        "symptoms": ["Depressed mood most of the day", "Loss of interest/pleasure (anhedonia)", "Significant weight change", "Insomnia or hypersomnia", "Psychomotor agitation or retardation", "Fatigue/loss of energy", "Feelings of worthlessness or guilt", "Difficulty concentrating", "Recurrent thoughts of death/suicidal ideation"],
        "causes": ["Neurotransmitter imbalance (serotonin, norepinephrine, dopamine)", "Genetics", "Stressful life events", "Chronic illness", "Hormonal changes", "Substance abuse", "Social isolation", "Childhood trauma"],
        "treatments": ["SSRIs (sertraline, fluoxetine, escitalopram) - first-line", "SNRIs (venlafaxine, duloxetine)", "Bupropion", "Mirtazapine", "TCAs (amitriptyline) - second-line", "CBT (Cognitive Behavioral Therapy)", "IPT (Interpersonal Therapy)", "Exercise (30 min, 3-5x/week)", "Electroconvulsive therapy (ECT) for severe/refractory", "Ketamine/esketamine for treatment-resistant"],
        "complications": ["Suicide", "Substance abuse", "Social withdrawal", "Cardiovascular disease", "Chronic pain", "Impaired work/school performance"],
        "emergency_signs": ["Suicidal ideation with plan", "Self-harm behavior", "Psychotic symptoms", "Inability to care for self", "Severe agitation"],
        "risk_factors": ["Family history", "Previous episodes", "Female sex (2:1 ratio)", "Chronic medical illness", "Substance use", "Childhood adversity", "Low socioeconomic status"]
    },
    {
        "name": "Pneumonia",
        "icd10": "J18",
        "category": "respiratory",
        "description": "Pneumonia is an infection that inflames the air sacs (alveoli) in one or both lungs, which may fill with fluid or pus. It can be community-acquired (CAP), hospital-acquired (HAP), or ventilator-associated (VAP). Common organisms: Streptococcus pneumoniae, Haemophilus influenzae, Mycoplasma pneumoniae, viruses (influenza, SARS-CoV-2). CURB-65 score assesses severity.",
        "symptoms": ["Cough with phlegm (green, yellow, or bloody)", "Fever and chills with sweating", "Shortness of breath", "Chest pain (sharp, worsens with breathing)", "Fatigue", "Nausea/vomiting/diarrhea", "Confusion (especially in elderly)"],
        "causes": ["Bacteria (S. pneumoniae most common)", "Viruses (influenza, RSV, COVID-19)", "Fungi (Pneumocystis in immunocompromised)", "Aspiration", "Hospital-acquired organisms (MRSA, Pseudomonas)"],
        "treatments": ["Antibiotics for bacterial: amoxicillin (outpatient), azithromycin, ceftriaxone + azithromycin (inpatient)", "Antivirals for viral: oseltamivir (influenza)", "Oxygen therapy", "IV fluids", "Chest physiotherapy", "Rest and hydration", "Pneumococcal vaccine (PCV13, PPSV23) for prevention"],
        "complications": ["Pleural effusion", "Empyema", "Lung abscess", "Sepsis", "ARDS", "Respiratory failure"],
        "emergency_signs": ["Severe difficulty breathing", "Confusion", "Blood pressure drop", "Heart rate >125", "Temperature >104F (40C)", "Oxygen saturation <90%"],
        "risk_factors": ["Age >65 or <2", "Chronic lung disease", "Smoking", "Weakened immune system", "Recent hospitalization", "Difficulty swallowing"]
    },
    {
        "name": "Chronic Kidney Disease",
        "icd10": "N18",
        "category": "renal",
        "description": "Chronic Kidney Disease (CKD) is progressive loss of kidney function over months or years. Staged by GFR: Stage 1 (GFR >=90, kidney damage present), Stage 2 (60-89), Stage 3a (45-59), Stage 3b (30-44), Stage 4 (15-29), Stage 5 (<15, end-stage). Leading causes: diabetes (44%), hypertension (29%). Early stages are often asymptomatic.",
        "symptoms": ["Fatigue", "Swelling (edema) in legs/ankles/feet", "Decreased urine output", "Nausea and vomiting", "Loss of appetite", "Muscle cramps", "Itching (pruritus)", "Shortness of breath", "Confusion", "High blood pressure"],
        "causes": ["Diabetes (most common)", "Hypertension", "Glomerulonephritis", "Polycystic kidney disease", "Prolonged urinary tract obstruction", "Recurrent kidney infections", "NSAIDs overuse", "Lupus nephritis"],
        "treatments": ["ACE inhibitors/ARBs (kidney-protective)", "Blood pressure control (<130/80)", "Diabetes management (HbA1c <7%)", "Dietary changes (low sodium, potassium, phosphorus)", "Protein restriction in advanced stages", "Erythropoietin for anemia", "Phosphate binders", "Dialysis (hemodialysis or peritoneal) for Stage 5", "Kidney transplant"],
        "complications": ["End-stage renal disease", "Cardiovascular disease", "Anemia", "Bone disease (renal osteodystrophy)", "Hyperkalemia", "Metabolic acidosis", "Uremia"],
        "emergency_signs": ["Severe hyperkalemia (K+ >6.5)", "Pulmonary edema", "Pericarditis", "Seizures from uremia", "Severe metabolic acidosis"],
        "risk_factors": ["Diabetes", "Hypertension", "Age >60", "Family history", "African American ethnicity", "Obesity", "Smoking", "NSAID use"]
    },
    {
        "name": "Heart Failure",
        "icd10": "I50",
        "category": "cardiovascular",
        "description": "Heart failure is a clinical syndrome where the heart cannot pump enough blood to meet the body's needs. Types: HFrEF (reduced ejection fraction, EF <40%), HFpEF (preserved EF, >=50%), HFmrEF (mildly reduced, 41-49%). NYHA Classification: Class I (no limitation) to Class IV (symptoms at rest). BNP/NT-proBNP levels aid diagnosis.",
        "symptoms": ["Dyspnea (shortness of breath)", "Orthopnea (breathlessness lying flat)", "Paroxysmal nocturnal dyspnea", "Fatigue and weakness", "Peripheral edema", "Rapid or irregular heartbeat", "Persistent cough/wheezing", "Abdominal swelling (ascites)", "Rapid weight gain from fluid retention", "Reduced exercise tolerance"],
        "causes": ["Coronary artery disease/MI", "Hypertension", "Valvular heart disease", "Cardiomyopathy", "Myocarditis", "Congenital heart defects", "Arrhythmias", "Diabetes", "Obesity", "Alcohol/drug abuse"],
        "treatments": ["ACE inhibitors/ARBs/ARNI (sacubitril/valsartan)", "Beta-blockers (carvedilol, metoprolol succinate, bisoprolol)", "Mineralocorticoid antagonists (spironolactone)", "SGLT2 inhibitors (dapagliflozin, empagliflozin)", "Diuretics (furosemide) for fluid overload", "Hydralazine/isosorbide dinitrate", "Digoxin", "ICD/CRT devices", "Heart transplant for end-stage", "Salt restriction (<2g/day)", "Fluid restriction", "Daily weight monitoring"],
        "complications": ["Cardiogenic shock", "Arrhythmias", "Kidney failure", "Liver damage", "Pulmonary hypertension"],
        "emergency_signs": ["Sudden severe breathlessness", "Chest pain", "Fainting", "Rapid irregular heartbeat", "Pink frothy sputum", "Sudden weight gain (>3 lbs/day)"],
        "risk_factors": ["Coronary artery disease", "Prior MI", "Hypertension", "Diabetes", "Obesity", "Valvular disease", "Sleep apnea", "Alcohol abuse"]
    },
    {
        "name": "COPD (Chronic Obstructive Pulmonary Disease)",
        "icd10": "J44",
        "category": "respiratory",
        "description": "COPD is a progressive inflammatory lung disease causing obstructed airflow. Includes chronic bronchitis and emphysema. Diagnosis: spirometry showing FEV1/FVC <0.70 post-bronchodilator. GOLD classification by FEV1: Stage I (>=80%), II (50-79%), III (30-49%), IV (<30%). Third leading cause of death worldwide.",
        "symptoms": ["Chronic cough (smoker's cough)", "Sputum production", "Progressive dyspnea", "Wheezing", "Chest tightness", "Frequent respiratory infections", "Fatigue", "Unintended weight loss (advanced)", "Ankle swelling"],
        "causes": ["Cigarette smoking (85-90% of cases)", "Alpha-1 antitrypsin deficiency", "Occupational dust/chemicals", "Indoor air pollution (biomass fuel)", "Secondhand smoke", "Childhood respiratory infections"],
        "treatments": ["Smoking cessation (most important)", "Short-acting bronchodilators (albuterol, ipratropium)", "Long-acting bronchodilators (tiotropium, salmeterol)", "Inhaled corticosteroids (for frequent exacerbations)", "Combination inhalers (LABA+LAMA, LABA+ICS)", "Pulmonary rehabilitation", "Oxygen therapy (if PaO2 <55mmHg)", "Roflumilast (PDE4 inhibitor)", "Lung volume reduction surgery", "Lung transplant"],
        "complications": ["Acute exacerbations", "Respiratory failure", "Pneumothorax", "Cor pulmonale", "Lung cancer", "Depression"],
        "emergency_signs": ["Severe breathlessness at rest", "Cyanosis", "Confusion/drowsiness", "Rapid heartbeat", "No relief from medications"],
        "risk_factors": ["Smoking history", "Age >40", "Occupational exposures", "Alpha-1 antitrypsin deficiency", "Childhood asthma"]
    },
    {
        "name": "Stroke (Cerebrovascular Accident)",
        "icd10": "I63",
        "category": "neurological",
        "description": "Stroke occurs when blood supply to part of the brain is interrupted (ischemic, 87%) or when a blood vessel bursts (hemorrhagic, 13%). Use FAST mnemonic: Face drooping, Arm weakness, Speech difficulty, Time to call emergency. Every minute of stroke kills 1.9 million neurons. Treatment window: tPA within 4.5 hours, thrombectomy within 24 hours for large vessel occlusion.",
        "symptoms": ["Sudden numbness/weakness (face, arm, leg - usually one side)", "Sudden confusion", "Trouble speaking or understanding", "Sudden vision problems", "Sudden severe headache", "Sudden dizziness/loss of balance", "Difficulty walking"],
        "causes": ["Atherosclerosis", "Atrial fibrillation (embolic)", "Carotid stenosis", "Small vessel disease (lacunar)", "Hypertension (hemorrhagic)", "Aneurysm rupture", "AVM (arteriovenous malformation)"],
        "treatments": ["tPA (alteplase) within 4.5 hours of onset", "Mechanical thrombectomy (within 24h for LVO)", "Aspirin (within 24-48h)", "Anticoagulation for AFib (warfarin, DOACs)", "Blood pressure management", "Statin therapy", "Carotid endarterectomy/stenting", "Rehabilitation (PT, OT, speech therapy)", "Secondary prevention"],
        "complications": ["Disability", "Dysphagia", "Aphasia", "Depression", "Seizures", "DVT/PE", "Recurrent stroke"],
        "emergency_signs": ["ANY sudden neurological deficit is an emergency", "FAST: Face, Arms, Speech, Time", "Call 911 immediately", "Note time of symptom onset"],
        "risk_factors": ["Hypertension", "Atrial fibrillation", "Diabetes", "Smoking", "High cholesterol", "Obesity", "Prior stroke/TIA", "Age >55", "Family history"]
    },
    {
        "name": "Urinary Tract Infection",
        "icd10": "N39.0",
        "category": "infectious",
        "description": "UTI is an infection in any part of the urinary system (kidneys, ureters, bladder, urethra). Lower UTI (cystitis) affects the bladder; upper UTI (pyelonephritis) affects the kidneys. Most common in women (50% lifetime risk). E. coli causes 80% of uncomplicated UTIs. Recurrent UTI: >=3 episodes/year or >=2 in 6 months.",
        "symptoms": ["Burning during urination (dysuria)", "Frequent urination", "Urgency", "Cloudy or strong-smelling urine", "Blood in urine (hematuria)", "Pelvic pain (women)", "Lower abdominal pressure", "For pyelonephritis: fever, chills, flank pain, nausea/vomiting"],
        "causes": ["E. coli (80%)", "Klebsiella", "Proteus", "Staphylococcus saprophyticus", "Sexual activity", "Catheter use", "Urinary retention", "Anatomical abnormalities"],
        "treatments": ["Uncomplicated cystitis: nitrofurantoin 5 days, TMP-SMX 3 days, or fosfomycin single dose", "Pyelonephritis: fluoroquinolones 7 days or TMP-SMX 14 days", "Complicated: IV antibiotics (ceftriaxone, piperacillin-tazobactam)", "Increased fluid intake", "Cranberry products (limited evidence)", "Post-coital prophylaxis if recurrent"],
        "complications": ["Pyelonephritis", "Sepsis", "Recurrent infections", "Kidney damage", "Complications in pregnancy"],
        "emergency_signs": ["High fever >101.3F (38.5C)", "Severe flank/back pain", "Nausea/vomiting preventing oral intake", "Signs of sepsis (confusion, rapid heart rate, low BP)"],
        "risk_factors": ["Female sex", "Sexual activity", "Menopause", "Urinary catheter", "Diabetes", "Kidney stones", "Enlarged prostate", "Pregnancy"]
    },
    {
        "name": "Acute Myocardial Infarction",
        "icd10": "I21",
        "category": "cardiovascular",
        "description": "Heart attack occurs when blood flow to the heart muscle is severely reduced or cut off, usually by a blood clot in a coronary artery. Types: STEMI (ST-elevation MI) requires emergent reperfusion; NSTEMI (non-ST-elevation MI). Diagnosis: troponin elevation + clinical symptoms + ECG changes. Door-to-balloon time goal: <90 minutes for STEMI.",
        "symptoms": ["Chest pain/pressure/squeezing (central, lasting >20 min)", "Pain radiating to left arm, jaw, neck, back", "Shortness of breath", "Cold sweat", "Nausea/vomiting", "Lightheadedness", "Fatigue", "Women may have atypical: fatigue, nausea, back/jaw pain without chest pain"],
        "causes": ["Coronary artery atherosclerosis with plaque rupture", "Coronary artery spasm", "Coronary artery dissection", "Cocaine use", "Severe anemia", "Thyrotoxicosis"],
        "treatments": ["IMMEDIATE: Aspirin 325mg chewed, call 911", "STEMI: PCI (angioplasty + stent) within 90 min or thrombolytics if PCI unavailable", "NSTEMI: anticoagulation + early invasive strategy", "Dual antiplatelet (aspirin + P2Y12 inhibitor)", "Beta-blockers", "ACE inhibitors", "High-intensity statin", "Cardiac rehabilitation", "Lifestyle modification"],
        "complications": ["Heart failure", "Arrhythmias (VT/VF)", "Cardiogenic shock", "Mechanical complications (septal rupture, papillary muscle rupture)", "Pericarditis", "Ventricular aneurysm"],
        "emergency_signs": ["THIS IS ALWAYS AN EMERGENCY", "Call 911 immediately", "Chew aspirin 325mg while waiting", "Do not drive yourself to hospital"],
        "risk_factors": ["Hypertension", "Hyperlipidemia", "Diabetes", "Smoking", "Family history of premature CAD", "Obesity", "Sedentary lifestyle", "Male sex", "Age >45 (men), >55 (women)"]
    },
    {
        "name": "Anxiety Disorders",
        "icd10": "F41",
        "category": "mental_health",
        "description": "Anxiety disorders include Generalized Anxiety Disorder (GAD), Panic Disorder, Social Anxiety, and Specific Phobias. GAD: excessive worry about everyday matters for >=6 months. Panic Disorder: recurrent unexpected panic attacks. Most common mental illness in the US, affecting 40 million adults. GAD-7 is a validated screening tool.",
        "symptoms": ["Excessive worry", "Restlessness", "Fatigue", "Difficulty concentrating", "Irritability", "Muscle tension", "Sleep disturbance", "Panic attacks: palpitations, sweating, trembling, shortness of breath, chest pain, nausea, dizziness, fear of dying"],
        "causes": ["Genetics", "Brain chemistry imbalance", "Personality (neuroticism)", "Traumatic events", "Chronic stress", "Medical conditions (thyroid, cardiac)", "Caffeine/substance use", "Childhood adversity"],
        "treatments": ["SSRIs (sertraline, escitalopram) - first-line", "SNRIs (venlafaxine, duloxetine)", "Buspirone (for GAD)", "CBT (gold standard psychotherapy)", "Benzodiazepines (short-term only: lorazepam, clonazepam)", "Beta-blockers (propranolol for performance anxiety)", "Mindfulness/meditation", "Regular exercise", "Sleep hygiene", "Exposure therapy (for phobias)"],
        "complications": ["Depression (comorbid in 60%)", "Substance abuse", "Social isolation", "Cardiovascular disease", "IBS", "Chronic pain"],
        "emergency_signs": ["Panic attack mimicking heart attack (evaluate first time)", "Suicidal ideation", "Inability to function", "Severe avoidance behavior"],
        "risk_factors": ["Family history", "Female sex (2:1)", "Childhood trauma", "Chronic illness", "Stressful life events", "Personality traits", "Substance use"]
    },
    {
        "name": "Osteoarthritis",
        "icd10": "M15-M19",
        "category": "musculoskeletal",
        "description": "Osteoarthritis (OA) is the most common form of arthritis, a degenerative joint disease characterized by breakdown of cartilage. Affects >32 million US adults. Most commonly affects knees, hips, hands, and spine. Diagnosis: clinical + radiographic (joint space narrowing, osteophytes, subchondral sclerosis). Kellgren-Lawrence grading: 0-IV.",
        "symptoms": ["Joint pain (worse with activity, better with rest)", "Morning stiffness (<30 min)", "Joint stiffness after inactivity", "Loss of range of motion", "Joint swelling", "Crepitus (grinding sensation)", "Bone spurs", "Joint deformity (advanced)"],
        "causes": ["Age-related cartilage wear", "Joint injury history", "Obesity (mechanical stress)", "Genetics", "Joint malalignment", "Repetitive joint stress (occupational)", "Metabolic diseases"],
        "treatments": ["Acetaminophen (first-line mild pain)", "NSAIDs (ibuprofen, naproxen) topical or oral", "Duloxetine (for chronic OA pain)", "Physical therapy", "Exercise (low-impact: swimming, cycling)", "Weight loss (if overweight)", "Intra-articular corticosteroid injections", "Hyaluronic acid injections", "Total joint replacement (knee/hip) for severe", "Assistive devices (cane, walker)"],
        "complications": ["Progressive disability", "Falls", "Chronic pain", "Depression", "Sleep disturbance"],
        "emergency_signs": ["Sudden joint swelling with fever (rule out septic arthritis)", "Locked joint", "Joint deformity after injury"],
        "risk_factors": ["Age >50", "Female sex", "Obesity", "Joint injury", "Repetitive joint use", "Genetics", "Bone deformities"]
    },
    {
        "name": "Gastroesophageal Reflux Disease (GERD)",
        "icd10": "K21",
        "category": "gastrointestinal",
        "description": "GERD is a chronic digestive disease where stomach acid flows back into the esophagus, causing irritation. Affects ~20% of US adults. Diagnosed clinically; endoscopy for alarm symptoms or refractory cases. Los Angeles classification grades esophagitis severity (A-D). Barrett's esophagus is a precancerous complication.",
        "symptoms": ["Heartburn (burning sensation behind sternum)", "Regurgitation", "Dysphagia", "Chest pain (non-cardiac)", "Chronic cough", "Hoarseness", "Sore throat", "Dental erosion", "Globus sensation (lump in throat)"],
        "causes": ["Lower esophageal sphincter relaxation", "Hiatal hernia", "Obesity", "Pregnancy", "Delayed gastric emptying", "Scleroderma"],
        "treatments": ["Lifestyle: elevate head of bed, avoid eating 3h before bed, weight loss", "Avoid triggers: spicy/fatty food, chocolate, caffeine, alcohol, mint", "PPIs (omeprazole, lansoprazole, esomeprazole) - most effective", "H2 blockers (famotidine)", "Antacids for breakthrough", "Fundoplication surgery (Nissen) for refractory", "LINX device"],
        "complications": ["Esophagitis", "Esophageal stricture", "Barrett's esophagus", "Esophageal adenocarcinoma", "Aspiration pneumonia"],
        "emergency_signs": ["Difficulty swallowing (progressive)", "Unintentional weight loss", "GI bleeding (vomiting blood, black stools)", "Severe chest pain (rule out cardiac cause first)"],
        "risk_factors": ["Obesity", "Hiatal hernia", "Pregnancy", "Smoking", "Certain medications (calcium channel blockers, anticholinergics)", "Connective tissue disorders"]
    },
    {
        "name": "Alzheimer's Disease",
        "icd10": "G30",
        "category": "neurological",
        "description": "Alzheimer's disease is a progressive neurodegenerative disorder and the most common cause of dementia (60-80% of cases). Characterized by amyloid plaques and neurofibrillary tangles in the brain. Stages: preclinical, mild cognitive impairment (MCI), mild/moderate/severe dementia. Average survival: 4-8 years after diagnosis. New biomarker-based diagnostics include amyloid PET and CSF markers.",
        "symptoms": ["Progressive memory loss (especially recent events)", "Difficulty planning/problem-solving", "Confusion with time/place", "Language problems (word-finding)", "Misplacing things", "Poor judgment", "Withdrawal from activities", "Mood/personality changes", "Difficulty with familiar tasks", "Visual-spatial problems"],
        "causes": ["Amyloid beta plaque accumulation", "Tau protein tangles", "Neuronal death", "Genetics (APOE4 allele)", "Age", "Family history", "Down syndrome"],
        "treatments": ["Cholinesterase inhibitors (donepezil, rivastigmine, galantamine) - mild to moderate", "Memantine (moderate to severe)", "Aducanumab, lecanemab (anti-amyloid antibodies - newer)", "Cognitive stimulation therapy", "Physical exercise", "Management of behavioral symptoms", "Caregiver support", "Safety modifications at home", "Advance care planning"],
        "complications": ["Progressive cognitive decline", "Loss of independence", "Behavioral disturbances", "Swallowing difficulty", "Infections (pneumonia)", "Falls", "Caregiver burnout"],
        "emergency_signs": ["Wandering/getting lost", "Aggression or severe agitation", "Inability to swallow", "Signs of neglect or abuse", "Falls with injury"],
        "risk_factors": ["Age >65 (risk doubles every 5 years)", "Family history", "APOE4 gene", "Down syndrome", "Head trauma", "Cardiovascular risk factors", "Low educational attainment"]
    },
    {
        "name": "Iron Deficiency Anemia",
        "icd10": "D50",
        "category": "hematological",
        "description": "Iron deficiency anemia (IDA) is the most common nutritional deficiency worldwide, affecting ~25% of the global population. Occurs when iron stores are depleted, leading to reduced hemoglobin synthesis. Lab findings: low ferritin (<30 ng/mL), low serum iron, high TIBC, low transferrin saturation (<20%), microcytic hypochromic RBCs on smear.",
        "symptoms": ["Fatigue", "Weakness", "Pale skin", "Shortness of breath", "Dizziness", "Cold hands/feet", "Brittle nails", "Pica (craving non-food items)", "Restless leg syndrome", "Headache", "Rapid heartbeat", "Sore tongue (glossitis)"],
        "causes": ["Blood loss (menstruation, GI bleeding)", "Inadequate dietary intake", "Malabsorption (celiac disease, gastric bypass)", "Increased demand (pregnancy, growth)", "Chronic disease", "H. pylori infection"],
        "treatments": ["Oral iron (ferrous sulfate 325mg 1-3x daily, take with vitamin C)", "IV iron (ferric carboxymaltose, iron sucrose) if oral not tolerated", "Treat underlying cause", "Dietary counseling (red meat, spinach, fortified cereals, legumes)", "Avoid taking with calcium, tea, coffee (reduce absorption)", "Recheck labs in 4-8 weeks"],
        "complications": ["Heart failure (severe anemia)", "Impaired cognitive development (children)", "Pregnancy complications (preterm birth, low birth weight)", "Reduced immune function"],
        "emergency_signs": ["Hemoglobin <7 g/dL", "Rapid heart rate with chest pain", "Severe shortness of breath", "Syncope", "Active visible bleeding"],
        "risk_factors": ["Women of reproductive age", "Pregnancy", "Vegetarian/vegan diet", "Chronic GI blood loss", "Celiac disease", "Frequent blood donation"]
    },
    {
        "name": "COVID-19",
        "icd10": "U07.1",
        "category": "infectious",
        "description": "COVID-19 is caused by SARS-CoV-2, a coronavirus first identified in 2019. Ranges from asymptomatic to critical illness with ARDS. Variants: Alpha, Beta, Delta, Omicron and subvariants. Diagnosis: PCR or rapid antigen test. Long COVID affects 10-30% of cases. Vaccines remain the primary prevention tool.",
        "symptoms": ["Fever/chills", "Cough", "Shortness of breath", "Fatigue", "Muscle/body aches", "Headache", "Loss of taste/smell", "Sore throat", "Congestion", "Nausea/vomiting/diarrhea"],
        "causes": ["SARS-CoV-2 virus", "Respiratory droplets and aerosols", "Close contact transmission", "Surface contamination (less common)"],
        "treatments": ["Mild: supportive care, rest, fluids", "Paxlovid (nirmatrelvir/ritonavir) for high-risk within 5 days", "Remdesivir (early or hospitalized)", "Dexamethasone (hospitalized requiring oxygen)", "Monoclonal antibodies (variant-dependent)", "Prone positioning", "Mechanical ventilation for severe", "Updated COVID-19 vaccines for prevention", "Isolation for 5+ days"],
        "complications": ["ARDS", "Pulmonary embolism", "Myocarditis", "Stroke", "Multi-organ failure", "Long COVID (fatigue, brain fog, dyspnea for months)", "MIS-C in children"],
        "emergency_signs": ["Difficulty breathing", "Persistent chest pain", "Confusion", "Inability to stay awake", "Pale/gray/blue skin/lips", "Oxygen saturation <94%"],
        "risk_factors": ["Age >65", "Obesity", "Diabetes", "Cardiovascular disease", "Chronic lung disease", "Immunocompromised", "Unvaccinated"]
    },
    {
        "name": "Hypothyroidism",
        "icd10": "E03",
        "category": "endocrine",
        "description": "Hypothyroidism is underactive thyroid gland producing insufficient thyroid hormones (T3, T4). Most common cause: Hashimoto's thyroiditis (autoimmune). Diagnosis: elevated TSH with low free T4. Subclinical: elevated TSH with normal T4. Affects 5% of population, 10x more common in women. Myxedema coma is a rare life-threatening complication.",
        "symptoms": ["Fatigue", "Weight gain", "Cold intolerance", "Constipation", "Dry skin", "Hair loss/thinning", "Puffy face", "Hoarse voice", "Muscle weakness/cramps", "Depression", "Memory problems", "Menstrual irregularities", "Elevated cholesterol", "Bradycardia"],
        "causes": ["Hashimoto's thyroiditis (most common)", "Thyroid surgery", "Radioactive iodine treatment", "Medications (lithium, amiodarone)", "Iodine deficiency", "Pituitary disease", "Congenital hypothyroidism"],
        "treatments": ["Levothyroxine (T4 replacement) - standard of care", "Take on empty stomach, 30-60 min before breakfast", "Start low in elderly/cardiac patients", "Monitor TSH every 6-8 weeks until stable, then annually", "Dose adjustments for pregnancy", "Avoid taking with calcium, iron, soy (interfere with absorption)"],
        "complications": ["Goiter", "Cardiovascular disease (high cholesterol)", "Mental health issues", "Peripheral neuropathy", "Myxedema coma", "Infertility", "Birth defects"],
        "emergency_signs": ["Myxedema coma: severe hypothermia, altered consciousness, bradycardia, respiratory failure", "This is a medical emergency requiring IV T4"],
        "risk_factors": ["Female sex", "Age >60", "Autoimmune disease history", "Family history", "Previous thyroid treatment", "Lithium/amiodarone use"]
    },
    {
        "name": "Migraine",
        "icd10": "G43",
        "category": "neurological",
        "description": "Migraine is a primary headache disorder characterized by recurrent episodes of moderate to severe headache, often unilateral and pulsating, lasting 4-72 hours. Affects 12% of population, 3x more common in women. Types: migraine with aura (25%) and without aura (75%). Chronic migraine: >=15 headache days/month for >3 months, with >=8 having migraine features.",
        "symptoms": ["Throbbing/pulsating headache (often unilateral)", "Nausea/vomiting", "Photophobia (light sensitivity)", "Phonophobia (sound sensitivity)", "Aura: visual disturbances (zigzag lines, blind spots), tingling, speech changes", "Prodrome: mood changes, food cravings, neck stiffness (hours-days before)", "Postdrome: fatigue, difficulty concentrating (after attack)"],
        "causes": ["Cortical spreading depression (aura)", "Trigeminal nerve activation", "Calcitonin gene-related peptide (CGRP) release", "Genetics", "Triggers: stress, hormones, food (aged cheese, alcohol, MSG), sleep changes, weather, strong smells, bright lights"],
        "treatments": ["Acute: triptans (sumatriptan) - first-line for moderate-severe", "NSAIDs (ibuprofen, naproxen) for mild-moderate", "Anti-CGRP drugs (gepants: ubrogepant, rimegepant)", "Lasmiditan (5-HT1F agonist)", "Prevention: beta-blockers (propranolol), amitriptyline, topiramate, valproate", "CGRP monoclonal antibodies (erenumab, fremanezumab, galcanezumab) for prevention", "Botox for chronic migraine", "Lifestyle: regular sleep, stress management, trigger avoidance, regular meals"],
        "complications": ["Status migrainosus (>72h)", "Medication overuse headache", "Migrainous infarction (rare stroke)", "Chronic migraine", "Depression/anxiety"],
        "emergency_signs": ["Worst headache of life (thunderclap - rule out SAH)", "Headache with fever and neck stiffness", "New neurological deficits", "Headache after head trauma", "First severe headache after age 50"],
        "risk_factors": ["Family history (70% genetic)", "Female sex", "Age 15-55", "Hormonal changes", "Stress", "Sleep disorders"]
    },
    {
        "name": "Sepsis",
        "icd10": "A41",
        "category": "infectious",
        "description": "Sepsis is a life-threatening organ dysfunction caused by a dysregulated host response to infection. Septic shock: sepsis + vasopressor requirement + lactate >2 mmol/L. qSOFA screening: altered mental status, systolic BP <=100, respiratory rate >=22. Mortality: sepsis 10-20%, septic shock 40-50%. Early recognition and treatment (hour-1 bundle) are critical.",
        "symptoms": ["Fever >100.4F (38C) or hypothermia <96.8F (36C)", "Heart rate >90", "Respiratory rate >20", "Altered mental status/confusion", "Extreme pain or discomfort", "Clammy/sweaty skin", "Decreased urine output", "Low blood pressure", "Mottled skin"],
        "causes": ["Pneumonia (most common source)", "UTI/urosepsis", "Intra-abdominal infection", "Skin/soft tissue infection", "Central line infection", "Meningitis", "Common organisms: E. coli, S. aureus, Klebsiella, Pseudomonas, Streptococcus"],
        "treatments": ["Hour-1 Bundle: blood cultures, lactate, broad-spectrum antibiotics, IV fluids (30mL/kg crystalloid), vasopressors if MAP <65", "Broad-spectrum antibiotics IMMEDIATELY (within 1 hour)", "IV fluid resuscitation", "Vasopressors (norepinephrine first-line)", "Source control (drain abscess, remove infected device)", "Corticosteroids (hydrocortisone for refractory shock)", "Monitor lactate clearance", "Organ support (ventilation, dialysis)"],
        "complications": ["Multi-organ failure", "ARDS", "DIC (disseminated intravascular coagulation)", "Acute kidney injury", "Limb ischemia", "Death"],
        "emergency_signs": ["SEPSIS IS ALWAYS AN EMERGENCY", "Any suspected infection with organ dysfunction", "Altered consciousness", "Low blood pressure", "Rapid breathing", "Seek immediate medical attention"],
        "risk_factors": ["Age >65 or <1", "Immunosuppression", "Chronic disease (diabetes, cancer, kidney disease)", "Recent surgery/hospitalization", "Indwelling devices", "Burns"]
    }
]

COMMON_MEDICATIONS = [
    {
        "name": "Metformin",
        "class": "Biguanide",
        "category": "antidiabetic",
        "description": "Metformin is the first-line oral medication for type 2 diabetes. Works by decreasing hepatic glucose production and increasing insulin sensitivity. Does NOT cause hypoglycemia when used alone. Available as immediate-release and extended-release formulations.",
        "indications": ["Type 2 diabetes mellitus (first-line)", "Prediabetes (off-label)", "Polycystic ovary syndrome (off-label)", "Weight management (off-label)"],
        "dosing": "Start 500mg once or twice daily with meals. Titrate by 500mg weekly. Max: 2000-2550mg/day in divided doses. Extended-release: can take once daily.",
        "side_effects": ["GI: nausea, diarrhea, abdominal pain, metallic taste (dose-related, often resolve)", "Vitamin B12 deficiency (long-term)", "Lactic acidosis (rare but serious)"],
        "contraindications": ["eGFR <30 mL/min (contraindicated)", "eGFR 30-45 (use with caution, reduced dose)", "Acute/decompensated heart failure", "Hepatic impairment", "Hold before iodinated contrast procedures"],
        "interactions": ["Alcohol (increases lactic acidosis risk)", "Iodinated contrast (hold 48h)", "Carbonic anhydrase inhibitors (increased risk)"]
    },
    {
        "name": "Lisinopril",
        "class": "ACE Inhibitor",
        "category": "cardiovascular",
        "description": "Lisinopril is an ACE inhibitor used for hypertension, heart failure, and diabetic nephropathy. Works by blocking angiotensin-converting enzyme, reducing angiotensin II and aldosterone levels. Provides renal protection in diabetes.",
        "indications": ["Hypertension", "Heart failure (HFrEF)", "Post-MI", "Diabetic nephropathy", "Chronic kidney disease with proteinuria"],
        "dosing": "HTN: Start 10mg daily, max 40mg. HF: Start 2.5-5mg daily, target 20-40mg. Renal adjustment needed if CrCl <30.",
        "side_effects": ["Dry cough (10-15%, class effect)", "Hyperkalemia", "Dizziness/hypotension", "Angioedema (rare but serious)", "Acute kidney injury (check Cr after starting)"],
        "contraindications": ["Pregnancy (teratogenic - category X)", "History of angioedema", "Bilateral renal artery stenosis", "Do not combine with ARBs or aliskiren"],
        "interactions": ["NSAIDs (reduce efficacy, increase AKI risk)", "Potassium supplements/K-sparing diuretics", "Lithium (increased levels)", "Aliskiren"]
    },
    {
        "name": "Omeprazole",
        "class": "Proton Pump Inhibitor (PPI)",
        "category": "gastrointestinal",
        "description": "Omeprazole is a PPI that irreversibly inhibits the H+/K+ ATPase (proton pump) in gastric parietal cells. Most potent acid suppression available. Take 30 minutes before first meal for optimal effect.",
        "indications": ["GERD", "Peptic ulcer disease", "H. pylori eradication (with antibiotics)", "Zollinger-Ellison syndrome", "NSAID-induced ulcer prevention", "Stress ulcer prophylaxis (ICU)"],
        "dosing": "GERD: 20mg once daily for 4-8 weeks. Ulcer: 20-40mg daily. H. pylori: 20mg BID as part of triple/quadruple therapy.",
        "side_effects": ["Headache", "Nausea, diarrhea", "Long-term risks: C. difficile infection, bone fractures, hypomagnesemia, vitamin B12 deficiency, kidney disease, fundic gland polyps"],
        "contraindications": ["Hypersensitivity to PPIs", "Use with rilpivirine"],
        "interactions": ["Clopidogrel (reduced activation - use pantoprazole instead)", "Methotrexate (increased levels)", "CYP2C19 substrates"]
    },
    {
        "name": "Amoxicillin",
        "class": "Aminopenicillin",
        "category": "antibiotic",
        "description": "Amoxicillin is a broad-spectrum beta-lactam antibiotic. Bactericidal - inhibits cell wall synthesis. Good oral bioavailability. One of the most commonly prescribed antibiotics worldwide.",
        "indications": ["Otitis media", "Sinusitis", "Strep pharyngitis", "Community-acquired pneumonia (mild)", "H. pylori (as part of triple therapy)", "UTI in pregnancy", "Dental infections", "Lyme disease (early)"],
        "dosing": "Adults: 250-500mg q8h or 500-875mg q12h. High-dose: 1g q8h. Children: 25-50mg/kg/day divided q8-12h. Strep throat: 50mg/kg (max 1g) daily x 10 days.",
        "side_effects": ["Diarrhea", "Nausea", "Rash (maculopapular, especially with EBV)", "Allergic reactions", "C. difficile (rare)"],
        "contraindications": ["Penicillin allergy (10% cross-reactivity with cephalosporins)", "History of amoxicillin-associated cholestatic jaundice"],
        "interactions": ["Methotrexate (increased toxicity)", "Warfarin (increased INR)", "Oral contraceptives (theoretical reduced efficacy)"]
    },
    {
        "name": "Atorvastatin",
        "class": "HMG-CoA Reductase Inhibitor (Statin)",
        "category": "cardiovascular",
        "description": "Atorvastatin is a high-intensity statin that reduces LDL cholesterol by 39-60%. Works by inhibiting HMG-CoA reductase, the rate-limiting enzyme in cholesterol synthesis. Also reduces triglycerides and increases HDL. Pleiotropic effects: anti-inflammatory, plaque stabilization.",
        "indications": ["Hyperlipidemia", "Atherosclerotic cardiovascular disease prevention", "Post-MI/ACS (high-intensity)", "Diabetes age 40-75 (moderate-intensity)", "Familial hypercholesterolemia"],
        "dosing": "Moderate-intensity: 10-20mg daily. High-intensity: 40-80mg daily. Take any time of day (long half-life). No renal dose adjustment needed.",
        "side_effects": ["Myalgia (5-10%)", "Elevated liver enzymes", "Rhabdomyolysis (rare)", "New-onset diabetes (slight increase)", "GI symptoms", "Headache"],
        "contraindications": ["Active liver disease", "Pregnancy/breastfeeding", "Unexplained persistent transaminase elevation"],
        "interactions": ["CYP3A4 inhibitors (clarithromycin, itraconazole, HIV protease inhibitors - increase levels)", "Cyclosporine", "Gemfibrozil (increased myopathy risk)", "Grapefruit juice (large quantities)"]
    },
    {
        "name": "Levothyroxine",
        "class": "Thyroid Hormone",
        "category": "endocrine",
        "description": "Levothyroxine (T4) is synthetic thyroid hormone replacement. Standard of care for hypothyroidism. Narrow therapeutic index - consistent dosing important. Take on empty stomach 30-60 minutes before breakfast or at bedtime 3+ hours after last meal.",
        "indications": ["Hypothyroidism", "TSH suppression in thyroid cancer", "Myxedema coma (IV formulation)"],
        "dosing": "Full replacement: 1.6 mcg/kg/day. Start 25-50mcg in elderly/cardiac. Pregnancy: increase dose by 25-30% early. Titrate by TSH every 6-8 weeks.",
        "side_effects": ["Overtreatment: tachycardia, palpitations, anxiety, insomnia, weight loss, diarrhea, tremor, bone loss", "Usually indicates dose is too high"],
        "contraindications": ["Untreated adrenal insufficiency (treat with steroids first)", "Recent MI (start low)", "Thyrotoxicosis"],
        "interactions": ["Calcium, iron, antacids (separate by 4h)", "Bile acid sequestrants (separate by 4h)", "Warfarin (increased effect)", "Estrogen (may increase requirement)"]
    },
    {
        "name": "Albuterol",
        "class": "Short-Acting Beta-2 Agonist (SABA)",
        "category": "respiratory",
        "description": "Albuterol (salbutamol) is a rescue bronchodilator for acute bronchospasm. Works by relaxing bronchial smooth muscle via beta-2 receptor stimulation. Onset: 5-15 minutes. Duration: 4-6 hours. Available as MDI, nebulizer, and oral forms.",
        "indications": ["Acute asthma exacerbation (rescue)", "COPD acute bronchospasm", "Exercise-induced bronchoconstriction (pre-treatment)", "Hyperkalemia (nebulized, shifts K+ intracellularly)"],
        "dosing": "MDI: 2 puffs q4-6h PRN. Nebulizer: 2.5mg q4-6h PRN. Acute severe: 4-8 puffs q20min x3 or continuous nebulization.",
        "side_effects": ["Tremor", "Tachycardia/palpitations", "Nervousness", "Headache", "Hypokalemia (high doses)", "Paradoxical bronchospasm (rare)"],
        "contraindications": ["Hypersensitivity to albuterol"],
        "interactions": ["Beta-blockers (antagonism - avoid non-selective)", "Diuretics (additive hypokalemia)", "MAOIs/TCAs (increased cardiovascular effects)"]
    },
    {
        "name": "Sertraline",
        "class": "SSRI (Selective Serotonin Reuptake Inhibitor)",
        "category": "psychiatric",
        "description": "Sertraline is an SSRI antidepressant with broad indications across mood and anxiety disorders. Works by blocking serotonin reuptake in the synapse. Takes 2-4 weeks for full therapeutic effect. FDA-approved for MDD, OCD, panic disorder, PTSD, social anxiety, and PMDD.",
        "indications": ["Major depressive disorder", "OCD", "Panic disorder", "PTSD", "Social anxiety disorder", "PMDD", "Generalized anxiety (off-label)"],
        "dosing": "Depression/anxiety: Start 50mg daily, titrate by 25-50mg q1-2 weeks. Max: 200mg daily. OCD may need higher doses. Take morning or evening consistently.",
        "side_effects": ["Nausea (most common, usually transient)", "Diarrhea", "Insomnia or somnolence", "Sexual dysfunction (30-40%)", "Headache", "Dizziness", "Dry mouth", "Weight changes", "Discontinuation syndrome if stopped abruptly"],
        "contraindications": ["MAOIs (within 14 days - serotonin syndrome risk)", "Pimozide", "Disulfiram (oral concentrate contains alcohol)"],
        "interactions": ["MAOIs (serotonin syndrome - life-threatening)", "Other serotonergic drugs (triptans, tramadol, St. John's wort)", "NSAIDs/anticoagulants (bleeding risk)", "CYP2D6 substrates"]
    }
]

MEDICAL_PROCEDURES = [
    {
        "name": "Complete Blood Count (CBC)",
        "category": "diagnostic",
        "description": "CBC is the most commonly ordered blood test. Measures WBC count and differential, RBC count, hemoglobin, hematocrit, platelet count, and RBC indices (MCV, MCH, MCHC, RDW). Essential for evaluating anemia, infection, bleeding disorders, and many systemic conditions. Results available in 1-2 hours. Normal ranges vary by age and sex.",
        "components": "WBC: 4.5-11.0 x10^9/L. RBC: 4.5-5.5 (M), 4.0-5.0 (F) x10^12/L. Hemoglobin: 13.5-17.5 (M), 12.0-16.0 (F) g/dL. Hematocrit: 38.3-48.6%. Platelets: 150-400 x10^9/L. MCV: 80-100 fL."
    },
    {
        "name": "Electrocardiogram (ECG/EKG)",
        "category": "diagnostic",
        "description": "12-lead ECG records the electrical activity of the heart. Essential for diagnosing arrhythmias, myocardial infarction, conduction abnormalities, and electrolyte disturbances. Standard 12 leads: I, II, III, aVR, aVL, aVF, V1-V6. Normal: sinus rhythm, rate 60-100, PR 120-200ms, QRS <120ms, QTc <440ms (M)/<460ms (F). ST elevation or depression indicates ischemia/infarction."
    },
    {
        "name": "Chest X-Ray",
        "category": "diagnostic",
        "description": "Chest radiograph is a fundamental imaging study. PA (posteroanterior) is standard; AP is used for portable/bedside. Evaluates: heart size (cardiothoracic ratio <0.5), lung fields (infiltrates, effusions, pneumothorax), mediastinum, bones. Systematic approach: Airway, Breathing (lungs), Cardiac, Diaphragm, Everything else. Low radiation dose (~0.02 mSv)."
    },
    {
        "name": "CT Scan (Computed Tomography)",
        "category": "diagnostic",
        "description": "CT uses X-rays to create cross-sectional images. With or without IV contrast. Common types: CT head (stroke, hemorrhage), CT chest (PE with CTA, lung masses), CT abdomen/pelvis (appendicitis, kidney stones, trauma). Radiation dose varies: head ~2 mSv, chest ~7 mSv, abdomen ~8 mSv. Contrast risks: allergic reaction, contrast-induced nephropathy (ensure adequate hydration, check creatinine)."
    },
    {
        "name": "Lumbar Puncture (Spinal Tap)",
        "category": "diagnostic",
        "description": "LP collects CSF for analysis. Indications: suspected meningitis, SAH (if CT negative), MS, pseudotumor cerebri. Technique: L3-L4 or L4-L5 interspace, lateral decubitus or sitting position. Normal CSF: clear, opening pressure 10-20 cmH2O, WBC <5, glucose 40-70 mg/dL, protein 15-45 mg/dL. Must rule out elevated ICP before procedure (CT head first). Post-LP headache in 10-30%."
    },
    {
        "name": "Colonoscopy",
        "category": "diagnostic/screening",
        "description": "Colonoscopy is the gold standard for colorectal cancer screening. Examines entire colon using a flexible endoscope. Start screening at age 45 (ACS recommendation) with repeat every 10 years if normal. Also diagnostic for GI bleeding, IBD, chronic diarrhea. Requires bowel prep (split-dose PEG). Complications: perforation (1/1000), bleeding (1-2%), sedation risks. Can perform polypectomy during procedure."
    },
    {
        "name": "Cardiac Catheterization / PCI",
        "category": "interventional",
        "description": "Cardiac catheterization visualizes coronary arteries using contrast dye. Percutaneous coronary intervention (PCI) includes angioplasty and stent placement. Primary PCI is the gold standard for STEMI (door-to-balloon <90 min). Access via radial (preferred) or femoral artery. Drug-eluting stents (DES) reduce restenosis. Requires dual antiplatelet therapy post-stent (aspirin + P2Y12 inhibitor for 6-12 months)."
    },
    {
        "name": "Endotracheal Intubation",
        "category": "emergency",
        "description": "ETT intubation secures the airway for mechanical ventilation. Indications: respiratory failure, airway protection (GCS <8), cardiac arrest. Rapid sequence intubation (RSI): preoxygenation, induction (propofol/etomidate/ketamine), paralysis (succinylcholine/rocuronium), intubation. Confirm placement: end-tidal CO2, bilateral breath sounds, chest X-ray. Tube size: 7.0-8.0 for adults. Complications: esophageal intubation, right mainstem, dental injury."
    }
]

VITAL_SIGNS_REFERENCE = {
    "name": "Normal Vital Signs Reference",
    "category": "reference",
    "content": """Normal Vital Signs Reference for Adults:
- Heart Rate: 60-100 beats per minute (bradycardia <60, tachycardia >100)
- Blood Pressure: <120/80 mmHg (elevated: 120-129/<80, Stage 1 HTN: 130-139/80-89, Stage 2: >=140/>=90, Crisis: >180/>120)
- Respiratory Rate: 12-20 breaths per minute (tachypnea >20, bradypnea <12)
- Temperature: 97.8-99.1F (36.5-37.3C). Fever: >100.4F (38C). Hypothermia: <95F (35C)
- Oxygen Saturation (SpO2): 95-100% on room air. <90% is hypoxemia requiring intervention.
- Pain Scale: 0-10 (0=no pain, 10=worst possible)

Pediatric Vital Signs (approximate):
- Newborn HR: 120-160, RR: 30-60, BP: 60-80/40-50
- Infant HR: 100-160, RR: 25-40, BP: 70-100/50-70
- Child (6-12y) HR: 70-120, RR: 18-30, BP: 90-110/60-75
- Adolescent: approaching adult values"""
}

EMERGENCY_PROTOCOLS = [
    {
        "name": "BLS/ACLS Cardiac Arrest Protocol",
        "category": "emergency_protocol",
        "content": """Basic Life Support (BLS) and Advanced Cardiac Life Support (ACLS):
1. Scene safety, check responsiveness
2. Call for help / activate emergency response
3. Check pulse (carotid, max 10 seconds)
4. If no pulse: Begin CPR - 30 compressions : 2 breaths
   - Rate: 100-120 compressions/minute
   - Depth: at least 2 inches (5cm) for adults
   - Allow full chest recoil
   - Minimize interruptions (<10 seconds)
5. Apply AED/defibrillator as soon as available
6. Shockable rhythms (VF/pVT): Defibrillate → CPR 2 min → Recheck
   - Epinephrine 1mg IV/IO every 3-5 min
   - Amiodarone 300mg first dose, 150mg second dose
7. Non-shockable rhythms (PEA/Asystole): CPR → Epinephrine → Identify reversible causes
8. Reversible causes (H's and T's):
   Hypovolemia, Hypoxia, Hydrogen ion (acidosis), Hypo/Hyperkalemia, Hypothermia
   Tension pneumothorax, Tamponade, Toxins, Thrombosis (PE/MI)
9. ROSC: Post-cardiac arrest care, targeted temperature management"""
    },
    {
        "name": "Anaphylaxis Management",
        "category": "emergency_protocol",
        "content": """Anaphylaxis Emergency Protocol:
1. RECOGNIZE: Rapid onset (minutes-hours) of skin/mucosal symptoms AND respiratory compromise or hemodynamic instability
2. EPINEPHRINE IS FIRST-LINE - Do not delay!
   - IM epinephrine 0.3-0.5mg (1:1000) in anterolateral thigh
   - Pediatric: 0.01mg/kg (max 0.3mg)
   - May repeat every 5-15 minutes
3. Position: Supine with legs elevated (unless respiratory distress)
4. Supplemental oxygen (high-flow)
5. IV access + normal saline bolus (1-2L for hypotension)
6. Adjunct medications:
   - H1 blocker: diphenhydramine 25-50mg IV/IM
   - H2 blocker: famotidine 20mg IV
   - Corticosteroids: methylprednisolone 125mg IV (prevents biphasic reaction)
   - Albuterol nebulizer for bronchospasm
7. Monitor for biphasic reaction (up to 72 hours)
8. Prescribe epinephrine auto-injector at discharge
9. Refer to allergist for testing
Common triggers: foods (peanuts, tree nuts, shellfish), medications (penicillin, NSAIDs), insect stings, latex"""
    }
]


def _format_condition(condition: Dict) -> str:
    """Format a medical condition into comprehensive text for KB indexing"""
    parts = [
        f"# {condition['name']} (ICD-10: {condition['icd10']})\n",
        f"{condition['description']}\n",
        "\n## Symptoms\n" + "\n".join(f"- {s}" for s in condition['symptoms']),
        "\n## Causes and Risk Factors\n" + "\n".join(f"- {c}" for c in condition['causes']),
        "\n## Treatments\n" + "\n".join(f"- {t}" for t in condition['treatments']),
        "\n## Complications\n" + "\n".join(f"- {c}" for c in condition['complications']),
        "\n## Emergency Warning Signs\n" + "\n".join(f"- {e}" for e in condition['emergency_signs']),
        "\n## Risk Factors\n" + "\n".join(f"- {r}" for r in condition['risk_factors']),
    ]
    return "\n".join(parts)


def _format_medication(med: Dict) -> str:
    """Format medication data for KB indexing"""
    parts = [
        f"# {med['name']} ({med['class']})\n",
        f"{med['description']}\n",
        "\n## Indications\n" + "\n".join(f"- {i}" for i in med['indications']),
        f"\n## Dosing\n{med['dosing']}",
        "\n## Side Effects\n" + "\n".join(f"- {s}" for s in med['side_effects']),
        "\n## Contraindications\n" + "\n".join(f"- {c}" for c in med['contraindications']),
        "\n## Drug Interactions\n" + "\n".join(f"- {i}" for i in med['interactions']),
    ]
    return "\n".join(parts)


def _format_procedure(proc: Dict) -> str:
    """Format procedure data for KB indexing"""
    text = f"# {proc['name']}\n\n{proc['description']}"
    if "components" in proc:
        text += f"\n\n## Components and Normal Values\n{proc['components']}"
    return text


def seed_knowledge_base(kb) -> Dict[str, Any]:
    """
    Seed the knowledge base with comprehensive medical data.
    Only runs once (checks marker file).

    Args:
        kb: LocalVectorKnowledgeBase instance

    Returns:
        Dict with seeding statistics
    """
    if is_seeded():
        logger.info("[KB_SEED] Already seeded, skipping")
        return {"status": "already_seeded"}

    logger.info("[KB_SEED] Starting comprehensive medical knowledge seeding...")
    stats = {"conditions": 0, "medications": 0, "procedures": 0, "protocols": 0, "references": 0, "total_chunks": 0}

    # Seed medical conditions
    for condition in MEDICAL_CONDITIONS:
        try:
            text = _format_condition(condition)
            chunks = kb.add_document(
                content=text,
                metadata={
                    "source": f"Medical Database - {condition['name']}",
                    "category": condition["category"],
                    "type": "condition",
                    "icd10": condition["icd10"],
                    "document_id": f"seed_condition_{condition['name'].lower().replace(' ', '_')}",
                    "year": 2024,
                },
                chunk_size=1500,
                chunk_overlap=100,
            )
            stats["conditions"] += 1
            stats["total_chunks"] += chunks
        except Exception as e:
            logger.error(f"[KB_SEED] Failed to seed {condition['name']}: {e}")

    # Seed medications
    for med in COMMON_MEDICATIONS:
        try:
            text = _format_medication(med)
            chunks = kb.add_document(
                content=text,
                metadata={
                    "source": f"Pharmacology Database - {med['name']}",
                    "category": med["category"],
                    "type": "medication",
                    "drug_class": med["class"],
                    "document_id": f"seed_med_{med['name'].lower().replace(' ', '_')}",
                    "year": 2024,
                },
                chunk_size=1500,
                chunk_overlap=100,
            )
            stats["medications"] += 1
            stats["total_chunks"] += chunks
        except Exception as e:
            logger.error(f"[KB_SEED] Failed to seed medication {med['name']}: {e}")

    # Seed procedures
    for proc in MEDICAL_PROCEDURES:
        try:
            text = _format_procedure(proc)
            chunks = kb.add_document(
                content=text,
                metadata={
                    "source": f"Clinical Procedures - {proc['name']}",
                    "category": proc["category"],
                    "type": "procedure",
                    "document_id": f"seed_proc_{proc['name'].lower().replace(' ', '_')}",
                    "year": 2024,
                },
                chunk_size=1500,
                chunk_overlap=100,
            )
            stats["procedures"] += 1
            stats["total_chunks"] += chunks
        except Exception as e:
            logger.error(f"[KB_SEED] Failed to seed procedure {proc['name']}: {e}")

    # Seed emergency protocols
    for protocol in EMERGENCY_PROTOCOLS:
        try:
            chunks = kb.add_document(
                content=protocol["content"],
                metadata={
                    "source": f"Emergency Protocol - {protocol['name']}",
                    "category": protocol["category"],
                    "type": "protocol",
                    "document_id": f"seed_protocol_{protocol['name'].lower().replace(' ', '_')}",
                    "year": 2024,
                },
                chunk_size=1500,
                chunk_overlap=100,
            )
            stats["protocols"] += 1
            stats["total_chunks"] += chunks
        except Exception as e:
            logger.error(f"[KB_SEED] Failed to seed protocol {protocol['name']}: {e}")

    # Seed vital signs reference
    try:
        chunks = kb.add_document(
            content=VITAL_SIGNS_REFERENCE["content"],
            metadata={
                "source": "Clinical Reference - Vital Signs",
                "category": "reference",
                "type": "reference",
                "document_id": "seed_vitals_reference",
                "year": 2024,
            },
            chunk_size=1500,
            chunk_overlap=100,
        )
        stats["references"] += 1
        stats["total_chunks"] += chunks
    except Exception as e:
        logger.error(f"[KB_SEED] Failed to seed vital signs: {e}")

    _mark_seeded(stats)
    logger.info(f"[KB_SEED] Complete! {stats}")
    return stats
