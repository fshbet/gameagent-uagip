import asyncio
from datetime import datetime
from typing import Any, Dict, Optional

from .job import Job
from .job_status import JobStatus
from .job_types import JobType


class OneTimeJob(Job):
    """A job that runs once at a specified datetime."""
    
    def __init__(self, 
                 job_id: str,
                 job_name: str,
                 scheduled_at: datetime,
                 callback: callable,
                 metadata: Optional[Dict[str, Any]] = None,
                 async_job: bool = False,
                 retry_count: int = 3,
                 retry_delay: float = 1.0,
                 exponential_backoff: bool = False):
        """
        Initialize a one-time job.
        
        Args:
            job_id: Unique identifier for the job
            job_name: Human-readable name for the job
            scheduled_at: When to run the job
            callback: Function to execute when the job runs
            metadata: Additional data about the job
            async_job: Whether this is an async job
            retry_count: Number of times to retry on failure
            retry_delay: Initial delay between retries (seconds)
            exponential_backoff: Whether to use exponential backoff for retries
        """
        super().__init__(
            job_id=job_id,
            job_name=job_name,
            _job_type=JobType.ONE_TIME,
            scheduled_at=scheduled_at,
            metadata=metadata or {},
            async_job=async_job,
            retry_count=retry_count,
            retry_delay=retry_delay,
            exponential_backoff=exponential_backoff
        )
        
        self.callback = callback
    
    def run(self) -> Optional[asyncio.Future]:
        """Execute the one-time job."""
        self.status = JobStatus.RUNNING
        
        if self.async_job:
            # For async jobs, we return a Future that can be awaited
            async def async_run():
                try:
                    result = await self.callback()
                    self.status = JobStatus.COMPLETED
                    return result
                except Exception as e:
                    self.retries += 1
                    if self.retries <= self.retry_count:
                        self.status = JobStatus.RETRYING
                        # Implement retry logic here
                        raise e
                    else:
                        self.status = JobStatus.FAILED
                        raise e
            
            return asyncio.ensure_future(async_run())
        else:
            # For sync jobs
            try:
                result = self.callback()
                self.status = JobStatus.COMPLETED
                return result
            except Exception as e:
                self.retries += 1
                if self.retries <= self.retry_count:
                    self.status = JobStatus.RETRYING
                    # Implement retry logic here
                    raise e
                else:
                    self.status = JobStatus.FAILED
                    raise e
    
    def get_next_run_time(self) -> datetime:
        """Get the next time this job should run.
        
        Returns:
            The next run time
        """
        return self.scheduled_at
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert job to dictionary for serialization."""
        data = super().to_dict()
        # Add any one-time specific data if needed
        return data