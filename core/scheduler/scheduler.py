import asyncio
import logging
import threading
import time
from datetime import datetime
from typing import Dict, List, Optional, Union, Any
from concurrent.futures import ThreadPoolExecutor

from .job import Job
from .job_status import JobStatus
from .job_types import JobType
from .one_time_job import OneTimeJob
from .interval_job import IntervalJob
from .cron_job import CronJob
from ..events.event_bus import EventBus
from ..events.event_types import EventType
from ..events.event import Event


class Scheduler:
    """Main scheduler class for managing jobs."""
    
    def __init__(self):
        """Initialize the scheduler."""
        self._jobs: Dict[str, Job] = {}
        self._running = False
        self._executor = ThreadPoolExecutor(max_workers=10)
        self._lock = threading.RLock()  # For thread safety
        self._logger = logging.getLogger(__name__)
        self._event_bus = EventBus()
        
        # Statistics tracking
        self._total_jobs = 0
        self._completed_jobs = 0
        self._failed_jobs = 0
        self._running_jobs = 0
        self._start_time = datetime.now()
    
    def schedule_job(self, job: Job) -> str:
        """Schedule a job for execution.
        
        Args:
            job: The job to schedule
            
        Returns:
            The job ID
        """
        with self._lock:
            job_id = job.job_id
            self._jobs[job_id] = job
            self._total_jobs += 1
            self._logger.info(f"Scheduled job {job_id}: {job.job_name}")
            return job_id
    
    def cancel_job(self, job_id: str) -> bool:
        """Cancel a scheduled job.
        
        Args:
            job_id: The ID of the job to cancel
            
        Returns:
            True if job was cancelled, False if not found
        """
        with self._lock:
            if job_id in self._jobs:
                job = self._jobs[job_id]
                if job.status != JobStatus.COMPLETED and job.status != JobStatus.FAILED:
                    job.status = JobStatus.CANCELLED
                    del self._jobs[job_id]
                    self._logger.info(f"Cancelled job {job_id}: {job.job_name}")
                    return True
            return False
    
    def pause_job(self, job_id: str) -> bool:
        """Pause a running job.
        
        Args:
            job_id: The ID of the job to pause
            
        Returns:
            True if job was paused, False if not found or already paused
        """
        with self._lock:
            if job_id in self._jobs:
                job = self._jobs[job_id]
                if job.status == JobStatus.RUNNING:
                    # In a real implementation, this would actually pause execution
                    # For now we'll just mark it as paused
                    job.status = JobStatus.PENDING
                    self._logger.info(f"Paused job {job_id}: {job.job_name}")
                    return True
            return False
    
    def resume_job(self, job_id: str) -> bool:
        """Resume a paused job.
        
        Args:
            job_id: The ID of the job to resume
            
        Returns:
            True if job was resumed, False if not found or not paused
        """
        with self._lock:
            if job_id in self._jobs:
                job = self._jobs[job_id]
                if job.status == JobStatus.PENDING:
                    # In a real implementation, this would actually resume execution
                    # For now we'll just mark it as pending again
                    job.status = JobStatus.PENDING
                    self._logger.info(f"Resumed job {job_id}: {job.job_name}")
                    return True
            return False
    
    def get_job(self, job_id: str) -> Optional[Job]:
        """Get a job by ID.
        
        Args:
            job_id: The ID of the job to retrieve
            
        Returns:
            The job if found, None otherwise
        """
        with self._lock:
            return self._jobs.get(job_id)
    
    def list_jobs(self) -> List[Job]:
        """Get a list of all scheduled jobs.
        
        Returns:
            A list of all jobs
        """
        with self._lock:
            return list(self._jobs.values())
    
    def get_statistics(self) -> Dict[str, int]:
        """Get scheduler statistics.
        
        Returns:
            Dictionary with statistics
        """
        with self._lock:
            return {
                'total_jobs': self._total_jobs,
                'completed_jobs': self._completed_jobs,
                'failed_jobs': self._failed_jobs,
                'running_jobs': self._running_jobs,
                'uptime': int((datetime.now() - self._start_time).total_seconds())
            }
    
    def start(self):
        """Start the scheduler."""
        with self._lock:
            if not self._running:
                self._running = True
                self._logger.info("Scheduler started")
    
    def stop(self):
        """Stop the scheduler."""
        with self._lock:
            if self._running:
                self._running = False
                self._executor.shutdown(wait=True)
                self._logger.info("Scheduler stopped")
    
    def run_job(self, job_id: str) -> bool:
        """Run a specific job.
        
        Args:
            job_id: The ID of the job to run
            
        Returns:
            True if job was executed successfully, False otherwise
        """
        with self._lock:
            if job_id in self._jobs:
                job = self._jobs[job_id]
                try:
                    # Publish JOB_STARTED event
                    event = Event(
                        event_type=EventType.JOB_STARTED,
                        payload={
                            'job_id': job_id,
                            'job_name': job.job_name,
                            'job_type': job.job_type
                        }
                    )
                    self._event_bus.publish(event)
                    
                    # Execute the job
                    if job.async_job:
                        # For async jobs, we need to run them in an event loop
                        # Create a new event loop for this execution
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                        try:
                            result = loop.run_until_complete(job.run())
                        finally:
                            loop.close()
                    else:
                        # For sync jobs, execute directly
                        result = job.run()
                    
                    # Update statistics - check the final status of the job
                    # The job's run() method should have set the correct status
                    if job.status == JobStatus.COMPLETED:
                        self._completed_jobs += 1
                        # Publish JOB_COMPLETED event
                        event = Event(
                            event_type=EventType.JOB_COMPLETED,
                            payload={
                                'job_id': job_id,
                                'job_name': job.job_name
                            }
                        )
                        self._event_bus.publish(event)
                    elif job.status == JobStatus.FAILED:
                        self._failed_jobs += 1
                        # Publish JOB_FAILED event
                        event = Event(
                            event_type=EventType.JOB_FAILED,
                            payload={
                                'job_id': job_id,
                                'job_name': job.job_name,
                                'error': 'Job failed'
                            }
                        )
                        self._event_bus.publish(event)
                    
                    self._logger.info(f"Job {job_id} completed: {job.job_name}")
                    return True
                except Exception as e:
                    # If an exception occurs during execution, the job should be marked as FAILED
                    job.status = JobStatus.FAILED
                    self._failed_jobs += 1
                    # Publish JOB_FAILED event
                    self._event_bus.publish(EventType.JOB_FAILED, {
                        'job_id': job_id,
                        'job_name': job.job_name,
                        'error': str(e)
                    })
                    self._logger.error(f"Job {job_id} failed: {str(e)}")
                    return False
            return False
    
    def run_pending_jobs(self):
        """Run all pending jobs that are due to execute."""
        with self._lock:
            current_time = datetime.now()
            jobs_to_run = []
            
            # Identify which jobs should run now
            for job in self._jobs.values():
                if job.status == JobStatus.PENDING:
                    if job.job_type == JobType.ONE_TIME:
                        # One-time jobs run once at a specific time
                        if job.scheduled_at <= current_time:
                            jobs_to_run.append(job)
                    elif job.job_type == JobType.INTERVAL:
                        # Interval jobs run based on their interval
                        next_run = job.get_next_run_time()
                        if next_run <= current_time:
                            jobs_to_run.append(job)
                    elif job.job_type == JobType.CRON:
                        # Cron jobs run based on cron expression
                        next_run = job.get_next_run_time()
                        if next_run <= current_time:
                            jobs_to_run.append(job)
            
            # Run identified jobs
            for job in jobs_to_run:
                # Set the job status to running before executing it
                job.status = JobStatus.RUNNING
                # Publish JOB_STARTED event
                event = Event(
                    event_type=EventType.JOB_STARTED,
                    payload={
                        'job_id': job.job_id,
                        'job_name': job.job_name,
                        'job_type': job.job_type
                    }
                )
                self._event_bus.publish(event)
                
                # Execute the job properly based on whether it's async or sync
                try:
                    if job.async_job:
                        # For async jobs, we need to run them in an event loop
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                        try:
                            result = loop.run_until_complete(job.run())
                        finally:
                            loop.close()
                    else:
                        # For sync jobs, execute directly
                        result = job.run()
                    
                    # Update statistics and publish events after successful execution
                    if job.status == JobStatus.COMPLETED:
                        self._completed_jobs += 1
                        # Publish JOB_COMPLETED event
                        event = Event(
                            event_type=EventType.JOB_COMPLETED,
                            payload={
                                'job_id': job.job_id,
                                'job_name': job.job_name
                            }
                        )
                        self._event_bus.publish(event)
                    elif job.status == JobStatus.FAILED:
                        self._failed_jobs += 1
                        # Publish JOB_FAILED event
                        event = Event(
                            event_type=EventType.JOB_FAILED,
                            payload={
                                'job_id': job.job_id,
                                'job_name': job.job_name,
                                'error': 'Job failed'
                            }
                        )
                        self._event_bus.publish(event)
                        
                except Exception as e:
                    # If an exception occurs during execution, the job should be marked as FAILED
                    job.status = JobStatus.FAILED
                    self._failed_jobs += 1
                    # Publish JOB_FAILED event
                    self._event_bus.publish(EventType.JOB_FAILED, {
                        'job_id': job.job_id,
                        'job_name': job.job_name,
                        'error': str(e)
                    })
                    self._logger.error(f"Job {job.job_id} failed: {str(e)}")
    
    def add_one_time_job(self, 
                        job_name: str,
                        scheduled_at: datetime,
                        callback: callable,
                        metadata: Optional[Dict[str, Any]] = None,
                        async_job: bool = False,
                        retry_count: int = 3,
                        retry_delay: float = 1.0,
                        exponential_backoff: bool = False) -> str:
        """Add a one-time job to the scheduler.
        
        Args:
            job_name: Human-readable name for the job
            scheduled_at: When to run the job
            callback: Function to execute when the job runs
            metadata: Additional data about the job
            async_job: Whether this is an async job
            retry_count: Number of times to retry on failure
            retry_delay: Initial delay between retries (seconds)
            exponential_backoff: Whether to use exponential backoff for retries
            
        Returns:
            The job ID
        """
        import uuid
        job_id = f"job_{uuid.uuid4().hex[:8]}"
        job = OneTimeJob(
            job_id=job_id,
            job_name=job_name,
            scheduled_at=scheduled_at,
            callback=callback,
            metadata=metadata,
            async_job=async_job,
            retry_count=retry_count,
            retry_delay=retry_delay,
            exponential_backoff=exponential_backoff
        )
        return self.schedule_job(job)
    
    def add_interval_job(self, 
                        job_name: str,
                        interval_seconds: int,
                        callback: callable,
                        start_at: Optional[datetime] = None,
                        metadata: Optional[Dict[str, Any]] = None,
                        async_job: bool = False,
                        retry_count: int = 3,
                        retry_delay: float = 1.0,
                        exponential_backoff: bool = False) -> str:
        """Add an interval job to the scheduler.
        
        Args:
            job_name: Human-readable name for the job
            interval_seconds: How often to run the job (in seconds)
            callback: Function to execute when the job runs
            start_at: When to start the first run (defaults to now)
            metadata: Additional data about the job
            async_job: Whether this is an async job
            retry_count: Number of times to retry on failure
            retry_delay: Initial delay between retries (seconds)
            exponential_backoff: Whether to use exponential backoff for retries
            
        Returns:
            The job ID
        """
        import uuid
        job_id = f"job_{uuid.uuid4().hex[:8]}"
        job = IntervalJob(
            job_id=job_id,
            job_name=job_name,
            interval_seconds=interval_seconds,
            callback=callback,
            start_at=start_at,
            metadata=metadata,
            async_job=async_job,
            retry_count=retry_count,
            retry_delay=retry_delay,
            exponential_backoff=exponential_backoff
        )
        return self.schedule_job(job)
    
    def add_cron_job(self, 
                    job_name: str,
                    cron_expression: str,
                    callback: callable,
                    metadata: Optional[Dict[str, Any]] = None,
                    async_job: bool = False,
                    retry_count: int = 3,
                    retry_delay: float = 1.0,
                    exponential_backoff: bool = False) -> str:
        """Add a cron job to the scheduler.
        
        Args:
            job_name: Human-readable name for the job
            cron_expression: Standard cron expression (e.g., "* * * * *")
            callback: Function to execute when the job runs
            metadata: Additional data about the job
            async_job: Whether this is an async job
            retry_count: Number of times to retry on failure
            retry_delay: Initial delay between retries (seconds)
            exponential_backoff: Whether to use exponential backoff for retries
            
        Returns:
            The job ID
        """
        import uuid
        job_id = f"job_{uuid.uuid4().hex[:8]}"
        job = CronJob(
            job_id=job_id,
            job_name=job_name,
            cron_expression=cron_expression,
            callback=callback,
            metadata=metadata,
            async_job=async_job,
            retry_count=retry_count,
            retry_delay=retry_delay,
            exponential_backoff=exponential_backoff
        )
        return self.schedule_job(job)
