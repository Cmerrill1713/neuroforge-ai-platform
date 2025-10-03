#!/usr/bin/env python3
"""
Production Monitoring System
Comprehensive monitoring and alerting for production deployment
"""

import time
import psutil
import logging
import asyncio
import aiohttp
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from collections import defaultdict, deque
import threading
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

logger = logging.getLogger(__name__)

@dataclass
class SystemMetrics:
    """System performance metrics"""
    timestamp: str
    cpu_percent: float
    memory_percent: float
    disk_percent: float
    network_io: Dict[str, int]
    active_connections: int
    response_time_avg: float
    requests_per_second: float
    error_rate: float
    uptime: float

@dataclass
class Alert:
    """Alert definition"""
    timestamp: str
    severity: str  # critical, warning, info
    service: str
    message: str
    metrics: Dict[str, Any]
    resolved: bool = False

class ProductionMonitor:
    """Production monitoring and alerting system"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.metrics_history = deque(maxlen=1000)  # Keep last 1000 metrics
        self.alerts = []
        self.alert_thresholds = {
            'cpu_percent': 80.0,
            'memory_percent': 85.0,
            'disk_percent': 90.0,
            'response_time_avg': 2000.0,  # 2 seconds
            'error_rate': 5.0,  # 5%
            'requests_per_second': 1000.0
        }
        self.running = False
        self.monitor_thread = None
        
        # Service health endpoints
        self.service_endpoints = {
            'backend': 'http://localhost:8004/health',
            'rag_service': 'http://localhost:8005/health',
            'tts_service': 'http://localhost:8087/health',
            'frontend': 'http://localhost:3000',
            'ollama': 'http://localhost:11434/api/tags'
        }
        
        # Email configuration
        self.email_config = {
            'smtp_server': config.get('SMTP_SERVER', 'smtp.gmail.com'),
            'smtp_port': config.get('SMTP_PORT', 587),
            'username': config.get('EMAIL_USERNAME', ''),
            'password': config.get('EMAIL_PASSWORD', ''),
            'to_emails': config.get_list('ALERT_EMAILS', [])
        }
    
    def start_monitoring(self):
        """Start the monitoring system"""
        if self.running:
            logger.warning("Monitoring already running")
            return
        
        self.running = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        logger.info("Production monitoring started")
    
    def stop_monitoring(self):
        """Stop the monitoring system"""
        self.running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        logger.info("Production monitoring stopped")
    
    def _monitor_loop(self):
        """Main monitoring loop"""
        while self.running:
            try:
                metrics = self._collect_metrics()
                self.metrics_history.append(metrics)
                
                # Check for alerts
                self._check_alerts(metrics)
                
                # Log metrics
                self._log_metrics(metrics)
                
                time.sleep(60)  # Collect metrics every minute
                
            except Exception as e:
                logger.error(f"Monitoring loop error: {e}")
                time.sleep(60)
    
    def _collect_metrics(self) -> SystemMetrics:
        """Collect system and application metrics"""
        # System metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        network = psutil.net_io_counters()
        
        # Application metrics
        response_times = []
        error_count = 0
        request_count = 0
        
        # Check service health
        active_connections = 0
        for service, endpoint in self.service_endpoints.items():
            try:
                start_time = time.time()
                response = asyncio.run(self._check_service_health(endpoint))
                response_time = (time.time() - start_time) * 1000
                response_times.append(response_time)
                
                if response and response.get('status') == 'healthy':
                    active_connections += 1
                else:
                    error_count += 1
                    
                request_count += 1
            except Exception as e:
                logger.error(f"Service health check failed for {service}: {e}")
                error_count += 1
                request_count += 1
        
        # Calculate averages
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        error_rate = (error_count / request_count * 100) if request_count > 0 else 0
        requests_per_second = request_count / 60  # Approximate RPS
        
        return SystemMetrics(
            timestamp=datetime.utcnow().isoformat(),
            cpu_percent=cpu_percent,
            memory_percent=memory.percent,
            disk_percent=disk.percent,
            network_io={
                'bytes_sent': network.bytes_sent,
                'bytes_recv': network.bytes_recv
            },
            active_connections=active_connections,
            response_time_avg=avg_response_time,
            requests_per_second=requests_per_second,
            error_rate=error_rate,
            uptime=time.time() - psutil.boot_time()
        )
    
    async def _check_service_health(self, endpoint: str) -> Optional[Dict[str, Any]]:
        """Check individual service health"""
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=5)) as session:
                async with session.get(endpoint) as response:
                    if response.status == 200:
                        return await response.json()
                    return None
        except Exception:
            return None
    
    def _check_alerts(self, metrics: SystemMetrics):
        """Check metrics against alert thresholds"""
        current_time = datetime.utcnow()
        
        # CPU alert
        if metrics.cpu_percent > self.alert_thresholds['cpu_percent']:
            self._create_alert(
                severity='warning',
                service='system',
                message=f'High CPU usage: {metrics.cpu_percent:.1f}%',
                metrics=asdict(metrics)
            )
        
        # Memory alert
        if metrics.memory_percent > self.alert_thresholds['memory_percent']:
            self._create_alert(
                severity='critical',
                service='system',
                message=f'High memory usage: {metrics.memory_percent:.1f}%',
                metrics=asdict(metrics)
            )
        
        # Disk alert
        if metrics.disk_percent > self.alert_thresholds['disk_percent']:
            self._create_alert(
                severity='critical',
                service='system',
                message=f'High disk usage: {metrics.disk_percent:.1f}%',
                metrics=asdict(metrics)
            )
        
        # Response time alert
        if metrics.response_time_avg > self.alert_thresholds['response_time_avg']:
            self._create_alert(
                severity='warning',
                service='api',
                message=f'Slow response time: {metrics.response_time_avg:.1f}ms',
                metrics=asdict(metrics)
            )
        
        # Error rate alert
        if metrics.error_rate > self.alert_thresholds['error_rate']:
            self._create_alert(
                severity='critical',
                service='api',
                message=f'High error rate: {metrics.error_rate:.1f}%',
                metrics=asdict(metrics)
            )
        
        # Service availability alert
        if metrics.active_connections < len(self.service_endpoints) * 0.8:
            self._create_alert(
                severity='critical',
                service='services',
                message=f'Service availability low: {metrics.active_connections}/{len(self.service_endpoints)}',
                metrics=asdict(metrics)
            )
    
    def _create_alert(self, severity: str, service: str, message: str, metrics: Dict[str, Any]):
        """Create and send alert"""
        alert = Alert(
            timestamp=datetime.utcnow().isoformat(),
            severity=severity,
            service=service,
            message=message,
            metrics=metrics
        )
        
        self.alerts.append(alert)
        
        # Send alert
        self._send_alert(alert)
        
        logger.warning(f"ALERT [{severity.upper()}] {service}: {message}")
    
    def _send_alert(self, alert: Alert):
        """Send alert via email"""
        if not self.email_config['to_emails']:
            return
        
        try:
            msg = MIMEMultipart()
            msg['From'] = self.email_config['username']
            msg['To'] = ', '.join(self.email_config['to_emails'])
            msg['Subject'] = f"[{alert.severity.upper()}] NeuroForge Alert: {alert.service}"
            
            body = f"""
