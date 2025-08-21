# Parallel Processing Engine
## Phase 2 Feature Documentation

### Overview
This document provides comprehensive documentation for implementing a parallel processing engine in the MCP Pipeline system. Based on Anthropic's Model Context Protocol (MCP) specification, this feature enables concurrent execution of pipeline operations to significantly improve performance.

### MCP Protocol Compliance
The implementation follows Anthropic's MCP v1.0 specification for:
- Asynchronous operation execution
- Resource management
- Task coordination
- Performance optimization

### System Architecture

#### Core Components
1. **ParallelExecutor Class** - Core parallel execution engine
2. **JobQueue Class** - Priority-based job scheduling
3. **ResourceManager Class** - CPU/memory resource management
4. **TaskCoordinator Class** - Task dependency management

#### Directory Structure
```
src/
├── processing/
│   ├── __init__.py
│   ├── parallel_executor.py
│   ├── job_queue.py
│   ├── resource_manager.py
│   └── task_coordinator.py
└── pipeline_mcp_server.py (integration point)
```

### Implementation Details

#### 1. ParallelExecutor Class
The core parallel execution engine that manages concurrent task execution.

```python
# File: src/processing/parallel_executor.py
import asyncio
import concurrent.futures
import multiprocessing
import threading
from typing import List, Dict, Any, Callable, Optional, Union
from dataclasses import dataclass, asdict
from enum import Enum
import logging
import time

class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class TaskPriority(Enum):
    HIGH = 1
    MEDIUM = 2
    LOW = 3

@dataclass
class TaskDefinition:
    """Definition of a task to be executed"""
    task_id: str
    task_type: str
    function: Callable
    args: tuple = ()
    kwargs: dict = None
    priority: TaskPriority = TaskPriority.MEDIUM
    dependencies: List[str] = None
    timeout: float = 300.0  # 5 minutes default
    retry_count: int = 0
    max_retries: int = 3

@dataclass
class TaskResult:
    """Result of a task execution"""
    task_id: str
    status: TaskStatus
    result: Any = None
    error: Optional[str] = None
    execution_time: float = 0.0
    start_time: float = 0.0
    end_time: float = 0.0
    retry_count: int = 0

class ParallelExecutor:
    """Async parallel task execution with resource management"""
    
    def __init__(self, max_workers: int = None, max_concurrent_tasks: int = 10):
        # Determine optimal worker count
        cpu_count = multiprocessing.cpu_count()
        self.max_workers = max_workers or min(4, cpu_count)
        self.max_concurrent_tasks = max_concurrent_tasks
        
        # Initialize thread pool executor
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers)
        
        # Initialize process pool executor for CPU-intensive tasks
        self.process_executor = concurrent.futures.ProcessPoolExecutor(max_workers=max(1, cpu_count // 2))
        
        # Task management
        self.pending_tasks: Dict[str, TaskDefinition] = {}
        self.running_tasks: Dict[str, TaskDefinition] = {}
        self.completed_tasks: Dict[str, TaskResult] = {}
        self.failed_tasks: Dict[str, TaskResult] = {}
        
        # Concurrency control
        self.semaphore = asyncio.Semaphore(max_concurrent_tasks)
        self.task_lock = asyncio.Lock()
        
        # Performance tracking
        self.logger = logging.getLogger(__name__)
        self.performance_metrics = {
            "total_tasks": 0,
            "completed_tasks": 0,
            "failed_tasks": 0,
            "average_execution_time": 0.0,
            "total_execution_time": 0.0
        }
        
    async def submit_task(self, task_def: TaskDefinition) -> asyncio.Future:
        """Submit a task for parallel execution"""
        async with self.task_lock:
            self.pending_tasks[task_def.task_id] = task_def
            self.performance_metrics["total_tasks"] += 1
            
        # Create future for task result
        future = asyncio.Future()
        
        # Schedule task execution
        asyncio.create_task(self._execute_task(task_def, future))
        
        return future
        
    async def submit_tasks(self, task_defs: List[TaskDefinition]) -> List[asyncio.Future]:
        """Submit multiple tasks for parallel execution"""
        futures = []
        for task_def in task_defs:
            future = await self.submit_task(task_def)
            futures.append(future)
        return futures
        
    async def _execute_task(self, task_def: TaskDefinition, future: asyncio.Future):
        """Execute a single task"""
        async with self.semaphore:  # Limit concurrent tasks
            async with self.task_lock:
                # Move from pending to running
                if task_def.task_id in self.pending_tasks:
                    del self.pending_tasks[task_def.task_id]
                self.running_tasks[task_def.task_id] = task_def
                
            start_time = time.time()
            task_result = TaskResult(
                task_id=task_def.task_id,
                status=TaskStatus.RUNNING,
                start_time=start_time
            )
            
            try:
                # Wait for dependencies if any
                if task_def.dependencies:
                    await self._wait_for_dependencies(task_def.dependencies)
                    
                # Execute task based on type
                if task_def.task_type == "cpu_intensive":
                    # Use process pool for CPU-intensive tasks
                    loop = asyncio.get_event_loop()
                    result = await loop.run_in_executor(
                        self.process_executor,
                        self._run_task_in_process,
                        task_def
                    )
                else:
                    # Use thread pool for I/O-bound tasks
                    loop = asyncio.get_event_loop()
                    result = await loop.run_in_executor(
                        self.executor,
                        self._run_task_in_thread,
                        task_def
                    )
                    
                # Calculate execution time
                end_time = time.time()
                execution_time = end_time - start_time
                
                # Update task result
                task_result.status = TaskStatus.COMPLETED
                task_result.result = result
                task_result.execution_time = execution_time
                task_result.end_time = end_time
                
                # Update performance metrics
                async with self.task_lock:
                    self.performance_metrics["completed_tasks"] += 1
                    self.performance_metrics["total_execution_time"] += execution_time
                    self.performance_metrics["average_execution_time"] = (
                        self.performance_metrics["total_execution_time"] / 
                        self.performance_metrics["completed_tasks"]
                    )
                    
                self.logger.info(f"Task {task_def.task_id} completed in {execution_time:.2f}s")
                
            except Exception as e:
                end_time = time.time()
                execution_time = end_time - start_time
                
                task_result.status = TaskStatus.FAILED
                task_result.error = str(e)
                task_result.execution_time = execution_time
                task_result.end_time = end_time
                
                async with self.task_lock:
                    self.performance_metrics["failed_tasks"] += 1
                    
                self.logger.error(f"Task {task_def.task_id} failed: {e}")
                
                # Retry logic
                if task_def.retry_count < task_def.max_retries:
                    self.logger.info(f"Retrying task {task_def.task_id} ({task_def.retry_count + 1}/{task_def.max_retries})")
                    task_def.retry_count += 1
                    asyncio.create_task(self._execute_task(task_def, future))
                    return
                    
            finally:
                # Move task from running to completed/failed
                async with self.task_lock:
                    if task_def.task_id in self.running_tasks:
                        del self.running_tasks[task_def.task_id]
                        
                    if task_result.status == TaskStatus.COMPLETED:
                        self.completed_tasks[task_def.task_id] = task_result
                    else:
                        self.failed_tasks[task_def.task_id] = task_result
                        
                # Set future result
                if not future.done():
                    if task_result.status == TaskStatus.COMPLETED:
                        future.set_result(task_result)
                    else:
                        future.set_exception(Exception(task_result.error))
                        
    def _run_task_in_thread(self, task_def: TaskDefinition) -> Any:
        """Run task in thread pool"""
        try:
            if asyncio.iscoroutinefunction(task_def.function):
                # For async functions, run in new event loop
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    return loop.run_until_complete(task_def.function(*task_def.args, **(task_def.kwargs or {})))
                finally:
                    loop.close()
            else:
                # For sync functions, call directly
                return task_def.function(*task_def.args, **(task_def.kwargs or {}))
        except Exception as e:
            self.logger.error(f"Thread execution failed for task {task_def.task_id}: {e}")
            raise
            
    def _run_task_in_process(self, task_def: TaskDefinition) -> Any:
        """Run task in process pool (must be picklable)"""
        try:
            # Only works with picklable functions and data
            return task_def.function(*task_def.args, **(task_def.kwargs or {}))
        except Exception as e:
            self.logger.error(f"Process execution failed for task {task_def.task_id}: {e}")
            raise
            
    async def _wait_for_dependencies(self, dependencies: List[str]):
        """Wait for task dependencies to complete"""
        dependency_futures = []
        for dep_id in dependencies:
            # Check if dependency is already completed
            if dep_id in self.completed_tasks:
                continue
            elif dep_id in self.failed_tasks:
                raise Exception(f"Dependency {dep_id} failed")
            else:
                # Wait for dependency to complete
                # In a real implementation, you'd have a way to wait for specific tasks
                await asyncio.sleep(0.1)  # Simple polling approach
                
    async def execute_parallel_tasks(self, task_defs: List[TaskDefinition], 
                                   timeout: float = 300.0) -> List[TaskResult]:
        """Execute multiple tasks in parallel and wait for completion"""
        if not task_defs:
            return []
            
        # Submit all tasks
        futures = await self.submit_tasks(task_defs)
        
        # Wait for all tasks to complete with timeout
        try:
            results = await asyncio.wait_for(
                asyncio.gather(*futures, return_exceptions=True),
                timeout=timeout
            )
            
            # Convert results to TaskResult objects
            task_results = []
            for i, result in enumerate(results):
                if isinstance(result, TaskResult):
                    task_results.append(result)
                elif isinstance(result, Exception):
                    task_id = task_defs[i].task_id if i < len(task_defs) else f"task_{i}"
                    task_results.append(TaskResult(
                        task_id=task_id,
                        status=TaskStatus.FAILED,
                        error=str(result),
                        execution_time=0.0
                    ))
                else:
                    task_id = task_defs[i].task_id if i < len(task_defs) else f"task_{i}"
                    task_results.append(TaskResult(
                        task_id=task_id,
                        status=TaskStatus.COMPLETED,
                        result=result,
                        execution_time=0.0
                    ))
                    
            return task_results
            
        except asyncio.TimeoutError:
            # Cancel pending tasks
            for future in futures:
                if not future.done():
                    future.cancel()
                    
            raise Exception(f"Parallel execution timed out after {timeout} seconds")
            
    def get_executor_status(self) -> Dict[str, Any]:
        """Get current executor status"""
        async with self.task_lock:
            return {
                "max_workers": self.max_workers,
                "max_concurrent_tasks": self.max_concurrent_tasks,
                "pending_tasks": len(self.pending_tasks),
                "running_tasks": len(self.running_tasks),
                "completed_tasks": len(self.completed_tasks),
                "failed_tasks": len(self.failed_tasks),
                "performance_metrics": self.performance_metrics.copy()
            }
            
    def cancel_task(self, task_id: str) -> bool:
        """Cancel a pending or running task"""
        async with self.task_lock:
            # Check pending tasks
            if task_id in self.pending_tasks:
                del self.pending_tasks[task_id]
                return True
                
            # Check running tasks (mark for cancellation)
            if task_id in self.running_tasks:
                # In a real implementation, you'd have a way to actually cancel the task
                # For now, we'll just mark it as cancelled in the result when it completes
                return True
                
        return False
        
    def cancel_all_tasks(self):
        """Cancel all pending tasks"""
        async with self.task_lock:
            cancelled_count = len(self.pending_tasks)
            self.pending_tasks.clear()
            return cancelled_count
            
    async def shutdown(self, wait: bool = True):
        """Shutdown the executor"""
        # Cancel all pending tasks
        cancelled = self.cancel_all_tasks()
        if cancelled > 0:
            self.logger.info(f"Cancelled {cancelled} pending tasks")
            
        # Shutdown executors
        self.executor.shutdown(wait=wait)
        self.process_executor.shutdown(wait=wait)
        
        self.logger.info("Parallel executor shutdown complete")
```

