"""
Inference result dataclass for UAGIP YOLO Model Management Framework.

This module defines the data structure for storing and representing
YOLO model inference results.
"""

from dataclasses import dataclass
from typing import List, Optional, Tuple, Dict, Any
from datetime import datetime


@dataclass
class InferenceResult:
    """
    Dataclass for storing YOLO inference results.
    
    This class represents a single detection result from a YOLO model,
    containing information about the detected object including its class,
    confidence score, bounding box, and optional segmentation data.
    """
    
    # Detection information
    class_id: int
    class_name: str
    confidence: float
    
    # Spatial information
    # Segmentation data (if available)
    segmentation: Optional[List[Tuple[float, float]]] = None
    
    # Timestamp of when the inference was performed
    timestamp: datetime = None
    
    def __post_init__(self):
        """Initialize the inference result after creation."""
        if self.timestamp is None:
            from datetime import datetime
            self.timestamp = datetime.now()
        
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("Confidence must be between 0.0 and 1.0")
    
    def to_dict(self) -> Dict[str, any]:
        """
        Convert InferenceResult instance to dictionary.
        
        Returns:
            Dictionary representation of the inference result
        """
        result = self.__dict__.copy()
        # Convert timestamp to ISO format string
        result['timestamp'] = self.timestamp.isoformat()
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, any]) -> 'InferenceResult':
        """
        Create InferenceResult instance from dictionary.
        
        Args:
            data: Dictionary containing inference result
            
        Returns:
            InferenceResult instance
        """
        # Convert timestamp string back to datetime object if needed
        if isinstance(data.get('timestamp'), str):
            from datetime import datetime
            data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        
        return cls(**data)
    
    def __str__(self) -> str:
        """String representation of the inference result."""
        return (f"InferenceResult(class={self.class_name}, "
                f"confidence={self.confidence:.2f}, "
                f"bbox={self.bbox})")
    
    def __repr__(self) -> str:
        """Detailed string representation of the inference result."""
        return (f"InferenceResult(class_id={self.class_id}, "
                f"class_name='{self.class_name}', confidence={self.confidence}, "
                f"bbox={self.bbox}, timestamp='{self.timestamp}')")