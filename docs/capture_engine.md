# UAGIP Capture Engine Documentation

The UAGIP Capture Engine is a production-grade framework for capturing and managing visual data from various sources. It provides a flexible, scalable architecture for handling screen captures, frame buffering, metrics tracking, and integration with the broader UAGIP system.

## Architecture Overview

The capture engine follows a modular design pattern with several core components:

1. **Frame Object**: Represents a single captured image with metadata
2. **Capture Source Interface**: Abstract base class for different capture implementations
3. **Screen Capture**: Concrete implementation for desktop/window/region capture
4. **Frame Buffer**: Thread-safe circular buffer for frame storage
5. **Capture Manager**: Central coordinator for multiple capture sources
6. **Metrics Tracking**: Performance monitoring and analytics
7. **Event Integration**: System-wide event broadcasting
8. **Logging Integration**: Comprehensive logging capabilities

## Core Components

### Frame Object

The `Frame` class represents a single captured image with all associated metadata.

```python
from capture import Frame
import numpy as np

# Create a frame
image = np.array([[1, 2], [3, 4]], dtype=np.uint8)
frame = Frame(
    frame_id="frame_001",
    timestamp=1234567890.0,
    width=640,
    height=480,
    source="screen_capture",
    image=image,
    metadata={"source_type": "desktop", "capture_time": 1234567890}
)
```

### Capture Source Interface

All capture implementations must inherit from `CaptureSource` and implement the required methods.

```python
from capture import CaptureSource

class MyCaptureSource(CaptureSource):
    def start(self):
        # Implementation
        pass
        
    def stop(self):
        # Implementation
        pass
        
    def get_frame(self):
        # Implementation
        pass
        
    def is_running(self):
        # Implementation
        pass
```

### Screen Capture

The `ScreenCapture` class provides desktop, window, and region capture capabilities using mss and pillow.

```python
from capture import ScreenCapture

# Create screen capture instance
capture = ScreenCapture(
    capture_type="desktop",  # or "window" or "region"
    window_title="My Window",  # for window capture
    region=(0, 0, 1920, 1080)   # for region capture
)

# Start capturing
capture.start()

# Get a frame
frame = capture.get_frame()

# Stop capturing
capture.stop()
```

### Frame Buffer

The `FrameBuffer` provides thread-safe circular buffer functionality.

```python
from capture import FrameBuffer

# Create buffer with capacity of 100 frames
buffer = FrameBuffer(capacity=100)

# Add frames
buffer.add_frame(frame)

# Get latest frame
latest = buffer.get_latest()

# Get last 10 frames
last_10 = buffer.get_last_n(10)

# Clear buffer
buffer.clear()
```

### Capture Manager

The `CaptureManager` handles registration and coordination of multiple capture sources.

```python
from capture import CaptureManager, ScreenCapture

# Create manager
manager = CaptureManager()

# Register a capture source
capture = ScreenCapture(capture_type="desktop")
manager.register_source(capture)

# Start a source
manager.start_source("screen_capture")

# Get frames
frame = manager.get_frame("screen_capture")

# List sources
sources = manager.list_sources()
```

### Metrics Tracking

The `CaptureMetrics` class tracks performance and analytics.

```python
from capture import CaptureMetrics

# Create metrics instance
metrics = CaptureMetrics()

# Update with captured frame data
metrics.update_fps(1)
metrics.update_latency(0.016)  # 16ms latency

# Get all metrics
all_metrics = metrics.get_metrics()
print(f"FPS: {metrics.fps}")
print(f"Average Latency: {metrics.average_latency}")
```

## Event Integration

The capture engine publishes events to the system's event bus:

- `CAPTURE_STARTED`: When a capture source starts
- `CAPTURE_STOPPED`: When a capture source stops  
- `FRAME_CAPTURED`: When a frame is captured
- `CAPTURE_ERROR`: When errors occur during capture

## Logging Integration

All capture operations are logged with appropriate log levels:
- Source startup/shutdown
- Capture errors
- FPS statistics and performance metrics

## Health Monitor Integration

The capture engine provides health checks for:
- Capture source status
- FPS degradation detection
- Dropped frame threshold monitoring

## Performance Considerations

- **Thread Safety**: All buffer operations are thread-safe using locks
- **Memory Efficiency**: Circular buffers prevent memory leaks
- **Frame Handling**: No unnecessary frame copies
- **Minimum FPS**: Target 30 FPS, support 60 FPS architecture

## Usage Examples

### Basic Desktop Capture

```python
from capture import CaptureManager, ScreenCapture

# Setup
manager = CaptureManager()
capture = ScreenCapture(capture_type="desktop")
manager.register_source(capture)

# Start capture
manager.start_source("screen_capture")

# Main loop
try:
    while True:
        frame = manager.get_frame("screen_capture")
        if frame:
            # Process frame here
            pass
finally:
    manager.stop_source("screen_capture")
```

### Multiple Source Capture

```python
from capture import CaptureManager, ScreenCapture

# Setup multiple sources
manager = CaptureManager()

# Desktop capture
desktop_capture = ScreenCapture(capture_type="desktop")
manager.register_source(desktop_capture)

# Window capture
window_capture = ScreenCapture(
    capture_type="window", 
    window_title="Game Window"
)
manager.register_source(window_capture)

# Start both
manager.start_source("desktop_capture")
manager.start_source("window_capture")

# Get frames from both sources
desktop_frame = manager.get_frame("desktop_capture")
window_frame = manager.get_frame("window_capture")
```

## Testing

Unit tests are provided in `tests/test_capture_engine.py` and cover:

- Frame creation and serialization
- Frame buffer functionality
- Source registration and management
- Metrics tracking
- Event publishing
- Thread safety

Run the tests with:
```bash
python -m pytest tests/test_capture_engine.py -v
```

## Future Compatibility

The architecture is designed to support future plugins:
- Android ADB Capture
- Emulator Capture  
- Video File Capture
- RTSP Streams

Extension points are provided through the `CaptureSource` interface and modular design.