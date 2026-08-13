"""
Model metadata for UAGIP YOLO Model Management Framework.

This module defines the data structures for tracking YOLO model metadata
and related information.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime


@dataclass
class ModelMetadata:
    """
    Metadata for a YOLO model.
    
    This class tracks all relevant information about a YOLO model,
    including identification, versioning, configuration, and technical details.
    """
    
    # Identification
    model_id: str
    model_name: str
    version: str
    
    # Framework and backend
    framework: str  # e.g., 'YOLOv8', 'YOLOv7', etc.
    backend: str    # e.g., 'ultralytics', 'onnx', 'tensorrt', etc.
    
    # Model configuration
    classes: List[str]  # List of class names the model can detect
    input_size: tuple   # Input size as (height, width)
    
    # Metadata
    created_at: datetime = None
    checksum: Optional[str] = None  # Hash of the model file for verification
    
    def __post_init__(self):
        """Initialize the model metadata after creation."""
        if self.created_at is None:
            self.created_at = datetime.now()
        
        # Ensure input_size is a tuple
        if not isinstance(self.input_size, tuple):
            raise ValueError("input_size must be a tuple (height, width)")


# Example usage:
"""
# Create a model metadata instance
metadata = ModelMetadata(
    model_id="yolo_v8_person_detector",
    model_name="YOLOv8 Person Detector",
    version="1.0.0",
    framework="YOLOv8",
    backend="ultralytics",
    classes=["person", "car", "dog"],
    input_size=(640, 640),
    checksum="abc123def456"
)
"""