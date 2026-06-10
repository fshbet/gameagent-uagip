"""
Capture Manager for UAGIP Capture Engine.
"""

import threading
from typing import Dict, Optional, List
import time

from .capture_source import CaptureSource
from .frame_buffer import FrameBuffer
from .frame import Frame
from .capture_metrics import CaptureMetrics


class CaptureManager:
    """
    Central manager for handling multiple capture sources.
    
    Provides registration, start/stop, and frame retrieval capabilities
    for multiple capture sources.
    """
    
    def __init__(self):
        """Initialize the capture manager."""
        self._sources: Dict[str, CaptureSource] = {}
        self._buffers: Dict[str, FrameBuffer] = {}
        self._metrics: Dict[str, CaptureMetrics] = {}
        self._lock = threading.Lock()
        
    def register_source(self, source: CaptureSource, buffer_capacity: int = 100) -> bool:
        """
        Register a capture source with the manager.
        
        Args:
            source: CaptureSource instance to register
            buffer_capacity: Frame buffer capacity for this source
            
        Returns:
            True if successfully registered, False otherwise
        """
        with self._lock:
            if source.name in self._sources:
                return False
                
            self._sources[source.name] = source
            self._buffers[source.name] = FrameBuffer(buffer_capacity)
            self._metrics[source.name] = CaptureMetrics()
            return True
    
    def remove_source(self, source_name: str) -> bool:
        """
        Remove a capture source from the manager.
        
        Args:
            source_name: Name of the source to remove
            
        Returns:
            True if successfully removed, False otherwise
        """
        with self._lock:
            if source_name not in self._sources:
                return False
                
            # Stop the source if it's running
            if self._sources[source_name].is_running():
                self._sources[source_name].stop()
                
            # Remove from all collections
            del self._sources[source_name]
            del self._buffers[source_name]
            del self._metrics[source_name]
            return True
    
    def start_source(self, source_name: str) -> bool:
        """
        Start a registered capture source.
        
        Args:
            source_name: Name of the source to start
            
        Returns:
            True if successfully started, False otherwise
        """
        with self._lock:
            if source_name not in self._sources:
                return False
                
            source = self._sources[source_name]
            if source.is_running():
                return True
                
            # Start the source and update metrics
            success = source.start()
            if success:
                self._metrics[source_name].start_time = time.time()
                
            return success
    
    def stop_source(self, source_name: str) -> bool:
        """
        Stop a running capture source.
        
        Args:
            source_name: Name of the source to stop
            
        Returns:
            True if successfully stopped, False otherwise
        """
        with self._lock:
            if source_name not in self._sources:
                return False
                
            source = self._sources[source_name]
            if not source.is_running():
                return True
                
            # Stop the source and update metrics
            success = source.stop()
            if success:
                self._metrics[source_name].stop_time = time.time()
                
            return success
    
    def get_frame(self, source_name: str) -> Optional[Frame]:
        """
        Get the latest frame from a specific source.
        
        Args:
            source_name: Name of the source to get frame from
            
        Returns:
            Latest Frame object or None if no frame available
        """
        with self._lock:
            if source_name not in self._sources:
                return None
                
            source = self._sources[source_name]
            frame = source.get_frame()
            
            if frame is not None:
                # Store frame in buffer
                self._buffers[source_name].add_frame(frame)
                
                # Update metrics
                self._metrics[source_name].update_fps(1)
                self._metrics[source_name].update_latency(time.time() - frame.timestamp)
                
            return frame
    
    def list_sources(self) -> List[str]:
        """
        Get a list of all registered source names.
        
        Returns:
            List of registered source names
        """
        with self._lock:
            return list(self._sources.keys())
    
    def get_source(self, source_name: str) -> Optional[CaptureSource]:
        """
        Get a reference to a specific capture source.
        
        Args:
            source_name: Name of the source to retrieve
            
        Returns:
            CaptureSource instance or None if not found
        """
        with self._lock:
            return self._sources.get(source_name)
    
    def get_buffer(self, source_name: str) -> Optional[FrameBuffer]:
        """
        Get the frame buffer for a specific source.
        
        Args:
            source_name: Name of the source
            
        Returns:
            FrameBuffer instance or None if not found
        """
        with self._lock:
            return self._buffers.get(source_name)
    
    def get_metrics(self, source_name: str) -> Optional[CaptureMetrics]:
        """
        Get metrics for a specific source.
        
        Args:
            source_name: Name of the source
            
        Returns:
            CaptureMetrics instance or None if not found
        """
        with self._lock:
            return self._metrics.get(source_name)
    
    def get_all_metrics(self) -> Dict[str, CaptureMetrics]:
        """
        Get metrics for all sources.
        
        Returns:
            Dictionary mapping source names to their metrics
        """
        with self._lock:
            return self._metrics.copy()