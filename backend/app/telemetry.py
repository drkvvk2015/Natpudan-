"""OpenTelemetry bootstrap helpers (optional runtime dependency)."""

from __future__ import annotations

import logging
import os
from typing import Optional

logger = logging.getLogger(__name__)


def init_telemetry(service_name: str = "natpudan-backend") -> bool:
    """Initialize OpenTelemetry tracing when OTEL environment is configured.

    Returns True when tracing is initialized successfully.
    """
    otlp_endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "").strip()
    if not otlp_endpoint:
        logger.info("OpenTelemetry endpoint not configured; tracing disabled")
        return False

    try:
        from opentelemetry import trace
        from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
        from opentelemetry.sdk.resources import Resource
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor
        from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

        resource = Resource.create({"service.name": service_name})
        provider = TracerProvider(resource=resource)
        provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter(endpoint=otlp_endpoint)))
        trace.set_tracer_provider(provider)

        logger.info("OpenTelemetry tracing initialized (endpoint=%s)", otlp_endpoint)
        return True
    except Exception as exc:  # pragma: no cover - optional dependency path
        logger.warning("OpenTelemetry init failed: %s", exc)
        return False


def instrument_fastapi_app(app) -> None:
    """Instrument a FastAPI app if OpenTelemetry instrumentation is available."""
    try:
        from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

        FastAPIInstrumentor.instrument_app(app)
        logger.info("FastAPI OpenTelemetry instrumentation enabled")
    except Exception as exc:  # pragma: no cover - optional dependency path
        logger.debug("FastAPI telemetry instrumentation skipped: %s", exc)
