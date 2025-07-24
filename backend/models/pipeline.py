from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum

class PipelineStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"
    CANCELLED = "cancelled"

class StepType(str, Enum):
    EXTRACT = "extract"
    TRANSFORM = "transform"
    LOAD = "load"
    VALIDATE = "validate"
    NOTIFY = "notify"

class PipelineStep(BaseModel):
    id: str
    name: str
    type: StepType
    config: Dict[str, Any]
    dependencies: List[str] = []
    retry_count: int = 3
    timeout_seconds: int = 300

class Pipeline(BaseModel):
    id: Optional[str] = None
    name: str
    description: Optional[str] = None
    status: PipelineStatus = PipelineStatus.DRAFT
    steps: List[PipelineStep]
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    created_by: str
    tags: List[str] = []
    version: str = "1.0.0"
    
class PipelineRun(BaseModel):
    id: Optional[str] = None
    pipeline_id: str
    status: PipelineStatus
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    logs: List[str] = []
    metrics: Dict[str, Any] = {}

class PipelineCreateRequest(BaseModel):
    name: str
    description: Optional[str] = None
    steps: List[PipelineStep]
    tags: List[str] = []
    created_by: str

class PipelineUpdateRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    steps: Optional[List[PipelineStep]] = None
    status: Optional[PipelineStatus] = None
    tags: Optional[List[str]] = None