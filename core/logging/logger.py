"""
Logger wrapper for UAGIP logging framework.
Provides a simplified interface over Python's logging module.
"""

import logging
from typing import Any, Dict, Optional
from datetime import datetime


class Logger:
    """
    Wrapper around Python's logging.Logger for simplified usage.
    
    This class provides a clean interface to Python's logging functionality
    with additional convenience methods and consistent behavior.
    """
    
    def __init__(self, name: str, python_logger: logging.Logger) -> None:
        """
        Initialize the Logger wrapper.
        
        Args:
            name (str): Name of the logger
            python_logger (logging.Logger): The underlying Python logger instance
        """
        self._name = name
        self._python_logger = python_logger
    
    @property
    def name(self) -> str:
        """
        Get the logger's name.
        
        Returns:
            str: Logger name
        """
        return self._name
    
    def debug(self, message: str, *args: Any, **kwargs: Any) -> None:
        """
        Log a debug message.
        
        Args:
            message (str): Message to log
            *args: Additional arguments for the message
            **kwargs: Additional keyword arguments for the logging system
        """
        self._python_logger.debug(message, *args, **kwargs)
    
    def info(self, message: str, *args: Any, **kwargs: Any) -> None:
        """
        Log an info message.
        
        Args:
            message (str): Message to log
            *args: Additional arguments for the message
            **kwargs: Additional keyword arguments for the logging system
        """
        self._python_logger.info(message, *args, **kwargs)
    
    def warning(self, message: str, *args: Any, **kwargs: Any) -> None:
        """
        Log a warning message.
        
        Args:
            message (str): Message to log
            *args: Additional arguments for the message
            **kwargs: Additional keyword arguments for the logging system
        """
        self._python_logger.warning(message, *args, **kwargs)
    
    def error(self, message: str, *args: Any, **kwargs: Any) -> None:
        """
        Log an error message.
        
        Args:
            message (str): Message to log
            *args: Additional arguments for the message
            **kwargs: Additional keyword arguments for the logging system
        """
        self._python_logger.error(message, *args, **kwargs)
    
    def critical(self, message: str, *args: Any, **kwargs: Any) -> None:
        """
        Log a critical message.
        
        Args:
            message (str): Message to log
            *args: Additional arguments for the message
            **kwargs: Additional keyword arguments for the logging system
        """
        self._python_logger.critical(message, *args, **kwargs)
    
    def exception(self, message: str, *args: Any, **kwargs: Any) -> None:
        """
        Log an exception with traceback.
        
        Args:
            message (str): Message to log
            *args: Additional arguments for the message
            **kwargs: Additional keyword arguments for the logging system
        """
        self._python_logger.exception(message, *args, **kwargs)
    
    def log(self, level: int, message: str, *args: Any, **kwargs: Any) -> None:
        """
        Log a message with the specified level.
        
        Args:
            level (int): Logging level
            message (str): Message to log
            *args: Additional arguments for the message
            **kwargs: Additional keyword arguments for the logging system
        """
        self._python_logger.log(level, message, *args, **kwargs)
    
    def set_level(self, level: int) -> None:
        """
        Set the logging level for this logger.
        
        Args:
            level (int): Logging level to set
        """
        self._python_logger.setLevel(level)
    
    def get_level(self) -> int:
        """
        Get the current logging level for this logger.
        
        Returns:
            int: Current logging level
        """
        return self._python_logger.level
    
    def is_enabled_for(self, level: int) -> bool:
        """
        Check if a message of the specified level would be logged.
        
        Args:
            level (int): Level to check
            
        Returns:
            bool: True if the level is enabled
        """
        return self._python_logger.isEnabledFor(level)
    
    @property
    def python_logger(self) -> logging.Logger:
        """
        Get the underlying Python logger instance.
        
        Returns:
            logging.Logger: The underlying Python logger
        """
        return self._python_logger
    
    def _get_python_logger(self) -> logging.Logger:
        """
        Get the underlying Python logger instance.
        
        Returns:
            logging.Logger: The underlying Python logger
        """
        return self._python_logger
    
    @property
    def logger(self) -> logging.Logger:
        """
        Get the underlying Python logger instance.
        
        Returns:
            logging.Logger: The underlying Python logger
        """
        return self._python_logger
