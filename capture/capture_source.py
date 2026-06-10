"""
Abstract base class for capture sources in UAGIP Capture Engine.
"""

from abc import ABC, abstractmethod
from typing import Optional
import threading


class CaptureSource(ABC):
    """
    Abstract base class for all capture sources.
    
    This class defines the interface that all capture sources must implement.
    It supports both synchronous and asynchronous capture operations.
    """
    
    def __init__(self, name: str):
        """
        Initialize the capture source.
        
        Args:
            name: Unique identifier for this capture source
        """
        self.name = name
        self._is_running = False
        self._lock = threading.Lock()
    
    @abstractmethod
    def start(self) -> bool:
        """
        Start the capture source.
        
        Returns:
            True if successfully started, False otherwise
        """
        pass
    
    @abstractmethod
    def stop(self) -> bool:
        """
        Stop the capture source.
        
        Returns:
            True if successfully stopped, False otherwise
        """
        pass
    
    @abstractmethod
    def get_frame(self) -> Optional[object]:
        """
        Get the latest frame from the capture source.
        
        Returns:
            The latest Frame object or None if no frame is available
        """
        pass
    
    def is_running(self) -> bool:
        """
        Check if the capture source is currently running.
        
        Returns:
            True if running, False otherwise
        """
        with self._lock:
            return self._is_running
    
    def _set_running_state(self, state: bool):
        """
        Internal method to set the running state.
        
        Args:
            state: The new running state
        """
        with self._lock:
            self._is_running = state