"""
Annotation record for Vision Engine Dataset Management Platform.
Supports bbox, polygon, classification, and confidence annotations.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Union
from enum import Enum
import json


class AnnotationType(Enum):
    """Enumeration of supported annotation types."""
    BBOX = "bbox"
    POLYGON = "polygon"
    CLASSIFICATION = "classification"


@dataclass
class AnnotationRecord:
    """Annotation record supporting multiple annotation types."""
    
    annotation_id: str
    image_id: str
    annotation_type: AnnotationType
    label: str
    confidence: Optional[float] = None
    bbox: Optional[List[float]] = None  # [x_min, y_min, x_max, y_max]
    polygon: Optional[List[List[float]]] = None  # List of [x, y] points
    classification: Optional[str] = None
    metadata: Dict[str, object] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate annotation record fields after initialization."""
        if not self.annotation_id:
            raise ValueError("Annotation ID cannot be empty")
        if not self.image_id:
            raise ValueError("Image ID cannot be empty")
        if not self.label:
            raise ValueError("Label cannot be empty")
        
        # Validate annotation type-specific fields
        if self.annotation_type == AnnotationType.BBOX and self.bbox is None:
            raise ValueError("BBox annotation requires bbox coordinates")
        if self.annotation_type == AnnotationType.POLYGON and self.polygon is None:
            raise ValueError("Polygon annotation requires polygon points")
        if self.annotation_type == AnnotationType.CLASSIFICATION and self.classification is None:
            raise ValueError("Classification annotation requires classification label")
        
        # Validate confidence range
        if self.confidence is not None and (self.confidence < 0 or self.confidence > 1):
            raise ValueError("Confidence must be between 0 and 1")
    
    def to_yolo_format(self) -> str:
        """
        Convert annotation to YOLO format string.
        
        Returns:
            str: YOLO formatted annotation line
        """
        if self.annotation_type != AnnotationType.BBOX:
            raise ValueError("Only bounding box annotations can be converted to YOLO format")
        
        if not self.bbox or len(self.bbox) != 4:
            raise ValueError("Invalid bbox coordinates for YOLO conversion")
        
        # YOLO format: class_id center_x center_y width height (normalized)
        # We'll return a placeholder for class_id as it's determined by the dataset
        return f"0 {self.bbox[0]} {self.bbox[1]} {self.bbox[2]} {self.bbox[3]}"
    
    def to_dict(self) -> Dict:
        """Convert annotation record to dictionary."""
        result = {
            "annotation_id": self.annotation_id,
            "image_id": self.image_id,
            "annotation_type": self.annotation_type.value,
            "label": self.label,
            "metadata": self.metadata
        }
        
        if self.confidence is not None:
            result["confidence"] = self.confidence
            
        if self.bbox is not None:
            result["bbox"] = self.bbox
            
        if self.polygon is not None:
            result["polygon"] = self.polygon
            
        if self.classification is not None:
            result["classification"] = self.classification
            
        return result
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'AnnotationRecord':
        """Create annotation record from dictionary."""
        return cls(
            annotation_id=data["annotation_id"],
            image_id=data["image_id"],
            annotation_type=AnnotationType(data["annotation_type"]),
            label=data["label"],
            confidence=data.get("confidence"),
            bbox=data.get("bbox"),
            polygon=data.get("polygon"),
            classification=data.get("classification"),
            metadata=data.get("metadata", {})
        )