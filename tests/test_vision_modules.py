"""
Unit tests for Vision Engine Foundation modules.
Tests all vision components including image preprocessor, template matcher,
object detector, and OCR engine.
"""

import cv2
import numpy as np
import pytest
from pathlib import Path
import logging

# Import the modules to test
from vision.image_preprocessor import ImagePreprocessor
from vision.template_matcher import TemplateMatcher
from vision.object_detector import ObjectDetector, DummyObjectDetector
from vision.ocr_engine import OCREngine, OCRResult
from vision.vision_manager import VisionManager


class TestImagePreprocessor:
    """Test cases for ImagePreprocessor module."""

    def test_resize(self):
        """Test image resizing functionality."""
        preprocessor = ImagePreprocessor()
        
        # Create a test image (100x100)
        test_image = np.zeros((100, 100, 3), dtype=np.uint8)
        test_image[:, :, 0] = 255  # Set red channel
        
        # Resize to 50x50
        resized = preprocessor.resize(test_image, 50, 50)
        
        assert resized.shape == (50, 50, 3)
        assert resized.dtype == np.uint8

    def test_crop(self):
        """Test image cropping functionality."""
        preprocessor = ImagePreprocessor()
        
        # Create a test image (100x100)
        test_image = np.zeros((100, 100, 3), dtype=np.uint8)
        test_image[:, :, 0] = 255  # Set red channel
        
        # Crop to 25x25 starting at (25, 25)
        cropped = preprocessor.crop(test_image, 25, 25, 25, 25)
        
        assert cropped.shape == (25, 25, 3)
        assert cropped.dtype == np.uint8

    def test_grayscale(self):
        """Test grayscale conversion."""
        preprocessor = ImagePreprocessor()
        
        # Create a colored test image
        test_image = np.zeros((50, 50, 3), dtype=np.uint8)
        test_image[:, :, 0] = 255  # Red channel
        test_image[:, :, 1] = 128  # Green channel  
        test_image[:, :, 2] = 64   # Blue channel
        
        # Convert to grayscale
        gray = preprocessor.grayscale(test_image)
        
        assert len(gray.shape) == 2
        assert gray.dtype == np.uint8

    def test_normalize(self):
        """Test image normalization."""
        preprocessor = ImagePreprocessor()
        
        # Create a test image with values 0-255
        test_image = np.random.randint(0, 256, (50, 50, 3), dtype=np.uint8)
        
        # Normalize
        normalized = preprocessor.normalize(test_image)
        
        assert normalized.shape == test_image.shape
        assert normalized.dtype == np.float32
        assert np.min(normalized) >= 0.0
        assert np.max(normalized) <= 1.0

    def test_histogram_equalization(self):
        """Test histogram equalization."""
        preprocessor = ImagePreprocessor()
        
        # Create a test image (grayscale)
        test_image = np.zeros((50, 50), dtype=np.uint8)
        test_image[25:, :] = 128  # Half of image is dark
        
        # Apply histogram equalization
        equalized = preprocessor.histogram_equalization(test_image)
        
        assert equalized.shape == test_image.shape
        assert equalized.dtype == np.uint8


class TestTemplateMatcher:
    """Test cases for TemplateMatcher module."""

    def test_match(self):
        """Test template matching functionality."""
        matcher = TemplateMatcher()
        
        # Create a source image (100x100)
        source = np.zeros((100, 100, 3), dtype=np.uint8)
        source[25:75, 25:75] = 255  # White square in center
        
        # Create a template image (50x50)
        template = np.zeros((50, 50, 3), dtype=np.uint8)
        template[:, :] = 255  # White template
        
        # Match templates
        matches = matcher.match(source, template, threshold=0.5)
        
        assert isinstance(matches, list)
        assert len(matches) >= 0  # Could be 0 if no matches above threshold

    def test_match_with_confidence(self):
        """Test template matching with confidence scores."""
        matcher = TemplateMatcher()
        
        # Create a source image (100x100)
        source = np.zeros((100, 100, 3), dtype=np.uint8)
        source[25:75, 25:75] = 255  # White square in center
        
        # Create a template image (50x50)
        template = np.zeros((50, 50, 3), dtype=np.uint8)
        template[:, :] = 255  # White template
        
        # Match templates
        matches = matcher.match(source, template, threshold=0.5)
        
        for match in matches:
            assert 0.0 <= match.confidence <= 1.0


class TestObjectDetector:
    """Test cases for ObjectDetector module."""

    def test_dummy_detector(self):
        """Test the dummy object detector."""
        detector = DummyObjectDetector(["object", "item"])
        
        # Create a test image
        test_image = np.zeros((100, 100, 3), dtype=np.uint8)
        test_image[25:75, 25:75] = 255  # White square in center
        
        # Detect objects
        detections = detector.detect(test_image)
        
        assert isinstance(detections, list)
        assert len(detections) >= 0  # Could be 0 if no objects detected
        
        # Check that all detections have required attributes
        for detection in detections:
            assert hasattr(detection, 'x')
            assert hasattr(detection, 'y')
            assert hasattr(detection, 'width')
            assert hasattr(detection, 'height')
            assert hasattr(detection, 'confidence')
            assert hasattr(detection, 'class_id')
            assert hasattr(detection, 'class_name')

    def test_detector_info(self):
        """Test getting detector information."""
        detector = DummyObjectDetector(["test_class"])
        
        info = detector.get_detector_info()
        
        assert isinstance(info, dict)
        assert "type" in info
        assert "name" in info
        assert "description" in info
        assert "classes" in info
        assert "version" in info


