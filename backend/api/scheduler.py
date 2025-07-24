from fastapi import APIRouter, HTTPException
from typing import List, Optional
from datetime import datetime
import uuid

from models.schedule import (
    Schedule, ScheduleRun, ScheduleCreateRequest, 
    ScheduleUpdateRequest, ScheduleStatus, ScheduleType
)
from scheduler.cron_scheduler import CronScheduler

router = APIRouter()
cron_scheduler = CronScheduler()

# In-memory storage (replace with database in production)
schedules_db = {}
schedule_runs_db = {}

@router.get("/", response_model=List[Schedule])
async def list_schedules(
    status: Optional[ScheduleStatus] = None,
    pipeline_id: Optional[str] = None,
    type: Optional[ScheduleType] = None
):
    """List all schedules with optional filtering"""
    schedules = list(schedules_db.values())
    
    if status:
        schedules = [s for s in schedules if s.status == status]
    if pipeline_id:
        schedules = [s for s in schedules if s.pipeline_id == pipeline_id]
    if type:
        schedules = [s for s in schedules if s.type == type]
    
    return schedules

@router.post("/", response_model=Schedule)
async def create_schedule(schedule_request: ScheduleCreateRequest):
    """Create a new schedule"""
    schedule_id = str(uuid.uuid4())
    
    # Validate cron expression if provided
    if schedule_request.type == ScheduleType.CRON and schedule_request.cron_expression:
        if not cron_scheduler.validate_cron_expression(schedule_request.cron_expression):
            raise HTTPException(status_code=400, detail="Invalid cron expression")
    
    schedule = Schedule(
        id=schedule_id,
        name=schedule_request.name,
        pipeline_id=schedule_request.pipeline_id,
        type=schedule_request.type,
        cron_expression=schedule_request.cron_expression,
        interval_seconds=schedule_request.interval_seconds,
        start_time=schedule_request.start_time,
        end_time=schedule_request.end_time,
        dependencies=schedule_request.dependencies,
        resource_requirements=schedule_request.resource_requirements,
        max_concurrent_runs=schedule_request.max_concurrent_runs,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        created_by=schedule_request.created_by,
        tags=schedule_request.tags
    )
    
    schedules_db[schedule_id] = schedule
    
    # Register with scheduler if active
    if schedule.status == ScheduleStatus.ACTIVE:
        cron_scheduler.add_schedule(schedule)
    
    return schedule

@router.get("/{schedule_id}", response_model=Schedule)
async def get_schedule(schedule_id: str):
    """Get a specific schedule by ID"""
    if schedule_id not in schedules_db:
        raise HTTPException(status_code=404, detail="Schedule not found")
    return schedules_db[schedule_id]

@router.put("/{schedule_id}", response_model=Schedule)
async def update_schedule(schedule_id: str, update_request: ScheduleUpdateRequest):
    """Update an existing schedule"""
    if schedule_id not in schedules_db:
        raise HTTPException(status_code=404, detail="Schedule not found")
    
    schedule = schedules_db[schedule_id]
    update_data = update_request.dict(exclude_unset=True)
    
    # Validate cron expression if being updated
    if "cron_expression" in update_data and update_data["cron_expression"]:
        if not cron_scheduler.validate_cron_expression(update_data["cron_expression"]):
            raise HTTPException(status_code=400, detail="Invalid cron expression")
    
    # Remove from scheduler if status changing from active
    if schedule.status == ScheduleStatus.ACTIVE and update_data.get("status") != ScheduleStatus.ACTIVE:
        cron_scheduler.remove_schedule(schedule_id)
    
    # Update schedule
    for field, value in update_data.items():
        setattr(schedule, field, value)
    
    schedule.updated_at = datetime.utcnow()
    schedules_db[schedule_id] = schedule
    
    # Add to scheduler if status changed to active
    if schedule.status == ScheduleStatus.ACTIVE:
        cron_scheduler.add_schedule(schedule)
    
    return schedule

