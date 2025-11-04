// Natpudan AI Clinical Assistant
// Main JavaScript functionality

// Medical knowledge base and data
const medicalKnowledge = {
    symptoms: {
        'fever': ['infection', 'flu', 'pneumonia', 'urinary tract infection', 'sepsis'],
        'headache': ['tension headache', 'migraine', 'cluster headache', 'sinusitis', 'hypertension'],
        'chest pain': ['myocardial infarction', 'angina', 'pneumonia', 'pulmonary embolism', 'costochondritis'],
        'shortness of breath': ['asthma', 'pneumonia', 'heart failure', 'pulmonary embolism', 'anxiety'],
        'abdominal pain': ['appendicitis', 'gallbladder disease', 'peptic ulcer', 'kidney stones', 'gastroenteritis'],
        'nausea': ['gastroenteritis', 'pregnancy', 'medication side effect', 'food poisoning', 'migraine'],
        'fatigue': ['anemia', 'depression', 'thyroid disorder', 'sleep disorder', 'chronic fatigue syndrome'],
        'dizziness': ['vertigo', 'hypotension', 'dehydration', 'inner ear infection', 'medication side effect'],
        'cough': ['upper respiratory infection', 'pneumonia', 'asthma', 'COPD', 'ACE inhibitor side effect'],
        'joint pain': ['arthritis', 'gout', 'fibromyalgia', 'lupus', 'injury']
    },
    
    drugInteractions: {
        'warfarin': {
            'aspirin': { severity: 'high', description: 'Increased bleeding risk' },
            'ibuprofen': { severity: 'high', description: 'Increased bleeding risk' },
            'naproxen': { severity: 'high', description: 'Increased bleeding risk' },
            'acetaminophen': { severity: 'low', description: 'Generally safe combination' }
        },
        'metformin': {
            'insulin': { severity: 'medium', description: 'Monitor blood glucose closely' },
            'contrast dye': { severity: 'high', description: 'Risk of lactic acidosis' }
        },
        'lisinopril': {
            'potassium supplements': { severity: 'medium', description: 'Risk of hyperkalemia' },
            'nsaids': { severity: 'medium', description: 'Reduced antihypertensive effect' }
        },
        'simvastatin': {
            'gemfibrozil': { severity: 'high', description: 'Increased risk of myopathy' },
            'grapefruit': { severity: 'medium', description: 'Increased statin levels' }
        }
    },
    
    medicalInfo: {
        'hypertension': {
            definition: 'High blood pressure, defined as systolic BP ≥140 mmHg or diastolic BP ≥90 mmHg',
            symptoms: 'Often asymptomatic, may include headache, dizziness, vision changes',
            treatment: 'Lifestyle modifications, ACE inhibitors, ARBs, thiazide diuretics, calcium channel blockers',
            monitoring: 'Regular BP checks, kidney function, electrolytes'
        },
        'diabetes': {
            definition: 'Metabolic disorder characterized by elevated blood glucose levels',
            symptoms: 'Polyuria, polydipsia, polyphagia, weight loss, fatigue',
            treatment: 'Lifestyle modifications, metformin, insulin, other antidiabetic medications',
            monitoring: 'HbA1c, blood glucose, kidney function, eye exams'
        },
        'pneumonia': {
            definition: 'Infection of the lung parenchyma causing inflammation',
            symptoms: 'Fever, cough, dyspnea, chest pain, fatigue',
            treatment: 'Antibiotics (empirical or targeted), supportive care',
            monitoring: 'Clinical response, chest X-ray, oxygen saturation'
        },
        'myocardial infarction': {
            definition: 'Death of cardiac muscle due to insufficient blood supply',
            symptoms: 'Chest pain, dyspnea, nausea, diaphoresis, radiation to arm/jaw',
            treatment: 'Urgent reperfusion therapy, antiplatelet agents, beta-blockers, ACE inhibitors',
            monitoring: 'ECG, cardiac enzymes, vital signs, complications'
        }
    }
};

// Patient data storage (in real app, this would be a secure database)
let patientData = JSON.parse(localStorage.getItem('natpudan_patients') || '[]');

