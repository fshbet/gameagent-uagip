"""
Vision Engine Foundation Package
This package provides computer vision capabilities including image preprocessing,
template matching, object detection, and OCR.
"""

from .image_preprocessor import ImagePreprocessor
from .template_matcher import TemplateMatcher
from .object_detector import ObjectDetector
from .ocr_engine import OCREngine
from .vision_manager import VisionManager

__all__ = [
    "ImagePreprocessor",
    "TemplateMatcher",
    "ObjectDetector",
    "OCREngine",
    "VisionManager"
]