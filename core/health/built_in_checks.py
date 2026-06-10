"""
Built-in Health Checks for UAGIP Health Monitoring System.
"""

import asyncio
import psutil
import os
from typing import Dict, Any
from datetime import datetime

from core.health.health_check import SyncHealthCheck
from core.health.component_health import ComponentHealth
from core.health.health_status import HealthStatus


class MemoryCheck(SyncHealthCheck):
    """
    Health check for system memory usage.
    """
    
    def __init__(self, component_id: str = "memory", component_name: str = "System Memory"):
        """
        Initialize the memory check.
        
        Args:
            component_id (str): Unique identifier for this component
            component_name (str): Name of the component
        """
        super().__init__(component_id, component_name)
    
    async def run_check(self) -> ComponentHealth:
        """
        Run the memory health check.
        
        Returns:
            ComponentHealth: The health status of system memory
        """
        try:
            # Get memory information
            memory = psutil.virtual_memory()
            
            # Define thresholds (in percentage)
            healthy_threshold = 80.0
            degraded_threshold = 90.0
            
            # Calculate usage percentage
            usage_percent = memory.percent
            
            # Determine status based on usage
            if usage_percent < healthy_threshold:
                status = HealthStatus.HEALTHY
                message = f"Memory usage: {usage_percent:.1f}%"
            elif usage_percent < degraded_threshold:
                status = HealthStatus.DEGRADED
                message = f"Memory usage: {usage_percent:.1f}% (degraded)"
            else:
                status = HealthStatus.UNHEALTHY
                message = f"Memory usage: {usage_percent:.1f}% (unhealthy)"
            
            # Create metrics
            metrics = {
                "total_memory": memory.total,
                "available_memory": memory.available,
                "used_memory": memory.used,
                "memory_percent": usage_percent
            }
            
            return ComponentHealth(
                component_id=self.component_id,
                component_name=self.component_name,
                status=status,
                message=message,
                metrics=metrics
            )
            
        except Exception as e:
            return ComponentHealth(
                component_id=self.component_id,
                component_name=self.component_name,
                status=HealthStatus.UNHEALTHY,
                message=f"Error checking memory: {str(e)}"
            )


class CpuCheck(SyncHealthCheck):
    """
    Health check for CPU usage.
    """
    
    def __init__(self, component_id: str = "cpu", component_name: str = "CPU Usage"):
        """
        Initialize the CPU check.
        
        Args:
            component_id (str): Unique identifier for this component
            component_name (str): Name of the component
        """
        super().__init__(component_id, component_name)
    
    async def run_check(self) -> ComponentHealth:
        """
        Run the CPU health check.
        
        Returns:
            ComponentHealth: The health status of CPU usage
        """
        try:
            # Get CPU information
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Define thresholds
            healthy_threshold = 70.0
            degraded_threshold = 85.0
            
            # Determine status based on usage
            if cpu_percent < healthy_threshold:
                status = HealthStatus.HEALTHY
                message = f"CPU usage: {cpu_percent:.1f}%"
            elif cpu_percent < degraded_threshold:
                status = HealthStatus.DEGRADED
                message = f"CPU usage: {cpu_percent:.1f}% (degraded)"
            else:
                status = HealthStatus.UNHEALTHY
                message = f"CPU usage: {cpu_percent:.1f}% (unhealthy)"
            
            # Create metrics
            metrics = {
                "cpu_percent": cpu_percent,
                "cpu_count": psutil.cpu_count()
            }
            
            return ComponentHealth(
                component_id=self.component_id,
                component_name=self.component_name,
                status=status,
                message=message,
                metrics=metrics
            )
            
        except Exception as e:
            return ComponentHealth(
                component_id=self.component_id,
                component_name=self.component_name,
                status=HealthStatus.UNHEALTHY,
                message=f"Error checking CPU: {str(e)}"
            )


