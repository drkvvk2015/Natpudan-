"""WebSocket API for ambient transcription in consultations"""
from fastapi import APIRouter, WebSocket, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db, SessionLocal
from app.services.ambient_transcriber import get_ambient_transcriber
from app.models import Conversation, Message
import json
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/voice/consultation", tags=["voice-consultation"])

@router.websocket("/ws/{conversation_id}")
async def websocket_consultation_transcription(websocket: WebSocket, conversation_id: int):
    db = None
    try:
        await websocket.accept()
        db = SessionLocal()
        conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
        
        if not conversation:
            await websocket.close(code=1000, reason="Conversation not found")
            return
        
        transcriber = get_ambient_transcriber()
        audio_chunks = []
        
        while True:
            data = await websocket.receive_text()
            msg = json.loads(data)
            
            if msg.get("type") == "audio_chunk":
                import base64
                chunk = base64.b64decode(msg.get("data", ""))
                audio_chunks.append(chunk)
                
                if len(audio_chunks) >= 5 or msg.get("flush"):
                    result = await transcriber.process_audio_stream(audio_chunks)
                    
                    if result.get("partial_transcript"):
                        message = Message(
                            conversation_id=conversation_id,
                            role="ambient_transcription",
                            content=result["partial_transcript"]
                        )
                        db.add(message)
                        db.commit()
                        
                        await websocket.send_json({
                            "type": "transcription",
                            "text": result["partial_transcript"],
                            "entities": result.get("medical_entities", {}),
                            "confidence": result.get("confidence", 0)
                        })
                        audio_chunks = []
                        
    except Exception as e:
        logger.error(f"[VOICE_CONSUL] WebSocket error: {e}")
    finally:
        if db:
            db.close()

@router.get("/summary/{conversation_id}")
def get_consultation_summary(conversation_id: int, db: Session = Depends(get_db)):
    try:
        messages = db.query(Message).filter(
            Message.conversation_id == conversation_id,
            Message.role == "ambient_transcription"
        ).all()
        
        return {
            "success": True,
            "conversation_id": conversation_id,
            "transcriptions": [m.content for m in messages],
            "count": len(messages)
        }
    except Exception as e:
        logger.error(f"[VOICE_CONSUL] Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
