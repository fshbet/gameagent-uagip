"""
Frame data class for UAGIP Capture Engine.
"""

from dataclasses import dataclass
from typing import Any, Dict, Optional
import numpy as np


@dataclass
class Frame:
    """
    Represents a captured frame with metadata.
    
    Attributes:
        frame_id: Unique identifier for the frame
        timestamp: Capture timestamp
        width: Frame width in pixels
        height: Frame height in pixels
        source: Source identifier where frame came from
        image: NumPy array containing the frame data
        metadata: Additional metadata about the frame
    """
    
    frame_id: str
    timestamp: float
    width: int
    height: int
    source: str
    image: np.ndarray
    metadata: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        """Validate frame data after initialization."""
        if self.metadata is None:
            self.metadata = {}
            
        # Validate that image is a numpy array
        if not isinstance(self.image, np.ndarray):
            raise TypeError("Image must be a NumPy array")
            
        # Validate dimensions
        if self.width <= 0 or self.height <= 0:
            raise ValueError("Width and height must be positive integers")