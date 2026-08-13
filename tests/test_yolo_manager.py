"""
Unit tests for YOLO Model Management Framework.
"""

import unittest
from unittest.mock import Mock, patch
from datetime import datetime
import tempfile
import os

from vision.yolo.model_metadata import ModelMetadata
from vision.yolo.model_registry import ModelRegistry
from vision.yolo.model_manager import ModelManager
from vision.yolo.inference_result import InferenceResult, InferenceBatchResult
from vision.yolo.exceptions import (
    ModelNotFoundError, 
    ModelRegistrationError, 
    ModelLoadError,
    ModelInferenceError
)
from core.events.event_bus import EventBus


class TestModelMetadata(unittest.TestCase):
    """Test cases for ModelMetadata class."""
    
    def test_model_metadata_creation(self):
        """Test creating a ModelMetadata object."""
        metadata = ModelMetadata(
            model_id="test_model_001",
            model_name="Test YOLO Model",
            version="1.0.0",
            framework="YOLOv8",
            backend="ultralytics",
            classes=["person", "car", "dog"],
            input_size=[640, 640],
            created_at=datetime.now(),
            checksum="abc123"
        )
        
        self.assertEqual(metadata.model_id, "test_model_001")
        self.assertEqual(metadata.model_name, "Test YOLO Model")
        self.assertEqual(metadata.version, "1.0.0")
        self.assertEqual(metadata.framework, "YOLOv8")
        self.assertEqual(metadata.backend, "ultralytics")
        self.assertEqual(metadata.classes, ["person", "car", "dog"])
        self.assertEqual(metadata.input_size, [640, 640])
        self.assertIsNotNone(metadata.created_at)
        self.assertEqual(metadata.checksum, "abc123")


