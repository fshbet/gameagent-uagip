"""
Base class for game plugins.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum

from .plugin_context import PluginContext
from .game_state import GameState
from .action import Action


class PluginStatus(str, Enum):
    """Enumeration of plugin statuses."""
    STOPPED = "stopped"
    RUNNING = "running"
    PAUSED = "paused"
    FAILED = "failed"
    UNLOADED = "unloaded"


class GamePlugin(ABC):
    """
    Abstract base class for game plugins.
    
    All game plugins must inherit from this class and implement
    the required methods.
    """

    def __init__(
        self,
        plugin_id: str,
        plugin_name: str,
        plugin_version: str,
        supported_platforms: List[str],
        context: PluginContext
    ):
        """
        Initialize a GamePlugin.
        
        Args:
            plugin_id: Unique identifier for the plugin
            plugin_name: Human-readable name of the plugin
            plugin_version: Version of the plugin
            supported_platforms: List of platforms this plugin supports
            context: PluginContext instance for accessing system components
        """
        self.plugin_id = plugin_id
        self.plugin_name = plugin_name
        self.plugin_version = plugin_version
        self.supported_platforms = supported_platforms
        self.plugin_status = PluginStatus.STOPPED
        self.created_at = datetime.now()
        self._context = context

    @property
    def context(self) -> PluginContext:
        """Get the plugin context."""
        return self._context

    @abstractmethod
    def initialize(self) -> bool:
        """
        Initialize the plugin.
        
        Returns:
            True if initialization was successful, False otherwise
            
        Raises:
            Exception: If initialization fails
        """
        pass

    @abstractmethod
    def start(self) -> bool:
        """
        Start the plugin execution.
        
        Returns:
            True if start was successful, False otherwise
            
        Raises:
            Exception: If start fails
        """
        pass

    @abstractmethod
    def stop(self) -> bool:
        """
        Stop the plugin execution.
        
        Returns:
            True if stop was successful, False otherwise
            
        Raises:
            Exception: If stop fails
        """
        pass

    @abstractmethod
    def pause(self) -> bool:
        """
        Pause the plugin execution.
        
        Returns:
            True if pause was successful, False otherwise
            
        Raises:
            Exception: If pause fails
        """
        pass

    @abstractmethod
    def resume(self) -> bool:
        """
        Resume the plugin execution.
        
        Returns:
            True if resume was successful, False otherwise
            
        Raises:
            Exception: If resume fails
        """
        pass

    @abstractmethod
    def shutdown(self) -> bool:
        """
        Shutdown the plugin completely.
        
        Returns:
            True if shutdown was successful, False otherwise
            
        Raises:
            Exception: If shutdown fails
        """
        pass

    @abstractmethod
    def detect_state(self) -> GameState:
        """
        Detect and return the current game state.
        
        Returns:
            GameState object representing the detected state
            
        Raises:
            Exception: If state detection fails
        """
        pass

    @abstractmethod
    def validate_state(self, state: GameState) -> bool:
        """
        Validate if the given state is correct.
        
        Args:
            state: GameState to validate
            
        Returns:
            True if state is valid, False otherwise
            
        Raises:
            Exception: If validation fails
        """
        pass

    @abstractmethod
    def available_actions(self) -> List[Action]:
        """
        Get list of actions this plugin can perform.
        
        Returns:
            List of available Action objects
            
        Raises:
            Exception: If action listing fails
        """
        pass

    @abstractmethod
    def execute_action(self, action: Action) -> bool:
        """
        Execute a given action.
        
        Args:
            action: Action to execute
            
        Returns:
            True if execution was successful, False otherwise
            
        Raises:
            Exception: If execution fails
        """
        pass

    @abstractmethod
    def health_check(self) -> Dict[str, Any]:
        """
        Perform health check for this plugin.
        
        Returns:
            Dictionary with health status information
            
        Raises:
            Exception: If health check fails
        """
        pass