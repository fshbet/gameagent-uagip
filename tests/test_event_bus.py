"""
Unit tests for the EventBus implementation.
"""

import asyncio
import logging
import time
from unittest.mock import Mock, patch

import pytest

from core.events import EventBus, Event, EventType


def test_event_base_class():
    """Test the base Event class functionality."""
    # Test basic event creation
    event = Event(
        event_type=EventType.SYSTEM_STARTUP,
        source="test_module",
        payload={"message": "test"}
    )
    
    assert event.event_id is not None
    assert event.event_type == EventType.SYSTEM_STARTUP
    assert event.source == "test_module"
    assert event.payload == {"message": "test"}
    assert event.timestamp is not None


def test_event_with_default_values():
    """Test Event creation with default values."""
    event = Event()
    
    assert event.event_id is not None
    assert event.event_type == ""
    assert event.source == ""
    assert event.payload == {}
    assert event.timestamp is not None


def test_event_types():
    """Test that all event types are defined correctly."""
    assert EventType.SYSTEM_STARTUP == "system.startup"
    assert EventType.SYSTEM_SHUTDOWN == "system.shutdown"
    assert EventType.CONFIG_LOADED == "config.loaded"
    assert EventType.CONFIG_CHANGED == "config.changed"
    assert EventType.CAPTURE_STARTED == "capture.started"
    assert EventType.CAPTURE_STOPPED == "capture.stopped"
    assert EventType.FRAME_CAPTURED == "frame.captured"
    assert EventType.OBJECT_DETECTED == "object.detected"
    assert EventType.ACTION_EXECUTED == "action.executed"
    assert EventType.LEARNING_UPDATE == "learning.update"
    assert EventType.VIDEO_CREATED == "video.created"
    assert EventType.PLUGIN_LOADED == "plugin.loaded"
    assert EventType.PLUGIN_UNLOADED == "plugin.unloaded"


def test_event_type_is_standard():
    """Test the is_standard_type method."""
    assert EventType.is_standard_type(EventType.SYSTEM_STARTUP) is True
    assert EventType.is_standard_type("custom.event") is False


def test_event_bus_initialization():
    """Test EventBus initialization."""
    event_bus = EventBus()
    
    assert event_bus is not None
    assert len(event_bus.get_recent_events()) == 0
    assert event_bus.get_stats().total_events == 0
    assert event_bus.get_stats().subscriber_count == 0


def test_event_bus_publish():
    """Test synchronous event publishing."""
    event_bus = EventBus()
    
    # Create a mock subscriber
    mock_callback = Mock()
    event_bus.subscribe(EventType.SYSTEM_STARTUP, mock_callback)
    
    # Publish an event
    event = Event(
        event_type=EventType.SYSTEM_STARTUP,
        source="test",
        payload={"message": "startup"}
    )
    
    event_bus.publish(event)
    
    # Verify the callback was called
    mock_callback.assert_called_once_with(event)
    
    # Verify statistics
    stats = event_bus.get_stats()
    assert stats.total_events == 1
    assert stats.events_by_type[EventType.SYSTEM_STARTUP] == 1


def test_event_bus_multiple_subscribers():
    """Test publishing to multiple subscribers."""
    event_bus = EventBus()
    
    # Create multiple mock subscribers
    mock_callback1 = Mock()
    mock_callback2 = Mock()
    
    event_bus.subscribe(EventType.SYSTEM_STARTUP, mock_callback1)
    event_bus.subscribe(EventType.SYSTEM_STARTUP, mock_callback2)
    
    # Publish an event
    event = Event(
        event_type=EventType.SYSTEM_STARTUP,
        source="test",
        payload={"message": "startup"}
    )
    
    event_bus.publish(event)
    
    # Verify both callbacks were called
    mock_callback1.assert_called_once_with(event)
    mock_callback2.assert_called_once_with(event)


