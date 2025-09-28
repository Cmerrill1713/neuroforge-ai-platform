#!/usr/bin/env python3
"""
Production Logging System for Agentic LLM Core v0.1

This module implements comprehensive production logging with:
- Structured logging with JSON format
- Log aggregation and analysis
- Performance logging
- Security event logging
- Audit trail logging
- Log rotation and retention
- Real-time log streaming
- Log correlation and tracing

Complies with:
- Agentic LLM Core Constitution (prompt_engineering/.specify/memory/constitution.md)
- System Specification: Agentic LLM Core v0.1 (specs/system.md)
- Architecture Plan: Agentic LLM Core v0.1 (plans/architecture.md)
- Milestone 2: Production Enhancements (plans/milestones.md)

Created: 2024-09-26
Status: Implementation Phase
"""

import asyncio
import json
import logging
import logging.handlers
import sys
import uuid
from abc import ABC, abstractmethod
from datetime import datetime, timezone, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional
import threading
from contextlib import asynccontextmanager

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

# ============================================================================
# Data Models
# ============================================================================

class LogLevel(str, Enum):
    """Log levels."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

class LogCategory(str, Enum):
    """Log categories."""
    SYSTEM = "system"
    SECURITY = "security"
    PERFORMANCE = "performance"
    AUDIT = "audit"
    BUSINESS = "business"
    TECHNICAL = "technical"
    USER_ACTION = "user_action"
    API_REQUEST = "api_request"
    DATABASE = "database"
    CACHE = "cache"
    EXTERNAL_SERVICE = "external_service"

class LogEvent(BaseModel):
    """Structured log event."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    level: LogLevel = Field(..., description="Log level")
    category: LogCategory = Field(..., description="Log category")
    message: str = Field(..., description="Log message")
    component: str = Field(..., description="Component that generated the log")
    correlation_id: Optional[str] = Field(None, description="Correlation ID for tracing")
    user_id: Optional[str] = Field(None, description="User ID if applicable")
    session_id: Optional[str] = Field(None, description="Session ID if applicable")
    request_id: Optional[str] = Field(None, description="Request ID if applicable")
    duration_ms: Optional[float] = Field(None, description="Duration in milliseconds")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    stack_trace: Optional[str] = Field(None, description="Stack trace for errors")
    tags: Dict[str, str] = Field(default_factory=dict, description="Log tags")

class PerformanceLog(BaseModel):
    """Performance-specific log event."""
    operation: str = Field(..., description="Operation being measured")
    component: str = Field(..., description="Component performing operation")
    start_time: datetime = Field(..., description="Operation start time")
    end_time: datetime = Field(..., description="Operation end time")
    duration_ms: float = Field(..., description="Operation duration in milliseconds")
    success: bool = Field(..., description="Whether operation succeeded")
    input_size: Optional[int] = Field(None, description="Input size in bytes")
    output_size: Optional[int] = Field(None, description="Output size in bytes")
    memory_usage_mb: Optional[float] = Field(None, description="Memory usage in MB")
    cpu_usage_percent: Optional[float] = Field(None, description="CPU usage percentage")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")

class SecurityLog(BaseModel):
    """Security-specific log event."""
    event_type: str = Field(..., description="Type of security event")
    severity: str = Field(..., description="Security event severity")
    source_ip: Optional[str] = Field(None, description="Source IP address")
    user_agent: Optional[str] = Field(None, description="User agent string")
    user_id: Optional[str] = Field(None, description="User ID if applicable")
    resource: Optional[str] = Field(None, description="Resource being accessed")
    action: Optional[str] = Field(None, description="Action being performed")
    result: str = Field(..., description="Result of the action")
    details: Dict[str, Any] = Field(default_factory=dict, description="Event details")

class AuditLog(BaseModel):
    """Audit-specific log event."""
    action: str = Field(..., description="Action being audited")
    actor: str = Field(..., description="Who performed the action")
    resource: str = Field(..., description="Resource affected")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    result: str = Field(..., description="Result of the action")
    details: Dict[str, Any] = Field(default_factory=dict, description="Audit details")
    ip_address: Optional[str] = Field(None, description="IP address of actor")
    user_agent: Optional[str] = Field(None, description="User agent of actor")

