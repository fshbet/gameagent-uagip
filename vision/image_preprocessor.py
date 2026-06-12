"""
Image Preprocessing Module for Vision Engine Foundation.
Provides image preprocessing capabilities including resize, crop, grayscale,
normalize, and histogram equalization.
"""

import cv2
import numpy as np
from typing import Optional, Tuple, Union
from pathlib import Path


class ImagePreprocessor:
    """
    A class to perform various image preprocessing operations on OpenCV images.
    
    This class provides methods for common image preprocessing tasks that are
    essential for computer vision applications.
    """

    def __init__(self):
        """Initialize the ImagePreprocessor."""
        pass

    def resize(self, image: np.ndarray, width: int, height: int, 
               interpolation: int = cv2.INTER_LINEAR) -> np.ndarray:
        """
        Resize an image to specified dimensions.
        
        Args:
            image (np.ndarray): Input image
            width (int): Target width
            height (int): Target height
            interpolation (int): Interpolation method (default: cv2.INTER_LINEAR)
            
        Returns:
            np.ndarray: Resized image
            
        Raises:
            ValueError: If image is None or dimensions are invalid
        """
        if image is None:
            raise ValueError("Input image cannot be None")
        
        if width <= 0 or height <= 0:
            raise ValueError("Width and height must be positive integers")
            
        return cv2.resize(image, (width, height), interpolation=interpolation)

    def crop(self, image: np.ndarray, x: int, y: int, width: int, height: int) -> np.ndarray:
        """
        Crop an image to specified region.
        
        Args:
            image (np.ndarray): Input image
            x (int): X coordinate of top-left corner
            y (int): Y coordinate of top-left corner
            width (int): Width of cropped region
            height (int): Height of cropped region
            
        Returns:
            np.ndarray: Cropped image
            
        Raises:
            ValueError: If parameters are invalid
        """
        if image is None:
            raise ValueError("Input image cannot be None")
            
        if x < 0 or y < 0 or width <= 0 or height <= 0:
            raise ValueError("Invalid crop parameters")
            
        if x + width > image.shape[1] or y + height > image.shape[0]:
            raise ValueError("Crop region exceeds image boundaries")
            
        return image[y:y+height, x:x+width]

    def grayscale(self, image: np.ndarray) -> np.ndarray:
        """
        Convert an image to grayscale.
        
        Args:
            image (np.ndarray): Input image
            
        Returns:
            np.ndarray: Grayscale image
            
        Raises:
            ValueError: If image is None
        """
        if image is None:
            raise ValueError("Input image cannot be None")
            
        return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    def normalize(self, image: np.ndarray) -> np.ndarray:
        """
        Normalize an image to 0-1 range.
        
        Args:
            image (np.ndarray): Input image
            
        Returns:
            np.ndarray: Normalized image
            
        Raises:
            ValueError: If image is None
        """
        if image is None:
            raise ValueError("Input image cannot be None")
            
        # Handle different data types
        if image.dtype != np.float32 and image.dtype != np.float64:
            image = image.astype(np.float32)
            
        return cv2.normalize(image, None, 0.0, 1.0, cv2.NORM_MINMAX)

    def histogram_equalization(self, image: np.ndarray) -> np.ndarray:
        """
        Apply histogram equalization to an image.
        
        Args:
            image (np.ndarray): Input image
            
        Returns:
            np.ndarray: Histogram equalized image
            
        Raises:
            ValueError: If image is None
        """
        if image is None:
            raise ValueError("Input image cannot be None")
            
        # For color images, convert to grayscale first
        if len(image.shape) == 3:
            gray = self.grayscale(image)
        else:
            gray = image
            
        return cv2.equalizeHist(gray)