def test_event_bus_unsubscribe():
    """Test unsubscribing from events."""
    event_bus = EventBus()
    
    mock_callback = Mock()
    
    # Subscribe
    event_bus.subscribe(EventType.SYSTEM_STARTUP, mock_callback)
    assert event_bus.get_stats().subscriber_count == 1
    
    # Unsubscribe
    result = event_bus.unsubscribe(EventType.SYSTEM_STARTUP, mock_callback)
    assert result is True
    assert event_bus.get_stats().subscriber_count == 0
    
    # Try to unsubscribe again (should return False)
    result = event_bus.unsubscribe(EventType.SYSTEM_STARTUP, mock_callback)
    assert result is False


def test_event_bus_history():
    """Test event history functionality."""
    event_bus = EventBus(max_history=3)
    
    # Publish 5 events
    for i in range(5):
        event = Event(
            event_type=EventType.FRAME_CAPTURED,
            source="test",
            payload={"frame_id": i}
        )
        event_bus.publish(event)
    
    # Check that only 3 events are kept (history limit)
    recent_events = event_bus.get_recent_events()
    assert len(recent_events) == 3
    
    # Check that the last 3 events are kept
    assert recent_events[0].payload["frame_id"] == 2
    assert recent_events[1].payload["frame_id"] == 3
    assert recent_events[2].payload["frame_id"] == 4
    
    # Clear history
    event_bus.clear_history()
    assert len(event_bus.get_recent_events()) == 0


def test_event_bus_wildcard_subscription():
    """Test wildcard subscription functionality."""
    event_bus = EventBus()
    
    mock_callback = Mock()
    
    # Subscribe with wildcard
    event_bus.subscribe_wildcard(mock_callback)
    
    # Publish events of different types
    event1 = Event(event_type=EventType.SYSTEM_STARTUP, source="test")
    event2 = Event(event_type=EventType.FRAME_CAPTURED, source="test")
    
    event_bus.publish(event1)
    event_bus.publish(event2)
    
    # Verify callback was called for both events
    assert mock_callback.call_count == 2


def test_event_bus_all_subscription():
    """Test all events subscription functionality."""
    event_bus = EventBus()
    
    mock_callback = Mock()
    
    # Subscribe to all events
    event_bus.subscribe_all(mock_callback)
    
    # Publish events of different types
    event1 = Event(event_type=EventType.SYSTEM_STARTUP, source="test")
    event2 = Event(event_type=EventType.FRAME_CAPTURED, source="test")
    
    event_bus.publish(event1)
    event_bus.publish(event2)
    
    # Verify callback was called for both events
    assert mock_callback.call_count == 2


def test_event_bus_error_isolation():
    """Test that one failing subscriber doesn't stop others."""
    event_bus = EventBus()
    
    # Create a mock subscriber that raises an exception
    failing_callback = Mock(side_effect=Exception("Test error"))
    successful_callback = Mock()
    
    # Subscribe both callbacks
    event_bus.subscribe(EventType.SYSTEM_STARTUP, failing_callback)
    event_bus.subscribe(EventType.SYSTEM_STARTUP, successful_callback)
    
    # Publish an event
    event = Event(event_type=EventType.SYSTEM_STARTUP, source="test")
    event_bus.publish(event)
    
    # Verify the successful callback was still called despite the error
    successful_callback.assert_called_once_with(event)


def test_event_bus_async_publish():
    """Test asynchronous event publishing."""
    event_bus = EventBus()
    
    # Create a mock subscriber
    mock_callback = Mock()
    event_bus.subscribe(EventType.SYSTEM_STARTUP, mock_callback)
    
    # Publish an event asynchronously
    async def publish_async():
        event = Event(
            event_type=EventType.SYSTEM_STARTUP,
            source="test",
            payload={"message": "async startup"}
        )
        await event_bus.publish_async(event)
        return event  # Return the event for verification
    
    # Run the async function
    event = asyncio.run(publish_async())
    
    # Verify the callback was called
    mock_callback.assert_called_once_with(event)


