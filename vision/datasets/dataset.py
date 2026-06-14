"""
Dataset dataclass for Vision Engine Dataset Management Platform.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional
import uuid


@dataclass
class Dataset:
    """Dataset object with all required fields."""
    
    dataset_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    version: str = "1.0.0"
    created_at: datetime = field(default_factory=datetime.now)
    labels: List[str] = field(default_factory=list)
    metadata: Dict[str, object] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate dataset fields after initialization."""
        if not self.name:
            raise ValueError("Dataset name cannot be empty")