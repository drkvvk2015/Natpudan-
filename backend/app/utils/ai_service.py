"""OpenAI integration for AI-powered responses with robust error handling."""

import os
import logging
from typing import List, Dict
from openai import OpenAI, APITimeoutError, RateLimitError, APIError
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# Load environment variables from backend/.env file
backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
env_path = os.path.join(backend_dir, '.env')
load_dotenv(env_path)

# Initialize OpenAI client with timeout and error handling
api_key = os.getenv("OPENAI_API_KEY")
client = None

if not api_key or api_key.startswith("sk-your"):
    logger.warning("[WARNING] OpenAI API key not configured properly - AI features will be limited")
else:
    try:
        client = OpenAI(api_key=api_key, timeout=30.0, max_retries=2)
        logger.info("[OK] OpenAI client initialized successfully")
    except Exception as e:
        logger.error(f"[ERROR] Failed to initialize OpenAI client: {e}")

MODEL = os.getenv("OPENAI_MODEL", "gpt-4o")


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
    # Check if client is available
    if not client:
        logger.error("OpenAI client not initialized")
        raise Exception("OpenAI API not configured. Please set OPENAI_API_KEY in backend/.env file. Visit: https://platform.openai.com/api-keys")
    
    try:
        # Prepare messages with system prompt
        formatted_messages = [{"role": "system", "content": system_prompt}]
        formatted_messages.extend(messages)
        
        # Call OpenAI API with timeout and retry
        logger.debug(f"Calling OpenAI {MODEL} with {len(messages)} messages")
        response = client.chat.completions.create(
            model=MODEL,
            messages=formatted_messages,
            max_tokens=max_tokens,
            temperature=temperature,
        )
        
        result = response.choices[0].message.content
        logger.debug(f"OpenAI response received ({len(result)} chars)")
        return result
    
    except APITimeoutError as e:
        logger.error(f"OpenAI API timeout after 30s: {e}")
        raise Exception("OpenAI timeout (30s). Please try with a shorter query or use knowledge base search.")
    
    except RateLimitError as e:
        logger.error(f"OpenAI rate limit exceeded: {e}")
        raise Exception("OpenAI rate limit exceeded. Please wait a few seconds and try again, or use knowledge base.")
    
    except APIError as api_error:
        error_msg = str(api_error)
        logger.error(f"OpenAI API Error: {error_msg}")
        
        # Provide specific, actionable error messages
        if "api_key" in error_msg.lower() or "authentication" in error_msg.lower() or "401" in error_msg:
            raise Exception("OpenAI API key invalid. Please check OPENAI_API_KEY in backend/.env file.")
        elif "quota" in error_msg.lower() or "insufficient_quota" in error_msg.lower():
            raise Exception("OpenAI quota exceeded. Please add credits at https://platform.openai.com/account/billing")
        elif "model" in error_msg.lower():
            raise Exception(f"Model '{MODEL}' not available. Try setting OPENAI_MODEL=gpt-4o-mini in backend/.env")
        else:
            raise Exception(f"OpenAI API error: {error_msg[:150]}. Using knowledge base fallback.")
    
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Unexpected error in AI service: {error_msg}", exc_info=True)
        # Re-raise if already a user-friendly exception
        if "OpenAI" in error_msg or "API" in error_msg or "quota" in error_msg:
            raise
        # Otherwise, create generic error with fallback suggestion
        raise Exception(f"AI service error: {error_msg[:100]}. Please try knowledge base search.")


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
