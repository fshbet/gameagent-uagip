"""
Component Health Dataclass for UAGIP Health Monitoring System.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Optional

from core.health.health_status import HealthStatus


@dataclass
class ComponentHealth:
    """
    Dataclass representing the health status of a component.
    """
    component_id: str
    component_name: str
    status: HealthStatus
    last_check: datetime = field(default_factory=datetime.now)
    message: Optional[str] = None
    metrics: Dict[str, float] = field(default_factory=dict)