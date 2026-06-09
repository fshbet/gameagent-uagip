"""
Formatters for UAGIP logging framework.
Provides custom formatters for console and file output.
"""

import json
import logging
from datetime import datetime
from typing import Any, Dict


class StandardFormatter(logging.Formatter):
    """
    Standard formatter for log messages.
    
    Formats log messages with timestamp, logger name, level, and message.
    """
    
    def format(self, record: logging.LogRecord) -> str:
        """
        Format the log record into a standard string format.
        
        Args:
            record (logging.LogRecord): The log record to format
            
        Returns:
            str: Formatted log message
        """
        # Create timestamp with microseconds
        timestamp = datetime.fromtimestamp(record.created).strftime('%Y-%m-%d %H:%M:%S.%f')
        
        # Format the message
        formatted_message = f"[{timestamp}] {record.levelname} [{record.name}] {record.getMessage()}"
        
        # Add exception info if present
        if record.exc_info:
            formatted_message += f"\n{self.formatException(record.exc_info)}"
            
        return formatted_message


class JSONFormatter(logging.Formatter):
    """
    JSON formatter for log messages.
    
    Formats log messages as structured JSON objects for easy parsing.
    """
    
    def format(self, record: logging.LogRecord) -> str:
        """
        Format the log record into a JSON string.
        
        Args:
            record (logging.LogRecord): The log record to format
            
        Returns:
            str: Formatted JSON log message
        """
        # Create the base log entry
        log_entry: Dict[str, Any] = {
            'timestamp': datetime.fromtimestamp(record.created).strftime('%Y-%m-%d %H:%M:%S.%f'),
            'level': record.levelname,
            'module': record.module,
            'message': record.getMessage()
        }
        
        # Add additional fields if they exist
        if hasattr(record, 'filename'):
            log_entry['filename'] = record.filename
        if hasattr(record, 'lineno'):
            log_entry['lineno'] = record.lineno
        if hasattr(record, 'funcName'):
            log_entry['function'] = record.funcName
            
        # Add exception info if present
        if record.exc_info:
            log_entry['exception'] = self.formatException(record.exc_info)
            
        # Serialize to JSON
        return json.dumps(log_entry, ensure_ascii=False)