# Dataset Manager Documentation

## Overview

The Dataset Manager is a production-grade platform for managing computer vision datasets within the Vision Engine. It provides comprehensive functionality for creating, organizing, and maintaining datasets with support for images, annotations, versioning, and statistics.

## Architecture

```
vision/datasets/
├── dataset.py
├── dataset_manager.py
├── image_record.py
├── annotation_record.py
├── version_manager.py
└── __init__.py
```

## Core Components

### Dataset Object (`dataset.py`)

A dataclass representing a vision dataset with the following fields:

- `dataset_id`: Unique identifier for the dataset
- `name`: Dataset name
- `version`: Dataset version
- `created_at`: Creation timestamp
- `labels`: List of label names used in the dataset
- `metadata`: Additional metadata dictionary

### Image Record (`image_record.py`)

Tracks image information with fields:

- `image_id`: Unique identifier for the image
- `path`: File path to the image
- `width`: Image width in pixels
- `height`: Image height in pixels
- `source`: Source of the image (camera, file, etc.)
- `hash`: SHA256 hash of the image file
- `tags`: List of tags associated with the image

### Annotation Record (`annotation_record.py`)

Supports multiple annotation types with YOLO compatibility:

- `bbox`: Bounding box coordinates [x, y, width, height]
- `polygon`: Polygon points as list of [x, y] coordinates
- `classification`: Class label for classification annotations
- `confidence`: Confidence score (0.0 to 1.0)

### Version Manager (`version_manager.py`)

Provides version control functionality:

- `create_version()`: Create a new dataset version
- `list_versions()`: List all versions of a dataset
- `rollback_version()`: Revert to a previous version

## Main Features

### Dataset Operations

- **Create**: `create_dataset()` - Creates a new dataset with specified properties
- **Load**: `load_dataset()` - Loads an existing dataset from storage
- **Delete**: `delete_dataset()` - Permanently deletes a dataset
- **List**: `list_datasets()` - Lists all available datasets

### Data Management

- **Add Images**: `add_image()` - Adds image records to datasets
- **Add Annotations**: `add_annotation()` - Adds annotation records to datasets
- **Validate**: `validate_dataset()` - Validates dataset integrity and detects issues
- **Statistics**: `get_dataset_statistics()` - Retrieves dataset statistics

### Version Control

- **Version Creation**: `create_version()` - Creates new versions of datasets
- **Version Listing**: `list_versions()` - Lists all versions with metadata
- **Rollback**: `rollback_version()` - Reverts to previous dataset versions

## Integration Points

### Event Bus Integration

Publishes events:
- `DATASET_CREATED`
- `DATASET_UPDATED` 
- `DATASET_DELETED`

### Logging Integration

Comprehensive logging for all operations including:
- Dataset creation and modification
- Image and annotation management
- Validation and statistics operations
- Version control activities

### Health Monitor Integration

Monitors dataset manager health through:
- Memory usage tracking
- File system health checks
- Thread safety verification
- Performance metrics

## Usage Examples

### Creating a Dataset

```python
from vision.datasets.dataset_manager import DatasetManager

# Initialize manager
manager = DatasetManager(datasets_root="datasets")

# Create a new dataset
dataset = manager.create_dataset(
    name="my_dataset",
    version="1.0.0",
    labels=["cat", "dog", "bird"],
    metadata={"description": "Animal detection dataset"}
)
```

### Adding Images

```python
from vision.datasets.image_record import ImageRecord

# Create image record
image_record = ImageRecord(
    image_id="img_001",
    path="/path/to/image.png",
    width=640,
    height=480,
    source="camera",
    hash="abc123def456"
)

# Add to dataset
manager.add_image("my_dataset", image_record)
```

### Adding Annotations

```python
from vision.datasets.annotation_record import AnnotationRecord, AnnotationType

# Create annotation record
annotation_record = AnnotationRecord(
    annotation_id="ann_001",
    image_id="img_001",
    annotation_type=AnnotationType.BBOX,
    label="cat",
    bbox=[10, 20, 100, 120],
    confidence=0.95
)

# Add to dataset
manager.add_annotation("my_dataset", annotation_record)
```

### Versioning Workflow

```python
# Get version manager for a dataset
version_manager = manager.get_version_manager("my_dataset")

# Create new version
version_manager.create_version("2.0.0", "Major update with new labels")

# List versions
versions = version_manager.list_versions()

# Rollback to previous version
version_manager.rollback_version("1.0.0")
```

## Thread Safety

The Dataset Manager implements thread-safe operations using:
- `threading.RLock()` for exclusive access control
- Atomic operations for dataset modifications
- Proper locking around critical sections

## Statistics

Provides detailed dataset statistics including:
- Image count
- Class count
- Annotation count
- Dataset size (in bytes)
- Unique labels used

## Validation

Comprehensive dataset validation includes:
- Image file existence checks
- Annotation integrity verification
- Duplicate detection by hash
- Error reporting and logging

## Requirements

- Python 3.8+
- Thread-safe operations
- Type hints for all methods
- JSON-based storage format
- Event bus integration
- Logging framework integration
- Health monitor integration

## Success Criteria

- All unit tests pass
- No regressions in existing functionality
- Production-grade implementation with proper error handling
- Comprehensive documentation
- Thread safety and performance considerations addressed