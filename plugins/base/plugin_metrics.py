"""
Plugin metrics tracking for plugin framework.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional
from datetime import datetime
import time


@dataclass
class PluginMetrics:
    """
    Tracks metrics for a plugin.
    
    This class provides detailed metrics and statistics for plugin execution
    including actions executed, state detections, failures, and performance.
    """
    
    # Core identification
    plugin_id: str
    plugin_name: str
    
    # Action metrics
    actions_executed: int = 0
    actions_successful: int = 0
    actions_failed: int = 0
    
    # State detection metrics
    state_detections: int = 0
    state_detections_successful: int = 0
    state_detections_failed: int = 0
    
    # Failure metrics
    total_failures: int = 0
    error_messages: list = field(default_factory=list)
    
    # Performance metrics
    execution_latency: float = 0.0  # in seconds
    total_execution_time: float = 0.0  # in seconds
    last_execution_time: Optional[float] = None
    
    # Timing information
    start_time: Optional[datetime] = None
    last_updated: Optional[datetime] = None
    
    def __post_init__(self):
        """
        Initialize the PluginMetrics instance.
        """
        self.start_time = datetime.now()
        self.last_updated = datetime.now()
    
    def increment_actions_executed(self) -> None:
        """
        Increment the actions executed counter.
        """
        self.actions_executed += 1
        self.last_updated = datetime.now()
    
    def increment_successful_actions(self) -> None:
        """
        Increment the successful actions counter.
        """
        self.actions_successful += 1
        self.last_updated = datetime.now()
    
    def increment_failed_actions(self) -> None:
        """
        Increment the failed actions counter.
        """
        self.actions_failed += 1
        self.total_failures += 1
        self.last_updated = datetime.now()
    
    def increment_state_detections(self) -> None:
        """
        Increment the state detections counter.
        """
        self.state_detections += 1
        self.last_updated = datetime.now()
    
    def increment_successful_state_detections(self) -> None:
        """
        Increment the successful state detections counter.
        """
        self.state_detections_successful += 1
        self.last_updated = datetime.now()
    
    def increment_failed_state_detections(self) -> None:
        """
        Increment the failed state detections counter.
        """
        self.state_detections_failed += 1
        self.total_failures += 1
        self.last_updated = datetime.now()
    
    def add_error_message(self, error_message: str) -> None:
        """
        Add an error message to the metrics.
        
        Args:
            error_message: Description of the error that occurred
        """
        self.error_messages.append(error_message)
        self.total_failures += 1
        self.last_updated = datetime.now()
    
    def record_execution_time(self, execution_time: float) -> None:
        """
        Record an execution time.
        
        Args:
            execution_time: Time taken for the execution in seconds
        """
        self.last_execution_time = execution_time
        self.total_execution_time += execution_time
        self.execution_latency = execution_time  # Keep latest execution latency
        self.last_updated = datetime.now()
    
    def get_success_rate(self) -> float:
        """
        Calculate the success rate for actions.
        
        Returns:
            Success rate as a percentage (0.0 to 100.0)
        """
        if self.actions_executed == 0:
            return 100.0  # No actions means perfect success rate
        
        return (self.actions_successful / self.actions_executed) * 100
    
    def get_state_detection_success_rate(self) -> float:
        """
        Calculate the success rate for state detections.
        
        Returns:
            Success rate as a percentage (0.0 to 100.0)
        """
        if self.state_detections == 0:
            return 100.0  # No detections means perfect success rate
        
        return (self.state_detections_successful / self.state_detections) * 100
    
    def get_total_execution_time(self) -> float:
        """
        Get the total execution time.
        
        Returns:
            Total execution time in seconds
        """
        return self.total_execution_time
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert PluginMetrics to dictionary for serialization.
        
        Returns:
            Dictionary representation of the PluginMetrics
        """
        return {
            'plugin_id': self.plugin_id,
            'plugin_name': self.plugin_name,
            'actions_executed': self.actions_executed,
            'actions_successful': self.actions_successful,
            'actions_failed': self.actions_failed,
            'state_detections': self.state_detections,
            'state_detections_successful': self.state_detections_successful,
            'state_detections_failed': self.state_detections_failed,
            'total_failures': self.total_failures,
            'error_messages': self.error_messages,
            'execution_latency': self.execution_latency,
            'total_execution_time': self.total_execution_time,
            'last_execution_time': self.last_execution_time,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'last_updated': self.last_updated.isoformat() if self.last_updated else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PluginMetrics':
        """
        Create PluginMetrics from dictionary.
        
        Args:
            data: Dictionary with PluginMetrics data
            
        Returns:
            New PluginMetrics instance
        """
        # Convert timestamp strings back to datetime
        if isinstance(data.get('start_time'), str):
            import dateutil.parser
            data['start_time'] = dateutil.parser.isoparse(data['start_time'])
            
        if isinstance(data.get('last_updated'), str):
            data['last_updated'] = dateutil.parser.isoparse(data['last_updated'])
            
        return cls(**data)