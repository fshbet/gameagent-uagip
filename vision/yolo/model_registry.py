"""
Model registry for UAGIP YOLO Model Management Framework.

This module provides a persistent registry for managing YOLO models,
including version lookup, active model selection, and rollback capabilities.
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, replace
import threading
import logging
from datetime import datetime

from vision.yolo.model_metadata import ModelMetadata
from vision.yolo.exceptions import ModelNotFoundError, ModelVersionError

logger = logging.getLogger(__name__)


@dataclass
class ModelEntry:
    """
    Registry entry for a model with its metadata and version information.
    
    This class tracks the metadata of a model along with additional information
    about its registration, versioning, and availability status.
    """
    
    # Model metadata
    metadata: ModelMetadata
    
    # Registration information
    registered_at: datetime = None
    is_active: bool = False
    
    # Version tracking
    version_history: List[ModelMetadata] = None
    
    def __post_init__(self):
        """Initialize the model entry after creation."""
        if self.registered_at is None:
            self.registered_at = datetime.now()
        
        if self.version_history is None:
            self.version_history = [self.metadata]


class ModelRegistry:
    """
    Persistent registry for managing YOLO models.
    
    This class provides functionality to register, lookup, and manage
    multiple versions of models with support for active selection and rollback.
    """
    
    def __init__(self):
        """Initialize the model registry."""
        self._models: Dict[str, Dict[str, ModelEntry]] = {}
        self._active_models: Dict[str, str] = {}  # model_id -> version
        self._lock = threading.RLock()  # For thread safety
        
    def register_model(self, metadata: ModelMetadata) -> None:
        """
        Register a new model in the registry.
        
        Args:
            metadata: Metadata for the model to register
            
        Raises:
            ModelRegistrationError: If registration fails
        """
        with self._lock:
            model_id = metadata.model_id
            version = metadata.version
            
            # Create or get model entry
            if model_id not in self._models:
                self._models[model_id] = {}
            
            # Check if this version already exists
            if version in self._models[model_id]:
                logger.warning(f"Model {model_id} version {version} already registered")
                return  # Don't overwrite existing version
            
            # Create new entry
            entry = ModelEntry(metadata=metadata)
            self._models[model_id][version] = entry
            
            # Set as active if this is the first version
            if len(self._models[model_id]) == 1:
                self._active_models[model_id] = version
                entry.is_active = True
            
            logger.info(f"Registered model {model_id} version {version}")
    
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
            if model_id not in self._models:
                raise ModelNotFoundError(f"Model {model_id} not found in registry")
            
            if version is None:
                # Remove all versions of this model
                del self._models[model_id]
                if model_id in self._active_models:
                    del self._active_models[model_id]
                logger.info(f"Unregistered all versions of model {model_id}")
                return True
            else:
                # Remove specific version
                if version not in self._models[model_id]:
                    raise ModelNotFoundError(f"Model {model_id} version {version} not found")
                
                # Check if this is the active version
                if self._active_models.get(model_id) == version:
                    # Find another version to activate, or remove if none exists
                    versions = list(self._models[model_id].keys())
                    versions.remove(version)
                    
                    if versions:
                        # Activate the newest version
                        latest_version = max(versions)
                        self._active_models[model_id] = latest_version
                        self._models[model_id][latest_version].is_active = True
                    else:
                        # No versions left, remove from active models
                        del self._active_models[model_id]
                
                # Remove the version
                del self._models[model_id][version]
                logger.info(f"Unregistered model {model_id} version {version}")
                return True
    
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
            if model_id not in self._models:
                raise ModelNotFoundError(f"Model {model_id} not found")
            
            # Determine which version to get
            if version is None:
                if model_id not in self._active_models:
                    raise ModelNotFoundError(f"No active version for model {model_id}")
                version = self._active_models[model_id]
            
            if version not in self._models[model_id]:
                raise ModelNotFoundError(f"Model {model_id} version {version} not found")
            
            return self._models[model_id][version].metadata
    
    def get_model_versions(self, model_id: str) -> List[str]:
        """
        Get all versions of a specific model.
        
        Args:
            model_id: ID of the model
            
        Returns:
            List of version strings for this model
            
        Raises:
            ModelNotFoundError: If the model is not found
        """
        with self._lock:
            if model_id not in self._models:
                raise ModelNotFoundError(f"Model {model_id} not found")
            
            return list(self._models[model_id].keys())
    
    def get_active_model(self, model_id: str) -> ModelMetadata:
        """
        Get the currently active version of a model.
        
        Args:
            model_id: ID of the model
            
        Returns:
            ModelMetadata for the active version
            
        Raises:
            ModelNotFoundError: If no active version exists
        """
        with self._lock:
            if model_id not in self._active_models:
                raise ModelNotFoundError(f"No active version for model {model_id}")
            
            version = self._active_models[model_id]
            return self.get_model(model_id, version)
    
    def set_active_version(self, model_id: str, version: str) -> bool:
        """
        Set a specific version as the active version for a model.
        
        Args:
            model_id: ID of the model
            version: Version to activate
            
        Returns:
            True if activation was successful, False otherwise
            
        Raises:
            ModelNotFoundError: If the model or version is not found
        """
        with self._lock:
            if model_id not in self._models:
                raise ModelNotFoundError(f"Model {model_id} not found")
            
            if version not in self._models[model_id]:
                raise ModelNotFoundError(f"Model {model_id} version {version} not found")
            
            # Update active version
            old_active_version = self._active_models.get(model_id)
            self._active_models[model_id] = version
            
            # Update is_active flags
            if old_active_version and old_active_version in self._models[model_id]:
                self._models[model_id][old_active_version].is_active = False
            
            self._models[model_id][version].is_active = True
            
            logger.info(f"Set active version for model {model_id} to {version}")
            return True
    
    def rollback_model(self, model_id: str, steps: int = 1) -> bool:
        """
        Rollback a model to a previous version.
        
        Args:
            model_id: ID of the model to rollback
            steps: Number of versions to rollback (default is 1)
            
        Returns:
            True if rollback was successful, False otherwise
            
        Raises:
            ModelNotFoundError: If the model or version is not found
            ModelVersionError: If rollback would go beyond available versions
        """
        with self._lock:
            if model_id not in self._models:
                raise ModelNotFoundError(f"Model {model_id} not found")
            
            # Get all versions sorted chronologically (by creation time)
            versions = list(self._models[model_id].keys())
            current_version = self._active_models.get(model_id)
            
            if not current_version:
                raise ModelNotFoundError(f"No active version for model {model_id}")
            
            # Find current position
            try:
                current_index = versions.index(current_version)
            except ValueError:
                raise ModelVersionError(f"Current version {current_version} not found in history")
            
            # Calculate target index
            target_index = current_index - steps
            
            if target_index < 0:
                raise ModelVersionError(
                    f"Cannot rollback {steps} steps from version {current_version}. "
                    f"Only {current_index + 1} versions available."
                )
            
            # Get target version
            target_version = versions[target_index]
            
            # Perform rollback
            return self.set_active_version(model_id, target_version)
    
    def list_models(self) -> List[Tuple[str, str]]:
        """
        List all registered models with their active versions.
        
        Returns:
            List of tuples (model_id, active_version)
        """
        with self._lock:
            result = []
            for model_id, versions in self._models.items():
                if model_id in self._active_models:
                    active_version = self._active_models[model_id]
                    result.append((model_id, active_version))
            return result
    
    def get_model_count(self) -> int:
        """
        Get the total number of registered models.
        
        Returns:
            Number of unique models in registry
        """
        with self._lock:
            return len(self._models)
    
    def get_version_count(self, model_id: str) -> int:
        """
        Get the number of versions for a specific model.
        
        Args:
            model_id: ID of the model
            
        Returns:
            Number of versions for this model
            
        Raises:
            ModelNotFoundError: If the model is not found
        """
        with self._lock:
            if model_id not in self._models:
                raise ModelNotFoundError(f"Model {model_id} not found")
            
            return len(self._models[model_id])