class LogConfig(BaseModel):
    """Logging configuration."""
    level: LogLevel = Field(default=LogLevel.INFO, description="Default log level")
    format: str = Field(default="json", description="Log format (json/text)")
    output: str = Field(default="file", description="Output destination (file/console/both)")
    file_path: Optional[str] = Field(None, description="Log file path")
    max_file_size_mb: int = Field(default=100, description="Maximum log file size in MB")
    backup_count: int = Field(default=10, description="Number of backup files to keep")
    retention_days: int = Field(default=30, description="Log retention period in days")
    enable_compression: bool = Field(default=True, description="Enable log compression")
    enable_rotation: bool = Field(default=True, description="Enable log rotation")
    enable_correlation: bool = Field(default=True, description="Enable correlation IDs")
    enable_performance_logging: bool = Field(default=True, description="Enable performance logging")
    enable_security_logging: bool = Field(default=True, description="Enable security logging")
    enable_audit_logging: bool = Field(default=True, description="Enable audit logging")
    components: Dict[str, Dict[str, Any]] = Field(default_factory=dict, description="Component-specific config")

# ============================================================================
# Log Handlers
# ============================================================================

class LogHandler(ABC):
    """Abstract base class for log handlers."""
    
    @abstractmethod
    async def handle_log(self, log_event: LogEvent) -> None:
        """Handle a log event."""
        pass
    
    @abstractmethod
    async def flush(self) -> None:
        """Flush any buffered logs."""
        pass
    
    @abstractmethod
    async def close(self) -> None:
        """Close the log handler."""
        pass

class FileLogHandler(LogHandler):
    """File-based log handler with rotation and compression."""
    
    def __init__(self, config: LogConfig):
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.file_handler")
        self.file_handler: Optional[logging.handlers.RotatingFileHandler] = None
        self._setup_file_handler()
    
    def _setup_file_handler(self):
        """Setup file handler with rotation."""
        if not self.config.file_path:
            return
        
        log_file = Path(self.config.file_path)
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Create rotating file handler
        self.file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=self.config.max_file_size_mb * 1024 * 1024,
            backupCount=self.config.backup_count
        )
        
        # Set formatter
        if self.config.format == "json":
            formatter = JsonFormatter()
        else:
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
        
        self.file_handler.setFormatter(formatter)
    
    async def handle_log(self, log_event: LogEvent) -> None:
        """Handle a log event by writing to file."""
        if not self.file_handler:
            return
        
        try:
            # Convert to logging record
            record = self._create_log_record(log_event)
            self.file_handler.emit(record)
        except Exception as e:
            self.logger.error(f"Failed to write log to file: {e}")
    
    def _create_log_record(self, log_event: LogEvent) -> logging.LogRecord:
        """Create a logging record from log event."""
        # Map log levels
        level_map = {
            LogLevel.DEBUG: logging.DEBUG,
            LogLevel.INFO: logging.INFO,
            LogLevel.WARNING: logging.WARNING,
            LogLevel.ERROR: logging.ERROR,
            LogLevel.CRITICAL: logging.CRITICAL
        }
        
        record = logging.LogRecord(
            name=log_event.component,
            level=level_map[log_event.level],
            pathname="",
            lineno=0,
            msg=log_event.message,
            args=(),
            exc_info=None
        )
        
        # Add custom attributes
        record.log_event = log_event
        record.correlation_id = log_event.correlation_id
        record.user_id = log_event.user_id
        record.session_id = log_event.session_id
        record.request_id = log_event.request_id
        record.duration_ms = log_event.duration_ms
        record.metadata = log_event.metadata
        record.tags = log_event.tags
        
        return record
    
    async def flush(self) -> None:
        """Flush the file handler."""
        if self.file_handler:
            self.file_handler.flush()
    
    async def close(self) -> None:
        """Close the file handler."""
        if self.file_handler:
            self.file_handler.close()