// Navigation functionality
function showSection(sectionId) {
    // Hide all sections
    document.querySelectorAll('.section').forEach(section => {
        section.classList.remove('active');
    });
    
    // Remove active class from all nav buttons
    document.querySelectorAll('.nav-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    
    // Show selected section
    document.getElementById(sectionId).classList.add('active');
    
    // Add active class to corresponding nav button
    document.querySelector(`[data-section="${sectionId}"]`).classList.add('active');
}

// Event listeners for navigation
document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.nav-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const section = this.getAttribute('data-section');
            showSection(section);
        });
    });
    
    // Load existing patient notes on startup
    loadPatientNotes();
});

// Symptom Analysis Function
function analyzeSymptoms() {
    const symptoms = document.getElementById('symptoms').value.toLowerCase().trim();
    const age = document.getElementById('age').value;
    const gender = document.getElementById('gender').value;
    
    if (!symptoms) {
        alert('Please enter patient symptoms');
        return;
    }
    
    const resultsDiv = document.getElementById('symptom-results');
    resultsDiv.innerHTML = '<div class="loading">Analyzing symptoms...</div>';
    resultsDiv.classList.add('show');
    
    // Simulate AI processing delay
    setTimeout(() => {
        const analysis = performSymptomAnalysis(symptoms, age, gender);
        displaySymptomResults(analysis);
    }, 1500);
}

function performSymptomAnalysis(symptoms, age, gender) {
    const results = [];
    const symptomWords = symptoms.split(/\s+/);
    
    // Check for matching symptoms in knowledge base
    Object.keys(medicalKnowledge.symptoms).forEach(symptom => {
        if (symptoms.includes(symptom)) {
            const conditions = medicalKnowledge.symptoms[symptom];
            conditions.forEach(condition => {
                const existing = results.find(r => r.condition === condition);
                if (existing) {
                    existing.confidence += 0.2;
                    existing.symptoms.push(symptom);
                } else {
                    results.push({
                        condition: condition,
                        confidence: 0.3,
                        symptoms: [symptom],
                        ageRelevant: isAgeRelevant(condition, age),
                        genderRelevant: isGenderRelevant(condition, gender)
                    });
                }
            });
        }
    });
    
    // Sort by confidence
    results.sort((a, b) => b.confidence - a.confidence);
    
    // Take top 5 results
    return results.slice(0, 5).map(result => ({
        ...result,
        confidence: Math.min(result.confidence * 100, 95) // Cap at 95%
    }));
}

function isAgeRelevant(condition, age) {
    const ageNum = parseInt(age);
    if (isNaN(ageNum)) return true;
    
    // Simple age-based risk factors
    if (ageNum > 65 && ['myocardial infarction', 'hypertension', 'diabetes'].includes(condition)) {
        return true;
    }
    if (ageNum < 18 && ['appendicitis', 'upper respiratory infection'].includes(condition)) {
        return true;
    }
    return false;
}

function isGenderRelevant(condition, gender) {
    // Simple gender-based considerations
    if (gender === 'female' && condition === 'pregnancy') return true;
    if (gender === 'male' && condition === 'myocardial infarction') return true;
    return false;
}

function displaySymptomResults(analysis) {
    const resultsDiv = document.getElementById('symptom-results');
    
    if (analysis.length === 0) {
        resultsDiv.innerHTML = `
            <div class="alert alert-info">
                <h4>No specific matches found</h4>
                <p>Consider conducting a more detailed clinical examination and history taking.</p>
            </div>
        `;
        return;
    }
    
    let html = '<h3>Differential Diagnosis Suggestions</h3>';
    html += '<div class="alert alert-warning"><strong>Note:</strong> This is an AI assistant tool and should not replace clinical judgment or proper medical examination.</div>';
    
    analysis.forEach((result, index) => {
        const confidenceClass = result.confidence > 60 ? 'severity-high' : 
                               result.confidence > 30 ? 'severity-medium' : 'severity-low';
        
        html += `
            <div class="result-item ${confidenceClass}">
                <h4>${index + 1}. ${capitalizeFirst(result.condition)} (${result.confidence.toFixed(1)}% match)</h4>
                <p><strong>Matching symptoms:</strong> ${result.symptoms.join(', ')}</p>
                ${result.ageRelevant ? '<p><strong>Age factor:</strong> Relevant for this age group</p>' : ''}
                ${result.genderRelevant ? '<p><strong>Gender factor:</strong> Relevant consideration</p>' : ''}
                <p><strong>Recommendation:</strong> Consider further diagnostic workup and clinical correlation.</p>
            </div>
        `;
    });
    
    resultsDiv.innerHTML = html;
}

