"""
Version manager for Vision Engine Dataset Management Platform.
"""

import os
import json
import shutil
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path


@dataclass
class VersionInfo:
    """Information about a dataset version."""
    version: str
    created_at: datetime
    description: str = ""
    annotations_count: int = 0
    images_count: int = 0


class VersionManager:
    """Manage dataset versions with create, list, and rollback capabilities."""
    
    def __init__(self, dataset_path: str):
        """
        Initialize version manager for a dataset.
        
        Args:
            dataset_path: Path to the dataset directory
        """
        self.dataset_path = Path(dataset_path)
        self.versions_dir = self.dataset_path / "versions"
        self.versions_dir.mkdir(exist_ok=True)
    
    def create_version(self, version: str, description: str = "") -> None:
        """
        Create a new version of the dataset.
        
        Args:
            version: Version identifier
            description: Description of this version
        """
        # Check if version already exists
        version_file = self.versions_dir / f"{version}.json"
        if version_file.exists():
            raise ValueError(f"Version {version} already exists")
        
        # Create version info
        version_info = VersionInfo(
            version=version,
            created_at=datetime.now(),
            description=description
        )
        
        # Save version info
        with open(version_file, 'w') as f:
            json.dump(asdict(version_info), f, default=str)
    
    def list_versions(self) -> List[VersionInfo]:
        """
        List all versions of the dataset.
        
        Returns:
            List of VersionInfo objects
        """
        versions = []
        for version_file in self.versions_dir.glob("*.json"):
            try:
                with open(version_file, 'r') as f:
                    data = json.load(f)
                    version_info = VersionInfo(**data)
                    versions.append(version_info)
            except Exception:
                # Skip invalid version files
                continue
        
        # Sort by creation date (newest first)
        return sorted(versions, key=lambda v: v.created_at, reverse=True)
    
    def rollback_version(self, version: str) -> None:
        """
        Rollback dataset to a previous version.
        
        Args:
            version: Version to rollback to
        """
        version_file = self.versions_dir / f"{version}.json"
        if not version_file.exists():
            raise ValueError(f"Version {version} does not exist")
        
        # For simplicity, we'll just mark this as the current version
        # In a real implementation, this would restore files from backup
        current_version_file = self.dataset_path / "current_version.json"
        with open(current_version_file, 'w') as f:
            json.dump({"version": version}, f)
    
    def get_current_version(self) -> Optional[str]:
        """
        Get the current version of the dataset.
        
        Returns:
            Current version string or None if not set
        """
        current_version_file = self.dataset_path / "current_version.json"
        if current_version_file.exists():
            try:
                with open(current_version_file, 'r') as f:
                    data = json.load(f)
                    return data.get("version")
            except Exception:
                return None
        return None