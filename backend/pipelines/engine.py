import asyncio
import logging
from typing import Dict, List, Any
from datetime import datetime
from dataclasses import dataclass

from models.pipeline import Pipeline, PipelineRun, PipelineStatus, StepType

logger = logging.getLogger(__name__)

@dataclass
class ValidationResult:
    is_valid: bool
    errors: List[str]
    warnings: List[str]

class PipelineEngine:
    def __init__(self):
        self.running_pipelines: Dict[str, asyncio.Task] = {}
        self.step_processors = {
            StepType.EXTRACT: self._process_extract_step,
            StepType.TRANSFORM: self._process_transform_step,
            StepType.LOAD: self._process_load_step,
            StepType.VALIDATE: self._process_validate_step,
            StepType.NOTIFY: self._process_notify_step,
        }
    
    async def execute_pipeline(self, pipeline: Pipeline, pipeline_run: PipelineRun):
        """Execute a pipeline with all its steps"""
        try:
            logger.info(f"Starting pipeline execution: {pipeline.name} (ID: {pipeline.id})")
            
            # Build dependency graph
            dependency_graph = self._build_dependency_graph(pipeline.steps)
            
            # Execute steps in dependency order
            completed_steps = set()
            step_results = {}
            
            while len(completed_steps) < len(pipeline.steps):
                # Find steps that can be executed (all dependencies completed)
                ready_steps = [
                    step for step in pipeline.steps 
                    if step.id not in completed_steps and 
                    all(dep in completed_steps for dep in step.dependencies)
                ]
                
                if not ready_steps:
                    raise Exception("Circular dependency detected or no steps ready to execute")
                
                # Execute ready steps in parallel
                tasks = []
                for step in ready_steps:
                    task = asyncio.create_task(self._execute_step(step, step_results))
                    tasks.append((step.id, task))
                
                # Wait for all tasks to complete
                for step_id, task in tasks:
                    try:
                        result = await task
                        step_results[step_id] = result
                        completed_steps.add(step_id)
                        pipeline_run.logs.append(f"Step {step_id} completed successfully")
                    except Exception as e:
                        pipeline_run.status = PipelineStatus.FAILED
                        pipeline_run.error_message = f"Step {step_id} failed: {str(e)}"
                        pipeline_run.completed_at = datetime.utcnow()
                        logger.error(f"Step {step_id} failed: {str(e)}")
                        return
            
            # Pipeline completed successfully
            pipeline_run.status = PipelineStatus.COMPLETED
            pipeline_run.completed_at = datetime.utcnow()
            pipeline_run.metrics = {
                "total_steps": len(pipeline.steps),
                "execution_time_seconds": (
                    pipeline_run.completed_at - pipeline_run.started_at
                ).total_seconds()
            }
            
            logger.info(f"Pipeline {pipeline.name} completed successfully")
            
        except Exception as e:
            pipeline_run.status = PipelineStatus.FAILED
            pipeline_run.error_message = str(e)
            pipeline_run.completed_at = datetime.utcnow()
            logger.error(f"Pipeline {pipeline.name} failed: {str(e)}")
    
    async def _execute_step(self, step, step_results: Dict[str, Any]):
        """Execute a single pipeline step"""
        logger.info(f"Executing step: {step.name} (Type: {step.type})")
        
        # Get processor for step type
        processor = self.step_processors.get(step.type)
        if not processor:
            raise Exception(f"No processor found for step type: {step.type}")
        
        # Execute step with retry logic
        for attempt in range(step.retry_count + 1):
            try:
                # Execute with timeout
                result = await asyncio.wait_for(
                    processor(step, step_results),
                    timeout=step.timeout_seconds
                )
                return result
            except asyncio.TimeoutError:
                if attempt == step.retry_count:
                    raise Exception(f"Step {step.name} timed out after {step.timeout_seconds} seconds")
                logger.warning(f"Step {step.name} timed out, retrying (attempt {attempt + 1})")
            except Exception as e:
                if attempt == step.retry_count:
                    raise e
                logger.warning(f"Step {step.name} failed, retrying (attempt {attempt + 1}): {str(e)}")
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
    
    async def _process_extract_step(self, step, step_results: Dict[str, Any]):
        """Process an extract step"""
        config = step.config
        source_type = config.get("source_type", "unknown")
        
        logger.info(f"Extracting data from {source_type}")
        
        # Simulate data extraction
        await asyncio.sleep(1)  # Simulate processing time
        
        extracted_data = {
            "source": source_type,
            "records_count": config.get("expected_records", 1000),
            "extraction_time": datetime.utcnow().isoformat()
        }
        
        return extracted_data
    
    async def _process_transform_step(self, step, step_results: Dict[str, Any]):
        """Process a transform step"""
        config = step.config
        transformation_type = config.get("transformation_type", "unknown")
        
        logger.info(f"Applying transformation: {transformation_type}")
        
        # Get input data from dependencies
        input_data = {}
        for dep_id in step.dependencies:
            if dep_id in step_results:
                input_data[dep_id] = step_results[dep_id]
        
        # Simulate data transformation
        await asyncio.sleep(2)  # Simulate processing time
        
        transformed_data = {
            "transformation": transformation_type,
            "input_records": sum(
                data.get("records_count", 0) for data in input_data.values() 
                if isinstance(data, dict)
            ),
            "output_records": config.get("output_records", 950),
            "transformation_time": datetime.utcnow().isoformat()
        }
        
        return transformed_data
    
    async def _process_load_step(self, step, step_results: Dict[str, Any]):
        """Process a load step"""
        config = step.config
        destination_type = config.get("destination_type", "unknown")
        
        logger.info(f"Loading data to {destination_type}")
        
        # Get input data from dependencies
        input_data = {}
        for dep_id in step.dependencies:
            if dep_id in step_results:
                input_data[dep_id] = step_results[dep_id]
        
        # Simulate data loading
        await asyncio.sleep(1.5)  # Simulate processing time
        
        loaded_data = {
            "destination": destination_type,
            "loaded_records": sum(
                data.get("output_records", data.get("records_count", 0)) 
                for data in input_data.values() 
                if isinstance(data, dict)
            ),
            "load_time": datetime.utcnow().isoformat()
        }
        
        return loaded_data
    
    async def _process_validate_step(self, step, step_results: Dict[str, Any]):
        """Process a validation step"""
        config = step.config
        validation_rules = config.get("validation_rules", [])
        
        logger.info(f"Running validation with {len(validation_rules)} rules")
        
        # Simulate validation
        await asyncio.sleep(0.5)  # Simulate processing time
        
        validation_result = {
            "validation_passed": True,
            "rules_checked": len(validation_rules),
            "validation_time": datetime.utcnow().isoformat()
        }
        
        return validation_result
    
    async def _process_notify_step(self, step, step_results: Dict[str, Any]):
        """Process a notification step"""
        config = step.config
        notification_type = config.get("notification_type", "email")
        
        logger.info(f"Sending {notification_type} notification")
        
        # Simulate notification sending
        await asyncio.sleep(0.3)  # Simulate processing time
        
        notification_result = {
            "notification_type": notification_type,
            "recipients": config.get("recipients", []),
            "sent_at": datetime.utcnow().isoformat()
        }
        
        return notification_result
    
    def _build_dependency_graph(self, steps):
        """Build a dependency graph from pipeline steps"""
        graph = {}
        for step in steps:
            graph[step.id] = step.dependencies
        return graph
    
    def validate_pipeline(self, pipeline: Pipeline) -> ValidationResult:
        """Validate pipeline configuration"""
        errors = []
        warnings = []
        
        # Check for duplicate step IDs
        step_ids = [step.id for step in pipeline.steps]
        if len(step_ids) != len(set(step_ids)):
            errors.append("Duplicate step IDs found")
        
        # Check for circular dependencies
        if self._has_circular_dependencies(pipeline.steps):
            errors.append("Circular dependencies detected")
        
        # Check for invalid dependencies
        valid_step_ids = set(step_ids)
        for step in pipeline.steps:
            for dep in step.dependencies:
                if dep not in valid_step_ids:
                    errors.append(f"Step {step.id} depends on non-existent step {dep}")
        
        # Check for empty pipelines
        if not pipeline.steps:
            warnings.append("Pipeline has no steps")
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )
    
    def _has_circular_dependencies(self, steps):
        """Check for circular dependencies in pipeline steps"""
        graph = {step.id: step.dependencies for step in steps}
        visited = set()
        rec_stack = set()
        
        def has_cycle(node):
            if node in rec_stack:
                return True
            if node in visited:
                return False
            
            visited.add(node)
            rec_stack.add(node)
            
            for neighbor in graph.get(node, []):
                if has_cycle(neighbor):
                    return True
            
            rec_stack.remove(node)
            return False
        
        for step_id in graph:
            if step_id not in visited:
                if has_cycle(step_id):
                    return True
        
        return False
    
    def cancel_pipeline(self, run_id: str):
        """Cancel a running pipeline"""
        if run_id in self.running_pipelines:
            task = self.running_pipelines[run_id]
            task.cancel()
            del self.running_pipelines[run_id]
            logger.info(f"Pipeline run {run_id} cancelled")