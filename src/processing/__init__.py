"""
Parallel processing engine for MCP pipeline
Implements 3x speed improvement through concurrent execution
"""

from .parallel_executor import ParallelExecutor
from .job_queue import JobQueue, Priority

__all__ = ['ParallelExecutor', 'JobQueue', 'Priority']