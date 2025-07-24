from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from datetime import datetime
import uvicorn

from api.pipelines import router as pipelines_router
from api.scheduler import router as scheduler_router
from api.monitoring import router as monitoring_router
from models.pipeline import Pipeline, PipelineStatus
from models.schedule import Schedule

app = FastAPI(
    title="CleanOps API",
    description="Data Pipeline Operations Platform API",
    version="1.0.0"
)

# CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(pipelines_router, prefix="/api/v1/pipelines", tags=["pipelines"])
app.include_router(scheduler_router, prefix="/api/v1/scheduler", tags=["scheduler"])
app.include_router(monitoring_router, prefix="/api/v1/monitoring", tags=["monitoring"])

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "CleanOps API",
        "version": "1.0.0",
        "docs": "/docs",
        "status": "operational"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {
            "api": "operational",
            "database": "operational",
            "scheduler": "operational"
        }
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)