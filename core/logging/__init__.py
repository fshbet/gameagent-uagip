"""
Logging package for UAGIP logging framework.

This module provides a production-grade logging system with the following features:
- Singleton Log Manager pattern
- Console and file output support
- Rotating log files
- JSON formatting options
- Thread-safe operation
- ConfigManager integration
"""

from .log_manager import LogManager
from .logger import Logger
# Formatters are available via from core.logging.formatters import * if needed

__all__ = ['LogManager', 'Logger']

# Create a default instance for easy access
log_manager = LogManager()