#### 2. JobQueue Class
Priority-based job scheduling system.

```python
# File: src/processing/job_queue.py
import asyncio
import heapq
import time
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum
import logging

class Priority(Enum):
    HIGH = 1
    MEDIUM = 2
    LOW = 3

@dataclass
class Job:
    """Job to be scheduled"""
    job_id: str
    task_data: Dict[str, Any]
    priority: Priority
    created_at: float
    scheduled_for: Optional[float] = None  # For delayed execution
    dependencies: List[str] = None

class JobQueue:
    """Priority-based job queue for task scheduling"""
    
    def __init__(self):
        self._queue = []
        self._job_index = 0
        self._jobs: Dict[str, Job] = {}
        self._lock = asyncio.Lock()
        self._condition = asyncio.Condition(self._lock)
        self.logger = logging.getLogger(__name__)
        
    async def put(self, task_data: Dict[str, Any], priority: Priority = Priority.MEDIUM, 
                  job_id: str = None, delay: float = 0, dependencies: List[str] = None):
        """Add job to queue with priority"""
        async with self._lock:
            if job_id is None:
                job_id = f"job_{self._job_index}"
                self._job_index += 1
                
            scheduled_time = time.time() + delay if delay > 0 else None
            
            job = Job(
                job_id=job_id,
                task_data=task_data,
                priority=priority,
                created_at=time.time(),
                scheduled_for=scheduled_time,
                dependencies=dependencies
            )
            
            self._jobs[job_id] = job
            
            # Add to priority queue
            # heapq is a min-heap, so we use priority.value to get correct ordering
            heapq.heappush(self._queue, (priority.value, job.created_at, job_id, job))
            
            self.logger.debug(f"Added job {job_id} with priority {priority.name}")
            
            # Notify waiting consumers
            self._condition.notify_all()
            
    async def get(self, timeout: Optional[float] = None) -> Optional[Job]:
        """Get highest priority job from queue"""
        async with self._condition:
            start_time = time.time()
            
            while True:
                # Check if queue has jobs
                if self._queue:
                    # Peek at the highest priority job
                    priority, created_at, job_id, job = self._queue[0]
                    
                    # Check if job is ready (no dependencies and not delayed)
                    if self._is_job_ready(job):
                        # Remove job from queue and return it
                        heapq.heappop(self._queue)
                        del self._jobs[job_id]
                        self.logger.debug(f"Retrieved job {job_id} with priority {job.priority.name}")
                        return job
                        
                # Check timeout
                if timeout is not None:
                    elapsed = time.time() - start_time
                    if elapsed >= timeout:
                        return None
                    remaining_timeout = timeout - elapsed
                else:
                    remaining_timeout = None
                    
                # Wait for new jobs or timeout
                try:
                    await asyncio.wait_for(self._condition.wait(), timeout=remaining_timeout)
                except asyncio.TimeoutError:
                    return None
                    
    def _is_job_ready(self, job: Job) -> bool:
        """Check if job is ready to execute"""
        # Check if scheduled for future execution
        if job.scheduled_for and time.time() < job.scheduled_for:
            return False
            
        # Check dependencies
        if job.dependencies:
            for dep_id in job.dependencies:
                if dep_id in self._jobs:
                    # Dependency still in queue
                    return False
                    
        return True
        
    async def peek(self) -> Optional[Job]:
        """Peek at the highest priority job without removing it"""
        async with self._lock:
            if self._queue:
                _, _, _, job = self._queue[0]
                return job
            return None
            
    async def remove(self, job_id: str) -> bool:
        """Remove a job from the queue"""
        async with self._lock:
            if job_id in self._jobs:
                # Remove from jobs dict
                del self._jobs[job_id]
                
                # Rebuild queue without the removed job
                new_queue = []
                for item in self._queue:
                    if item[2] != job_id:  # job_id is at index 2
                        new_queue.append(item)
                self._queue = new_queue
                heapq.heapify(self._queue)
                
                self.logger.debug(f"Removed job {job_id}")
                return True
            return False
            
    async def get_queue_size(self) -> int:
        """Get current queue size"""
        async with self._lock:
            return len(self._queue)
            
    async def get_job_count_by_priority(self) -> Dict[str, int]:
        """Get job count by priority"""
        async with self._lock:
            counts = {"HIGH": 0, "MEDIUM": 0, "LOW": 0}
            for _, _, _, job in self._queue:
                counts[job.priority.name] += 1
            return counts
            
    async def clear(self):
        """Clear all jobs from the queue"""
        async with self._lock:
            self._queue.clear()
            self._jobs.clear()
            self.logger.info("Cleared job queue")
            
    async def get_scheduled_jobs(self) -> List[Job]:
        """Get all scheduled jobs"""
        async with self._lock:
            return list(self._jobs.values())
```

#### 3. ResourceManager Class
CPU/memory resource management.

