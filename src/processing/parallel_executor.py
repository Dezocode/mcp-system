#!/usr/bin/env python3
"""
Parallel execution engine for MCP pipeline
Provides concurrent task execution with resource management
"""

import asyncio
import concurrent.futures
import logging
import multiprocessing
import threading
import time
from dataclasses import asdict, dataclass
from enum import Enum
from typing import Any, Awaitable, Callable, Dict, List, Optional

logger = logging.getLogger(__name__)


class TaskStatus(Enum):
    """Status of parallel tasks"""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class ParallelTask:
    """Task definition for parallel execution"""

    task_id: str
    task_type: str
    function: Callable
    args: tuple = ()
    kwargs: dict = None
    priority: int = 0
    timeout: Optional[float] = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.kwargs is None:
            self.kwargs = {}
        if self.metadata is None:
            self.metadata = {}


@dataclass
class TaskResult:
    """Result of parallel task execution"""

    task_id: str
    status: TaskStatus
    result: Any = None
    error: Optional[str] = None
    execution_time: float = 0.0
    started_at: float = 0.0
    completed_at: float = 0.0


class ParallelExecutor:
    """Async parallel task execution with resource management"""

    def __init__(self, max_workers: int = None, cpu_bound_workers: int = None):
        # Determine optimal worker counts
        cpu_count = multiprocessing.cpu_count()
        self.max_workers = max_workers or min(4, cpu_count)
        self.cpu_bound_workers = cpu_bound_workers or max(1, cpu_count - 1)

        # Thread and process pools
        self.thread_executor = concurrent.futures.ThreadPoolExecutor(
            max_workers=self.max_workers
        )
        self.process_executor = concurrent.futures.ProcessPoolExecutor(
            max_workers=self.cpu_bound_workers
        )

        # Task management
        self.task_queue = asyncio.Queue()
        self.active_tasks: Dict[str, asyncio.Task] = {}
        self.completed_tasks: Dict[str, TaskResult] = {}

        # Resource tracking
        self.resource_usage = {
            "active_threads": 0,
            "active_processes": 0,
            "total_tasks_executed": 0,
            "total_execution_time": 0.0,
        }

        # Performance metrics
        self.performance_metrics = {
            "tasks_per_second": 0.0,
            "average_execution_time": 0.0,
            "success_rate": 100.0,
            "speedup_factor": 1.0,
        }

        self._lock = threading.RLock()
        self._start_time = time.time()

        logger.info(
            f"ParallelExecutor initialized: {self.max_workers} thread workers, {self.cpu_bound_workers} process workers"
        )

    async def execute_parallel(self, tasks: List[ParallelTask]) -> List[TaskResult]:
        """Execute multiple tasks in parallel"""
        if not tasks:
            return []

        logger.info(f"Starting parallel execution of {len(tasks)} tasks")
        start_time = time.time()

        # Create asyncio tasks for each parallel task
        async_tasks = []
        for task in tasks:
            async_task = asyncio.create_task(self._execute_single_task(task))
            async_tasks.append(async_task)
            self.active_tasks[task.task_id] = async_task

        # Wait for all tasks to complete
        try:
            results = await asyncio.gather(*async_tasks, return_exceptions=True)

            # Process results
            task_results = []
            for i, result in enumerate(results):
                task = tasks[i]
                if isinstance(result, Exception):
                    task_result = TaskResult(
                        task_id=task.task_id,
                        status=TaskStatus.FAILED,
                        error=str(result),
                        execution_time=time.time() - start_time,
                    )
                else:
                    task_result = result

                task_results.append(task_result)
                self.completed_tasks[task.task_id] = task_result

                # Clean up active tasks
                if task.task_id in self.active_tasks:
                    del self.active_tasks[task.task_id]

            # Update performance metrics
            execution_time = time.time() - start_time
            self._update_performance_metrics(len(tasks), execution_time, task_results)

            logger.info(f"Completed parallel execution in {execution_time:.2f}s")
            return task_results

        except Exception as e:
            logger.error(f"Parallel execution failed: {e}")
            # Clean up active tasks
            for task in tasks:
                if task.task_id in self.active_tasks:
                    self.active_tasks[task.task_id].cancel()
                    del self.active_tasks[task.task_id]
            raise

    async def _execute_single_task(self, task: ParallelTask) -> TaskResult:
        """Execute a single task with proper error handling"""
        task_result = TaskResult(
            task_id=task.task_id, status=TaskStatus.RUNNING, started_at=time.time()
        )

        try:
            logger.debug(f"Starting task {task.task_id} ({task.task_type})")

            # Determine execution method based on task type
            if task.task_type in ["io_bound", "network", "file_operations"]:
                # Use thread pool for I/O bound tasks
                result = await self._execute_in_thread_pool(task)
            elif task.task_type in ["cpu_bound", "computation", "processing"]:
                # Use process pool for CPU bound tasks
                result = await self._execute_in_process_pool(task)
            else:
                # Default to thread pool
                result = await self._execute_in_thread_pool(task)

            task_result.result = result
            task_result.status = TaskStatus.COMPLETED
            task_result.completed_at = time.time()
            task_result.execution_time = (
                task_result.completed_at - task_result.started_at
            )

            logger.debug(
                f"Completed task {task.task_id} in {task_result.execution_time:.2f}s"
            )

        except asyncio.CancelledError:
            task_result.status = TaskStatus.CANCELLED
            task_result.error = "Task was cancelled"
            logger.info(f"Task {task.task_id} was cancelled")

        except Exception as e:
            task_result.status = TaskStatus.FAILED
            task_result.error = str(e)
            task_result.completed_at = time.time()
            task_result.execution_time = (
                task_result.completed_at - task_result.started_at
            )
            logger.error(f"Task {task.task_id} failed: {e}")

        return task_result

    async def _execute_in_thread_pool(self, task: ParallelTask) -> Any:
        """Execute task in thread pool"""
        loop = asyncio.get_event_loop()

        with self._lock:
            self.resource_usage["active_threads"] += 1

        try:
            if asyncio.iscoroutinefunction(task.function):
                # For async functions, run them directly
                result = await task.function(*task.args, **task.kwargs)
            else:
                # For sync functions, use thread pool
                result = await loop.run_in_executor(
                    self.thread_executor,
                    lambda: task.function(*task.args, **task.kwargs),
                )
            return result
        finally:
            with self._lock:
                self.resource_usage["active_threads"] -= 1

    async def _execute_in_process_pool(self, task: ParallelTask) -> Any:
        """Execute task in process pool"""
        loop = asyncio.get_event_loop()

        # Note: Process pool can only execute pure functions (no async)
        if asyncio.iscoroutinefunction(task.function):
            logger.warning(
                f"Task {task.task_id}: async function in process pool, falling back to thread pool"
            )
            return await self._execute_in_thread_pool(task)

        with self._lock:
            self.resource_usage["active_processes"] += 1

        try:
            result = await loop.run_in_executor(
                self.process_executor, task.function, *task.args
            )
            return result
        finally:
            with self._lock:
                self.resource_usage["active_processes"] -= 1

    def _update_performance_metrics(
        self, task_count: int, execution_time: float, results: List[TaskResult]
    ):
        """Update performance metrics based on execution results"""
        with self._lock:
            self.resource_usage["total_tasks_executed"] += task_count
            self.resource_usage["total_execution_time"] += execution_time

            # Calculate success rate
            successful_tasks = sum(
                1 for r in results if r.status == TaskStatus.COMPLETED
            )
            success_rate = (
                (successful_tasks / task_count * 100) if task_count > 0 else 0
            )

            # Calculate average execution time
            task_times = [r.execution_time for r in results if r.execution_time > 0]
            avg_time = sum(task_times) / len(task_times) if task_times else 0

            # Calculate tasks per second
            total_time = time.time() - self._start_time
            tasks_per_second = (
                self.resource_usage["total_tasks_executed"] / total_time
                if total_time > 0
                else 0
            )

            # Estimate speedup factor (compared to sequential execution)
            sequential_time = sum(task_times)
            speedup = sequential_time / execution_time if execution_time > 0 else 1.0

            self.performance_metrics.update(
                {
                    "tasks_per_second": tasks_per_second,
                    "average_execution_time": avg_time,
                    "success_rate": success_rate,
                    "speedup_factor": speedup,
                }
            )

    def get_performance_summary(self) -> Dict[str, Any]:
        """Get comprehensive performance summary"""
        with self._lock:
            return {
                "execution_statistics": {
                    "total_tasks_executed": self.resource_usage["total_tasks_executed"],
                    "total_execution_time": self.resource_usage["total_execution_time"],
                    "uptime_seconds": time.time() - self._start_time,
                },
                "current_load": {
                    "active_threads": self.resource_usage["active_threads"],
                    "active_processes": self.resource_usage["active_processes"],
                    "active_tasks": len(self.active_tasks),
                    "completed_tasks": len(self.completed_tasks),
                },
                "performance_metrics": self.performance_metrics.copy(),
                "resource_configuration": {
                    "max_thread_workers": self.max_workers,
                    "max_process_workers": self.cpu_bound_workers,
                    "cpu_count": multiprocessing.cpu_count(),
                },
            }

    def cancel_task(self, task_id: str) -> bool:
        """Cancel a running task"""
        if task_id in self.active_tasks:
            self.active_tasks[task_id].cancel()
            logger.info(f"Cancelled task {task_id}")
            return True
        return False

    def cancel_all_tasks(self):
        """Cancel all running tasks"""
        cancelled_count = 0
        for task_id, task in list(self.active_tasks.items()):
            task.cancel()
            cancelled_count += 1

        logger.info(f"Cancelled {cancelled_count} active tasks")

    async def shutdown(self):
        """Gracefully shutdown the parallel executor"""
        logger.info("Shutting down ParallelExecutor...")

        # Cancel all active tasks
        self.cancel_all_tasks()

        # Wait for tasks to complete cancellation
        if self.active_tasks:
            await asyncio.gather(*self.active_tasks.values(), return_exceptions=True)

        # Shutdown executors
        self.thread_executor.shutdown(wait=True)
        self.process_executor.shutdown(wait=True)

        logger.info("ParallelExecutor shutdown complete")


