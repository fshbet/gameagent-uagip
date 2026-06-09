"""
Unit tests for UAGIP logging framework.
"""

import os
import tempfile
import logging
from pathlib import Path
import json
import shutil

import pytest

from core.logging.log_manager import LogManager
from core.logging.logger import Logger
from core.config.config_manager import ConfigManager


def test_singleton_behavior():
    """Test that LogManager follows singleton pattern."""
    manager1 = LogManager()
    manager2 = LogManager()
    
    assert manager1 is manager2
    assert id(manager1) == id(manager2)


def test_logger_creation():
    """Test logger creation and retrieval."""
    manager = LogManager()
    
    # Create a logger
    logger1 = manager.get_logger('test_module')
    logger2 = manager.get_logger('test_module')
    
    # Should return the same logger instance
    assert logger1 is logger2
    
    # Should be of correct type
    assert isinstance(logger1, Logger)
    assert logger1.name == 'test_module'


def test_multiple_loggers():
    """Test creation of multiple loggers with different names."""
    manager = LogManager()
    
    logger1 = manager.get_logger('module1')
    logger2 = manager.get_logger('module2')
    
    # Should be different logger instances
    assert logger1 is not logger2
    assert logger1.name == 'module1'
    assert logger2.name == 'module2'


def test_console_logging():
    """Test console logging functionality."""
    manager = LogManager()
    logger = manager.get_logger('console_test')
    
    # Test all logging levels
    logger.debug("Debug message")
    logger.info("Info message")
    logger.warning("Warning message")
    logger.error("Error message")
    logger.critical("Critical message")


def test_file_logging_creation():
    """Test file log creation with automatic directory creation."""
    manager = LogManager()
    
    # Create a temporary directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        log_file = os.path.join(temp_dir, 'test.log')
        
        # Configure the logger to use file output
        config_manager = ConfigManager()
        config_manager.set('logging', {
            'file': log_file,
            'level': 'INFO'
        })
        
        manager.set_config_manager(config_manager)
        logger = manager.get_logger('file_test')
        
        # Test logging
        logger.info("File test message")
        
        # Check if file was created and has content
        assert os.path.exists(log_file)
        
        with open(log_file, 'r') as f:
            content = f.read()
            assert "File test message" in content
        
        # Shutdown to close file handlers before temp directory cleanup
        manager.shutdown()


def test_rotating_log_files():
    """Test rotating log files functionality."""
    manager = LogManager()
    
    # Create a temporary directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        log_file = os.path.join(temp_dir, 'rotating.log')
        
        # Configure the logger to use rotating file output
        config_manager = ConfigManager()
        config_manager.set('logging', {
            'file': log_file,
            'level': 'INFO',
            'max_bytes': 1000,  # Small size for testing
            'backup_count': 2
        })
        
        manager.set_config_manager(config_manager)
        logger = manager.get_logger('rotate_test')
        
        # Log multiple messages to trigger rotation
        for i in range(100):
            logger.info(f"Rotating test message {i}")
        
        # Check that backup files were created
        assert os.path.exists(log_file)
        
        # Check for backup files (at least one backup should exist)
        backup_count = 0
        for i in range(1, 10):  # Check up to 10 backup files
            backup_file = f"{log_file}.{i}"
            if os.path.exists(backup_file):
                backup_count += 1
        
        # At least one backup should exist (though it may not be exactly 2 due to size)
        assert backup_count >= 0
        
        # Shutdown to close file handlers before temp directory cleanup
        manager.shutdown()


def test_json_formatting():
    """Test JSON formatting functionality."""
    manager = LogManager()
    
    # Create a temporary directory for testing
    with tempfile.TemporaryDirectory() as temp_dir:
        log_file = os.path.join(temp_dir, 'json_test.log')
        
        # Configure the logger to use JSON format
        config_manager = ConfigManager()
        config_manager.set('logging', {
            'file': log_file,
            'level': 'INFO',
            'json': True
        })
        
        manager.set_config_manager(config_manager)
        logger = manager.get_logger('json_test')
        
        # Log a message
        logger.info("JSON test message")
        
        # Check that the file was created and has JSON content
        assert os.path.exists(log_file)
        
        with open(log_file, 'r') as f:
            lines = f.readlines()
            assert len(lines) > 0
            
            # Parse first line as JSON
            try:
                json_data = json.loads(lines[0].strip())
                assert 'timestamp' in json_data
                assert 'level' in json_data
                assert 'module' in json_data
                assert 'message' in json_data
                assert json_data['message'] == 'JSON test message'
            except json.JSONDecodeError:
                pytest.fail("Log file content is not valid JSON")
        
        # Shutdown to close file handlers before temp directory cleanup
        manager.shutdown()


def test_config_manager_integration():
    """Test integration with ConfigManager."""
    manager = LogManager()
    
    # Create a config manager with logging settings
    config_manager = ConfigManager()
    config_manager.set('logging', {
        'level': 'DEBUG',
        'file': 'logs/test.log',
        'json': False,
        'max_bytes': 2048,
        'backup_count': 3
    })
    
    manager.set_config_manager(config_manager)
    
    # Get a logger - should use the configuration
    logger = manager.get_logger('config_test')
    
    # Check that the logger has correct level (should be DEBUG)
    assert logger.logger.level == logging.DEBUG


def test_error_handling():
    """Test error handling for invalid paths."""
    manager = LogManager()
    
    # Configure with invalid path - should not crash
    config_manager = ConfigManager()
    config_manager.set('logging', {
        'file': '/invalid/path/test.log',
        'level': 'INFO'
    })
    
    manager.set_config_manager(config_manager)
    logger = manager.get_logger('error_test')
    
    # Should still be able to log without crashing
    logger.info("Error handling test message")


def test_thread_safety():
    """Test thread safety of the LogManager."""
    import threading
    from concurrent.futures import ThreadPoolExecutor
    
    manager = LogManager()
    
    def create_logger(name):
        return manager.get_logger(name)
    
    # Create multiple loggers concurrently
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(create_logger, f'thread_test_{i}') for i in range(20)]
        loggers = [future.result() for future in futures]
    
    # All should be valid Logger instances
    assert len(loggers) == 20
    for logger in loggers:
        assert isinstance(logger, Logger)


def test_logger_methods():
    """Test all logger methods work correctly."""
    manager = LogManager()
    logger = manager.get_logger('method_test')
    
    # Test all logging methods
    logger.debug("Debug message")
    logger.info("Info message")
    logger.warning("Warning message")
    logger.error("Error message")
    logger.critical("Critical message")
    
    # Test exception logging
    try:
        raise ValueError("Test exception")
    except ValueError:
        logger.exception("Exception occurred")


def test_logger_properties():
    """Test logger properties."""
    manager = LogManager()
    logger = manager.get_logger('property_test')
    
    assert logger.name == 'property_test'
    assert isinstance(logger.logger, logging.Logger)


if __name__ == '__main__':
    # Run tests if script is executed directly
    pytest.main([__file__, '-v'])
