from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from enum import Enum

router = APIRouter()

class MetricType(str, Enum):
    PIPELINE_RUNS = "pipeline_runs"
    SUCCESS_RATE = "success_rate"
    EXECUTION_TIME = "execution_time"
    RESOURCE_USAGE = "resource_usage"
    ERROR_COUNT = "error_count"

class AlertSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

# Mock data for demonstration
mock_metrics = {
    "pipeline_runs": [
        {"timestamp": "2024-01-15T10:00:00Z", "value": 15, "pipeline_id": "pipeline_1"},
        {"timestamp": "2024-01-15T11:00:00Z", "value": 12, "pipeline_id": "pipeline_1"},
        {"timestamp": "2024-01-15T12:00:00Z", "value": 18, "pipeline_id": "pipeline_2"},
    ],
    "success_rate": [
        {"timestamp": "2024-01-15T10:00:00Z", "value": 95.5, "pipeline_id": "pipeline_1"},
        {"timestamp": "2024-01-15T11:00:00Z", "value": 92.3, "pipeline_id": "pipeline_1"},
        {"timestamp": "2024-01-15T12:00:00Z", "value": 98.1, "pipeline_id": "pipeline_2"},
    ]
}

mock_alerts = [
    {
        "id": "alert_1",
        "title": "High Error Rate",
        "description": "Pipeline 'Customer ETL' has error rate above 5%",
        "severity": AlertSeverity.HIGH,
        "pipeline_id": "pipeline_1",
        "created_at": "2024-01-15T14:30:00Z",
        "resolved": False
    },
    {
        "id": "alert_2",
        "title": "Long Execution Time",
        "description": "Pipeline 'Data Validation' took 45 minutes to complete",
        "severity": AlertSeverity.MEDIUM,
        "pipeline_id": "pipeline_2",
        "created_at": "2024-01-15T13:15:00Z",
        "resolved": True
    }
]

@router.get("/metrics")
async def get_metrics(
    metric_type: MetricType,
    pipeline_id: Optional[str] = None,
    start_time: Optional[datetime] = Query(None, description="Start time for metrics (ISO format)"),
    end_time: Optional[datetime] = Query(None, description="End time for metrics (ISO format)"),
    aggregation: Optional[str] = Query("hour", description="Aggregation level: minute, hour, day")
):
    """Get metrics data for monitoring dashboards"""
    
    # Default time range to last 24 hours if not specified
    if not end_time:
        end_time = datetime.utcnow()
    if not start_time:
        start_time = end_time - timedelta(hours=24)
    
    # Filter mock data based on parameters
    metrics_data = mock_metrics.get(metric_type.value, [])
    
    if pipeline_id:
        metrics_data = [m for m in metrics_data if m.get("pipeline_id") == pipeline_id]
    
    return {
        "metric_type": metric_type,
        "pipeline_id": pipeline_id,
        "start_time": start_time.isoformat(),
        "end_time": end_time.isoformat(),
        "aggregation": aggregation,
        "data": metrics_data
    }