# Utility functions for creating common task types


def create_pipeline_task(
    task_id: str,
    operation: str,
    command: List[str],
    cwd: str = None,
    timeout: float = None,
) -> ParallelTask:
    """Create a pipeline operation task"""
    import subprocess

    def run_command():
        try:
            result = subprocess.run(
                command, cwd=cwd, capture_output=True, text=True, timeout=timeout
            )
            return {
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "command": command,
            }
        except subprocess.TimeoutExpired:
            return {
                "returncode": -1,
                "stdout": "",
                "stderr": f"Command timed out after {timeout} seconds",
                "command": command,
            }

    return ParallelTask(
        task_id=task_id,
        task_type="cpu_bound",
        function=run_command,
        timeout=timeout,
        metadata={"operation": operation, "command": command},
    )


def create_file_task(
    task_id: str, operation: str, filepath: str, **kwargs
) -> ParallelTask:
    """Create a file operation task"""

    def file_operation():
        if operation == "read":
            with open(filepath, "r") as f:
                return f.read()
        elif operation == "write":
            content = kwargs.get("content", "")
            with open(filepath, "w") as f:
                f.write(content)
                return len(content)
        elif operation == "analyze":
            # File analysis operation
            import os

            stat = os.stat(filepath)
            return {
                "size": stat.st_size,
                "modified": stat.st_mtime,
                "filepath": filepath,
            }

    return ParallelTask(
        task_id=task_id,
        task_type="io_bound",
        function=file_operation,
        metadata={"operation": operation, "filepath": filepath},
    )