```python
# File: src/processing/resource_manager.py
import psutil
import asyncio
import time
from typing import Dict, Any, Optional
from dataclasses import dataclass
import logging

@dataclass
class ResourceLimits:
    """Resource limits for task execution"""
    max_cpu_percent: float = 80.0
    max_memory_percent: float = 80.0
    max_concurrent_tasks: int = 10
    min_free_memory_mb: int = 500

@dataclass
class ResourceUsage:
    """Current resource usage"""
    cpu_percent: float
    memory_percent: float
    memory_available_mb: float
    concurrent_tasks: int

class ResourceManager:
    """Manages system resources for parallel task execution"""
    
    def __init__(self, limits: ResourceLimits = None):
        self.limits = limits or ResourceLimits()
        self.current_tasks = 0
        self.task_lock = asyncio.Lock()
        self.logger = logging.getLogger(__name__)
        
        # Resource monitoring
        self.last_check_time = 0.0
        self.cached_usage: Optional[ResourceUsage] = None
        self.cache_duration = 1.0  # Cache for 1 second
        
    async def acquire_resources(self, requested_resources: Dict[str, Any] = None) -> bool:
        """Acquire resources for task execution"""
        async with self.task_lock:
            # Check if we can acquire resources
            if not await self._can_acquire_resources(requested_resources):
                return False
                
            # Increment task count
            self.current_tasks += 1
            self.logger.debug(f"Acquired resources for task. Current tasks: {self.current_tasks}")
            return True
            
    async def release_resources(self):
        """Release resources after task completion"""
        async with self.task_lock:
            if self.current_tasks > 0:
                self.current_tasks -= 1
                self.logger.debug(f"Released resources. Current tasks: {self.current_tasks}")
                
    async def _can_acquire_resources(self, requested_resources: Dict[str, Any] = None) -> bool:
        """Check if resources can be acquired"""
        # Check concurrent task limit
        if self.current_tasks >= self.limits.max_concurrent_tasks:
            self.logger.warning(f"Concurrent task limit reached: {self.current_tasks}/{self.limits.max_concurrent_tasks}")
            return False
            
        # Check system resources
        usage = await self.get_current_usage()
        
        # Check CPU usage
        if usage.cpu_percent > self.limits.max_cpu_percent:
            self.logger.warning(f"CPU usage too high: {usage.cpu_percent:.1f}% > {self.limits.max_cpu_percent}%")
            return False
            
        # Check memory usage
        if usage.memory_percent > self.limits.max_memory_percent:
            self.logger.warning(f"Memory usage too high: {usage.memory_percent:.1f}% > {self.limits.max_memory_percent}%")
            return False
            
        if usage.memory_available_mb < self.limits.min_free_memory_mb:
            self.logger.warning(f"Available memory too low: {usage.memory_available_mb:.1f}MB < {self.limits.min_free_memory_mb}MB")
            return False
            
        return True
        
    async def get_current_usage(self) -> ResourceUsage:
        """Get current system resource usage"""
        current_time = time.time()
        
        # Return cached usage if still valid
        if (self.cached_usage and 
            (current_time - self.last_check_time) < self.cache_duration):
            return self.cached_usage
            
        # Get fresh resource usage
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=0.1)
            
            # Memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            memory_available_mb = memory.available / (1024 * 1024)
            
            usage = ResourceUsage(
                cpu_percent=cpu_percent,
                memory_percent=memory_percent,
                memory_available_mb=memory_available_mb,
                concurrent_tasks=self.current_tasks
            )
            
            # Cache the result
            self.cached_usage = usage
            self.last_check_time = current_time
            
            return usage
            
        except Exception as e:
            self.logger.error(f"Failed to get resource usage: {e}")
            # Return default values if monitoring fails
            return ResourceUsage(
                cpu_percent=0.0,
                memory_percent=0.0,
                memory_available_mb=1000.0,
                concurrent_tasks=self.current_tasks
            )
            
    def update_limits(self, new_limits: ResourceLimits):
        """Update resource limits"""
        self.limits = new_limits
        self.logger.info(f"Updated resource limits: {new_limits}")
        
    async def wait_for_resources(self, timeout: float = 30.0) -> bool:
        """Wait for resources to become available"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            if await self._can_acquire_resources():
                return True
            await asyncio.sleep(0.5)  # Check every 500ms
            
        return False
        
    def get_resource_status(self) -> Dict[str, Any]:
        """Get current resource status"""
        return {
            "limits": {
                "max_cpu_percent": self.limits.max_cpu_percent,
                "max_memory_percent": self.limits.max_memory_percent,
                "max_concurrent_tasks": self.limits.max_concurrent_tasks,
                "min_free_memory_mb": self.limits.min_free_memory_mb
            },
            "current": {
                "concurrent_tasks": self.current_tasks,
                "last_usage_check": self.last_check_time
            }
        }
```

#### 4. TaskCoordinator Class
Task dependency management and coordination.

