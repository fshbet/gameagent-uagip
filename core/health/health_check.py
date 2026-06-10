"""
Health Check Interface for UAGIP Health Monitoring System.
"""

import asyncio
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional, Union

from core.health.component_health import ComponentHealth
from core.health.health_status import HealthStatus


class HealthCheck(ABC):
    """
    Abstract base class for health checks.
    """
    
    def __init__(self, component_id: str, component_name: str):
        """
        Initialize a health check.
        
        Args:
            component_id (str): Unique identifier for the component
            component_name (str): Name of the component
        """
        self.component_id = component_id
        self.component_name = component_name
    
    @abstractmethod
    async def run_check(self) -> ComponentHealth:
        """
        Run the health check and return component health.
        
        Returns:
            ComponentHealth: The health status of the component
        """
        pass
    
    @abstractmethod
    def is_async(self) -> bool:
        """
        Check if this check is asynchronous.
        
        Returns:
            bool: True if async, False if sync
        """
        pass


class SyncHealthCheck(HealthCheck):
    """
    Base class for synchronous health checks.
    """
    
    async def run_check(self) -> ComponentHealth:
        """
        Run the synchronous health check.
        
        Returns:
            ComponentHealth: The health status of the component
        """
        # This will be implemented by subclasses
        pass
    
    def is_async(self) -> bool:
        """
        Check if this check is asynchronous.
        
        Returns:
            bool: False for sync checks
        """
        return False


class AsyncHealthCheck(HealthCheck):
    """
    Base class for asynchronous health checks.
    """
    
    async def run_check(self) -> ComponentHealth:
        """
        Run the asynchronous health check.
        
        Returns:
            ComponentHealth: The health status of the component
        """
        # This will be implemented by subclasses
        pass
    
    def is_async(self) -> bool:
        """
        Check if this check is asynchronous.
        
        Returns:
            bool: True for async checks
        """
        return True