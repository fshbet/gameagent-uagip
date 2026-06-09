import asyncio
import time
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

import pytest

from core.scheduler import (
    Scheduler,
    OneTimeJob,
    IntervalJob,
    CronJob,
    JobStatus,
    JobType
)


def test_job_base_class():
    """Test the base Job class functionality."""
    # Create a mock callback
    callback = Mock()
    
    # Create a basic job
    job = OneTimeJob(
        job_id="test_job_1",
        job_name="Test Job",
        scheduled_at=datetime.now(),
        callback=callback
    )
    
    assert job.job_id == "test_job_1"
    assert job.job_name == "Test Job"
    assert job.job_type == "one_time"
    assert job.status == JobStatus.PENDING
    assert job.retry_count == 3
    assert job.retry_delay == 1.0
    assert job.exponential_backoff is False


def test_one_time_job():
    """Test one-time job functionality."""
    # Create a mock callback
    callback = Mock()
    
    # Create a one-time job
    scheduled_at = datetime.now() + timedelta(seconds=1)
    job = OneTimeJob(
        job_id="test_onetime_1",
        job_name="One-Time Test Job",
        scheduled_at=scheduled_at,
        callback=callback
    )
    
    assert job.job_type == "one_time"
    assert job.scheduled_at == scheduled_at


def test_interval_job():
    """Test interval job functionality."""
    # Create a mock callback
    callback = Mock()
    
    # Create an interval job
    job = IntervalJob(
        job_id="test_interval_1",
        job_name="Interval Test Job",
        interval_seconds=60,
        callback=callback
    )
    
    assert job.job_type == "interval"
    assert job.interval_seconds == 60


def test_cron_job():
    """Test cron job functionality."""
    # Create a mock callback
    callback = Mock()
    
    # Create a cron job
    job = CronJob(
        job_id="test_cron_1",
        job_name="Cron Test Job",
        cron_expression="* * * * *",
        callback=callback
    )
    
    assert job.job_type == "cron"
    assert job.cron_expression == "* * * * *"


def test_scheduler_basic():
    """Test basic scheduler functionality."""
    scheduler = Scheduler()
    
    # Test that scheduler starts correctly
    scheduler.start()
    assert scheduler._running is True
    
    # Test that scheduler stops correctly
    scheduler.stop()
    assert scheduler._running is False


def test_schedule_and_get_job():
    """Test scheduling and retrieving jobs."""
    scheduler = Scheduler()
    
    # Create a mock callback
    callback = Mock()
    
    # Schedule a job
    job = OneTimeJob(
        job_id="test_job_1",
        job_name="Test Job",
        scheduled_at=datetime.now(),
        callback=callback
    )
    
    job_id = scheduler.schedule_job(job)
    assert job_id == "test_job_1"
    
    # Retrieve the job
    retrieved_job = scheduler.get_job("test_job_1")
    assert retrieved_job is not None
    assert retrieved_job.job_name == "Test Job"


def test_list_jobs():
    """Test listing all jobs."""
    scheduler = Scheduler()
    
    # Create mock callbacks
    callback1 = Mock()
    callback2 = Mock()
    
    # Schedule two jobs
    job1 = OneTimeJob(
        job_id="test_job_1",
        job_name="Test Job 1",
        scheduled_at=datetime.now(),
        callback=callback1
    )
    
    job2 = OneTimeJob(
        job_id="test_job_2",
        job_name="Test Job 2",
        scheduled_at=datetime.now(),
        callback=callback2
    )
    
    scheduler.schedule_job(job1)
    scheduler.schedule_job(job2)
    
    jobs = scheduler.list_jobs()
    assert len(jobs) == 2
    assert jobs[0].job_name == "Test Job 1"
    assert jobs[1].job_name == "Test Job 2"


def test_cancel_job():
    """Test cancelling a job."""
    scheduler = Scheduler()
    
    # Create a mock callback
    callback = Mock()
    
    # Schedule a job
    job = OneTimeJob(
        job_id="test_job_1",
        job_name="Test Job",
        scheduled_at=datetime.now(),
        callback=callback
    )
    
    scheduler.schedule_job(job)
    
    # Cancel the job
    result = scheduler.cancel_job("test_job_1")
    assert result is True
    
    # Verify job was removed
    retrieved_job = scheduler.get_job("test_job_1")
    assert retrieved_job is None