// Drug Interaction Checker
function checkInteractions() {
    const medicationsText = document.getElementById('medications').value.trim();
    
    if (!medicationsText) {
        alert('Please enter medications');
        return;
    }
    
    const medications = medicationsText.toLowerCase().split('\n').map(med => med.trim()).filter(med => med);
    
    if (medications.length < 2) {
        alert('Please enter at least 2 medications to check for interactions');
        return;
    }
    
    const resultsDiv = document.getElementById('interaction-results');
    resultsDiv.innerHTML = '<div class="loading">Checking drug interactions...</div>';
    resultsDiv.classList.add('show');
    
    setTimeout(() => {
        const interactions = findDrugInteractions(medications);
        displayInteractionResults(interactions, medications);
    }, 1000);
}

function findDrugInteractions(medications) {
    const interactions = [];
    
    for (let i = 0; i < medications.length; i++) {
        for (let j = i + 1; j < medications.length; j++) {
            const med1 = medications[i];
            const med2 = medications[j];
            
            // Check both directions
            if (medicalKnowledge.drugInteractions[med1] && medicalKnowledge.drugInteractions[med1][med2]) {
                interactions.push({
                    drug1: med1,
                    drug2: med2,
                    ...medicalKnowledge.drugInteractions[med1][med2]
                });
            } else if (medicalKnowledge.drugInteractions[med2] && medicalKnowledge.drugInteractions[med2][med1]) {
                interactions.push({
                    drug1: med2,
                    drug2: med1,
                    ...medicalKnowledge.drugInteractions[med2][med1]
                });
            }
        }
    }
    
    return interactions;
}

function displayInteractionResults(interactions, medications) {
    const resultsDiv = document.getElementById('interaction-results');
    
    let html = '<h3>Drug Interaction Analysis</h3>';
    html += `<div class="alert alert-info"><strong>Medications analyzed:</strong> ${medications.join(', ')}</div>`;
    
    if (interactions.length === 0) {
        html += `
            <div class="alert alert-success">
                <h4>No Known Interactions Found</h4>
                <p>No significant interactions detected in our database. However, always verify with current drug references and consider patient-specific factors.</p>
            </div>
        `;
    } else {
        interactions.forEach(interaction => {
            const severityClass = `severity-${interaction.severity}`;
            const severityText = interaction.severity.charAt(0).toUpperCase() + interaction.severity.slice(1);
            
            html += `
                <div class="result-item ${severityClass}">
                    <h4>${severityText} Severity Interaction</h4>
                    <p><strong>Drugs:</strong> ${capitalizeFirst(interaction.drug1)} + ${capitalizeFirst(interaction.drug2)}</p>
                    <p><strong>Effect:</strong> ${interaction.description}</p>
                    <p><strong>Recommendation:</strong> ${getInteractionRecommendation(interaction.severity)}</p>
                </div>
            `;
        });
    }
    
    resultsDiv.innerHTML = html;
}

function getInteractionRecommendation(severity) {
    switch (severity) {
        case 'high':
            return 'Avoid this combination if possible. If unavoidable, use with extreme caution and close monitoring.';
        case 'medium':
            return 'Use with caution. Monitor patient closely for adverse effects and consider dose adjustments.';
        case 'low':
            return 'Generally safe combination, but monitor for any unexpected effects.';
        default:
            return 'Consult current drug references for detailed guidance.';
    }
}

