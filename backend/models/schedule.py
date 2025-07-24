from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum

class ScheduleType(str, Enum):
    CRON = "cron"
    INTERVAL = "interval"
    ONE_TIME = "one_time"
    EVENT_DRIVEN = "event_driven"

class ScheduleStatus(str, Enum):
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"

class ResourceRequirement(BaseModel):
    cpu_cores: float = 1.0
    memory_mb: int = 512
    disk_gb: float = 1.0
    gpu_count: int = 0

class Schedule(BaseModel):
    id: Optional[str] = None
    name: str
    pipeline_id: str
    type: ScheduleType
    cron_expression: Optional[str] = None  # For CRON type
    interval_seconds: Optional[int] = None  # For INTERVAL type
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    status: ScheduleStatus = ScheduleStatus.ACTIVE
    dependencies: List[str] = []  # Other schedule IDs this depends on
    resource_requirements: ResourceRequirement = ResourceRequirement()
    max_concurrent_runs: int = 1
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    created_by: str
    tags: List[str] = []
    
class ScheduleRun(BaseModel):
    id: Optional[str] = None
    schedule_id: str
    pipeline_run_id: str
    scheduled_time: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    status: ScheduleStatus
    error_message: Optional[str] = None

class ScheduleCreateRequest(BaseModel):
    name: str
    pipeline_id: str
    type: ScheduleType
    cron_expression: Optional[str] = None
    interval_seconds: Optional[int] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    dependencies: List[str] = []
    resource_requirements: ResourceRequirement = ResourceRequirement()
    max_concurrent_runs: int = 1
    created_by: str
    tags: List[str] = []

class ScheduleUpdateRequest(BaseModel):
    name: Optional[str] = None
    cron_expression: Optional[str] = None
    interval_seconds: Optional[int] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    status: Optional[ScheduleStatus] = None
    dependencies: Optional[List[str]] = None
    resource_requirements: Optional[ResourceRequirement] = None
    max_concurrent_runs: Optional[int] = None
    tags: Optional[List[str]] = None