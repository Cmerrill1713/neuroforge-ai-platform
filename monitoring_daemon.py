#!/usr/bin/env python3
"""
Intelligent Self-Monitoring Daemon
Runs the intelligent monitor as a background service
"""

import asyncio
import signal
import sys
import os
from pathlib import Path

# Add the project directory to Python path
project_dir = Path(__file__).parent
sys.path.insert(0, str(project_dir))

from intelligent_self_monitor import IntelligentSelfMonitor

class MonitoringDaemon:
    """Daemon for running intelligent self-monitoring"""
    
    def __init__(self, check_interval=300):  # 5 minutes default
        self.monitor = IntelligentSelfMonitor(check_interval=check_interval)
        self.running = False
        
    def signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        print(f"\n🛑 Received signal {signum}, shutting down gracefully...")
        self.running = False
        self.monitor.stop_monitoring()
    
    async def run(self):
        """Run the monitoring daemon"""
        # Set up signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        self.running = True
        
        print("🧠 Starting Intelligent Self-Monitoring Daemon")
        print("=" * 50)
        print("💡 The system will:")
        print("   📊 Monitor performance every 5 minutes")
        print("   🧠 Intelligently decide when to optimize")
        print("   ⚡ Only optimize when degradation is detected")
        print("   ⏰ Respect 30-minute cooldown between optimizations")
        print("=" * 50)
        print("🔄 Monitoring started... (Press Ctrl+C to stop)")
        
        try:
            await self.monitor.start_monitoring()
        except Exception as e:
            print(f"❌ Daemon error: {e}")
        finally:
            print("👋 Intelligent Self-Monitoring Daemon stopped")

def main():
    """Main entry point"""
    # Check if running as daemon
    if len(sys.argv) > 1 and sys.argv[1] == "--daemon":
        # Run as background daemon
        import daemon
        with daemon.DaemonContext():
            asyncio.run(MonitoringDaemon().run())
    else:
        # Run in foreground
        asyncio.run(MonitoringDaemon().run())

if __name__ == "__main__":
    main()
