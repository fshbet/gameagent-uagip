"""
Health Status Enum for UAGIP Health Monitoring System.
"""

from enum import Enum


class HealthStatus(Enum):
    """
    Enumeration of possible health statuses for components and system.
    """
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"