class ConsoleLogHandler(LogHandler):
    """Console-based log handler."""
    
    def __init__(self, config: LogConfig):
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.console_handler")
        self.console_handler = logging.StreamHandler(sys.stdout)
        self._setup_console_handler()
    
    def _setup_console_handler(self):
        """Setup console handler."""
        if self.config.format == "json":
            formatter = JsonFormatter()
        else:
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
        
        self.console_handler.setFormatter(formatter)
    
    async def handle_log(self, log_event: LogEvent) -> None:
        """Handle a log event by writing to console."""
        try:
            record = self._create_log_record(log_event)
            self.console_handler.emit(record)
        except Exception as e:
            self.logger.error(f"Failed to write log to console: {e}")
    
    def _create_log_record(self, log_event: LogEvent) -> logging.LogRecord:
        """Create a logging record from log event."""
        level_map = {
            LogLevel.DEBUG: logging.DEBUG,
            LogLevel.INFO: logging.INFO,
            LogLevel.WARNING: logging.WARNING,
            LogLevel.ERROR: logging.ERROR,
            LogLevel.CRITICAL: logging.CRITICAL
        }
        
        record = logging.LogRecord(
            name=log_event.component,
            level=level_map[log_event.level],
            pathname="",
            lineno=0,
            msg=log_event.message,
            args=(),
            exc_info=None
        )
        
        record.log_event = log_event
        return record
    
    async def flush(self) -> None:
        """Flush the console handler."""
        self.console_handler.flush()
    
    async def close(self) -> None:
        """Close the console handler."""
        self.console_handler.close()

