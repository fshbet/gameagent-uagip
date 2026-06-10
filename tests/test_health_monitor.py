import asyncio
import unittest
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime

from core.health.health_monitor import HealthMonitor
from core.health.health_check import SyncHealthCheck
from core.health.component_health import ComponentHealth
from core.health.health_status import HealthStatus
from core.events.event_bus import EventBus


class TestHealthCheck(SyncHealthCheck):
    """Test health check implementation."""
    
    def __init__(self, component_id: str, component_name: str, status: HealthStatus = HealthStatus.HEALTHY):
        super().__init__(component_id, component_name)
        self._status = status
    
    async def run_check(self) -> ComponentHealth:
        return ComponentHealth(
            component_id=self.component_id,
            component_name=self.component_name,
            status=self._status,
            message=f"Test check for {self.component_name}"
        )
    
    def is_async(self) -> bool:
        return False


class TestHealthMonitor(unittest.TestCase):
    """Tests for HealthMonitor class."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.event_bus = Mock(spec=EventBus)
        self.health_monitor = HealthMonitor(event_bus=self.event_bus)
    
    def test_register_check(self):
        """Test registering a health check."""
        check = TestHealthCheck("test_id", "Test Component")
        self.health_monitor.register_check(check)
        
        self.assertIn("test_id", self.health_monitor._checks)
        self.assertEqual(self.health_monitor._checks["test_id"], check)
    
    def test_remove_check(self):
        """Test removing a health check."""
        check = TestHealthCheck("test_id", "Test Component")
        self.health_monitor.register_check(check)
        
        # Should return True when removed
        result = self.health_monitor.remove_check("test_id")
        self.assertTrue(result)
        self.assertNotIn("test_id", self.health_monitor._checks)
        
        # Should return False when not found
        result = self.health_monitor.remove_check("nonexistent")
        self.assertFalse(result)
    
    def test_get_system_health(self):
        """Test getting system health status."""
        # Test with no components
        status = self.health_monitor.get_system_health()
        self.assertEqual(status, HealthStatus.UNKNOWN)
        
        # Add a healthy component
        check = TestHealthCheck("test_id", "Test Component", HealthStatus.HEALTHY)
        self.health_monitor.register_check(check)
        self.health_monitor._component_health["test_id"] = ComponentHealth(
            component_id="test_id",
            component_name="Test Component",
            status=HealthStatus.HEALTHY
        )
        
        status = self.health_monitor.get_system_health()
        self.assertEqual(status, HealthStatus.HEALTHY)
    
    def test_get_component_health(self):
        """Test getting component health."""
        check = TestHealthCheck("test_id", "Test Component")
        self.health_monitor.register_check(check)
        
        # Add component health
        expected_health = ComponentHealth(
            component_id="test_id",
            component_name="Test Component",
            status=HealthStatus.HEALTHY,
            message="Test message"
        )
        self.health_monitor._component_health["test_id"] = expected_health
        
        actual_health = self.health_monitor.get_component_health("test_id")
        self.assertEqual(actual_health, expected_health)
        
        # Test with non-existent component
        actual_health = self.health_monitor.get_component_health("nonexistent")
        self.assertIsNone(actual_health)
    
    def test_get_health_summary(self):
        """Test getting health summary."""
        # Test with no components
        summary = self.health_monitor.get_health_summary()
        self.assertEqual(summary, {})
        
        # Add some component health
        self.health_monitor._component_health = {
            "comp1": ComponentHealth(
                component_id="comp1",
                component_name="Component 1",
                status=HealthStatus.HEALTHY
            ),
            "comp2": ComponentHealth(
                component_id="comp2",
                component_name="Component 2",
                status=HealthStatus.DEGRADED
            ),
            "comp3": ComponentHealth(
                component_id="comp3",
                component_name="Component 3",
                status=HealthStatus.HEALTHY
            )
        }
        
        summary = self.health_monitor.get_health_summary()
        expected = {"healthy": 2, "degraded": 1}
        self.assertEqual(summary, expected)
    
    def test_get_all_component_health(self):
        """Test getting all component health."""
        # Add some component health
        expected_health = {
            "comp1": ComponentHealth(
                component_id="comp1",
                component_name="Component 1",
                status=HealthStatus.HEALTHY
            ),
            "comp2": ComponentHealth(
                component_id="comp2",
                component_name="Component 2",
                status=HealthStatus.DEGRADED
            )
        }
        self.health_monitor._component_health = expected_health
        
        actual_health = self.health_monitor.get_all_component_health()
        self.assertEqual(actual_health, expected_health)
    
    @patch('asyncio.gather', new_callable=AsyncMock)
    def test_run_all_checks(self, mock_gather):
        """Test running all checks."""
        # Set up a check
        check = TestHealthCheck("test_id", "Test Component")
        self.health_monitor.register_check(check)
        
        # Mock the gather function to return successful results
        mock_result = [ComponentHealth(
            component_id="test_id",
            component_name="Test Component",
            status=HealthStatus.HEALTHY
        )]
        mock_gather.return_value = mock_result
        
        # Run all checks
        result = asyncio.run(self.health_monitor.run_all_checks())
        
        # Verify results
        self.assertIn("test_id", result)
        self.assertEqual(result["test_id"].status, HealthStatus.HEALTHY)


if __name__ == '__main__':
    unittest.main()