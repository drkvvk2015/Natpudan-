"""Wearable Device OAuth Router"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import WearableDeviceAuth, PatientIntake
import uuid
from datetime import datetime

router = APIRouter(prefix="/wearable", tags=["wearable"])

@router.get("/auth/fitbit")
def start_fitbit_auth(patient_intake_id: int):
    """Start Fitbit OAuth flow"""
    import os
    client_id = os.getenv("FITBIT_CLIENT_ID", "demo")
    redirect_uri = os.getenv("FITBIT_REDIRECT_URI", "http://localhost:8000/api/wearable/callback/fitbit")
    scopes = "heartrate location nutrition profile settings sleep weight"
    auth_url = f"https://www.fitbit.com/oauth2/authorize?response_type=code&client_id={client_id}&redirect_uri={redirect_uri}&scope={scopes}&state={patient_intake_id}"
    return {"auth_url": auth_url}

@router.get("/callback/fitbit")
def fitbit_oauth_callback(code: str = Query(...), state: str = Query(...), db: Session = Depends(SessionLocal)):
    """Handle Fitbit OAuth callback"""
    try:
        patient_intake_id = int(state)
        patient = db.query(PatientIntake).filter(PatientIntake.id == patient_intake_id).first()
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")
        
        auth = WearableDeviceAuth(
            auth_id=str(uuid.uuid4()),
            patient_intake_id=patient_intake_id,
            user_id=1,
            device_type="fitbit",
            device_user_id="fitbit_user_123",
            access_token=code,
            refresh_token="refresh_123",
            auto_sync_enabled=True
        )
        db.add(auth)
        db.commit()
        return {"success": True, "message": "Fitbit connected"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/devices")
def list_wearable_devices(patient_intake_id: int, db: Session = Depends(SessionLocal)):
    """List connected wearable devices"""
    devices = db.query(WearableDeviceAuth).filter(
        WearableDeviceAuth.patient_intake_id == patient_intake_id,
        WearableDeviceAuth.is_active == True
    ).all()
    return {
        "devices": [
            {
                "auth_id": d.auth_id,
                "device_type": d.device_type,
                "last_sync": d.last_sync_at,
                "is_active": d.is_active
            } for d in devices
        ]
    }
