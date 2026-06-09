# UAGIP Scheduler

The UAGIP Scheduler is a robust, production-grade job scheduling system designed to handle various types of scheduled tasks within the UAGIP framework.

## Overview

The scheduler provides a unified interface for managing jobs with different execution patterns:
- One-time jobs that run once at a specified time
- Interval jobs that run periodically at fixed intervals
- Cron jobs that follow standard cron expressions

## Architecture

### Core Components

1. **Job Base Class**: Abstract base class defining common job properties and methods
2. **Job Types**: Different job implementations for one-time, interval, and cron scheduling
3. **Scheduler Engine**: Main engine responsible for job scheduling, execution, and management
4. **Job Status Management**: Track the state of jobs throughout their lifecycle
5. **Statistics System**: Monitor scheduler performance and job execution metrics

### Job Lifecycle

```
PENDING → RUNNING → [COMPLETED/FAILED/CANCELLED]
         ↘
          RETRYING
```

## Job Types

### One-Time Jobs
Jobs that execute once at a specific datetime.

```python
from datetime import datetime
from core.scheduler import Scheduler

scheduler = Scheduler()
job_id = scheduler.add_one_time_job(
    job_name="Daily Report",
    scheduled_at=datetime(2026, 6, 10, 9, 0),  # June 10, 2026 at 9:00 AM
    callback=generate_report
)
```

### Interval Jobs
Jobs that execute repeatedly at fixed intervals (in seconds).

```python
from core.scheduler import Scheduler

scheduler = Scheduler()
job_id = scheduler.add_interval_job(
    job_name="Data Sync",
    interval_seconds=300,  # Every 5 minutes
    callback=sync_data
)
```

### Cron Jobs
Jobs that execute based on standard cron expressions.

```python
from core.scheduler import Scheduler

scheduler = Scheduler()
job_id = scheduler.add_cron_job(
    job_name="Hourly Backup",
    cron_expression="0 * * * *",  # Every hour at minute 0
    callback=backup_database
)
```

## Features

### Async Support
Jobs can be executed synchronously or asynchronously.

```python
# Synchronous job
scheduler.add_one_time_job(
    job_name="Sync Job",
    scheduled_at=datetime.now(),
    callback=sync_function
)

# Asynchronous job
scheduler.add_one_time_job(
    job_name="Async Job",
    scheduled_at=datetime.now(),
    callback=async_function,
    async_job=True
)
```

### Retry Logic
Configurable retry behavior with exponential backoff support.

```python
scheduler.add_one_time_job(
    job_name="Failable Job",
    scheduled_at=datetime.now(),
    callback=failable_function,
    retry_count=3,           # Retry up to 3 times
    retry_delay=5.0,         # Initial delay of 5 seconds
    exponential_backoff=True # Use exponential backoff
)
```

### Thread Safety
The scheduler is designed to be thread-safe for concurrent job scheduling and management.

## Usage Examples

### Basic Scheduling
```python
from datetime import datetime
from core.scheduler import Scheduler

def my_task():
    print("Task executed!")

# Create scheduler
scheduler = Scheduler()
scheduler.start()

# Schedule different types of jobs
one_time_job_id = scheduler.add_one_time_job(
    job_name="One-time Task",
    scheduled_at=datetime.now() + timedelta(minutes=5),
    callback=my_task
)

interval_job_id = scheduler.add_interval_job(
    job_name="Interval Task",
    interval_seconds=60,
    callback=my_task
)

cron_job_id = scheduler.add_cron_job(
    job_name="Cron Task",
    cron_expression="0 0 * * *",  # Daily at midnight
    callback=my_task
)

# Stop the scheduler when done
scheduler.stop()
```

### Job Management
```python
# Get a specific job
job = scheduler.get_job(job_id)

# List all jobs
all_jobs = scheduler.list_jobs()

# Cancel a job
scheduler.cancel_job(job_id)

# Get statistics
stats = scheduler.get_statistics()
print(f"Total jobs: {stats['total_jobs']}")
```

## Cron Expressions

The scheduler supports standard cron expressions with 5 fields:

```
* * * * *
│ │ │ │ │
│ │ │ │ └── Day of week (0-7, where 0 and 7 are Sunday)
│ │ │ └──── Month (1-12)
│ │ └────── Day of month (1-31)
└────────── Hour (0-23)
```

### Common Examples
- `*/5 * * * *` - Every 5 minutes
- `0 * * * *` - Every hour at minute 0
- `0 0 * * *` - Daily at midnight
- `0 0 * * 0` - Weekly on Sunday at midnight

## Statistics

The scheduler tracks key performance metrics:

```python
stats = scheduler.get_statistics()
{
    'total_jobs': 10,
    'completed_jobs': 8,
    'failed_jobs': 1,
    'running_jobs': 1,
    'uptime': 3600  # seconds since start
}
```

## Implementation Details

### Thread Safety
The scheduler uses a `threading.RLock()` to ensure thread safety during job operations.

### Logging
All scheduler operations are logged using Python's standard logging framework.

### Event Integration
The scheduler publishes events to the event bus for job lifecycle management (JOB_CREATED, JOB_STARTED, JOB_COMPLETED, JOB_FAILED, JOB_CANCELLED).

## Future Extensions

The scheduler is designed to be extensible:
- Additional job types can be added by implementing the Job base class
- Persistence layer can be implemented for storage backends (SQLite, PostgreSQL)
- Advanced scheduling features like job dependencies and priorities can be added