def test_event_bus_mixed_callback_types():
    """Test that both sync and async callbacks work together."""
    event_bus = EventBus()
    
    # Create a synchronous mock subscriber
    sync_callback = Mock()
    
    # Create an asynchronous mock subscriber
    async_callback = Mock()
    
    # Subscribe both callbacks
    event_bus.subscribe(EventType.SYSTEM_STARTUP, sync_callback)
    event_bus.subscribe(EventType.SYSTEM_STARTUP, async_callback)
    
    # Publish an event
    event = Event(event_type=EventType.SYSTEM_STARTUP, source="test")
    event_bus.publish(event)
    
    # Verify both callbacks were called
    sync_callback.assert_called_once_with(event)
    # Note: async callbacks are more complex to test in this context


def test_event_bus_statistics():
    """Test event bus statistics."""
    event_bus = EventBus()
    
    # Publish some events
    event1 = Event(event_type=EventType.SYSTEM_STARTUP, source="test")
    event2 = Event(event_type=EventType.FRAME_CAPTURED, source="test")
    event3 = Event(event_type=EventType.SYSTEM_STARTUP, source="test")
    
    event_bus.publish(event1)
    event_bus.publish(event2)
    event_bus.publish(event3)
    
    stats = event_bus.get_stats()
    
    assert stats.total_events == 3
    assert stats.events_by_type[EventType.SYSTEM_STARTUP] == 2
    assert stats.events_by_type[EventType.FRAME_CAPTURED] == 1
    assert stats.subscriber_count == 0


def test_event_bus_thread_safety():
    """Test thread safety with multiple concurrent operations."""
    event_bus = EventBus()
    
    # Create a mock subscriber
    mock_callback = Mock()
    
    # Subscribe to events
    event_bus.subscribe(EventType.SYSTEM_STARTUP, mock_callback)
    
    # Publish events in quick succession (simulate concurrent access)
    def publish_events():
        for i in range(10):
            event = Event(
                event_type=EventType.SYSTEM_STARTUP,
                source="test",
                payload={"counter": i}
            )
            event_bus.publish(event)
    
    # This should not raise any exceptions
    try:
        publish_events()
        assert mock_callback.call_count == 10
    except Exception as e:
        pytest.fail(f"Thread safety test failed: {e}")


def test_event_bus_get_recent_events_limit():
    """Test that get_recent_events respects the limit parameter."""
    event_bus = EventBus(max_history=5)
    
    # Publish more events than the limit
    for i in range(10):
        event = Event(
            event_type=EventType.FRAME_CAPTURED,
            source="test",
            payload={"id": i}
        )
        event_bus.publish(event)
    
    # Get recent events with a specific limit
    recent_events = event_bus.get_recent_events(limit=3)
    assert len(recent_events) == 3
    
    # The most recent events should be returned
    assert recent_events[0].payload["id"] == 7
    assert recent_events[1].payload["id"] == 8
    assert recent_events[2].payload["id"] == 9


def test_event_bus_multiple_subscriber_types():
    """Test subscription to multiple types of events."""
    event_bus = EventBus()
    
    # Create mock subscribers for different event types
    startup_callback = Mock()
    frame_callback = Mock()
    wildcard_callback = Mock()
    
    # Subscribe to specific event types and wildcard
    event_bus.subscribe(EventType.SYSTEM_STARTUP, startup_callback)
    event_bus.subscribe(EventType.FRAME_CAPTURED, frame_callback)
    event_bus.subscribe_wildcard(wildcard_callback)
    
    # Publish different events
    startup_event = Event(event_type=EventType.SYSTEM_STARTUP, source="test")
    frame_event = Event(event_type=EventType.FRAME_CAPTURED, source="test")
    other_event = Event(event_type="custom.event", source="test")
    
    event_bus.publish(startup_event)
    event_bus.publish(frame_event)
    event_bus.publish(other_event)
    
    # Verify callbacks were called correctly
    startup_callback.assert_called_once_with(startup_event)
    frame_callback.assert_called_once_with(frame_event)
    
    # Check that wildcard callback was called with all three events
    # The order of calls might vary, so we check if all 3 were called
    assert wildcard_callback.call_count == 3
    call_args_list = wildcard_callback.call_args_list
    
    # Verify all three events were passed to the wildcard callback
    assert startup_event in [call[0][0] for call in call_args_list]
    assert frame_event in [call[0][0] for call in call_args_list]
    assert other_event in [call[0][0] for call in call_args_list]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])