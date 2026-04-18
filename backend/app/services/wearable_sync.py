"""Wearable Device Sync Service"""
import logging
from datetime import datetime
logger = logging.getLogger(__name__)
_wearable_sync = None

class WearableSync:
    def __init__(self):
        pass
    
    async def fetch_fitbit_data(self, access_token: str, user_id: str, data_type: str = "heart_rate"):
        try:
            import requests
            headers = {"Authorization": f"Bearer {access_token}"}
            url = f"https://api.fitbit.com/1/user/{user_id}/activities/heart/date/today/1d.json"
            resp = requests.get(url, headers=headers)
            if resp.status_code == 200:
                data = resp.json().get('activities-heart', [])
                return {"success": True, "data": data}
            return {"success": False, "error": f"Status {resp.status_code}"}
        except Exception as e:
            logger.error(f"[WEARABLE] Fitbit fetch error: {e}")
            return {"success": False, "error": str(e)}
    
    async def import_wearable_data(self, db, patient_intake_id: int, device_type: str, data_entries: list):
        try:
            from app.models import WearableDeviceData
            import uuid
            
            imported = 0
            for entry in data_entries:
                record = WearableDeviceData(
                    data_id=str(uuid.uuid4()),
                    patient_intake_id=patient_intake_id,
                    device_type=device_type,
                    data_category=entry.get("data_category"),
                    value=entry.get("value"),
                    unit=entry.get("unit"),
                    measurement_date=entry.get("measurement_date", datetime.utcnow()),
                    confidence=entry.get("confidence", 0.9)
                )
                db.add(record)
                imported += 1
            
            db.commit()
            logger.info(f"[WEARABLE] Imported {imported} records")
            return {"success": True, "imported_count": imported}
        except Exception as e:
            logger.error(f"[WEARABLE] Import error: {e}")
            db.rollback()
            return {"success": False, "error": str(e)}

def get_wearable_sync() -> WearableSync:
    global _wearable_sync
    if _wearable_sync is None:
        _wearable_sync = WearableSync()
    return _wearable_sync
