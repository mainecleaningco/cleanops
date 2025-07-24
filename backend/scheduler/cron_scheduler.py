import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import re
from croniter import croniter

from models.schedule import Schedule, ScheduleStatus, ScheduleType

logger = logging.getLogger(__name__)

class CronScheduler:
    def __init__(self):
        self.schedules: Dict[str, Schedule] = {}
        self.running_tasks: Dict[str, asyncio.Task] = {}
        self.scheduler_task: Optional[asyncio.Task] = None
        self.is_running = False
        
    def start(self):
        """Start the scheduler"""
        if not self.is_running:
            self.is_running = True
            self.scheduler_task = asyncio.create_task(self._scheduler_loop())
            logger.info("Cron scheduler started")
    
    def stop(self):
        """Stop the scheduler"""
        self.is_running = False
        if self.scheduler_task:
            self.scheduler_task.cancel()
        
        # Cancel all running tasks
        for task in self.running_tasks.values():
            task.cancel()
        self.running_tasks.clear()
        
        logger.info("Cron scheduler stopped")
    
    def add_schedule(self, schedule: Schedule):
        """Add a schedule to the scheduler"""
        if schedule.status == ScheduleStatus.ACTIVE:
            self.schedules[schedule.id] = schedule
            logger.info(f"Added schedule: {schedule.name} (ID: {schedule.id})")
    
    def remove_schedule(self, schedule_id: str):
        """Remove a schedule from the scheduler"""
        if schedule_id in self.schedules:
            del self.schedules[schedule_id]
            
            # Cancel running task if exists
            if schedule_id in self.running_tasks:
                self.running_tasks[schedule_id].cancel()
                del self.running_tasks[schedule_id]
            
            logger.info(f"Removed schedule: {schedule_id}")
    
    def validate_cron_expression(self, cron_expression: str) -> bool:
        """Validate a cron expression"""
        try:
            croniter(cron_expression)
            return True
        except Exception:
            return False
    
    def get_next_run_time(self, schedule: Schedule) -> Optional[datetime]:
        """Get the next run time for a schedule"""
        now = datetime.utcnow()
        
        if schedule.type == ScheduleType.CRON and schedule.cron_expression:
            try:
                cron = croniter(schedule.cron_expression, now)
                next_run = cron.get_next(datetime)
                
                # Check if within time bounds
                if schedule.end_time and next_run > schedule.end_time:
                    return None
                if schedule.start_time and next_run < schedule.start_time:
                    # Find next run after start time
                    cron = croniter(schedule.cron_expression, schedule.start_time)
                    next_run = cron.get_next(datetime)
                
                return next_run
            except Exception as e:
                logger.error(f"Error calculating next run time for schedule {schedule.id}: {e}")
                return None
        
        elif schedule.type == ScheduleType.INTERVAL and schedule.interval_seconds:
            next_run = now + timedelta(seconds=schedule.interval_seconds)
            
            # Check if within time bounds
            if schedule.end_time and next_run > schedule.end_time:
                return None
            if schedule.start_time and next_run < schedule.start_time:
                return schedule.start_time
            
            return next_run
        
        elif schedule.type == ScheduleType.ONE_TIME and schedule.start_time:
            if schedule.start_time > now:
                return schedule.start_time
        
        return None
    
    async def _scheduler_loop(self):
        """Main scheduler loop"""
        while self.is_running:
            try:
                await self._process_schedules()
                await asyncio.sleep(30)  # Check every 30 seconds
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in scheduler loop: {e}")
                await asyncio.sleep(60)  # Wait longer on error
    
    async def _process_schedules(self):
        """Process all active schedules"""
        now = datetime.utcnow()
        
        for schedule_id, schedule in list(self.schedules.items()):
            try:
                # Check if schedule should run
                if self._should_run_now(schedule, now):
                    # Check dependencies
                    if self._dependencies_met(schedule):
                        # Check resource availability
                        if self._resources_available(schedule):
                            # Check concurrent run limit
                            if self._can_run_concurrent(schedule):
                                await self._trigger_schedule(schedule)
                            else:
                                logger.info(f"Schedule {schedule.name} skipped due to concurrent run limit")
                        else:
                            logger.info(f"Schedule {schedule.name} skipped due to resource constraints")
                    else:
                        logger.info(f"Schedule {schedule.name} skipped due to unmet dependencies")
            except Exception as e:
                logger.error(f"Error processing schedule {schedule_id}: {e}")
    
    def _should_run_now(self, schedule: Schedule, now: datetime) -> bool:
        """Check if a schedule should run now"""
        next_run_time = self.get_next_run_time(schedule)
        if not next_run_time:
            return False
        
        # Allow 1 minute window for execution
        return abs((next_run_time - now).total_seconds()) <= 60
    
    def _dependencies_met(self, schedule: Schedule) -> bool:
        """Check if all schedule dependencies are met"""
        for dep_id in schedule.dependencies:
            if dep_id not in self.schedules:
                continue
            
            dep_schedule = self.schedules[dep_id]
            # For now, just check if dependency is not currently running
            # In a real implementation, you'd check the last successful run
            if dep_id in self.running_tasks:
                return False
        
        return True
    
    def _resources_available(self, schedule: Schedule) -> bool:
        """Check if required resources are available"""
        # Simple resource check - in production, integrate with resource manager
        requirements = schedule.resource_requirements
        
        # For demo purposes, assume resources are always available
        # In reality, you'd check CPU, memory, GPU availability
        return True
    
    def _can_run_concurrent(self, schedule: Schedule) -> bool:
        """Check if schedule can run based on concurrent run limits"""
        current_runs = sum(
            1 for task_id, task in self.running_tasks.items()
            if task_id.startswith(schedule.id) and not task.done()
        )
        
        return current_runs < schedule.max_concurrent_runs
    
    async def _trigger_schedule(self, schedule: Schedule):
        """Trigger a schedule to run"""
        task_id = f"{schedule.id}_{datetime.utcnow().isoformat()}"
        
        logger.info(f"Triggering schedule: {schedule.name} (ID: {schedule.id})")
        
        # Create and start task
        task = asyncio.create_task(self._execute_scheduled_pipeline(schedule))
        self.running_tasks[task_id] = task
        
        # Clean up completed tasks
        self._cleanup_completed_tasks()
    
    async def _execute_scheduled_pipeline(self, schedule: Schedule):
        """Execute a pipeline for a scheduled run"""
        try:
            # This would integrate with the pipeline API to actually run the pipeline
            logger.info(f"Executing pipeline {schedule.pipeline_id} for schedule {schedule.id}")
            
            # Simulate pipeline execution
            await asyncio.sleep(10)  # Simulate work
            
            logger.info(f"Completed pipeline execution for schedule {schedule.id}")
            
            # If this was a one-time schedule, mark it as completed
            if schedule.type == ScheduleType.ONE_TIME:
                schedule.status = ScheduleStatus.COMPLETED
                self.remove_schedule(schedule.id)
                
        except Exception as e:
            logger.error(f"Error executing pipeline for schedule {schedule.id}: {e}")
    
    def _cleanup_completed_tasks(self):
        """Clean up completed tasks"""
        completed_tasks = [
            task_id for task_id, task in self.running_tasks.items()
            if task.done()
        ]
        
        for task_id in completed_tasks:
            del self.running_tasks[task_id]
    
    def get_scheduler_status(self) -> Dict:
        """Get current scheduler status"""
        return {
            "is_running": self.is_running,
            "active_schedules": len(self.schedules),
            "running_tasks": len([t for t in self.running_tasks.values() if not t.done()]),
            "completed_tasks": len([t for t in self.running_tasks.values() if t.done()]),
            "schedules": [
                {
                    "id": s.id,
                    "name": s.name,
                    "type": s.type,
                    "status": s.status,
                    "next_run": self.get_next_run_time(s).isoformat() if self.get_next_run_time(s) else None
                }
                for s in self.schedules.values()
            ]
        }