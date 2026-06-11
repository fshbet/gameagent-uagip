"""
Unit tests for Android ADB Capture module.
"""

import unittest
from unittest.mock import Mock, patch
import numpy as np
from PIL import Image
import io

# Import the modules we're testing
from capture.android import (
    ADBDevice, 
    DeviceInfo,
    ADBCapture,
    ADBInput,
    ADBMonitor,
    RealADBExecutor,
    MockADBExecutor
)
from capture.frame import Frame


class TestADBDevice(unittest.TestCase):
    """Test cases for ADBDevice class."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.mock_executor = Mock()
        self.device_manager = ADBDevice(self.mock_executor)
    
    def test_list_devices_success(self):
        """Test successful device listing."""
        # Mock the executor to return sample device data
        mock_output = """List of devices attached
emulator-5554    device product:sdk_gphone64_x86_64 model:Android_SDK_built_for_x86_64 device:generic_x86_64 transport_id:1
192.168.1.100:5555    device product:Pixel_5 model:Pixel_5 device:cheetah transport_id:2"""
        
        self.mock_executor.execute_with_timeout.return_value = mock_output
        
        devices = self.device_manager.list_devices()
        
        self.assertEqual(len(devices), 2)
        self.assertEqual(devices[0].device_id, "emulator-5554")
        self.assertEqual(devices[0].model, "Android_SDK_built_for_x86_64")
        self.assertEqual(devices[1].device_id, "192.168.1.100:5555")
        self.assertEqual(devices[1].model, "Pixel_5")
    
    def test_get_device_success(self):
        """Test successful device retrieval."""
        mock_output = """List of devices attached
emulator-5554    device product:sdk_gphone64_x86_64 model:Android_SDK_built_for_x86_64 device:generic_x86_64 transport_id:1"""
        
        self.mock_executor.execute_with_timeout.return_value = mock_output
        
        device = self.device_manager.get_device("emulator-5554")
        
        self.assertEqual(device.device_id, "emulator-5554")
        self.assertEqual(device.model, "Android_SDK_built_for_x86_64")
    
    def test_connect_success(self):
        """Test successful device connection."""
        self.mock_executor.execute_with_timeout.return_value = "connected to 192.168.1.100:5555"
        
        self.device_manager.connect("192.168.1.100:5555")
        
        self.mock_executor.execute_with_timeout.assert_called_once_with("connect 192.168.1.100:5555", timeout=10)
    
    def test_disconnect_success(self):
        """Test successful device disconnection."""
        self.mock_executor.execute_with_timeout.return_value = "disconnected 192.168.1.100:5555"
        
        self.device_manager.disconnect("192.168.1.100:5555")
        
        self.mock_executor.execute_with_timeout.assert_called_once_with("disconnect 192.168.1.100:5555", timeout=5)
    
    def test_reconnect_success(self):
        """Test successful device reconnection."""
        # Mock disconnect
        self.mock_executor.execute_with_timeout.side_effect = [
            "disconnected 192.168.1.100:5555",
            "connected to 192.168.1.100:5555"
        ]
        
        self.device_manager.reconnect("192.168.1.100:5555")
        
        # Should call disconnect and then connect
        self.assertEqual(self.mock_executor.execute_with_timeout.call_count, 2)
        self.mock_executor.execute_with_timeout.assert_any_call("disconnect 192.168.1.100:5555", timeout=5)
        self.mock_executor.execute_with_timeout.assert_any_call("connect 192.168.1.100:5555", timeout=10)


class TestADBCapture(unittest.TestCase):
    """Test cases for ADBCapture class."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.mock_executor = Mock()
        self.capture_manager = ADBCapture(self.mock_executor)
    
    @patch('numpy.frombuffer')
    @patch('cv2.imdecode')
    def test_capture_screen_success(self, mock_imdecode, mock_frombuffer):
        """Test successful screen capture."""
        # Create a real PNG image for testing
        # Create a simple test image
        test_image = Image.new('RGB', (100, 100), color='red')
        
        # Save the image to bytes in PNG format
        png_bytes = io.BytesIO()
        test_image.save(png_bytes, format='PNG')
        png_bytes.seek(0)
        real_png_data = png_bytes.read()
        
        # Mock the numpy and cv2 operations
        mock_array = Mock()
        mock_frombuffer.return_value = mock_array
        mock_imdecode.return_value = "decoded_image"
        
        self.mock_executor.execute_with_timeout.return_value = real_png_data
        
        frame = self.capture_manager.capture_screen()
        
        self.assertIsInstance(frame, Frame)
        self.assertEqual(frame.data, "decoded_image")
    
    @patch('numpy.frombuffer')
    @patch('cv2.imdecode')
    def test_capture_region_success(self, mock_imdecode, mock_frombuffer):
        """Test successful region capture."""
        # Create a real PNG image for testing
        # Create a simple test image
        test_image = Image.new('RGB', (100, 100), color='red')
        
        # Save the image to bytes in PNG format
        png_bytes = io.BytesIO()
        test_image.save(png_bytes, format='PNG')
        png_bytes.seek(0)
        real_png_data = png_bytes.read()
        
        # Mock the numpy and cv2 operations
        mock_array = Mock()
        mock_frombuffer.return_value = mock_array
        mock_imdecode.return_value = "decoded_image"
        
        self.mock_executor.execute_with_timeout.return_value = real_png_data
        
        frame = self.capture_manager.capture_region(100, 100, 200, 200)
        
        self.assertIsInstance(frame, Frame)
        self.assertEqual(frame.data, "decoded_image")
        # Verify the correct command was called
        self.mock_executor.execute_with_timeout.assert_called_once()


