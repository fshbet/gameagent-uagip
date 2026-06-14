"""
Health Monitor for UAGIP - Main monitoring system.
"""

import asyncio
import logging
from collections import defaultdict
from datetime import datetime
from typing import Dict, List, Optional, Union
from concurrent.futures import ThreadPoolExecutor

from core.health.component_health import ComponentHealth
from core.health.health_check import HealthCheck
from core.health.health_status import HealthStatus
from core.events.event_bus import EventBus
from core.events.event_types import EventType


class HealthMonitor:
    """
    Main health monitor for tracking component health and running checks.
    """
    
    def __init__(self, event_bus: Optional[EventBus] = None):
        """
        Initialize the health monitor.
        
        Args:
            event_bus (EventBus, optional): Event bus for publishing events
        """
        self._checks: Dict[str, HealthCheck] = {}
        self._component_health: Dict[str, ComponentHealth] = {}
        self._event_bus = event_bus
        self._logger = logging.getLogger(__name__)
        self._executor = ThreadPoolExecutor(max_workers=10)
    
    def register_check(self, check: HealthCheck) -> None:
        """
        Register a health check.
        
        Args:
            check (HealthCheck): The health check to register
        """
        self._checks[check.component_id] = check
        self._logger.debug(f"Registered health check for component {check.component_name}")
    
    def remove_check(self, component_id: str) -> bool:
        """
        Remove a health check by component ID.
        
        Args:
            component_id (str): The component ID to remove
            
        Returns:
            bool: True if removed, False if not found
        """
        if component_id in self._checks:
            del self._checks[component_id]
            self._logger.debug(f"Removed health check for component {component_id}")
            return True
        return False
    
    async def run_check(self, component_id: str) -> ComponentHealth:
        """
        Run a single health check.
        
        Args:
            component_id (str): The component ID to check
            
        Returns:
            ComponentHealth: The health status of the component
            
        Raises:
            KeyError: If component ID is not found
        """
        if component_id not in self._checks:
            raise KeyError(f"No health check registered for component {component_id}")
        
        check = self._checks[component_id]
        
        # Publish event
        if self._event_bus:
            await self._event_bus.publish(EventType.HEALTH_CHECK_STARTED, {
                "component_id": component_id,
                "component_name": check.component_name
            })
        
        try:
            # Run the check - this is always async since all checks inherit from HealthCheck which has async run_check()
            component_health = await check.run_check()
            
            # Update internal state
            self._component_health[component_id] = component_health
            
            # Publish event based on status change
            if self._event_bus:
                if component_health.status == HealthStatus.UNHEALTHY:
                    await self._event_bus.publish(EventType.COMPONENT_FAILED, {
                        "component_id": component_id,
                        "component_name": check.component_name,
                        "status": component_health.status.value,
                        "message": component_health.message
                    })
                elif component_health.status == HealthStatus.DEGRADED:
                    await self._event_bus.publish(EventType.COMPONENT_DEGRADED, {
                        "component_id": component_id,
                        "component_name": check.component_name,
                        "status": component_health.status.value,
                        "message": component_health.message
                    })
            
            # Log the result
            self._logger.info(
                f"Health check completed for {check.component_name}: "
                f"{component_health.status.value} - {component_health.message or ''}"
            )
            
            return component_health
            
        except Exception as e:
            # Handle exceptions in health checks
            error_health = ComponentHealth(
                component_id=component_id,
                component_name=check.component_name,
                status=HealthStatus.UNHEALTHY,
                message=str(e)
            )
            
            self._component_health[component_id] = error_health
            
            if self._event_bus:
                await self._event_bus.publish(EventType.COMPONENT_FAILED, {
                    "component_id": component_id,
                    "component_name": check.component_name,
                    "status": HealthStatus.UNHEALTHY.value,
                    "message": str(e)
                })
            
            self._logger.error(
                f"Health check failed for {check.component_name}: {str(e)}"
            )
            
            return error_health
    
    
    def get_system_health(self) -> HealthStatus:
        """
        Get the overall system health status.
        
        Returns:
            HealthStatus: The overall system health
        """
        if not self._component_health:
            return HealthStatus.UNKNOWN
        
        # Count statuses
        status_counts = defaultdict(int)
        for component in self._component_health.values():
            status_counts[component.status] += 1
        
        # Determine overall status based on priority
        if status_counts[HealthStatus.UNHEALTHY] > 0:
            return HealthStatus.UNHEALTHY
        elif status_counts[HealthStatus.DEGRADED] > 0:
            return HealthStatus.DEGRADED
        elif status_counts[HealthStatus.HEALTHY] > 0:
            return HealthStatus.HEALTHY
        else:
            return HealthStatus.UNKNOWN
    
    def get_component_health(self, component_id: str) -> Optional[ComponentHealth]:
        """
        Get health information for a specific component.
        
        Args:
            component_id (str): The component ID
            
        Returns:
            ComponentHealth: The component health or None if not found
        """
        return self._component_health.get(component_id)
    
    def get_health_summary(self) -> Dict[str, int]:
        """
        Get a summary of health status counts.
        
        Returns:
            Dict[str, int]: Dictionary with status counts
        """
        status_counts = defaultdict(int)
        for component in self._component_health.values():
            status_counts[component.status.value] += 1
        
        return dict(status_counts)
    
    def get_all_component_health(self) -> Dict[str, ComponentHealth]:
        """
        Get health information for all components.
        
        Returns:
            Dict[str, ComponentHealth]: Dictionary mapping component IDs to their health
        """
        return self._component_health.copy()

    async def run_all_checks(self) -> Dict[str, ComponentHealth]:
        """
        Run all registered health checks concurrently and return results.

        Returns:
            Dict[str, ComponentHealth]: Dictionary mapping component IDs to their health results
        """
        if not self._checks:
            return {}
        
        # Create tasks for all checks
        tasks = [
            self.run_check(component_id)
            for component_id in self._checks.keys()
        ]
        
        # Run all tasks concurrently using asyncio.gather
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Build result dictionary
        final_results = {}
        for i, (component_id, result) in enumerate(zip(self._checks.keys(), results)):
            if isinstance(result, Exception):
                # Handle exceptions in health checks
                final_results[component_id] = ComponentHealth(
                    component_id=component_id,
                    component_name=self._checks[component_id].component_name,
                    status=HealthStatus.UNHEALTHY,
                    message=str(result)
                )
            else:
                final_results[component_id] = result
        
        return final_results
