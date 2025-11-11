"""OpenAI integration for AI-powered responses."""

import os
from typing import List, Dict
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
MODEL = os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview")


async def generate_ai_response(
    messages: List[Dict[str, str]],
    system_prompt: str = "You are a helpful medical AI assistant. Provide accurate, professional medical information.",
    max_tokens: int = 2000,
    temperature: float = 0.7,
) -> str:
    """
    Generate AI response using OpenAI API.
    
    Args:
        messages: List of conversation messages with role and content
        system_prompt: System prompt to set AI behavior
        max_tokens: Maximum tokens in response
        temperature: Response randomness (0-2)
        
    Returns:
        AI generated response text
    """
    try:
        # Prepare messages with system prompt
        formatted_messages = [{"role": "system", "content": system_prompt}]
        formatted_messages.extend(messages)
        
        # Call OpenAI API
        response = client.chat.completions.create(
            model=MODEL,
            messages=formatted_messages,
            max_tokens=max_tokens,
            temperature=temperature,
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        print(f"OpenAI API Error: {str(e)}")
        # Fallback response if API fails
        return "I apologize, but I'm having trouble processing your request right now. Please try again later or contact support if the issue persists."


async def generate_discharge_summary(patient_data: Dict[str, str]) -> str:
    """
    Generate comprehensive discharge summary using AI.
    
    Args:
        patient_data: Dictionary containing patient information
        
    Returns:
        AI generated discharge summary
    """
    system_prompt = """You are an expert medical physician assistant specializing in creating comprehensive discharge summaries. 
    Provide detailed, professional medical documentation following standard medical practices. 
    Include appropriate medical terminology, proper formatting, and evidence-based recommendations."""
    
    user_prompt = f"""
Based on the following patient information, generate a comprehensive discharge summary:

PATIENT INFORMATION:
- Name: {patient_data.get('patient_name', 'Not provided')}
- Age: {patient_data.get('patient_age', 'Not provided')}
- Gender: {patient_data.get('patient_gender', 'Not provided')}
- MRN: {patient_data.get('mrn', 'Not provided')}
- Admission Date: {patient_data.get('admission_date', 'Not provided')}
- Discharge Date: {patient_data.get('discharge_date', 'Not provided')}

CLINICAL DETAILS:
- Chief Complaint: {patient_data.get('chief_complaint', 'Not provided')}
- History of Present Illness: {patient_data.get('history_present_illness', 'Not provided')}
- Past Medical History: {patient_data.get('past_medical_history', 'Not provided')}
- Physical Examination: {patient_data.get('physical_examination', 'Not provided')}
- Diagnosis: {patient_data.get('diagnosis', 'Not provided')}
- Hospital Course: {patient_data.get('hospital_course', 'Not provided')}
- Procedures: {patient_data.get('procedures_performed', 'Not provided')}
- Medications During Stay: {patient_data.get('medications', 'Not provided')}

Please generate:
1. HOSPITAL COURSE SUMMARY: Concise narrative of the hospitalization
2. DISCHARGE MEDICATIONS: Complete list with dosages, frequency, and duration
3. FOLLOW-UP INSTRUCTIONS: Specific appointments and monitoring needed
4. DIET: Detailed dietary recommendations and restrictions
5. ACTIVITY: Activity level and restrictions
6. WARNING SIGNS: Red flags requiring immediate medical attention
7. PATIENT EDUCATION: Key points patient should understand

Format professionally as a complete discharge summary.
"""
    
    messages = [{"role": "user", "content": user_prompt}]
    
    return await generate_ai_response(
        messages=messages,
        system_prompt=system_prompt,
        max_tokens=3000,
        temperature=0.5,  # Lower temperature for more consistent medical documentation
    )


async def generate_diagnosis_assistance(symptoms: str, patient_history: str = "") -> str:
    """
    Generate differential diagnosis suggestions.
    
    Args:
        symptoms: Patient symptoms description
        patient_history: Patient medical history
        
    Returns:
        AI generated diagnosis assistance
    """
    system_prompt = """You are an expert diagnostic assistant physician. Provide differential diagnoses based on symptoms and patient history.
    Always include: 1) Most likely diagnoses, 2) Red flags/concerning features, 3) Recommended investigations.
    Emphasize that this is for clinical decision support and not a replacement for clinical judgment."""
    
    user_prompt = f"""
Patient presents with the following:

SYMPTOMS: {symptoms}

PATIENT HISTORY: {patient_history if patient_history else 'Not provided'}

Please provide:
1. Differential Diagnoses (in order of likelihood)
2. Key Clinical Features supporting each diagnosis
3. Red Flags or concerning features
4. Recommended Investigations
5. Initial Management Considerations
"""
    
    messages = [{"role": "user", "content": user_prompt}]
    
    return await generate_ai_response(
        messages=messages,
        system_prompt=system_prompt,
        max_tokens=2000,
        temperature=0.6,
    )
