# YOLO Model Management Framework

## Overview

The YOLO Model Management Framework provides a comprehensive solution for managing YOLO (You Only Look Once) models within the GameAgent system. This framework handles model registration, loading, unloading, versioning, and inference operations while maintaining thread safety and integration with the system's event bus and health monitoring.

## Architecture

The framework consists of several core components:

1. **ModelMetadata** - Stores metadata about YOLO models
2. **DetectorBackend** - Abstract interface for different model backends
3. **ModelRegistry** - Persistent registry for managing model versions
4. **ModelManager** - Main controller for model operations
5. **InferenceResult** - Data structures for inference outputs
6. **Exceptions** - Custom exceptions for error handling

## Model Metadata

The `ModelMetadata` class tracks essential information about YOLO models:

- `model_id`: Unique identifier for the model
- `model_name`: Human-readable name of the model
- `version`: Version string (semantic versioning recommended)
- `framework`: Framework used (e.g., "YOLOv8", "YOLOv10")
- `backend`: Backend implementation (e.g., "ultralytics", "onnxruntime")
- `classes`: List of class names the model can detect
- `input_size`: Input dimensions for the model (e.g., [640, 640])
- `created_at`: Timestamp when the model was created
- `checksum`: Checksum for model integrity verification

## Detector Backend Interface

The `DetectorBackend` abstract base class defines the interface that all backend implementations must follow:

```python
class DetectorBackend(ABC):
    @abstractmethod
    def load_model(self) -> None:
        """Load the model into memory."""
        pass
    
    @abstractmethod
    def unload_model(self) -> None:
        """Unload the model from memory."""
        pass
    
    @abstractmethod
    def infer(self, input_data) -> InferenceBatchResult:
        """Perform inference on input data."""
        pass
    
    @abstractmethod
    def warmup(self) -> None:
        """Warm up the model for optimal performance."""
        pass
    
    @abstractmethod
    def get_info(self) -> dict:
        """Get backend-specific information."""
        pass
```

### Supported Backends

The framework currently supports:

1. **Ultralytics YOLO** - Primary implementation using Ultralytics YOLO library
2. **ONNX Runtime** - Cross-platform inference using ONNX models
3. **TensorRT** - NVIDIA GPU optimized inference (planned)
4. **OpenVINO** - Intel CPU/GPU optimized inference (planned)

## Model Registry

The `ModelRegistry` provides persistent storage for models and version management:

- Supports multiple versions of the same model
- Manages active model selection
- Enables rollback to previous versions
- Provides version lookup functionality

## Model Manager

The `ModelManager` serves as the central controller that orchestrates all model operations:

### Key Methods

- `register_model(metadata)`: Register a new model with metadata
- `unregister_model(model_id)`: Remove a model from registry
- `load_model(model_id)`: Load a model into memory
- `unload_model(model_id)`: Unload a model from memory
- `list_models()`: List all registered models
- `get_model(model_id, version=None)`: Retrieve specific model information
- `infer(input_data)`: Perform inference using the active model

## Inference Result

The framework uses structured data classes for inference results:

### InferenceResult
Stores individual detection results with:
- `class_id`: Numeric identifier of detected class
- `class_name`: Human-readable name of detected class
- `confidence`: Detection confidence score (0.0-1.0)
- `bbox`: Bounding box coordinates [x, y, width, height]
- `segmentation`: Segmentation mask data (optional)
- `timestamp`: When the detection occurred

### InferenceBatchResult
Stores batch results with:
- `results`: List of individual `InferenceResult` objects
- `model_id`: Identifier of the model used
- `version`: Version of the model used
- `input_size`: Input dimensions for inference
- `processing_time`: Time taken for processing
- Helper methods for filtering and analyzing results

## Integration Points

### Event Bus Integration

The framework publishes events to the system's event bus:

- `MODEL_REGISTERED`: When a model is registered
- `MODEL_LOADED`: When a model is loaded into memory
- `MODEL_UNLOADED`: When a model is unloaded from memory
- `MODEL_FAILED`: When model operations fail

### Health Integration

The framework integrates with the system's health monitoring:

- Reports model loading status
- Monitors memory usage
- Indicates inference availability

## Thread Safety

All components in the framework are designed to be thread-safe, allowing concurrent access to model management operations.

## Future Extensions

### TensorRT Support

Planned support for NVIDIA TensorRT optimization for GPU-accelerated inference.

### OpenVINO Support

Planned support for Intel's OpenVINO toolkit for CPU/GPU inference optimization.

### Model Quantization

Support for quantized models to reduce memory footprint and improve performance.

## Usage Example

```python
# Initialize model manager
manager = ModelManager(event_bus=event_bus)

# Register a model
metadata = ModelMetadata(
    model_id="yolo_v8_model",
    model_name="YOLOv8 Object Detector",
    version="1.0.0",
    framework="YOLOv8",
    backend="ultralytics",
    classes=["person", "car", "dog"],
    input_size=[640, 640],
    checksum="abc123"
)

manager.register_model(metadata)

# Load the model
backend = manager.load_model("yolo_v8_model")

# Perform inference
result = manager.infer(input_image)
```

## Testing

The framework includes comprehensive unit tests covering:

- Model metadata creation and validation
- Registry operations (registration, versioning, retrieval)
- Inference result handling
- Model manager functionality
- Edge cases and error conditions

All tests use mocking to avoid requiring actual model weights or hardware dependencies.