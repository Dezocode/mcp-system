"""
Parallel processing engine for MCP pipeline
Implements 3x speed improvement through concurrent execution
"""

from .job_queue import JobQueue, Priority
from .parallel_executor import ParallelExecutor

__all__ = ["ParallelExecutor", "JobQueue", "Priority"]
