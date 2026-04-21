"""Application container helpers for lazy imports and wiring."""

from __future__ import annotations

from typing import List, Tuple

from fastapi import APIRouter


def get_router_specs() -> List[Tuple[str, str, str]]:
    """Return `(module, symbol, tag)` specs for lazily-loaded API routers."""
    return [
        ("app.api.auth_new", "router", "auth"),
        ("app.api.chat_new", "router", "chat"),
        ("app.api.discharge", "router", "discharge"),
        ("app.api.treatment", "router", "treatment"),
        ("app.api.medical", "router", "medical"),
        ("app.api.upload", "router", "upload"),
        ("app.api.timeline", "router", "timeline"),
        ("app.api.analytics", "router", "analytics"),
        ("app.api.fhir", "router", "fhir"),
        ("app.api.health", "router", "health"),
        ("app.api.knowledge_base", "router", "knowledge"),
        ("app.api.reports", "router", "reports"),
        ("app.api.predictions", "router", "predictions"),
        ("app.api.voice", "router", "voice"),
        ("app.api.voice_consul", "router", "voice-consultation"),
        ("app.api.knowledge_graph_viz", "router", "knowledge-graph"),
        ("app.api.wearable_auth", "router", "wearable"),
        ("app.api.kb_growth", "router", "kb-growth"),
    ]


def import_router(module_path: str, symbol: str = "router"):
    """Import router symbol lazily by module path."""
    module = __import__(module_path, fromlist=[symbol])
    return getattr(module, symbol)


def register_api_routers(api_router: APIRouter) -> None:
    """Register modular API routers via lazy imports.

    Keeps `app.main` lean and reduces module-level coupling.
    """
    router_configs = [
        ("app.api.auth_new", "router", {}, {}),
        ("app.api.chat_new", "router", {}, {}),
        ("app.api.discharge", "router", {}, {}),
        ("app.api.treatment", "router", {}, {}), # Prefix in router itself
        ("app.api.medical", "router", {}, {}),   # Prefix in router itself
        ("app.api.upload", "router", {}, {}),    # Prefix in router itself
        ("app.api.timeline", "router", {"prefix": "/timeline"}, {"tags": ["timeline"]}),
        ("app.api.analytics", "router", {"prefix": "/analytics"}, {"tags": ["analytics"]}),
        ("app.api.fhir", "router", {"prefix": "/fhir"}, {"tags": ["fhir"]}),
        ("app.api.health", "router", {}, {"tags": ["health"]}),
        ("app.api.knowledge_base", "router", {"prefix": "/medical/knowledge"}, {"tags": ["knowledge-base"]}),
        ("app.api.knowledge_graph_viz", "router", {}, {"tags": ["knowledge-graph"]}),
        ("app.api.reports", "router", {"prefix": "/reports"}, {"tags": ["reports"]}),
        ("app.api.predictions", "router", {}, {"tags": ["predictions"]}),
        ("app.api.voice", "router", {}, {"tags": ["voice"]}),
        ("app.api.voice_consul", "router", {}, {"tags": ["voice-consultation"]}),
        ("app.api.wearable_auth", "router", {}, {"tags": ["wearable"]}),
        ("app.api.kb_growth", "router", {}, {"tags": ["kb-growth"]}),
        ("app.api.futuristic_kb", "router", {}, {"tags": ["futuristic-kb"]}),
        ("app.api.futuristic_features", "router", {}, {"tags": ["features"]}),
    ]

    for module_path, symbol, include_kwargs, extra_kwargs in router_configs:
        router = import_router(module_path, symbol)
        api_router.include_router(router, **include_kwargs, **extra_kwargs)
