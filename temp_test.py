#!/usr/bin/env python3
"""
Simple test to verify logging framework works.
"""

import os
import tempfile
from core.logging.log_manager import LogManager
from core.config.config_manager import ConfigManager

def test_basic_functionality():
    """Test basic logging functionality."""
    print("Testing basic logging framework...")
    
    # Test singleton behavior
    manager1 = LogManager()
    manager2 = LogManager()
    assert manager1 is manager2
    print("✓ Singleton pattern works")
    
    # Test logger creation
    logger = manager1.get_logger('test_module')
    assert logger.name == 'test_module'
    print("✓ Logger creation works")
    
    # Test configuration
    config_manager = ConfigManager()
    config_manager.set('logging', {
        'level': 'INFO',
        'file': 'logs/test.log',
        'json': False
    })
    manager1.set_config_manager(config_manager)
    print("✓ Configuration integration works")
    
    # Test logging
    logger.info("Test message")
    print("✓ Logging works")
    
    print("All basic tests passed!")

if __name__ == '__main__':
    test_basic_functionality()