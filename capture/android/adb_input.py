"""
Android ADB Input Module for UAGIP.

This module provides input injection functionality for Android devices connected via ADB.
It supports tap, swipe, long press, text input, and key events.
"""

from typing import Optional
from core.logging.log_manager import LogManager


logger = LogManager().get_logger(__name__)


class ADBInput:
    """
    Android ADB input injection implementation for UAGIP.
    
    This class provides methods to inject various types of input into Android devices
    connected via ADB, including taps, swipes, text input, and key events.
    """
    
    def __init__(self, executor):
        """
        Initialize the ADBInput instance.
        
        Args:
            executor: The ADB executor to use for command execution
        """
        self.executor = executor
    
    def tap(self, x: int, y: int) -> None:
        """
        Perform a tap at the specified coordinates.
        
        Args:
            x: X coordinate of the tap location
            y: Y coordinate of the tap location
            
        Raises:
            Exception: If tap fails
        """
        logger.debug(f"Tapping at ({x}, {y})")
        
        try:
            command = f"shell input tap {x} {y}"
            self.executor.execute_with_timeout(command, timeout=5)
            
            logger.debug(f"Successfully tapped at ({x}, {y})")
            
        except Exception as e:
            logger.error(f"Failed to tap at ({x}, {y}): {e}")
            raise
    
    def swipe(self, x1: int, y1: int, x2: int, y2: int, duration: Optional[int] = None) -> None:
        """
        Perform a swipe from one point to another.
        
        Args:
            x1: Starting X coordinate
            y1: Starting Y coordinate
            x2: Ending X coordinate
            y2: Ending Y coordinate
            duration: Duration of the swipe in milliseconds (optional)
            
        Raises:
            Exception: If swipe fails
        """
        logger.debug(f"Swiping from ({x1}, {y1}) to ({x2}, {y2})")
        
        try:
            if duration:
                command = f"shell input swipe {x1} {y1} {x2} {y2} {duration}"
            else:
                command = f"shell input swipe {x1} {y1} {x2} {y2}"
            
            self.executor.execute_with_timeout(command, timeout=5)
            
            logger.debug(f"Successfully swiped from ({x1}, {y1}) to ({x2}, {y2})")
            
        except Exception as e:
            logger.error(f"Failed to swipe from ({x1}, {y1}) to ({x2}, {y2}): {e}")
            raise
    
    def long_press(self, x: int, y: int, duration: int = 1000) -> None:
        """
        Perform a long press at the specified coordinates.
        
        Args:
            x: X coordinate of the long press location
            y: Y coordinate of the long press location
            duration: Duration of the long press in milliseconds (default: 1000)
            
        Raises:
            Exception: If long press fails
        """
        logger.debug(f"Long pressing at ({x}, {y}) for {duration}ms")
        
        try:
            command = f"shell input swipe {x} {y} {x} {y} {duration}"
            self.executor.execute_with_timeout(command, timeout=5)
            
            logger.debug(f"Successfully long pressed at ({x}, {y}) for {duration}ms")
            
        except Exception as e:
            logger.error(f"Failed to long press at ({x}, {y}) for {duration}ms: {e}")
            raise
    
    def input_text(self, text: str) -> None:
        """
        Input text into the device.
        
        Args:
            text: Text to input
            
        Raises:
            Exception: If text input fails
        """
        logger.debug(f"Inputting text: {text}")
        
        try:
            # Escape special characters for shell command
            escaped_text = text.replace("'", "\\'")
            command = f"shell input text '{escaped_text}'"
            self.executor.execute_with_timeout(command, timeout=5)
            
            logger.debug(f"Successfully input text: {text}")
            
        except Exception as e:
            logger.error(f"Failed to input text '{text}': {e}")
            raise
    
    def key_event(self, keycode: int) -> None:
        """
        Send a key event to the device.
        
        Args:
            keycode: The keycode to send
            
        Raises:
            Exception: If key event fails
        """
        logger.debug(f"Sending key event: {keycode}")
        
        try:
            command = f"shell input keyevent {keycode}"
            self.executor.execute_with_timeout(command, timeout=5)
            
            logger.debug(f"Successfully sent key event: {keycode}")
            
        except Exception as e:
            logger.error(f"Failed to send key event {keycode}: {e}")
            raise