Alert Details:
- Time: {alert.timestamp}
- Severity: {alert.severity}
- Service: {alert.service}
- Message: {alert.message}

Current Metrics:
- CPU: {alert.metrics.get('cpu_percent', 0):.1f}%
- Memory: {alert.metrics.get('memory_percent', 0):.1f}%
- Disk: {alert.metrics.get('disk_percent', 0):.1f}%
- Response Time: {alert.metrics.get('response_time_avg', 0):.1f}ms
- Error Rate: {alert.metrics.get('error_rate', 0):.1f}%

Please investigate immediately.
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            server = smtplib.SMTP(self.email_config['smtp_server'], self.email_config['smtp_port'])
            server.starttls()
            server.login(self.email_config['username'], self.email_config['password'])
            server.send_message(msg)
            server.quit()
            
        except Exception as e:
            logger.error(f"Failed to send alert email: {e}")
    
    def _log_metrics(self, metrics: SystemMetrics):
        """Log metrics for analysis"""
        logger.info(f"METRICS: {json.dumps(asdict(metrics))}")
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get current metrics summary"""
        if not self.metrics_history:
            return {}
        
        latest = self.metrics_history[-1]
        return {
            'current': asdict(latest),
            'history_count': len(self.metrics_history),
            'alerts_count': len([a for a in self.alerts if not a.resolved]),
            'uptime_hours': latest.uptime / 3600
        }
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get overall health status"""
        if not self.metrics_history:
            return {'status': 'unknown', 'message': 'No metrics available'}
        
        latest = self.metrics_history[-1]
        active_alerts = [a for a in self.alerts if not a.resolved]
        
        if any(a.severity == 'critical' for a in active_alerts):
            status = 'critical'
        elif any(a.severity == 'warning' for a in active_alerts):
            status = 'warning'
        elif latest.error_rate > 1.0:
            status = 'degraded'
        else:
            status = 'healthy'
        
        return {
            'status': status,
            'message': f"System {status}",
            'active_alerts': len(active_alerts),
            'last_check': latest.timestamp,
            'services_healthy': f"{latest.active_connections}/{len(self.service_endpoints)}"
        }

# Global monitor instance
monitor = None

def initialize_monitor(config: Dict[str, Any]):
    """Initialize the global monitor"""
    global monitor
    monitor = ProductionMonitor(config)
    monitor.start_monitoring()
    return monitor

def get_monitor() -> Optional[ProductionMonitor]:
    """Get the global monitor instance"""
    return monitor