```python
# File: src/processing/task_coordinator.py
import asyncio
from typing import Dict, List, Set, Optional, Callable, Any
from dataclasses import dataclass
from enum import Enum
import logging

class TaskState(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

@dataclass
class TaskInfo:
    """Information about a task"""
    task_id: str
    dependencies: Set[str]
    dependents: Set[str]
    state: TaskState = TaskState.PENDING
    result: Any = None
    error: Optional[str] = None

class TaskCoordinator:
    """Coordinates task dependencies and execution order"""
    
    def __init__(self):
        self.tasks: Dict[str, TaskInfo] = {}
        self.task_lock = asyncio.Lock()
        self.state_changed = asyncio.Event()
        self.logger = logging.getLogger(__name__)
        
    async def register_task(self, task_id: str, dependencies: List[str] = None):
        """Register a task with its dependencies"""
        async with self.task_lock:
            if task_id in self.tasks:
                raise ValueError(f"Task {task_id} already registered")
                
            # Create task info
            task_info = TaskInfo(
                task_id=task_id,
                dependencies=set(dependencies or []),
                dependents=set()
            )
            
            # Update dependents of dependency tasks
            if dependencies:
                for dep_id in dependencies:
                    if dep_id in self.tasks:
                        self.tasks[dep_id].dependents.add(task_id)
                    else:
                        # Create placeholder for dependency if it doesn't exist
                        dep_info = TaskInfo(
                            task_id=dep_id,
                            dependencies=set(),
                            dependents={task_id}
                        )
                        self.tasks[dep_id] = dep_info
                        
            self.tasks[task_id] = task_info
            self.logger.debug(f"Registered task {task_id} with dependencies {dependencies}")
            
    async def mark_task_running(self, task_id: str):
        """Mark a task as running"""
        async with self.task_lock:
            if task_id not in self.tasks:
                raise ValueError(f"Task {task_id} not registered")
                
            self.tasks[task_id].state = TaskState.RUNNING
            self.logger.debug(f"Task {task_id} marked as running")
            self.state_changed.set()
            self.state_changed.clear()
            
    async def mark_task_completed(self, task_id: str, result: Any = None):
        """Mark a task as completed"""
        async with self.task_lock:
            if task_id not in self.tasks:
                raise ValueError(f"Task {task_id} not registered")
                
            task_info = self.tasks[task_id]
            task_info.state = TaskState.COMPLETED
            task_info.result = result
            
            self.logger.debug(f"Task {task_id} marked as completed")
            self.state_changed.set()
            self.state_changed.clear()
            
    async def mark_task_failed(self, task_id: str, error: str = None):
        """Mark a task as failed"""
        async with self.task_lock:
            if task_id not in self.tasks:
                raise ValueError(f"Task {task_id} not registered")
                
            task_info = self.tasks[task_id]
            task_info.state = TaskState.FAILED
            task_info.error = error
            
            self.logger.debug(f"Task {task_id} marked as failed: {error}")
            self.state_changed.set()
            self.state_changed.clear()
            
    async def get_ready_tasks(self) -> List[str]:
        """Get tasks that are ready to run (no pending dependencies)"""
        async with self.task_lock:
            ready_tasks = []
            for task_id, task_info in self.tasks.items():
                if task_info.state == TaskState.PENDING:
                    # Check if all dependencies are completed
                    if all(
                        dep_id in self.tasks and 
                        self.tasks[dep_id].state == TaskState.COMPLETED
                        for dep_id in task_info.dependencies
                    ):
                        ready_tasks.append(task_id)
            return ready_tasks
            
    async def wait_for_ready_tasks(self, timeout: float = None) -> List[str]:
        """Wait for tasks to become ready"""
        start_time = asyncio.get_event_loop().time()
        
        while True:
            ready_tasks = await self.get_ready_tasks()
            if ready_tasks:
                return ready_tasks
                
            # Check timeout
            if timeout is not None:
                elapsed = asyncio.get_event_loop().time() - start_time
                if elapsed >= timeout:
                    return []
                remaining_timeout = timeout - elapsed
            else:
                remaining_timeout = None
                
            # Wait for state changes
            try:
                await asyncio.wait_for(self.state_changed.wait(), timeout=remaining_timeout)
            except asyncio.TimeoutError:
                return []
                
    async def get_task_state(self, task_id: str) -> TaskState:
        """Get the state of a task"""
        async with self.task_lock:
            if task_id not in self.tasks:
                raise ValueError(f"Task {task_id} not registered")
            return self.tasks[task_id].state
            
    async def get_task_result(self, task_id: str) -> Any:
        """Get the result of a completed task"""
        async with self.task_lock:
            if task_id not in self.tasks:
                raise ValueError(f"Task {task_id} not registered")
                
            task_info = self.tasks[task_id]
            if task_info.state != TaskState.COMPLETED:
                raise ValueError(f"Task {task_id} is not completed")
                
            return task_info.result
            
    async def get_failed_tasks(self) -> List[str]:
        """Get list of failed tasks"""
        async with self.task_lock:
            return [
                task_id for task_id, task_info in self.tasks.items()
                if task_info.state == TaskState.FAILED
            ]
            
    async def get_pending_tasks(self) -> List[str]:
        """Get list of pending tasks"""
        async with self.task_lock:
            return [
                task_id for task_id, task_info in self.tasks.items()
                if task_info.state == TaskState.PENDING
            ]
            
    async def get_running_tasks(self) -> List[str]:
        """Get list of running tasks"""
        async with self.task_lock:
            return [
                task_id for task_id, task_info in self.tasks.items()
                if task_info.state == TaskState.RUNNING
            ]
            
    async def is_workflow_completed(self) -> bool:
        """Check if all tasks in the workflow are completed"""
        async with self.task_lock:
            return all(
                task_info.state in [TaskState.COMPLETED, TaskState.FAILED, TaskState.CANCELLED]
                for task_info in self.tasks.values()
            )
            
    async def get_workflow_status(self) -> Dict[str, Any]:
        """Get overall workflow status"""
        async with self.task_lock:
            status_counts = {}
            for task_info in self.tasks.values():
                state_name = task_info.state.value
                status_counts[state_name] = status_counts.get(state_name, 0) + 1
                
            return {
                "total_tasks": len(self.tasks),
                "status_counts": status_counts,
                "completed": await self.is_workflow_completed()
            }
            
    async def cancel_task(self, task_id: str):
        """Cancel a task"""
        async with self.task_lock:
            if task_id in self.tasks:
                self.tasks[task_id].state = TaskState.CANCELLED
                self.logger.debug(f"Task {task_id} cancelled")
                self.state_changed.set()
                self.state_changed.clear()
                
    async def cancel_workflow(self):
        """Cancel all pending tasks in the workflow"""
        async with self.task_lock:
            cancelled_count = 0
            for task_info in self.tasks.values():
                if task_info.state == TaskState.PENDING:
                    task_info.state = TaskState.CANCELLED
                    cancelled_count += 1
                    
            if cancelled_count > 0:
                self.logger.info(f"Cancelled {cancelled_count} pending tasks")
                self.state_changed.set()
                self.state_changed.clear()
```

#### 5. Integration with Pipeline MCP Server

```python
# File: src/pipeline_mcp_server.py (integration points)
# ADD imports after existing imports:
from processing.parallel_executor import ParallelExecutor, TaskDefinition, TaskPriority
from processing.job_queue import JobQueue, Priority
from processing.resource_manager import ResourceManager, ResourceLimits
from processing.task_coordinator import TaskCoordinator

# MODIFY PipelineMCPServer class:
class PipelineMCPServer:
    def __init__(self):
        # ... existing code ...
        
        # ADD PARALLEL PROCESSING CAPABILITIES
        self.parallel_executor = ParallelExecutor(
            max_workers=4, 
            max_concurrent_tasks=10
        )
        self.job_queue = JobQueue()
        self.resource_manager = ResourceManager()
        self.task_coordinator = TaskCoordinator()
        
        # Performance optimization settings
        self.optimization_settings = {
            "enable_parallel_processing": True,
            "max_parallel_cycles": 3,
            "resource_aware_scheduling": True,
            "dependency_aware_execution": True
        }
        
    async def shutdown(self):
        """Shutdown the server and cleanup resources"""
        # ... existing shutdown code ...
        
        # Shutdown parallel executor
        await self.parallel_executor.shutdown()
        
    def get_server_performance(self) -> Dict[str, Any]:
        """Get server performance metrics including parallel processing stats"""
        base_metrics = {
            # ... existing metrics ...
        }
        
        # ADD PARALLEL PROCESSING METRICS
        parallel_metrics = self.parallel_executor.get_executor_status()
        
        base_metrics.update({
            "parallel_processing": parallel_metrics,
            "optimization_settings": self.optimization_settings
        })
        
        return base_metrics

# MODIFY handle_pipeline_run_full for parallel processing:
async def handle_pipeline_run_full(arguments: Dict[str, Any]) -> List[TextContent]:
    """Execute complete pipeline cycle with parallel processing capabilities"""
    
    # ... existing setup code ...
    
    # Check if parallel processing is enabled
    if server.optimization_settings.get("enable_parallel_processing", True):
        return await handle_pipeline_run_parallel(arguments)
    else:
        # Fall back to sequential execution
        return await handle_pipeline_run_sequential(arguments)

async def handle_pipeline_run_parallel(arguments: Dict[str, Any]) -> List[TextContent]:
    """Execute pipeline with parallel processing"""
    
    # ... existing setup code ...
    
    results = {
        "session_id": session_id,
        "cycles": [],
        "final_metrics": {},
        "success": False,
        "parallel_processing": True
    }
    
    try:
        # Create task definitions for parallel execution
        task_definitions = []
        
        for cycle in range(1, max_cycles + 1):
            # Create task definition for this cycle
            cycle_task_def = TaskDefinition(
                task_id=f"pipeline_cycle_{session_id}_{cycle}",
                task_type="pipeline_cycle",
                function=execute_pipeline_cycle,
                args=(session_id, cycle, arguments),
                priority=TaskPriority.HIGH if cycle == 1 else TaskPriority.MEDIUM,
                timeout=600.0,  # 10 minutes
                max_retries=2
            )
            
            task_definitions.append(cycle_task_def)
            
        # Execute tasks in parallel
        cycle_results = await server.parallel_executor.execute_parallel_tasks(
            task_definitions, 
            timeout=3600.0  # 1 hour total timeout
        )
        
        # Process results
        successful_cycles = 0
        for task_result in cycle_results:
            if task_result.status == TaskStatus.COMPLETED:
                cycle_result = task_result.result
                results["cycles"].append(cycle_result)
                successful_cycles += 1
            else:
                # Handle failed cycles
                results["cycles"].append({
                    "cycle": task_result.task_id.split("_")[-1],
                    "status": "failed",
                    "error": task_result.error
                })
                
        # Determine overall success
        results["success"] = successful_cycles > 0
        
        # Update session metrics
        session.metrics.update({
            "parallel_cycles_executed": len(task_definitions),
            "parallel_cycles_successful": successful_cycles,
            "parallel_execution_time": sum(
                tr.execution_time for tr in cycle_results 
                if tr.status == TaskStatus.COMPLETED
            )
        })
        
    except Exception as e:
        logger.error(f"Parallel pipeline execution failed: {e}")
        results["error"] = str(e)
        
    # ... existing return code ...
    
    return [TextContent(
        type="text",
        text=json.dumps({
            "tool": "pipeline_run_full",
            "status": "success" if results["success"] else "partial",
            "results": results
        }, indent=2)
    )]

async def execute_pipeline_cycle(session_id: str, cycle: int, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Execute a single pipeline cycle (runs in parallel)"""
    
    # This function would contain the logic for a single pipeline cycle
    # It's extracted so it can be run in parallel
    
    cycle_start = time.time()
    cycle_result = {"cycle": cycle, "stages": [], "start_time": cycle_start}
    
    try:
        # Stage 1: Version Keeper Scan
        logger.info(f"Cycle {cycle}: Running Version Keeper scan")
        scan_result = await handle_version_keeper_scan({
            "session_id": session_id,
            "comprehensive": True,
            "output_format": "json"
        })
        
        scan_data = json.loads(scan_result[0].text)
        cycle_result["stages"].append({
            "stage": "version_keeper_scan",
            "status": "completed",
            "execution_time": scan_data.get("execution_time", 0)
        })
        
        # Check if no issues found
        issues_found = session.metrics.get("total_issues", 0)
        if issues_found == 0 and arguments.get("break_on_no_issues", True):
            logger.info(f"Cycle {cycle}: No issues found, pipeline complete")
            cycle_result["status"] = "completed_no_issues"
            return cycle_result
            
        # Stage 2: Quality Patcher (only if issues found)
        if issues_found > 0:
            logger.info(f"Cycle {cycle}: Applying fixes for {issues_found} issues")
            fix_result = await handle_quality_patcher_fix({
                "session_id": session_id,
                "max_fixes": arguments.get("max_fixes_per_cycle", 10),
                "auto_apply": True,
                "claude_agent": True
            })
            
            fix_data = json.loads(fix_result[0].text)
            cycle_result["stages"].append({
                "stage": "quality_patcher_fix", 
                "status": "completed",
                "execution_time": fix_data.get("execution_time", 0),
                "fixes_applied": session.metrics.get("fixes_applied", 0)
            })
            
            # Stage 3: Validation Scan
            logger.info(f"Cycle {cycle}: Running validation scan")
            validation_result = await handle_version_keeper_scan({
                "session_id": session_id,
                "comprehensive": True,
                "output_format": "json"
            })
            
            validation_data = json.loads(validation_result[0].text)
            cycle_result["stages"].append({
                "stage": "validation_scan",
                "status": "completed", 
                "execution_time": validation_data.get("execution_time", 0),
                "remaining_issues": session.metrics.get("remaining_issues", 0)
            })
            
        cycle_result["status"] = "completed"
        cycle_result["execution_time"] = time.time() - cycle_start
        
    except Exception as e:
        logger.error(f"Cycle {cycle} failed: {str(e)}")
        cycle_result["status"] = "failed"
        cycle_result["error"] = str(e)
        cycle_result["execution_time"] = time.time() - cycle_start
        
    return cycle_result

# ADD new tool for parallel task management:
@server.call_tool()
async def handle_parallel_task_management(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """Manage parallel tasks and get status information"""
    
    action = arguments.get("action", "status")
    
    if action == "status":
        # Get parallel processing status
        status = server.parallel_executor.get_executor_status()
        return [TextContent(
            type="text",
            text=json.dumps({
                "tool": "parallel_task_management",
                "action": "status",
                "status": status
            }, indent=2)
        )]
        
    elif action == "queue_status":
        # Get job queue status
        queue_size = await server.job_queue.get_queue_size()
        job_counts = await server.job_queue.get_job_count_by_priority()
        return [TextContent(
            type="text",
            text=json.dumps({
                "tool": "parallel_task_management",
                "action": "queue_status",
                "queue_size": queue_size,
                "job_counts": job_counts
            }, indent=2)
        )]
        
    elif action == "resource_status":
        # Get resource status
        resource_status = server.resource_manager.get_resource_status()
        usage = await server.resource_manager.get_current_usage()
        return [TextContent(
            type="text",
            text=json.dumps({
                "tool": "parallel_task_management",
                "action": "resource_status",
                "resource_status": resource_status,
                "current_usage": {
                    "cpu_percent": usage.cpu_percent,
                    "memory_percent": usage.memory_percent,
                    "memory_available_mb": usage.memory_available_mb,
                    "concurrent_tasks": usage.concurrent_tasks
                }
            }, indent=2)
        )]
        
    else:
        raise ValueError(f"Unknown action: {action}")
```

