#!/usr/bin/env python3
"""Complex application with multiple design patterns."""

import asyncio
import logging
import threading
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Callable, Any
from enum import Enum
from contextlib import asynccontextmanager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TaskStatus(Enum):
    """Task status enumeration."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class Task:
    """Task data structure."""
    id: str
    name: str
    status: TaskStatus = TaskStatus.PENDING
    result: Optional[Any] = None
    error: Optional[str] = None
    dependencies: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        """Post-initialization processing."""
        if not self.id:
            raise ValueError("Task ID cannot be empty")

class Observable:
    """Observer pattern implementation."""
    
    def __init__(self):
        self._observers: List[Callable] = []
    
    def attach(self, observer: Callable):
        """Attach an observer."""
        if observer not in self._observers:
            self._observers.append(observer)
    
    def detach(self, observer: Callable):
        """Detach an observer."""
        if observer in self._observers:
            self._observers.remove(observer)
    
    def notify(self, *args, **kwargs):
        """Notify all observers."""
        for observer in self._observers:
            try:
                observer(*args, **kwargs)
            except Exception as e:
                logger.error(f"Observer error: {e}")

class TaskProcessor(ABC):
    """Abstract task processor."""
    
    @abstractmethod
    async def process(self, task: Task) -> Any:
        """Process a task."""
        pass

class SimpleTaskProcessor(TaskProcessor):
    """Simple task processor implementation."""
    
    def __init__(self, processing_delay: float = 1.0):
        self.processing_delay = processing_delay
    
    async def process(self, task: Task) -> Any:
        """Process a task with artificial delay."""
        logger.info(f"Processing task {task.id}: {task.name}")
        await asyncio.sleep(self.processing_delay)
        
        # Simulate processing logic
        if "fail" in task.name.lower():
            raise RuntimeError(f"Task {task.id} failed as requested")
        
        return f"Result for {task.name}"

class TaskScheduler(Observable):
    """Task scheduler with dependency management."""
    
    def __init__(self, max_concurrent_tasks: int = 3):
        super().__init__()
        self.max_concurrent_tasks = max_concurrent_tasks
        self.tasks: Dict[str, Task] = {}
        self.running_tasks: Dict[str, asyncio.Task] = {}
        self.processor: Optional[TaskProcessor] = None
        self._lock = threading.Lock()
    
    def set_processor(self, processor: TaskProcessor):
        """Set the task processor."""
        self.processor = processor
    
    def add_task(self, task: Task):
        """Add a task to the scheduler."""
        with self._lock:
            if task.id in self.tasks:
                raise ValueError(f"Task {task.id} already exists")
            self.tasks[task.id] = task
            self.notify("task_added", task)
    
    def get_task(self, task_id: str) -> Optional[Task]:
        """Get a task by ID."""
        return self.tasks.get(task_id)
    
    def _check_dependencies(self, task: Task) -> bool:
        """Check if all dependencies are completed."""
        for dep_id in task.dependencies:
            dep_task = self.tasks.get(dep_id)
            if not dep_task or dep_task.status != TaskStatus.COMPLETED:
                return False
        return True
    
    async def _execute_task(self, task: Task):
        """Execute a single task."""
        try:
            task.status = TaskStatus.RUNNING
            self.notify("task_started", task)
            
            if not self.processor:
                raise RuntimeError("No processor set")
            
            result = await self.processor.process(task)
            task.result = result
            task.status = TaskStatus.COMPLETED
            self.notify("task_completed", task)
            
        except Exception as e:
            task.error = str(e)
            task.status = TaskStatus.FAILED
            self.notify("task_failed", task)
            logger.error(f"Task {task.id} failed: {e}")
        
        finally:
            if task.id in self.running_tasks:
                del self.running_tasks[task.id]
    
    async def run(self):
        """Run the task scheduler."""
        logger.info("Starting task scheduler")
        
        while True:
            # Find tasks ready to run
            ready_tasks = [
                task for task in self.tasks.values()
                if (task.status == TaskStatus.PENDING and 
                    self._check_dependencies(task) and
                    task.id not in self.running_tasks)
            ]
            
            # Start new tasks if we have capacity
            available_slots = self.max_concurrent_tasks - len(self.running_tasks)
            for task in ready_tasks[:available_slots]:
                task_coroutine = asyncio.create_task(self._execute_task(task))
                self.running_tasks[task.id] = task_coroutine
            
            # Check if all tasks are done
            if not self.running_tasks and all(
                task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED]
                for task in self.tasks.values()
            ):
                break
            
            # Wait a bit before checking again
            await asyncio.sleep(0.1)
        
        logger.info("Task scheduler finished")

class TaskMonitor:
    """Task monitor with observer pattern."""
    
    def __init__(self):
        self.task_counts = {status: 0 for status in TaskStatus}
    
    def on_task_added(self, task: Task):
        """Handle task added event."""
        self.task_counts[TaskStatus.PENDING] += 1
        logger.info(f"Task added: {task.id}")
    
    def on_task_started(self, task: Task):
        """Handle task started event."""
        self.task_counts[TaskStatus.PENDING] -= 1
        self.task_counts[TaskStatus.RUNNING] += 1
        logger.info(f"Task started: {task.id}")
    
    def on_task_completed(self, task: Task):
        """Handle task completed event."""
        self.task_counts[TaskStatus.RUNNING] -= 1
        self.task_counts[TaskStatus.COMPLETED] += 1
        logger.info(f"Task completed: {task.id} -> {task.result}")
    
    def on_task_failed(self, task: Task):
        """Handle task failed event."""
        self.task_counts[TaskStatus.RUNNING] -= 1
        self.task_counts[TaskStatus.FAILED] += 1
        logger.error(f"Task failed: {task.id} -> {task.error}")
    
    def print_summary(self):
        """Print task summary."""
        logger.info("Task Summary:")
        for status, count in self.task_counts.items():
            logger.info(f"  {status.value}: {count}")

@asynccontextmanager
async def task_execution_context(scheduler: TaskScheduler):
    """Context manager for task execution."""
    logger.info("Entering task execution context")
    try:
        yield scheduler
    finally:
        logger.info("Exiting task execution context")

async def main():
    """Main application function."""
    # Create components
    scheduler = TaskScheduler(max_concurrent_tasks=2)
    processor = SimpleTaskProcessor(processing_delay=0.5)
    monitor = TaskMonitor()
    
    # Set up scheduler
    scheduler.set_processor(processor)
    
    # Attach monitor to scheduler events
    scheduler.attach(lambda event, task: getattr(monitor, f"on_{event}", lambda x: None)(task))
    
    # Create tasks with dependencies
    tasks = [
        Task("task1", "First task"),
        Task("task2", "Second task", dependencies=["task1"]),
        Task("task3", "Third task"),
        Task("task4", "Fourth task (will fail)", dependencies=["task2", "task3"]),
        Task("task5", "Fifth task", dependencies=["task1"]),
    ]
    
    # Add tasks to scheduler
    for task in tasks:
        scheduler.add_task(task)
    
    # Run scheduler
    async with task_execution_context(scheduler):
        await scheduler.run()
    
    # Print summary
    monitor.print_summary()
    
    # Print final task states
    logger.info("Final task states:")
    for task in tasks:
        logger.info(f"  {task.id}: {task.status.value} - {task.result or task.error}")

if __name__ == "__main__":
    asyncio.run(main())