"""
Android ADB Executor Interface and Implementations for UAGIP.

This module defines the interface and concrete implementations for executing
ADB commands, supporting both real device execution and mocking for testing.
"""

from abc import ABC, abstractmethod
from typing import Any


class ADBExecutor(ABC):
    """
    Abstract base class for ADB command execution.
    
    This interface allows for different implementations of ADB command execution,
    enabling both real device interaction and mock testing.
    """
    
    @abstractmethod
    def execute_with_timeout(self, command: str, timeout: int = 10) -> Any:
        """
        Execute an ADB command with a specified timeout.
        
        Args:
            command: The ADB command to execute
            timeout: Timeout in seconds
            
        Returns:
            The result of the command execution
            
        Raises:
            Exception: If command execution fails or times out
        """
        pass


class RealADBExecutor(ADBExecutor):
    """
    Concrete implementation for executing ADB commands on real devices.
    
    This implementation uses subprocess to run actual ADB commands.
    """
    
    def execute_with_timeout(self, command: str, timeout: int = 10) -> Any:
        """
        Execute an ADB command with a specified timeout on a real device.
        
        Args:
            command: The ADB command to execute
            timeout: Timeout in seconds
            
        Returns:
            The result of the command execution
            
        Raises:
            Exception: If command execution fails or times out
        """
        import subprocess
        
        # For Android ADB, we'll construct the full adb command
        full_command = f"adb {command}"
        
        try:
            # Execute the command with timeout
            result = subprocess.run(
                full_command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            if result.returncode != 0:
                raise Exception(f"ADB command failed: {result.stderr}")
                
            return result.stdout
            
        except subprocess.TimeoutExpired:
            raise Exception(f"ADB command timed out after {timeout} seconds")
        except Exception as e:
            raise Exception(f"Failed to execute ADB command '{command}': {str(e)}")


class MockADBExecutor(ADBExecutor):
    """
    Mock implementation for testing purposes.
    
    This implementation returns predefined responses and is used in unit tests
    to avoid requiring physical Android devices.
    """
    
    def execute_with_timeout(self, command: str, timeout: int = 10) -> Any:
        """
        Mock execution that returns the command string itself.
        
        This allows tests to verify commands are called correctly without
        executing actual ADB commands.
        
        Args:
            command: The ADB command that would be executed
            timeout: Timeout parameter (not used in mock)
            
        Returns:
            The command string itself
        """
        return command