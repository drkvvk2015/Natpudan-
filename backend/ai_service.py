"""
AI service for medical assistant functionality.
Integrates with OpenAI for intelligent responses.
"""
import os
from typing import List, Dict, Optional
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()


class AIService:
    """Handles AI-powered medical assistance."""
    
    def __init__(self):
        """Initialize the AI service."""
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        
        self.client = OpenAI(api_key=api_key)
        self.model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
    
    def analyze_symptoms(self, symptoms: str, age: Optional[int] = None, 
                        gender: Optional[str] = None, context: Optional[str] = None) -> str:
        """
        Analyze symptoms using AI and provide differential diagnosis suggestions.
        
        Args:
            symptoms: Patient symptoms description
            age: Patient age
            gender: Patient gender
            context: Additional medical knowledge context
            
        Returns:
            AI-generated analysis
        """
        system_prompt = """You are an expert medical AI assistant helping physicians with differential diagnosis.
Provide thoughtful analysis of symptoms and suggest possible conditions to consider.
Always emphasize that this is an AI assistant tool and should not replace proper medical examination.
Format your response in a clear, structured way."""

        user_prompt = f"Patient presents with the following symptoms: {symptoms}"
        
        if age:
            user_prompt += f"\nPatient age: {age}"
        if gender:
            user_prompt += f"\nPatient gender: {gender}"
        if context:
            user_prompt += f"\n\nRelevant medical knowledge:\n{context}"
        
        user_prompt += "\n\nProvide a differential diagnosis analysis with possible conditions to consider."
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"Error calling AI service: {str(e)}")
    
    def check_drug_interactions(self, medications: List[str], context: Optional[str] = None) -> str:
        """
        Check for potential drug interactions using AI.
        
        Args:
            medications: List of medication names
            context: Additional medical knowledge context
            
        Returns:
            AI-generated interaction analysis
        """
        system_prompt = """You are an expert pharmacology AI assistant helping physicians identify drug interactions.
Analyze medication combinations for potential interactions, contraindications, and safety concerns.
Provide clear severity ratings and recommendations."""

        user_prompt = f"Check for interactions between these medications:\n"
        for med in medications:
            user_prompt += f"- {med}\n"
        
        if context:
            user_prompt += f"\n\nRelevant medical knowledge:\n{context}"
        
        user_prompt += "\n\nProvide a detailed interaction analysis including severity and recommendations."
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.5,
                max_tokens=1000
            )
            
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"Error calling AI service: {str(e)}")
    
    def search_medical_information(self, query: str, context: Optional[str] = None) -> str:
        """
        Search for medical information using AI.
        
        Args:
            query: Medical information query
            context: Additional medical knowledge context
            
        Returns:
            AI-generated medical information
        """
        system_prompt = """You are an expert medical reference AI assistant.
Provide accurate, concise medical information about conditions, procedures, and medical terms.
Include definitions, symptoms, treatments, and monitoring recommendations when relevant."""

        user_prompt = f"Provide medical information about: {query}"
        
        if context:
            user_prompt += f"\n\nRelevant medical knowledge:\n{context}"
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.6,
                max_tokens=800
            )
            
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"Error calling AI service: {str(e)}")
    
    def generate_treatment_suggestions(self, condition: str, patient_info: Dict, 
                                      context: Optional[str] = None) -> str:
        """
        Generate treatment suggestions for a condition.
        
        Args:
            condition: Medical condition
            patient_info: Patient information (age, gender, etc.)
            context: Additional medical knowledge context
            
        Returns:
            AI-generated treatment suggestions
        """
        system_prompt = """You are an expert medical treatment AI assistant.
Provide evidence-based treatment suggestions for medical conditions.
Consider patient-specific factors and provide clear recommendations."""

        user_prompt = f"Generate treatment suggestions for: {condition}\n"
        user_prompt += f"Patient information: {patient_info}"
        
        if context:
            user_prompt += f"\n\nRelevant medical knowledge:\n{context}"
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.6,
                max_tokens=800
            )
            
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"Error calling AI service: {str(e)}")
