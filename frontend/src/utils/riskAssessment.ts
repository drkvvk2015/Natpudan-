/**
 * Risk Assessment Utility
 * Calculates patient risk levels based on multiple factors
 */

export interface RiskFactors {
  age: string | number
  travelHistory: any[]
  familyHistory: any[]
  chronicConditions?: string[]
  recentSymptoms?: string[]
}

export interface RiskScore {
  total: number
  level: 'low' | 'medium' | 'high' | 'critical'
  factors: {
    age: number
    travel: number
    family: number
    chronic: number
    symptoms: number
  }
  alerts: string[]
  recommendations: string[]
}

const HIGH_RISK_CONDITIONS = [
  'heart disease',
  'diabetes',
  'cancer',
  'hypertension',
  'kidney disease',
  'liver disease',
  'stroke',
  'copd',
  'asthma',
  'immunocompromised',
  'hiv',
  'tuberculosis',
]

const HIGH_RISK_DESTINATIONS = [
  'wuhan',
  'italy',
  'spain',
  'new york',
  'brazil',
  'india',
  'south africa',
  'uk',
  'france',
]

const CRITICAL_SYMPTOMS = [
  'difficulty breathing',
  'chest pain',
  'confusion',
  'severe headache',
  'high fever',
  'coughing blood',
  'unconscious',
  'seizure',
]

/**
 * Calculate age-based risk
 * High risk: <5 or >65 years
 * Medium risk: 5-18 or 50-65 years
 * Low risk: 18-50 years
 */
function calculateAgeRisk(age: string | number): { score: number; alert?: string } {
  const ageNum = typeof age === 'string' ? parseInt(age) : age
  
  if (isNaN(ageNum)) return { score: 0 }
  
  if (ageNum < 5) {
    return { score: 3, alert: 'Pediatric patient - requires special attention' }
  } else if (ageNum >= 65) {
    return { score: 3, alert: 'Elderly patient - increased vulnerability to complications' }
  } else if (ageNum < 18 || (ageNum >= 50 && ageNum < 65)) {
    return { score: 1 }
  }
  
  return { score: 0 }
}

/**
 * Calculate travel-based risk
 * Considers destination, recency, and duration
 */
function calculateTravelRisk(travelHistory: any[]): { score: number; alerts: string[] } {
  if (!travelHistory || travelHistory.length === 0) {
    return { score: 0, alerts: [] }
  }

  let score = 0
  const alerts: string[] = []
  const now = new Date()

  travelHistory.forEach((travel) => {
    const destination = (travel.destination || '').toLowerCase()
    const returnDate = travel.returnDate ? new Date(travel.returnDate) : null
    
    // Check if high-risk destination
    const isHighRisk = HIGH_RISK_DESTINATIONS.some(dest => destination.includes(dest))
    
    if (isHighRisk) {
      score += 2
      alerts.push(`Recent travel to high-risk area: ${travel.destination}`)
    } else {
      score += 1
    }

    // Check recency (within 14 days)
    if (returnDate) {
      const daysSinceReturn = Math.floor((now.getTime() - returnDate.getTime()) / (1000 * 60 * 60 * 24))
      if (daysSinceReturn <= 14) {
        score += 2
        alerts.push(`Recent return from ${travel.destination} (${daysSinceReturn} days ago) - monitor closely`)
      }
    }

    // Check exposure during travel
    if (travel.exposureToSickIndividuals) {
      score += 3
      alerts.push(`Reported exposure to sick individuals during travel to ${travel.destination}`)
    }

    // Check high-risk activities
    const highRiskActivities = ['hospital visit', 'nursing home visit', 'crowded events']
    if (travel.activities) {
      const hasHighRiskActivity = travel.activities.some((activity: string) =>
        highRiskActivities.some(risk => activity.toLowerCase().includes(risk))
      )
      if (hasHighRiskActivity) {
        score += 1
        alerts.push(`High-risk activities during travel: ${travel.activities.join(', ')}`)
      }
    }
  })

  return { score: Math.min(score, 10), alerts }
}

/**
 * Calculate family history-based risk
 * Considers hereditary conditions and their status
 */
function calculateFamilyHistoryRisk(familyHistory: any[]): { score: number; alerts: string[] } {
  if (!familyHistory || familyHistory.length === 0) {
    return { score: 0, alerts: [] }
  }

  let score = 0
  const alerts: string[] = []

  familyHistory.forEach((family) => {
    const condition = (family.condition || '').toLowerCase()
    
    // Check if high-risk hereditary condition
    const isHighRisk = HIGH_RISK_CONDITIONS.some(risk => condition.includes(risk))
    
    if (isHighRisk) {
      score += 2
      
      // Multiple family members with same condition
      const sameConditionCount = familyHistory.filter(
        f => f.condition.toLowerCase() === condition
      ).length
      
      if (sameConditionCount > 1) {
        score += 1
        alerts.push(`Multiple family members with ${family.condition} - increased genetic risk`)
      } else {
        alerts.push(`Family history of ${family.condition} - monitor for hereditary risk`)
      }
    } else {
      score += 1
    }

    // Check status
    if (family.status === 'deceased' && family.ageAtOnset && family.ageAtOnset < 50) {
      score += 1
      alerts.push(`Family member deceased from ${family.condition} at young age (${family.ageAtOnset}) - increased concern`)
    }
  })

  return { score: Math.min(score, 10), alerts }
}

