"""Ambient Transcriber Service - Real-time WebSocket audio transcription"""
import logging
logger = logging.getLogger(__name__)
_ambient_transcriber = None

class AmbientTranscriber:
    def __init__(self):
        from app.services.voice_transcriber import get_voice_transcriber
        self.transcriber = get_voice_transcriber()
    
    async def process_audio_stream(self, audio_chunks: list, buffer_timeout_seconds: float = 2.0):
        try:
            buffered_audio = b"".join(audio_chunks)
            if not buffered_audio:
                return {"partial_transcript": "", "entities": [], "confidence": 0.0}
            
            result = self.transcriber.transcribe_audio("/tmp/ambient_audio.wav")
            if result.get("success"):
                transcription = result.get("raw_transcription", "")
                entities = self.transcriber.extract_medical_entities(transcription)
                return {
                    "partial_transcript": transcription,
                    "full_transcript": transcription,
                    "medical_entities": entities,
                    "confidence": result.get("confidence", 0.9),
                    "sentiment": self.transcriber.analyze_sentiment(transcription)
                }
            return {"error": result.get("error"), "partial_transcript": "", "entities": [], "confidence": 0.0}
        except Exception as e:
            logger.error(f"[AMBIENT] Error: {e}")
            return {"error": str(e), "partial_transcript": "", "entities": [], "confidence": 0.0}

def get_ambient_transcriber() -> AmbientTranscriber:
    global _ambient_transcriber
    if _ambient_transcriber is None:
        _ambient_transcriber = AmbientTranscriber()
    return _ambient_transcriber