def test_add_one_time_job():
    """Test adding one-time jobs via scheduler helper."""
    scheduler = Scheduler()
    
    # Create a mock callback
    callback = Mock()
    
    # Add a one-time job
    job_id = scheduler.add_one_time_job(
        job_name="One-Time Test",
        scheduled_at=datetime.now() + timedelta(seconds=1),
        callback=callback
    )
    
    assert job_id is not None
    assert len(scheduler.list_jobs()) == 1


def test_add_interval_job():
    """Test adding interval jobs via scheduler helper."""
    scheduler = Scheduler()
    
    # Create a mock callback
    callback = Mock()
    
    # Add an interval job
    job_id = scheduler.add_interval_job(
        job_name="Interval Test",
        interval_seconds=30,
        callback=callback
    )
    
    assert job_id is not None
    assert len(scheduler.list_jobs()) == 1


def test_add_cron_job():
    """Test adding cron jobs via scheduler helper."""
    scheduler = Scheduler()
    
    # Create a mock callback
    callback = Mock()
    
    # Add a cron job
    job_id = scheduler.add_cron_job(
        job_name="Cron Test",
        cron_expression="* * * * *",
        callback=callback
    )
    
    assert job_id is not None
    assert len(scheduler.list_jobs()) == 1


def test_statistics():
    """Test scheduler statistics."""
    scheduler = Scheduler()
    
    # Create a mock callback
    callback = Mock()
    
    # Add some jobs
    scheduler.add_one_time_job(
        job_name="Test Job 1",
        scheduled_at=datetime.now() + timedelta(seconds=1),
        callback=callback
    )
    
    stats = scheduler.get_statistics()
    assert stats['total_jobs'] == 1
    assert stats['completed_jobs'] == 0
    assert stats['failed_jobs'] == 0
    assert stats['running_jobs'] == 0


def test_run_job():
    """Test running a job."""
    scheduler = Scheduler()
    
    # Create a mock callback that returns a value
    callback = Mock(return_value="test_result")
    
    # Add a one-time job
    job_id = scheduler.add_one_time_job(
        job_name="Test Run Job",
        scheduled_at=datetime.now(),
        callback=callback
    )
    
    # Run the job
    result = scheduler.run_job(job_id)
    assert result is True
    
    # Verify the callback was called
    callback.assert_called_once()


    def test_run_pending_jobs():
        """Test running pending jobs."""
        scheduler = Scheduler()

        # Create a mock callback
        callback = Mock()

        # Add a one-time job that's already due
        job_id = scheduler.add_one_time_job(
            job_name="Pending Test Job",
            scheduled_at=datetime.now() - timedelta(seconds=1),
            callback=callback
        )

        # Run pending jobs
        scheduler.run_pending_jobs()

        # Verify the job was executed
        callback.assert_called_once()


def test_async_job():
    """Test async job functionality."""
    scheduler = Scheduler()
    
    # Create an async callback
    async def async_callback():
        await asyncio.sleep(0.1)
        return "async_result"
    
    # Add an async one-time job
    job_id = scheduler.add_one_time_job(
        job_name="Async Test Job",
        scheduled_at=datetime.now(),
        callback=async_callback,
        async_job=True
    )
    
    # Run the job
    result = scheduler.run_job(job_id)
    assert result is True


def test_thread_safety():
    """Test that the scheduler is thread-safe."""
    scheduler = Scheduler()
    
    # Create a mock callback
    callback = Mock()
    
    # Add jobs in parallel using different threads
    def add_job():
        job_id = scheduler.add_one_time_job(
            job_name="Thread Test Job",
            scheduled_at=datetime.now() + timedelta(seconds=1),
            callback=callback
        )
        return job_id
    
    # This should not raise any exceptions
    job_ids = [add_job() for _ in range(5)]
    
    assert len(job_ids) == 5
    assert len(scheduler.list_jobs()) == 5


if __name__ == "__main__":
    pytest.main([__file__, "-v"])