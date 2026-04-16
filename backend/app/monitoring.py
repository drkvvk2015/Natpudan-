"""Monitoring and error tracking helpers."""

from __future__ import annotations

import logging

from app.core.config import settings

logger = logging.getLogger(__name__)


def init_monitoring() -> None:
    """Initialize optional monitoring providers."""
    if not settings.SENTRY_DSN:
        logger.info("Monitoring provider not configured; skipping remote error tracking")
        return

    try:
        import sentry_sdk
        from sentry_sdk.integrations.fastapi import FastApiIntegration

        sentry_sdk.init(
            dsn=settings.SENTRY_DSN,
            environment=settings.ENVIRONMENT,
            release=settings.APP_VERSION,
            traces_sample_rate=settings.SENTRY_TRACES_SAMPLE_RATE,
            profiles_sample_rate=0.0,
            integrations=[FastApiIntegration()],
            send_default_pii=False,
        )
        logger.info("Sentry monitoring initialized")
    except Exception as exc:  # pragma: no cover - optional dependency path
        logger.warning("Failed to initialize monitoring: %s", exc)