class TestModelRegistry(unittest.TestCase):
    """Test cases for ModelRegistry class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.registry = ModelRegistry()
    
    def test_register_model(self):
        """Test registering a model."""
        metadata = ModelMetadata(
            model_id="test_model_001",
            model_name="Test YOLO Model",
            version="1.0.0",
            framework="YOLOv8",
            backend="ultralytics",
            classes=["person", "car"],
            input_size=[640, 640],
            created_at=datetime.now(),
            checksum="abc123"
        )
        
        self.registry.register_model(metadata)
        
        # Verify model is registered
        retrieved = self.registry.get_model("test_model_001")
        self.assertEqual(retrieved.model_id, "test_model_001")
        self.assertEqual(retrieved.version, "1.0.0")
    
    def test_register_multiple_versions(self):
        """Test registering multiple versions of the same model."""
        metadata1 = ModelMetadata(
            model_id="test_model_001",
            model_name="Test YOLO Model",
            version="1.0.0",
            framework="YOLOv8",
            backend="ultralytics",
            classes=["person", "car"],
            input_size=[640, 640],
            created_at=datetime.now(),
            checksum="abc123"
        )
        
        metadata2 = ModelMetadata(
            model_id="test_model_001",
            model_name="Test YOLO Model",
            version="2.0.0",
            framework="YOLOv8",
            backend="ultralytics",
            classes=["person", "car", "dog"],
            input_size=[640, 640],
            created_at=datetime.now(),
            checksum="def456"
        )
        
        self.registry.register_model(metadata1)
        self.registry.register_model(metadata2)
        
        # Verify both versions exist
        retrieved_v1 = self.registry.get_model("test_model_001", "1.0.0")
        retrieved_v2 = self.registry.get_model("test_model_001", "2.0.0")
        
        self.assertEqual(retrieved_v1.version, "1.0.0")
        self.assertEqual(retrieved_v2.version, "2.0.0")
    
    def test_get_model_not_found(self):
        """Test getting a non-existent model."""
        with self.assertRaises(ModelNotFoundError):
            self.registry.get_model("non_existent_model")
    
    def test_list_models(self):
        """Test listing models."""
        metadata1 = ModelMetadata(
            model_id="test_model_001",
            model_name="Test YOLO Model 1",
            version="1.0.0",
            framework="YOLOv8",
            backend="ultralytics",
            classes=["person", "car"],
            input_size=[640, 640],
            created_at=datetime.now(),
            checksum="abc123"
        )
        
        metadata2 = ModelMetadata(
            model_id="test_model_002",
            model_name="Test YOLO Model 2",
            version="1.0.0",
            framework="YOLOv8",
            backend="ultralytics",
            classes=["person", "car"],
            input_size=[640, 640],
            created_at=datetime.now(),
            checksum="def456"
        )
        
        self.registry.register_model(metadata1)
        self.registry.register_model(metadata2)
        
        models = self.registry.list_models()
        self.assertEqual(len(models), 2)
    
    def test_set_active_version(self):
        """Test setting active version."""
        metadata1 = ModelMetadata(
            model_id="test_model_001",
            model_name="Test YOLO Model",
            version="1.0.0",
            framework="YOLOv8",
            backend="ultralytics",
            classes=["person", "car"],
            input_size=[640, 640],
            created_at=datetime.now(),
            checksum="abc123"
        )
        
        metadata2 = ModelMetadata(
            model_id="test_model_001",
            model_name="Test YOLO Model",
            version="2.0.0",
            framework="YOLOv8",
            backend="ultralytics",
            classes=["person", "car", "dog"],
            input_size=[640, 640],
            created_at=datetime.now(),
            checksum="def456"
        )
        
        self.registry.register_model(metadata1)
        self.registry.register_model(metadata2)
        
        # Set version 2.0.0 as active
        self.registry.set_active_version("test_model_001", "2.0.0")
        
        # Get active version
        active_version = self.registry.get_active_version("test_model_001")
        self.assertEqual(active_version, "2.0.0")


class TestInferenceResult(unittest.TestCase):
    """Test cases for InferenceResult and InferenceBatchResult classes."""
    
    def test_inference_result(self):
        """Test creating an InferenceResult."""
        result = InferenceResult(
            class_id=1,
            class_name="person",
            confidence=0.95,
            bbox=[100, 100, 200, 200]
        )
        
        self.assertEqual(result.class_id, 1)
        self.assertEqual(result.class_name, "person")
        self.assertEqual(result.confidence, 0.95)
        self.assertEqual(result.bbox, [100, 100, 200, 200])
        self.assertIsNotNone(result.timestamp)
    
    def test_inference_batch_result(self):
        """Test creating an InferenceBatchResult."""
        result1 = InferenceResult(
            class_id=1,
            class_name="person",
            confidence=0.95,
            bbox=[100, 100, 200, 200]
        )
        
        result2 = InferenceResult(
            class_id=2,
            class_name="car",
            confidence=0.85,
            bbox=[300, 300, 400, 400]
        )
        
        batch_result = InferenceBatchResult(
            results=[result1, result2],
            model_id="test_model_001",
            version="1.0.0",
            input_size=[640, 640],
            processing_time=0.1
        )
        
        self.assertEqual(batch_result.num_detections, 2)
        self.assertEqual(batch_result.model_id, "test_model_001")
        self.assertEqual(batch_result.version, "1.0.0")
        self.assertEqual(batch_result.input_size, [640, 640])
        self.assertEqual(batch_result.processing_time, 0.1)
        
        # Test helper methods
        detections_by_class = batch_result.get_detections_by_class("person")
        self.assertEqual(len(detections_by_class), 1)
        self.assertEqual(detections_by_class[0].class_name, "person")
        
        top_detections = batch_result.get_top_detections(1)
        self.assertEqual(len(top_detections), 1)
        self.assertEqual(top_detections[0].confidence, 0.95)
        
        avg_confidence = batch_result.get_average_confidence()
        self.assertEqual(avg_confidence, 0.9)


class TestModelManager(unittest.TestCase):
    """Test cases for ModelManager class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.event_bus = Mock(spec=EventBus)
        self.manager = ModelManager(event_bus=self.event_bus)
    
    @patch('vision.yolo.model_manager.MockDetectorBackend')
    def test_register_and_load_model(self, mock_backend_class):
        """Test registering and loading a model."""
        # Setup mock backend
        mock_backend_instance = Mock()
        mock_backend_class.return_value = mock_backend_instance
        
        metadata = ModelMetadata(
            model_id="test_model_001",
            model_name="Test YOLO Model",
            version="1.0.0",
            framework="YOLOv8",
            backend="ultralytics",
            classes=["person", "car"],
            input_size=[640, 640],
            created_at=datetime.now(),
            checksum="abc123"
        )
        
        # Register model
        self.manager.register_model(metadata)
        
        # Load model
        backend = self.manager.load_model("test_model_001")
        
        # Verify backend was called
        mock_backend_class.assert_called_once_with(metadata)
        mock_backend_instance.load_model.assert_called_once()
        mock_backend_instance.warmup.assert_called_once()
        
        # Verify event was published
        self.event_bus.publish.assert_called()
    
    def test_get_model_info(self):
        """Test getting model information."""
        metadata = ModelMetadata(
            model_id="test_model_001",
            model_name="Test YOLO Model",
            version="1.0.0",
            framework="YOLOv8",
            backend="ultralytics",
            classes=["person", "car"],
            input_size=[640, 640],
            created_at=datetime.now(),
            checksum="abc123"
        )
        
        self.manager.register_model(metadata)
        
        # Get model info
        info = self.manager.get_model_info("test_model_001")
        
        self.assertEqual(info['model_id'], "test_model_001")
        self.assertEqual(info['version'], "1.0.0")
        self.assertIn('loaded_versions', info)
        self.assertIn('backend_info', info)
    
    def test_list_models(self):
        """Test listing models."""
        metadata1 = ModelMetadata(
            model_id="test_model_001",
            model_name="Test YOLO Model 1",
            version="1.0.0",
            framework="YOLOv8",
            backend="ultralytics",
            classes=["person", "car"],
            input_size=[640, 640],
            created_at=datetime.now(),
            checksum="abc123"
        )
        
        metadata2 = ModelMetadata(
            model_id="test_model_002",
            model_name="Test YOLO Model 2",
            version="1.0.0",
            framework="YOLOv8",
            backend="ultralytics",
            classes=["person", "car"],
            input_size=[640, 640],
            created_at=datetime.now(),
            checksum="def456"
        )
        
        self.manager.register_model(metadata1)
        self.manager.register_model(metadata2)
        
        models = self.manager.list_models()
        self.assertEqual(len(models), 2)
    
    def test_get_model(self):
        """Test getting a specific model."""
        metadata = ModelMetadata(
            model_id="test_model_001",
            model_name="Test YOLO Model",
            version="1.0.0",
            framework="YOLOv8",
            backend="ultralytics",
            classes=["person", "car"],
            input_size=[640, 640],
            created_at=datetime.now(),
            checksum="abc123"
        )
        
        self.manager.register_model(metadata)
        
        # Get model
        retrieved = self.manager.get_model("test_model_001")
        self.assertEqual(retrieved.model_id, "test_model_001")
        self.assertEqual(retrieved.version, "1.0.0")
    
    def test_infer(self):
        """Test performing inference."""
        # Create a mock backend for testing
        metadata = ModelMetadata(
            model_id="test_model_001",
            model_name="Test YOLO Model",
            version="1.0.0",
            framework="YOLOv8",
            backend="ultralytics",
            classes=["person", "car"],
            input_size=[640, 640],
            created_at=datetime.now(),
            checksum="abc123"
        )
        
        self.manager.register_model(metadata)
        
        # Mock the backend's infer method
        with patch.object(self.manager, '_create_backend_instance') as mock_create_backend:
            mock_backend = Mock()
            mock_backend.infer.return_value = InferenceBatchResult(
                results=[],
                model_id="test_model_001",
                version="1.0.0",
                input_size=[640, 640],
                processing_time=0.05
            )
            mock_create_backend.return_value = mock_backend
            
            # Perform inference
            result = self.manager.infer("test_input")
            
            # Verify the backend's infer method was called
            mock_backend.infer.assert_called_once_with("test_input")


if __name__ == '__main__':
    unittest.main()