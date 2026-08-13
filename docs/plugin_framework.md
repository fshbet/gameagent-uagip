# Plugin Framework Documentation

This document provides comprehensive documentation for the GameAgent Plugin Framework, which enables developers to create custom plugins for various games and applications.

## Architecture Overview

The plugin framework is designed to be modular, extensible, and production-ready. It provides a standardized interface for game automation plugins while maintaining loose coupling between components.

### Core Components

1. **GamePlugin** - Abstract base class that all plugins must inherit from
2. **PluginContext** - Provides access to system components without direct instantiation
3. **GameState** - Represents the current state of a game or application
4. **Action** - Defines actions that can be executed by plugins
5. **PluginManager** - Manages plugin lifecycle and registration
6. **PluginHealth** - Tracks health metrics for individual plugins
7. **PluginMetrics** - Collects performance and execution statistics

## Plugin Lifecycle

The lifecycle of a plugin follows these stages:

1. **Registration** - Plugin is registered with the PluginManager
2. **Loading** - Plugin is loaded into memory
3. **Initialization** - Plugin performs setup operations
4. **Start** - Plugin begins executing
5. **Execution** - Plugin detects states and executes actions
6. **Pause/Resume** - Plugin can be paused and resumed
7. **Stop** - Plugin stops execution
8. **Unloading** - Plugin is removed from memory

## GamePlugin Base Class

The `GamePlugin` class serves as the foundation for all plugins. It defines abstract methods that must be implemented by concrete plugin classes.

### Properties

- `plugin_id`: Unique identifier for the plugin
- `plugin_name`: Human-readable name of the plugin
- `plugin_version`: Version string of the plugin
- `supported_platforms`: List of platforms this plugin supports (Android, Windows, etc.)
- `plugin_status`: Current status of the plugin
- `created_at`: Timestamp when the plugin was created

### Methods

#### Lifecycle Methods

```python
def initialize(self) -> bool:
    """Initialize the plugin. Returns True if successful."""
    pass

def start(self) -> bool:
    """Start the plugin execution. Returns True if successful."""
    pass

def stop(self) -> bool:
    """Stop the plugin execution. Returns True if successful."""
    pass

def pause(self) -> bool:
    """Pause the plugin execution. Returns True if successful."""
    pass

def resume(self) -> bool:
    """Resume the plugin execution. Returns True if successful."""
    pass

def shutdown(self) -> bool:
    """Shut down the plugin. Returns True if successful."""
    pass
```

#### Vision Methods

```python
def detect_state(self) -> GameState:
    """Detect and return the current game state."""
    pass

def validate_state(self, state: GameState) -> bool:
    """Validate if the given state is correct."""
    pass
```

#### Action Methods

```python
def available_actions(self) -> list:
    """Return a list of available actions for this plugin."""
    pass

def execute_action(self, action: Action) -> bool:
    """Execute the given action. Returns True if successful."""
    pass
```

#### Health Methods

```python
def health_check(self) -> dict:
    """Perform a health check and return status information."""
    pass
```

## PluginContext

The `PluginContext` provides access to system components without direct instantiation, following dependency injection principles.

### Available Components

- `config_manager`: Access to configuration management
- `logger`: Logging framework integration
- `event_bus`: Event broadcasting and listening
- `health_monitor`: System health monitoring
- `capture_manager`: Screen capture functionality
- `vision_manager`: Vision processing capabilities

## GameState Model

The `GameState` dataclass represents the current state of a game or application.

### Properties

- `game_name`: Name of the game
- `screen_name`: Name of the current screen
- `state_id`: Unique identifier for this state
- `confidence`: Confidence level of state detection (0.0 to 1.0)
- `detected_elements`: List of detected UI elements
- `timestamp`: When the state was detected
- `metadata`: Additional contextual information

## Action Model

The `Action` dataclass defines actions that can be executed by plugins.

### Properties

- `action_id`: Unique identifier for the action
- `action_name`: Human-readable name of the action
- `action_type`: Type of action (tap, swipe, wait, custom)
- `parameters`: Action-specific parameters
- `created_at`: When the action was created
- `metadata`: Additional contextual information

### Action Types

- `TAP`: Tap on a specific coordinate
- `SWIPE`: Swipe from one point to another
- `WAIT`: Wait for a specified duration
- `CUSTOM`: Custom action defined by the plugin

## PluginManager

The `PluginManager` handles registration, loading, and lifecycle management of plugins.

### Methods

