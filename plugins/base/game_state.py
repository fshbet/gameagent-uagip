"""
Game state model for plugin framework.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List
from datetime import datetime


@dataclass
class GameState:
    """
    Represents the current game state detected by a plugin.
    
    This dataclass stores information about the detected state of a game,
    including screen details, confidence levels, and metadata.
    """
    
    # Core identifying information
    game_name: str
    screen_name: str
    state_id: str
    
    # Detection quality metrics
    confidence: float = 0.0
    detected_elements: List[str] = field(default_factory=list)
    
    # Timing and metadata
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """
        Validate the GameState after initialization.
        
        Raises:
            ValueError: If validation fails
        """
        if self.confidence < 0.0 or self.confidence > 1.0:
            raise ValueError("Confidence must be between 0.0 and 1.0")
        
        if not self.game_name:
            raise ValueError("Game name cannot be empty")
            
        if not self.screen_name:
            raise ValueError("Screen name cannot be empty")
            
        if not self.state_id:
            raise ValueError("State ID cannot be empty")
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert GameState to dictionary for serialization.
        
        Returns:
            Dictionary representation of the GameState
        """
        return {
            'game_name': self.game_name,
            'screen_name': self.screen_name,
            'state_id': self.state_id,
            'confidence': self.confidence,
            'detected_elements': self.detected_elements,
            'timestamp': self.timestamp.isoformat(),
            'metadata': self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'GameState':
        """
        Create GameState from dictionary.
        
        Args:
            data: Dictionary with GameState data
            
        Returns:
            New GameState instance
        """
        # Convert timestamp string back to datetime
        if isinstance(data.get('timestamp'), str):
            import dateutil.parser
            data['timestamp'] = dateutil.parser.isoparse(data['timestamp'])
            
        return cls(**data)