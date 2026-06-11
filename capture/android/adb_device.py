"""
Android ADB Device Module for UAGIP.

This module provides device discovery and management functionality for Android devices connected via ADB.
"""

from dataclasses import dataclass
from typing import Optional, List
from core.logging.log_manager import LogManager


logger = LogManager().get_logger(__name__)


@dataclass
class DeviceInfo:
    """
    Data class representing information about an Android device.
    
    This class holds structured information about Android devices connected via ADB,
    including device ID, model, manufacturer, Android version, and state.
    """
    device_id: str
    model: Optional[str] = None
    manufacturer: Optional[str] = None
    android_version: Optional[str] = None
    state: Optional[str] = None


class ADBDevice:
    """
    Android ADB device management implementation for UAGIP.
    
    This class provides methods to discover, connect, disconnect, and manage
    Android devices connected via ADB.
    """
    
    def __init__(self, executor):
        """
        Initialize the ADBDevice instance.
        
        Args:
            executor: The ADB executor to use for command execution
        """
        self.executor = executor
    
    def list_devices(self) -> List[DeviceInfo]:
        """
        List all connected Android devices.
        
        Returns:
            List[DeviceInfo]: List of DeviceInfo objects for each connected device
            
        Raises:
            Exception: If device listing fails
        """
        logger.debug("Listing connected devices")
        
        try:
            command = "devices -l"
            output = self.executor.execute_with_timeout(command, timeout=5)
            
            devices = []
            
            # Parse adb devices output
            lines = output.strip().split('\n')
            for line in lines[1:]:  # Skip header line
                if line.strip() and not line.startswith('List'):
                    parts = line.split()
                    if len(parts) >= 2:
                        device_id = parts[0]
                        state = parts[1]
                        
                        # Get additional device info if available
                        model = None
                        manufacturer = None
                        android_version = None
                        
                        # Parse detailed information from 'adb devices -l' output
                        for part in parts:
                            if part.startswith('model:'):
                                model = part.split(':', 1)[1]
                            elif part.startswith('manufacturer:'):
                                manufacturer = part.split(':', 1)[1]
                            elif part.startswith('version:'):
                                android_version = part.split(':', 1)[1]
                        
                        device_info = DeviceInfo(
                            device_id=device_id,
                            model=model,
                            manufacturer=manufacturer,
                            android_version=android_version,
                            state=state
                        )
                        devices.append(device_info)
            
            logger.debug(f"Found {len(devices)} connected devices")
            return devices
            
        except Exception as e:
            logger.error(f"Failed to list devices: {e}")
            raise
    
    def get_device(self, device_id: str) -> DeviceInfo:
        """
        Get information about a specific device.
        
        Args:
            device_id: The ID of the device to retrieve information for
            
        Returns:
            DeviceInfo: Information about the specified device
            
        Raises:
            Exception: If device retrieval fails
        """
        logger.debug(f"Getting information for device: {device_id}")
        
        try:
            # Get list of all devices and find the specific one
            devices = self.list_devices()
            
            for device in devices:
                if device.device_id == device_id:
                    return device
            
            raise Exception(f"Device {device_id} not found")
            
        except Exception as e:
            logger.error(f"Failed to get device {device_id}: {e}")
            raise
    
    def connect(self, device_id: str) -> None:
        """
        Connect to a specific device.
        
        Args:
            device_id: The ID of the device to connect to
            
        Raises:
            Exception: If connection fails
        """
        logger.debug(f"Connecting to device: {device_id}")
        
        try:
            command = f"connect {device_id}"
            self.executor.execute_with_timeout(command, timeout=10)
            
            logger.debug(f"Successfully connected to device: {device_id}")
            
        except Exception as e:
            logger.error(f"Failed to connect to device {device_id}: {e}")
            raise
    
    def disconnect(self, device_id: str) -> None:
        """
        Disconnect from a specific device.
        
        Args:
            device_id: The ID of the device to disconnect from
            
        Raises:
            Exception: If disconnection fails
        """
        logger.debug(f"Disconnecting from device: {device_id}")
        
        try:
            command = f"disconnect {device_id}"
            self.executor.execute_with_timeout(command, timeout=5)
            
            logger.debug(f"Successfully disconnected from device: {device_id}")
            
        except Exception as e:
            logger.error(f"Failed to disconnect from device {device_id}: {e}")
            raise
    
    def reconnect(self, device_id: str) -> None:
        """
        Reconnect to a specific device.
        
        Args:
            device_id: The ID of the device to reconnect to
            
        Raises:
            Exception: If reconnection fails
        """
        logger.debug(f"Reconnecting to device: {device_id}")
        
        try:
            self.disconnect(device_id)
            self.connect(device_id)
            
            logger.debug(f"Successfully reconnected to device: {device_id}")
            
        except Exception as e:
            logger.error(f"Failed to reconnect to device {device_id}: {e}")
            raise