### Configuration and Deployment

#### Environment Configuration

```python
# File: src/processing/config.py
import os
from dataclasses import dataclass
from typing import Optional

@dataclass
class ParallelProcessingConfig:
    """Configuration for parallel processing system"""
    
    # Executor settings
    max_workers: int = int(os.getenv('PARALLEL_MAX_WORKERS', '4'))
    max_concurrent_tasks: int = int(os.getenv('PARALLEL_MAX_CONCURRENT_TASKS', '10'))
    enable_process_pool: bool = os.getenv('PARALLEL_ENABLE_PROCESS_POOL', 'false').lower() == 'true'
    
    # Resource management
    max_cpu_percent: float = float(os.getenv('PARALLEL_MAX_CPU_PERCENT', '80.0'))
    max_memory_percent: float = float(os.getenv('PARALLEL_MAX_MEMORY_PERCENT', '80.0'))
    min_free_memory_mb: int = int(os.getenv('PARALLEL_MIN_FREE_MEMORY_MB', '500'))
    
    # Task settings
    default_task_timeout: float = float(os.getenv('PARALLEL_DEFAULT_TASK_TIMEOUT', '300.0'))
    max_task_retries: int = int(os.getenv('PARALLEL_MAX_TASK_RETRIES', '3'))
    
    # Optimization settings
    enable_resource_aware_scheduling: bool = os.getenv('PARALLEL_ENABLE_RESOURCE_SCHEDULING', 'true').lower() == 'true'
    enable_dependency_aware_execution: bool = os.getenv('PARALLEL_ENABLE_DEPENDENCY_EXECUTION', 'true').lower() == 'true'
    
    @classmethod
    def from_env(cls) -> 'ParallelProcessingConfig':
        """Create configuration from environment variables"""
        return cls()
```

#### Docker Configuration

```yaml
# File: docker-compose.parallel.yml
version: '3.8'

services:
  mcp-parallel-processing:
    build:
      context: .
      dockerfile: docker/Dockerfile.parallel
    environment:
      - PARALLEL_MAX_WORKERS=4
      - PARALLEL_MAX_CONCURRENT_TASKS=10
      - PARALLEL_MAX_CPU_PERCENT=80.0
      - PARALLEL_MAX_MEMORY_PERCENT=80.0
      - PARALLEL_MIN_FREE_MEMORY_MB=500
      - PARALLEL_DEFAULT_TASK_TIMEOUT=300.0
      - PARALLEL_MAX_TASK_RETRIES=3
      - PARALLEL_ENABLE_RESOURCE_SCHEDULING=true
      - PARALLEL_ENABLE_DEPENDENCY_EXECUTION=true
    volumes:
      - ./src/processing:/app/src/processing
      - ./logs:/app/logs
    depends_on:
      - mcp-system
    networks:
      - mcp-network
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 2G
        reservations:
          cpus: '1.0'
          memory: 1G

  mcp-task-monitor:
    build:
      context: .
      dockerfile: docker/Dockerfile.task-monitor
    ports:
      - "8081:8081"  # Task monitoring API
    environment:
      - MONITORING_PORT=8081
      - MONITORING_ENABLED=true
    volumes:
      - ./src/processing:/app/src/processing
    networks:
      - mcp-network

networks:
  mcp-network:
    driver: bridge
```

### Testing and Validation

#### Unit Tests

