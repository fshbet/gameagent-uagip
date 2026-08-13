"""
Plugin context providing access to system components.
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass

from core.config.config_manager import ConfigManager
from core.logging.logger import Logger
from core.events.event_bus import EventBus
from core.health.health_monitor import HealthMonitor
from capture.capture_manager import CaptureManager
from vision.vision_manager import VisionManager


@dataclass
class PluginContext:
    """
    Context providing access to system components for plugins.
    
    Plugins must never instantiate these components directly.
    Instead, they should use the context to access them.
    """
    
    config_manager: ConfigManager
    logger: Logger
    event_bus: EventBus
    health_monitor: HealthMonitor
    capture_manager: CaptureManager
    vision_manager: VisionManager
    
    def get_component(self, component_name: str) -> Optional[Any]:
        """
        Get a specific component by name.
        
        Args:
            component_name: Name of the component to retrieve
            
        Returns:
            The requested component or None if not found
        """
        components = {
            'config_manager': self.config_manager,
            'logger': self.logger,
            'event_bus': self.event_bus,
            'health_monitor': self.health_monitor,
            'capture_manager': self.capture_manager,
            'vision_manager': self.vision_manager
        }
        
        return components.get(component_name)
    
    def get_config(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value.
        
        Args:
            key: Configuration key
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        return self.config_manager.get(key, default)
    
    def log_info(self, message: str) -> None:
        """
        Log an info message.
        
        Args:
            message: Message to log
        """
        self.logger.info(message)
    
    def log_error(self, message: str) -> None:
        """
        Log an error message.
        
        Args:
            message: Message to log
        """
        self.logger.error(message)
    
    def log_debug(self, message: str) -> None:
        """
        Log a debug message.
        
        Args:
            message: Message to log
        """
        self.logger.debug(message)
    
    def publish_event(self, event_type: str, data: Dict[str, Any]) -> None:
        """
        Publish an event to the EventBus.
        
        Args:
            event_type: Type of event to publish
            data: Event data
        """
        self.event_bus.publish(event_type, data)