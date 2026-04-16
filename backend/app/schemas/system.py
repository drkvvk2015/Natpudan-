from pydantic import BaseModel, Field
from typing import Dict, Literal, Optional


class RootResponse(BaseModel):
    status: str = Field(..., examples=["ok"])
    timestamp: str


class HealthResponse(BaseModel):
    status: Literal["healthy", "degraded"]
    service: str
    services: Dict[str, bool]
    timestamp: str


class ResourceUsage(BaseModel):
    total: int
    available: Optional[int] = None
    percent: float
    used: int
    free: Optional[int] = None


class DetailedHealthResponse(BaseModel):
    status: Literal["healthy", "error"]
    uptime: int
    cpu_usage: float
    memory_usage: ResourceUsage
    disk_usage: ResourceUsage
    database_status: str
    cache_status: str
    assistant_status: str
    knowledge_base_status: str
    last_check_in: str
    error: Optional[str] = None
