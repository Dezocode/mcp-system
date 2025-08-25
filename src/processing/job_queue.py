#!/usr/bin/env python3
"""
Priority-based job queue for MCP pipeline
Manages task scheduling and prioritization
"""

import asyncio
import heapq
import time
import threading
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from enum import IntEnum
import logging

logger = logging.getLogger(__name__)


class Priority(IntEnum):
    """Task priority levels (lower number = higher priority)"""
    CRITICAL = 1
    HIGH = 2
    NORMAL = 3
    LOW = 4
    BACKGROUND = 5


@dataclass
class QueuedJob:
    """Job in the priority queue"""
    priority: Priority
    job_id: str
    job_type: str
    function: Callable
    args: tuple = ()
    kwargs: dict = None
    created_at: float = field(default_factory=time.time)
    timeout: Optional[float] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.kwargs is None:
            self.kwargs = {}
        if self.metadata is None:
            self.metadata = {}
    
    def __lt__(self, other):
        """Enable priority queue ordering"""
        if self.priority != other.priority:
            return self.priority < other.priority
        # If same priority, use creation time (FIFO)
        return self.created_at < other.created_at


@dataclass 
class JobResult:
    """Result of job execution"""
    job_id: str
    status: str
    result: Any = None
    error: Optional[str] = None
    execution_time: float = 0.0
    started_at: float = 0.0
    completed_at: float = 0.0
    queue_time: float = 0.0