class TestADBInput(unittest.TestCase):
    """Test cases for ADBInput class."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.mock_executor = Mock()
        self.input_manager = ADBInput(self.mock_executor)
    
    def test_tap_success(self):
        """Test successful tap operation."""
        self.input_manager.tap(100, 200)
        
        self.mock_executor.execute_with_timeout.assert_called_once_with("shell input tap 100 200", timeout=5)
    
    def test_swipe_success(self):
        """Test successful swipe operation."""
        self.input_manager.swipe(100, 200, 300, 400, duration=500)
        
        self.mock_executor.execute_with_timeout.assert_called_once_with("shell input swipe 100 200 300 400 500", timeout=5)
    
    def test_swipe_no_duration(self):
        """Test swipe without duration parameter."""
        self.input_manager.swipe(100, 200, 300, 400)
        
        self.mock_executor.execute_with_timeout.assert_called_once_with("shell input swipe 100 200 300 400", timeout=5)
    
    def test_long_press_success(self):
        """Test successful long press operation."""
        self.input_manager.long_press(100, 200, duration=1000)
        
        self.mock_executor.execute_with_timeout.assert_called_once_with("shell input swipe 100 200 100 200 1000", timeout=5)
    
    def test_input_text_success(self):
        """Test successful text input."""
        self.input_manager.input_text("Hello World")
        
        # Should escape single quotes
        self.mock_executor.execute_with_timeout.assert_called_once_with("shell input text 'Hello World'", timeout=5)
    
    def test_key_event_success(self):
        """Test successful key event."""
        self.input_manager.key_event(66)
        
        self.mock_executor.execute_with_timeout.assert_called_once_with("shell input keyevent 66", timeout=5)


class TestADBMonitor(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.mock_executor = Mock()
        self.monitor = ADBMonitor(self.mock_executor)
    
    def test_get_metrics_success(self):
        """Test successful metrics retrieval."""
        # Mock various system commands
        self.mock_executor.execute_with_timeout.side_effect = [
            "Current state: CHARGING",  # dumpsys battery
            "100",                       # battery level (from dumpsys battery)
            "35.0",                      # temperature 
            "1920x1080",                 # screen resolution
            "on",                        # screen state
            "0"                          # orientation
        ]
        
        metrics = self.monitor.get_metrics("test_device_id")
        
        # Check that the right methods were called
        self.assertEqual(self.mock_executor.execute_with_timeout.call_count, 5)
        # Note: The actual structure of DeviceMetrics would be tested in more detail


class TestMockADBExecutor(unittest.TestCase):
    """Test cases for MockADBExecutor."""
    
    def test_execute_with_timeout(self):
        """Test mock executor execution."""
        executor = MockADBExecutor()
        
        result = executor.execute_with_timeout("test command", timeout=5)
        
        # Mock executor should return the command string
        self.assertEqual(result, "test command")


if __name__ == '__main__':
    unittest.main()