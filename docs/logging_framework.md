# UAGIP Logging Framework

The UAGIP logging framework provides a production-grade logging solution with support for multiple output formats, file rotation, and configuration management.

## Features

- **Singleton Log Manager**: Ensures only one logger instance per name
- **Thread-Safe**: Safe for use in multi-threaded applications
- **Console Logging**: Support for DEBUG, INFO, WARNING, ERROR, CRITICAL levels
- **File Logging**: Automatic directory creation and UTF-8 support
- **Rotating Log Files**: Configurable max file size and backup count
- **JSON Logging**: Structured logging for easy parsing
- **ConfigManager Integration**: Load settings from configuration
- **Custom Formatters**: Standard and JSON formatters
- **Error Handling**: Graceful handling of invalid paths and permission issues
- **Type Hints**: Full type safety support

## Installation

The logging framework is included as part of the core package. No additional installation is required.

## Usage

### Basic Usage

```python
from core.logging import log_manager

# Get a logger instance
logger = log_manager.get_logger(__name__)

# Log messages
logger.info("Application started")
logger.error("An error occurred")
```

### Using with ConfigManager

```python
from core.config.config_manager import ConfigManager
from core.logging import log_manager

# Set up configuration manager
config = ConfigManager()
config.load_from_dict({
    'logging': {
        'level': 'DEBUG',
        'file': 'logs/app.log',
        'json': False,
        'max_bytes': 1048576,  # 1MB
        'backup_count': 3
    }
})

# Set config manager in log manager
log_manager.set_config_manager(config)

# Get a logger instance
logger = log_manager.get_logger(__name__)
logger.info("This will be logged to console and file")
```

### JSON Logging

```python
from core.config.config_manager import ConfigManager
from core.logging import log_manager

config = ConfigManager()
config.load_from_dict({
    'logging': {
        'level': 'INFO',
        'file': 'logs/app.log',
        'json': True  # Enable JSON formatting
    }
})

log_manager.set_config_manager(config)
logger = log_manager.get_logger(__name__)
logger.info("This will be logged in JSON format")
```

## Configuration

The logging framework can be configured through the ConfigManager with the following options:

```yaml
logging:
  level: INFO          # Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
  file: logs/app.log   # Path to log file (optional)
  json: false          # Enable JSON formatting (optional)
  max_bytes: 1048576   # Max file size for rotation (optional)
  backup_count: 3      # Number of backup files (optional)
```

## Logger Methods

The logger wrapper supports all standard logging methods:

- `debug(message, *args, **kwargs)`
- `info(message, *args, **kwargs)`
- `warning(message, *args, **kwargs)`
- `error(message, *args, **kwargs)`
- `critical(message, *args, **kwargs)`
- `exception(message, *args, **kwargs)`
- `log(level, message, *args, **kwargs)`

## Error Handling

The logging framework handles the following error conditions gracefully:

- Invalid log paths
- Permission issues when creating log files
- Missing directories (automatically created)
- Configuration errors

## Testing

Unit tests are provided in `tests/test_logging.py` to verify all functionality.

To run the tests:
```bash
python -m pytest tests/test_logging.py
```

## Architecture

The logging framework follows SOLID principles with:

1. **Single Responsibility**: Each class has a single, well-defined responsibility
2. **Open/Closed**: Extensible through inheritance and composition
3. **Liskov Substitution**: Formatters can be used interchangeably
4. **Interface Segregation**: Clean separation of concerns between components
5. **Dependency Inversion**: Uses dependency injection for configuration management

## Thread Safety

The LogManager uses a thread-safe singleton pattern with double-checked locking to ensure thread safety across concurrent access.