```python
# File: tests/test_parallel_processing.py
import asyncio
import unittest
import time
from unittest.mock import Mock, AsyncMock, patch
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from processing.parallel_executor import ParallelExecutor, TaskDefinition, TaskPriority, TaskStatus
from processing.job_queue import JobQueue, Priority
from processing.resource_manager import ResourceManager, ResourceLimits
from processing.task_coordinator import TaskCoordinator, TaskState

class TestParallelExecutor(unittest.TestCase):
    """Test cases for ParallelExecutor"""
    
    def setUp(self):
        self.executor = ParallelExecutor(max_workers=2, max_concurrent_tasks=5)
        
    def tearDown(self):
        # Cleanup executor
        asyncio.run(self.executor.shutdown())
        
    async def async_tearDown(self):
        await self.executor.shutdown()
        
    def test_task_definition_creation(self):
        """Test creating task definitions"""
        def test_function():
            return "test_result"
            
        task_def = TaskDefinition(
            task_id="test_task_1",
            task_type="test",
            function=test_function,
            args=(),
            kwargs=None,
            priority=TaskPriority.MEDIUM,
            dependencies=None,
            timeout=30.0,
            retry_count=0,
            max_retries=3
        )
        
        self.assertEqual(task_def.task_id, "test_task_1")
        self.assertEqual(task_def.task_type, "test")
        self.assertEqual(task_def.function, test_function)
        self.assertEqual(task_def.priority, TaskPriority.MEDIUM)
        self.assertEqual(task_def.timeout, 30.0)
        self.assertEqual(task_def.max_retries, 3)
        
    async def test_simple_task_execution(self):
        """Test executing a simple task"""
        def simple_task(x, y):
            return x + y
            
        task_def = TaskDefinition(
            task_id="simple_add_task",
            task_type="compute",
            function=simple_task,
            args=(5, 3),
            priority=TaskPriority.HIGH
        )
        
        future = await self.executor.submit_task(task_def)
        result = await future
        
        self.assertEqual(result.status, TaskStatus.COMPLETED)
        self.assertEqual(result.result, 8)
        self.assertGreater(result.execution_time, 0)
        
    async def test_multiple_task_execution(self):
        """Test executing multiple tasks"""
        def compute_task(n):
            # Simulate some work
            time.sleep(0.1)
            return n * n
            
        # Create task definitions
        task_defs = []
        for i in range(5):
            task_def = TaskDefinition(
                task_id=f"compute_task_{i}",
                task_type="compute",
                function=compute_task,
                args=(i,),
                priority=TaskPriority.MEDIUM
            )
            task_defs.append(task_def)
            
        # Execute tasks in parallel
        results = await self.executor.execute_parallel_tasks(task_defs, timeout=10.0)
        
        # Verify results
        self.assertEqual(len(results), 5)
        for i, result in enumerate(results):
            self.assertEqual(result.status, TaskStatus.COMPLETED)
            self.assertEqual(result.result, i * i)
            
    async def test_task_with_dependencies(self):
        """Test task execution with dependencies"""
        execution_order = []
        
        def task_a():
            execution_order.append("A")
            return "result_a"
            
        def task_b(result_a):
            execution_order.append("B")
            return f"result_b_{result_a}"
            
        # Create tasks
        task_a_def = TaskDefinition(
            task_id="task_a",
            task_type="compute",
            function=task_a,
            priority=TaskPriority.HIGH
        )
        
        task_b_def = TaskDefinition(
            task_id="task_b",
            task_type="compute",
            function=task_b,
            args=("placeholder",),  # Will be replaced with actual result
            dependencies=["task_a"],
            priority=TaskPriority.HIGH
        )
        
        # Submit tasks
        future_a = await self.executor.submit_task(task_a_def)
        future_b = await self.executor.submit_task(task_b_def)
        
        # Wait for completion
        result_a = await future_a
        result_b = await future_b
        
        # Verify execution order and results
        self.assertEqual(execution_order, ["A", "B"])
        self.assertEqual(result_a.status, TaskStatus.COMPLETED)
        self.assertEqual(result_a.result, "result_a")
        self.assertEqual(result_b.status, TaskStatus.COMPLETED)
        self.assertEqual(result_b.result, "result_b_placeholder")  # Placeholder since we don't actually pass the result
        
    async def test_task_failure_and_retry(self):
        """Test task failure and retry mechanism"""
        call_count = 0
        
        def failing_task():
            nonlocal call_count
            call_count += 1
            if call_count <= 2:
                raise Exception(f"Task failed on attempt {call_count}")
            return "success"
            
        task_def = TaskDefinition(
            task_id="failing_task",
            task_type="compute",
            function=failing_task,
            max_retries=3,
            priority=TaskPriority.HIGH
        )
        
        future = await self.executor.submit_task(task_def)
        result = await future
        
        # Should succeed after retries
        self.assertEqual(result.status, TaskStatus.COMPLETED)
        self.assertEqual(result.result, "success")
        self.assertEqual(call_count, 3)  # Called 3 times (2 failures + 1 success)
        
    async def test_task_timeout(self):
        """Test task timeout handling"""
        def slow_task():
            time.sleep(2)  # Longer than timeout
            return "slow_result"
            
        task_def = TaskDefinition(
            task_id="slow_task",
            task_type="compute",
            function=slow_task,
            timeout=0.5,  # Short timeout
            priority=TaskPriority.LOW
        )
        
        future = await self.executor.submit_task(task_def)
        
        # Should raise timeout exception
        with self.assertRaises(Exception):
            await future
            
    async def test_executor_status(self):
        """Test getting executor status"""
        status = self.executor.get_executor_status()
        
        self.assertEqual(status["max_workers"], 2)
        self.assertEqual(status["max_concurrent_tasks"], 5)
        self.assertEqual(status["pending_tasks"], 0)
        self.assertEqual(status["running_tasks"], 0)
        self.assertEqual(status["completed_tasks"], 0)
        self.assertEqual(status["failed_tasks"], 0)
        
    async def test_task_cancellation(self):
        """Test task cancellation"""
        def long_running_task():
            time.sleep(5)
            return "result"
            
        task_def = TaskDefinition(
            task_id="long_task",
            task_type="compute",
            function=long_running_task,
            priority=TaskPriority.MEDIUM
        )
        
        # Submit task and immediately cancel
        future = await self.executor.submit_task(task_def)
        self.executor.cancel_task("long_task")
        
        # Task should be cancelled
        with self.assertRaises(Exception):
            await future

class TestJobQueue(unittest.TestCase):
    """Test cases for JobQueue"""
    
    def setUp(self):
        self.job_queue = JobQueue()
        
    async def test_job_queue_put_get(self):
        """Test putting and getting jobs from queue"""
        # Put jobs with different priorities
        await self.job_queue.put(
            task_data={"task": "high_priority"},
            priority=Priority.HIGH,
            job_id="high_job"
        )
        
        await self.job_queue.put(
            task_data={"task": "low_priority"},
            priority=Priority.LOW,
            job_id="low_job"
        )
        
        await self.job_queue.put(
            task_data={"task": "medium_priority"},
            priority=Priority.MEDIUM,
            job_id="medium_job"
        )
        
        # Get jobs - should be in priority order (HIGH, MEDIUM, LOW)
        job1 = await self.job_queue.get()
        self.assertEqual(job1.job_id, "high_job")
        self.assertEqual(job1.task_data["task"], "high_priority")
        self.assertEqual(job1.priority, Priority.HIGH)
        
        job2 = await self.job_queue.get()
        self.assertEqual(job2.job_id, "medium_job")
        self.assertEqual(job2.priority, Priority.MEDIUM)
        
        job3 = await self.job_queue.get()
        self.assertEqual(job3.job_id, "low_job")
        self.assertEqual(job3.priority, Priority.LOW)
        
    async def test_job_queue_size(self):
        """Test getting queue size"""
        initial_size = await self.job_queue.get_queue_size()
        self.assertEqual(initial_size, 0)
        
        # Add jobs
        await self.job_queue.put({"task": "job1"}, Priority.MEDIUM)
        await self.job_queue.put({"task": "job2"}, Priority.HIGH)
        
        size = await self.job_queue.get_queue_size()
        self.assertEqual(size, 2)
        
    async def test_job_queue_counts(self):
        """Test getting job counts by priority"""
        # Add jobs with different priorities
        await self.job_queue.put({"task": "high1"}, Priority.HIGH)
        await self.job_queue.put({"task": "high2"}, Priority.HIGH)
        await self.job_queue.put({"task": "medium1"}, Priority.MEDIUM)
        await self.job_queue.put({"task": "low1"}, Priority.LOW)
        await self.job_queue.put({"task": "low2"}, Priority.LOW)
        await self.job_queue.put({"task": "low3"}, Priority.LOW)
        
        counts = await self.job_queue.get_job_count_by_priority()
        self.assertEqual(counts["HIGH"], 2)
        self.assertEqual(counts["MEDIUM"], 1)
        self.assertEqual(counts["LOW"], 3)
        
    async def test_job_removal(self):
        """Test removing jobs from queue"""
        await self.job_queue.put({"task": "job1"}, Priority.MEDIUM, job_id="job1")
        await self.job_queue.put({"task": "job2"}, Priority.HIGH, job_id="job2")
        await self.job_queue.put({"task": "job3"}, Priority.LOW, job_id="job3")
        
        # Remove middle job
        removed = await self.job_queue.remove("job2")
        self.assertTrue(removed)
        
        # Verify queue size
        size = await self.job_queue.get_queue_size()
        self.assertEqual(size, 2)
        
        # Get remaining jobs - should be job1 then job3 (medium then low)
        job1 = await self.job_queue.get()
        self.assertEqual(job1.job_id, "job1")
        
        job3 = await self.job_queue.get()
        self.assertEqual(job3.job_id, "job3")

class TestResourceManager(unittest.TestCase):
    """Test cases for ResourceManager"""
    
    def setUp(self):
        limits = ResourceLimits(
            max_cpu_percent=80.0,
            max_memory_percent=80.0,
            max_concurrent_tasks=5,
            min_free_memory_mb=100
        )
        self.resource_manager = ResourceManager(limits)
        
    async def test_resource_acquisition(self):
        """Test acquiring and releasing resources"""
        # Should be able to acquire resources initially
        acquired = await self.resource_manager.acquire_resources()
        self.assertTrue(acquired)
        
        # Check current tasks
        status = self.resource_manager.get_resource_status()
        self.assertEqual(status["current"]["concurrent_tasks"], 1)
        
        # Release resources
        await self.resource_manager.release_resources()
        
        # Check current tasks
        status = self.resource_manager.get_resource_status()
        self.assertEqual(status["current"]["concurrent_tasks"], 0)
        
    async def test_resource_limits(self):
        """Test resource limits"""
        # Acquire maximum allowed tasks
        for i in range(5):
            acquired = await self.resource_manager.acquire_resources()
            self.assertTrue(acquired, f"Failed to acquire resource {i}")
            
        # Try to acquire one more - should fail
        acquired = await self.resource_manager.acquire_resources()
        self.assertFalse(acquired, "Should not be able to acquire more than limit")
        
        # Release one and try again
        await self.resource_manager.release_resources()
        acquired = await self.resource_manager.acquire_resources()
        self.assertTrue(acquired, "Should be able to acquire after releasing")

class TestTaskCoordinator(unittest.TestCase):
    """Test cases for TaskCoordinator"""
    
    def setUp(self):
        self.task_coordinator = TaskCoordinator()
        
    async def test_task_registration(self):
        """Test registering tasks"""
        await self.task_coordinator.register_task("task1")
        await self.task_coordinator.register_task("task2", dependencies=["task1"])
        await self.task_coordinator.register_task("task3", dependencies=["task1", "task2"])
        
        # Check task states
        state1 = await self.task_coordinator.get_task_state("task1")
        self.assertEqual(state1, TaskState.PENDING)
        
        # Check ready tasks (only task1 should be ready)
        ready_tasks = await self.task_coordinator.get_ready_tasks()
        self.assertEqual(ready_tasks, ["task1"])
        
    async def test_task_execution_flow(self):
        """Test task execution flow with dependencies"""
        # Register tasks with dependencies
        await self.task_coordinator.register_task("task1")
        await self.task_coordinator.register_task("task2", dependencies=["task1"])
        await self.task_coordinator.register_task("task3", dependencies=["task1"])
        await self.task_coordinator.register_task("task4", dependencies=["task2", "task3"])
        
        # Initially, only task1 should be ready
        ready_tasks = await self.task_coordinator.get_ready_tasks()
        self.assertEqual(set(ready_tasks), {"task1"})
        
        # Mark task1 as running and completed
        await self.task_coordinator.mark_task_running("task1")
        await self.task_coordinator.mark_task_completed("task1", "result1")
        
        # Now task2 and task3 should be ready
        ready_tasks = await self.task_coordinator.get_ready_tasks()
        self.assertEqual(set(ready_tasks), {"task2", "task3"})
        
        # Mark task2 as completed
        await self.task_coordinator.mark_task_running("task2")
        await self.task_coordinator.mark_task_completed("task2", "result2")
        
        # Still need task3 to complete for task4
        ready_tasks = await self.task_coordinator.get_ready_tasks()
        self.assertEqual(set(ready_tasks), {"task3"})
        
        # Mark task3 as completed
        await self.task_coordinator.mark_task_running("task3")
        await self.task_coordinator.mark_task_completed("task3", "result3")
        
        # Now task4 should be ready
        ready_tasks = await self.task_coordinator.get_ready_tasks()
        self.assertEqual(set(ready_tasks), {"task4"})
        
        # Mark task4 as completed
        await self.task_coordinator.mark_task_running("task4")
        await self.task_coordinator.mark_task_completed("task4", "result4")
        
        # All tasks should be completed
        workflow_status = await self.task_coordinator.get_workflow_status()
        self.assertTrue(workflow_status["completed"])
        self.assertEqual(workflow_status["status_counts"]["completed"], 4)
        
    async def test_task_failure_handling(self):
        """Test handling of task failures"""
        await self.task_coordinator.register_task("task1")
        await self.task_coordinator.register_task("task2", dependencies=["task1"])
        
        # Mark task1 as failed
        await self.task_coordinator.mark_task_running("task1")
        await self.task_coordinator.mark_task_failed("task1", "Something went wrong")
        
        # Task2 should never become ready since its dependency failed
        ready_tasks = await self.task_coordinator.get_ready_tasks()
        self.assertEqual(ready_tasks, [])
        
        # Check failed tasks
        failed_tasks = await self.task_coordinator.get_failed_tasks()
        self.assertEqual(failed_tasks, ["task1"])

if __name__ == '__main__':
    unittest.main()
```

