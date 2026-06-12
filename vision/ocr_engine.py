"""
OCR Engine Module for Vision Engine Foundation.
Provides Tesseract integration for optical character recognition with region support and confidence scoring.
"""

import cv2
import numpy as np
import pytesseract
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from pathlib import Path


@dataclass
class OCRResult:
    """
    Data class representing OCR recognition results.
    
    Attributes:
        text (str): Recognized text
        confidence (float): Confidence score (0.0 to 1.0)
        x (int): X coordinate of bounding box
        y (int): Y coordinate of bounding box
        width (int): Width of bounding box
        height (int): Height of bounding box
    """
    text: str
    confidence: float
    x: int
    y: int
    width: int
    height: int


class OCREngine:
    """
    A class to perform OCR operations using Tesseract.
    
    This class provides functionality for optical character recognition with
    support for region-based OCR and confidence scoring.
    """

    def __init__(self, tesseract_path: Optional[str] = None):
        """
        Initialize the OCREngine.
        
        Args:
            tesseract_path (str, optional): Path to Tesseract executable
        """
        if tesseract_path:
            pytesseract.pytesseract.tesseract_cmd = tesseract_path
            
        # Verify that Tesseract is available
        try:
            pytesseract.get_languages(config='')
        except Exception as e:
            raise RuntimeError(f"Tesseract not found or not properly configured: {e}")

    def recognize_text(self, image: np.ndarray) -> List[OCRResult]:
        """
        Recognize text in an entire image.
        
        Args:
            image (np.ndarray): Input image
            
        Returns:
            List[OCRResult]: List of OCR results with text and confidence scores
            
        Raises:
            ValueError: If image is None
        """
        if image is None:
            raise ValueError("Input image cannot be None")
            
        # Convert to grayscale if needed
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
            
        # Use Tesseract to get OCR data
        data = pytesseract.image_to_data(gray, output_type=pytesseract.Output.DICT)
        
        results = []
        for i in range(len(data['text'])):
            # Skip empty text or low confidence results
            if int(data['conf'][i]) > 0 and data['text'][i].strip():
                result = OCRResult(
                    text=data['text'][i].strip(),
                    confidence=float(data['conf'][i]) / 100.0,  # Convert to 0.0-1.0 range
                    x=int(data['left'][i]),
                    y=int(data['top'][i]),
                    width=int(data['width'][i]),
                    height=int(data['height'][i])
                )
                results.append(result)
                
        return results

    def recognize_text_region(self, image: np.ndarray, x: int, y: int, 
                            width: int, height: int) -> List[OCRResult]:
        """
        Recognize text in a specific region of an image.
        
        Args:
            image (np.ndarray): Input image
            x (int): X coordinate of region
            y (int): Y coordinate of region
            width (int): Width of region
            height (int): Height of region
            
        Returns:
            List[OCRResult]: List of OCR results within the specified region
            
        Raises:
            ValueError: If parameters are invalid
        """
        if image is None:
            raise ValueError("Input image cannot be None")
            
        if x < 0 or y < 0 or width <= 0 or height <= 0:
            raise ValueError("Invalid region parameters")
            
        if x + width > image.shape[1] or y + height > image.shape[0]:
            raise ValueError("Region exceeds image boundaries")
            
        # Extract the region
        region = image[y:y+height, x:x+width]
        
        # Perform OCR on the region
        return self.recognize_text(region)

    def get_text_from_region(self, image: np.ndarray, x: int, y: int, 
                           width: int, height: int) -> str:
        """
        Get recognized text from a specific region of an image.
        
        Args:
            image (np.ndarray): Input image
            x (int): X coordinate of region
            y (int): Y coordinate of region
            width (int): Width of region
            height (int): Height of region
            
        Returns:
            str: Recognized text from the region
            
        Raises:
            ValueError: If parameters are invalid
        """
        if image is None:
            raise ValueError("Input image cannot be None")
            
        results = self.recognize_text_region(image, x, y, width, height)
        
        # Combine all recognized text
        return ' '.join([r.text for r in results if r.text.strip()])

    def get_ocr_statistics(self, results: List[OCRResult]) -> Dict[str, Any]:
        """
        Get statistics about OCR results.
        
        Args:
            results (List[OCRResult]): List of OCR results
            
        Returns:
            Dict[str, Any]: Dictionary containing OCR statistics
        """
        if not results:
            return {
                "count": 0,
                "avg_confidence": 0.0,
                "max_confidence": 0.0,
                "min_confidence": 0.0,
                "total_characters": 0
            }
            
        confidences = [r.confidence for r in results]
        total_chars = sum(len(r.text) for r in results if r.text.strip())
        
        return {
            "count": len(results),
            "avg_confidence": float(np.mean(confidences)),
            "max_confidence": float(max(confidences)),
            "min_confidence": float(min(confidences)),
            "total_characters": total_chars
        }