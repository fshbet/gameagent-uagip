"""
Capture Engine package for UAGIP.
"""

# Import core classes for easy access
from .frame import Frame
from .capture_source import CaptureSource
from .screen_capture import ScreenCapture
from .frame_buffer import FrameBuffer
from .capture_manager import CaptureManager
from .capture_metrics import CaptureMetrics

__all__ = [
    'Frame',
    'CaptureSource', 
    'ScreenCapture',
    'FrameBuffer',
    'CaptureManager',
    'CaptureMetrics'
]

# Package metadata
__version__ = "1.0.0"
__author__ = "UAGIP Team"