/**
 * Calculate chronic conditions risk
 */
function calculateChronicConditionsRisk(conditions?: string[]): { score: number; alerts: string[] } {
  if (!conditions || conditions.length === 0) {
    return { score: 0, alerts: [] }
  }

  let score = 0
  const alerts: string[] = []

  conditions.forEach((condition) => {
    const conditionLower = condition.toLowerCase()
    const isHighRisk = HIGH_RISK_CONDITIONS.some(risk => conditionLower.includes(risk))
    
    if (isHighRisk) {
      score += 2
      alerts.push(`Pre-existing condition: ${condition}`)
    } else {
      score += 1
    }
  })

  // Multiple conditions increase risk exponentially
  if (conditions.length >= 3) {
    score += 2
    alerts.push(`Multiple chronic conditions (${conditions.length}) - comprehensive care needed`)
  }

  return { score: Math.min(score, 10), alerts }
}

/**
 * Calculate symptoms-based risk
 */
function calculateSymptomsRisk(symptoms?: string[]): { score: number; alerts: string[] } {
  if (!symptoms || symptoms.length === 0) {
    return { score: 0, alerts: [] }
  }

  let score = 0
  const alerts: string[] = []

  symptoms.forEach((symptom) => {
    const symptomLower = symptom.toLowerCase()
    const isCritical = CRITICAL_SYMPTOMS.some(critical => symptomLower.includes(critical))
    
    if (isCritical) {
      score += 5
      alerts.push(`CRITICAL SYMPTOM: ${symptom} - immediate medical attention required`)
    } else {
      score += 1
    }
  })

  return { score: Math.min(score, 15), alerts }
}

/**
 * Main risk assessment function
 * Returns comprehensive risk score and recommendations
 */
export function assessRisk(factors: RiskFactors): RiskScore {
  const ageRisk = calculateAgeRisk(factors.age)
  const travelRisk = calculateTravelRisk(factors.travelHistory)
  const familyRisk = calculateFamilyHistoryRisk(factors.familyHistory)
  const chronicRisk = calculateChronicConditionsRisk(factors.chronicConditions)
  const symptomsRisk = calculateSymptomsRisk(factors.recentSymptoms)

  const total = 
    ageRisk.score +
    travelRisk.score +
    familyRisk.score +
    chronicRisk.score +
    symptomsRisk.score

  // Compile all alerts
  const alerts: string[] = []
  if (ageRisk.alert) alerts.push(ageRisk.alert)
  alerts.push(...travelRisk.alerts)
  alerts.push(...familyRisk.alerts)
  alerts.push(...chronicRisk.alerts)
  alerts.push(...symptomsRisk.alerts)

  // Determine risk level
  let level: 'low' | 'medium' | 'high' | 'critical' = 'low'
  if (total >= 15 || symptomsRisk.score >= 5) {
    level = 'critical'
  } else if (total >= 10) {
    level = 'high'
  } else if (total >= 5) {
    level = 'medium'
  }

  // Generate recommendations
  const recommendations: string[] = []
  
  if (level === 'critical') {
    recommendations.push('🚨 IMMEDIATE MEDICAL EVALUATION REQUIRED')
    recommendations.push('Consider emergency department referral')
    recommendations.push('Close monitoring of vital signs')
  } else if (level === 'high') {
    recommendations.push('⚠️ Schedule urgent medical consultation')
    recommendations.push('Comprehensive diagnostic testing recommended')
    recommendations.push('Monitor symptoms daily')
  } else if (level === 'medium') {
    recommendations.push('📋 Schedule routine medical check-up')
    recommendations.push('Review family history with physician')
    recommendations.push('Monitor for symptom development')
  } else {
    recommendations.push('✅ Continue routine preventive care')
    recommendations.push('Maintain healthy lifestyle')
    recommendations.push('Annual check-ups as recommended')
  }

  return {
    total,
    level,
    factors: {
      age: ageRisk.score,
      travel: travelRisk.score,
      family: familyRisk.score,
      chronic: chronicRisk.score,
      symptoms: symptomsRisk.score,
    },
    alerts,
    recommendations,
  }
}

/**
 * Get color and icon for risk level
 */
export function getRiskDisplay(level: 'low' | 'medium' | 'high' | 'critical') {
  const displays = {
    low: {
      color: '#4caf50',
      bgColor: '#e8f5e9',
      icon: '✓',
      label: 'Low Risk',
    },
    medium: {
      color: '#ff9800',
      bgColor: '#fff3e0',
      icon: '⚠',
      label: 'Medium Risk',
    },
    high: {
      color: '#f44336',
      bgColor: '#ffebee',
      icon: '⚠',
      label: 'High Risk',
    },
    critical: {
      color: '#d32f2f',
      bgColor: '#ffcdd2',
      icon: '🚨',
      label: 'CRITICAL',
    },
  }
  
  return displays[level]
}
