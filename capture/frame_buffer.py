"""
Circular buffer implementation for UAGIP Capture Engine.
"""

import threading
from collections import deque
from typing import Deque, Optional, List
import time

from .frame import Frame


class FrameBuffer:
    """
    Circular buffer for storing captured frames.
    
    Provides thread-safe storage of frame history with configurable size.
    Supports access to latest frame and last N frames.
    """
    
    def __init__(self, capacity: int = 100):
        """
        Initialize the frame buffer.
        
        Args:
            capacity: Maximum number of frames to store
        """
        self._capacity = capacity
        self._buffer: Deque[Frame] = deque(maxlen=capacity)
        self._lock = threading.Lock()
        self._frame_count = 0
        
    def add_frame(self, frame: Frame) -> bool:
        """
        Add a frame to the buffer.
        
        Args:
            frame: Frame to add
            
        Returns:
            True if frame was added, False if buffer is full
        """
        with self._lock:
            # Check if we're at capacity
            if len(self._buffer) >= self._capacity:
                # Remove oldest frame to make space (circular behavior)
                self._buffer.popleft()
                
            self._buffer.append(frame)
            self._frame_count += 1
            return True
    
    def get_latest(self) -> Optional[Frame]:
        """
        Get the latest frame from the buffer.
        
        Returns:
            The most recent frame or None if buffer is empty
        """
        with self._lock:
            if not self._buffer:
                return None
            return self._buffer[-1]
    
    def get_last_n(self, n: int) -> List[Frame]:
        """
        Get the last N frames from the buffer.
        
        Args:
            n: Number of frames to retrieve
            
        Returns:
            List of frames (most recent first)
        """
        with self._lock:
            if not self._buffer:
                return []
            
            # Return last n frames in reverse order (most recent first)
            result = list(self._buffer)[-n:]
            return result[::-1]
    
    def clear(self):
        """
        Clear all frames from the buffer.
        """
        with self._lock:
            self._buffer.clear()
            self._frame_count = 0
    
    def size(self) -> int:
        """
        Get the current number of frames in the buffer.
        
        Returns:
            Number of frames currently stored
        """
        with self._lock:
            return len(self._buffer)
    
    def capacity(self) -> int:
        """
        Get the maximum capacity of the buffer.
        
        Returns:
            Maximum number of frames the buffer can hold
        """
        return self._capacity
    
    def is_full(self) -> bool:
        """
        Check if the buffer is at maximum capacity.
        
        Returns:
            True if buffer is full, False otherwise
        """
        with self._lock:
            return len(self._buffer) >= self._capacity
    
    def frame_count(self) -> int:
        """
        Get total number of frames added to the buffer since initialization.
        
        Returns:
            Total frame count
        """
        with self._lock:
            return self._frame_count