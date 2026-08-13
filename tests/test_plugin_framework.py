"""
Tests for the plugin framework components.
"""

import unittest
from unittest.mock import Mock, patch
from datetime import datetime
import time

from plugins.base.game_plugin import GamePlugin
from plugins.base.plugin_context import PluginContext
from plugins.base.game_state import GameState
from plugins.base.action import Action, ActionType
from plugins.base.plugin_manager import PluginManager
from plugins.base.plugin_health import PluginHealth
from plugins.base.plugin_metrics import PluginMetrics


class MockGamePlugin(GamePlugin):
    """Mock implementation of GamePlugin for testing."""
    
    def __init__(self, plugin_id: str, plugin_name: str, plugin_version: str,
                 supported_platforms: list, context: PluginContext):
        super().__init__(plugin_id, plugin_name, plugin_version, 
                        supported_platforms, context)
        
    def initialize(self) -> bool:
        return True
        
    def start(self) -> bool:
        return True
        
    def stop(self) -> bool:
        return True
        
    def pause(self) -> bool:
        return True
        
    def resume(self) -> bool:
        return True
        
    def shutdown(self) -> bool:
        return True
        
    def detect_state(self) -> GameState:
        return GameState(
            game_name="test_game",
            screen_name="test_screen",
            state_id="test_state_1",
            confidence=0.95,
            detected_elements=[],
            timestamp=datetime.now(),
            metadata={}
        )
        
    def validate_state(self, state: GameState) -> bool:
        return True
        
    def available_actions(self) -> list:
        return []
        
    def execute_action(self, action: Action) -> bool:
        return True
        
    def health_check(self) -> dict:
        return {"status": "healthy"}


