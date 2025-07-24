from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import List, Optional
from datetime import datetime
import uuid

from models.pipeline import (
    Pipeline, PipelineRun, PipelineCreateRequest, 
    PipelineUpdateRequest, PipelineStatus
)
from pipelines.engine import PipelineEngine

router = APIRouter()
pipeline_engine = PipelineEngine()

# In-memory storage (replace with database in production)
pipelines_db = {}
pipeline_runs_db = {}

@router.get("/", response_model=List[Pipeline])
async def list_pipelines(
    status: Optional[PipelineStatus] = None,
    tags: Optional[str] = None,
    created_by: Optional[str] = None
):
    """List all pipelines with optional filtering"""
    pipelines = list(pipelines_db.values())
    
    if status:
        pipelines = [p for p in pipelines if p.status == status]
    if tags:
        tag_list = [t.strip() for t in tags.split(",")]
        pipelines = [p for p in pipelines if any(tag in p.tags for tag in tag_list)]
    if created_by:
        pipelines = [p for p in pipelines if p.created_by == created_by]
    
    return pipelines

@router.post("/", response_model=Pipeline)
async def create_pipeline(pipeline_request: PipelineCreateRequest):
    """Create a new pipeline"""
    pipeline_id = str(uuid.uuid4())
    pipeline = Pipeline(
        id=pipeline_id,
        name=pipeline_request.name,
        description=pipeline_request.description,
        steps=pipeline_request.steps,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
        created_by=pipeline_request.created_by,
        tags=pipeline_request.tags
    )
    
    pipelines_db[pipeline_id] = pipeline
    return pipeline

@router.get("/{pipeline_id}", response_model=Pipeline)
async def get_pipeline(pipeline_id: str):
    """Get a specific pipeline by ID"""
    if pipeline_id not in pipelines_db:
        raise HTTPException(status_code=404, detail="Pipeline not found")
    return pipelines_db[pipeline_id]

@router.put("/{pipeline_id}", response_model=Pipeline)
async def update_pipeline(pipeline_id: str, update_request: PipelineUpdateRequest):
    """Update an existing pipeline"""
    if pipeline_id not in pipelines_db:
        raise HTTPException(status_code=404, detail="Pipeline not found")
    
    pipeline = pipelines_db[pipeline_id]
    update_data = update_request.dict(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(pipeline, field, value)
    
    pipeline.updated_at = datetime.utcnow()
    pipelines_db[pipeline_id] = pipeline
    return pipeline

@router.delete("/{pipeline_id}")
async def delete_pipeline(pipeline_id: str):
    """Delete a pipeline"""
    if pipeline_id not in pipelines_db:
        raise HTTPException(status_code=404, detail="Pipeline not found")
    
    del pipelines_db[pipeline_id]
    return {"message": "Pipeline deleted successfully"}

@router.post("/{pipeline_id}/run", response_model=PipelineRun)
async def run_pipeline(pipeline_id: str, background_tasks: BackgroundTasks):
    """Execute a pipeline"""
    if pipeline_id not in pipelines_db:
        raise HTTPException(status_code=404, detail="Pipeline not found")
    
    pipeline = pipelines_db[pipeline_id]
    run_id = str(uuid.uuid4())
    
    pipeline_run = PipelineRun(
        id=run_id,
        pipeline_id=pipeline_id,
        status=PipelineStatus.RUNNING,
        started_at=datetime.utcnow()
    )
    
    pipeline_runs_db[run_id] = pipeline_run
    
    # Execute pipeline in background
    background_tasks.add_task(pipeline_engine.execute_pipeline, pipeline, pipeline_run)
    
    return pipeline_run

@router.get("/{pipeline_id}/runs", response_model=List[PipelineRun])
async def list_pipeline_runs(pipeline_id: str, limit: int = 10):
    """List runs for a specific pipeline"""
    if pipeline_id not in pipelines_db:
        raise HTTPException(status_code=404, detail="Pipeline not found")
    
    runs = [run for run in pipeline_runs_db.values() if run.pipeline_id == pipeline_id]
    runs.sort(key=lambda x: x.started_at or datetime.min, reverse=True)
    return runs[:limit]

@router.get("/{pipeline_id}/runs/{run_id}", response_model=PipelineRun)
async def get_pipeline_run(pipeline_id: str, run_id: str):
    """Get details of a specific pipeline run"""
    if run_id not in pipeline_runs_db:
        raise HTTPException(status_code=404, detail="Pipeline run not found")
    
    pipeline_run = pipeline_runs_db[run_id]
    if pipeline_run.pipeline_id != pipeline_id:
        raise HTTPException(status_code=404, detail="Pipeline run not found for this pipeline")
    
    return pipeline_run

@router.post("/{pipeline_id}/runs/{run_id}/cancel")
async def cancel_pipeline_run(pipeline_id: str, run_id: str):
    """Cancel a running pipeline"""
    if run_id not in pipeline_runs_db:
        raise HTTPException(status_code=404, detail="Pipeline run not found")
    
    pipeline_run = pipeline_runs_db[run_id]
    if pipeline_run.pipeline_id != pipeline_id:
        raise HTTPException(status_code=404, detail="Pipeline run not found for this pipeline")
    
    if pipeline_run.status == PipelineStatus.RUNNING:
        pipeline_run.status = PipelineStatus.CANCELLED
        pipeline_run.completed_at = datetime.utcnow()
        pipeline_runs_db[run_id] = pipeline_run
        
        # Signal pipeline engine to cancel execution
        pipeline_engine.cancel_pipeline(run_id)
    
    return {"message": "Pipeline run cancelled successfully"}

@router.get("/{pipeline_id}/validate")
async def validate_pipeline(pipeline_id: str):
    """Validate pipeline configuration"""
    if pipeline_id not in pipelines_db:
        raise HTTPException(status_code=404, detail="Pipeline not found")
    
    pipeline = pipelines_db[pipeline_id]
    validation_result = pipeline_engine.validate_pipeline(pipeline)
    
    return {
        "valid": validation_result.is_valid,
        "errors": validation_result.errors,
        "warnings": validation_result.warnings
    }