"""
Voice Transcriber Service

Transcribes audio files to text using OpenAI Whisper API.
Includes medical entity extraction from transcriptions.
"""

import logging
import os
from typing import Dict, Optional, List
from pathlib import Path
import json

logger = logging.getLogger(__name__)

# Global service instance
_voice_transcriber = None


class VoiceTranscriber:
    """Service for transcribing audio to text using OpenAI Whisper"""

    def __init__(self):
        """Initialize transcriber with OpenAI client"""
        try:
            from openai import OpenAI
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                logger.warning("[VOICE] No OPENAI_API_KEY configured - Whisper will not work")
                self.client = None
            else:
                self.client = OpenAI(api_key=api_key)
                logger.info("[VOICE] OpenAI Whisper client initialized")
        except ImportError:
            logger.error("[VOICE] openai package not installed")
            self.client = None
        except Exception as e:
            logger.error(f"[VOICE] Error initializing OpenAI client: {e}")
            self.client = None

    def transcribe_audio(
        self,
        audio_file_path: str,
        language: str = "en"
    ) -> Dict:
        """
        Transcribe audio file using OpenAI Whisper

        Args:
            audio_file_path: Path to audio file (wav, mp3, m4a, ogg, etc.)
            language: Language code (default: "en")

        Returns:
            {
                "raw_transcription": str,
                "confidence": float (0-1),
                "duration_seconds": float,
                "language": str,
                "success": bool,
                "error": optional str
            }
        """
        try:
            if not self.client:
                return {
                    "success": False,
                    "error": "OpenAI client not initialized",
                    "raw_transcription": None,
                    "confidence": 0.0
                }

            # Verify file exists
            audio_path = Path(audio_file_path)
            if not audio_path.exists():
                return {
                    "success": False,
                    "error": f"Audio file not found: {audio_file_path}",
                    "raw_transcription": None,
                    "confidence": 0.0
                }

            # Transcribe with Whisper
            with open(audio_path, "rb") as audio_file:
                transcript = self.client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    language=language,
                    response_format="verbose_json"  # Get confidence scores
                )

            # Extract transcription
            raw_text = transcript.text if hasattr(transcript, 'text') else str(transcript)

            # Calculate confidence (Whisper doesn't return per-word, so use 0.9 if successful)
            confidence = 0.9

            # Get duration
            duration = getattr(transcript, 'duration', None)

            logger.info(f"[VOICE] Transcribed {audio_path.name}: {len(raw_text)} chars")

            return {
                "success": True,
                "raw_transcription": raw_text,
                "confidence": confidence,
                "duration_seconds": duration,
                "language": language,
                "model": "whisper-1"
            }

        except Exception as e:
            logger.error(f"[VOICE] Transcription error: {e}")
            return {
                "success": False,
                "error": str(e),
                "raw_transcription": None,
                "confidence": 0.0
            }

    def extract_medical_entities(self, transcription: str) -> Dict:
        """
        Extract medical entities from transcription

        Uses pattern matching to identify symptoms, medications, procedures.
        This is a simple rule-based approach - can be enhanced with NLP.

        Args:
            transcription: Transcribed text

        Returns:
            {
                "symptoms": [{text, confidence}],
                "medications": [{text, confidence}],
                "procedures": [{text, confidence}],
                "conditions": [{text, confidence}]
            }
        """
        try:
            entities = {
                "symptoms": [],
                "medications": [],
                "procedures": [],
                "conditions": []
            }

            if not transcription:
                return entities

            text_lower = transcription.lower()

            # Common symptoms (pattern-based)
            symptom_patterns = [
                ("fever", 0.95), ("cough", 0.95), ("headache", 0.95),
                ("nausea", 0.95), ("vomiting", 0.95), ("diarrhea", 0.95),
                ("fatigue", 0.9), ("weakness", 0.9), ("chest pain", 0.95),
                ("shortness of breath", 0.95), ("difficulty breathing", 0.95),
                ("dizziness", 0.9), ("pain", 0.85), ("ache", 0.85),
                ("swelling", 0.9), ("rash", 0.9), ("itching", 0.85)
            ]

            for symptom, confidence in symptom_patterns:
                if symptom in text_lower:
                    entities["symptoms"].append({
                        "text": symptom,
                        "confidence": confidence
                    })

            # Common medications
            medication_patterns = [
                ("aspirin", 0.95), ("ibuprofen", 0.95), ("paracetamol", 0.95),
                ("amoxicillin", 0.95), ("metformin", 0.95), ("lisinopril", 0.95),
                ("omeprazole", 0.95), ("atorvastatin", 0.95), ("levothyroxine", 0.95),
                ("insulin", 0.95), ("antibiotics", 0.9), ("painkillers", 0.85)
            ]

            for med, confidence in medication_patterns:
                if med in text_lower:
                    entities["medications"].append({
                        "text": med,
                        "confidence": confidence
                    })

            # Common procedures
            procedure_patterns = [
                ("x-ray", 0.95), ("ultrasound", 0.95), ("ct scan", 0.95),
                ("blood test", 0.95), ("lab work", 0.9), ("surgery", 0.95),
                ("vaccination", 0.95), ("injection", 0.9), ("endoscopy", 0.95)
            ]

            for proc, confidence in procedure_patterns:
                if proc in text_lower:
                    entities["procedures"].append({
                        "text": proc,
                        "confidence": confidence
                    })

            # Common conditions
            condition_patterns = [
                ("diabetes", 0.95), ("hypertension", 0.95), ("asthma", 0.95),
                ("pneumonia", 0.95), ("bronchitis", 0.95), ("arthritis", 0.95),
                ("heart disease", 0.95), ("stroke", 0.95), ("cancer", 0.95),
                ("infection", 0.9), ("inflammation", 0.9), ("allergy", 0.9)
            ]

            for condition, confidence in condition_patterns:
                if condition in text_lower:
                    entities["conditions"].append({
                        "text": condition,
                        "confidence": confidence
                    })

            logger.info(f"[VOICE] Extracted {len(entities['symptoms'])} symptoms, {len(entities['medications'])} medications")

            return entities

        except Exception as e:
            logger.error(f"[VOICE] Entity extraction error: {e}")
            return {
                "symptoms": [],
                "medications": [],
                "procedures": [],
                "conditions": []
            }

    def analyze_sentiment(self, transcription: str) -> str:
        """
        Simple sentiment analysis of transcription

        Returns: "positive", "negative", "neutral"
        """
        try:
            if not transcription:
                return "neutral"

            text_lower = transcription.lower()

            # Simple keyword-based sentiment
            positive_words = ["good", "better", "improved", "well", "fine", "healthy"]
            negative_words = ["bad", "worse", "pain", "infection", "severe", "critical"]

            positive_count = sum(1 for word in positive_words if word in text_lower)
            negative_count = sum(1 for word in negative_words if word in text_lower)

            if negative_count > positive_count:
                return "negative"
            elif positive_count > negative_count:
                return "positive"
            else:
                return "neutral"

        except Exception as e:
            logger.warning(f"[VOICE] Sentiment analysis error: {e}")
            return "neutral"


def get_voice_transcriber() -> VoiceTranscriber:
    """Factory function to get singleton service instance"""
    global _voice_transcriber
    if _voice_transcriber is None:
        _voice_transcriber = VoiceTranscriber()
    return _voice_transcriber


if __name__ == "__main__":
    # Test service
    import sys

    if len(sys.argv) < 2:
        print("Usage: python voice_transcriber.py <audio_file>")
        sys.exit(1)

    transcriber = get_voice_transcriber()
    audio_file = sys.argv[1]

    print(f"\n[TEST] Transcribing: {audio_file}")
    print("=" * 60)

    result = transcriber.transcribe_audio(audio_file)
    print(json.dumps(result, indent=2))

    if result.get("success"):
        print("\n[ENTITIES]")
        print("=" * 60)
        entities = transcriber.extract_medical_entities(result["raw_transcription"])
        print(json.dumps(entities, indent=2))

        print("\n[SENTIMENT]")
        print("=" * 60)
        sentiment = transcriber.analyze_sentiment(result["raw_transcription"])
        print(f"Sentiment: {sentiment}")