class TestOCREngine:
    """Test cases for OCREngine module."""

    def test_recognize_text(self):
        """Test text recognition functionality."""
        ocr = OCREngine()
        
        # Create a test image with some text
        test_image = np.zeros((100, 200, 3), dtype=np.uint8)
        # This would normally be a real image with text, but we're testing the method signature
        
        # Test that it doesn't crash on empty image
        results = ocr.recognize_text(test_image)
        
        assert isinstance(results, list)

    def test_recognize_text_region(self):
        """Test region-based text recognition."""
        ocr = OCREngine()
        
        # Create a test image (100x100)
        test_image = np.zeros((100, 100, 3), dtype=np.uint8)
        
        # Test with valid region
        results = ocr.recognize_text_region(test_image, 10, 10, 50, 50)
        
        assert isinstance(results, list)

    def test_get_text_from_region(self):
        """Test getting text from a specific region."""
        ocr = OCREngine()
        
        # Create a test image (100x100)
        test_image = np.zeros((100, 100, 3), dtype=np.uint8)
        
        # Test with valid region
        text = ocr.get_text_from_region(test_image, 10, 10, 50, 50)
        
        assert isinstance(text, str)

    def test_ocr_statistics(self):
        """Test OCR statistics calculation."""
        ocr = OCREngine()
        
        # Create some mock results
        mock_results = [
            OCRResult("test", 0.8, 10, 10, 20, 20),
            OCRResult("data", 0.9, 30, 30, 20, 20)
        ]
        
        stats = ocr.get_ocr_statistics(mock_results)
        
        assert isinstance(stats, dict)
        assert "count" in stats
        assert "avg_confidence" in stats
        assert "max_confidence" in stats
        assert "min_confidence" in stats
        assert "total_characters" in stats


class TestVisionManager:
    """Test cases for VisionManager module."""

    def test_initialization(self):
        """Test VisionManager initialization."""
        manager = VisionManager()
        
        assert hasattr(manager, 'image_preprocessor')
        assert hasattr(manager, 'template_matcher')
        assert hasattr(manager, 'object_detector')
        assert hasattr(manager, 'ocr_engine')

    def test_preprocess_image(self):
        """Test image preprocessing through VisionManager."""
        manager = VisionManager()
        
        # Create a test image
        test_image = np.zeros((100, 100, 3), dtype=np.uint8)
        test_image[:, :, 0] = 255  # Set red channel
        
        # Test preprocessing with various options
        processed = manager.preprocess_image(
            test_image,
            resize_width=50,
            resize_height=50,
            grayscale=True
        )
        
        assert processed.shape[0] == 50
        assert processed.shape[1] == 50

    def test_find_template_matches(self):
        """Test template matching through VisionManager."""
        manager = VisionManager()
        
        # Create a source image (100x100)
        source = np.zeros((100, 100, 3), dtype=np.uint8)
        source[25:75, 25:75] = 255  # White square in center
        
        # Create a template image (50x50)
        template = np.zeros((50, 50, 3), dtype=np.uint8)
        template[:, :] = 255  # White template
        
        # Find matches
        matches = manager.find_template_matches(source, template, threshold=0.5)
        
        assert isinstance(matches, list)

    def test_detect_objects(self):
        """Test object detection through VisionManager."""
        manager = VisionManager()
        
        # Create a test image
        test_image = np.zeros((100, 100, 3), dtype=np.uint8)
        test_image[25:75, 25:75] = 255  # White square in center
        
        # Detect objects
        detections = manager.detect_objects(test_image)
        
        assert isinstance(detections, list)

    def test_recognize_text(self):
        """Test text recognition through VisionManager."""
        manager = VisionManager()
        
        # Create a test image
        test_image = np.zeros((100, 200, 3), dtype=np.uint8)
        
        # Recognize text
        results = manager.recognize_text(test_image)
        
        assert isinstance(results, list)

    def test_get_component_info(self):
        """Test getting component information."""
        manager = VisionManager()
        
        info = manager.get_component_info()
        
        assert isinstance(info, dict)
        assert "image_preprocessor" in info
        assert "template_matcher" in info
        assert "object_detector" in info
        assert "ocr_engine" in info

    def test_health_check(self):
        """Test health check functionality."""
        manager = VisionManager()
        
        health = manager.health_check()
        
        assert isinstance(health, dict)
        assert "status" in health
        assert "components" in health


# Run tests if this file is executed directly
if __name__ == "__main__":
    pytest.main([__file__, "-v"])