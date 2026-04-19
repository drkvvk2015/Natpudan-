"""Monitoring and error tracking helpers."""

from __future__ import annotations

import logging
import time
from functools import lru_cache
from typing import Optional

from app.core.config import settings

logger = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def _metrics_registry():
    """Create Prometheus metrics lazily to keep optional dependency behavior."""
    try:
        from prometheus_client import Counter, Histogram

        return {
            "requests_total": Counter(
                "natpudan_requests_total",
                "Total HTTP requests handled",
                ["method", "path", "status"],
            ),
            "request_latency_seconds": Histogram(
                "natpudan_request_latency_seconds",
                "HTTP request latency in seconds",
                ["method", "path"],
            ),
        }
    except Exception as exc:  # pragma: no cover - optional dependency path
        logger.debug("Prometheus client unavailable: %s", exc)
        return None


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


def record_http_metrics(method: str, path: str, status: int, started_at: float) -> None:
    """Record per-request Prometheus counters/histograms when available."""
    registry = _metrics_registry()
    if not registry:
        return

    duration = max(time.perf_counter() - started_at, 0)
    registry["requests_total"].labels(method=method, path=path, status=str(status)).inc()
    registry["request_latency_seconds"].labels(method=method, path=path).observe(duration)


def render_prometheus_metrics() -> Optional[str]:
    """Return metrics exposition text, or None when Prometheus is unavailable."""
    try:
        from prometheus_client import generate_latest

        return generate_latest().decode("utf-8")
    except Exception as exc:  # pragma: no cover - optional dependency path
        logger.debug("Failed generating Prometheus metrics: %s", exc)
        return None
