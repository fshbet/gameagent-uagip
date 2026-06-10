"""
Capture metrics tracking for UAGIP Capture Engine.
"""

import time
from typing import Optional
import statistics


class CaptureMetrics:
    """
    Metrics tracking for capture sources.
    
    Tracks FPS, dropped frames, latency, and uptime for capture sources.
    """
    
    def __init__(self):
        """Initialize capture metrics."""
        self.start_time: Optional[float] = None
        self.stop_time: Optional[float] = None
        self._frame_count = 0
        self._dropped_frames = 0
        self._latency_samples = []
        self._fps_samples = []
        
    def update_fps(self, frame_count: int = 1):
        """
        Update FPS metrics.
        
        Args:
            frame_count: Number of frames to count (default: 1)
        """
        self._frame_count += frame_count
        # Store samples for calculation (keep last 100 samples)
        if len(self._fps_samples) >= 100:
            self._fps_samples.pop(0)
        self._fps_samples.append(frame_count)
        
    def update_latency(self, latency: float):
        """
        Update latency metrics.
        
        Args:
            latency: Capture latency in seconds
        """
        # Store samples for calculation (keep last 1000 samples)
        if len(self._latency_samples) >= 1000:
            self._latency_samples.pop(0)
        self._latency_samples.append(latency)
        
    def update_dropped_frames(self, count: int = 1):
        """
        Update dropped frames count.
        
        Args:
            count: Number of dropped frames to add (default: 1)
        """
        self._dropped_frames += count
        
    @property
    def fps(self) -> float:
        """
        Get current FPS.
        
        Returns:
            Current frames per second
        """
        if not self._fps_samples:
            return 0.0
            
        # Calculate average over last samples
        return statistics.mean(self._fps_samples)
        
    @property
    def average_latency(self) -> float:
        """
        Get average latency.
        
        Returns:
            Average capture latency in seconds
        """
        if not self._latency_samples:
            return 0.0
            
        return statistics.mean(self._latency_samples)
        
    @property
    def dropped_frames(self) -> int:
        """
        Get total dropped frames.
        
        Returns:
            Number of dropped frames
        """
        return self._dropped_frames
        
    @property
    def frame_count(self) -> int:
        """
        Get total frame count.
        
        Returns:
            Total number of captured frames
        """
        return self._frame_count
        
    @property
    def capture_uptime(self) -> float:
        """
        Get capture uptime in seconds.
        
        Returns:
            Uptime in seconds, or 0 if not started
        """
        if self.start_time is None:
            return 0.0
            
        end_time = self.stop_time if self.stop_time is not None else time.time()
        return end_time - self.start_time
        
    @property
    def is_active(self) -> bool:
        """
        Check if capture is currently active.
        
        Returns:
            True if capture source is active, False otherwise
        """
        return self.start_time is not None and self.stop_time is None
        
    def get_metrics(self) -> dict:
        """
        Get all metrics as a dictionary.
        
        Returns:
            Dictionary containing all metrics
        """
        return {
            'fps': self.fps,
            'average_latency': self.average_latency,
            'dropped_frames': self.dropped_frames,
            'frame_count': self.frame_count,
            'capture_uptime': self.capture_uptime,
            'is_active': self.is_active
        }
        
    def reset(self):
        """
        Reset all metrics to initial state.
        """
        self.start_time = None
        self.stop_time = None
        self._frame_count = 0
        self._dropped_frames = 0
        self._latency_samples = []
        self._fps_samples = []