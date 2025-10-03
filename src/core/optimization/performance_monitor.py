#!/usr/bin/env python3
"""
Performance Monitoring System
Comprehensive performance tracking and optimization for the entire system
"""

import asyncio
import logging
import time
import psutil
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import json
import threading
from collections import defaultdict, deque

logger = logging.getLogger(__name__)

@dataclass
class PerformanceMetric:
    """Performance metric data point"""
    timestamp: datetime
    metric_name: str
    value: float
    unit: str
    tags: Dict[str, str]
    metadata: Dict[str, Any]

@dataclass
class SystemHealth:
    """System health status"""
    overall_score: float
    cpu_usage: float
    memory_usage: float
    disk_usage: float
    network_latency: float
    database_connections: int
    cache_hit_ratio: float
    error_rate: float
    response_time_p95: float
    timestamp: datetime
    alerts: List[str]

@dataclass
class PerformanceAlert:
    """Performance alert"""
    alert_id: str
    severity: str  # low, medium, high, critical
    metric_name: str
    threshold: float
    current_value: float
    message: str
    timestamp: datetime
    resolved: bool = False

class PerformanceMonitor:
    """Comprehensive performance monitoring system"""
    
    def __init__(self, alert_thresholds: Optional[Dict[str, float]] = None):
        self.metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.alerts: List[PerformanceAlert] = []
        self.health_history: deque = deque(maxlen=100)
        
        # Default alert thresholds
        self.thresholds = alert_thresholds or {
            'cpu_usage': 80.0,
            'memory_usage': 85.0,
            'disk_usage': 90.0,
            'response_time_ms': 5000.0,
            'error_rate': 0.05,
            'cache_hit_ratio': 0.7,
            'database_connections': 50
        }
        
        self._monitoring = False
        self._monitor_task: Optional[asyncio.Task] = None
        self._lock = asyncio.Lock()
        
        # Performance tracking
        self.request_times: deque = deque(maxlen=1000)
        self.error_counts: Dict[str, int] = defaultdict(int)
        self.success_counts: Dict[str, int] = defaultdict(int)
    
    async def start_monitoring(self, interval: float = 30.0):
        """Start continuous performance monitoring"""
        if self._monitoring:
            return
        
        self._monitoring = True
        self._monitor_task = asyncio.create_task(self._monitoring_loop(interval))
        logger.info(f"✅ Performance monitoring started (interval: {interval}s)")
    
    async def stop_monitoring(self):
        """Stop performance monitoring"""
        self._monitoring = False
        if self._monitor_task:
            self._monitor_task.cancel()
            try:
                await self._monitor_task
            except asyncio.CancelledError:
                pass
        logger.info("✅ Performance monitoring stopped")
    
    async def _monitoring_loop(self, interval: float):
        """Main monitoring loop"""
        while self._monitoring:
            try:
                await self._collect_system_metrics()
                await self._check_alerts()
                await self._update_health_score()
                await asyncio.sleep(interval)
            except Exception as e:
                logger.error(f"Monitoring loop error: {e}")
                await asyncio.sleep(interval)
    
    async def _collect_system_metrics(self):
        """Collect system performance metrics"""
        timestamp = datetime.now()
        
        # CPU usage
        cpu_percent = psutil.cpu_percent(interval=1)
        await self._record_metric('cpu_usage', cpu_percent, '%', timestamp)
        
        # Memory usage
        memory = psutil.virtual_memory()
        await self._record_metric('memory_usage', memory.percent, '%', timestamp)
        
        # Disk usage
        disk = psutil.disk_usage('/')
        disk_percent = (disk.used / disk.total) * 100
        await self._record_metric('disk_usage', disk_percent, '%', timestamp)
        
        # Network latency (simplified)
        network_latency = await self._measure_network_latency()
        await self._record_metric('network_latency', network_latency, 'ms', timestamp)
        
        # Database connections (estimated)
        db_connections = await self._count_database_connections()
        await self._record_metric('database_connections', db_connections, 'count', timestamp)
        
        # Cache hit ratio
        cache_hit_ratio = await self._get_cache_hit_ratio()
        await self._record_metric('cache_hit_ratio', cache_hit_ratio, 'ratio', timestamp)
        
        # Response time (P95)
        response_time_p95 = self._calculate_response_time_p95()
        await self._record_metric('response_time_p95', response_time_p95, 'ms', timestamp)
        
        # Error rate
        error_rate = self._calculate_error_rate()
        await self._record_metric('error_rate', error_rate, 'ratio', timestamp)
    
    async def _record_metric(
        self,
        name: str,
        value: float,
        unit: str,
        timestamp: datetime,
        tags: Optional[Dict[str, str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Record a performance metric"""
        metric = PerformanceMetric(
            timestamp=timestamp,
            metric_name=name,
            value=value,
            unit=unit,
            tags=tags or {},
            metadata=metadata or {}
        )
        
        async with self._lock:
            self.metrics[name].append(metric)
    
    async def _measure_network_latency(self) -> float:
        """Measure network latency (simplified)"""
        try:
            start_time = time.time()
            # Simulate network check
            await asyncio.sleep(0.001)  # Minimal delay
            return (time.time() - start_time) * 1000
        except Exception:
            return 0.0
    
    async def _count_database_connections(self) -> int:
        """Count active database connections"""
        try:
            # This would be implemented based on your database setup
            # For now, return a simulated value
            return 5
        except Exception:
            return 0
    
    async def _get_cache_hit_ratio(self) -> float:
        """Get current cache hit ratio"""
        try:
            # This would integrate with your cache system
            # For now, return a simulated value
            return 0.85
        except Exception:
            return 0.0
    
    def _calculate_response_time_p95(self) -> float:
        """Calculate 95th percentile response time"""
        if not self.request_times:
            return 0.0
        
        sorted_times = sorted(self.request_times)
        p95_index = int(len(sorted_times) * 0.95)
        return sorted_times[p95_index] if p95_index < len(sorted_times) else sorted_times[-1]
    
    def _calculate_error_rate(self) -> float:
        """Calculate current error rate"""
        total_requests = sum(self.success_counts.values()) + sum(self.error_counts.values())
        if total_requests == 0:
            return 0.0
        
        total_errors = sum(self.error_counts.values())
        return total_errors / total_requests
    
    async def _check_alerts(self):
        """Check for performance alerts"""
        current_alerts = []
        
        for metric_name, threshold in self.thresholds.items():
            if metric_name not in self.metrics or not self.metrics[metric_name]:
                continue
            
            latest_metric = self.metrics[metric_name][-1]
            current_value = latest_metric.value
            
            # Check if threshold is exceeded
            if current_value > threshold:
                alert = PerformanceAlert(
                    alert_id=f"{metric_name}_{int(time.time())}",
                    severity=self._determine_severity(metric_name, current_value, threshold),
                    metric_name=metric_name,
                    threshold=threshold,
                    current_value=current_value,
                    message=f"{metric_name} exceeded threshold: {current_value:.2f} > {threshold:.2f}",
                    timestamp=datetime.now()
                )
                current_alerts.append(alert)
        
        # Add new alerts
        async with self._lock:
            for alert in current_alerts:
                if not any(a.alert_id == alert.alert_id for a in self.alerts):
                    self.alerts.append(alert)
                    logger.warning(f"🚨 Performance Alert: {alert.message}")
    
    def _determine_severity(self, metric_name: str, current_value: float, threshold: float) -> str:
        """Determine alert severity based on how much threshold is exceeded"""
        excess_ratio = current_value / threshold
        
        if excess_ratio >= 2.0:
            return "critical"
        elif excess_ratio >= 1.5:
            return "high"
        elif excess_ratio >= 1.2:
            return "medium"
        else:
            return "low"
    
    async def _update_health_score(self):
        """Update overall system health score"""
        try:
            # Get latest metrics
            latest_metrics = {}
            for metric_name in self.metrics:
                if self.metrics[metric_name]:
                    latest_metrics[metric_name] = self.metrics[metric_name][-1].value
            
            # Calculate health score (0-100)
            health_score = 100.0
            
            # CPU penalty
            cpu_usage = latest_metrics.get('cpu_usage', 0)
            if cpu_usage > 80:
                health_score -= (cpu_usage - 80) * 2
            
            # Memory penalty
            memory_usage = latest_metrics.get('memory_usage', 0)
            if memory_usage > 85:
                health_score -= (memory_usage - 85) * 2
            
            # Response time penalty
            response_time = latest_metrics.get('response_time_p95', 0)
            if response_time > 2000:  # 2 seconds
                health_score -= min(20, (response_time - 2000) / 100)
            
            # Error rate penalty
            error_rate = latest_metrics.get('error_rate', 0)
            if error_rate > 0.01:  # 1%
                health_score -= error_rate * 1000
            
            # Cache hit ratio bonus
            cache_hit_ratio = latest_metrics.get('cache_hit_ratio', 0)
            if cache_hit_ratio > 0.8:
                health_score += min(5, (cache_hit_ratio - 0.8) * 25)
            
            health_score = max(0, min(100, health_score))
            
            # Create health status
            health = SystemHealth(
                overall_score=health_score,
                cpu_usage=cpu_usage,
                memory_usage=memory_usage,
                disk_usage=latest_metrics.get('disk_usage', 0),
                network_latency=latest_metrics.get('network_latency', 0),
                database_connections=latest_metrics.get('database_connections', 0),
                cache_hit_ratio=cache_hit_ratio,
                error_rate=error_rate,
                response_time_p95=response_time,
                timestamp=datetime.now(),
                alerts=[alert.message for alert in self.alerts[-5:]]  # Last 5 alerts
            )
            
            async with self._lock:
                self.health_history.append(health)
            
        except Exception as e:
            logger.error(f"Failed to update health score: {e}")
    
    def record_request_time(self, duration_ms: float):
        """Record request duration"""
        self.request_times.append(duration_ms)
    
    def record_success(self, operation: str):
        """Record successful operation"""
        self.success_counts[operation] += 1
    
    def record_error(self, operation: str):
        """Record failed operation"""
        self.error_counts[operation] += 1
    
    async def get_current_health(self) -> SystemHealth:
        """Get current system health"""
        async with self._lock:
            if self.health_history:
                return self.health_history[-1]
            else:
                # Return default health if no data
                return SystemHealth(
                    overall_score=50.0,
                    cpu_usage=0.0,
                    memory_usage=0.0,
                    disk_usage=0.0,
                    network_latency=0.0,
                    database_connections=0,
                    cache_hit_ratio=0.0,
                    error_rate=0.0,
                    response_time_p95=0.0,
                    timestamp=datetime.now(),
                    alerts=[]
                )
    
    async def get_performance_summary(self) -> Dict[str, Any]:
        """Get comprehensive performance summary"""
        async with self._lock:
            summary = {
                'current_health': asdict(await self.get_current_health()),
                'active_alerts': len([a for a in self.alerts if not a.resolved]),
                'total_alerts': len(self.alerts),
                'metrics_tracked': len(self.metrics),
                'monitoring_active': self._monitoring,
                'thresholds': self.thresholds
            }
            
            # Add metric summaries
            metric_summaries = {}
            for metric_name, metric_deque in self.metrics.items():
                if metric_deque:
                    values = [m.value for m in metric_deque]
                    metric_summaries[metric_name] = {
                        'count': len(values),
                        'min': min(values),
                        'max': max(values),
                        'avg': sum(values) / len(values),
                        'latest': values[-1],
                        'unit': metric_deque[-1].unit
                    }
            
            summary['metric_summaries'] = metric_summaries
            return summary
    
    async def get_alerts(self, severity: Optional[str] = None, unresolved_only: bool = True) -> List[PerformanceAlert]:
        """Get performance alerts"""
        async with self._lock:
            alerts = self.alerts.copy()
        
        if unresolved_only:
            alerts = [a for a in alerts if not a.resolved]
        
        if severity:
            alerts = [a for a in alerts if a.severity == severity]
        
        return sorted(alerts, key=lambda a: a.timestamp, reverse=True)
    
    async def resolve_alert(self, alert_id: str) -> bool:
        """Resolve a performance alert"""
        async with self._lock:
            for alert in self.alerts:
                if alert.alert_id == alert_id:
                    alert.resolved = True
                    logger.info(f"✅ Resolved alert: {alert.message}")
                    return True
        return False
    
    async def update_threshold(self, metric_name: str, threshold: float):
        """Update alert threshold for a metric"""
        self.thresholds[metric_name] = threshold
        logger.info(f"Updated threshold for {metric_name}: {threshold}")

def performance_timer(operation_name: str):
    """Decorator to time function execution"""
    def decorator(func: Callable):
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                duration_ms = (time.time() - start_time) * 1000
                
                # Record performance
                monitor = get_performance_monitor()
                monitor.record_request_time(duration_ms)
                monitor.record_success(operation_name)
                
                return result
            except Exception as e:
                duration_ms = (time.time() - start_time) * 1000
                
                # Record error
                monitor = get_performance_monitor()
                monitor.record_request_time(duration_ms)
                monitor.record_error(operation_name)
                
                raise
        
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                duration_ms = (time.time() - start_time) * 1000
                
                # Record performance
                monitor = get_performance_monitor()
                monitor.record_request_time(duration_ms)
                monitor.record_success(operation_name)
                
                return result
            except Exception as e:
                duration_ms = (time.time() - start_time) * 1000
                
                # Record error
                monitor = get_performance_monitor()
                monitor.record_request_time(duration_ms)
                monitor.record_error(operation_name)
                
                raise
        
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator

# Global instance
_global_monitor: Optional[PerformanceMonitor] = None

def get_performance_monitor() -> PerformanceMonitor:
    """Get global performance monitor instance"""
    global _global_monitor
    if _global_monitor is None:
        _global_monitor = PerformanceMonitor()
    return _global_monitor

async def initialize_performance_monitoring(interval: float = 30.0) -> PerformanceMonitor:
    """Initialize global performance monitoring"""
    global _global_monitor
    _global_monitor = PerformanceMonitor()
    await _global_monitor.start_monitoring(interval)
    return _global_monitor

if __name__ == "__main__":
    # Test the performance monitoring system
    async def test_monitoring():
        monitor = await initialize_performance_monitoring(interval=5.0)
        
        # Simulate some activity
        monitor.record_request_time(100.0)
        monitor.record_success("test_operation")
        monitor.record_request_time(2000.0)  # Slow request
        monitor.record_error("test_operation")
        
        # Wait for monitoring cycle
        await asyncio.sleep(6)
        
        # Get health status
        health = await monitor.get_current_health()
        print(f"System Health Score: {health.overall_score:.1f}")
        
        # Get performance summary
        summary = await monitor.get_performance_summary()
        print(f"Performance Summary: {json.dumps(summary, indent=2, default=str)}")
        
        # Get alerts
        alerts = await monitor.get_alerts()
        print(f"Active Alerts: {len(alerts)}")
        
        await monitor.stop_monitoring()
    
    asyncio.run(test_monitoring())