@router.delete("/{schedule_id}")
async def delete_schedule(schedule_id: str):
    """Delete a schedule"""
    if schedule_id not in schedules_db:
        raise HTTPException(status_code=404, detail="Schedule not found")
    
    # Remove from scheduler
    cron_scheduler.remove_schedule(schedule_id)
    
    del schedules_db[schedule_id]
    return {"message": "Schedule deleted successfully"}

@router.post("/{schedule_id}/pause")
async def pause_schedule(schedule_id: str):
    """Pause a schedule"""
    if schedule_id not in schedules_db:
        raise HTTPException(status_code=404, detail="Schedule not found")
    
    schedule = schedules_db[schedule_id]
    schedule.status = ScheduleStatus.PAUSED
    schedule.updated_at = datetime.utcnow()
    
    # Remove from scheduler
    cron_scheduler.remove_schedule(schedule_id)
    
    return {"message": "Schedule paused successfully"}

@router.post("/{schedule_id}/resume")
async def resume_schedule(schedule_id: str):
    """Resume a paused schedule"""
    if schedule_id not in schedules_db:
        raise HTTPException(status_code=404, detail="Schedule not found")
    
    schedule = schedules_db[schedule_id]
    schedule.status = ScheduleStatus.ACTIVE
    schedule.updated_at = datetime.utcnow()
    
    # Add back to scheduler
    cron_scheduler.add_schedule(schedule)
    
    return {"message": "Schedule resumed successfully"}

@router.get("/{schedule_id}/runs", response_model=List[ScheduleRun])
async def list_schedule_runs(schedule_id: str, limit: int = 10):
    """List runs for a specific schedule"""
    if schedule_id not in schedules_db:
        raise HTTPException(status_code=404, detail="Schedule not found")
    
    runs = [run for run in schedule_runs_db.values() if run.schedule_id == schedule_id]
    runs.sort(key=lambda x: x.scheduled_time, reverse=True)
    return runs[:limit]

@router.get("/{schedule_id}/next-run")
async def get_next_run_time(schedule_id: str):
    """Get the next scheduled run time for a schedule"""
    if schedule_id not in schedules_db:
        raise HTTPException(status_code=404, detail="Schedule not found")
    
    schedule = schedules_db[schedule_id]
    next_run_time = cron_scheduler.get_next_run_time(schedule)
    
    return {
        "schedule_id": schedule_id,
        "next_run_time": next_run_time.isoformat() if next_run_time else None,
        "status": schedule.status
    }

@router.post("/{schedule_id}/trigger")
async def trigger_schedule_now(schedule_id: str):
    """Manually trigger a schedule to run immediately"""
    if schedule_id not in schedules_db:
        raise HTTPException(status_code=404, detail="Schedule not found")
    
    schedule = schedules_db[schedule_id]
    run_id = str(uuid.uuid4())
    
    schedule_run = ScheduleRun(
        id=run_id,
        schedule_id=schedule_id,
        pipeline_run_id="",  # Will be set when pipeline starts
        scheduled_time=datetime.utcnow(),
        status=ScheduleStatus.ACTIVE
    )
    
    schedule_runs_db[run_id] = schedule_run
    
    # Trigger pipeline execution
    # This would integrate with the pipeline API
    
    return {"message": "Schedule triggered successfully", "run_id": run_id}

@router.get("/stats")
async def get_scheduler_stats():
    """Get scheduler statistics"""
    total_schedules = len(schedules_db)
    active_schedules = len([s for s in schedules_db.values() if s.status == ScheduleStatus.ACTIVE])
    paused_schedules = len([s for s in schedules_db.values() if s.status == ScheduleStatus.PAUSED])
    
    # Get recent runs
    recent_runs = sorted(
        schedule_runs_db.values(), 
        key=lambda x: x.scheduled_time, 
        reverse=True
    )[:10]
    
    return {
        "total_schedules": total_schedules,
        "active_schedules": active_schedules,
        "paused_schedules": paused_schedules,
        "recent_runs": len(schedule_runs_db),
        "scheduler_status": "running",
        "recent_run_details": [
            {
                "id": run.id,
                "schedule_id": run.schedule_id,
                "scheduled_time": run.scheduled_time.isoformat(),
                "status": run.status
            }
            for run in recent_runs
        ]
    }