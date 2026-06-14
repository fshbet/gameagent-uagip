#!/usr/bin/env python3
"""
Test script to reproduce the coroutine warning issue.
"""

import asyncio
import unittest
from unittest.mock import Mock, patch
from core.health.health_monitor import HealthMonitor
from core.health.health_check import SyncHealthCheck
from core.health.component_health import ComponentHealth
from core.health.health_status import HealthStatus


class TestAsyncHealthCheck(SyncHealthCheck):
    def __init__(self, component_id: str, component_name: str):
        super().__init__(component_id, component_name)
    
    async def run_check(self) -> ComponentHealth:
        return ComponentHealth(
            component_id=self.component_id,
            component_name=self.component_name,
            status=HealthStatus.HEALTHY,
            message="Test check"
        )
    
    def is_async(self) -> bool:
        return False


class TestCoroutineWarning(unittest.TestCase):
    """Test to reproduce the coroutine warning."""
    
    def test_run_all_checks_coroutine_warning(self):
        """Test that reproduces the coroutine warning by mocking asyncio.gather."""
        # Create a health monitor
        health_monitor = HealthMonitor()
        
        # Add a check
        check = TestAsyncHealthCheck("test_component", "Test Component")
        health_monitor.register_check(check)
        
        # Try to run all checks - this should trigger the warning if there's an issue
        async def test_run():
            results = await health_monitor.run_all_checks()
            return results
            
        # Run the async function
        results = asyncio.run(test_run())
        print("Results:", results)

    @patch('asyncio.gather')
    def test_mocked_gather_warning(self, mock_gather):
        """Test that shows how mocking gather can cause coroutine warnings."""
        # Create a health monitor
        health_monitor = HealthMonitor()
        
        # Add a check
        check = TestAsyncHealthCheck("test_component", "Test Component")
        health_monitor.register_check(check)
        
        # Mock asyncio.gather to return a list of coroutines instead of awaited results
        mock_gather.return_value = [asyncio.create_task(health_monitor.run_check("test_component"))]
        
        # This should trigger the warning about unawaited coroutines
        with self.assertWarns(RuntimeWarning):
            async def test_run():
                results = await health_monitor.run_all_checks()
                return results
                
            asyncio.run(test_run())


if __name__ == '__main__':
    unittest.main()