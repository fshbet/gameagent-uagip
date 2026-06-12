"""
Vision Manager Module for Vision Engine Foundation.
Orchestrates all vision modules including image preprocessing, template matching,
object detection, and OCR.
"""

import cv2
import numpy as np
from typing import List, Optional, Dict, Any
from pathlib import Path
import logging

# Import vision components
from .image_preprocessor import ImagePreprocessor
from .template_matcher import TemplateMatcher
from .object_detector import ObjectDetector, DummyObjectDetector
from .ocr_engine import OCREngine


class VisionManager:
    """
    A class to orchestrate all vision modules.
    
    This class provides a unified interface for performing computer vision tasks
    by coordinating the different components of the vision engine.
    """

    def __init__(self, logger: Optional[logging.Logger] = None):
        """
        Initialize the VisionManager.
        
        Args:
            logger (logging.Logger, optional): Logger instance to use
        """
        self.logger = logger or logging.getLogger(__name__)
        
        # Initialize vision components
        self.image_preprocessor = ImagePreprocessor()
        self.template_matcher = TemplateMatcher()
        self.object_detector = DummyObjectDetector()
        self.ocr_engine = OCREngine()
        
        self.logger.info("VisionManager initialized with all components")

    def preprocess_image(self, image: np.ndarray, **kwargs) -> np.ndarray:
        """
        Preprocess an image using the image preprocessor.
        
        Args:
            image (np.ndarray): Input image
            **kwargs: Preprocessing parameters
            
        Returns:
            np.ndarray: Preprocessed image
            
        Raises:
            ValueError: If image is None or preprocessing fails
        """
        if image is None:
            raise ValueError("Input image cannot be None")
            
        try:
            # Default preprocessing steps
            if 'resize_width' in kwargs and 'resize_height' in kwargs:
                image = self.image_preprocessor.resize(
                    image, 
                    kwargs['resize_width'], 
                    kwargs['resize_height']
                )
                
            if 'crop_x' in kwargs and 'crop_y' in kwargs and 'crop_width' in kwargs and 'crop_height' in kwargs:
                image = self.image_preprocessor.crop(
                    image,
                    kwargs['crop_x'],
                    kwargs['crop_y'],
                    kwargs['crop_width'],
                    kwargs['crop_height']
                )
                
            if kwargs.get('grayscale', False):
                image = self.image_preprocessor.grayscale(image)
                
            if kwargs.get('normalize', False):
                image = self.image_preprocessor.normalize(image)
                
            if kwargs.get('histogram_equalization', False):
                image = self.image_preprocessor.histogram_equalization(image)
                
            self.logger.debug("Image preprocessing completed successfully")
            return image
            
        except Exception as e:
            self.logger.error(f"Error in image preprocessing: {e}")
            raise

    def find_template_matches(self, source_image: np.ndarray, template_image: np.ndarray,
                            method: int = cv2.TM_CCOEFF_NORMED,
                            threshold: float = 0.8,
                            max_matches: Optional[int] = None) -> List:
        """
        Find template matches in an image.
        
        Args:
            source_image (np.ndarray): Source image to search in
            template_image (np.ndarray): Template image to search for
            method (int): OpenCV template matching method
            threshold (float): Minimum confidence threshold
            max_matches (int, optional): Maximum number of matches to return
            
        Returns:
            List: List of template match results
            
        Raises:
            ValueError: If inputs are invalid
        """
        if source_image is None or template_image is None:
            raise ValueError("Source and template images cannot be None")
            
        try:
            matches = self.template_matcher.match(
                source_image, 
                template_image, 
                method, 
                threshold, 
                max_matches
            )
            
            self.logger.debug(f"Found {len(matches)} template matches")
            return matches
            
        except Exception as e:
            self.logger.error(f"Error in template matching: {e}")
            raise

    def detect_objects(self, image: np.ndarray) -> List:
        """
        Detect objects in an image.
        
        Args:
            image (np.ndarray): Input image
            
        Returns:
            List: List of detected objects with bounding boxes
            
        Raises:
            ValueError: If image is None
        """
        if image is None:
            raise ValueError("Input image cannot be None")
            
        try:
            detections = self.object_detector.detect(image)
            self.logger.debug(f"Detected {len(detections)} objects")
            return detections
            
        except Exception as e:
            self.logger.error(f"Error in object detection: {e}")
            raise

    def recognize_text(self, image: np.ndarray) -> List:
        """
        Recognize text in an image.
        
        Args:
            image (np.ndarray): Input image
            
        Returns:
            List: List of OCR results
            
        Raises:
            ValueError: If image is None
        """
        if image is None:
            raise ValueError("Input image cannot be None")
            
        try:
            results = self.ocr_engine.recognize_text(image)
            self.logger.debug(f"Recognized {len(results)} text regions")
            return results
            
        except Exception as e:
            self.logger.error(f"Error in OCR recognition: {e}")
            raise

    def recognize_text_region(self, image: np.ndarray, x: int, y: int, 
                            width: int, height: int) -> List:
        """
        Recognize text in a specific region of an image.
        
        Args:
            image (np.ndarray): Input image
            x (int): X coordinate of region
            y (int): Y coordinate of region
            width (int): Width of region
            height (int): Height of region
            
        Returns:
            List: List of OCR results in the specified region
            
        Raises:
            ValueError: If parameters are invalid
        """
        if image is None:
            raise ValueError("Input image cannot be None")
            
        try:
            results = self.ocr_engine.recognize_text_region(image, x, y, width, height)
            self.logger.debug(f"Recognized text in region ({x}, {y}, {width}, {height})")
            return results
            
        except Exception as e:
            self.logger.error(f"Error in region OCR: {e}")
            raise

    def get_component_info(self) -> Dict[str, Any]:
        """
        Get information about all vision components.
        
        Returns:
            Dict[str, Any]: Dictionary containing information about all components
        """
        return {
            "image_preprocessor": "Initialized",
            "template_matcher": "Initialized",
            "object_detector": self.object_detector.get_detector_info(),
            "ocr_engine": "Initialized"
        }

    def set_object_detector(self, detector: ObjectDetector):
        """
        Set a custom object detector.
        
        Args:
            detector (ObjectDetector): Object detector instance
        """
        if not isinstance(detector, ObjectDetector):
            raise ValueError("Detector must be an instance of ObjectDetector")
            
        self.object_detector = detector
        self.logger.info("Custom object detector set successfully")

    def health_check(self) -> Dict[str, Any]:
        """
        Perform a health check on the vision manager components.
        
        Returns:
            Dict[str, Any]: Health status of all components
        """
        health_status = {
            "status": "healthy",
            "components": {
                "image_preprocessor": True,
                "template_matcher": True,
                "object_detector": True,
                "ocr_engine": True
            }
        }
        
        # Test each component
        try:
            # Test image preprocessing with a dummy image
            dummy_image = np.zeros((100, 100, 3), dtype=np.uint8)
            self.image_preprocessor.grayscale(dummy_image)
            
            # Test template matching
            self.template_matcher.match(dummy_image, dummy_image)
            
            # Test object detection
            self.object_detector.detect(dummy_image)
            
            # Test OCR
            self.ocr_engine.recognize_text(dummy_image)
            
        except Exception as e:
            health_status["status"] = "unhealthy"
            health_status["error"] = str(e)
            
        return health_status