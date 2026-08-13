"""
Plugin manager for loading, registering, and managing game plugins.
"""

import threading
from typing import Dict, List, Optional, Type
from collections import OrderedDict
import logging

from .game_plugin import GamePlugin
from .plugin_context import PluginContext
from core.events.event_bus import EventBus
from core.health.health_monitor import HealthMonitor


class PluginManager:
    """
    Manages game plugins including registration, loading, and execution.
    
    This class provides thread-safe operations for plugin lifecycle management.
    """
    
    def __init__(self, context: PluginContext):
        """
        Initialize the PluginManager.
        
        Args:
            context: PluginContext instance for accessing system components
        """
        self._context = context
        self._plugins: OrderedDict[str, GamePlugin] = OrderedDict()
        self._lock = threading.RLock()  # Reentrant lock for thread safety
        self._logger = context.logger
        
        # Register with EventBus for plugin lifecycle events
        self._event_bus = context.event_bus
        self._health_monitor = context.health_monitor
        
    @property
    def context(self) -> PluginContext:
        """Get the plugin context."""
        return self._context
    
    def register_plugin(self, plugin_class: Type[GamePlugin]) -> bool:
        """
        Register a plugin class for later loading.
        
        Args:
            plugin_class: GamePlugin subclass to register
            
        Returns:
            True if registration was successful, False otherwise
        """
        with self._lock:
            try:
                # Create an instance to get plugin metadata
                plugin_instance = plugin_class(
                    plugin_id="temp_id",
                    plugin_name="temp_name", 
                    plugin_version="0.0.0",
                    supported_platforms=[],
                    context=self._context
                )
                
                # Register with EventBus
                self._event_bus.publish("PLUGIN_REGISTERED", {
                    "plugin_id": plugin_instance.plugin_id,
                    "plugin_name": plugin_instance.plugin_name,
                    "plugin_version": plugin_instance.plugin_version
                })
                
                self._logger.info(f"Plugin registered: {plugin_instance.plugin_name}")
                return True
                
            except Exception as e:
                self._logger.error(f"Failed to register plugin: {str(e)}")
                return False
    
    def unregister_plugin(self, plugin_id: str) -> bool:
        """
        Unregister a plugin.
        
        Args:
            plugin_id: ID of the plugin to unregister
            
        Returns:
            True if unregistration was successful, False otherwise
        """
        with self._lock:
            try:
                if plugin_id in self._plugins:
                    plugin = self._plugins[plugin_id]
                    # Stop the plugin if it's running
                    if plugin.plugin_status.value != "stopped":
                        plugin.stop()
                    
                    # Remove from registry
                    del self._plugins[plugin_id]
                    
                    # Publish event
                    self._event_bus.publish("PLUGIN_UNREGISTERED", {
                        "plugin_id": plugin_id
                    })
                    
                    self._logger.info(f"Plugin unregistered: {plugin_id}")
                    return True
                    
            except Exception as e:
                self._logger.error(f"Failed to unregister plugin {plugin_id}: {str(e)}")
                return False
            
            return False
    
    def load_plugin(self, plugin_class: Type[GamePlugin], 
                   plugin_id: str, plugin_name: str, 
                   plugin_version: str, supported_platforms: List[str]) -> Optional[GamePlugin]:
        """
        Load and initialize a plugin.
        
        Args:
            plugin_class: GamePlugin subclass to load
            plugin_id: Unique identifier for the plugin
            plugin_name: Human-readable name of the plugin
            plugin_version: Version of the plugin
            supported_platforms: List of platforms this plugin supports
            
        Returns:
            Plugin instance if successful, None otherwise
        """
        with self._lock:
            try:
                # Create plugin instance
                plugin = plugin_class(
                    plugin_id=plugin_id,
                    plugin_name=plugin_name,
                    plugin_version=plugin_version,
                    supported_platforms=supported_platforms,
                    context=self._context
                )
                
                # Initialize the plugin
                if not plugin.initialize():
                    self._logger.error(f"Failed to initialize plugin: {plugin_name}")
                    return None
                
                # Store in registry
                self._plugins[plugin_id] = plugin
                
                # Publish event
                self._event_bus.publish("PLUGIN_LOADED", {
                    "plugin_id": plugin_id,
                    "plugin_name": plugin_name,
                    "plugin_version": plugin_version
                })
                
                self._logger.info(f"Plugin loaded: {plugin_name}")
                return plugin
                
            except Exception as e:
                self._logger.error(f"Failed to load plugin {plugin_name}: {str(e)}")
                return None
    
    def unload_plugin(self, plugin_id: str) -> bool:
        """
        Unload a plugin.
        
        Args:
            plugin_id: ID of the plugin to unload
            
        Returns:
            True if unloading was successful, False otherwise
        """
        with self._lock:
            try:
                if plugin_id in self._plugins:
                    plugin = self._plugins[plugin_id]
                    
                    # Stop the plugin if it's running
                    if plugin.plugin_status.value != "stopped":
                        plugin.stop()
                    
                    # Shutdown the plugin
                    if not plugin.shutdown():
                        self._logger.error(f"Failed to shutdown plugin: {plugin_id}")
                        return False
                    
                    # Remove from registry
                    del self._plugins[plugin_id]
                    
                    # Publish event
                    self._event_bus.publish("PLUGIN_UNLOADED", {
                        "plugin_id": plugin_id
                    })
                    
                    self._logger.info(f"Plugin unloaded: {plugin_id}")
                    return True
                    
            except Exception as e:
                self._logger.error(f"Failed to unload plugin {plugin_id}: {str(e)}")
                return False
            
            return False
    
    def start_plugin(self, plugin_id: str) -> bool:
        """
        Start a loaded plugin.
        
        Args:
            plugin_id: ID of the plugin to start
            
        Returns:
            True if start was successful, False otherwise
        """
        with self._lock:
            try:
                if plugin_id not in self._plugins:
                    self._logger.error(f"Plugin {plugin_id} not found")
                    return False
                
                plugin = self._plugins[plugin_id]
                
                # Start the plugin
                if not plugin.start():
                    self._logger.error(f"Failed to start plugin: {plugin_id}")
                    return False
                
                # Publish event
                self._event_bus.publish("PLUGIN_STARTED", {
                    "plugin_id": plugin_id,
                    "plugin_name": plugin.plugin_name
                })
                
                self._logger.info(f"Plugin started: {plugin_id}")
                return True
                
            except Exception as e:
                self._logger.error(f"Failed to start plugin {plugin_id}: {str(e)}")
                return False
    
    def stop_plugin(self, plugin_id: str) -> bool:
        """
        Stop a running plugin.
        
        Args:
            plugin_id: ID of the plugin to stop
            
        Returns:
            True if stop was successful, False otherwise
        """
        with self._lock:
            try:
                if plugin_id not in self._plugins:
                    self._logger.error(f"Plugin {plugin_id} not found")
                    return False
                
                plugin = self._plugins[plugin_id]
                
                # Stop the plugin
                if not plugin.stop():
                    self._logger.error(f"Failed to stop plugin: {plugin_id}")
                    return False
                
                # Publish event
                self._event_bus.publish("PLUGIN_STOPPED", {
                    "plugin_id": plugin_id,
                    "plugin_name": plugin.plugin_name
                })
                
                self._logger.info(f"Plugin stopped: {plugin_id}")
                return True
                
            except Exception as e:
                self._logger.error(f"Failed to stop plugin {plugin_id}: {str(e)}")
                return False
    
    def get_plugin(self, plugin_id: str) -> Optional[GamePlugin]:
        """
        Get a plugin by ID.
        
        Args:
            plugin_id: ID of the plugin to retrieve
            
        Returns:
            Plugin instance if found, None otherwise
        """
        with self._lock:
            return self._plugins.get(plugin_id)
    
    def list_plugins(self) -> List[GamePlugin]:
        """
        Get a list of all loaded plugins.
        
        Returns:
            List of all loaded plugins
        """
        with self._lock:
            return list(self._plugins.values())
    
    def get_plugin_count(self) -> int:
        """
        Get the number of loaded plugins.
        
        Returns:
            Number of loaded plugins
        """
        with self._lock:
            return len(self._plugins)