class DiskCheck(SyncHealthCheck):
    """
    Health check for disk usage.
    """
    
    def __init__(self, component_id: str = "disk", component_name: str = "Disk Usage"):
        """
        Initialize the disk check.
        
        Args:
            component_id (str): Unique identifier for this component
            component_name (str): Name of the component
        """
        super().__init__(component_id, component_name)
    
    async def run_check(self) -> ComponentHealth:
        """
        Run the disk health check.
        
        Returns:
            ComponentHealth: The health status of disk usage
        """
        try:
            # Get disk information
            disk = psutil.disk_usage('/')
            
            # Calculate usage percentage
            usage_percent = (disk.used / disk.total) * 100
            
            # Define thresholds
            healthy_threshold = 80.0
            degraded_threshold = 90.0
            
            # Determine status based on usage
            if usage_percent < healthy_threshold:
                status = HealthStatus.HEALTHY
                message = f"Disk usage: {usage_percent:.1f}%"
            elif usage_percent < degraded_threshold:
                status = HealthStatus.DEGRADED
                message = f"Disk usage: {usage_percent:.1f}% (degraded)"
            else:
                status = HealthStatus.UNHEALTHY
                message = f"Disk usage: {usage_percent:.1f}% (unhealthy)"
            
            # Create metrics
            metrics = {
                "total_disk": disk.total,
                "used_disk": disk.used,
                "free_disk": disk.free,
                "disk_percent": usage_percent
            }
            
            return ComponentHealth(
                component_id=self.component_id,
                component_name=self.component_name,
                status=status,
                message=message,
                metrics=metrics
            )
            
        except Exception as e:
            return ComponentHealth(
                component_id=self.component_id,
                component_name=self.component_name,
                status=HealthStatus.UNHEALTHY,
                message=f"Error checking disk: {str(e)}"
            )


class ProcessCheck(SyncHealthCheck):
    """
    Health check for process monitoring.
    """
    
    def __init__(self, process_name: str, component_id: str = None, component_name: str = None):
        """
        Initialize the process check.
        
        Args:
            process_name (str): Name of the process to monitor
            component_id (str): Unique identifier for this component
            component_name (str): Name of the component
        """
        if component_id is None:
            component_id = f"process_{process_name}"
        if component_name is None:
            component_name = f"Process: {process_name}"
            
        super().__init__(component_id, component_name)
        self.process_name = process_name
    
    async def run_check(self) -> ComponentHealth:
        """
        Run the process health check.
        
        Returns:
            ComponentHealth: The health status of the process
        """
        try:
            # Find processes with matching name
            matching_processes = []
            for proc in psutil.process_iter(['pid', 'name']):
                if self.process_name.lower() in proc.info['name'].lower():
                    matching_processes.append(proc)
            
            # Determine status based on number of processes
            if len(matching_processes) > 0:
                status = HealthStatus.HEALTHY
                message = f"Process '{self.process_name}' found ({len(matching_processes)} instances)"
                
                # Get memory usage for the first process
                try:
                    first_process = matching_processes[0]
                    mem_info = first_process.memory_info()
                    metrics = {
                        "process_count": len(matching_processes),
                        "memory_rss": mem_info.rss,
                        "memory_percent": first_process.memory_percent()
                    }
                except Exception:
                    metrics = {"process_count": len(matching_processes)}
            else:
                status = HealthStatus.UNHEALTHY
                message = f"Process '{self.process_name}' not found"
                metrics = {"process_count": 0}
            
            return ComponentHealth(
                component_id=self.component_id,
                component_name=self.component_name,
                status=status,
                message=message,
                metrics=metrics
            )
            
        except Exception as e:
            return ComponentHealth(
                component_id=self.component_id,
                component_name=self.component_name,
                status=HealthStatus.UNHEALTHY,
                message=f"Error checking process: {str(e)}"
            )


class CustomCheck(SyncHealthCheck):
    """
    Custom health check that allows users to define their own check logic.
    """
    
    def __init__(self, check_function, component_id: str, component_name: str):
        """
        Initialize the custom check.
        
        Args:
            check_function (callable): Function that performs the check and returns ComponentHealth
            component_id (str): Unique identifier for this component
            component_name (str): Name of the component
        """
        super().__init__(component_id, component_name)
        self.check_function = check_function
    
    async def run_check(self) -> ComponentHealth:
        """
        Run the custom health check.
        
        Returns:
            ComponentHealth: The result of the custom check
        """
        try:
            # Execute the custom check function
            result = self.check_function()
            
            # If it returns a ComponentHealth object, return it directly
            if isinstance(result, ComponentHealth):
                return result
            else:
                # Otherwise assume it's a status and create ComponentHealth
                return ComponentHealth(
                    component_id=self.component_id,
                    component_name=self.component_name,
                    status=result,
                    message="Custom check completed"
                )
        except Exception as e:
            return ComponentHealth(
                component_id=self.component_id,
                component_name=self.component_name,
                status=HealthStatus.UNHEALTHY,
                message=f"Error in custom check: {str(e)}"
            )