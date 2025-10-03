import asyncio
import time
import psutil
import os
from datetime import datetime

class PerformanceMonitor:
    def __init__(self):
        self.process = psutil.Process(os.getpid())
        self.metrics = []
    
    async def collect_metrics(self):
        """Collect system performance metrics"""
        while True:
            try:
                # CPU usage
                cpu_percent = self.process.cpu_percent()
                
                # Memory usage
                memory_info = self.process.memory_info()
                memory_mb = memory_info.rss / 1024 / 1024
                
                # System metrics
                system_cpu = psutil.cpu_percent(interval=1)
                system_memory = psutil.virtual_memory()
                
                metric = {
                    'timestamp': datetime.now().isoformat(),
                    'process_cpu': cpu_percent,
                    'process_memory_mb': memory_mb,
                    'system_cpu': system_cpu,
                    'system_memory_percent': system_memory.percent,
                    'system_memory_available_gb': system_memory.available / 1024 / 1024 / 1024
                }
                
                self.metrics.append(metric)
                
                # Keep only last 100 metrics
                if len(self.metrics) > 100:
                    self.metrics = self.metrics[-100:]
                
                print(f'📊 Performance: CPU {cpu_percent:.1f}%, Memory {memory_mb:.1f}MB')
                
                await asyncio.sleep(10)  # Collect every 10 seconds
                
            except Exception as e:
                print(f'❌ Performance monitoring error: {e}')
                await asyncio.sleep(10)

# Usage example
async def main():
    monitor = PerformanceMonitor()
    await monitor.collect_metrics()

if __name__ == '__main__':
    asyncio.run(main())
