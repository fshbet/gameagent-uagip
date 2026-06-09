"""
Test cases for invalid YAML handling in ConfigManager
"""

import os
import tempfile
import unittest
from pathlib import Path

# Add the core directory to Python path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / 'core'))

from config.config_manager import ConfigManager, ConfigLoadError


class TestInvalidYAML(unittest.TestCase):
    """Test cases for invalid YAML handling"""

    def test_invalid_yaml_file(self):
        """Test that invalid YAML raises ConfigLoadError"""
        # Create a temporary invalid YAML file
        temp_config = tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False)
        temp_config.write("""
database:
  host: localhost
  port: 5432
  username: testuser
  password: testpass
  # This is an invalid YAML - missing colon
  invalid_setting
""")
        temp_config.close()
        
        # Try to create ConfigManager with invalid YAML - should raise ConfigLoadError
        with self.assertRaises(ConfigLoadError):
            config = ConfigManager(temp_config.name)
        
        # Clean up
        os.unlink(temp_config.name)

    def test_nonexistent_file(self):
        """Test that nonexistent file works correctly (should not raise error)"""
        # Try to create ConfigManager with non-existent file - should not raise error
        # but create an empty config
        config = ConfigManager("nonexistent.yaml")
        self.assertEqual(config.data, {})

    def test_empty_file(self):
        """Test that empty YAML file works correctly"""
        # Create a temporary empty YAML file
        temp_config = tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False)
        temp_config.write("")
        temp_config.close()
        
        # This should not raise an error and create an empty config
        config = ConfigManager(temp_config.name)
        self.assertEqual(config.data, {})
        
        # Clean up
        os.unlink(temp_config.name)


if __name__ == '__main__':
    unittest.main()