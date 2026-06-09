"""
Event base class for UAGIP Event Bus.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, Optional
import uuid


@dataclass
class Event:
    """
    Base event class for all events in the UAGIP system.
    
    Supports event_id, event_type, timestamp, source, and payload.
    """
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    event_type: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    source: str = ""
    payload: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        """Initialize the payload if not provided."""
        if self.payload is None:
            self.payload = {}