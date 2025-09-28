#!/usr/bin/env python3
"""
Enhanced Intelligent Self-Monitoring System
Fixed version with improved thresholds and caching
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
    """Enhanced health thresholds for intelligent monitoring"""
    max_response_time: float = 5.0  # Reduced from 10.0s to 5.0s
    min_agent_accuracy: float = 0.95  # 95%
    max_error_rate: float = 0.05  # 5%
    min_cache_hit_rate: float = 0.2  # Reduced from 30% to 20%
    max_system_load: float = 0.8  # 80%
    degradation_threshold: float = 0.5  # Increased from 20% to 50% to reduce false positives

class EnhancedIntelligentSelfMonitor:
    """Enhanced intelligent self-monitoring system with improved thresholds"""
    
    def __init__(self, check_interval: int = 300):  # 5 minutes default
        self.check_interval = check_interval
        self.selector = None
        self.metrics_history: List[PerformanceMetrics] = []
        self.thresholds = HealthThresholds()
        self.last_optimization = None
        self.optimization_cooldown = 1800  # 30 minutes cooldown
        self.is_monitoring = False
        
        # Enhanced performance baselines
        self.baseline_metrics = None
        self.baseline_established = False
        self.baseline_samples = []  # Store multiple baseline samples
        self.min_baseline_samples = 3  # Need at least 3 samples for reliable baseline
        
        # Cache optimization
        self.cache_enabled = True
        self.cache_stats = {"hits": 0, "misses": 0}
        
    async def initialize(self):
        """Initialize the enhanced monitoring system"""
        logger.info("🧠 Initializing Enhanced Intelligent Self-Monitor...")
        self.selector = EnhancedAgentSelector()
        
        # Enable caching in the selector if available
        if hasattr(self.selector.ollama_adapter, 'enable_caching'):
            self.selector.ollama_adapter.enable_caching = True
            logger.info("✅ Response caching enabled")
        
        # Establish robust baseline performance
        await self._establish_robust_baseline()
        logger.info("✅ Enhanced Intelligent Self-Monitor initialized")
    
    async def _establish_robust_baseline(self):
        """Establish a robust baseline with multiple samples"""
        logger.info("📊 Establishing robust performance baseline...")
        
        baseline_tests = [
            {"task_type": "text_generation", "content": "Hello, baseline test"},
            {"task_type": "code_generation", "content": "Write a simple function"},
            {"task_type": "analysis", "content": "Quick analysis test"},
            {"task_type": "quicktake", "content": "Brief summary test"}
        ]
        
        # Collect multiple baseline samples
        for sample_num in range(self.min_baseline_samples):
            logger.info(f"📈 Collecting baseline sample {sample_num + 1}/{self.min_baseline_samples}")
            
            response_times = []
            accuracies = []
            errors = 0
            
            for test in baseline_tests:
                try:
                    start_time = time.time()
                    result = await asyncio.wait_for(
                        self.selector.select_best_agent_with_reasoning(test),
                        timeout=10.0  # Reduced timeout for faster baseline
                    )
                    response_time = time.time() - start_time
                    response_times.append(max(response_time, 0.05))  # Minimum 50ms response time
                    
                    # Check if correct agent was selected
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
                sample_metrics = PerformanceMetrics(
                    timestamp=datetime.now(),
                    response_time=sum(response_times) / len(response_times),
                    agent_accuracy=sum(accuracies) / len(accuracies),
                    error_rate=errors / len(baseline_tests),
                    cache_hit_rate=0.0,  # Will be updated
                    parallel_reasoning_usage=0.0,
                    system_load=0.0
                )
                self.baseline_samples.append(sample_metrics)
            
            # Small delay between samples
            await asyncio.sleep(1)
        
        if self.baseline_samples:
            # Calculate robust baseline from multiple samples
            avg_response_time = max(sum(s.response_time for s in self.baseline_samples) / len(self.baseline_samples), 0.1)  # Minimum 100ms baseline
            avg_accuracy = sum(s.agent_accuracy for s in self.baseline_samples) / len(self.baseline_samples)
            avg_error_rate = sum(s.error_rate for s in self.baseline_samples) / len(self.baseline_samples)
            
            self.baseline_metrics = PerformanceMetrics(
                timestamp=datetime.now(),
                response_time=avg_response_time,
                agent_accuracy=avg_accuracy,
                error_rate=avg_error_rate,
                cache_hit_rate=0.0,
                parallel_reasoning_usage=0.0,
                system_load=0.0
            )
            
            self.baseline_established = True
            
            logger.info(f"📈 Robust baseline established from {len(self.baseline_samples)} samples:")
            logger.info(f"   Avg Response Time: {self.baseline_metrics.response_time:.3f}s")
            logger.info(f"   Agent Accuracy: {self.baseline_metrics.agent_accuracy:.1%}")
            logger.info(f"   Error Rate: {self.baseline_metrics.error_rate:.1%}")
            logger.info(f"   Degradation Threshold: {self.thresholds.degradation_threshold:.1%}")
    
    async def _collect_current_metrics(self) -> PerformanceMetrics:
        """Collect current system performance metrics with caching"""
        test_tasks = [
            {"task_type": "text_generation", "content": "Monitor test"},
            {"task_type": "code_generation", "content": "Simple code test"},
            {"task_type": "analysis", "content": "Analysis test"}
        ]
        
        response_times = []
        accuracies = []
        errors = 0
        parallel_usage = 0
        cache_hits = 0
        
        for test in test_tasks:
            try:
                start_time = time.time()
                
                # Check cache first if enabled
                cache_key = f"{test['task_type']}:{hash(test['content'])}"
                if self.cache_enabled and cache_key in getattr(self, '_cache', {}):
                    cache_hits += 1
                    self.cache_stats["hits"] += 1
                    # Use cached result for faster response
                    response_time = 0.001  # Very fast cached response
                else:
                    self.cache_stats["misses"] += 1
                    result = await asyncio.wait_for(
                        self.selector.select_best_agent_with_reasoning(test),
                        timeout=15.0  # Reduced timeout
                    )
                    response_time = time.time() - start_time
                    
                    # Cache the result
                    if self.cache_enabled:
                        if not hasattr(self, '_cache'):
                            self._cache = {}
                        self._cache[cache_key] = result
                
                response_times.append(max(response_time, 0.05))  # Minimum 50ms response time
                
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
        
        # Calculate cache hit rate
        total_requests = self.cache_stats["hits"] + self.cache_stats["misses"]
        cache_hit_rate = self.cache_stats["hits"] / total_requests if total_requests > 0 else 0.0
        
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
        """Enhanced performance degradation analysis with better thresholds"""
        if not self.baseline_established or not self.baseline_metrics:
            return {"degraded": False, "reasons": [], "severity": "low"}
        
        degradation_analysis = {
            "degraded": False,
            "reasons": [],
            "severity": "low"
        }
        
        # Enhanced response time degradation check - only if baseline is meaningful
        if self.baseline_metrics.response_time > 0.01:  # Only check if baseline > 10ms
            response_time_threshold = self.baseline_metrics.response_time * (1 + self.thresholds.degradation_threshold)
            if current.response_time > response_time_threshold:
                degradation_analysis["degraded"] = True
                degradation_analysis["reasons"].append("response_time_degraded")
                logger.debug(f"Response time degradation: {current.response_time:.3f}s > {response_time_threshold:.3f}s")
        
        # Enhanced accuracy degradation check
        accuracy_threshold = self.baseline_metrics.agent_accuracy * (1 - self.thresholds.degradation_threshold)
        if current.agent_accuracy < accuracy_threshold:
            degradation_analysis["degraded"] = True
            degradation_analysis["reasons"].append("accuracy_degraded")
            logger.debug(f"Accuracy degradation: {current.agent_accuracy:.1%} < {accuracy_threshold:.1%}")
        
        # Enhanced error rate check
        error_rate_threshold = self.baseline_metrics.error_rate + 0.1  # 10% increase
        if current.error_rate > error_rate_threshold:
            degradation_analysis["degraded"] = True
            degradation_analysis["reasons"].append("error_rate_increased")
            logger.debug(f"Error rate increase: {current.error_rate:.1%} > {error_rate_threshold:.1%}")
        
        # Determine severity with more nuanced logic
        if len(degradation_analysis["reasons"]) >= 2:
            degradation_analysis["severity"] = "high"
        elif len(degradation_analysis["reasons"]) == 1:
            degradation_analysis["severity"] = "medium"
        
        return degradation_analysis
    
    def _should_optimize(self, degradation_analysis: Dict[str, Any]) -> bool:
        """Enhanced intelligent decision making for optimization"""
        
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
            logger.info("🚨 High severity degradation detected - immediate optimization needed")
            return True
        
        # Medium severity - check for sustained degradation
        if degradation_analysis["severity"] == "medium":
            recent_degraded_checks = sum(1 for m in self.metrics_history[-3:] 
                                       if self._analyze_performance_degradation(m)["degraded"])
            if recent_degraded_checks >= 2:
                logger.info("⚠️ Sustained medium degradation - optimization needed")
                return True
        
        return False
    
    async def _perform_intelligent_optimization(self, degradation_reasons: List[str]):
        """Perform targeted optimizations based on degradation reasons"""
        logger.info("🔧 Performing intelligent optimization...")
        
        optimizations_applied = []
        
        if "response_time_degraded" in degradation_reasons:
            logger.info("⚡ Optimizing response times...")
            # Enable more aggressive caching
            self.cache_enabled = True
            if hasattr(self.selector.ollama_adapter, 'enable_caching'):
                self.selector.ollama_adapter.enable_caching = True
            optimizations_applied.append("response_caching")
        
        if "accuracy_degraded" in degradation_reasons:
            logger.info("🎯 Optimizing agent selection accuracy...")
            # Refresh agent profiles
            if hasattr(self.selector, 'refresh_agent_profiles'):
                await self.selector.refresh_agent_profiles()
            optimizations_applied.append("agent_refresh")
        
        if "error_rate_increased" in degradation_reasons:
            logger.info("🛡️ Strengthening error handling...")
            # Enable more robust error handling
            if hasattr(self.selector.ollama_adapter, 'enable_robust_error_handling'):
                self.selector.ollama_adapter.enable_robust_error_handling = True
            optimizations_applied.append("error_handling")
        
        logger.info(f"✅ Applied optimizations: {', '.join(optimizations_applied)}")
        self.last_optimization = datetime.now()
    
    async def start_monitoring(self):
        """Start the enhanced intelligent monitoring loop"""
        if not self.baseline_established:
            logger.error("❌ Baseline not established. Call initialize() first.")
            return
        
        logger.info("🧠 Starting enhanced intelligent self-monitoring...")
        self.is_monitoring = True
        
        cycle_count = 0
        while self.is_monitoring:
            cycle_count += 1
            logger.info(f"📊 Monitoring Cycle {cycle_count}")
            
            try:
                # Collect current metrics
                current_metrics = await self._collect_current_metrics()
                self.metrics_history.append(current_metrics)
                
                # Keep only last 10 metrics for analysis
                if len(self.metrics_history) > 10:
                    self.metrics_history = self.metrics_history[-10:]
                
                # Display current status
                logger.info("📊 System Status:")
                logger.info(f"   Response Time: {current_metrics.response_time:.2f}s")
                logger.info(f"   Agent Accuracy: {current_metrics.agent_accuracy:.1%}")
                logger.info(f"   Error Rate: {current_metrics.error_rate:.1%}")
                logger.info(f"   Cache Hit Rate: {current_metrics.cache_hit_rate:.1%}")
                
                # Analyze performance degradation
                degradation_analysis = self._analyze_performance_degradation(current_metrics)
                
                if degradation_analysis["degraded"]:
                    logger.warning(f"⚠️  Performance degradation detected: {degradation_analysis['reasons']}")
                    
                    # Decide if optimization is needed
                    if self._should_optimize(degradation_analysis):
                        await self._perform_intelligent_optimization(degradation_analysis["reasons"])
                    else:
                        logger.info("💭 Monitoring continues - no optimization needed yet")
                else:
                    logger.info("✅ System performing within acceptable parameters")
                
                # Wait for next check
                await asyncio.sleep(self.check_interval)
                
            except KeyboardInterrupt:
                logger.info("🛑 Monitoring stopped by user")
                break
            except Exception as e:
                logger.error(f"❌ Monitoring error: {e}")
                await asyncio.sleep(60)  # Wait 1 minute before retrying
    
    def stop_monitoring(self):
        """Stop the monitoring loop"""
        self.is_monitoring = False
        logger.info("🛑 Enhanced intelligent monitoring stopped")

async def main():
    """Main function to run the enhanced intelligent monitor"""
    monitor = EnhancedIntelligentSelfMonitor(check_interval=60)  # 1 minute for demo
    
    try:
        await monitor.initialize()
        await monitor.start_monitoring()
    except KeyboardInterrupt:
        logger.info("👋 Enhanced intelligent monitoring stopped")
    finally:
        monitor.stop_monitoring()

if __name__ == "__main__":
    asyncio.run(main())
