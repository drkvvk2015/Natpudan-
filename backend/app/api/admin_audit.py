"""
Admin Audit Logs API
Endpoints:
- GET /api/admin/audit-logs: list with filters
- POST /api/admin/audit-logs: create a manual audit entry
- GET /api/admin/audit-logs/export: export CSV
"""

from __future__ import annotations

import csv
import io
import json
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import select, and_, desc

from app.database import get_db
from app.models import AuditLog, User
from app.services.audit_logger import log_action

router = APIRouter(prefix="/admin", tags=["admin-audit"])


@router.get("/audit-logs")
def list_audit_logs(
    request: Request,
    db: Session = Depends(get_db),
    user_id: Optional[int] = Query(None),
    action: Optional[str] = Query(None),
    resource: Optional[str] = Query(None),
    start: Optional[str] = Query(None, description="ISO datetime start"),
    end: Optional[str] = Query(None, description="ISO datetime end"),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
) -> Dict[str, Any]:
    """List audit logs with simple filters and pagination."""
    filters = []
    if user_id is not None:
        filters.append(AuditLog.user_id == user_id)
    if action:
        filters.append(AuditLog.action == action)
    if resource:
        filters.append(AuditLog.resource == resource)
    if start:
        try:
            start_dt = datetime.fromisoformat(start)
            filters.append(AuditLog.created_at >= start_dt)
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid 'start' ISO datetime")
    if end:
        try:
            end_dt = datetime.fromisoformat(end)
            filters.append(AuditLog.created_at <= end_dt)
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid 'end' ISO datetime")

    stmt = select(AuditLog).order_by(desc(AuditLog.created_at)).offset(offset).limit(limit)
    if filters:
        stmt = select(AuditLog).where(and_(*filters)).order_by(desc(AuditLog.created_at)).offset(offset).limit(limit)

    rows = db.execute(stmt).scalars().all()

    # Map to serializable format
    def to_dict(row: AuditLog) -> Dict[str, Any]:
        return {
            "id": row.id,
            "user_id": row.user_id,
            "action": row.action,
            "resource": row.resource,
            "details": _safe_json(row.details),
            "ip_address": row.ip_address,
            "user_agent": row.user_agent,
            "created_at": row.created_at.isoformat() if row.created_at else None,
        }

    return {"items": [to_dict(r) for r in rows], "count": len(rows), "offset": offset, "limit": limit}


@router.post("/audit-logs")
def create_audit_log(
    request: Request,
    payload: Dict[str, Any],
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """Create a manual audit log entry."""
    user_id = payload.get("user_id")
    action = payload.get("action")
    resource = payload.get("resource")
    details = payload.get("details")

    if not action:
        raise HTTPException(status_code=400, detail="'action' is required")

    entry = log_action(
        db=db,
        user_id=user_id,
        action=str(action),
        resource=str(resource) if resource else None,
        details=details if isinstance(details, dict) else None,
        request=request,
    )

    return {
        "id": entry.id,
        "user_id": entry.user_id,
        "action": entry.action,
        "resource": entry.resource,
        "details": _safe_json(entry.details),
        "ip_address": entry.ip_address,
        "user_agent": entry.user_agent,
        "created_at": entry.created_at.isoformat() if entry.created_at else None,
    }


@router.get("/audit-logs/export")
def export_audit_logs_csv(
    request: Request,
    db: Session = Depends(get_db),
    user_id: Optional[int] = Query(None),
    action: Optional[str] = Query(None),
    resource: Optional[str] = Query(None),
    start: Optional[str] = Query(None),
    end: Optional[str] = Query(None),
) -> StreamingResponse:
    """Export filtered logs as CSV."""
    # Reuse filtering logic
    filters = []
    if user_id is not None:
        filters.append(AuditLog.user_id == user_id)
    if action:
        filters.append(AuditLog.action == action)
    if resource:
        filters.append(AuditLog.resource == resource)
    if start:
        try:
            start_dt = datetime.fromisoformat(start)
            filters.append(AuditLog.created_at >= start_dt)
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid 'start' ISO datetime")
    if end:
        try:
            end_dt = datetime.fromisoformat(end)
            filters.append(AuditLog.created_at <= end_dt)
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid 'end' ISO datetime")

    stmt = select(AuditLog).order_by(desc(AuditLog.created_at))
    if filters:
        stmt = select(AuditLog).where(and_(*filters)).order_by(desc(AuditLog.created_at))

    rows = db.execute(stmt).scalars().all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["id", "user_id", "action", "resource", "details", "ip_address", "user_agent", "created_at"])
    for row in rows:
        writer.writerow([
            row.id,
            row.user_id,
            row.action,
            row.resource,
            row.details,
            row.ip_address,
            row.user_agent,
            row.created_at.isoformat() if row.created_at else "",
        ])

    output.seek(0)
    filename = f"audit_logs_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"
    return StreamingResponse(
        output,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )


def _safe_json(text: Optional[str]) -> Any:
    if text is None:
        return None
    try:
        return json.loads(text)
    except Exception:
        return text
