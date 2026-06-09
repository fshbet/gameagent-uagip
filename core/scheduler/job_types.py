from enum import Enum


class JobType(Enum):
    """Enumeration of job types."""
    
    ONE_TIME = "one_time"
    INTERVAL = "interval"
    CRON = "cron"