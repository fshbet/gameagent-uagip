"""
Model manager for UAGIP YOLO Model Management Framework.

This module provides the main interface for managing YOLO models,
including loading, unloading, and retrieving models.
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
import threading
import logging
from datetime import datetime

from vision.yolo.detector_backend import DetectorBackend
from vision.yolo.model_metadata import ModelMetadata
from vision.yolo.model_registry import ModelRegistry
from vision.yolo.inference_result import InferenceResult
from vision.yolo.exceptions import (
    ModelNotFoundError, 
    ModelLoadingError, 
    ModelUnloadingError,
    ModelInferenceError
)
from core.events.event_bus import EventBus
from core.events.event_types import MODEL_REGISTERED, MODEL_LOADED, MODEL_UNLOADED, MODEL_FAILED

logger = logging.getLogger(__name__)


class ModelManager:
    """
    Main manager for YOLO models.
    
    This class provides the primary interface for registering, loading,
    unloading, and managing YOLO models within the framework.
    """
    
    def __init__(self, event_bus: Optional[EventBus] = None):
        """
        Initialize the model manager.
        
        Args:
            event_bus: Optional event bus for publishing events
        """
        self.registry = ModelRegistry()
        self._loaded_models: Dict[str, DetectorBackend] = {}
        self._lock = threading.RLock()  # For thread safety
        self.event_bus = event_bus
        
    def register_model(self, metadata: ModelMetadata) -> None:
        """
        Register a new model in the registry.
        
        Args:
            metadata: Metadata for the model to register
            
        Raises:
            ModelRegistrationError: If registration fails
        """
        with self._lock:
            self.registry.register_model(metadata)
            
            # Publish event
            if self.event_bus:
                self.event_bus.publish(MODEL_REGISTERED, {
                    'model_id': metadata.model_id,
                    'model_name': metadata.model_name,
                    'version': metadata.version
                })
            
            logger.info(f"Registered model {metadata.model_id} version {metadata.version}")
    
    def unregister_model(self, model_id: str, version: Optional[str] = None) -> bool:
        """
        Unregister a model or specific version from the registry.
        
        Args:
            model_id: ID of the model to unregister
            version: Specific version to unregister (if None, removes all versions)
            
        Returns:
            True if unregistration was successful, False otherwise
            
        Raises:
            ModelNotFoundError: If the model is not found
        """
        with self._lock:
            # First check if the model is loaded and unload it if needed
            if model_id in self._loaded_models:
                self.unload_model(model_id)
            
            result = self.registry.unregister_model(model_id, version)
            
            logger.info(f"Unregistered model {model_id}")
            return result
    
    def load_model(self, model_id: str, version: Optional[str] = None) -> DetectorBackend:
        """
        Load a model into memory.
        
        Args:
            model_id: ID of the model to load
            version: Specific version to load (if None, loads active version)
            
        Returns:
            The loaded detector backend
            
        Raises:
            ModelLoadingError: If loading fails
            ModelNotFoundError: If the model is not found
        """
        with self._lock:
            # Get the model metadata
            try:
                metadata = self.registry.get_model(model_id, version)
            except ModelNotFoundError:
                raise ModelNotFoundError(f"Model {model_id} not found")
            
            # Check if already loaded
            if model_id in self._loaded_models:
                logger.info(f"Model {model_id} already loaded")
                return self._loaded_models[model_id]
            
            # Create the backend instance (this is a mock implementation)
            # In a real implementation, this would create an actual backend
            # such as UltralyticsYOLOBackend or ONNXRuntimeBackend
            try:
                # This is a mock implementation - in reality we'd create 
                # a concrete backend based on metadata.backend
                backend = self._create_mock_backend(metadata)
                
                # Load the model (mock implementation)
                if not backend.load_model():
                    raise ModelLoadingError(f"Failed to load model {model_id}")
                
                # Warmup (mock implementation)
                if not backend.warmup():
                    logger.warning(f"Warmup failed for model {model_id}")
                
                self._loaded_models[model_id] = backend
                
                # Publish event
                if self.event_bus:
                    self.event_bus.publish(MODEL_LOADED, {
                        'model_id': model_id,
                        'model_name': metadata.model_name,
                        'version': metadata.version
                    })
                
                logger.info(f"Loaded model {model_id} version {metadata.version}")
                return backend
                
            except Exception as e:
                # Publish failure event
                if self.event_bus:
                    self.event_bus.publish(MODEL_FAILED, {
                        'model_id': model_id,
                        'error': str(e),
                        'operation': 'load'
                    })
                
                raise ModelLoadingError(f"Failed to load model {model_id}: {str(e)}")
    
    def unload_model(self, model_id: str) -> bool:
        """
        Unload a model from memory.
        
        Args:
            model_id: ID of the model to unload
            
        Returns:
            True if unloading was successful, False otherwise
            
        Raises:
            ModelUnloadingError: If unloading fails
        """
        with self._lock:
            if model_id not in self._loaded_models:
                logger.info(f"Model {model_id} not loaded")
                return True  # Already unloaded
            
            try:
                backend = self._loaded_models[model_id]
                
                # Unload the model (mock implementation)
                if not backend.unload_model():
                    raise ModelUnloadingError(f"Failed to unload model {model_id}")
                
                # Remove from loaded models
                del self._loaded_models[model_id]
                
                # Publish event
                if self.event_bus:
                    self.event_bus.publish(MODEL_UNLOADED, {
                        'model_id': model_id
                    })
                
                logger.info(f"Unloaded model {model_id}")
                return True
                
            except Exception as e:
                # Publish failure event
                if self.event_bus:
                    self.event_bus.publish(MODEL_FAILED, {
                        'model_id': model_id,
                        'error': str(e),
                        'operation': 'unload'
                    })
                
                raise ModelUnloadingError(f"Failed to unload model {model_id}: {str(e)}")
    
    def _create_mock_backend(self, metadata: ModelMetadata) -> DetectorBackend:
        """
        Create a mock backend for demonstration purposes.
        
        In a real implementation, this would create actual backends based on 
        the metadata.backend field.
        
        Args:
            metadata: Metadata for the model
            
        Returns:
            Mock detector backend
        """
        # This is a simplified mock - in reality we'd create different backends
        # based on metadata.backend value like 'ultralytics', 'onnx', etc.
        class MockDetectorBackend(DetectorBackend):
            def __init__(self, model_id: str, backend_name: str):
                super().__init__(model_id, backend_name)
                
            def load_model(self) -> bool:
                logger.info(f"Mock loading model {self.model_id}")
                self.is_loaded = True
                return True
                
            def unload_model(self) -> bool:
                logger.info(f"Mock unloading model {self.model_id}")
                self.is_loaded = False
                return True
                
            def infer(self, image) -> List[Dict[str, any]]:
                # Mock inference - return some dummy results
                from datetime import datetime
                result = [
                    {
                        'class_id': 0,
                        'class_name': 'person',
                        'confidence': 0.95,
                        'bbox': (100, 100, 200, 200)
                    }
                ]
                logger.info(f"Mock inference for model {self.model_id}")
                return result
                
            def warmup(self) -> bool:
                logger.info(f"Mock warming up model {self.model_id}")
                return True
                
            def get_info(self) -> Dict[str, any]:
                return {
                    'model_id': self.model_id,
                    'backend': self.backend_name,
                    'is_loaded': self.is_loaded,
                    'framework': 'YOLO',
                    'classes': ['person', 'car', 'dog']
                }
        
        return MockDetectorBackend(metadata.model_id, metadata.backend)
    
    def list_models(self) -> List[tuple]:
        """
        List all registered models with their active versions.
        
        Returns:
            List of tuples (model_id, active_version)
        """
        with self._lock:
            return self.registry.list_models()
    
    def get_model(self, model_id: str, version: Optional[str] = None) -> ModelMetadata:
        """
        Get metadata for a specific model and version.
        
        Args:
            model_id: ID of the model to retrieve
            version: Specific version (if None, returns active version)
            
        Returns:
            ModelMetadata for the requested model
            
        Raises:
            ModelNotFoundError: If the model or version is not found
        """
        with self._lock:
            return self.registry.get_model(model_id, version)
    
    def get_loaded_models(self) -> List[str]:
        """
        Get list of currently loaded model IDs.
        
        Returns:
            List of model IDs that are currently loaded
        """
        with self._lock:
            return list(self._loaded_models.keys())
    
    def is_model_loaded(self, model_id: str) -> bool:
        """
        Check if a model is currently loaded.
        
        Args:
            model_id: ID of the model to check
            
        Returns:
            True if model is loaded, False otherwise
        """
        with self._lock:
            return model_id in self._loaded_models
    
    def get_model_info(self, model_id: str) -> Dict[str, any]:
        """
        Get detailed information about a model.
        
        Args:
            model_id: ID of the model
            
        Returns:
            Dictionary containing model information
        """
        with self._lock:
            try:
                # Try to get from loaded models if available
                if model_id in self._loaded_models:
                    return self._loaded_models[model_id].get_info()
                
                # Otherwise get metadata
                metadata = self.registry.get_active_model(model_id)
                return {
                    'model_id': metadata.model_id,
                    'model_name': metadata.model_name,
                    'version': metadata.version,
                    'framework': metadata.framework,
                    'backend': metadata.backend,
                    'is_loaded': False,
                    'classes': metadata.classes
                }
            except Exception as e:
                logger.error(f"Error getting model info for {model_id}: {str(e)}")
                raise ModelNotFoundError(f"Model {model_id} not found: {str(e)}")
    
    def get_model_health(self, model_id: str) -> Dict[str, any]:
        """
        Get health information for a loaded model.
        
        Args:
            model_id: ID of the model
            
        Returns:
            Dictionary containing model health metrics
        """
        with self._lock:
            if not self.is_model_loaded(model_id):
                return {
                    'model_id': model_id,
                    'status': 'unloaded',
                    'memory_usage': 0,
                    'inference_available': False
                }
            
            # For loaded models, we'd gather actual health metrics
            backend = self._loaded_models[model_id]
            info = backend.get_info()
            
            return {
                'model_id': model_id,
                'status': 'loaded',
                'memory_usage': info.get('memory_usage', 0),
                'inference_available': True,
                'backend': info.get('backend', 'unknown')
            }
    
    def infer(self, model_id: str, image) -> List[InferenceResult]:
        """
        Perform inference using a loaded model.
        
        Args:
            model_id: ID of the model to use for inference
            image: Input image data
            
        Returns:
            List of InferenceResult objects
            
        Raises:
            ModelInferenceError: If inference fails
            ModelNotFoundError: If model is not found or not loaded
        """
        with self._lock:
            if not self.is_model_loaded(model_id):
                raise ModelNotFoundError(f"Model {model_id} not loaded")
            
            try:
                backend = self._loaded_models[model_id]
                results = backend.infer(image)
                
                # Convert to InferenceResult objects
                inference_results = []
                for result in results:
                    inference_result = InferenceResult(
                        class_id=result['class_id'],
                        class_name=result['class_name'],
                        confidence=result['confidence'],
                        bbox=result['bbox']
                    )
                    inference_results.append(inference_result)
                
                return inference_results
                
            except Exception as e:
                raise ModelInferenceError(f"Inference failed for model {model_id}: {str(e)}")