"""
Event types for UAGIP Event Bus.
"""

from typing import Set


class EventType:
    """
    Defines all standard event types for the UAGIP system.
    """
    
    # System events
    SYSTEM_STARTUP = "system.startup"
    SYSTEM_SHUTDOWN = "system.shutdown"
    
    # Configuration events
    CONFIG_LOADED = "config.loaded"
    CONFIG_CHANGED = "config.changed"
    
    # Capture events
    CAPTURE_STARTED = "capture.started"
    CAPTURE_STOPPED = "capture.stopped"
    
    # Frame capture events
    FRAME_CAPTURED = "frame.captured"
    
    # Object detection events
    OBJECT_DETECTED = "object.detected"
    
    # Action execution events
    ACTION_EXECUTED = "action.executed"
    
    # Learning events
    LEARNING_UPDATE = "learning.update"
    
    # Video events
    VIDEO_CREATED = "video.created"
    
    # Plugin events
    PLUGIN_LOADED = "plugin.loaded"
    PLUGIN_UNLOADED = "plugin.unloaded"
    
    # All standard event types
    ALL_STANDARD_TYPES: Set[str] = {
        SYSTEM_STARTUP,
        SYSTEM_SHUTDOWN,
        CONFIG_LOADED,
        CONFIG_CHANGED,
        CAPTURE_STARTED,
        CAPTURE_STOPPED,
        FRAME_CAPTURED,
        OBJECT_DETECTED,
        ACTION_EXECUTED,
        LEARNING_UPDATE,
        VIDEO_CREATED,
        PLUGIN_LOADED,
        PLUGIN_UNLOADED
    }
    
    @classmethod
    def is_standard_type(cls, event_type: str) -> bool:
        """
        Check if an event type is a standard UAGIP event type.
        
        Args:
            event_type: The event type to check
            
        Returns:
            True if the event type is a standard UAGIP event type, False otherwise
        """
        return event_type in cls.ALL_STANDARD_TYPES
    
    @classmethod
    def get_all_standard_types(cls) -> Set[str]:
        """
        Get all standard UAGIP event types.
        
        Returns:
            A set of all standard event types
        """
        return cls.ALL_STANDARD_TYPES.copy()