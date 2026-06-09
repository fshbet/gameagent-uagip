# Event Bus Documentation

## Overview

The Event Bus is a core component of the UAGIP system that facilitates communication between different modules through a publish/subscribe pattern. It supports both synchronous and asynchronous operations, thread safety, event history, filtering, and error isolation.

## Architecture

```
┌─────────────┐    ┌──────────────────┐    ┌─────────────┐
│   Module A  │    │  Event Bus       │    │   Module B  │
│             │    │                  │    │             │
│  Publish    │───▶│  Subscribe       │───▶│  Handle     │
│  Event      │    │  Events          │    │  Event      │
└─────────────┘    └──────────────────┘    └─────────────┘
```

## Features

### 1. Event Base Class
- `event_id`: Unique identifier for each event
- `event_type`: Type of the event (e.g., "system.startup")
- `timestamp`: When the event occurred
- `source`: Module that generated the event
- `payload`: Additional data related to the event

### 2. Event Types
The system supports standard event types including:
- System events: `system.startup`, `system.shutdown`
- Configuration events: `config.loaded`, `config.changed`
- Capture events: `capture.started`, `capture.stopped`
- Frame capture: `frame.captured`
- Object detection: `object.detected`
- Action execution: `action.executed`
- Learning updates: `learning.update`
- Video creation: `video.created`
- Plugin events: `plugin.loaded`, `plugin.unloaded`

### 3. Publish/Subscribe System
Supports:
- `publish(event)`: Synchronous event publishing
- `subscribe(event_type, callback)`: Subscribe to specific event types
- `unsubscribe(event_type, callback)`: Remove subscription

### 4. Async Support
- `publish_async(event)`: Asynchronous event publishing
- Supports both async and sync callbacks in the same system

### 5. Thread Safety
- Uses locks to ensure thread safety
- Multiple publishers are supported safely

### 6. Event History
- Maintains configurable history buffer
- `get_recent_events()` to retrieve recent events
- `clear_history()` to clear event history

### 7. Event Filtering
- Exact event type subscriptions
- Wildcard subscriptions for all events
- All events subscription

### 8. Error Isolation
- If one subscriber fails, other subscribers continue processing
- Exceptions are logged but don't stop the event propagation

### 9. Logging Integration
- Logs event publishing
- Logs subscriber failures
- Logs event statistics

### 10. Statistics
- Total events published
- Events by type
- Subscriber count
- System uptime

## Usage Examples

### Basic Usage
```python
from core.events import EventBus, Event, EventType

# Create event bus
event_bus = EventBus()

# Create and publish an event
event = Event(
    event_type=EventType.SYSTEM_STARTUP,
    source="main",
    payload={"message": "System started"}
)
event_bus.publish(event)
```

### Subscribe to Events
```python
def handle_startup_event(event):
    print(f"Startup event received: {event.payload}")

# Subscribe to specific event type
event_bus.subscribe(EventType.SYSTEM_STARTUP, handle_startup_event)

# Subscribe to all events
event_bus.subscribe_all(handle_startup_event)

# Subscribe with wildcard (all events)
event_bus.subscribe_wildcard(handle_startup_event)
```

### Async Usage
```python
import asyncio

async def async_publish_example():
    event = Event(
        event_type=EventType.FRAME_CAPTURED,
        source="capture_module",
        payload={"frame_id": 123}
    )
    
    # Publish asynchronously
    await event_bus.publish_async(event)
```

### Get Statistics
```python
stats = event_bus.get_stats()
print(f"Total events: {stats.total_events}")
print(f"Subscriber count: {stats.subscriber_count}")
```

## Implementation Details

### Thread Safety
The EventBus uses `threading.Lock` to ensure thread safety for all operations that modify shared state, including:
- Publishing events
- Managing subscribers
- Modifying history
- Updating statistics

### Error Isolation
When a subscriber callback raises an exception, the EventBus:
1. Logs the error
2. Continues processing other subscribers
3. Does not stop event propagation

### Async Support
The EventBus supports both synchronous and asynchronous callbacks:
- Synchronous callbacks are executed in a thread pool for async operations
- Asynchronous callbacks are awaited directly
- Mixed callback types can be used simultaneously

### Event History
- Maintains a configurable history buffer using `collections.deque`
- Automatically manages memory by removing oldest events when buffer is full
- Provides methods to retrieve recent events and clear history

## Best Practices

1. **Use standard event types** from `EventType` class for consistency
2. **Handle exceptions** in subscriber callbacks to prevent system-wide failures
3. **Monitor statistics** to detect issues or performance bottlenecks
4. **Limit history buffer size** to prevent memory issues with high-volume systems
5. **Use appropriate subscription methods** based on your needs (specific, wildcard, all)

## Performance Considerations

- The EventBus is designed for high throughput with thread safety
- Async operations are handled efficiently using `ThreadPoolExecutor`
- History buffer uses `collections.deque` for efficient memory usage
- Statistics are updated atomically to prevent race conditions