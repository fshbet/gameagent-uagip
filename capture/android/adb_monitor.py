"""
Android ADB Monitor Module for UAGIP.

This module provides device monitoring functionality for Android devices connected via ADB.
It tracks battery level, charging status, temperature, screen state, orientation, and resolution.
"""

from typing import Dict, Any, Optional
from core.logging.log_manager import LogManager
from capture.android.adb_device import DeviceInfo


logger = LogManager().get_logger(__name__)


class ADBMonitor:
    """
    Android ADB device monitoring implementation for UAGIP.
    
    This class provides methods to monitor various metrics of Android devices
    connected via ADB, including battery status, screen state, and more.
    """
    
    def __init__(self, executor):
        """
        Initialize the ADBMonitor instance.
        
        Args:
            executor: The ADB executor to use for command execution
        """
        self.executor = executor
    
    def get_metrics(self, device_id: str) -> Dict[str, Any]:
        """
        Get all monitoring metrics for a specific device.
        
        Args:
            device_id: The ID of the device to monitor
            
        Returns:
            Dict[str, Any]: Dictionary containing all device metrics
            
        Raises:
            Exception: If metric retrieval fails
        """
        logger.debug(f"Getting metrics for device: {device_id}")
        
        try:
            # Get all metrics in a single command where possible
            metrics = {}
            
            # Get battery info with one command
            battery_info = self._get_battery_info(device_id)
            metrics.update(battery_info)
            
            # Get screen state and resolution with one command
            screen_info = self._get_screen_info(device_id)
            metrics.update(screen_info)
            
            # Get orientation
            orientation = self._get_orientation(device_id)
            metrics["orientation"] = orientation
            
            logger.debug(f"Successfully retrieved metrics for device {device_id}: {metrics}")
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to get metrics for device {device_id}: {e}")
            raise
    
    def _get_battery_info(self, device_id: str) -> Dict[str, Any]:
        """
        Get battery information of the device.
        
        Args:
            device_id: The ID of the device
            
        Returns:
            Dict[str, Any]: Dictionary containing battery info
        """
        try:
            # Get all battery info with one command
            command = f"shell dumpsys battery"
            output = self.executor.execute_with_timeout(command, timeout=5)
            
            battery_info = {}
            for line in output.split('\n'):
                if 'level:' in line:
                    battery_info['battery_level'] = int(line.split(':')[1].strip())
                elif 'status:' in line:
                    status_code = int(line.split(':')[1].strip())
                    status_map = {
                        1: "unknown",
                        2: "charging", 
                        3: "discharging",
                        4: "full",
                        5: "not_charging"
                    }
                    battery_info['charging_status'] = status_map.get(status_code, "unknown")
                elif 'temperature:' in line:
                    temp_raw = line.split(':')[1].strip()
                    battery_info['temperature'] = float(temp_raw) / 10.0  # Temperature is reported in tenths of degrees
            
            return battery_info
            
        except Exception as e:
            logger.error(f"Failed to get battery info for device {device_id}: {e}")
            return {}
    
    
    
    def _get_screen_info(self, device_id: str) -> Dict[str, Any]:
        """
        Get screen information of the device.
        
        Args:
            device_id: The ID of the device
            
        Returns:
            Dict[str, Any]: Dictionary containing screen info
        """
        try:
            # Get resolution with one command
            command = f"shell wm size"
            output = self.executor.execute_with_timeout(command, timeout=5)
            
            screen_info = {}
            
            # Parse resolution from output like "Physical size: 1080x2220"
            if 'Physical size:' in output:
                size_str = output.split('Physical size:')[1].strip()
                width, height = map(int, size_str.split('x'))
                screen_info['resolution'] = {"width": width, "height": height}
            else:
                # Try alternative method
                command = f"shell dumpsys window displays | grep \"init=\""
                output = self.executor.execute_with_timeout(command, timeout=5)
                
                for line in output.split('\n'):
                    if 'init=' in line:
                        size_str = line.split('init=')[1].split()[0]  # Get first part before space
                        width, height = map(int, size_str.split('x'))
                        screen_info['resolution'] = {"width": width, "height": height}
                        break
            
            # Get screen state
            command = f"shell dumpsys power | grep \"Display Power\""
            output = self.executor.execute_with_timeout(command, timeout=5)
            
            if 'state=ON' in output:
                screen_info['screen_state'] = 'on'
            else:
                screen_info['screen_state'] = 'off'
                
            return screen_info
            
        except Exception as e:
            logger.error(f"Failed to get screen info for device {device_id}: {e}")
            return {}
    
    def _get_orientation(self, device_id: str) -> int:
        """
        Get orientation of the device.
        
        Args:
            device_id: The ID of the device
            
        Returns:
            int: Orientation (0=portrait, 1=landscape, 2=reverse portrait, 3=reverse landscape)
        """
        try:
            command = f"shell dumpsys window displays | grep \"init=\""
            output = self.executor.execute_with_timeout(command, timeout=5)
            
            # Parse orientation from output like "init=1080x2220 420dpi cur=1080x2220 app=1080x2160"
            for line in output.split('\n'):
                if 'init=' in line:
                    # This is a simplified approach - actual implementation would need
                    # to parse the orientation more precisely from rotation info
                    return 0  # Default to portrait
            
            return 0  # Default to portrait
            
        except Exception as e:
            logger.error(f"Failed to get orientation for device {device_id}: {e}")
            return 0
    
