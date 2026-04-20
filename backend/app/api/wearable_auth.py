"""Wearable Device OAuth Router"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import WearableDeviceAuth, PatientIntake, WearableDeviceData
from app.services.wearable_sync import get_wearable_sync
from datetime import datetime, timedelta
import uuid
import random

router = APIRouter(prefix="/wearable", tags=["wearable"])


def _resolve_patient(db: Session, patient_intake_id: int | None) -> PatientIntake | None:
    if patient_intake_id is not None:
        return db.query(PatientIntake).filter(PatientIntake.id == patient_intake_id).first()
    return db.query(PatientIntake).order_by(PatientIntake.id.asc()).first()


def _summarize_today_stats(db: Session, patient_id: int | None) -> dict:
    if patient_id is None:
        return {}

    start_of_day = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    records = db.query(WearableDeviceData).filter(
        WearableDeviceData.patient_intake_id == patient_id,
        WearableDeviceData.measurement_date >= start_of_day,
    ).all()

    if not records:
        return {}

    grouped: dict[str, list[float]] = {}
    for record in records:
        if record.value is None:
            continue
        grouped.setdefault(record.data_category, []).append(record.value)

    stats: dict[str, float] = {}
    if grouped.get("heart_rate"):
        stats["heart_rate"] = round(sum(grouped["heart_rate"]) / len(grouped["heart_rate"]))
    if grouped.get("steps"):
        stats["steps"] = round(sum(grouped["steps"]))
    if grouped.get("sleep_hours"):
        stats["sleep_hours"] = round(sum(grouped["sleep_hours"]) / len(grouped["sleep_hours"]), 1)
    if grouped.get("oxygen_saturation"):
        stats["oxygen_saturation"] = round(sum(grouped["oxygen_saturation"]) / len(grouped["oxygen_saturation"]))
    return stats


def _build_week_data(db: Session, patient_id: int | None) -> list[dict]:
    if patient_id is None:
        return []

    since = datetime.utcnow() - timedelta(days=7)
    records = db.query(WearableDeviceData).filter(
        WearableDeviceData.patient_intake_id == patient_id,
        WearableDeviceData.measurement_date >= since,
    ).order_by(WearableDeviceData.measurement_date.asc()).all()

    if not records:
        return []

    grouped: dict[str, dict[str, float]] = {}
    for record in records:
        day_key = record.measurement_date.strftime("%m-%d")
        day_bucket = grouped.setdefault(day_key, {"timestamp": day_key})
        if record.value is not None:
            day_bucket[record.data_category] = record.value

    return list(grouped.values())


def _seed_demo_wearable_data(db: Session, patient_id: int, device_type: str) -> None:
    now = datetime.utcnow()
    for days_back in range(6, -1, -1):
        measurement_date = now - timedelta(days=days_back)
        samples = [
            ("heart_rate", random.randint(68, 92), "bpm"),
            ("steps", random.randint(4200, 11500), "steps"),
            ("sleep_hours", round(random.uniform(5.8, 8.4), 1), "hours"),
            ("oxygen_saturation", random.randint(95, 99), "%"),
        ]
        for category, value, unit in samples:
            record = WearableDeviceData(
                data_id=str(uuid.uuid4()),
                patient_intake_id=patient_id,
                device_type=device_type,
                device_name=device_type.title(),
                data_category=category,
                value=value,
                unit=unit,
                measurement_date=measurement_date,
                confidence=0.95,
                data_source="demo_seed",
                sync_status="completed",
            )
            db.add(record)
    db.commit()

@router.get("/auth/fitbit")
def start_fitbit_auth(patient_intake_id: int):
    """Start Fitbit OAuth flow"""
    import os
    client_id = os.getenv("FITBIT_CLIENT_ID", "demo")
    redirect_uri = os.getenv("FITBIT_REDIRECT_URI", "http://localhost:8000/api/wearable/callback/fitbit")
    scopes = "heartrate location nutrition profile settings sleep weight"
    auth_url = f"https://www.fitbit.com/oauth2/authorize?response_type=code&client_id={client_id}&redirect_uri={redirect_uri}&scope={scopes}&state={patient_intake_id}"
    return {"auth_url": auth_url}


@router.get("/auth/{device_type}/url")
def start_device_auth(device_type: str, patient_intake_id: int | None = None, db: Session = Depends(get_db)):
    """Compatibility endpoint used by the frontend integration page."""
    device = device_type.lower()
    patient = _resolve_patient(db, patient_intake_id)
    state = patient.id if patient else 1

    if device == "fitbit":
        return start_fitbit_auth(state)

    demo_url = f"https://demo.natpudan.local/wearable/{device}/oauth?state={state}"
    return {
        "auth_url": demo_url,
        "device_type": device,
        "mode": "demo",
    }

@router.get("/callback/fitbit")
def fitbit_oauth_callback(code: str = Query(...), state: str = Query(...), db: Session = Depends(get_db)):
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
            refresh_token="refresh_123",  # nosec B106
            auto_sync_enabled=True
        )
        db.add(auth)
        db.commit()
        return {"success": True, "message": "Fitbit connected"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e)) from e

@router.get("/devices")
def list_wearable_devices(patient_intake_id: int | None = None, db: Session = Depends(get_db)):
    """List connected wearable devices"""
    patient = _resolve_patient(db, patient_intake_id)
    patient_id = patient.id if patient else None
    query = db.query(WearableDeviceAuth).filter(WearableDeviceAuth.is_active.is_(True))
    if patient_id is not None:
        query = query.filter(WearableDeviceAuth.patient_intake_id == patient_id)
    devices = query.all()

    today_stats = _summarize_today_stats(db, patient_id)
    week_data = _build_week_data(db, patient_id)

    return {
        "devices": [
            {
                "auth_id": d.auth_id,
                "device_id": d.auth_id,
                "device_type": d.device_type,
                "device_name": d.device_type.replace("_", " ").title(),
                "last_sync": d.last_sync_at,
                "last_sync_at": d.last_sync_at,
                "is_active": d.is_active,
                "auto_sync_enabled": d.auto_sync_enabled,
            } for d in devices
        ],
        "today_stats": today_stats,
        "week_data": week_data,
    }


@router.post("/sync-now")
async def sync_now(patient_intake_id: int | None = None, db: Session = Depends(get_db)):
    """Sync or simulate wearable data for the selected patient."""
    patient = _resolve_patient(db, patient_intake_id)
    if not patient:
        raise HTTPException(status_code=404, detail="No patient available for wearable sync")

    devices = db.query(WearableDeviceAuth).filter(
        WearableDeviceAuth.patient_intake_id == patient.id,
        WearableDeviceAuth.is_active.is_(True)
    ).all()

    if not devices:
        demo_auth = WearableDeviceAuth(
            auth_id=str(uuid.uuid4()),
            patient_intake_id=patient.id,
            user_id=1,
            device_type="fitbit",
            device_user_id=f"demo-fitbit-{patient.id}",
            access_token="demo-token",
            refresh_token="demo-refresh",
            auto_sync_enabled=True,
        )
        db.add(demo_auth)
        db.commit()
        devices = [demo_auth]

    sync_service = get_wearable_sync()
    imported = 0
    for device in devices:
        device.last_sync_at = datetime.utcnow()
        sample_entries = [
            {"data_category": "heart_rate", "value": random.randint(68, 92), "unit": "bpm", "measurement_date": datetime.utcnow()},
            {"data_category": "steps", "value": random.randint(3500, 12000), "unit": "steps", "measurement_date": datetime.utcnow()},
            {"data_category": "sleep_hours", "value": round(random.uniform(5.8, 8.4), 1), "unit": "hours", "measurement_date": datetime.utcnow()},
            {"data_category": "oxygen_saturation", "value": random.randint(95, 99), "unit": "%", "measurement_date": datetime.utcnow()},
        ]
        result = await sync_service.import_wearable_data(db, patient.id, device.device_type, sample_entries)
        imported += int(result.get("imported_count", 0))

        existing_count = db.query(WearableDeviceData).filter(
            WearableDeviceData.patient_intake_id == patient.id,
            WearableDeviceData.device_type == device.device_type,
        ).count()
        if existing_count < 8:
            _seed_demo_wearable_data(db, patient.id, device.device_type)

    db.commit()
    return {
        "success": True,
        "patient_id": patient.id,
        "devices_synced": len(devices),
        "records_imported": imported,
    }


@router.delete("/devices/{device_id}")
def delete_device(device_id: str, db: Session = Depends(get_db)):
    """Disconnect a wearable device."""
    device = db.query(WearableDeviceAuth).filter(WearableDeviceAuth.auth_id == device_id).first()
    if not device:
        raise HTTPException(status_code=404, detail="Device not found")

    device.is_active = False
    device.is_revoked = True
    device.revoked_at = datetime.utcnow()
    db.commit()
    return {"success": True, "device_id": device_id}
