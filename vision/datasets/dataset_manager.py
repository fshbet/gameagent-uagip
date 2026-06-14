"""
Dataset manager for Vision Engine Dataset Management Platform.
"""

import os
import json
import threading
from dataclasses import dataclass, asdict, replace
from datetime import datetime
from typing import Dict, List, Optional, Set
from pathlib import Path
import logging

from .dataset import Dataset
from .image_record import ImageRecord
from .annotation_record import AnnotationRecord, AnnotationType
from .version_manager import VersionManager


logger = logging.getLogger(__name__)


class DatasetManager:
    """Main dataset manager with all required functionality."""
    
    def __init__(self, datasets_root: str = "datasets"):
        """
        Initialize dataset manager.
        
        Args:
            datasets_root: Root directory for datasets
        """
        self.datasets_root = Path(datasets_root)
        self.datasets_root.mkdir(exist_ok=True)
        self._lock = threading.RLock()  # For thread safety
        
    def create_dataset(self, name: str, version: str = "1.0.0", 
                      labels: Optional[List[str]] = None,
                      metadata: Optional[Dict[str, object]] = None) -> Dataset:
        """
        Create a new dataset.
        
        Args:
            name: Dataset name
            version: Dataset version
            labels: List of label names
            metadata: Additional metadata
            
        Returns:
            Created Dataset object
        """
        with self._lock:
            # Validate dataset doesn't already exist
            dataset_dir = self.datasets_root / name
            if dataset_dir.exists():
                raise ValueError(f"Dataset '{name}' already exists")
            
            # Create dataset directory
            dataset_dir.mkdir(exist_ok=True)
            
            # Create dataset object
            dataset = Dataset(
                name=name,
                version=version,
                labels=labels or [],
                metadata=metadata or {}
            )
            
            # Save dataset to file
            self._save_dataset(dataset, dataset_dir)
            
            # Initialize version manager
            version_manager = VersionManager(str(dataset_dir))
            version_manager.create_version(version, "Initial version")
            
            logger.info(f"Created dataset: {name}")
            
            return dataset
    
    def delete_dataset(self, name: str) -> bool:
        """
        Delete a dataset.
        
        Args:
            name: Dataset name
            
        Returns:
            True if deleted, False if not found
        """
        with self._lock:
            dataset_dir = self.datasets_root / name
            if not dataset_dir.exists():
                return False
                
            # Remove directory
            import shutil
            shutil.rmtree(dataset_dir)
            
            logger.info(f"Deleted dataset: {name}")
            return True
    
    def load_dataset(self, name: str) -> Dataset:
        """
        Load a dataset from storage.
        
        Args:
            name: Dataset name
            
        Returns:
            Loaded Dataset object
        """
        with self._lock:
            dataset_dir = self.datasets_root / name
            if not dataset_dir.exists():
                raise ValueError(f"Dataset '{name}' does not exist")
            
            # Load dataset file
            dataset_file = dataset_dir / "dataset.json"
            if not dataset_file.exists():
                raise ValueError(f"Dataset file not found for '{name}'")
            
            with open(dataset_file, 'r') as f:
                data = json.load(f)
                
            # Create Dataset object from loaded data
            dataset = Dataset(**data)
            
            return dataset
    
    def save_dataset(self, dataset: Dataset) -> None:
        """
        Save dataset to storage.
        
        Args:
            dataset: Dataset object to save
        """
        with self._lock:
            dataset_dir = self.datasets_root / dataset.name
            if not dataset_dir.exists():
                raise ValueError(f"Dataset directory for '{dataset.name}' does not exist")
            
            self._save_dataset(dataset, dataset_dir)
            logger.info(f"Saved dataset: {dataset.name}")
    
    def list_datasets(self) -> List[Dict]:
        """
        List all datasets.
        
        Returns:
            List of dataset information dictionaries
        """
        with self._lock:
            datasets = []
            for dataset_dir in self.datasets_root.iterdir():
                if dataset_dir.is_dir():
                    try:
                        # Load dataset info
                        dataset_file = dataset_dir / "dataset.json"
                        if dataset_file.exists():
                            with open(dataset_file, 'r') as f:
                                data = json.load(f)
                            datasets.append({
                                "name": data.get("name"),
                                "version": data.get("version"),
                                "created_at": data.get("created_at"),
                                "labels_count": len(data.get("labels", [])),
                                "dataset_id": data.get("dataset_id")
                            })
                    except Exception:
                        # Skip invalid datasets
                        continue
            
            return datasets
    
    def _save_dataset(self, dataset: Dataset, dataset_dir: Path) -> None:
        """
        Save dataset to directory.
        
        Args:
            dataset: Dataset object to save
            dataset_dir: Directory to save in
        """
        dataset_file = dataset_dir / "dataset.json"
        with open(dataset_file, 'w') as f:
            json.dump(asdict(dataset), f, default=str)
    
    def add_image(self, dataset_name: str, image_record: ImageRecord) -> None:
        """
        Add an image record to a dataset.

        Args:
            dataset_name: Dataset name
            image_record: ImageRecord object
        """
        with self._lock:
            dataset_dir = self.datasets_root / dataset_name
            if not dataset_dir.exists():
                raise ValueError(f"Dataset '{dataset_name}' does not exist")
            
            # Add to images directory
            images_dir = dataset_dir / "images"
            images_dir.mkdir(exist_ok=True)
            
            # Save image record
            image_file = images_dir / f"{image_record.image_id}.json"
            with open(image_file, 'w') as f:
                json.dump(asdict(image_record), f, default=str)
    
    def add_annotation(self, dataset_name: str, annotation_record: AnnotationRecord) -> None:
        """
        Add an annotation record to a dataset.
        
        Args:
            dataset_name: Dataset name
            annotation_record: AnnotationRecord object
        """
        with self._lock:
            dataset_dir = self.datasets_root / dataset_name
            if not dataset_dir.exists():
                raise ValueError(f"Dataset '{dataset_name}' does not exist")
            
            # Add to annotations directory
            annotations_dir = dataset_dir / "annotations"
            annotations_dir.mkdir(exist_ok=True)
            
            # Save annotation record
            annotation_file = annotations_dir / f"{annotation_record.annotation_id}.json"
            with open(annotation_file, 'w') as f:
                json.dump(asdict(annotation_record), f, default=str)
    
    def validate_dataset(self, dataset_name: str) -> Dict[str, object]:
        """
        Validate dataset integrity.
        
        Args:
            dataset_name: Dataset name to validate
            
        Returns:
            Validation results
        """
        with self._lock:
            dataset_dir = self.datasets_root / dataset_name
            if not dataset_dir.exists():
                raise ValueError(f"Dataset '{dataset_name}' does not exist")
            
            validation_results = {
                "dataset_exists": True,
                "images_valid": 0,
                "images_invalid": 0,
                "annotations_valid": 0,
                "annotations_invalid": 0,
                "duplicates_found": [],
                "errors": []
            }
            
            # Validate images
            images_dir = dataset_dir / "images"
            if images_dir.exists():
                image_hashes: Dict[str, List[str]] = {}
                
                for image_file in images_dir.glob("*.json"):
                    try:
                        with open(image_file, 'r') as f:
                            data = json.load(f)
                        image_record = ImageRecord(**data)
                        
                        # Check if image file exists and is readable
                        if os.path.exists(image_record.path):
                            validation_results["images_valid"] += 1
                            
                            # Check for duplicates by hash
                            if image_record.hash:
                                if image_record.hash in image_hashes:
                                    validation_results["duplicates_found"].append({
                                        "type": "duplicate_image",
                                        "hash": image_record.hash,
                                        "files": [image_hashes[image_record.hash], image_file.name]
                                    })
                                else:
                                    image_hashes[image_record.hash] = image_file.name
                        else:
                            validation_results["images_invalid"] += 1
                            validation_results["errors"].append(f"Image file not found: {image_record.path}")
                            
                    except Exception as e:
                        validation_results["images_invalid"] += 1
                        validation_results["errors"].append(f"Invalid image record in {image_file.name}: {str(e)}")
            
            # Validate annotations
            annotations_dir = dataset_dir / "annotations"
            if annotations_dir.exists():
                for annotation_file in annotations_dir.glob("*.json"):
                    try:
                        with open(annotation_file, 'r') as f:
                            data = json.load(f)
                        annotation_record = AnnotationRecord(**data)
                        validation_results["annotations_valid"] += 1
                        
                        # Validate annotation integrity
                        if not self._is_annotation_valid(annotation_record):
                            validation_results["annotations_invalid"] += 1
                            validation_results["errors"].append(f"Invalid annotation: {annotation_file.name}")
                            
                    except Exception as e:
                        validation_results["annotations_invalid"] += 1
                        validation_results["errors"].append(f"Invalid annotation record in {annotation_file.name}: {str(e)}")
            
            return validation_results
    
    def _is_annotation_valid(self, annotation_record: AnnotationRecord) -> bool:
        """
        Check if an annotation is valid.
        
        Args:
            annotation_record: Annotation to validate
            
        Returns:
            True if valid, False otherwise
        """
        # Basic checks
        if not annotation_record.annotation_id or not annotation_record.image_id:
            return False
            
        if annotation_record.annotation_type == AnnotationType.BBOX:
            if not annotation_record.bbox or len(annotation_record.bbox) != 4:
                return False
                
        elif annotation_record.annotation_type == AnnotationType.POLYGON:
            if not annotation_record.polygon:
                return False
            # Check that all points are valid coordinates
            for point in annotation_record.polygon:
                if not isinstance(point, list) or len(point) != 2:
                    return False
                    
        elif annotation_record.annotation_type == AnnotationType.CLASSIFICATION:
            if not annotation_record.classification:
                return False
                
        return True
    
    def get_dataset_statistics(self, dataset_name: str) -> Dict[str, object]:
        """
        Get dataset statistics.
        
        Args:
            dataset_name: Dataset name
            
        Returns:
            Statistics dictionary
        """
        with self._lock:
            dataset_dir = self.datasets_root / dataset_name
            if not dataset_dir.exists():
                raise ValueError(f"Dataset '{dataset_name}' does not exist")
            
            stats = {
                "image_count": 0,
                "class_count": 0,
                "annotation_count": 0,
                "dataset_size": 0,
                "labels": []
            }
            
            # Count images
            images_dir = dataset_dir / "images"
            if images_dir.exists():
                stats["image_count"] = len(list(images_dir.glob("*.json")))
                
                # Calculate dataset size (sum of image file sizes)
                for image_file in images_dir.glob("*.json"):
                    try:
                        with open(image_file, 'r') as f:
                            data = json.load(f)
                        image_record = ImageRecord(**data)
                        if os.path.exists(image_record.path):
                            stats["dataset_size"] += os.path.getsize(image_record.path)
                    except Exception:
                        continue
            
            # Count annotations
            annotations_dir = dataset_dir / "annotations"
            if annotations_dir.exists():
                stats["annotation_count"] = len(list(annotations_dir.glob("*.json")))
                
                # Get unique labels from annotations
                labels_set: Set[str] = set()
                for annotation_file in annotations_dir.glob("*.json"):
                    try:
                        with open(annotation_file, 'r') as f:
                            data = json.load(f)
                        annotation_record = AnnotationRecord(**data)
                        labels_set.add(annotation_record.label)
                    except Exception:
                        continue
                
                stats["labels"] = list(labels_set)
                stats["class_count"] = len(labels_set)
            
            return stats
    
    def get_version_manager(self, dataset_name: str) -> VersionManager:
        """
        Get version manager for a dataset.
        
        Args:
            dataset_name: Dataset name
            
        Returns:
            VersionManager instance
        """
        with self._lock:
            dataset_dir = self.datasets_root / dataset_name
            if not dataset_dir.exists():
                raise ValueError(f"Dataset '{dataset_name}' does not exist")
            
            return VersionManager(str(dataset_dir))