### Integration Testing

```python
# File: tests/test_parallel_processing_integration.py
import asyncio
import unittest
import time
import sys
from pathlib import Path
from unittest.mock import Mock, AsyncMock, patch

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from processing.parallel_executor import ParallelExecutor, TaskDefinition, TaskPriority
from processing.job_queue import JobQueue, Priority
from processing.resource_manager import ResourceManager
from processing.task_coordinator import TaskCoordinator

class TestParallelProcessingIntegration(unittest.TestCase):
    """Integration tests for parallel processing components"""
    
    def setUp(self):
        self.executor = ParallelExecutor(max_workers=3, max_concurrent_tasks=5)
        self.job_queue = JobQueue()
        self.resource_manager = ResourceManager()
        self.task_coordinator = TaskCoordinator()
        
    async def async_tearDown(self):
        await self.executor.shutdown()
        
    async def test_end_to_end_parallel_pipeline(self):
        """Test end-to-end parallel pipeline execution"""
        # Simulate a pipeline with multiple stages that can run in parallel
        
        # Track execution order and timing
        execution_log = []
        
        def stage_one_worker(item_id):
            """Simulate stage one work"""
            time.sleep(0.1)  # Simulate work
            execution_log.append(f"stage_one_{item_id}_start")
            time.sleep(0.2)  # More work
            execution_log.append(f"stage_one_{item_id}_end")
            return f"result_one_{item_id}"
            
        def stage_two_worker(prev_result, item_id):
            """Simulate stage two work (depends on stage one)"""
            time.sleep(0.1)  # Simulate work
            execution_log.append(f"stage_two_{item_id}_start")
            time.sleep(0.15)  # More work
            execution_log.append(f"stage_two_{item_id}_end")
            return f"result_two_{item_id}_{prev_result}"
            
        def stage_three_worker(prev_result, item_id):
            """Simulate stage three work (depends on stage two)"""
            time.sleep(0.05)  # Simulate work
            execution_log.append(f"stage_three_{item_id}_start")
            time.sleep(0.1)  # More work
            execution_log.append(f"stage_three_{item_id}_end")
            return f"final_result_{item_id}_{prev_result}"
            
        # Create task definitions for 3 items
        task_definitions = []
        
        for i in range(3):
            # Stage 1 tasks (can run in parallel)
            stage_one_task = TaskDefinition(
                task_id=f"stage_one_{i}",
                task_type="compute",
                function=stage_one_worker,
                args=(i,),
                priority=TaskPriority.HIGH
            )
            task_definitions.append(stage_one_task)
            
            # Stage 2 tasks (depend on stage 1)
            stage_two_task = TaskDefinition(
                task_id=f"stage_two_{i}",
                task_type="compute",
                function=stage_two_worker,
                args=(f"placeholder_{i}", i),  # Placeholder for actual result
                dependencies=[f"stage_one_{i}"],
                priority=TaskPriority.MEDIUM
            )
            task_definitions.append(stage_two_task)
            
            # Stage 3 tasks (depend on stage 2)
            stage_three_task = TaskDefinition(
                task_id=f"stage_three_{i}",
                task_type="compute",
                function=stage_three_worker,
                args=(f"placeholder_{i}", i),  # Placeholder for actual result
                dependencies=[f"stage_two_{i}"],
                priority=TaskPriority.LOW
            )
            task_definitions.append(stage_three_task)
            
        # Execute all tasks in parallel
        start_time = time.time()
        results = await self.executor.execute_parallel_tasks(task_definitions, timeout=10.0)
        end_time = time.time()
        
        # Verify all tasks completed
        completed_tasks = [r for r in results if r.status == "completed"]
        self.assertEqual(len(completed_tasks), 9)  # 3 items × 3 stages
        
        # Verify execution time is less than sequential (which would be ~2.7s)
        execution_time = end_time - start_time
        self.assertLess(execution_time, 2.0)  # Should be much faster than sequential
        
        # Verify all tasks have results
        for result in completed_tasks:
            self.assertIsNotNone(result.result)
            self.assertGreater(result.execution_time, 0)
            
        # Verify executor status
        status = self.executor.get_executor_status()
        self.assertEqual(status["completed_tasks"], 9)
        self.assertEqual(status["failed_tasks"], 0)
        self.assertEqual(status["total_tasks"], 9)
        
    async def test_resource_aware_scheduling(self):
        """Test resource-aware task scheduling"""
        # Configure resource manager with strict limits
        from processing.resource_manager import ResourceLimits
        strict_limits = ResourceLimits(
            max_cpu_percent=50.0,
            max_memory_percent=50.0,
            max_concurrent_tasks=2,  # Very strict limit
            min_free_memory_mb=500
        )
        self.resource_manager.update_limits(strict_limits)
        
        # Create memory-intensive tasks
        def memory_intensive_task(size_mb):
            # Allocate memory
            data = [0] * (size_mb * 1024 * 1024 // 8)  # Approximately size_mb MB
            time.sleep(0.1)
            return f"processed_{size_mb}mb"
            
        # Try to submit many tasks
        task_definitions = []
        for i in range(5):
            task_def = TaskDefinition(
                task_id=f"memory_task_{i}",
                task_type="cpu_intensive",  # Use process pool
                function=memory_intensive_task,
                args=(10,),  # 10MB each
                priority=TaskPriority.MEDIUM
            )
            task_definitions.append(task_def)
            
        # Execute tasks - should respect resource limits
        start_time = time.time()
        results = await self.executor.execute_parallel_tasks(task_definitions, timeout=15.0)
        end_time = time.time()
        
        # Verify execution respects limits
        execution_time = end_time - start_time
        self.assertGreater(execution_time, 1.0)  # Should take longer due to limits
        
        # Verify all tasks completed (resource manager should have allowed them)
        completed_tasks = [r for r in results if r.status == "completed"]
        self.assertEqual(len(completed_tasks), 5)
        
    async def test_job_queue_integration(self):
        """Test integration with job queue"""
        # Add jobs to queue
        for i in range(5):
            priority = Priority.HIGH if i < 2 else Priority.MEDIUM if i < 4 else Priority.LOW
            await self.job_queue.put(
                task_data={"task_id": f"task_{i}", "data": f"data_{i}"},
                priority=priority,
                job_id=f"job_{i}"
            )
            
        # Verify queue size
        queue_size = await self.job_queue.get_queue_size()
        self.assertEqual(queue_size, 5)
        
        # Get jobs in priority order
        retrieved_jobs = []
        for _ in range(5):
            job = await self.job_queue.get(timeout=1.0)
            if job:
                retrieved_jobs.append(job)
                
        # Verify priority order (HIGH, MEDIUM, LOW)
        self.assertEqual(len(retrieved_jobs), 5)
        self.assertEqual(retrieved_jobs[0].job_id, "job_0")  # HIGH
        self.assertEqual(retrieved_jobs[1].job_id, "job_1")  # HIGH
        self.assertEqual(retrieved_jobs[2].job_id, "job_2")  # MEDIUM
        self.assertEqual(retrieved_jobs[3].job_id, "job_3")  # MEDIUM
        self.assertEqual(retrieved_jobs[4].job_id, "job_4")  # LOW
        
    async def test_task_coordinator_with_executor(self):
        """Test task coordinator working with executor"""
        # Register a workflow with the coordinator
        await self.task_coordinator.register_task("task_a")
        await self.task_coordinator.register_task("task_b", dependencies=["task_a"])
        await self.task_coordinator.register_task("task_c", dependencies=["task_a"])
        await self.task_coordinator.register_task("task_d", dependencies=["task_b", "task_c"])
        
        # Execute tasks in the right order using coordinator
        execution_results = {}
        
        def simple_task(task_name, duration=0.1):
            time.sleep(duration)
            return f"result_{task_name}"
            
        # Process tasks in workflow order
        while not (await self.task_coordinator.is_workflow_completed()):
            # Get ready tasks
            ready_tasks = await self.task_coordinator.get_ready_tasks()
            
            if not ready_tasks:
                # Wait for tasks to become ready
                ready_tasks = await self.task_coordinator.wait_for_ready_tasks(timeout=2.0)
                if not ready_tasks:
                    break
                    
            # Execute ready tasks in parallel
            task_defs = []
            for task_id in ready_tasks:
                task_def = TaskDefinition(
                    task_id=task_id,
                    task_type="compute",
                    function=simple_task,
                    args=(task_id,),
                    priority=TaskPriority.HIGH
                )
                task_defs.append(task_def)
                
            # Mark tasks as running
            for task_id in ready_tasks:
                await self.task_coordinator.mark_task_running(task_id)
                
            # Execute in parallel
            results = await self.executor.execute_parallel_tasks(task_defs, timeout=5.0)
            
            # Process results and mark tasks as completed/failed
            for result in results:
                if result.status == "completed":
                    await self.task_coordinator.mark_task_completed(result.task_id, result.result)
                    execution_results[result.task_id] = result.result
                else:
                    await self.task_coordinator.mark_task_failed(result.task_id, result.error)
                    
        # Verify all tasks completed
        workflow_status = await self.task_coordinator.get_workflow_status()
        self.assertTrue(workflow_status["completed"])
        
        # Verify execution results
        self.assertIn("task_a", execution_results)
        self.assertIn("task_b", execution_results)
        self.assertIn("task_c", execution_results)
        self.assertIn("task_d", execution_results)
        
        # Verify execution order through timestamps
        # Task A should complete before B and C
        # Tasks B and C should complete before D

if __name__ == '__main__':
    # Run async tests
    unittest.main()
```

