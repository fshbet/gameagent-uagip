"""
Event Bus implementation for UAGIP.
"""

import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from threading import Lock
from typing import Any, Callable, Dict, List, Optional, Set, Union
from collections import deque

from core.events.event import Event
from core.events.event_types import EventType


@dataclass
class EventBusStats:
    """Statistics for the event bus."""
    total_events: int = 0
    events_by_type: Dict[str, int] = field(default_factory=dict)
    subscriber_count: int = 0
    start_time: datetime = field(default_factory=datetime.now)


class EventBus:
    """
    Production-grade Event Bus for UAGIP system.
    
    Supports publish/subscribe pattern with async support, thread safety,
    event history, filtering, and error isolation.
    """
    
    def __init__(self, max_history: int = 1000):
        """
        Initialize the EventBus.
        
        Args:
            max_history: Maximum number of events to keep in history buffer
        """
        self._subscribers: Dict[str, List[Callable]] = {}
        self._wildcard_subscribers: List[Callable] = []
        self._all_subscribers: List[Callable] = []
        self._history: deque = deque(maxlen=max_history)
        self._lock = Lock()
        self._stats = EventBusStats()
        self._logger = logging.getLogger(__name__)
        
        # For async operations
        self._executor = ThreadPoolExecutor(max_workers=10)
        
    def publish(self, event: Event) -> None:
        """
        Publish an event synchronously.
        
        Args:
            event: The event to publish
        """
        # Add to history
        with self._lock:
            self._history.append(event)
            self._stats.total_events += 1
            
            # Update event type statistics
            event_type = event.event_type
            if event_type in self._stats.events_by_type:
                self._stats.events_by_type[event_type] += 1
            else:
                self._stats.events_by_type[event_type] = 1
                
        # Log the event
        self._logger.info(f"Published event: {event.event_type} ({event.event_id})")
        
        # Notify subscribers
        self._notify_subscribers(event)
    
    async def publish_async(self, event: Event) -> None:
        """
        Publish an event asynchronously.
        
        Args:
            event: The event to publish
        """
        # Add to history
        with self._lock:
            self._history.append(event)
            self._stats.total_events += 1
            
            # Update event type statistics
            event_type = event.event_type
            if event_type in self._stats.events_by_type:
                self._stats.events_by_type[event_type] += 1
            else:
                self._stats.events_by_type[event_type] = 1
                
        # Log the event
        self._logger.info(f"Published async event: {event.event_type} ({event.event_id})")
        
        # Notify subscribers asynchronously
        await self._notify_subscribers_async(event)
    
    def subscribe(self, event_type: str, callback: Callable) -> None:
        """
        Subscribe to events of a specific type.
        
        Args:
            event_type: The event type to subscribe to
            callback: The callback function to call when event is published
        """
        with self._lock:
            if event_type not in self._subscribers:
                self._subscribers[event_type] = []
            self._subscribers[event_type].append(callback)
            self._stats.subscriber_count += 1
            
        self._logger.debug(f"Subscribed to {event_type}")
    
    def subscribe_wildcard(self, callback: Callable) -> None:
        """
        Subscribe to all events using wildcard subscription.
        
        Args:
            callback: The callback function to call for all events
        """
        with self._lock:
            self._wildcard_subscribers.append(callback)
            self._stats.subscriber_count += 1
            
        self._logger.debug("Subscribed to all events (wildcard)")
    
    def subscribe_all(self, callback: Callable) -> None:
        """
        Subscribe to all events using all events subscription.
        
        Args:
            callback: The callback function to call for all events
        """
        with self._lock:
            self._all_subscribers.append(callback)
            self._stats.subscriber_count += 1
            
        self._logger.debug("Subscribed to all events")
    
    def unsubscribe(self, event_type: str, callback: Callable) -> bool:
        """
        Unsubscribe from events of a specific type.
        
        Args:
            event_type: The event type to unsubscribe from
            callback: The callback function to remove
            
        Returns:
            True if the subscription was removed, False if not found
        """
        with self._lock:
            if event_type in self._subscribers:
                try:
                    self._subscribers[event_type].remove(callback)
                    self._stats.subscriber_count -= 1
                    return True
                except ValueError:
                    return False
            return False
    
    def unsubscribe_wildcard(self, callback: Callable) -> bool:
        """
        Unsubscribe from wildcard subscription.
        
        Args:
            callback: The callback function to remove
            
        Returns:
            True if the subscription was removed, False if not found
        """
        with self._lock:
            try:
                self._wildcard_subscribers.remove(callback)
                self._stats.subscriber_count -= 1
                return True
            except ValueError:
                return False
    
    def unsubscribe_all(self, callback: Callable) -> bool:
        """
        Unsubscribe from all events subscription.
        
        Args:
            callback: The callback function to remove
            
        Returns:
            True if the subscription was removed, False if not found
        """
        with self._lock:
            try:
                self._all_subscribers.remove(callback)
                self._stats.subscriber_count -= 1
                return True
            except ValueError:
                return False
    
    def get_recent_events(self, limit: int = 100) -> List[Event]:
        """
        Get recent events from history.
        
        Args:
            limit: Maximum number of events to return
            
        Returns:
            List of recent events
        """
        with self._lock:
            # Convert deque to list and limit the size
            events = list(self._history)
            return events[-limit:] if len(events) > limit else events
    
    def clear_history(self) -> None:
        """Clear event history."""
        with self._lock:
            self._history.clear()
    
    def get_stats(self) -> EventBusStats:
        """
        Get current statistics.
        
        Returns:
            EventBusStats object with current statistics
        """
        return self._stats
    
    def _notify_subscribers(self, event: Event) -> None:
        """
        Notify all subscribers of an event synchronously.
        
        Args:
            event: The event to notify subscribers about
        """
        # Notify specific type subscribers
        if event.event_type in self._subscribers:
            for callback in self._subscribers[event.event_type]:
                try:
                    callback(event)
                except Exception as e:
                    self._logger.error(f"Error in subscriber for {event.event_type}: {e}")
        
        # Notify wildcard subscribers
        for callback in self._wildcard_subscribers:
            try:
                callback(event)
            except Exception as e:
                self._logger.error(f"Error in wildcard subscriber: {e}")
        
        # Notify all subscribers
        for callback in self._all_subscribers:
            try:
                callback(event)
            except Exception as e:
                self._logger.error(f"Error in all subscriber: {e}")
    
    async def _notify_subscribers_async(self, event: Event) -> None:
        """
        Notify all subscribers of an event asynchronously.
        
        Args:
            event: The event to notify subscribers about
        """
        # Notify specific type subscribers
        if event.event_type in self._subscribers:
            tasks = []
            for callback in self._subscribers[event.event_type]:
                try:
                    if asyncio.iscoroutinefunction(callback):
                        tasks.append(callback(event))
                    else:
                        # Run sync callback in thread pool
                        task = asyncio.get_event_loop().run_in_executor(
                            self._executor, callback, event
                        )
                        tasks.append(task)
                except Exception as e:
                    self._logger.error(f"Error preparing async subscriber for {event.event_type}: {e}")
            
            # Wait for all tasks to complete
            await asyncio.gather(*tasks, return_exceptions=True)
        
        # Notify wildcard subscribers
        tasks = []
        for callback in self._wildcard_subscribers:
            try:
                if asyncio.iscoroutinefunction(callback):
                    tasks.append(callback(event))
                else:
                    # Run sync callback in thread pool
                    task = asyncio.get_event_loop().run_in_executor(
                        self._executor, callback, event
                    )
                    tasks.append(task)
            except Exception as e:
                self._logger.error(f"Error preparing async wildcard subscriber: {e}")
        
        await asyncio.gather(*tasks, return_exceptions=True)
        
        # Notify all subscribers
        tasks = []
        for callback in self._all_subscribers:
            try:
                if asyncio.iscoroutinefunction(callback):
                    tasks.append(callback(event))
                else:
                    # Run sync callback in thread pool
                    task = asyncio.get_event_loop().run_in_executor(
                        self._executor, callback, event
                    )
                    tasks.append(task)
            except Exception as e:
                self._logger.error(f"Error preparing async all subscriber: {e}")
        
        await asyncio.gather(*tasks, return_exceptions=True)