```python
def register_plugin(self, plugin_class: type) -> bool:
    """Register a plugin class."""
    pass

def unregister_plugin(self, plugin_id: str) -> bool:
    """Unregister a plugin by ID."""
    pass

def load_plugin(self, plugin_class: type, plugin_id: str, 
                plugin_name: str, plugin_version: str, 
                supported_platforms: list) -> GamePlugin:
    """Load and instantiate a plugin."""
    pass

def unload_plugin(self, plugin_id: str) -> bool:
    """Unload a plugin by ID."""
    pass

def start_plugin(self, plugin_id: str) -> bool:
    """Start a loaded plugin."""
    pass

def stop_plugin(self, plugin_id: str) -> bool:
    """Stop a running plugin."""
    pass

def get_plugin(self, plugin_id: str) -> GamePlugin:
    """Get a plugin by ID."""
    pass

def list_plugins(self) -> list:
    """List all loaded plugins."""
    pass
```

## PluginHealth

The `PluginHealth` class tracks health information for individual plugins.

### Properties

- `plugin_id`: Identifier of the plugin
- `plugin_name`: Name of the plugin
- `is_alive`: Whether the plugin is alive (not crashed)
- `is_running`: Whether the plugin is currently running
- `last_execution`: Timestamp of last execution
- `start_time`: When the plugin was started
- `last_heartbeat`: Last heartbeat timestamp
- `failures`: Number of failures encountered
- `error_messages`: List of error messages
- `uptime`: Plugin uptime in seconds
- `last_execution_time`: Time taken for last execution

## PluginMetrics

The `PluginMetrics` class collects performance and execution statistics.

### Properties

- `plugin_id`: Identifier of the plugin
- `plugin_name`: Name of the plugin
- `actions_executed`: Total actions executed
- `actions_successful`: Successful actions
- `actions_failed`: Failed actions
- `state_detections`: Total state detections
- `state_detections_successful`: Successful state detections
- `state_detections_failed`: Failed state detections
- `total_failures`: Total number of failures
- `error_messages`: List of error messages
- `execution_latency`: Latest execution time
- `total_execution_time`: Cumulative execution time
- `last_execution_time`: Time taken for last execution
- `start_time`: When metrics collection started
- `last_updated`: Last update timestamp

### Methods

```python
def get_success_rate(self) -> float:
    """Calculate the success rate for actions."""
    pass

def get_state_detection_success_rate(self) -> float:
    """Calculate the success rate for state detections."""
    pass

def get_total_execution_time(self) -> float:
    """Get total execution time."""
    pass
```

## Event Bus Integration

The plugin framework publishes events to the EventBus:

- `PLUGIN_REGISTERED`
- `PLUGIN_LOADED`
- `PLUGIN_STARTED`
- `PLUGIN_STOPPED`
- `PLUGIN_FAILED`

These events allow for monitoring and integration with other system components.

## Logging Integration

All plugin lifecycle operations are logged using the system's logging framework, providing visibility into plugin behavior and issues.

## Platform Support

The framework supports multiple platforms:

- Android
- Windows
- Emulator

Platform-specific implementations can be added as needed without modifying core components.

## Development Guide

### Creating a New Plugin

1. Create a new class that inherits from `GamePlugin`
2. Implement all abstract methods
3. Use the provided context to access system components
4. Register your plugin with the `PluginManager`

### Example Plugin Implementation

```python
from plugins.base import GamePlugin, PluginContext, GameState, Action

class MyGamePlugin(GamePlugin):
    def __init__(self, plugin_id: str, plugin_name: str, plugin_version: str,
                 supported_platforms: list, context: PluginContext):
        super().__init__(plugin_id, plugin_name, plugin_version, 
                        supported_platforms, context)
    
    def initialize(self) -> bool:
        # Initialize your plugin here
        return True
    
    def start(self) -> bool:
        # Start plugin execution
        return True
    
    def detect_state(self) -> GameState:
        # Detect current game state
        return GameState(
            game_name="MyGame",
            screen_name="main_menu",
            state_id="state_1",
            confidence=0.95,
            detected_elements=["button_start", "button_settings"],
            timestamp=datetime.now(),
            metadata={}
        )
    
    def execute_action(self, action: Action) -> bool:
        # Execute the given action
        return True
    
    # Implement other required methods...
```

## Future Game Plugin Examples

The following game plugins are planned for implementation:

- Shadow Fight 3 plugin
- Clash of Clans plugin  
- Hay Day plugin
- Minecraft plugin

These will demonstrate how to implement platform-specific logic while maintaining the framework's abstraction.

## Testing

All plugin framework components are tested with comprehensive unit tests that cover:

- Plugin registration and lifecycle management
- State creation and validation
- Action execution
- Metrics tracking
- Health integration
- Thread safety

Run tests using:
```bash
python -m pytest tests/test_plugin_framework.py -v
```

## Validation

The plugin framework has been validated to ensure:

- All existing tests continue to pass
- Plugin tests pass successfully
- No regressions are introduced
- No warnings or errors are present
- Code is production-ready and follows best practices