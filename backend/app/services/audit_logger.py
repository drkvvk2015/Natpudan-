"""
Audit logging service to record user actions for compliance and debugging.
Provides a simple function `log_action` to write an audit record.
"""

from __future__ import annotations

import json
import logging
from typing import Any, Dict, Optional
from sqlalchemy.orm import Session
from fastapi import Request

from app.database import get_db
from app.models import AuditLog, User

logger = logging.getLogger(__name__)


def log_action(
    *,
    db: Optional[Session] = None,
    user_id: Optional[int] = None,
    action: str,
    resource: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None,
    request: Optional[Request] = None,
) -> AuditLog:
    """
    Write an audit log entry.

    Args:
        db: SQLAlchemy session (optional, will create a new one if not provided)
        user_id: ID of the user performing the action (optional)
        action: Short action name
        resource: Target resource identifier (optional)
        details: Extra context dict (optional)
        request: FastAPI Request to extract IP and user-agent (optional)
    """
    own_session = False
    if db is None:
        own_session = True
        db_gen = get_db()
        db = next(db_gen)

    try:
        ip_address = None
        user_agent = None
        if request is not None:
            try:
                ip_address = request.client.host if request.client else None
                user_agent = request.headers.get("User-Agent")
            except Exception:
                pass

        details_text = None
        if details is not None:
            try:
                details_text = json.dumps(details, ensure_ascii=False)
            except Exception:
                details_text = str(details)

        entry = AuditLog(
            user_id=user_id,
            action=action,
            resource=resource,
            details=details_text,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        db.add(entry)
        db.commit()
        db.refresh(entry)
        return entry
    except Exception as e:
        logger.error(f"Audit log write failed: {e}")
        if own_session:
            try:
                db.rollback()
            except Exception:
                pass
        raise
    finally:
        if own_session:
            try:
                # close generator
                next(db_gen, None)
            except Exception:
                pass