class JobQueue:
    """Priority-based job queue with async execution"""
    
    def __init__(self, max_concurrent_jobs: int = 3):
        self.max_concurrent_jobs = max_concurrent_jobs
        
        # Priority queue using heap
        self._queue: List[QueuedJob] = []
        self._queue_lock = threading.RLock()
        
        # Job tracking
        self.pending_jobs: Dict[str, QueuedJob] = {}
        self.running_jobs: Dict[str, asyncio.Task] = {}
        self.completed_jobs: Dict[str, JobResult] = {}
        
        # Statistics
        self.stats = {
            "total_jobs_queued": 0,
            "total_jobs_completed": 0,
            "total_jobs_failed": 0,
            "average_queue_time": 0.0,
            "average_execution_time": 0.0
        }
        
        # Queue management
        self._running = False
        self._worker_task: Optional[asyncio.Task] = None
        
        logger.info(f"JobQueue initialized with max {max_concurrent_jobs} concurrent jobs")
    
    def add_job(self, job: QueuedJob) -> str:
        """Add job to priority queue"""
        with self._queue_lock:
            heapq.heappush(self._queue, job)
            self.pending_jobs[job.job_id] = job
            self.stats["total_jobs_queued"] += 1
        
        logger.debug(f"Added job {job.job_id} with priority {job.priority.name}")
        return job.job_id
    
    def add_pipeline_job(
        self, 
        job_id: str, 
        job_type: str, 
        function: Callable, 
        priority: Priority = Priority.NORMAL,
        timeout: Optional[float] = None,
        **kwargs
    ) -> str:
        """Convenience method to add a pipeline job"""
        job = QueuedJob(
            priority=priority,
            job_id=job_id,
            job_type=job_type,
            function=function,
            kwargs=kwargs,
            timeout=timeout,
            metadata={"job_type": job_type}
        )
        return self.add_job(job)
    
    async def start_processing(self):
        """Start processing jobs from the queue"""
        if self._running:
            logger.warning("Job queue already running")
            return
        
        self._running = True
        self._worker_task = asyncio.create_task(self._process_jobs())
        logger.info("Started job queue processing")
    
    async def stop_processing(self):
        """Stop processing jobs"""
        self._running = False
        
        if self._worker_task:
            self._worker_task.cancel()
            try:
                await self._worker_task
            except asyncio.CancelledError:
                pass
        
        # Cancel all running jobs
        for job_id, task in list(self.running_jobs.items()):
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
        
        logger.info("Stopped job queue processing")
    
    async def _process_jobs(self):
        """Main job processing loop"""
        while self._running:
            try:
                # Check if we can start more jobs
                if len(self.running_jobs) < self.max_concurrent_jobs:
                    job = self._get_next_job()
                    if job:
                        await self._start_job(job)
                
                # Brief pause to prevent busy waiting
                await asyncio.sleep(0.1)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in job processing loop: {e}")
                await asyncio.sleep(1)
    
    def _get_next_job(self) -> Optional[QueuedJob]:
        """Get next job from priority queue"""
        with self._queue_lock:
            if not self._queue:
                return None
            
            job = heapq.heappop(self._queue)
            if job.job_id in self.pending_jobs:
                del self.pending_jobs[job.job_id]
                return job
            
            # Job was already processed or cancelled
            return None
    
    async def _start_job(self, job: QueuedJob):
        """Start executing a job"""
        task = asyncio.create_task(self._execute_job(job))
        self.running_jobs[job.job_id] = task
        
        logger.debug(f"Started job {job.job_id}")
        
        # Set up task completion callback
        task.add_done_callback(lambda t: self._job_completed(job.job_id, t))
    
    async def _execute_job(self, job: QueuedJob) -> JobResult:
        """Execute a single job"""
        result = JobResult(
            job_id=job.job_id,
            status="running",
            started_at=time.time(),
            queue_time=time.time() - job.created_at
        )
        
        try:
            logger.debug(f"Executing job {job.job_id} ({job.job_type})")
            
            # Execute the job function
            if asyncio.iscoroutinefunction(job.function):
                job_result = await job.function(*job.args, **job.kwargs)
            else:
                # Run sync function in thread pool
                loop = asyncio.get_event_loop()
                job_result = await loop.run_in_executor(
                    None, 
                    lambda: job.function(*job.args, **job.kwargs)
                )
            
            result.result = job_result
            result.status = "completed"
            result.completed_at = time.time()
            result.execution_time = result.completed_at - result.started_at
            
            logger.debug(f"Completed job {job.job_id} in {result.execution_time:.2f}s")
            
        except asyncio.CancelledError:
            result.status = "cancelled"
            result.error = "Job was cancelled"
            logger.info(f"Job {job.job_id} was cancelled")
            
        except Exception as e:
            result.status = "failed"
            result.error = str(e)
            result.completed_at = time.time()
            result.execution_time = result.completed_at - result.started_at
            logger.error(f"Job {job.job_id} failed: {e}")
        
        return result
    
    def _job_completed(self, job_id: str, task: asyncio.Task):
        """Callback when job completes"""
        try:
            result = task.result()
            self.completed_jobs[job_id] = result
            
            # Update statistics
            if result.status == "completed":
                self.stats["total_jobs_completed"] += 1
            elif result.status == "failed":
                self.stats["total_jobs_failed"] += 1
            
            # Update average times
            completed_results = [r for r in self.completed_jobs.values() 
                               if r.status in ["completed", "failed"]]
            
            if completed_results:
                self.stats["average_queue_time"] = sum(r.queue_time for r in completed_results) / len(completed_results)
                self.stats["average_execution_time"] = sum(r.execution_time for r in completed_results) / len(completed_results)
            
        except Exception as e:
            logger.error(f"Error processing job completion for {job_id}: {e}")
        finally:
            # Clean up
            if job_id in self.running_jobs:
                del self.running_jobs[job_id]
    
    def get_queue_status(self) -> Dict[str, Any]:
        """Get current queue status"""
        with self._queue_lock:
            return {
                "queue_size": len(self._queue),
                "pending_jobs": len(self.pending_jobs),
                "running_jobs": len(self.running_jobs),
                "completed_jobs": len(self.completed_jobs),
                "max_concurrent": self.max_concurrent_jobs,
                "is_processing": self._running,
                "statistics": self.stats.copy()
            }
    
    def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get status of specific job"""
        if job_id in self.pending_jobs:
            job = self.pending_jobs[job_id]
            return {
                "job_id": job_id,
                "status": "pending",
                "priority": job.priority.name,
                "job_type": job.job_type,
                "queued_at": job.created_at,
                "queue_time": time.time() - job.created_at
            }
        
        if job_id in self.running_jobs:
            return {
                "job_id": job_id,
                "status": "running",
                "started_at": time.time()  # Approximate
            }
        
        if job_id in self.completed_jobs:
            result = self.completed_jobs[job_id]
            return {
                "job_id": job_id,
                "status": result.status,
                "result": result.result,
                "error": result.error,
                "execution_time": result.execution_time,
                "queue_time": result.queue_time,
                "completed_at": result.completed_at
            }
        
        return None
    
    def cancel_job(self, job_id: str) -> bool:
        """Cancel a pending or running job"""
        # Cancel pending job
        if job_id in self.pending_jobs:
            with self._queue_lock:
                del self.pending_jobs[job_id]
                # Remove from heap queue (expensive operation)
                self._queue = [job for job in self._queue if job.job_id != job_id]
                heapq.heapify(self._queue)
            logger.info(f"Cancelled pending job {job_id}")
            return True
        
        # Cancel running job
        if job_id in self.running_jobs:
            task = self.running_jobs[job_id]
            task.cancel()
            logger.info(f"Cancelled running job {job_id}")
            return True
        
        return False
    
    def get_jobs_by_priority(self, priority: Priority) -> List[Dict[str, Any]]:
        """Get all jobs with specific priority"""
        jobs = []
        
        # Pending jobs
        with self._queue_lock:
            for job in self._queue:
                if job.priority == priority:
                    jobs.append({
                        "job_id": job.job_id,
                        "status": "pending",
                        "job_type": job.job_type,
                        "created_at": job.created_at
                    })
        
        # Running jobs (we don't store priority info for running jobs in this simple implementation)
        # In a production system, you'd want to maintain this info
        
        # Completed jobs with matching priority
        for job_id, result in self.completed_jobs.items():
            # Note: We'd need to store priority in JobResult for this to work properly
            pass
        
        return jobs
    
    def clear_completed_jobs(self, keep_last: int = 100):
        """Clear completed jobs, keeping only the most recent ones"""
        if len(self.completed_jobs) <= keep_last:
            return
        
        # Sort by completion time and keep only the most recent
        sorted_jobs = sorted(
            self.completed_jobs.items(),
            key=lambda x: x[1].completed_at,
            reverse=True
        )
        
        self.completed_jobs = dict(sorted_jobs[:keep_last])
        logger.info(f"Cleared old completed jobs, keeping {keep_last} most recent")
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get detailed performance metrics"""
        current_time = time.time()
        
        # Calculate throughput
        completed_count = self.stats["total_jobs_completed"]
        failed_count = self.stats["total_jobs_failed"]
        total_processed = completed_count + failed_count
        
        success_rate = (completed_count / total_processed * 100) if total_processed > 0 else 0
        
        # Calculate queue efficiency
        avg_queue_time = self.stats["average_queue_time"]
        avg_execution_time = self.stats["average_execution_time"]
        
        efficiency = (avg_execution_time / (avg_queue_time + avg_execution_time) * 100) if (avg_queue_time + avg_execution_time) > 0 else 0
        
        return {
            "throughput": {
                "total_jobs_processed": total_processed,
                "jobs_completed": completed_count,
                "jobs_failed": failed_count,
                "success_rate": success_rate
            },
            "timing": {
                "average_queue_time": avg_queue_time,
                "average_execution_time": avg_execution_time,
                "queue_efficiency": efficiency
            },
            "current_load": {
                "pending_jobs": len(self.pending_jobs),
                "running_jobs": len(self.running_jobs),
                "queue_utilization": len(self.running_jobs) / self.max_concurrent_jobs * 100
            }
        }