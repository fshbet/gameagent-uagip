"""
Template Matching Module for Vision Engine Foundation.
Provides OpenCV-based template matching with confidence scoring and multiple match support.
"""

import cv2
import numpy as np
from typing import List, Tuple, Optional, Dict, Any
from dataclasses import dataclass
from pathlib import Path


@dataclass
class TemplateMatch:
    """
    Data class representing a template match result.
    
    Attributes:
        x (int): X coordinate of the match
        y (int): Y coordinate of the match
        confidence (float): Confidence score of the match (0.0 to 1.0)
        width (int): Width of the matched region
        height (int): Height of the matched region
    """
    x: int
    y: int
    confidence: float
    width: int
    height: int


class TemplateMatcher:
    """
    A class to perform template matching operations using OpenCV.
    
    This class provides functionality for finding occurrences of a template image
    within a source image, with confidence scoring and support for multiple matches.
    """

    def __init__(self):
        """Initialize the TemplateMatcher."""
        pass

    def match(self, source_image: np.ndarray, template_image: np.ndarray,
              method: int = cv2.TM_CCOEFF_NORMED,
              threshold: float = 0.8,
              max_matches: Optional[int] = None) -> List[TemplateMatch]:
        """
        Perform template matching on an image.
        
        Args:
            source_image (np.ndarray): Source image to search in
            template_image (np.ndarray): Template image to search for
            method (int): OpenCV template matching method (default: TM_CCOEFF_NORMED)
            threshold (float): Minimum confidence threshold (0.0 to 1.0, default: 0.8)
            max_matches (int, optional): Maximum number of matches to return
            
        Returns:
            List[TemplateMatch]: List of template matches with coordinates and confidence scores
            
        Raises:
            ValueError: If inputs are invalid
        """
        if source_image is None or template_image is None:
            raise ValueError("Source and template images cannot be None")
            
        if threshold < 0.0 or threshold > 1.0:
            raise ValueError("Threshold must be between 0.0 and 1.0")
            
        # Ensure the template image is not larger than source
        if (template_image.shape[1] > source_image.shape[1] or 
            template_image.shape[0] > source_image.shape[0]):
            raise ValueError("Template image cannot be larger than source image")
            
        # Perform template matching
        result = cv2.matchTemplate(source_image, template_image, method)
        
        # Get all matches above threshold
        locations = np.where(result >= threshold)
        
        matches = []
        for y, x in zip(*locations):
            # Calculate confidence (for normalized methods, this is already in 0-1 range)
            confidence = float(result[y, x])
            
            match = TemplateMatch(
                x=int(x),
                y=int(y),
                confidence=confidence,
                width=template_image.shape[1],
                height=template_image.shape[0]
            )
            
            matches.append(match)
            
        # Sort by confidence (highest first)
        matches.sort(key=lambda m: m.confidence, reverse=True)
        
        # Limit number of matches if specified
        if max_matches is not None:
            matches = matches[:max_matches]
            
        return matches

    def match_with_roi(self, source_image: np.ndarray, template_image: np.ndarray,
                      roi_x: int, roi_y: int, roi_width: int, roi_height: int,
                      method: int = cv2.TM_CCOEFF_NORMED,
                      threshold: float = 0.8) -> List[TemplateMatch]:
        """
        Perform template matching within a specified region of interest.
        
        Args:
            source_image (np.ndarray): Source image to search in
            template_image (np.ndarray): Template image to search for
            roi_x (int): X coordinate of ROI top-left corner
            roi_y (int): Y coordinate of ROI top-left corner
            roi_width (int): Width of ROI
            roi_height (int): Height of ROI
            method (int): OpenCV template matching method
            threshold (float): Minimum confidence threshold
            
        Returns:
            List[TemplateMatch]: List of template matches within ROI
            
        Raises:
            ValueError: If inputs are invalid
        """
        if source_image is None or template_image is None:
            raise ValueError("Source and template images cannot be None")
            
        # Extract region of interest from source image
        roi = source_image[roi_y:roi_y+roi_height, roi_x:roi_x+roi_width]
        
        # Perform matching on ROI
        matches = self.match(roi, template_image, method, threshold)
        
        # Adjust coordinates to global image coordinates
        for match in matches:
            match.x += roi_x
            match.y += roi_y
            
        return matches

    def get_match_statistics(self, matches: List[TemplateMatch]) -> Dict[str, Any]:
        """
        Get statistics about a list of template matches.
        
        Args:
            matches (List[TemplateMatch]): List of template matches
            
        Returns:
            Dict[str, Any]: Dictionary containing match statistics
        """
        if not matches:
            return {
                "count": 0,
                "avg_confidence": 0.0,
                "max_confidence": 0.0,
                "min_confidence": 0.0
            }
            
        confidences = [m.confidence for m in matches]
        
        return {
            "count": len(matches),
            "avg_confidence": float(np.mean(confidences)),
            "max_confidence": float(max(confidences)),
            "min_confidence": float(min(confidences))
        }