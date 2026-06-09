import asyncio
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

from .job import Job
from .job_status import JobStatus
from .job_types import JobType


class IntervalJob(Job):
    """A job that runs at regular intervals."""
    
    def __init__(self, 
                 job_id: str,
                 job_name: str,
                 interval_seconds: int,
                 callback: callable,
                 start_at: Optional[datetime] = None,
                 metadata: Optional[Dict[str, Any]] = None,
                 async_job: bool = False,
                 retry_count: int = 3,
                 retry_delay: float = 1.0,
                 exponential_backoff: bool = False):
        """
        Initialize an interval job.
        
        Args:
            job_id: Unique identifier for the job
            job_name: Human-readable name for the job
            interval_seconds: How often to run the job (in seconds)
            callback: Function to execute when the job runs
            start_at: When to start the first run (defaults to now)
            metadata: Additional data about the job
            async_job: Whether this is an async job
            retry_count: Number of times to retry on failure
            retry_delay: Initial delay between retries (seconds)
            exponential_backoff: Whether to use exponential backoff for retries
        """
        # Set the scheduled_at based on start_at or now
        if start_at is None:
            start_at = datetime.now()
        
        super().__init__(
            job_id=job_id,
            job_name=job_name,
            _job_type=JobType.INTERVAL,
            scheduled_at=start_at,
            metadata=metadata or {},
            async_job=async_job,
            retry_count=retry_count,
            retry_delay=retry_delay,
            exponential_backoff=exponential_backoff
        )
        
        self.interval_seconds = interval_seconds
        self.callback = callback
    
    def run(self) -> Optional[asyncio.Future]:
        """Execute the interval job."""
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
        # Calculate next run time based on interval
        next_run = self.scheduled_at
        while next_run <= datetime.now():
            next_run += timedelta(seconds=self.interval_seconds)
            
        return next_run
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert job to dictionary for serialization."""
        data = super().to_dict()
        # Add interval-specific data
        data['interval_seconds'] = self.interval_seconds
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'IntervalJob':
        """Create interval job from dictionary."""
        job = super().from_dict(data)
        # Create a new instance with the correct class type
        return cls(
            job_id=job.job_id,
            job_name=job.job_name,
            interval_seconds=data['interval_seconds'],
            callback=None,  # This would need to be handled specially
            start_at=job.scheduled_at,
            metadata=job.metadata,
            async_job=job.async_job,
            retry_count=job.retry_count,
            retry_delay=job.retry_delay,
            exponential_backoff=job.exponential_backoff
        )
