"""
Config Manager for GameAgent
Handles YAML configuration with environment variable overrides and type hints.
"""

import os
import yaml
from typing import Any, Dict, Optional, Union
from pathlib import Path


class ConfigError(Exception):
    """Base exception for configuration errors."""
    pass


class ConfigLoadError(ConfigError):
    """Custom exception for configuration loading errors."""
    pass


class ConfigValidationError(ConfigError):
    """Custom exception for configuration validation errors."""
    pass


class ConfigManager:
    """
    A configuration manager that loads YAML files and allows environment variable overrides.
    """

    def __init__(self, config_file: str = "config.yaml"):
        """
        Initialize the ConfigManager with a configuration file.

        Args:
            config_file (str): Path to the YAML configuration file
        """
        self.config_file = config_file
        self._config_data: Dict[str, Any] = {}
        self.load_config()


    def load_config(self) -> None:
        """
        Load configuration from YAML file and apply environment variable overrides.
        """
        # Load base configuration from YAML file
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as file:
                    self._config_data = yaml.safe_load(file) or {}
            else:
                # If file doesn't exist, initialize empty config
                self._config_data = {}
        except yaml.YAMLError as e:
            raise ConfigLoadError(f"Invalid YAML in config file '{self.config_file}': {str(e)}")
        except PermissionError:
            raise ConfigLoadError(f"Permission denied reading config file '{self.config_file}'")
        except Exception as e:
            raise ConfigLoadError(f"Error reading config file '{self.config_file}': {str(e)}")
        
        # Apply environment variable overrides
        self._apply_env_overrides()

    def _apply_env_overrides(self) -> None:
        """
        Apply environment variable overrides to the configuration.
        Environment variables should be in the format: CONFIG_SECTION_KEY
        """
        for key, value in os.environ.items():
            if key.startswith('CONFIG_'):
                # Remove the 'CONFIG_' prefix
                config_key = key[7:].lower()
                # Handle nested keys with dots
                keys = config_key.split('_')
                self._set_nested_value(self._config_data, keys, value)

    def _set_nested_value(self, data: Dict[str, Any], keys: list, value: str) -> None:
        """
        Set a nested value in the configuration dictionary.

        Args:
            data (Dict[str, Any]): The configuration dictionary
            keys (list): List of keys representing the path to the value
            value (str): The value to set
        """
        current = data
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        
        # Try to convert string value to appropriate type
        converted_value = self._convert_type(value)
        current[keys[-1]] = converted_value

    def _convert_type(self, value: str) -> Union[str, int, float, bool]:
        """
        Convert string value to appropriate Python type.

        Args:
            value (str): String value to convert

        Returns:
            Union[str, int, float, bool]: Converted value
        """
        # Try boolean
        if value.lower() in ('true', 'false'):
            return value.lower() == 'true'
        
        # Try integer
        try:
            return int(value)
        except ValueError:
            pass
        
        # Try float
        try:
            return float(value)
        except ValueError:
            pass
        
        # Return as string if no conversion worked
        return value

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value by key.

        Args:
            key (str): Configuration key (can use dots for nested access)
            default (Any): Default value if key is not found

        Returns:
            Any: Configuration value or default
        """
        keys = key.split('.')
        current = self._config_data
        
        try:
            for k in keys:
                current = current[k]
            return current
        except (KeyError, TypeError):
            return default

    def set(self, key: str, value: Any) -> None:
        """
        Set a configuration value by key.

        Args:
            key (str): Configuration key (can use dots for nested access)
            value (Any): Value to set
        """
        keys = key.split('.')
        current = self._config_data
        
        # Navigate to the parent of the target key
        for k in keys[:-1]:
            if k not in current:
                current[k] = {}
            current = current[k]
        
        # Set the final value
        current[keys[-1]] = value

    def reload(self) -> None:
        """
        Reload configuration from file.
        """
        self.load_config()

    @property
    def data(self) -> Dict[str, Any]:
        """
        Get a copy of the configuration data.

        Returns:
            Dict[str, Any]: Configuration data
        """
        return self._config_data.copy()