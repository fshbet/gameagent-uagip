"""
Plugin health tracking for plugin framework.
"""

import time
from datetime import datetime
from typing import Dict, Any, Optional
from dataclasses import dataclass, field

from core.health.component_health import ComponentHealth


@dataclass
class PluginHealth:
    """
    Tracks health information for a plugin.
    
    This class provides detailed health metrics and status tracking
    for individual plugins within the system.
    """
    
    # Core identification
    plugin_id: str
    plugin_name: str
    
    # Health status
    is_alive: bool = False
    is_running: bool = False
    
    # Timing information
    last_execution: Optional[datetime] = None
    start_time: Optional[datetime] = None
    last_heartbeat: Optional[datetime] = None
    
    # Error tracking
    failures: int = 0
    error_messages: list = field(default_factory=list)
    
    # Performance metrics
    uptime: float = 0.0  # in seconds
    last_execution_time: Optional[float] = None
    
    def __post_init__(self):
        """
        Initialize the PluginHealth instance.
        """
        self.start_time = datetime.now()
        self.last_heartbeat = datetime.now()
    
    def update_heartbeat(self) -> None:
        """
        Update the last heartbeat timestamp.
        """
        self.last_heartbeat = datetime.now()
    
    def mark_execution(self, execution_time: Optional[float] = None) -> None:
        """
        Mark that an execution occurred.
        
        Args:
            execution_time: Time taken for the execution in seconds
        """
        self.last_execution = datetime.now()
        self.last_execution_time = execution_time
        self.update_heartbeat()
    
    def mark_failure(self, error_message: str) -> None:
        """
        Mark a failure occurred.
        
        Args:
            error_message: Description of the error that occurred
        """
        self.failures += 1
        self.error_messages.append(error_message)
        self.update_heartbeat()
        self.is_alive = False  # Mark as not alive on failure
    
    def mark_alive(self) -> None:
        """
        Mark that the plugin is alive.
        """
        self.is_alive = True
        self.update_heartbeat()
    
    def mark_running(self) -> None:
        """
        Mark that the plugin is running.
        """
        self.is_running = True
        self.mark_alive()
    
    def mark_stopped(self) -> None:
        """
        Mark that the plugin has stopped.
        """
        self.is_running = False
        self.update_heartbeat()
    
    def get_uptime(self) -> float:
        """
        Get the current uptime in seconds.
        
        Returns:
            Uptime in seconds
        """
        if self.start_time:
            return (datetime.now() - self.start_time).total_seconds()
        return 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert PluginHealth to dictionary for serialization.
        
        Returns:
            Dictionary representation of the PluginHealth
        """
        return {
            'plugin_id': self.plugin_id,
            'plugin_name': self.plugin_name,
            'is_alive': self.is_alive,
            'is_running': self.is_running,
            'last_execution': self.last_execution.isoformat() if self.last_execution else None,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'last_heartbeat': self.last_heartbeat.isoformat() if self.last_heartbeat else None,
            'failures': self.failures,
            'error_messages': self.error_messages,
            'uptime': self.get_uptime(),
            'last_execution_time': self.last_execution_time
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PluginHealth':
        """
        Create PluginHealth from dictionary.
        
        Args:
            data: Dictionary with PluginHealth data
            
        Returns:
            New PluginHealth instance
        """
        # Convert timestamp strings back to datetime
        if isinstance(data.get('last_execution'), str):
            import dateutil.parser
            data['last_execution'] = dateutil.parser.isoparse(data['last_execution'])
            
        if isinstance(data.get('start_time'), str):
            data['start_time'] = dateutil.parser.isoparse(data['start_time'])
            
        if isinstance(data.get('last_heartbeat'), str):
            data['last_heartbeat'] = dateutil.parser.isoparse(data['last_heartbeat'])
            
        return cls(**data)
    
    def get_component_health(self) -> ComponentHealth:
        """
        Convert PluginHealth to ComponentHealth for integration with HealthMonitor.
        
        Returns:
            ComponentHealth instance
        """
        status = "healthy" if self.is_alive else "unhealthy"
        message = f"Plugin {self.plugin_name} is {'running' if self.is_running else 'stopped'}"
        
        if self.failures > 0:
            message += f" with {self.failures} failures"
            
        return ComponentHealth(
            component_id=f"plugin-{self.plugin_id}",
            status=status,
            message=message,
            last_updated=self.last_heartbeat
        )