@router.get("/system-health")
async def get_system_health():
    """Get overall system health status"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "components": {
            "api_server": {
                "status": "healthy",
                "response_time_ms": 45,
                "uptime_hours": 168.5
            },
            "database": {
                "status": "healthy",
                "connection_pool": "8/20",
                "query_time_ms": 12
            },
            "scheduler": {
                "status": "healthy",
                "active_schedules": 15,
                "pending_tasks": 3
            },
            "pipeline_engine": {
                "status": "healthy",
                "running_pipelines": 2,
                "queue_size": 5
            }
        },
        "resource_usage": {
            "cpu_percent": 45.2,
            "memory_percent": 62.8,
            "disk_percent": 34.1,
            "network_io": {
                "bytes_sent": 1024000,
                "bytes_received": 2048000
            }
        }
    }

@router.get("/alerts")
async def get_alerts(
    severity: Optional[AlertSeverity] = None,
    pipeline_id: Optional[str] = None,
    resolved: Optional[bool] = None,
    limit: int = Query(50, le=100)
):
    """Get system alerts with filtering options"""
    
    alerts = mock_alerts.copy()
    
    # Apply filters
    if severity:
        alerts = [a for a in alerts if a["severity"] == severity]
    if pipeline_id:
        alerts = [a for a in alerts if a.get("pipeline_id") == pipeline_id]
    if resolved is not None:
        alerts = [a for a in alerts if a["resolved"] == resolved]
    
    # Sort by created_at descending
    alerts.sort(key=lambda x: x["created_at"], reverse=True)
    
    return {
        "alerts": alerts[:limit],
        "total_count": len(alerts),
        "unresolved_count": len([a for a in alerts if not a["resolved"]])
    }

@router.post("/alerts/{alert_id}/resolve")
async def resolve_alert(alert_id: str):
    """Mark an alert as resolved"""
    
    # Find and update alert
    for alert in mock_alerts:
        if alert["id"] == alert_id:
            alert["resolved"] = True
            alert["resolved_at"] = datetime.utcnow().isoformat()
            return {"message": "Alert resolved successfully", "alert": alert}
    
    raise HTTPException(status_code=404, detail="Alert not found")

@router.get("/logs")
async def get_logs(
    pipeline_id: Optional[str] = None,
    run_id: Optional[str] = None,
    level: Optional[str] = Query(None, description="Log level: DEBUG, INFO, WARNING, ERROR, CRITICAL"),
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    limit: int = Query(100, le=1000)
):
    """Get system and pipeline logs"""
    
    # Mock log data
    mock_logs = [
        {
            "timestamp": "2024-01-15T14:30:15Z",
            "level": "INFO",
            "message": "Pipeline 'Customer ETL' started successfully",
            "pipeline_id": "pipeline_1",
            "run_id": "run_123",
            "component": "pipeline_engine"
        },
        {
            "timestamp": "2024-01-15T14:30:45Z",
            "level": "WARNING",
            "message": "Step 'data_validation' took longer than expected",
            "pipeline_id": "pipeline_1",
            "run_id": "run_123",
            "component": "pipeline_engine"
        },
        {
            "timestamp": "2024-01-15T14:31:20Z",
            "level": "ERROR",
            "message": "Failed to connect to external API",
            "pipeline_id": "pipeline_1",
            "run_id": "run_123",
            "component": "extract_step"
        }
    ]
    
    logs = mock_logs.copy()
    
    # Apply filters
    if pipeline_id:
        logs = [log for log in logs if log.get("pipeline_id") == pipeline_id]
    if run_id:
        logs = [log for log in logs if log.get("run_id") == run_id]
    if level:
        logs = [log for log in logs if log["level"] == level.upper()]
    
    # Sort by timestamp descending
    logs.sort(key=lambda x: x["timestamp"], reverse=True)
    
    return {
        "logs": logs[:limit],
        "total_count": len(logs),
        "filters": {
            "pipeline_id": pipeline_id,
            "run_id": run_id,
            "level": level,
            "start_time": start_time.isoformat() if start_time else None,
            "end_time": end_time.isoformat() if end_time else None
        }
    }

@router.get("/dashboard")
async def get_dashboard_data():
    """Get comprehensive dashboard data"""
    
    now = datetime.utcnow()
    
    return {
        "timestamp": now.isoformat(),
        "summary": {
            "total_pipelines": 25,
            "active_pipelines": 18,
            "running_pipelines": 3,
            "failed_pipelines_24h": 2,
            "success_rate_24h": 94.2,
            "avg_execution_time_minutes": 15.3
        },
        "recent_runs": [
            {
                "id": "run_456",
                "pipeline_name": "Customer Data ETL",
                "status": "completed",
                "duration_minutes": 12.5,
                "started_at": (now - timedelta(minutes=20)).isoformat()
            },
            {
                "id": "run_457",
                "pipeline_name": "Log Aggregation",
                "status": "running",
                "duration_minutes": 8.2,
                "started_at": (now - timedelta(minutes=8)).isoformat()
            },
            {
                "id": "run_458",
                "pipeline_name": "Data Validation",
                "status": "failed",
                "duration_minutes": 5.1,
                "started_at": (now - timedelta(minutes=35)).isoformat()
            }
        ],
        "alerts_summary": {
            "critical": 0,
            "high": 1,
            "medium": 2,
            "low": 0
        },
        "resource_usage": {
            "cpu_percent": 45.2,
            "memory_percent": 62.8,
            "disk_percent": 34.1
        },
        "upcoming_schedules": [
            {
                "schedule_name": "Daily Customer Sync",
                "pipeline_name": "Customer ETL",
                "next_run": (now + timedelta(hours=2)).isoformat()
            },
            {
                "schedule_name": "Hourly Log Processing",
                "pipeline_name": "Log Aggregation",
                "next_run": (now + timedelta(minutes=45)).isoformat()
            }
        ]
    }

@router.get("/performance")
async def get_performance_metrics(
    pipeline_id: Optional[str] = None,
    days: int = Query(7, description="Number of days to analyze")
):
    """Get performance analysis and trends"""
    
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(days=days)
    
    return {
        "analysis_period": {
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "days": days
        },
        "pipeline_id": pipeline_id,
        "metrics": {
            "total_runs": 156,
            "successful_runs": 147,
            "failed_runs": 9,
            "success_rate": 94.2,
            "avg_execution_time_minutes": 15.3,
            "min_execution_time_minutes": 3.2,
            "max_execution_time_minutes": 45.8,
            "median_execution_time_minutes": 12.1
        },
        "trends": {
            "success_rate_trend": "stable",
            "execution_time_trend": "improving",
            "error_rate_trend": "stable"
        },
        "recommendations": [
            "Consider optimizing data transformation step for better performance",
            "Monitor error patterns in external API connections",
            "Review resource allocation for peak hours"
        ]
    }