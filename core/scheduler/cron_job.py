import asyncio
from datetime import datetime
from typing import Any, Dict, Optional
from croniter import croniter

from .job import Job
from .job_status import JobStatus
from .job_types import JobType


class CronJob(Job):
    """A job that runs based on cron expressions."""
    
    def __init__(self, 
                 job_id: str,
                 job_name: str,
                 cron_expression: str,
                 callback: callable,
                 metadata: Optional[Dict[str, Any]] = None,
                 async_job: bool = False,
                 retry_count: int = 3,
                 retry_delay: float = 1.0,
                 exponential_backoff: bool = False):
        """
        Initialize a cron job.
        
        Args:
            job_id: Unique identifier for the job
            job_name: Human-readable name for the job
            cron_expression: Standard cron expression (e.g., "* * * * *")
            callback: Function to execute when the job runs
            metadata: Additional data about the job
            async_job: Whether this is an async job
            retry_count: Number of times to retry on failure
            retry_delay: Initial delay between retries (seconds)
            exponential_backoff: Whether to use exponential backoff for retries
        """
        # For cron jobs, we'll set scheduled_at to now and store the cron expression
        super().__init__(
            job_id=job_id,
            job_name=job_name,
            _job_type=JobType.CRON,
            scheduled_at=datetime.now(),
            metadata=metadata or {},
            async_job=async_job,
            retry_count=retry_count,
            retry_delay=retry_delay,
            exponential_backoff=exponential_backoff
        )
        
        self.cron_expression = cron_expression
        self.callback = callback
        # Precompute the cron iterator for performance
        self._cron_iter = croniter(cron_expression, datetime.now())
    
    def run(self) -> Optional[asyncio.Future]:
        """Execute the cron job."""
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
        from croniter import croniter
        import datetime as dt_module
        
        # Get the next run time using croniter
        cron = croniter(self.cron_expression, datetime.now())
        next_run = cron.get_next(dt_module.datetime)
        
        return next_run
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert job to dictionary for serialization."""
        data = super().to_dict()
        # Add cron-specific data
        data['cron_expression'] = self.cron_expression
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CronJob':
        """Create cron job from dictionary."""
        job = super().from_dict(data)
        # Create a new instance with the correct class type
        return cls(
            job_id=job.job_id,
            job_name=job.job_name,
            cron_expression=data['cron_expression'],
            callback=None,  # This would need to be handled specially
            metadata=job.metadata,
            async_job=job.async_job,
            retry_count=job.retry_count,
            retry_delay=job.retry_delay,
            exponential_backoff=job.exponential_backoff
        )
