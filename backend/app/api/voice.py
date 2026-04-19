"""
Voice Documentation API Router

Endpoints for uploading voice recordings, transcribing, and auto-generating SOAP notes.
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Depends, Form
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
import logging
import os
from pathlib import Path
import uuid
from datetime import datetime

from app.database import SessionLocal
from app.services.voice_transcriber import get_voice_transcriber
from app.services.voice_to_soap import get_voice_to_soap
from app.api.auth_new import get_current_user
from app.models import VoiceRecording, Conversation, PatientIntake, DischargeSummary
from app.models import User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/voice", tags=["voice"])

# Directory for storing voice files
VOICE_STORAGE_DIR = "backend/data/voice_recordings"
Path(VOICE_STORAGE_DIR).mkdir(parents=True, exist_ok=True)


def get_db():
    """Database dependency"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/upload")
async def upload_voice_recording(
    file: UploadFile = File(...),
    conversation_id: Optional[int] = Form(None),
    patient_intake_id: Optional[int] = Form(None),
    db: Session = Depends(get_db)
) -> Dict:
    """
    Upload voice recording for transcription

    Args:
        file: Audio file (wav, mp3, ogg, m4a, etc.)
        conversation_id: Optional conversation ID to attach to
        patient_intake_id: Optional patient ID

    Returns:
        {
            recording_id, file_path, filename,
            raw_transcription, medical_entities, sentiment,
            soap_note_preview
        }
    """
    try:
        # Validate file type
        allowed_extensions = {".wav", ".mp3", ".ogg", ".m4a", ".flac", ".aac"}
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in allowed_extensions:
            raise HTTPException(
                status_code=400,
                detail=f"File type {file_ext} not supported. Use: {allowed_extensions}"
            )

        # Save file
        recording_id = str(uuid.uuid4())
        file_path = os.path.join(VOICE_STORAGE_DIR, f"{recording_id}{file_ext}")

        contents = await file.read()
        with open(file_path, "wb") as f:
            f.write(contents)

        logger.info(f"[VOICE] Saved recording: {file_path} ({len(contents)} bytes)")

        # Transcribe
        transcriber = get_voice_transcriber()
        transcription_result = transcriber.transcribe_audio(file_path)

        if not transcription_result.get("success"):
            raise HTTPException(
                status_code=500,
                detail=f"Transcription failed: {transcription_result.get('error', 'Unknown error')}"
            )

        raw_transcription = transcription_result["raw_transcription"]
        confidence = transcription_result["confidence"]

        # Extract entities
        entities = transcriber.extract_medical_entities(raw_transcription)
        sentiment = transcriber.analyze_sentiment(raw_transcription)

        # Generate SOAP note preview
        soap_generator = get_voice_to_soap()
        soap_note = soap_generator.generate_soap_note(
            transcription=raw_transcription,
            medical_entities=entities,
            include_rag_search=False  # Quick preview, skip RAG
        )

        # Get patient context for database
        _patient_context = None
        if patient_intake_id:
            patient = db.query(PatientIntake).filter(
                PatientIntake.id == patient_intake_id
            ).first()
            if patient:
                _patient_context = {
                    "age": patient.age,
                    "gender": patient.gender,
                    "family_history": []
                }

        # Store in database
        voice_recording = VoiceRecording(
            recording_id=recording_id,
            conversation_id=conversation_id,
            patient_intake_id=patient_intake_id,
            file_path=file_path,
            file_size=len(contents),
            duration_seconds=transcription_result.get("duration_seconds"),
            audio_format=file_ext.lstrip("."),
            raw_transcription=raw_transcription,
            transcription_confidence=confidence,
            medical_entities=entities,
            sentiment=sentiment,
            is_processed=True
        )

        db.add(voice_recording)
        db.commit()
        db.refresh(voice_recording)

        logger.info(f"[VOICE] Recording stored: {recording_id}")

        return {
            "success": True,
            "recording_id": recording_id,
            "file_path": file_path,
            "filename": file.filename,
            "file_size": len(contents),
            "duration_seconds": transcription_result.get("duration_seconds"),
            "raw_transcription": raw_transcription,
            "transcription_confidence": confidence,
            "medical_entities": entities,
            "sentiment": sentiment,
            "soap_note_preview": soap_note,
            "created_at": voice_recording.created_at.isoformat()
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[VOICE] Upload error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate-documentation")
def generate_documentation(
    payload: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Dict:
    """
    Generate final SOAP note and discharge summary from voice recording

    Args:
        payload: {
            recording_id: str,
            patient_intake_id: int,
            edited_transcription: optional str (if user edited),
            approve_entities: bool (use extracted entities)
        }

    Returns:
        {
            discharge_summary_id, soap_note, created_at
        }
    """
    try:
        recording_id = payload.get("recording_id")
        patient_intake_id = payload.get("patient_intake_id")
        edited_transcription = payload.get("edited_transcription")

        if not recording_id or not patient_intake_id:
            raise HTTPException(
                status_code=400,
                detail="recording_id and patient_intake_id required"
            )

        # Get voice recording
        voice_recording = db.query(VoiceRecording).filter(
            VoiceRecording.recording_id == recording_id
        ).first()

        if not voice_recording:
            raise HTTPException(status_code=404, detail="Recording not found")

        # Use edited transcription if provided, otherwise original
        transcription = edited_transcription or voice_recording.raw_transcription

        # Get patient data
        patient = db.query(PatientIntake).filter(
            PatientIntake.id == patient_intake_id
        ).first()

        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")

        # Re-extract entities if transcription was edited
        if edited_transcription:
            transcriber = get_voice_transcriber()
            medical_entities = transcriber.extract_medical_entities(transcription)
        else:
            medical_entities = voice_recording.medical_entities or {}

        # Generate SOAP note with RAG grounding
        soap_generator = get_voice_to_soap()
        soap_note = soap_generator.generate_soap_note(
            transcription=transcription,
            medical_entities=medical_entities,
            patient_context={
                "age": patient.age,
                "gender": patient.gender
            },
            include_rag_search=True
        )

        # Create discharge summary from SOAP note
        subjective = soap_note.get("subjective", {})
        objective = soap_note.get("objective", {})
        assessment = soap_note.get("assessment", {})
        plan = soap_note.get("plan", {})

        # Build discharge summary text
        discharge = DischargeSummary(
            created_by_id=current_user.id,
            patient_name=patient.name,
            patient_age=patient.age,
            patient_gender=patient.gender,
            chief_complaint=subjective.get("chief_complaint", ""),
            history_present_illness=subjective.get("history_present_illness", ""),
            past_medical_history=subjective.get("past_medical_history", ""),
            physical_examination=objective.get("physical_examination", ""),
            diagnosis=assessment.get("assessment", ""),
            medications=", ".join([med["name"] for med in plan.get("medications", [])]),
            discharge_medications=", ".join([med["name"] for med in plan.get("medications", [])]),
            follow_up_instructions=f"Follow-up: {plan.get('follow_up', {}).get('timeframe', 'As needed')}",
            ai_summary=f"Auto-generated from voice recording: {recording_id}"
        )

        db.add(discharge)
        db.commit()
        db.refresh(discharge)

        # Link voice recording to discharge summary
        voice_recording.soap_note_id = discharge.id
        voice_recording.processed_at = datetime.utcnow()
        db.commit()

        logger.info(f"[VOICE] Generated discharge summary {discharge.id} from recording {recording_id}")

        return {
            "success": True,
            "discharge_summary_id": discharge.id,
            "recording_id": recording_id,
            "patient_id": patient_intake_id,
            "soap_note": soap_note,
            "created_at": discharge.created_at.isoformat()
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[VOICE] Documentation generation error: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/recording/{recording_id}")
def get_recording(
    recording_id: str,
    db: Session = Depends(get_db)
) -> Dict:
    """
    Get details of a voice recording

    Args:
        recording_id: Recording UUID

    Returns:
        Recording details including transcription and entities
    """
    try:
        recording = db.query(VoiceRecording).filter(
            VoiceRecording.recording_id == recording_id
        ).first()

        if not recording:
            raise HTTPException(status_code=404, detail="Recording not found")

        return {
            "success": True,
            "recording_id": recording.recording_id,
            "patient_id": recording.patient_intake_id,
            "conversation_id": recording.conversation_id,
            "file_path": recording.file_path,
            "duration_seconds": recording.duration_seconds,
            "raw_transcription": recording.raw_transcription,
            "processed_transcription": recording.processed_transcription,
            "transcription_confidence": recording.transcription_confidence,
            "medical_entities": recording.medical_entities,
            "sentiment": recording.sentiment,
            "is_processed": recording.is_processed,
            "created_at": recording.created_at.isoformat(),
            "processed_at": recording.processed_at.isoformat() if recording.processed_at else None
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[VOICE] Error retrieving recording: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/recording/{recording_id}")
def delete_recording(
    recording_id: str,
    db: Session = Depends(get_db)
) -> Dict:
    """
    Delete a voice recording and associated file

    Args:
        recording_id: Recording UUID

    Returns:
        Success confirmation
    """
    try:
        recording = db.query(VoiceRecording).filter(
            VoiceRecording.recording_id == recording_id
        ).first()

        if not recording:
            raise HTTPException(status_code=404, detail="Recording not found")

        # Delete file
        if recording.file_path and os.path.exists(recording.file_path):
            os.remove(recording.file_path)
            logger.info(f"[VOICE] Deleted file: {recording.file_path}")

        # Delete database record
        db.delete(recording)
        db.commit()

        logger.info(f"[VOICE] Deleted recording: {recording_id}")

        return {
            "success": True,
            "message": f"Recording {recording_id} deleted"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[VOICE] Error deleting recording: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