class TestPluginFramework(unittest.TestCase):
    """Test cases for the plugin framework components."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Create a mock context
        self.mock_context = Mock(spec=PluginContext)
        self.mock_context.config_manager = Mock()
        self.mock_context.logger = Mock()
        self.mock_context.event_bus = Mock()
        self.mock_context.health_monitor = Mock()
        self.mock_context.capture_manager = Mock()
        self.mock_context.vision_manager = Mock()
        
    def test_game_plugin_base_class(self):
        """Test the GamePlugin base class functionality."""
        plugin = MockGamePlugin(
            plugin_id="test_plugin_1",
            plugin_name="Test Plugin",
            plugin_version="1.0.0",
            supported_platforms=["Android", "Windows"],
            context=self.mock_context
        )
        
        self.assertEqual(plugin.plugin_id, "test_plugin_1")
        self.assertEqual(plugin.plugin_name, "Test Plugin")
        self.assertEqual(plugin.plugin_version, "1.0.0")
        self.assertEqual(plugin.supported_platforms, ["Android", "Windows"])
        self.assertIsNotNone(plugin.created_at)
        
        # Test that abstract methods are properly defined
        self.assertTrue(callable(plugin.initialize))
        self.assertTrue(callable(plugin.start))
        self.assertTrue(callable(plugin.stop))
        self.assertTrue(callable(plugin.pause))
        self.assertTrue(callable(plugin.resume))
        self.assertTrue(callable(plugin.shutdown))
        self.assertTrue(callable(plugin.detect_state))
        self.assertTrue(callable(plugin.validate_state))
        self.assertTrue(callable(plugin.available_actions))
        self.assertTrue(callable(plugin.execute_action))
        self.assertTrue(callable(plugin.health_check))
        
    def test_game_state(self):
        """Test GameState dataclass."""
        state = GameState(
            game_name="test_game",
            screen_name="main_menu",
            state_id="state_123",
            confidence=0.95,
            detected_elements=["button_start", "button_settings"],
            timestamp=datetime.now(),
            metadata={"user_level": 5}
        )
        
        self.assertEqual(state.game_name, "test_game")
        self.assertEqual(state.screen_name, "main_menu")
        self.assertEqual(state.state_id, "state_123")
        self.assertEqual(state.confidence, 0.95)
        self.assertEqual(state.detected_elements, ["button_start", "button_settings"])
        self.assertIsNotNone(state.timestamp)
        self.assertEqual(state.metadata, {"user_level": 5})
        
        # Test serialization
        state_dict = state.to_dict()
        self.assertIn("game_name", state_dict)
        self.assertIn("timestamp", state_dict)
        
        # Test deserialization
        restored_state = GameState.from_dict(state_dict)
        self.assertEqual(restored_state.game_name, "test_game")
        self.assertEqual(restored_state.screen_name, "main_menu")
        
    def test_action(self):
        """Test Action dataclass."""
        action = Action(
            action_id="action_123",
            action_name="tap_start_button",
            action_type=ActionType.TAP,
            parameters={"x": 100, "y": 200},
            metadata={"source": "plugin"}
        )
        
        self.assertEqual(action.action_id, "action_123")
        self.assertEqual(action.action_name, "tap_start_button")
        self.assertEqual(action.action_type, ActionType.TAP)
        self.assertEqual(action.parameters, {"x": 100, "y": 200})
        self.assertEqual(action.metadata, {"source": "plugin"})
        
        # Test serialization
        action_dict = action.to_dict()
        self.assertIn("action_id", action_dict)
        self.assertIn("created_at", action_dict)
        
        # Test deserialization
        restored_action = Action.from_dict(action_dict)
        self.assertEqual(restored_action.action_id, "action_123")
        self.assertEqual(restored_action.action_name, "tap_start_button")
        
        # Test wait action methods
        wait_action = Action(
            action_id="wait_1",
            action_name="wait_1s",
            action_type=ActionType.WAIT,
            parameters={"duration": 1.0}
        )
        
        self.assertTrue(wait_action.is_wait_action())
        self.assertEqual(wait_action.get_wait_duration(), 1.0)
        self.assertIsNone(Action(
            action_id="wait_2",
            action_name="wait_2s", 
            action_type=ActionType.WAIT,
            parameters={}
        ).get_wait_duration())
        
    def test_plugin_manager(self):
        """Test PluginManager functionality."""
        plugin_manager = PluginManager(self.mock_context)
        
        # Test initialization
        self.assertIsNotNone(plugin_manager.context)
        
        # Test registration (mocked since we don't have actual plugins)
        result = plugin_manager.register_plugin(MockGamePlugin)
        self.assertTrue(result)
        
        # Test loading a plugin
        loaded_plugin = plugin_manager.load_plugin(
            MockGamePlugin,
            "test_plugin_2",
            "Test Plugin 2",
            "1.0.0",
            ["Android"]
        )
        
        self.assertIsNotNone(loaded_plugin)
        self.assertEqual(plugin_manager.get_plugin_count(), 1)
        
        # Test getting plugin
        retrieved_plugin = plugin_manager.get_plugin("test_plugin_2")
        self.assertEqual(retrieved_plugin, loaded_plugin)
        
        # Test listing plugins
        plugins_list = plugin_manager.list_plugins()
        self.assertEqual(len(plugins_list), 1)
        
        # Test unloading plugin
        result = plugin_manager.unload_plugin("test_plugin_2")
        self.assertTrue(result)
        self.assertEqual(plugin_manager.get_plugin_count(), 0)
        
    def test_plugin_health(self):
        """Test PluginHealth dataclass."""
        health = PluginHealth(
            plugin_id="health_test_1",
            plugin_name="Health Test Plugin"
        )
        
        self.assertFalse(health.is_alive)
        self.assertFalse(health.is_running)
        self.assertEqual(health.failures, 0)
        self.assertEqual(health.uptime, 0.0)
        
        # Test marking alive
        health.mark_alive()
        self.assertTrue(health.is_alive)
        
        # Test marking running
        health.mark_running()
        self.assertTrue(health.is_running)
        
        # Test execution tracking
        health.mark_execution(0.1)
        self.assertIsNotNone(health.last_execution)
        self.assertEqual(health.last_execution_time, 0.1)
        
        # Test failure tracking
        health.mark_failure("Test error")
        self.assertEqual(health.failures, 1)
        self.assertEqual(len(health.error_messages), 1)
        self.assertFalse(health.is_alive)  # Should be marked as not alive on failure
        
        # Test uptime calculation
        uptime = health.get_uptime()
        self.assertGreaterEqual(uptime, 0.0)
        
        # Test serialization
        health_dict = health.to_dict()
        self.assertIn("plugin_id", health_dict)
        self.assertIn("start_time", health_dict)
        
        # Test deserialization
        restored_health = PluginHealth.from_dict(health_dict)
        self.assertEqual(restored_health.plugin_id, "health_test_1")
        self.assertEqual(restored_health.plugin_name, "Health Test Plugin")
        
    def test_plugin_metrics(self):
        """Test PluginMetrics dataclass."""
        metrics = PluginMetrics(
            plugin_id="metrics_test_1",
            plugin_name="Metrics Test Plugin"
        )
        
        # Test initial state
        self.assertEqual(metrics.actions_executed, 0)
        self.assertEqual(metrics.state_detections, 0)
        self.assertEqual(metrics.total_failures, 0)
        
        # Test incrementing actions
        metrics.increment_actions_executed()
        metrics.increment_successful_actions()
        metrics.increment_failed_actions()
        
        self.assertEqual(metrics.actions_executed, 1)
        self.assertEqual(metrics.actions_successful, 1)
        self.assertEqual(metrics.actions_failed, 1)
        
        # Test incrementing state detections
        metrics.increment_state_detections()
        metrics.increment_successful_state_detections()
        metrics.increment_failed_state_detections()

        self.assertEqual(metrics.state_detections, 1)
        self.assertEqual(metrics.state_detections_successful, 1)
        self.assertEqual(metrics.state_detections_failed, 1)
        self.assertEqual(metrics.total_failures, 2)  # 1 from actions + 1 from detections
        
        # Test adding error message
        metrics.add_error_message("Test error message")
        self.assertEqual(len(metrics.error_messages), 1)
        self.assertEqual(metrics.total_failures, 4)
        
        # Test execution time recording
        metrics.record_execution_time(0.5)
        self.assertEqual(metrics.execution_latency, 0.5)
        self.assertEqual(metrics.total_execution_time, 0.5)
        
        # Test success rate calculations
        success_rate = metrics.get_success_rate()
        self.assertEqual(success_rate, 50.0)  # 1 successful out of 2 actions
        
        state_success_rate = metrics.get_state_detection_success_rate()
        self.assertEqual(state_success_rate, 50.0)  # 1 successful out of 2 detections
        
        # Test serialization
        metrics_dict = metrics.to_dict()
        self.assertIn("plugin_id", metrics_dict)
        self.assertIn("start_time", metrics_dict)
        
        # Test deserialization
        restored_metrics = PluginMetrics.from_dict(metrics_dict)
        self.assertEqual(restored_metrics.plugin_id, "metrics_test_1")
        self.assertEqual(restored_metrics.plugin_name, "Metrics Test Plugin")
        
    def test_thread_safety(self):
        """Test that PluginManager is thread-safe (basic testing)."""
        plugin_manager = PluginManager(self.mock_context)
        
        # This test ensures the manager can be instantiated
        # More comprehensive thread safety tests would require
        # actual threading scenarios which are beyond this scope
        self.assertIsNotNone(plugin_manager)


if __name__ == '__main__':
    unittest.main()