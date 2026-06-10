# Health Monitor System

## Overview

The Health Monitor System is a production-grade component for tracking and managing the health status of various components within the UAGIP system. It provides comprehensive monitoring capabilities including built-in checks, event integration, logging, and API endpoints.

## Architecture

```
core/
└── health/
    ├── __init__.py
    ├── health_check.py
    ├── health_monitor.py
    ├── health_status.py
    ├── component_health.py
    ├── built_in_checks.py
    └── health_monitor.py
```

## Core Components

### HealthStatus Enum
Defines the possible health states:
- `HEALTHY`: Component is functioning properly
- `DEGRADED`: Component is partially functional
- `UNHEALTHY`: Component is not functioning
- `UNKNOWN`: Health status cannot be determined

### ComponentHealth Dataclass
Represents the health information for a component:
- `component_id`: Unique identifier for the component
- `component_name`: Name of the component
- `status`: Current health status
- `last_check`: Timestamp of last check
- `message`: Optional status message
- `metrics`: Additional metrics data

### HealthCheck Interface
Abstract base class for all health checks:
- `component_id`: Unique identifier for the component
- `component_name`: Name of the component
- `run_check()`: Async method to perform the health check

## Built-in Checks

The system provides several built-in checks:
- Memory Check: Monitors memory usage
- CPU Check: Monitors CPU utilization
- Disk Check: Monitors disk space
- Process Check: Monitors process status

## Features

### Core Functionality
- Register and remove health checks
- Run individual or all checks
- Thread-safe concurrent execution
- Async support for both sync and async checks

### Event Integration
- HEALTH_CHECK_STARTED: When a check begins
- HEALTH_CHECK_COMPLETED: When a check completes
- COMPONENT_DEGRADED: When component status changes to degraded
- COMPONENT_FAILED: When component fails

### Logging
- Logs failures, recoveries, and degraded states
- Detailed information about health check results

### Metrics Tracking
- Uptime tracking
- Health score calculation
- Failed checks count
- Degraded components tracking

## API Endpoints

### System-level APIs
- `get_system_health()`: Get overall system health status
- `get_health_summary()`: Get summary of health status counts
- `get_all_component_health()`: Get health information for all components

### Component-level APIs
- `get_component_health(component_id)`: Get health information for specific component
- `run_check(component_id)`: Run a single check
- `run_all_checks()`: Run all registered checks

## Usage Examples

### Basic Usage
```python
from core.health.health_monitor import HealthMonitor
from core.health.built_in_checks import MemoryCheck, CPUCheck

# Create monitor
monitor = HealthMonitor()

# Register built-in checks
monitor.register_check(MemoryCheck("memory_01", "System Memory"))
monitor.register_check(CPUCheck("cpu_01", "CPU Usage"))

# Run all checks
results = asyncio.run(monitor.run_all_checks())

# Get system health
system_health = monitor.get_system_health()
```

### Custom Check
```python
from core.health.health_check import SyncHealthCheck
from core.health.component_health import ComponentHealth
from core.health.health_status import HealthStatus

class CustomCheck(SyncHealthCheck):
    async def run_check(self) -> ComponentHealth:
        # Your custom logic here
        return ComponentHealth(
            component_id="custom_01",
            component_name="Custom Service",
            status=HealthStatus.HEALTHY,
            message="Service is running"
        )
```

## Testing

The system includes comprehensive tests covering:
- Status changes
- Component registration
- Async checks
- Event integration
- Scheduler integration
- Statistics
- Thread safety

## Quality Requirements

- Python 3.12+
- SOLID principles
- Production-ready code
- Full type hints
- Comprehensive documentation