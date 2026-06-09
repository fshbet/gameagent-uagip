"""
Initialization module for UAGIP logging framework.
"""

from .log_manager import LogManager
from .logger import Logger

# Create the global logger manager instance
log_manager = LogManager()

def get_logger(name: str) -> Logger:
    """
    Get a logger instance by name.

    Args:
        name (str): Name of the logger

    Returns:
        Logger: Logger instance
    """
    return log_manager.get_logger(name)

# Export for easy import
__all__ = ['log_manager', 'get_logger']