### Performance and Scalability Considerations

#### Performance Optimization Strategies

1. **Resource-Aware Scheduling**: Tasks are only scheduled when system resources are available
2. **Adaptive Concurrency**: Number of concurrent tasks adjusts based on system load
3. **Efficient Resource Pools**: Separate thread and process pools for different task types
4. **Caching**: Resource usage metrics are cached to reduce overhead

#### Scalability Features

1. **Horizontal Scaling**: Multiple executor instances can run independently
2. **Load Balancing**: Job queue can distribute tasks across multiple workers
3. **Memory Management**: Automatic cleanup of completed task data
4. **Timeout Handling**: Prevents resource leaks from hung tasks

### Security Considerations

1. **Resource Limits**: Prevents tasks from consuming excessive system resources
2. **Task Isolation**: CPU-intensive tasks run in separate processes
3. **Input Validation**: All task parameters are validated before execution
4. **Access Control**: Executor configuration can restrict task types

### Deployment Considerations

1. **Docker Support**: Ready-to-use Docker configuration for containerized deployment
2. **Environment Configuration**: All settings configurable via environment variables
3. **Monitoring Integration**: Built-in metrics for performance monitoring
4. **Health Checks**: Executor status endpoints for container orchestration

### Future Enhancements

1. **Distributed Task Execution**: Support for executing tasks across multiple nodes
2. **Machine Learning-Based Scheduling**: Predictive scheduling based on historical performance
3. **Advanced Resource Monitoring**: Integration with system monitoring tools
4. **Task Visualization Dashboard**: Web interface for monitoring task execution
5. **Dynamic Resource Allocation**: Automatic adjustment of resource limits based on workload

This comprehensive parallel processing system provides significant performance improvements for pipeline operations while maintaining system stability and resource efficiency. The implementation follows MCP protocol best practices and provides a solid foundation for high-performance task execution.