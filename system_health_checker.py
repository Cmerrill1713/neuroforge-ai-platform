import asyncio
import requests
import subprocess
import sys
import time
from datetime import datetime

class SystemHealthChecker:
    def __init__(self):
        self.services = [
            (8000, 'Main API'),
            (8002, 'MCP Server'),
            (6379, 'Redis'),
            (8090, 'Weaviate'),
            (9200, 'Elasticsearch'),
            (3002, 'Grafana'),
            (9090, 'Prometheus')
        ]
    
    async def check_service_health(self, port, name):
        """Check health of a specific service"""
        try:
            if port in [6379, 8090, 9200]:  # Non-HTTP services
                return {'name': name, 'status': 'unknown', 'response_time': 0}
            
            start_time = time.time()
            response = requests.get(f'http://localhost:{port}/health', timeout=5)
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                return {'name': name, 'status': 'healthy', 'response_time': response_time}
            else:
                return {'name': name, 'status': 'unhealthy', 'response_time': response_time}
                
        except Exception as e:
            return {'name': name, 'status': 'down', 'response_time': 0, 'error': str(e)}
    
    async def check_system_health(self):
        """Check health of all services"""
        print('🔍 System Health Check')
        print('=' * 40)
        
        health_results = []
        
        for port, name in self.services:
            result = await self.check_service_health(port, name)
            health_results.append(result)
            
            status_icon = '✅' if result['status'] == 'healthy' else '❌'
            print(f'{status_icon} {name}: {result["status"]} ({result["response_time"]:.3f}s)')
        
        # Summary
        healthy_services = sum(1 for r in health_results if r['status'] == 'healthy')
        total_services = len(health_results)
        health_percentage = (healthy_services / total_services) * 100
        
        print(f'\n📊 System Health: {healthy_services}/{total_services} services healthy ({health_percentage:.1f}%)')
        
        if health_percentage >= 80:
            print('🟢 System Status: EXCELLENT')
        elif health_percentage >= 60:
            print('🟡 System Status: GOOD')
        else:
            print('🔴 System Status: NEEDS ATTENTION')
        
        return health_results

# Usage example
async def main():
    checker = SystemHealthChecker()
    await checker.check_system_health()

if __name__ == '__main__':
    asyncio.run(main())
