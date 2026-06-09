"""
Unit tests for ConfigManager
"""

import os
import tempfile
import unittest
from pathlib import Path

# Add the core directory to Python path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / 'core'))

from config.config_manager import ConfigManager, ConfigLoadError


class TestConfigManager(unittest.TestCase):
    """Test cases for ConfigManager"""

    def setUp(self):
        """Set up test fixtures before each test method."""
        # Create a temporary YAML file for testing
        self.temp_config = tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False)
        self.temp_config.write("""
database:
  host: localhost
  port: 5432
  username: testuser
  password: testpass
api:
  timeout: 30
  retries: 3
debug: true
""")
        self.temp_config.close()
        
        # Create ConfigManager instance with temp file
        self.config = ConfigManager(self.temp_config.name)

    def tearDown(self):
        """Clean up test fixtures after each test method."""
        # Remove the temporary file
        os.unlink(self.temp_config.name)

    def test_init_with_file(self):
        """Test initialization with a configuration file"""
        self.assertIsNotNone(self.config)
        self.assertEqual(self.config.config_file, self.temp_config.name)

    def test_load_config(self):
        """Test loading configuration from YAML file"""
        # Check that database section is loaded
        self.assertEqual(self.config.get('database.host'), 'localhost')
        self.assertEqual(self.config.get('database.port'), 5432)
        self.assertEqual(self.config.get('database.username'), 'testuser')
        self.assertEqual(self.config.get('database.password'), 'testpass')
        
        # Check that api section is loaded
        self.assertEqual(self.config.get('api.timeout'), 30)
        self.assertEqual(self.config.get('api.retries'), 3)
        
        # Check that debug is loaded as boolean
        self.assertTrue(self.config.get('debug'))

    def test_get_with_default(self):
        """Test getting configuration values with defaults"""
        # Test existing key
        self.assertEqual(self.config.get('database.host'), 'localhost')
        
        # Test non-existing key with default
        self.assertEqual(self.config.get('non.existing.key', 'default_value'), 'default_value')
        
        # Test non-existing key without default (should return None)
        self.assertIsNone(self.config.get('non.existing.key'))

    def test_set_and_get(self):
        """Test setting and getting configuration values"""
        # Set a new value
        self.config.set('new.setting', 'test_value')
        self.assertEqual(self.config.get('new.setting'), 'test_value')
        
        # Set a nested value
        self.config.set('nested.value', 42)
        self.assertEqual(self.config.get('nested.value'), 42)

    def test_reload(self):
        """Test reloading configuration"""
        # Modify the config file content
        with open(self.temp_config.name, 'w') as f:
            f.write("""
updated:
  value: new_value
""")
        
        # Reload and check
        self.config.reload()
        self.assertEqual(self.config.get('updated.value'), 'new_value')

    def test_env_override(self):
        """Test environment variable overrides"""
        # Set an environment variable
        os.environ['CONFIG_DATABASE_HOST'] = 'env_host'
        
        # Create new config manager to trigger env override
        config_with_env = ConfigManager(self.temp_config.name)
        
        # Check that the value was overridden
        self.assertEqual(config_with_env.get('database.host'), 'env_host')
        
        # Clean up environment variable
        del os.environ['CONFIG_DATABASE_HOST']

    def test_env_override_types(self):
        """Test environment variable overrides with type conversion"""
        # Test boolean override
        os.environ['CONFIG_DEBUG'] = 'false'
        config_with_env = ConfigManager(self.temp_config.name)
        self.assertFalse(config_with_env.get('debug'))
        del os.environ['CONFIG_DEBUG']
        
        # Test integer override
        os.environ['CONFIG_DATABASE_PORT'] = '3306'
        config_with_env = ConfigManager(self.temp_config.name)
        self.assertEqual(config_with_env.get('database.port'), 3306)
        del os.environ['CONFIG_DATABASE_PORT']
        
        # Test float override
        os.environ['CONFIG_API_TIMEOUT'] = '45.5'
        config_with_env = ConfigManager(self.temp_config.name)
        self.assertEqual(config_with_env.get('api.timeout'), 45.5)
        del os.environ['CONFIG_API_TIMEOUT']

    def test_nested_access(self):
        """Test nested configuration access"""
        # Test accessing nested values
        self.assertEqual(self.config.get('database.host'), 'localhost')
        self.assertEqual(self.config.get('database.port'), 5432)
        
        # Test non-existent nested key
        self.assertIsNone(self.config.get('database.nonexistent'))
        self.assertEqual(self.config.get('database.nonexistent', 'default'), 'default')

    def test_data_property(self):
        """Test data property returns a copy"""
        data = self.config.data
        data['test_key'] = 'test_value'
        
        # Original config should not be affected
        self.assertNotIn('test_key', self.config.data)


if __name__ == '__main__':
    unittest.main()