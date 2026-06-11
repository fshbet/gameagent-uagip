# Android ADB Capture Module

## Overview

The Android ADB Capture module provides comprehensive functionality for interacting with Android devices via ADB (Android Debug Bridge) within the UAGIP framework. This module enables device discovery, screenshot capture, input injection, and device monitoring capabilities.

## Architecture

```
capture/android/
├── adb_device.py          # Device discovery and management
├── adb_capture.py         # Screenshot capture functionality
├── adb_input.py           # Input injection (tap, swipe, etc.)
├── adb_monitor.py         # Device monitoring and metrics
├── adb_executor.py        # ADB command execution abstraction
└── __init__.py            # Module exports
```

## Key Features

### 1. Device Discovery
- `list_devices()`: Lists all connected Android devices with detailed information
- `get_device(device_id)`: Retrieves information about a specific device
- `connect(device_id)`: Establishes connection to a device
- `disconnect(device_id)`: Closes connection to a device
- `reconnect(device_id)`: Reconnects to a device

### 2. Screenshot Capture
- `capture_screen()`: Captures full screen as numpy array
- `capture_region(x, y, width, height)`: Captures specific region of screen

### 3. Input Injection
- `tap(x, y)`: Performs tap at specified coordinates
- `swipe(x1, y1, x2, y2, duration)`: Performs swipe gesture
- `long_press(x, y, duration)`: Performs long press gesture
- `input_text(text)`: Inputs text into device
- `key_event(keycode)`: Sends key event to device

### 4. Device Monitoring
- `get_metrics()`: Retrieves device metrics including battery, temperature, screen state, etc.

## Usage Examples

### Basic Device Management
```python
from capture.android import ADBDevice, RealADBExecutor

# Create executor and device manager
executor = RealADBExecutor()
device_manager = ADBDevice(executor)

# List connected devices
devices = device_manager.list_devices()
for device in devices:
    print(f"Device: {device.device_id}, Model: {device.model}")

# Connect to a specific device
device_manager.connect("device_serial_number")
```

### Screenshot Capture
```python
from capture.android import ADBCapture, RealADBExecutor

executor = RealADBExecutor()
capture_manager = ADBCapture(executor)

# Capture full screen
frame = capture_manager.capture_screen()

# Capture specific region
region_frame = capture_manager.capture_region(100, 100, 200, 200)
```

### Input Injection
```python
from capture.android import ADBInput, RealADBExecutor

executor = RealADBExecutor()
input_manager = ADBInput(executor)

# Perform tap
input_manager.tap(100, 200)

# Perform swipe
input_manager.swipe(100, 200, 300, 400, duration=500)

# Input text
input_manager.input_text("Hello World")
```

### Device Monitoring
```python
from capture.android import ADBMonitor, RealADBExecutor

executor = RealADBExecutor()
monitor = ADBMonitor(executor)

# Get device metrics
metrics = monitor.get_metrics()
print(f"Battery: {metrics.battery_level}%")
print(f"Temperature: {metrics.temperature}°C")
```

## Event Bus Integration

The module publishes the following events through the UAGIP event bus:

- `ADB_CONNECTED`: When a device connects
- `ADB_DISCONNECTED`: When a device disconnects  
- `ADB_CAPTURED`: When screenshot is captured
- `ADB_ERROR`: When an ADB operation fails
- `INPUT_EXECUTED`: When input command is executed

## Health Monitor Integration

The module performs health checks including:
- Device reachability
- ADB responsiveness
- Screenshot capture latency

## Thread Safety

The implementation supports concurrent operations on multiple devices by using separate executor instances for each device connection.

## Mockable Design

All ADB execution is abstracted through the `ADBExecutor` interface, allowing for:
- Real ADB execution (`RealADBExecutor`)
- Mock execution for testing (`MockADBExecutor`)

## Performance

Target specifications:
- Screenshot latency under 300ms
- Support for multiple screenshots per second

## Extension Points

### Custom ADB Executor
```python
class CustomADBExecutor(ADBExecutor):
    def execute_with_timeout(self, command: str, timeout: int) -> str:
        # Custom implementation
        pass
```

### Device Metrics Customization
The `DeviceMetrics` dataclass can be extended to include additional metrics as needed.

## Supported ADB Commands

- `adb devices -l`: List connected devices with details
- `adb connect <device>`: Connect to device
- `adb disconnect <device>`: Disconnect from device
- `adb exec-out screencap -p`: Capture screenshot
- `adb shell input tap x y`: Tap gesture
- `adb shell input swipe x1 y1 x2 y2 [duration]`: Swipe gesture
- `adb shell input text "text"`: Input text
- `adb shell input keyevent keycode`: Send key event
- `adb shell dumpsys battery`: Get battery information
- `adb shell wm size`: Get screen resolution
- `adb shell dumpsys power`: Get power status