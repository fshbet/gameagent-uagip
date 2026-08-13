"""
Action model for plugin framework.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional
from datetime import datetime
from enum import Enum


class ActionType(str, Enum):
    """Enumeration of action types."""
    TAP = "tap"
    SWIPE = "swipe"
    WAIT = "wait"
    CUSTOM = "custom"


@dataclass
class Action:
    """
    Represents an action that can be performed by a plugin.
    
    Actions are used to interact with the game or system components.
    """
    
    # Core identifying information
    action_id: str
    action_name: str
    action_type: ActionType
    
    # Action parameters
    parameters: Dict[str, Any] = field(default_factory=dict)
    
    # Timing and metadata
    created_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """
        Validate the Action after initialization.
        
        Raises:
            ValueError: If validation fails
        """
        if not self.action_id:
            raise ValueError("Action ID cannot be empty")
            
        if not self.action_name:
            raise ValueError("Action name cannot be empty")
            
        if not isinstance(self.action_type, ActionType):
            raise ValueError("Invalid action type")
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert Action to dictionary for serialization.
        
        Returns:
            Dictionary representation of the Action
        """
        return {
            'action_id': self.action_id,
            'action_name': self.action_name,
            'action_type': self.action_type.value,
            'parameters': self.parameters,
            'created_at': self.created_at.isoformat(),
            'metadata': self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Action':
        """
        Create Action from dictionary.
        
        Args:
            data: Dictionary with Action data
            
        Returns:
            New Action instance
        """
        # Convert timestamp string back to datetime
        if isinstance(data.get('created_at'), str):
            import dateutil.parser
            data['created_at'] = dateutil.parser.isoparse(data['created_at'])
            
        # Convert action_type string back to enum
        if 'action_type' in data and isinstance(data['action_type'], str):
            data['action_type'] = ActionType(data['action_type'])
            
        return cls(**data)
    
    def is_wait_action(self) -> bool:
        """
        Check if this is a wait action.
        
        Returns:
            True if this is a wait action, False otherwise
        """
        return self.action_type == ActionType.WAIT
    
    def get_wait_duration(self) -> Optional[float]:
        """
        Get the wait duration if this is a wait action.
        
        Returns:
            Wait duration in seconds or None if not a wait action
        """
        if self.is_wait_action() and 'duration' in self.parameters:
            return self.parameters['duration']
        return None