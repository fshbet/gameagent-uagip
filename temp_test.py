#!/usr/bin/env python3
"""Test script to reproduce the coroutine warning."""

import asyncio
import warnings
from unittest.mock import patch, AsyncMock
from core.health.health_monitor import HealthMonitor
from core.health.health_check import SyncHealthCheck
from core.health.component_health import ComponentHealth
from core.health.health_status import HealthStatus

class TestHealthCheck(SyncHealthCheck):
    def __init__(self, component_id: str, component_name: str):
        super().__init__(component_id, component_name)
    
    async def run_check(self) -> ComponentHealth:
        return ComponentHealth(
            component_id=self.component_id,
            component_name=self.component_name,
            status=HealthStatus.HEALTHY,
            message=f"Test check for {self.component_name}"
        )
    
    def is_async(self) -> bool:
        return False

async def test_run_all_checks():
    """Test run_all_checks method directly."""
    # Enable all warnings
    warnings.filterwarnings('error', category=RuntimeWarning)
    
    health_monitor = HealthMonitor()
    
    # Add a check
    check = TestHealthCheck("test_component", "Test Component")
    health_monitor.register_check(check)
    
    # This should trigger the warning if there's an issue
    results = await health_monitor.run_all_checks()
    print(f"Results: {results}")

async def test_with_warnings():
    """Test with warnings enabled to see the actual issue."""
    warnings.filterwarnings('error', category=RuntimeWarning)
    
    # Let's also try to run just the specific problematic code
    health_monitor = HealthMonitor()
    
    # Add a check
    check = TestHealthCheck("test_component", "Test Component")
    health_monitor.register_check(check)
    
    # Try to manually reproduce what happens in run_all_checks method
    print("About to create tasks list...")
    tasks = [
        health_monitor.run_check(component_id)
        for component_id in health_monitor._checks.keys()
    ]
    print(f"Tasks created: {tasks}")
    print(f"Task types: {[type(t) for t in tasks]}")
    
    # Now try to gather them
    print("About to call asyncio.gather...")
    results = await asyncio.gather(*tasks, return_exceptions=True)
    print(f"Gathered results: {results}")

if __name__ == "__main__":
    asyncio.run(test_with_warnings())