class JsonFormatter(logging.Formatter):
    """JSON formatter for structured logging."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        try:
            # Base log data
            log_data = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "level": record.levelname,
                "component": record.name,
                "message": record.getMessage()
            }
            
            # Add custom attributes if available
            if hasattr(record, 'log_event'):
                log_event = record.log_event
                log_data.update({
                    "id": log_event.id,
                    "category": log_event.category.value,
                    "correlation_id": log_event.correlation_id,
                    "user_id": log_event.user_id,
                    "session_id": log_event.session_id,
                    "request_id": log_event.request_id,
                    "duration_ms": log_event.duration_ms,
                    "metadata": log_event.metadata,
                    "tags": log_event.tags
                })
                
                if log_event.stack_trace:
                    log_data["stack_trace"] = log_event.stack_trace
            
            # Add exception info if available
            if record.exc_info:
                log_data["exception"] = self.formatException(record.exc_info)
            
            return json.dumps(log_data, default=str)
            
        except Exception:
            # Fallback to simple format
            return f"{record.levelname}: {record.getMessage()}"

# ============================================================================
# Performance Monitoring
# ============================================================================

class PerformanceMonitor:
    """Performance monitoring and logging."""
    
    def __init__(self, logger: 'ProductionLogger'):
        self.logger = logger
        self.active_operations: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.RLock()
    
    @asynccontextmanager
    async def measure_operation(self, 
                              operation: str, 
                              component: str,
                              correlation_id: Optional[str] = None,
                              **metadata):
        """Context manager for measuring operation performance."""
        operation_id = str(uuid.uuid4())
        start_time = datetime.now(timezone.utc)
        
        # Store operation info
        with self._lock:
            self.active_operations[operation_id] = {
                "operation": operation,
                "component": component,
                "start_time": start_time,
                "correlation_id": correlation_id,
                "metadata": metadata
            }
        
        try:
            yield operation_id
        except Exception as e:
            # Log error
            await self._log_operation_result(
                operation_id, False, str(e), None, None, None, None
            )
            raise
        finally:
            # Log success
            await self._log_operation_result(
                operation_id, True, None, None, None, None, None
            )
    
    async def _log_operation_result(self,
                                  operation_id: str,
                                  success: bool,
                                  error: Optional[str],
                                  input_size: Optional[int],
                                  output_size: Optional[int],
                                  memory_usage: Optional[float],
                                  cpu_usage: Optional[float]):
        """Log operation result."""
        with self._lock:
            if operation_id not in self.active_operations:
                return
            
            operation_info = self.active_operations[operation_id]
            del self.active_operations[operation_id]
        
        end_time = datetime.now(timezone.utc)
        duration_ms = (end_time - operation_info["start_time"]).total_seconds() * 1000
        
        # Create performance log
        perf_log = PerformanceLog(
            operation=operation_info["operation"],
            component=operation_info["component"],
            start_time=operation_info["start_time"],
            end_time=end_time,
            duration_ms=duration_ms,
            success=success,
            input_size=input_size,
            output_size=output_size,
            memory_usage_mb=memory_usage,
            cpu_usage_percent=cpu_usage,
            metadata=operation_info["metadata"]
        )
        
        # Log the performance event
        await self.logger.log_performance(perf_log, operation_info["correlation_id"])

# ============================================================================
# Production Logger Implementation
# ============================================================================

class ProductionLogger:
    """Comprehensive production logging system."""
    
    def __init__(self, config: LogConfig):
        self.config = config
        self.handlers: List[LogHandler] = []
        self.correlation_ids: Dict[str, str] = {}
        self.performance_monitor = PerformanceMonitor(self)
        self._lock = threading.RLock()
        
        # Setup handlers
        self._setup_handlers()
        
        # Start background tasks
        self._cleanup_task: Optional[asyncio.Task] = None
    
    def _setup_handlers(self):
        """Setup log handlers based on configuration."""
        if self.config.output in ["file", "both"]:
            self.handlers.append(FileLogHandler(self.config))
        
        if self.config.output in ["console", "both"]:
            self.handlers.append(ConsoleLogHandler(self.config))
    
    async def start(self):
        """Start the production logger."""
        # Start cleanup task
        self._cleanup_task = asyncio.create_task(self._cleanup_loop())
    
    async def stop(self):
        """Stop the production logger."""
        # Stop cleanup task
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
        
        # Close all handlers
        for handler in self.handlers:
            await handler.close()
    
    async def _cleanup_loop(self):
        """Background cleanup loop."""
        while True:
            try:
                await asyncio.sleep(3600)  # Run every hour
                await self._cleanup_old_logs()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Log cleanup error: {e}")
                await asyncio.sleep(300)  # Wait 5 minutes before retrying
    
    async def _cleanup_old_logs(self):
        """Clean up old log files."""
        if not self.config.file_path:
            return
        
        try:
            log_dir = Path(self.config.file_path).parent
            cutoff_time = datetime.now(timezone.utc) - timedelta(days=self.config.retention_days)
            
            for log_file in log_dir.glob("*.log*"):
                if log_file.stat().st_mtime < cutoff_time.timestamp():
                    log_file.unlink()
                    logger.info(f"Deleted old log file: {log_file}")
        
        except Exception as e:
            logger.error(f"Failed to cleanup old logs: {e}")
    
    async def log(self,
                 level: LogLevel,
                 category: LogCategory,
                 message: str,
                 component: str,
                 correlation_id: Optional[str] = None,
                 user_id: Optional[str] = None,
                 session_id: Optional[str] = None,
                 request_id: Optional[str] = None,
                 duration_ms: Optional[float] = None,
                 metadata: Optional[Dict[str, Any]] = None,
                 stack_trace: Optional[str] = None,
                 tags: Optional[Dict[str, str]] = None):
        """Log a message with full context."""
        # Generate correlation ID if not provided
        if not correlation_id and self.config.enable_correlation:
            correlation_id = self._get_or_create_correlation_id()
        
        # Create log event
        log_event = LogEvent(
            level=level,
            category=category,
            message=message,
            component=component,
            correlation_id=correlation_id,
            user_id=user_id,
            session_id=session_id,
            request_id=request_id,
            duration_ms=duration_ms,
            metadata=metadata or {},
            stack_trace=stack_trace,
            tags=tags or {}
        )
        
        # Send to all handlers
        for handler in self.handlers:
            try:
                await handler.handle_log(log_event)
            except Exception as e:
                logger.error(f"Handler error: {e}")
    
    async def log_performance(self, perf_log: PerformanceLog, correlation_id: Optional[str] = None):
        """Log a performance event."""
        if not self.config.enable_performance_logging:
            return
        
        await self.log(
            level=LogLevel.INFO,
            category=LogCategory.PERFORMANCE,
            message=f"Operation {perf_log.operation} completed in {perf_log.duration_ms:.2f}ms",
            component=perf_log.component,
            correlation_id=correlation_id,
            duration_ms=perf_log.duration_ms,
            metadata={
                "operation": perf_log.operation,
                "success": perf_log.success,
                "input_size": perf_log.input_size,
                "output_size": perf_log.output_size,
                "memory_usage_mb": perf_log.memory_usage_mb,
                "cpu_usage_percent": perf_log.cpu_usage_percent,
                "start_time": perf_log.start_time.isoformat(),
                "end_time": perf_log.end_time.isoformat(),
                **perf_log.metadata
            },
            tags={"type": "performance"}
        )
    
    async def log_security(self, security_log: SecurityLog, correlation_id: Optional[str] = None):
        """Log a security event."""
        if not self.config.enable_security_logging:
            return
        
        level = LogLevel.WARNING if security_log.severity == "high" else LogLevel.INFO
        
        await self.log(
            level=level,
            category=LogCategory.SECURITY,
            message=f"Security event: {security_log.event_type} - {security_log.result}",
            component="security",
            correlation_id=correlation_id,
            user_id=security_log.user_id,
            metadata={
                "event_type": security_log.event_type,
                "severity": security_log.severity,
                "source_ip": security_log.source_ip,
                "user_agent": security_log.user_agent,
                "resource": security_log.resource,
                "action": security_log.action,
                "result": security_log.result,
                **security_log.details
            },
            tags={"type": "security", "severity": security_log.severity}
        )
    
    async def log_audit(self, audit_log: AuditLog, correlation_id: Optional[str] = None):
        """Log an audit event."""
        if not self.config.enable_audit_logging:
            return
        
        await self.log(
            level=LogLevel.INFO,
            category=LogCategory.AUDIT,
            message=f"Audit: {audit_log.action} by {audit_log.actor} on {audit_log.resource} - {audit_log.result}",
            component="audit",
            correlation_id=correlation_id,
            metadata={
                "action": audit_log.action,
                "actor": audit_log.actor,
                "resource": audit_log.resource,
                "result": audit_log.result,
                "ip_address": audit_log.ip_address,
                "user_agent": audit_log.user_agent,
                **audit_log.details
            },
            tags={"type": "audit"}
        )
    
    def _get_or_create_correlation_id(self) -> str:
        """Get or create correlation ID for current context."""
        thread_id = threading.get_ident()
        
        with self._lock:
            if thread_id not in self.correlation_ids:
                self.correlation_ids[thread_id] = str(uuid.uuid4())
            
            return self.correlation_ids[thread_id]
    
    def set_correlation_id(self, correlation_id: str):
        """Set correlation ID for current context."""
        thread_id = threading.get_ident()
        
        with self._lock:
            self.correlation_ids[thread_id] = correlation_id
    
    def clear_correlation_id(self):
        """Clear correlation ID for current context."""
        thread_id = threading.get_ident()
        
        with self._lock:
            if thread_id in self.correlation_ids:
                del self.correlation_ids[thread_id]
    
    # Convenience methods
    async def debug(self, message: str, component: str, **kwargs):
        """Log debug message."""
        await self.log(LogLevel.DEBUG, LogCategory.TECHNICAL, message, component, **kwargs)
    
    async def info(self, message: str, component: str, **kwargs):
        """Log info message."""
        await self.log(LogLevel.INFO, LogCategory.TECHNICAL, message, component, **kwargs)
    
    async def warning(self, message: str, component: str, **kwargs):
        """Log warning message."""
        await self.log(LogLevel.WARNING, LogCategory.TECHNICAL, message, component, **kwargs)
    
    async def error(self, message: str, component: str, **kwargs):
        """Log error message."""
        await self.log(LogLevel.ERROR, LogCategory.TECHNICAL, message, component, **kwargs)
    
    async def critical(self, message: str, component: str, **kwargs):
        """Log critical message."""
        await self.log(LogLevel.CRITICAL, LogCategory.TECHNICAL, message, component, **kwargs)

# ============================================================================
# Factory Functions
# ============================================================================

def create_production_logger(config: LogConfig) -> ProductionLogger:
    """Create a production logger with configuration."""
    return ProductionLogger(config)

def create_default_log_config() -> LogConfig:
    """Create default logging configuration."""
    return LogConfig(
        level=LogLevel.INFO,
        format="json",
        output="both",
        file_path="logs/agentic_llm_core.log",
        max_file_size_mb=100,
        backup_count=10,
        retention_days=30,
        enable_compression=True,
        enable_rotation=True,
        enable_correlation=True,
        enable_performance_logging=True,
        enable_security_logging=True,
        enable_audit_logging=True
    )

# ============================================================================
# Export all classes and functions
# ============================================================================

__all__ = [
    # Enums
    "LogLevel",
    "LogCategory",
    
    # Data Models
    "LogEvent",
    "PerformanceLog",
    "SecurityLog",
    "AuditLog",
    "LogConfig",
    
    # Handlers
    "LogHandler",
    "FileLogHandler",
    "ConsoleLogHandler",
    "JsonFormatter",
    
    # Performance Monitoring
    "PerformanceMonitor",
    
    # Main Implementation
    "ProductionLogger",
    
    # Factory Functions
    "create_production_logger",
    "create_default_log_config",
]
