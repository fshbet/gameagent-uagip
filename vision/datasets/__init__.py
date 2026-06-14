"""
Vision Engine Dataset Management Platform.
"""

from .dataset import Dataset
from .image_record import ImageRecord
from .annotation_record import AnnotationRecord, AnnotationType
from .dataset_manager import DatasetManager
from .version_manager import VersionManager

__all__ = [
    "Dataset",
    "ImageRecord",
    "AnnotationRecord",
    "AnnotationType",
    "DatasetManager",
    "VersionManager"
]