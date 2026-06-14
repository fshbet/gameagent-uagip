"""
Tests for Dataset Manager.
"""

import os
import tempfile
import shutil
from pathlib import Path
import pytest

from vision.datasets.dataset import Dataset
from vision.datasets.image_record import ImageRecord
from vision.datasets.annotation_record import AnnotationRecord, AnnotationType
from vision.datasets.dataset_manager import DatasetManager


class TestDatasetManager:
    """Test cases for DatasetManager."""
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        # Create a temporary directory for tests
        self.temp_dir = tempfile.mkdtemp()
        self.dataset_manager = DatasetManager(datasets_root=self.temp_dir)
        
    def teardown_method(self):
        """Clean up after each test method."""
        # Remove the temporary directory
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_create_dataset(self):
        """Test creating a new dataset."""
        labels = ["cat", "dog", "bird"]
        metadata = {"description": "Test dataset"}
        
        dataset = self.dataset_manager.create_dataset(
            name="test_dataset",
            version="1.0.0",
            labels=labels,
            metadata=metadata
        )
        
        assert dataset.name == "test_dataset"
        assert dataset.version == "1.0.0"
        assert dataset.labels == labels
        assert dataset.metadata == metadata
        
        # Verify dataset directory was created
        dataset_dir = Path(self.temp_dir) / "test_dataset"
        assert dataset_dir.exists()
        
        # Verify dataset file was saved
        dataset_file = dataset_dir / "dataset.json"
        assert dataset_file.exists()
    
    def test_load_dataset(self):
        """Test loading an existing dataset."""
        # First create a dataset
        self.dataset_manager.create_dataset(
            name="test_dataset",
            version="1.0.0",
            labels=["cat", "dog"]
        )
        
        # Load the dataset
        loaded_dataset = self.dataset_manager.load_dataset("test_dataset")
        
        assert loaded_dataset.name == "test_dataset"
        assert loaded_dataset.version == "1.0.0"
        assert loaded_dataset.labels == ["cat", "dog"]
    
    def test_list_datasets(self):
        """Test listing datasets."""
        # Create two datasets
        self.dataset_manager.create_dataset("dataset1", version="1.0.0")
        self.dataset_manager.create_dataset("dataset2", version="2.0.0")
        
        datasets = self.dataset_manager.list_datasets()
        
        assert len(datasets) == 2
        dataset_names = [d["name"] for d in datasets]
        assert "dataset1" in dataset_names
        assert "dataset2" in dataset_names
    
    def test_delete_dataset(self):
        """Test deleting a dataset."""
        # Create a dataset
        self.dataset_manager.create_dataset("test_dataset")
        
        # Verify it exists
        datasets = self.dataset_manager.list_datasets()
        assert len(datasets) == 1
        
        # Delete it
        result = self.dataset_manager.delete_dataset("test_dataset")
        
        assert result is True
        
        # Verify it's gone
        datasets = self.dataset_manager.list_datasets()
        assert len(datasets) == 0
    
    def test_add_image(self):
        """Test adding an image record."""
        # Create a dataset first
        self.dataset_manager.create_dataset("test_dataset")
        
        # Create an image record
        image_record = ImageRecord(
            image_id="img_001",
            path="/path/to/image.png",
            width=640,
            height=480,
            source="camera",
            hash="abc123"
        )
        
        # Add the image
        self.dataset_manager.add_image("test_dataset", image_record)
        
        # Verify it was saved
        dataset_dir = Path(self.temp_dir) / "test_dataset" / "images"
        assert dataset_dir.exists()
        image_file = dataset_dir / "img_001.json"
        assert image_file.exists()
    
    def test_add_annotation(self):
        """Test adding an annotation record."""
        # Create a dataset first
        self.dataset_manager.create_dataset("test_dataset")
        
        # Create an annotation record
        annotation_record = AnnotationRecord(
            annotation_id="ann_001",
            image_id="img_001",
            annotation_type=AnnotationType.BBOX,
            label="cat",
            bbox=[10, 20, 100, 120],
            confidence=0.95
        )
        
        # Add the annotation
        self.dataset_manager.add_annotation("test_dataset", annotation_record)
        
        # Verify it was saved
        dataset_dir = Path(self.temp_dir) / "test_dataset" / "annotations"
        assert dataset_dir.exists()
        annotation_file = dataset_dir / "ann_001.json"
        assert annotation_file.exists()
    
    def test_validate_dataset(self):
        """Test dataset validation."""
        # Create a dataset first
        self.dataset_manager.create_dataset("test_dataset")
        
        # Validate empty dataset
        results = self.dataset_manager.validate_dataset("test_dataset")
        
        assert results["dataset_exists"] is True
        assert results["images_valid"] == 0
        assert results["annotations_valid"] == 0
    
    def test_get_dataset_statistics(self):
        """Test getting dataset statistics."""
        # Create a dataset first
        self.dataset_manager.create_dataset("test_dataset")
        
        # Get statistics for empty dataset
        stats = self.dataset_manager.get_dataset_statistics("test_dataset")
        
        assert stats["image_count"] == 0
        assert stats["class_count"] == 0
        assert stats["annotation_count"] == 0
    
    def test_create_version(self):
        """Test creating a version."""
        # Create a dataset first
        self.dataset_manager.create_dataset("test_dataset")
        
        # Get version manager
        version_manager = self.dataset_manager.get_version_manager("test_dataset")
        
        # Create a version
        version_manager.create_version("v1.0", "Initial version")
        
        # List versions
        versions = version_manager.list_versions()
        assert len(versions) >= 1


if __name__ == "__main__":
    pytest.main([__file__])