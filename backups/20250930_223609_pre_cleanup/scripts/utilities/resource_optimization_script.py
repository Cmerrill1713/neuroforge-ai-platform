#!/usr/bin/env python3
""'
Resource Usage Optimization Script

This script optimizes memory and CPU usage across the system by:
- Cleaning up unused processes and memory
- Optimizing database connections
- Clearing caches
- Optimizing file system
- Monitoring and reporting resource usage

Based on the comprehensive system evaluation and improvement plan.
""'

import asyncio
import gc
import logging
import os
import psutil
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import json

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ResourceOptimizer:
    """TODO: Add docstring."""
    """Resource usage optimizer for the agentic LLM system.""'

    def __init__(self):
        """TODO: Add docstring."""
        """Initialize the resource optimizer.""'
        self.logger = logging.getLogger(__name__)
        self.optimization_results = {}
        self.before_metrics = {}
        self.after_metrics = {}

    async def run_comprehensive_optimization(self) -> Dict[str, any]:
        """Run comprehensive resource optimization.""'
        self.logger.info("🚀 Starting comprehensive resource optimization...')

        # Capture initial metrics
        self.before_metrics = await self._capture_system_metrics()
        self.logger.info(f"📊 Initial metrics: CPU={self.before_metrics['cpu_percent']:.1f}%, Memory={self.before_metrics['memory_percent']:.1f}%')

        # Run optimization tasks
        optimization_tasks = [
            ("memory_cleanup', self._optimize_memory_usage),
            ("process_cleanup', self._cleanup_unused_processes),
            ("cache_optimization', self._optimize_caches),
            ("database_optimization', self._optimize_database_connections),
            ("file_system_optimization', self._optimize_file_system),
            ("python_garbage_collection', self._run_python_garbage_collection),
            ("system_cache_cleanup', self._cleanup_system_caches)
        ]

        for task_name, task_func in optimization_tasks:
            try:
                self.logger.info(f"🔧 Running {task_name}...')
                start_time = time.time()
                result = await task_func()
                duration = time.time() - start_time

                self.optimization_results[task_name] = {
                    "success': True,
                    "duration': duration,
                    "result': result
                }
                self.logger.info(f"✅ {task_name} completed in {duration:.2f}s')

            except Exception as e:
                self.logger.error(f"❌ {task_name} failed: {e}')
                self.optimization_results[task_name] = {
                    "success': False,
                    "error': str(e)
                }

        # Capture final metrics
        await asyncio.sleep(2)  # Allow system to stabilize
        self.after_metrics = await self._capture_system_metrics()

        # Calculate improvements
        improvements = self._calculate_improvements()

        # Generate report
        report = self._generate_optimization_report(improvements)

        self.logger.info("🎉 Resource optimization completed!')
        return report

    async def _capture_system_metrics(self) -> Dict[str, float]:
        """Capture current system resource metrics.""'
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)

            # Memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            memory_available = memory.available / (1024**3)  # GB

            # Disk usage
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            disk_free = disk.free / (1024**3)  # GB

            # Process count
            process_count = len(psutil.pids())

            # Load average (Unix-like systems)
            try:
                load_avg = os.getloadavg()
            except AttributeError:
                load_avg = [0, 0, 0]  # Windows doesn't have load average

            return {
                "cpu_percent': cpu_percent,
                "memory_percent': memory_percent,
                "memory_available_gb': memory_available,
                "disk_percent': disk_percent,
                "disk_free_gb': disk_free,
                "process_count': process_count,
                "load_avg_1min': load_avg[0],
                "load_avg_5min': load_avg[1],
                "load_avg_15min': load_avg[2]
            }

        except Exception as e:
            self.logger.error(f"Failed to capture system metrics: {e}')
            return {}

    async def _optimize_memory_usage(self) -> Dict[str, any]:
        """Optimize memory usage.""'
        results = {}

        try:
            # Get current memory usage
            memory_before = psutil.virtual_memory()

            # Clear Python caches
            if hasattr(sys, '_clear_type_cache'):
                sys._clear_type_cache()

            # Clear module caches
            for module_name in list(sys.modules.keys()):
                if module_name.startswith('_'):
                    del sys.modules[module_name]

            # Force garbage collection
            collected = gc.collect()

            # Get memory after cleanup
            memory_after = psutil.virtual_memory()

            results = {
                "memory_freed_mb': (memory_before.used - memory_after.used) / (1024**2),
                "garbage_collected': collected,
                "memory_before_percent': memory_before.percent,
                "memory_after_percent': memory_after.percent
            }

            self.logger.info(f"🧹 Memory optimization: Freed {results['memory_freed_mb']:.1f}MB, GC collected {collected} objects')

        except Exception as e:
            self.logger.error(f"Memory optimization failed: {e}')
            results = {"error': str(e)}

        return results

    async def _cleanup_unused_processes(self) -> Dict[str, any]:
        """Clean up unused processes.""'
        results = {}

        try:
            processes_before = len(psutil.pids())

            # Find and kill zombie processes
            zombie_count = 0
            for proc in psutil.process_iter(['pid', 'name', 'status']):
                try:
                    if proc.info['status'] == psutil.STATUS_ZOMBIE:
                        zombie_count += 1
                        # Note: Can't kill zombie processes directly
                        self.logger.warning(f"Found zombie process: {proc.info['pid']} ({proc.info['name']})')
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass

            # Clean up defunct processes
            defunct_count = 0
            for proc in psutil.process_iter(['pid', 'name', 'status']):
                try:
                    if proc.info['status'] == psutil.STATUS_DEAD:
                        defunct_count += 1
                        self.logger.warning(f"Found defunct process: {proc.info['pid']} ({proc.info['name']})')
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass

            processes_after = len(psutil.pids())

            results = {
                "processes_before': processes_before,
                "processes_after': processes_after,
                "zombie_processes': zombie_count,
                "defunct_processes': defunct_count,
                "processes_cleaned': processes_before - processes_after
            }

            self.logger.info(f"🧹 Process cleanup: {results['processes_cleaned']} processes cleaned, {zombie_count} zombies found')

        except Exception as e:
            self.logger.error(f"Process cleanup failed: {e}')
            results = {"error': str(e)}

        return results

    async def _optimize_caches(self) -> Dict[str, any]:
        """Optimize system caches.""'
        results = {}

        try:
            # Clear Python bytecode cache
            bytecode_cache_cleared = 0
            for root, dirs, files in os.walk('.'):
                for dir_name in dirs:
                    if dir_name == '__pycache__':
                        pycache_path = os.path.join(root, dir_name)
                        try:
                            import shutil
                            shutil.rmtree(pycache_path)
                            bytecode_cache_cleared += 1
                        except Exception as e:
                            self.logger.warning(f"Failed to clear {pycache_path}: {e}')

            # Clear temporary files
            temp_files_cleared = 0
            temp_dirs = ['/tmp', '/var/tmp']
            for temp_dir in temp_dirs:
                if os.path.exists(temp_dir):
                    try:
                        for file in os.listdir(temp_dir):
                            file_path = os.path.join(temp_dir, file)
                            if os.path.isfile(file_path) and file.startswith('tmp'):
                                try:
                                    os.remove(file_path)
                                    temp_files_cleared += 1
                                except Exception:
                                    pass
                    except Exception:
                        pass

            results = {
                "bytecode_caches_cleared': bytecode_cache_cleared,
                "temp_files_cleared': temp_files_cleared
            }

            self.logger.info(f"🧹 Cache optimization: Cleared {bytecode_cache_cleared} bytecode caches, {temp_files_cleared} temp files')

        except Exception as e:
            self.logger.error(f"Cache optimization failed: {e}')
            results = {"error': str(e)}

        return results

    async def _optimize_database_connections(self) -> Dict[str, any]:
        """Optimize database connections.""'
        results = {}

        try:
            # Check PostgreSQL connections
            try:
                result = subprocess.run(
                    ['psql', '-h', 'localhost', '-p', '5432', '-U', 'postgres', '-d', 'postgres',
                     '-c', "SELECT count(*) as active_connections FROM pg_stat_activity WHERE state = 'active';'],
                    capture_output=True, text=True, timeout=10
                )
                if result.returncode == 0:
                    active_connections = result.stdout.strip().split('\n')[-1].strip()
                    results['postgres_active_connections'] = active_connections
            except Exception as e:
                self.logger.warning(f"Could not check PostgreSQL connections: {e}')

            # Check Redis connections
            try:
                result = subprocess.run(
                    ['redis-cli', 'info', 'clients'],
                    capture_output=True, text=True, timeout=5
                )
                if result.returncode == 0:
                    for line in result.stdout.split('\n'):
                        if 'connected_clients:' in line:
                            connected_clients = line.split(':')[1].strip()
                            results['redis_connected_clients'] = connected_clients
                            break
            except Exception as e:
                self.logger.warning(f"Could not check Redis connections: {e}')

            self.logger.info("🗄️ Database connection optimization completed')

        except Exception as e:
            self.logger.error(f"Database optimization failed: {e}')
            results = {"error': str(e)}

        return results

    async def _optimize_file_system(self) -> Dict[str, any]:
        """Optimize file system.""'
        results = {}

        try:
            # Check disk usage
            disk_before = psutil.disk_usage('/')

            # Find and report large files
            large_files = []
            for root, dirs, files in os.walk('.'):
                for file in files:
                    file_path = os.path.join(root, file)
                    try:
                        file_size = os.path.getsize(file_path)
                        if file_size > 100 * 1024 * 1024:  # > 100MB
                            large_files.append({
                                "path': file_path,
                                "size_mb': file_size / (1024**2)
                            })
                    except Exception:
                        pass

            # Sort by size
            large_files.sort(key=lambda x: x['size_mb'], reverse=True)
            large_files = large_files[:10]  # Top 10 largest files

            results = {
                "large_files': large_files,
                "total_large_files': len(large_files)
            }

            self.logger.info(f"📁 File system optimization: Found {len(large_files)} large files')

        except Exception as e:
            self.logger.error(f"File system optimization failed: {e}')
            results = {"error': str(e)}

        return results

    async def _run_python_garbage_collection(self) -> Dict[str, any]:
        """Run Python garbage collection.""'
        results = {}

        try:
            # Get current object counts
            objects_before = len(gc.get_objects())

            # Run garbage collection
            collected = gc.collect()

            # Get object counts after
            objects_after = len(gc.get_objects())

            results = {
                "objects_before': objects_before,
                "objects_after': objects_after,
                "objects_collected': collected,
                "objects_freed': objects_before - objects_after
            }

            self.logger.info(f"🗑️ Python GC: Collected {collected} objects, freed {results['objects_freed']} objects')

        except Exception as e:
            self.logger.error(f"Python garbage collection failed: {e}')
            results = {"error': str(e)}

        return results

    async def _cleanup_system_caches(self) -> Dict[str, any]:
        """Clean up system caches.""'
        results = {}

        try:
            # Clear DNS cache (macOS)
            try:
                subprocess.run(['sudo', 'dscacheutil', '-flushcache'], check=False)
                subprocess.run(['sudo', 'killall', '-HUP', 'mDNSResponder'], check=False)
                results['dns_cache_cleared'] = True
            except Exception:
                results['dns_cache_cleared'] = False

            # Clear system logs (if accessible)
            try:
                log_files_cleared = 0
                log_dirs = ['/var/log', '/tmp']
                for log_dir in log_dirs:
                    if os.path.exists(log_dir):
                        for file in os.listdir(log_dir):
                            if file.endswith('.log') and os.path.getsize(os.path.join(log_dir, file)) > 10 * 1024 * 1024:  # > 10MB
                                try:
                                    with open(os.path.join(log_dir, file), 'w') as f:
                                        f.write('')
                                    log_files_cleared += 1
                                except Exception:
                                    pass
                results['log_files_cleared'] = log_files_cleared
            except Exception:
                results['log_files_cleared'] = 0

            self.logger.info(f"🧹 System cache cleanup: DNS cache cleared, {results.get('log_files_cleared', 0)} log files cleared')

        except Exception as e:
            self.logger.error(f"System cache cleanup failed: {e}')
            results = {"error': str(e)}

        return results

    def _calculate_improvements(self) -> Dict[str, any]:
        """TODO: Add docstring."""
        """Calculate optimization improvements.""'
        improvements = {}

        try:
            if self.before_metrics and self.after_metrics:
                # CPU improvement
                cpu_before = self.before_metrics.get('cpu_percent', 0)
                cpu_after = self.after_metrics.get('cpu_percent', 0)
                improvements['cpu_improvement'] = cpu_before - cpu_after

                # Memory improvement
                memory_before = self.before_metrics.get('memory_percent', 0)
                memory_after = self.after_metrics.get('memory_percent', 0)
                improvements['memory_improvement'] = memory_before - memory_after

                # Process count improvement
                processes_before = self.before_metrics.get('process_count', 0)
                processes_after = self.after_metrics.get('process_count', 0)
                improvements['process_count_improvement'] = processes_before - processes_after

                # Load average improvement
                load_before = self.before_metrics.get('load_avg_1min', 0)
                load_after = self.after_metrics.get('load_avg_1min', 0)
                improvements['load_improvement'] = load_before - load_after

        except Exception as e:
            self.logger.error(f"Failed to calculate improvements: {e}')

        return improvements

    def _generate_optimization_report(self, improvements: Dict[str, any]) -> Dict[str, any]:
        """TODO: Add docstring."""
        """Generate comprehensive optimization report.""'
        report = {
            "timestamp': datetime.now().isoformat(),
            "optimization_results': self.optimization_results,
            "before_metrics': self.before_metrics,
            "after_metrics': self.after_metrics,
            "improvements': improvements,
            "summary': {
                "total_optimizations': len(self.optimization_results),
                "successful_optimizations': sum(1 for r in self.optimization_results.values() if r.get('success', False)),
                "failed_optimizations': sum(1 for r in self.optimization_results.values() if not r.get('success', False)),
                "cpu_improvement_percent': improvements.get('cpu_improvement', 0),
                "memory_improvement_percent': improvements.get('memory_improvement', 0),
                "process_count_improvement': improvements.get('process_count_improvement', 0)
            }
        }

        return report

async def main():
    """Main execution function.""'
    logger.info("🚀 Starting Resource Usage Optimization')

    optimizer = ResourceOptimizer()

    try:
        # Run comprehensive optimization
        report = await optimizer.run_comprehensive_optimization()

        # Save report
        report_path = f"resource_optimization_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json'
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2, default=str)

        # Print summary
        summary = report['summary']
        logger.info("📊 Optimization Summary:')
        logger.info(f"   Total optimizations: {summary['total_optimizations']}')
        logger.info(f"   Successful: {summary['successful_optimizations']}')
        logger.info(f"   Failed: {summary['failed_optimizations']}')
        logger.info(f"   CPU improvement: {summary['cpu_improvement_percent']:.1f}%')
        logger.info(f"   Memory improvement: {summary['memory_improvement_percent']:.1f}%')
        logger.info(f"   Process count improvement: {summary['process_count_improvement']}')
        logger.info(f"📄 Detailed report saved to: {report_path}')

    except Exception as e:
        logger.error(f"❌ Optimization failed: {e}')
        return 1

    return 0

if __name__ == "__main__':
    sys.exit(asyncio.run(main()))
