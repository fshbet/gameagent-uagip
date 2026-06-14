"""
Image record tracking for Vision Engine Dataset Management Platform.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional
import hashlib
import os
from datetime import datetime


@dataclass
class ImageRecord:
    """Track image metadata and properties."""
    
    image_id: str
    path: str
    width: int
    height: int
    source: str = ""
    hash: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        """Validate image record fields after initialization."""
        if not self.image_id:
            raise ValueError("Image ID cannot be empty")
        if not self.path:
            raise ValueError("Image path cannot be empty")
        if self.width <= 0 or self.height <= 0:
            raise ValueError("Image dimensions must be positive")
        
        # Generate hash if not provided
        if self.hash is None:
            self._generate_hash()
    
    def _generate_hash(self) -> None:
        """Generate SHA256 hash of the image file."""
        if os.path.exists(self.path):
            try:
                with open(self.path, 'rb') as f:
                    file_hash = hashlib.sha256()
                    for chunk in iter(lambda: f.read(4096), b""):
                        file_hash.update(chunk)
                    self.hash = file_hash.hexdigest()
            except Exception:
                # If we can't generate hash, set to None
                self.hash = None
        else:
            self.hash = None
    
    def update_timestamp(self) -> None:
        """Update the updated_at timestamp."""
        self.updated_at = datetime.now()