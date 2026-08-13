"""
Custom exceptions for UAGIP YOLO Model Management Framework.

This module defines all custom exceptions that may be raised by the YOLO model management components.
"""

from typing import Optional


class YOLOModelException(Exception):
    """
    Base exception class for YOLO model management errors.
    
    All custom exceptions in this framework should inherit from this class.
    """
    
    def __init__(self, message: str, error_code: Optional[str] = None):
        """
        Initialize the base YOLO model exception.
        
        Args:
            message: Error message
            error_code: Optional error code for identification
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code


class ModelRegistrationError(YOLOModelException):
    """
    Exception raised when there's an error registering a model.
    
    This exception is raised when attempting to register a model with invalid parameters
    or when the registration process fails for any reason.
    """
    
    def __init__(self, message: str, error_code: Optional[str] = None):
        """
        Initialize the model registration error.
        
        Args:
            message: Error message
            error_code: Optional error code for identification
        """
        super().__init__(message, error_code)


class ModelLoadingError(YOLOModelException):
    """
    Exception raised when there's an error loading a model.
    
    This exception is raised when attempting to load a model fails,
    either due to file corruption, incorrect format, or other loading issues.
    """
    
    def __init__(self, message: str, error_code: Optional[str] = None):
        """
        Initialize the model loading error.
        
        Args:
            message: Error message
            error_code: Optional error code for identification
        """
        super().__init__(message, error_code)


class ModelUnloadingError(YOLOModelException):
    """
    Exception raised when there's an error unloading a model.
    
    This exception is raised when attempting to unload a model fails,
    typically due to system issues or resource conflicts.
    """
    
    def __init__(self, message: str, error_code: Optional[str] = None):
        """
        Initialize the model unloading error.
        
        Args:
            message: Error message
            error_code: Optional error code for identification
        """
        super().__init__(message, error_code)


class ModelNotFoundError(YOLOModelException):
    """
    Exception raised when a requested model is not found.
    
    This exception is raised when trying to access a model that doesn't exist
    in the registry or has been removed.
    """
    
    def __init__(self, message: str, error_code: Optional[str] = None):
        """
        Initialize the model not found error.
        
        Args:
            message: Error message
            error_code: Optional error code for identification
        """
        super().__init__(message, error_code)


class ModelInferenceError(YOLOModelException):
    """
    Exception raised when there's an error during model inference.
    
    This exception is raised when the model fails to produce valid inference results,
    either due to input issues, model problems, or system errors.
    """
    
    def __init__(self, message: str, error_code: Optional[str] = None):
        """
        Initialize the model inference error.
        
        Args:
            message: Error message
            error_code: Optional error code for identification
        """
        super().__init__(message, error_code)


class ModelVersionError(YOLOModelException):
    """
    Exception raised when there's an issue with model versioning.
    
    This exception is raised when attempting to access a model version that doesn't exist
    or when there are conflicts in version management.
    """
    
    def __init__(self, message: str, error_code: Optional[str] = None):
        """
        Initialize the model version error.
        
        Args:
            message: Error message
            error_code: Optional error code for identification
        """
        super().__init__(message, error_code)