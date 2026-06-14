#!/usr/bin/env python3
"""
Test script to reproduce the coroutine warning issue.
"""

import asyncio
import warnings
from unittest.mock import Mock
from core.health.health_monitor import HealthMonitor
from core.events.event_bus import EventBus

# Enable all warnings
warnings.filterwarnings('error', category=RuntimeWarning)

async def test_coroutine_warning():
    """Test that reproduces the coroutine warning."""
    
    # Create a mock event bus
    event_bus = Mock(spec=EventBus)
    
    # Create health monitor
    health_monitor = HealthMonitor(event_bus=event_bus)
    
    # Try to trigger the run_all_checks method which should cause the warning
    try:
        result = await health_monitor.run_all_checks()
        print("run_all_checks completed without error")
        print(f"Result: {result}")
    except RuntimeWarning as e:
        print(f"RuntimeWarning caught: {e}")
        raise
    except Exception as e:
        print(f"Other exception: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(test_coroutine_warning())