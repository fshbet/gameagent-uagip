"""
Screen capture implementation for UAGIP Capture Engine.
"""

import threading
from typing import Optional, Dict, Any
import numpy as np
from PIL import Image
import mss

from .capture_source import CaptureSource
from .frame import Frame


class ScreenCapture(CaptureSource):
    """
    Screen capture implementation using mss and PIL.
    
    Supports:
    - Desktop capture
    - Window capture  
    - Region capture
    
    Uses mss for fast screen capturing, PIL for image processing,
    and numpy for frame data storage.
    """
    
    def __init__(self, name: str, capture_type: str = "desktop", **kwargs):
        """
        Initialize the screen capture source.
        
        Args:
            name: Unique identifier for this capture source
            capture_type: Type of capture ("desktop", "window", "region")
            **kwargs: Additional parameters for capture configuration
        """
        super().__init__(name)
        self.capture_type = capture_type
        self.capture_params = kwargs
        
        # Initialize mss
        self._mss = None
        self._lock = threading.Lock()
        
        # Capture configuration
        self._width = kwargs.get('width', 0)
        self._height = kwargs.get('height', 0)
        self._left = kwargs.get('left', 0)
        self._top = kwargs.get('top', 0)
        
    def start(self) -> bool:
        """
        Start the screen capture source.
        
        Returns:
            True if successfully started, False otherwise
        """
        with self._lock:
            if self.is_running():
                return True
                
            try:
                self._mss = mss.mss()
                self._set_running_state(True)
                return True
            except Exception as e:
                print(f"Failed to start screen capture: {e}")
                return False
    
    def stop(self) -> bool:
        """
        Stop the screen capture source.
        
        Returns:
            True if successfully stopped, False otherwise
        """
        with self._lock:
            if not self.is_running():
                return True
                
            try:
                if self._mss:
                    self._mss.close()
                self._set_running_state(False)
                return True
            except Exception as e:
                print(f"Failed to stop screen capture: {e}")
                return False
    
    def get_frame(self) -> Optional[Frame]:
        """
        Get the latest frame from the screen capture source.
        
        Returns:
            The latest Frame object or None if no frame is available
        """
        with self._lock:
            if not self.is_running() or not self._mss:
                return None
                
            try:
                # Capture screen
                screenshot = self._capture_screen()
                
                if screenshot is None:
                    return None
                    
                # Convert to numpy array
                image_array = np.array(screenshot)
                
                # Create and return Frame object
                frame = Frame(
                    frame_id=f"{self.name}_{threading.current_thread().ident}",
                    timestamp=threading.current_thread().ident,  # Simplified timestamp
                    width=image_array.shape[1],
                    height=image_array.shape[0],
                    source=self.name,
                    image=image_array,
                    metadata={
                        "capture_type": self.capture_type,
                        "width": image_array.shape[1],
                        "height": image_array.shape[0]
                    }
                )
                
                return frame
                
            except Exception as e:
                print(f"Error getting frame: {e}")
                return None
    
    def _capture_screen(self) -> Optional[Image.Image]:
        """
        Capture screen based on capture type.
        
        Returns:
            PIL Image object or None if failed
        """
        try:
            if self.capture_type == "desktop":
                # Capture entire desktop
                screenshot = self._mss.grab(self._mss.monitors[0])
            elif self.capture_type == "region":
                # Capture specified region
                monitor = {
                    "top": self._top,
                    "left": self._left,
                    "width": self._width,
                    "height": self._height
                }
                screenshot = self._mss.grab(monitor)
            else:
                # Default to first monitor
                screenshot = self._mss.grab(self._mss.monitors[0])
                
            # Convert to PIL Image
            return Image.frombytes("RGB", (screenshot.width, screenshot.height), screenshot.rgb)
            
        except Exception as e:
            print(f"Screen capture error: {e}")
            return None
    
    def set_capture_region(self, left: int, top: int, width: int, height: int):
        """
        Set the capture region for region-based capture.
        
        Args:
            left: Left coordinate
            top: Top coordinate  
            width: Width of region
            height: Height of region
        """
        self._left = left
        self._top = top
        self._width = width
        self._height = height