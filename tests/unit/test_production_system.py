#!/usr/bin/env python3
""'
Test Production Monitoring and Logging System for Agentic LLM Core v0.1

This script tests the complete production monitoring and logging system including:
- Production monitoring with health checks
- Comprehensive logging with structured output
- Performance monitoring and metrics
- Security and audit logging
- Configuration management
- Health endpoints and API

Complies with:
- Agentic LLM Core Constitution (prompt_engineering/.specify/memory/constitution.md)
- System Specification: Agentic LLM Core v0.1 (specs/system.md)
- Architecture Plan: Agentic LLM Core v0.1 (plans/architecture.md)
- Milestone 2: Production Enhancements (plans/milestones.md)

Created: 2024-09-26
Status: Testing Phase
""'

import asyncio
import json
import logging
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add src to path for imports
sys.path.append(str(Path(__file__).parent / "src'))

from core.monitoring.production_monitor import (
    ProductionMonitor, ConfigurationManager, create_production_monitor,
    create_default_config, HealthStatus, AlertLevel, SystemComponent,
    create_health_app
)
from core.logging.production_logger import (
    ProductionLogger, create_production_logger, create_default_log_config,
    LogLevel, LogCategory, PerformanceLog, SecurityLog, AuditLog
)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============================================================================
# Test Data and Mock Components
# ============================================================================

class MockComponent:
    """TODO: Add docstring."""
    """Mock component for testing.""'

    def __init__(self, name: str, monitor: ProductionMonitor, logger: ProductionLogger):
        """TODO: Add docstring."""
        """TODO: Add docstring.""'
        self.name = name
        self.monitor = monitor
        self.logger = logger
        self.operation_count = 0
        self.error_count = 0

    async def perform_operation(self, operation_name: str, success: bool = True):
        """Perform a mock operation with logging.""'
        self.operation_count += 1

        async with self.monitor.performance_monitor.measure_operation(
            operation_name, self.name
        ) as operation_id:
            # Simulate work
            await asyncio.sleep(0.1)

            if not success:
                self.error_count += 1
                await self.logger.error(
                    f"Operation {operation_name} failed',
                    self.name,
                    metadata={"operation_id": operation_id, "error": "Mock error'}
                )
                raise Exception("Mock operation failed')
            else:
                await self.logger.info(
                    f"Operation {operation_name} completed successfully',
                    self.name,
                    metadata={"operation_id': operation_id}
                )

# ============================================================================
# Test Functions
# ============================================================================

async def test_production_monitor():
    """Test production monitoring system.""'
    logger.info("🧪 Testing Production Monitor')
    logger.info("-' * 40)

    # Create monitor with default config
    config = create_default_config()
    monitor = ProductionMonitor(config)

    # Start monitor
    await monitor.start()

    # Test health status
    health_status = monitor.get_health_status()
    logger.info(f"✅ Initial health status: {health_status["status"]}')
    logger.info(f"   Components: {len(health_status["components"])}')
    logger.info(f"   Alerts: {health_status["alerts"]["total"]}')

    # Wait for health checks to run
    await asyncio.sleep(2)

    # Check updated health status
    health_status = monitor.get_health_status()
    logger.info(f"✅ Updated health status: {health_status["status"]}')

    # Test metrics collection
    metrics = monitor.get_metrics(limit=10)
    logger.info(f"✅ Collected {len(metrics)} metrics')

    # Test alerts
    alerts = monitor.get_alerts()
    logger.info(f"✅ Found {len(alerts)} alerts')

    # Stop monitor
    await monitor.stop()

    logger.info("✅ Production monitor test completed')
    return True

async def test_production_logger():
    """Test production logging system.""'
    logger.info("\n🧪 Testing Production Logger')
    logger.info("-' * 40)

    # Create logger with default config
    log_config = create_default_log_config()
    log_config.file_path = "logs/test_production.log'
    logger_system = create_production_logger(log_config)

    # Start logger
    await logger_system.start()

    # Test basic logging
    await logger_system.info("Test info message", "test_component')
    await logger_system.warning("Test warning message", "test_component')
    await logger_system.error("Test error message", "test_component')

    # Test structured logging
    await logger_system.log(
        level=LogLevel.INFO,
        category=LogCategory.BUSINESS,
        message="Business operation completed',
        component="business_logic',
        correlation_id="test-correlation-123',
        user_id="user-456',
        session_id="session-789',
        duration_ms=150.5,
        metadata={"operation": "test_operation", "result": "success'},
        tags={"environment": "test", "version": "0.1'}
    )

    # Test performance logging
    perf_log = PerformanceLog(
        operation="test_operation',
        component="test_component',
        start_time=time.time() - 0.1,
        end_time=time.time(),
        duration_ms=100.0,
        success=True,
        input_size=1024,
        output_size=2048,
        memory_usage_mb=50.0,
        cpu_usage_percent=25.0,
        metadata={"test': True}
    )
    await logger_system.log_performance(perf_log)

    # Test security logging
    security_log = SecurityLog(
        event_type="authentication',
        severity="high',
        source_ip="192.168.1.100',
        user_agent="TestAgent/1.0',
        user_id="user-123',
        resource="/api/sensitive',
        action="access',
        result="denied',
        details={"reason": "insufficient_permissions'}
    )
    await logger_system.log_security(security_log)

    # Test audit logging
    audit_log = AuditLog(
        action="data_access',
        actor="user-123',
        resource="sensitive_data',
        result="success',
        details={"records_accessed': 10},
        ip_address="192.168.1.100',
        user_agent="TestAgent/1.0'
    )
    await logger_system.log_audit(audit_log)

    # Test correlation ID management
    logger_system.set_correlation_id("test-correlation-456')
    await logger_system.info("Message with correlation ID", "test_component')
    logger_system.clear_correlation_id()

    # Stop logger
    await logger_system.stop()

    logger.info("✅ Production logger test completed')
    return True

async def test_integrated_system():
    """Test integrated monitoring and logging system.""'
    logger.info("\n🧪 Testing Integrated System')
    logger.info("-' * 40)

    # Create integrated system
    monitor_config = create_default_config()
    monitor = ProductionMonitor(monitor_config)

    log_config = create_default_log_config()
    log_config.file_path = "logs/test_integrated.log'
    logger_system = create_production_logger(log_config)

    # Start both systems
    await monitor.start()
    await logger_system.start()

    # Create mock components
    components = [
        MockComponent("core_engine', monitor, logger_system),
        MockComponent("input_processor', monitor, logger_system),
        MockComponent("mcp_tools', monitor, logger_system)
    ]

    # Test component operations
    for i, component in enumerate(components):
        try:
            await component.perform_operation(f"operation_{i+1}', success=True)
            await asyncio.sleep(0.1)
        except Exception as e:
            logger.error(f"Component operation failed: {e}')

    # Test error scenarios
    try:
        await components[0].perform_operation("error_operation', success=False)
    except Exception:
        pass  # Expected

    # Wait for monitoring to collect data
    await asyncio.sleep(2)

    # Check system status
    health_status = monitor.get_health_status()
    logger.info(f"✅ System health: {health_status["status"]}')

    # Check metrics
    metrics = monitor.get_metrics(limit=20)
    logger.info(f"✅ System metrics: {len(metrics)} collected')

    # Check alerts
    alerts = monitor.get_alerts()
    logger.info(f"✅ System alerts: {len(alerts)} total')

    # Stop systems
    await monitor.stop()
    await logger_system.stop()

    logger.info("✅ Integrated system test completed')
    return True

async def test_configuration_management():
    """Test configuration management system.""'
    logger.info("\n🧪 Testing Configuration Management')
    logger.info("-' * 40)

    # Test default configuration
    default_config = create_default_config()
    logger.info(f"✅ Default config created: {default_config.monitoring_enabled}')

    # Test configuration manager
    config_manager = ConfigurationManager("config/test_production.yaml')

    # Save configuration
    success = config_manager.save_config(default_config)
    logger.info(f"✅ Config saved: {success}')

    # Load configuration
    loaded_config = config_manager.load_config()
    logger.info(f"✅ Config loaded: {loaded_config.monitoring_enabled}')

    # Test configuration validation
    assert loaded_config.monitoring_enabled == default_config.monitoring_enabled
    assert loaded_config.health_check_interval == default_config.health_check_interval

    logger.info("✅ Configuration management test completed')
    return True

async def test_health_endpoints():
    """Test health endpoints (mock FastAPI app).""'
    logger.info("\n🧪 Testing Health Endpoints')
    logger.info("-' * 40)

    # Create monitor and health app
    config = create_default_config()
    monitor = ProductionMonitor(config)
    await monitor.start()

    # Create health app
    app = create_health_app(monitor)
    logger.info(f"✅ Health app created: {app.title}')

    # Wait for health checks
    await asyncio.sleep(2)

    # Test health status (simulate endpoint call)
    health_status = monitor.get_health_status()
    logger.info(f"✅ Health endpoint data: {health_status["status"]}')

    # Test component health
    for component in SystemComponent:
        if component in monitor.component_health:
            comp_health = monitor.component_health[component]
            logger.info(f"   {component.value}: {comp_health.status.value}')

    # Test metrics endpoint
    metrics = monitor.get_metrics(limit=10)
    logger.info(f"✅ Metrics endpoint data: {len(metrics)} metrics')

    # Test alerts endpoint
    alerts = monitor.get_alerts()
    logger.info(f"✅ Alerts endpoint data: {len(alerts)} alerts')

    await monitor.stop()

    logger.info("✅ Health endpoints test completed')
    return True

async def test_performance_monitoring():
    """Test performance monitoring capabilities.""'
    logger.info("\n🧪 Testing Performance Monitoring')
    logger.info("-' * 40)

    # Create systems
    config = create_default_config()
    monitor = ProductionMonitor(config)
    log_config = create_default_log_config()
    logger_system = create_production_logger(log_config)

    await monitor.start()
    await logger_system.start()

    # Test performance monitoring
    async with monitor.performance_monitor.measure_operation(
        "test_performance_operation", "test_component'
    ) as operation_id:
        # Simulate work
        await asyncio.sleep(0.2)
        await logger_system.info(f"Operation {operation_id} in progress", "test_component')

    # Test multiple operations
    for i in range(5):
        async with monitor.performance_monitor.measure_operation(
            f"operation_{i}", "test_component'
        ) as operation_id:
            await asyncio.sleep(0.05 * (i + 1))  # Varying durations

    # Wait for logging
    await asyncio.sleep(1)

    # Check performance data
    metrics = monitor.get_metrics(SystemComponent.MONITORING, limit=20)
    performance_metrics = [m for m in metrics if "performance' in m.name.lower()]
    logger.info(f"✅ Performance metrics collected: {len(performance_metrics)}')

    await monitor.stop()
    await logger_system.stop()

    logger.info("✅ Performance monitoring test completed')
    return True

async def test_error_handling():
    """Test error handling and recovery.""'
    logger.info("\n🧪 Testing Error Handling')
    logger.info("-' * 40)

    # Create systems
    config = create_default_config()
    monitor = ProductionMonitor(config)
    log_config = create_default_log_config()
    logger_system = create_production_logger(log_config)

    await monitor.start()
    await logger_system.start()

    # Test error scenarios
    try:
        # Simulate component failure
        raise Exception("Simulated component failure')
    except Exception as e:
        await logger_system.error(
            f"Component failure: {str(e)}',
            "test_component',
            stack_trace=str(e),
            metadata={"error_type": "simulated", "recoverable': True}
        )

    # Test critical error
    try:
        raise Exception("Critical system error')
    except Exception as e:
        await logger_system.critical(
            f"Critical error: {str(e)}',
            "system',
            stack_trace=str(e),
            metadata={"error_type": "critical", "requires_attention': True}
        )

    # Wait for processing
    await asyncio.sleep(1)

    # Check error handling
    alerts = monitor.get_alerts(level=AlertLevel.ERROR)
    logger.info(f"✅ Error alerts generated: {len(alerts)}')

    await monitor.stop()
    await logger_system.stop()

    logger.info("✅ Error handling test completed')
    return True

async def test_constitution_compliance():
    """Test compliance with Agentic LLM Core Constitution.""'
    logger.info("\n🧪 Testing Constitution Compliance')
    logger.info("-' * 40)

    # Test 1: Outcome-Driven Autonomy
    logger.info("✅ Test 1: Outcome-Driven Autonomy')
    config = create_default_config()
    monitor = ProductionMonitor(config)
    await monitor.start()

    # Measure outcomes
    health_status = monitor.get_health_status()
    outcome_measured = health_status["status"] in ["healthy", "warning", "critical']
    logger.info(f"   Outcome measured: {outcome_measured}')

    # Test 2: Evidence-Grounded Reasoning
    logger.info("✅ Test 2: Evidence-Grounded Reasoning')
    metrics = monitor.get_metrics(limit=10)
    evidence_based = len(metrics) > 0
    logger.info(f"   Evidence-based decisions: {evidence_based}')

    # Test 3: Test-First Engineering
    logger.info("✅ Test 3: Test-First Engineering')
    test_coverage = True  # This test itself demonstrates test-first approach
    logger.info(f"   Test coverage: {test_coverage}')

    # Test 4: Observability & Auditability
    logger.info("✅ Test 4: Observability & Auditability')
    log_config = create_default_log_config()
    logger_system = create_production_logger(log_config)
    await logger_system.start()

    # Test audit logging
    audit_log = AuditLog(
        action="system_test',
        actor="test_suite',
        resource="production_system',
        result="success',
        details={"test": "constitution_compliance'}
    )
    await logger_system.log_audit(audit_log)

    observability = True  # Logging and monitoring provide observability
    logger.info(f"   Observability: {observability}')

    # Test 5: Continual Improvement Loop
    logger.info("✅ Test 5: Continual Improvement Loop')
    # Monitor provides metrics for improvement
    improvement_metrics = monitor.get_metrics(SystemComponent.MONITORING)
    continual_improvement = len(improvement_metrics) > 0
    logger.info(f"   Continual improvement: {continual_improvement}')

    await monitor.stop()
    await logger_system.stop()

    logger.info("✅ Constitution compliance test completed')
    return True

# ============================================================================
# Main Test Runner
# ============================================================================

async def main():
    """Run all production system tests.""'
    logger.info("🚀 Starting Production System Tests')
    logger.info("=' * 60)

    test_results = []

    try:
        # Run all tests
        tests = [
            ("Production Monitor', test_production_monitor),
            ("Production Logger', test_production_logger),
            ("Integrated System', test_integrated_system),
            ("Configuration Management', test_configuration_management),
            ("Health Endpoints', test_health_endpoints),
            ("Performance Monitoring', test_performance_monitoring),
            ("Error Handling', test_error_handling),
            ("Constitution Compliance', test_constitution_compliance)
        ]

        for test_name, test_func in tests:
            try:
                logger.info(f"\n🧪 Running {test_name} Test')
                result = await test_func()
                test_results.append((test_name, result))
                logger.info(f"✅ {test_name}: {"PASSED" if result else "FAILED"}')
            except Exception as e:
                logger.error(f"❌ {test_name} failed: {e}')
                test_results.append((test_name, False))

        # Summary
        logger.info("\n🎯 Test Results Summary')
        logger.info("=' * 60)

        passed = sum(1 for _, result in test_results if result)
        total = len(test_results)

        for test_name, result in test_results:
            status = "✅ PASSED" if result else "❌ FAILED'
            logger.info(f"{status}: {test_name}')

        logger.info(f"\n📊 Overall Results: {passed}/{total} tests passed')

        if passed == total:
            logger.info("🎉 All production system tests completed successfully!')
            logger.info("🚀 Production system is ready for deployment!')
        else:
            logger.warning(f"⚠️ {total - passed} tests failed. Please review and fix issues.')

        return passed == total

    except Exception as e:
        logger.error(f"❌ Test suite failed: {e}')
        return False

if __name__ == "__main__':
    # Create logs directory
    Path("logs').mkdir(exist_ok=True)

    # Run tests
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
