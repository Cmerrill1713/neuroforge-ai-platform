#!/usr/bin/env python3
"""
Intelligent Self-Monitoring System
Monitors system performance and intelligently decides when to self-improve
"""

import asyncio
import logging
import sys
import time
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from enhanced_agent_selection import EnhancedAgentSelector

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class PerformanceMetrics:
    """Performance metrics for monitoring"""
    timestamp: datetime
    response_time: float
    agent_accuracy: float
    error_rate: float
    cache_hit_rate: float
    parallel_reasoning_usage: float
    system_load: float

@dataclass
class HealthThresholds:
    """Health thresholds for intelligent monitoring"""
    max_response_time: float = 10.0  # seconds
    min_agent_accuracy: float = 0.95  # 95%
    max_error_rate: float = 0.05  # 5%
    min_cache_hit_rate: float = 0.3  # 30%
    max_system_load: float = 0.8  # 80%

class IntelligentSelfMonitor:
    """Intelligent self-monitoring system that decides when to optimize"""
    
    def __init__(self, check_interval: int = 300):  # 5 minutes default
        self.check_interval = check_interval
        self.selector = None
        self.metrics_history: List[PerformanceMetrics] = []
        self.thresholds = HealthThresholds()
        self.last_optimization = None
        self.optimization_cooldown = 1800  # 30 minutes cooldown
        self.is_monitoring = False
        
        # Performance baselines
        self.baseline_metrics = None
        self.degradation_threshold = 0.2  # 20% degradation triggers action
        
    async def initialize(self):
        """Initialize the monitoring system"""
        logger.info("🧠 Initializing Intelligent Self-Monitor...")
        self.selector = EnhancedAgentSelector()
        
        # Establish baseline performance
        await self._establish_baseline()
        logger.info("✅ Intelligent Self-Monitor initialized")
    
    async def _establish_baseline(self):
        """Establish baseline performance metrics"""
        logger.info("📊 Establishing performance baseline...")
        
        baseline_tests = [
            {"task_type": "text_generation", "content": "Hello, baseline test"},
            {"task_type": "code_generation", "content": "Write a simple function"},
            {"task_type": "analysis", "content": "Quick analysis test"},
            {"task_type": "quicktake", "content": "Brief summary test"}
        ]
        
        response_times = []
        accuracies = []
        errors = 0
        
        for test in baseline_tests:
            try:
                start_time = time.time()
                result = await asyncio.wait_for(
                    self.selector.select_best_agent_with_reasoning(test),
                    timeout=15.0
                )
                response_time = time.time() - start_time
                response_times.append(response_time)
                
                # Check if correct agent was selected (simplified)
                expected_agents = {
                    "text_generation": "generalist",
                    "code_generation": "codesmith", 
                    "analysis": "analyst",
                    "quicktake": "quicktake"
                }
                selected_agent = result["selected_agent"]["agent_name"]
                expected_agent = expected_agents.get(test["task_type"])
                if selected_agent == expected_agent:
                    accuracies.append(1.0)
                else:
                    accuracies.append(0.0)
                    
            except Exception as e:
                errors += 1
                logger.warning(f"Baseline test error: {e}")
        
        if response_times and accuracies:
            self.baseline_metrics = PerformanceMetrics(
                timestamp=datetime.now(),
                response_time=sum(response_times) / len(response_times),
                agent_accuracy=sum(accuracies) / len(accuracies),
                error_rate=errors / len(baseline_tests),
                cache_hit_rate=0.0,  # Will be updated
                parallel_reasoning_usage=0.0,  # Will be updated
                system_load=0.0  # Simplified
            )
            
            logger.info(f"📈 Baseline established:")
            logger.info(f"   Avg Response Time: {self.baseline_metrics.response_time:.2f}s")
            logger.info(f"   Agent Accuracy: {self.baseline_metrics.agent_accuracy:.1%}")
            logger.info(f"   Error Rate: {self.baseline_metrics.error_rate:.1%}")
    
    async def _collect_current_metrics(self) -> PerformanceMetrics:
        """Collect current system performance metrics"""
        test_tasks = [
            {"task_type": "text_generation", "content": "Monitor test"},
            {"task_type": "code_generation", "content": "Simple code test"},
            {"task_type": "analysis", "content": "Analysis test"}
        ]
        
        response_times = []
        accuracies = []
        errors = 0
        parallel_usage = 0
        
        for test in test_tasks:
            try:
                start_time = time.time()
                result = await asyncio.wait_for(
                    self.selector.select_best_agent_with_reasoning(test),
                    timeout=20.0
                )
                response_time = time.time() - start_time
                response_times.append(response_time)
                
                # Check accuracy
                expected_agents = {
                    "text_generation": "generalist",
                    "code_generation": "codesmith",
                    "analysis": "analyst"
                }
                selected_agent = result["selected_agent"]["agent_name"]
                expected_agent = expected_agents.get(test["task_type"])
                if selected_agent == expected_agent:
                    accuracies.append(1.0)
                else:
                    accuracies.append(0.0)
                
                # Track parallel reasoning usage
                if result.get("use_parallel_reasoning"):
                    parallel_usage += 1
                    
            except Exception as e:
                errors += 1
                logger.warning(f"Metrics collection error: {e}")
        
        # Calculate cache hit rate (simplified)
        cache_hit_rate = 0.0
        if hasattr(self.selector.ollama_adapter, 'cache_stats'):
            stats = self.selector.ollama_adapter.cache_stats
            total_requests = stats.get("hits", 0) + stats.get("misses", 0)
            if total_requests > 0:
                cache_hit_rate = stats.get("hits", 0) / total_requests
        
        return PerformanceMetrics(
            timestamp=datetime.now(),
            response_time=sum(response_times) / len(response_times) if response_times else 0,
            agent_accuracy=sum(accuracies) / len(accuracies) if accuracies else 0,
            error_rate=errors / len(test_tasks),
            cache_hit_rate=cache_hit_rate,
            parallel_reasoning_usage=parallel_usage / len(test_tasks),
            system_load=0.0  # Simplified
        )
    
    def _analyze_performance_degradation(self, current: PerformanceMetrics) -> Dict[str, Any]:
        """Analyze if performance has degraded significantly"""
        if not self.baseline_metrics:
            return {"degraded": False, "reasons": []}
        
        degradation_analysis = {
            "degraded": False,
            "reasons": [],
            "severity": "low"
        }
        
        # Check response time degradation
        if current.response_time > self.baseline_metrics.response_time * (1 + self.degradation_threshold):
            degradation_analysis["degraded"] = True
            degradation_analysis["reasons"].append("response_time_degraded")
        
        # Check accuracy degradation
        if current.agent_accuracy < self.baseline_metrics.agent_accuracy * (1 - self.degradation_threshold):
            degradation_analysis["degraded"] = True
            degradation_analysis["reasons"].append("accuracy_degraded")
        
        # Check error rate increase
        if current.error_rate > self.baseline_metrics.error_rate + 0.1:  # 10% increase
            degradation_analysis["degraded"] = True
            degradation_analysis["reasons"].append("error_rate_increased")
        
        # Determine severity
        if len(degradation_analysis["reasons"]) >= 2:
            degradation_analysis["severity"] = "high"
        elif len(degradation_analysis["reasons"]) == 1:
            degradation_analysis["severity"] = "medium"
        
        return degradation_analysis
    
    def _should_optimize(self, degradation_analysis: Dict[str, Any]) -> bool:
        """Intelligently decide if optimization is needed"""
        
        # Don't optimize if no degradation
        if not degradation_analysis["degraded"]:
            return False
        
        # Check cooldown period
        if self.last_optimization:
            time_since_last = datetime.now() - self.last_optimization
            if time_since_last.total_seconds() < self.optimization_cooldown:
                logger.info(f"⏰ Optimization cooldown active ({self.optimization_cooldown}s)")
                return False
        
        # High severity degradation - optimize immediately
        if degradation_analysis["severity"] == "high":
            logger.warning("🚨 High severity degradation detected - optimization needed")
            return True
        
        # Medium severity - check if it's been degrading for multiple checks
        if degradation_analysis["severity"] == "medium":
            recent_degraded_checks = sum(
                1 for metrics in self.metrics_history[-3:] 
                if self._analyze_performance_degradation(metrics)["degraded"]
            )
            if recent_degraded_checks >= 2:
                logger.warning("⚠️  Sustained medium degradation - optimization needed")
                return True
        
        return False
    
    async def _perform_intelligent_optimization(self, degradation_analysis: Dict[str, Any]):
        """Perform targeted optimization based on degradation analysis"""
        logger.info("🔧 Performing intelligent optimization...")
        
        optimizations_applied = []
        
        # Response time optimization
        if "response_time_degraded" in degradation_analysis["reasons"]:
            logger.info("⚡ Optimizing response times...")
            # Implement response caching if not already active
            if not hasattr(self.selector.ollama_adapter, 'cache_stats'):
                # Apply caching optimization
                await self._apply_caching_optimization()
                optimizations_applied.append("response_caching")
        
        # Accuracy optimization
        if "accuracy_degraded" in degradation_analysis["reasons"]:
            logger.info("🎯 Optimizing agent selection accuracy...")
            # Re-validate agent selection logic
            await self._validate_agent_selection()
            optimizations_applied.append("agent_selection_validation")
        
        # Error rate optimization
        if "error_rate_increased" in degradation_analysis["reasons"]:
            logger.info("🛡️  Optimizing error handling...")
            # Strengthen error handling
            await self._strengthen_error_handling()
            optimizations_applied.append("error_handling_strengthening")
        
        self.last_optimization = datetime.now()
        
        logger.info(f"✅ Applied optimizations: {', '.join(optimizations_applied)}")
        return optimizations_applied
    
    async def _apply_caching_optimization(self):
        """Apply response caching optimization"""
        # Simple caching implementation
        cache = {}
        cache_stats = {"hits": 0, "misses": 0}
        
        original_method = self.selector.ollama_adapter.generate_response
        
        async def cached_generate_response(model_key, prompt, **kwargs):
            cache_key = f"{model_key}:{hash(prompt)}"
            
            if cache_key in cache:
                cache_stats["hits"] += 1
                return cache[cache_key]
            
            cache_stats["misses"] += 1
            response = await original_method(model_key, prompt, **kwargs)
            
            if len(cache) < 50:  # Limit cache size
                cache[cache_key] = response
            
            return response
        
        self.selector.ollama_adapter.generate_response = cached_generate_response
        self.selector.ollama_adapter.cache_stats = cache_stats
    
    async def _validate_agent_selection(self):
        """Validate and optimize agent selection"""
        # Re-run baseline tests to ensure accuracy
        test_cases = [
            {"task_type": "code_generation", "expected": "codesmith"},
            {"task_type": "analysis", "expected": "analyst"},
            {"task_type": "quicktake", "expected": "quicktake"}
        ]
        
        for test_case in test_cases:
            try:
                result = await self.selector.select_best_agent_with_reasoning({
                    "task_type": test_case["task_type"],
                    "content": f"Test {test_case['task_type']}"
                })
                selected = result["selected_agent"]["agent_name"]
                if selected != test_case["expected"]:
                    logger.warning(f"Agent selection mismatch: {selected} != {test_case['expected']}")
            except Exception as e:
                logger.warning(f"Agent validation error: {e}")
    
    async def _strengthen_error_handling(self):
        """Strengthen error handling mechanisms"""
        # Add additional error handling layers
        original_method = self.selector.ollama_adapter.generate_response
        
        async def robust_generate_response(model_key, prompt, **kwargs):
            try:
                return await original_method(model_key, prompt, **kwargs)
            except Exception as e:
                logger.error(f"Error in {model_key}: {e}")
                # Try fallback
                if model_key != 'primary':
                    try:
                        return await original_method('primary', prompt, **kwargs)
                    except Exception as fallback_error:
                        logger.error(f"Fallback also failed: {fallback_error}")
                        raise e
                raise e
        
        self.selector.ollama_adapter.generate_response = robust_generate_response
    
    async def monitor_cycle(self):
        """Single monitoring cycle"""
        try:
            # Collect current metrics
            current_metrics = await self._collect_current_metrics()
            self.metrics_history.append(current_metrics)
            
            # Keep only last 10 metrics
            if len(self.metrics_history) > 10:
                self.metrics_history = self.metrics_history[-10:]
            
            # Analyze performance degradation
            degradation_analysis = self._analyze_performance_degradation(current_metrics)
            
            # Log current status
            logger.info(f"📊 System Status:")
            logger.info(f"   Response Time: {current_metrics.response_time:.2f}s")
            logger.info(f"   Agent Accuracy: {current_metrics.agent_accuracy:.1%}")
            logger.info(f"   Error Rate: {current_metrics.error_rate:.1%}")
            logger.info(f"   Cache Hit Rate: {current_metrics.cache_hit_rate:.1%}")
            
            if degradation_analysis["degraded"]:
                logger.warning(f"⚠️  Performance degradation detected: {degradation_analysis['reasons']}")
                
                # Decide if optimization is needed
                if self._should_optimize(degradation_analysis):
                    await self._perform_intelligent_optimization(degradation_analysis)
                else:
                    logger.info("💭 Monitoring continues - no optimization needed yet")
            else:
                logger.info("✅ System performing within acceptable parameters")
            
        except Exception as e:
            logger.error(f"❌ Monitoring cycle error: {e}")
    
    async def start_monitoring(self):
        """Start intelligent monitoring"""
        if self.is_monitoring:
            logger.info("🔍 Monitoring already active")
            return
        
        await self.initialize()
        self.is_monitoring = True
        
        logger.info(f"🧠 Starting intelligent self-monitoring (check every {self.check_interval}s)")
        logger.info("💡 System will intelligently decide when to optimize based on performance")
        
        try:
            while self.is_monitoring:
                await self.monitor_cycle()
                await asyncio.sleep(self.check_interval)
        except KeyboardInterrupt:
            logger.info("🛑 Monitoring stopped by user")
            self.is_monitoring = False
        except Exception as e:
            logger.error(f"❌ Monitoring error: {e}")
            self.is_monitoring = False
    
    def stop_monitoring(self):
        """Stop monitoring"""
        self.is_monitoring = False
        logger.info("🛑 Intelligent monitoring stopped")

async def main():
    """Run the intelligent self-monitor"""
    print("🧠 INTELLIGENT SELF-MONITORING SYSTEM")
    print("=" * 50)
    print("💡 This system will:")
    print("   📊 Monitor performance continuously")
    print("   🧠 Intelligently decide when to optimize")
    print("   ⚡ Only act when degradation is detected")
    print("   ⏰ Respect cooldown periods between optimizations")
    print("=" * 50)
    
    monitor = IntelligentSelfMonitor(check_interval=60)  # Check every minute for demo
    
    try:
        await monitor.start_monitoring()
    except KeyboardInterrupt:
        print("\n🛑 Monitoring stopped")
        monitor.stop_monitoring()

if __name__ == "__main__":
    asyncio.run(main())