// Medical Reference Search
function searchMedicalInfo() {
    const searchTerm = document.getElementById('search-term').value.toLowerCase().trim();
    
    if (!searchTerm) {
        alert('Please enter a search term');
        return;
    }
    
    const resultsDiv = document.getElementById('reference-results');
    resultsDiv.innerHTML = '<div class="loading">Searching medical database...</div>';
    resultsDiv.classList.add('show');
    
    setTimeout(() => {
        const results = searchMedicalDatabase(searchTerm);
        displayMedicalInfo(results, searchTerm);
    }, 800);
}

function searchMedicalDatabase(searchTerm) {
    const results = [];
    
    Object.keys(medicalKnowledge.medicalInfo).forEach(condition => {
        if (condition.includes(searchTerm) || 
            medicalKnowledge.medicalInfo[condition].definition.toLowerCase().includes(searchTerm) ||
            medicalKnowledge.medicalInfo[condition].symptoms.toLowerCase().includes(searchTerm)) {
            results.push({
                condition: condition,
                info: medicalKnowledge.medicalInfo[condition]
            });
        }
    });
    
    return results;
}

function displayMedicalInfo(results, searchTerm) {
    const resultsDiv = document.getElementById('reference-results');
    
    let html = `<h3>Medical Reference Results for "${searchTerm}"</h3>`;
    
    if (results.length === 0) {
        html += `
            <div class="alert alert-info">
                <h4>No results found</h4>
                <p>No matching information found in the database. Consider searching with different terms or consulting comprehensive medical references.</p>
            </div>
        `;
    } else {
        results.forEach(result => {
            html += `
                <div class="result-item">
                    <h4>${capitalizeFirst(result.condition)}</h4>
                    <p><strong>Definition:</strong> ${result.info.definition}</p>
                    <p><strong>Symptoms:</strong> ${result.info.symptoms}</p>
                    <p><strong>Treatment:</strong> ${result.info.treatment}</p>
                    <p><strong>Monitoring:</strong> ${result.info.monitoring}</p>
                </div>
            `;
        });
    }
    
    resultsDiv.innerHTML = html;
}

// Patient Management Functions
function savePatientNote() {
    const patientId = document.getElementById('patient-id').value.trim();
    const patientName = document.getElementById('patient-name').value.trim();
    const notes = document.getElementById('notes').value.trim();
    
    if (!patientId || !patientName || !notes) {
        alert('Please fill in all patient information fields');
        return;
    }
    
    const patient = {
        id: patientId,
        name: patientName,
        notes: notes,
        timestamp: new Date().toISOString()
    };
    
    // Check if patient already exists
    const existingIndex = patientData.findIndex(p => p.id === patientId);
    if (existingIndex >= 0) {
        patientData[existingIndex] = patient;
    } else {
        patientData.push(patient);
    }
    
    // Save to localStorage
    localStorage.setItem('natpudan_patients', JSON.stringify(patientData));
    
    // Clear form
    document.getElementById('patient-id').value = '';
    document.getElementById('patient-name').value = '';
    document.getElementById('notes').value = '';
    
    // Refresh patient list
    loadPatientNotes();
    
    alert('Patient notes saved successfully!');
}

function loadPatientNotes() {
    const patientList = document.getElementById('patient-list');
    
    if (patientData.length === 0) {
        patientList.innerHTML = `
            <div class="alert alert-info">
                <h4>No patient notes found</h4>
                <p>Start by adding a patient note above.</p>
            </div>
        `;
        return;
    }
    
    let html = '<h3>Patient Notes</h3>';
    patientData.forEach(patient => {
        const date = new Date(patient.timestamp).toLocaleDateString();
        html += `
            <div class="patient-item">
                <h4>${patient.name}</h4>
                <div class="patient-id">ID: ${patient.id} | Date: ${date}</div>
                <div class="patient-notes">${patient.notes}</div>
            </div>
        `;
    });
    
    patientList.innerHTML = html;
}

// Utility Functions
function capitalizeFirst(str) {
    return str.charAt(0).toUpperCase() + str.slice(1);
}

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    console.log('Natpudan AI Clinical Assistant initialized');
});