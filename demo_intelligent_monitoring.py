#!/usr/bin/env python3
"""
Intelligent Self-Monitoring Demonstration
Shows how the system intelligently monitors and decides when to optimize
"""

import asyncio
import logging
import sys
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from intelligent_self_monitor import IntelligentSelfMonitor

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def demonstrate_intelligent_monitoring():
    """Demonstrate the intelligent monitoring system"""
    
    print("🧠 INTELLIGENT SELF-MONITORING DEMONSTRATION")
    print("=" * 60)
    print("💡 This demonstrates how the system:")
    print("   📊 Monitors performance intelligently")
    print("   🧠 Decides when optimization is needed")
    print("   ⚡ Only acts when degradation is detected")
    print("   ⏰ Respects cooldown periods")
    print("=" * 60)
    
    # Create monitor with short intervals for demo
    monitor = IntelligentSelfMonitor(check_interval=10)  # 10 seconds for demo
    
    await monitor.initialize()
    
    print("\n🔍 Running 3 monitoring cycles to demonstrate intelligence...")
    
    # Run 3 monitoring cycles
    for cycle in range(1, 4):
        print(f"\n📊 Monitoring Cycle {cycle}:")
        print("-" * 30)
        
        await monitor.monitor_cycle()
        
        if cycle < 3:
            print(f"⏰ Waiting 10 seconds before next cycle...")
            await asyncio.sleep(10)
    
    print("\n🎯 DEMONSTRATION COMPLETE")
    print("=" * 60)
    print("✅ The system demonstrated:")
    print("   📊 Performance monitoring")
    print("   🧠 Intelligent decision making")
    print("   ⚡ Targeted optimization when needed")
    print("   💭 Patience when performance is acceptable")
    
    print(f"\n📈 Monitoring Results:")
    print(f"   Total Metrics Collected: {len(monitor.metrics_history)}")
    print(f"   Baseline Established: {'✅' if monitor.baseline_metrics else '❌'}")
    print(f"   Last Optimization: {monitor.last_optimization or 'None'}")
    
    if monitor.metrics_history:
        latest = monitor.metrics_history[-1]
        print(f"   Latest Response Time: {latest.response_time:.2f}s")
        print(f"   Latest Accuracy: {latest.agent_accuracy:.1%}")
        print(f"   Latest Error Rate: {latest.error_rate:.1%}")
    
    print(f"\n🤖 The system will continue monitoring intelligently!")
    print(f"   It will only optimize when performance degrades")
    print(f"   It respects cooldown periods between optimizations")
    print(f"   It learns from its optimization attempts")

async def simulate_performance_degradation():
    """Simulate performance degradation to trigger optimization"""
    
    print("\n🧪 SIMULATING PERFORMANCE DEGRADATION")
    print("=" * 50)
    print("💡 This will simulate degraded performance to trigger optimization")
    
    monitor = IntelligentSelfMonitor(check_interval=5)
    await monitor.initialize()
    
    # Simulate degradation by modifying the baseline
    if monitor.baseline_metrics:
        # Artificially degrade the baseline to trigger optimization
        monitor.baseline_metrics.response_time = 1.0  # Very fast baseline
        monitor.baseline_metrics.agent_accuracy = 1.0  # Perfect accuracy
        monitor.baseline_metrics.error_rate = 0.0      # No errors
        
        print("📉 Simulated degraded baseline (artificially fast)")
    
    # Run monitoring cycle
    print("\n🔍 Running monitoring cycle with simulated degradation...")
    await monitor.monitor_cycle()
    
    print("\n✅ Degradation simulation complete!")

async def main():
    """Run the demonstration"""
    try:
        # Run normal demonstration
        await demonstrate_intelligent_monitoring()
        
        # Ask if user wants to see degradation simulation
        print(f"\n❓ Would you like to see how the system handles performance degradation?")
        print(f"   (This will simulate degraded performance to trigger optimization)")
        
        # For demo purposes, run the degradation simulation
        await simulate_performance_degradation()
        
    except Exception as e:
        logger.error(f"❌ Demonstration failed: {e}")
        print(f"❌ Demonstration failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())
