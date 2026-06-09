import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, Optional, Union

from .job_status import JobStatus
from .job_types import JobType


@dataclass
class Job:
    """Base class for all jobs."""
    
    job_id: str
    job_name: str
    _job_type: JobType
    created_at: datetime = field(default_factory=datetime.now)
    scheduled_at: Optional[datetime] = None
    status: JobStatus = JobStatus.PENDING
    retries: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    async_job: bool = False
    retry_count: int = 3
    retry_delay: float = 1.0
    exponential_backoff: bool = False
    
    @property
    def job_type(self) -> str:
        """Return the job type as a string value."""
        return self._job_type.value
    
    def __post_init__(self):
        """Initialize the job after creation."""
        if self.scheduled_at is None:
            self.scheduled_at = self.created_at
    
    def run(self) -> Union[None, asyncio.Future]:
        """Execute the job.
        
        Returns:
            None or asyncio.Future depending on whether it's async
        """
        # This method will be overridden by subclasses
        raise NotImplementedError("Subclasses must implement run method")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert job to dictionary for serialization."""
        return {
            'job_id': self.job_id,
            'job_name': self.job_name,
            'job_type': self._job_type.value,
            'created_at': self.created_at.isoformat(),
            'scheduled_at': self.scheduled_at.isoformat() if self.scheduled_at else None,
            'status': self.status.value,
            'retries': self.retries,
            'metadata': self.metadata,
            'async_job': self.async_job,
            'retry_count': self.retry_count,
            'retry_delay': self.retry_delay,
            'exponential_backoff': self.exponential_backoff
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Job':
        """Create job from dictionary."""
        # Convert back to proper types
        job_type = JobType(data['job_type'])
        created_at = datetime.fromisoformat(data['created_at'])
        scheduled_at = datetime.fromisoformat(data['scheduled_at']) if data['scheduled_at'] else None
        status = JobStatus(data['status'])
        
        return cls(
            job_id=data['job_id'],
            job_name=data['job_name'],
            _job_type=job_type,
            created_at=created_at,
            scheduled_at=scheduled_at,
            status=status,
            retries=data['retries'],
            metadata=data['metadata'],
            async_job=data['async_job'],
            retry_count=data['retry_count'],
            retry_delay=data['retry_delay'],
            exponential_backoff=data['exponential_backoff']
        )
