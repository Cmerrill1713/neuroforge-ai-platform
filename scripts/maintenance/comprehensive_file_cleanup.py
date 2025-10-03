#!/usr/bin/env python3
"""
Comprehensive File System Cleanup System
Automatically manages file deletion and prevents excessive junk accumulation
"""

import os
import shutil
import time
import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import subprocess
import psutil

class ComprehensiveFileCleanup:
    """Comprehensive file system cleanup and management system."""
    
    def __init__(self, project_root: str = "."):
        """Initialize the cleanup system."""
        self.project_root = Path(project_root)
        self.logger = self._setup_logging()
        self.cleanup_config = self._load_cleanup_config()
        self.cleanup_stats = {
            "files_deleted": 0,
            "directories_deleted": 0,
            "space_freed_mb": 0,
            "cleanup_duration": 0,
            "last_cleanup": None
        }
    
    def _setup_logging(self) -> logging.Logger:
        """Setup logging for cleanup operations."""
        logger = logging.getLogger("file_cleanup")
        logger.setLevel(logging.INFO)
        
        # Create logs directory if it doesn't exist
        logs_dir = self.project_root / "logs"
        logs_dir.mkdir(exist_ok=True)
        
        # File handler
        file_handler = logging.FileHandler(logs_dir / "file_cleanup.log")
        file_handler.setLevel(logging.INFO)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
        return logger
    
    def _load_cleanup_config(self) -> Dict[str, Any]:
        """Load cleanup configuration."""
        config_file = self.project_root / "config" / "cleanup_config.json"
        
        # Default configuration
        default_config = {
            "cleanup_schedule": {
                "daily": True,
                "time": "02:00",
                "weekly": True,
                "weekly_day": "sunday"
            },
            "file_retention": {
                "log_files_days": 7,
                "temp_files_hours": 24,
                "cache_files_days": 30,
                "backup_files_days": 14,
                "test_files_hours": 12
            },
            "directories_to_clean": {
                "logs": {
                    "path": "logs",
                    "patterns": ["*.log", "*.log.*"],
                    "recursive": True,
                    "max_age_days": 7
                },
                "temp": {
                    "path": "temp",
                    "patterns": ["*"],
                    "recursive": True,
                    "max_age_hours": 24
                },
                "cache": {
                    "path": "cache",
                    "patterns": ["*.cache", "*.tmp"],
                    "recursive": True,
                    "max_age_days": 30
                },
                "backups": {
                    "path": "backups",
                    "patterns": ["*"],
                    "recursive": True,
                    "max_age_days": 14
                },
                "test_outputs": {
                    "path": ".",
                    "patterns": ["test_*.wav", "test_*.json", "test_*.txt"],
                    "recursive": False,
                    "max_age_hours": 12
                }
            },
            "file_size_limits": {
                "max_log_file_size_mb": 100,
                "max_temp_file_size_mb": 50,
                "max_cache_file_size_mb": 200
            },
            "preserve_patterns": [
                "README.md",
                "*.py",
                "*.js",
                "*.ts",
                "*.tsx",
                "*.json",
                "*.yml",
                "*.yaml",
                "*.sh",
                "*.md",
                "requirements.txt",
                "package.json",
                "Dockerfile*",
                "docker-compose*.yml"
            ],
            "cleanup_actions": {
                "remove_empty_directories": True,
                "compress_old_logs": True,
                "clean_python_cache": True,
                "clean_node_modules_cache": True,
                "clean_docker_cache": True,
                "clean_system_temp": True
            }
        }
        
        # Create config directory if it doesn't exist
        config_file.parent.mkdir(exist_ok=True)
        
        if not config_file.exists():
            config_file.write_text(json.dumps(default_config, indent=2))
            self.logger.info(f"Created default cleanup config: {config_file}")
            return default_config
        
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
            self.logger.info(f"Loaded cleanup config: {config_file}")
            return config
        except Exception as e:
            self.logger.warning(f"Failed to load config, using default: {e}")
            return default_config
    
    def run_comprehensive_cleanup(self) -> Dict[str, Any]:
        """Run comprehensive file system cleanup."""
        start_time = time.time()
        self.logger.info("🧹 Starting comprehensive file cleanup...")
        
        cleanup_results = {
            "success": True,
            "files_deleted": 0,
            "directories_deleted": 0,
            "space_freed_mb": 0,
            "errors": [],
            "cleanup_details": {}
        }
        
        try:
            # 1. Clean directories based on configuration
            for dir_name, dir_config in self.cleanup_config["directories_to_clean"].items():
                result = self._clean_directory(dir_name, dir_config)
                cleanup_results["cleanup_details"][dir_name] = result
                cleanup_results["files_deleted"] += result.get("files_deleted", 0)
                cleanup_results["directories_deleted"] += result.get("directories_deleted", 0)
                cleanup_results["space_freed_mb"] += result.get("space_freed_mb", 0)
            
            # 2. Run additional cleanup actions
            if self.cleanup_config["cleanup_actions"]["clean_python_cache"]:
                result = self._clean_python_cache()
                cleanup_results["cleanup_details"]["python_cache"] = result
                cleanup_results["files_deleted"] += result.get("files_deleted", 0)
                cleanup_results["space_freed_mb"] += result.get("space_freed_mb", 0)
            
            if self.cleanup_config["cleanup_actions"]["clean_node_modules_cache"]:
                result = self._clean_node_modules_cache()
                cleanup_results["cleanup_details"]["node_cache"] = result
                cleanup_results["space_freed_mb"] += result.get("space_freed_mb", 0)
            
            if self.cleanup_config["cleanup_actions"]["clean_docker_cache"]:
                result = self._clean_docker_cache()
                cleanup_results["cleanup_details"]["docker_cache"] = result
                cleanup_results["space_freed_mb"] += result.get("space_freed_mb", 0)
            
            if self.cleanup_config["cleanup_actions"]["clean_system_temp"]:
                result = self._clean_system_temp()
                cleanup_results["cleanup_details"]["system_temp"] = result
                cleanup_results["files_deleted"] += result.get("files_deleted", 0)
                cleanup_results["space_freed_mb"] += result.get("space_freed_mb", 0)
            
            # 3. Remove empty directories
            if self.cleanup_config["cleanup_actions"]["remove_empty_directories"]:
                result = self._remove_empty_directories()
                cleanup_results["cleanup_details"]["empty_dirs"] = result
                cleanup_results["directories_deleted"] += result.get("directories_deleted", 0)
            
            # 4. Update cleanup stats
            cleanup_results["cleanup_duration"] = time.time() - start_time
            cleanup_results["last_cleanup"] = datetime.now().isoformat()
            
            # 5. Save cleanup stats
            self._save_cleanup_stats(cleanup_results)
            
            self.logger.info(
                f"✅ Cleanup completed: {cleanup_results['files_deleted']} files, "
                f"{cleanup_results['directories_deleted']} directories, "
                f"{cleanup_results['space_freed_mb']:.1f}MB freed in "
                f"{cleanup_results['cleanup_duration']:.2f}s"
            )
            
        except Exception as e:
            self.logger.error(f"❌ Cleanup failed: {e}")
            cleanup_results["success"] = False
            cleanup_results["errors"].append(str(e))
        
        return cleanup_results
    
    def _clean_directory(self, dir_name: str, dir_config: Dict[str, Any]) -> Dict[str, Any]:
        """Clean a specific directory based on configuration."""
        result = {
            "files_deleted": 0,
            "directories_deleted": 0,
            "space_freed_mb": 0,
            "files_processed": []
        }
        
        try:
            dir_path = self.project_root / dir_config["path"]
            if not dir_path.exists():
                self.logger.warning(f"Directory not found: {dir_path}")
                return result
            
            max_age = dir_config.get("max_age_days", 7)
            if "hours" in dir_config:
                max_age = dir_config["max_age_hours"] / 24  # Convert hours to days
            
            cutoff_time = datetime.now() - timedelta(days=max_age)
            
            self.logger.info(f"🧹 Cleaning directory: {dir_path} (max age: {max_age} days)")
            
            # Find files to clean
            files_to_clean = []
            for pattern in dir_config["patterns"]:
                if dir_config.get("recursive", False):
                    files_to_clean.extend(dir_path.rglob(pattern))
                else:
                    files_to_clean.extend(dir_path.glob(pattern))
            
            # Process files
            for file_path in files_to_clean:
                if file_path.is_file():
                    try:
                        # Check file age
                        file_time = datetime.fromtimestamp(file_path.stat().st_mtime)
                        if file_time < cutoff_time:
                            # Check if file should be preserved
                            if not self._should_preserve_file(file_path):
                                file_size = file_path.stat().st_size
                                file_path.unlink()
                                result["files_deleted"] += 1
                                result["space_freed_mb"] += file_size / (1024 * 1024)
                                result["files_processed"].append(str(file_path))
                                self.logger.debug(f"Deleted: {file_path}")
                    except Exception as e:
                        self.logger.warning(f"Failed to process {file_path}: {e}")
            
        except Exception as e:
            self.logger.error(f"Failed to clean directory {dir_name}: {e}")
        
        return result
    
    def _should_preserve_file(self, file_path: Path) -> bool:
        """Check if a file should be preserved based on patterns."""
        for pattern in self.cleanup_config["preserve_patterns"]:
            if file_path.match(pattern):
                return True
        return False
    
    def _clean_python_cache(self) -> Dict[str, Any]:
        """Clean Python bytecode cache."""
        result = {"files_deleted": 0, "space_freed_mb": 0}
        
        try:
            self.logger.info("🐍 Cleaning Python bytecode cache...")
            
            for pycache_dir in self.project_root.rglob("__pycache__"):
                try:
                    size_before = sum(f.stat().st_size for f in pycache_dir.rglob("*") if f.is_file())
                    shutil.rmtree(pycache_dir)
                    result["files_deleted"] += len(list(pycache_dir.rglob("*")))
                    result["space_freed_mb"] += size_before / (1024 * 1024)
                    self.logger.debug(f"Removed: {pycache_dir}")
                except Exception as e:
                    self.logger.warning(f"Failed to remove {pycache_dir}: {e}")
        
        except Exception as e:
            self.logger.error(f"Failed to clean Python cache: {e}")
        
        return result
    
    def _clean_node_modules_cache(self) -> Dict[str, Any]:
        """Clean Node.js cache."""
        result = {"space_freed_mb": 0}
        
        try:
            self.logger.info("📦 Cleaning Node.js cache...")
            
            # Clean npm cache
            try:
                result_npm = subprocess.run(
                    ["npm", "cache", "clean", "--force"],
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                if result_npm.returncode == 0:
                    self.logger.info("✅ NPM cache cleaned")
                else:
                    self.logger.warning(f"NPM cache clean warning: {result_npm.stderr}")
            except Exception as e:
                self.logger.warning(f"Failed to clean npm cache: {e}")
            
            # Clean yarn cache if exists
            try:
                result_yarn = subprocess.run(
                    ["yarn", "cache", "clean"],
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                if result_yarn.returncode == 0:
                    self.logger.info("✅ Yarn cache cleaned")
            except Exception:
                pass  # Yarn not available
        
        except Exception as e:
            self.logger.error(f"Failed to clean Node.js cache: {e}")
        
        return result
    
    def _clean_docker_cache(self) -> Dict[str, Any]:
        """Clean Docker cache."""
        result = {"space_freed_mb": 0}
        
        try:
            self.logger.info("🐳 Cleaning Docker cache...")
            
            # Docker system prune
            result_docker = subprocess.run(
                ["docker", "system", "prune", "-f"],
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if result_docker.returncode == 0:
                self.logger.info("✅ Docker system pruned")
                # Try to extract space freed from output
                output = result_docker.stdout
                if "reclaimed" in output.lower():
                    self.logger.info(f"Docker cleanup output: {output}")
            else:
                self.logger.warning(f"Docker prune warning: {result_docker.stderr}")
        
        except Exception as e:
            self.logger.error(f"Failed to clean Docker cache: {e}")
        
        return result
    
    def _clean_system_temp(self) -> Dict[str, Any]:
        """Clean system temporary files."""
        result = {"files_deleted": 0, "space_freed_mb": 0}
        
        try:
            self.logger.info("🗂️ Cleaning system temporary files...")
            
            temp_dirs = ["/tmp", "/var/tmp"]
            for temp_dir in temp_dirs:
                if os.path.exists(temp_dir):
                    try:
                        for file_name in os.listdir(temp_dir):
                            file_path = os.path.join(temp_dir, file_name)
                            if os.path.isfile(file_path):
                                # Only clean files that look like temporary files
                                if (file_name.startswith("tmp") or 
                                    file_name.startswith("temp") or
                                    file_name.endswith(".tmp")):
                                    try:
                                        file_size = os.path.getsize(file_path)
                                        os.remove(file_path)
                                        result["files_deleted"] += 1
                                        result["space_freed_mb"] += file_size / (1024 * 1024)
                                        self.logger.debug(f"Deleted temp file: {file_path}")
                                    except Exception:
                                        pass  # Skip files that can't be deleted
                    except Exception as e:
                        self.logger.warning(f"Failed to access {temp_dir}: {e}")
        
        except Exception as e:
            self.logger.error(f"Failed to clean system temp: {e}")
        
        return result
    
    def _remove_empty_directories(self) -> Dict[str, Any]:
        """Remove empty directories."""
        result = {"directories_deleted": 0}
        
        try:
            self.logger.info("📁 Removing empty directories...")
            
            # Find empty directories (bottom-up)
            for root, dirs, files in os.walk(self.project_root, topdown=False):
                for dir_name in dirs:
                    dir_path = os.path.join(root, dir_name)
                    try:
                        # Skip certain directories
                        if dir_name in [".git", "node_modules", "__pycache__", ".venv", "venv"]:
                            continue
                        
                        if not os.listdir(dir_path):  # Directory is empty
                            os.rmdir(dir_path)
                            result["directories_deleted"] += 1
                            self.logger.debug(f"Removed empty directory: {dir_path}")
                    except Exception as e:
                        self.logger.debug(f"Could not remove {dir_path}: {e}")
        
        except Exception as e:
            self.logger.error(f"Failed to remove empty directories: {e}")
        
        return result
    
    def _save_cleanup_stats(self, cleanup_results: Dict[str, Any]):
        """Save cleanup statistics."""
        try:
            stats_file = self.project_root / "logs" / "cleanup_stats.json"
            
            # Load existing stats
            if stats_file.exists():
                with open(stats_file, 'r') as f:
                    all_stats = json.load(f)
            else:
                all_stats = []
            
            # Add new stats
            all_stats.append({
                "timestamp": cleanup_results["last_cleanup"],
                "duration": cleanup_results["cleanup_duration"],
                "files_deleted": cleanup_results["files_deleted"],
                "directories_deleted": cleanup_results["directories_deleted"],
                "space_freed_mb": cleanup_results["space_freed_mb"]
            })
            
            # Keep only last 30 cleanup records
            if len(all_stats) > 30:
                all_stats = all_stats[-30:]
            
            # Save updated stats
            with open(stats_file, 'w') as f:
                json.dump(all_stats, f, indent=2)
            
            self.logger.info(f"Cleanup stats saved to {stats_file}")
        
        except Exception as e:
            self.logger.error(f"Failed to save cleanup stats: {e}")
    
    def get_cleanup_stats(self) -> Dict[str, Any]:
        """Get cleanup statistics."""
        try:
            stats_file = self.project_root / "logs" / "cleanup_stats.json"
            if stats_file.exists():
                with open(stats_file, 'r') as f:
                    return json.load(f)
            else:
                return []
        except Exception as e:
            self.logger.error(f"Failed to load cleanup stats: {e}")
            return []
    
    def get_disk_usage(self) -> Dict[str, Any]:
        """Get current disk usage statistics."""
        try:
            usage = psutil.disk_usage(str(self.project_root))
            return {
                "total_gb": usage.total / (1024**3),
                "used_gb": usage.used / (1024**3),
                "free_gb": usage.free / (1024**3),
                "percent_used": (usage.used / usage.total) * 100
            }
        except Exception as e:
            self.logger.error(f"Failed to get disk usage: {e}")
            return {}


def main():
    """Main function for running cleanup."""
    print("🧹 Comprehensive File System Cleanup")
    print("=" * 50)
    
    cleanup = ComprehensiveFileCleanup()
    
    # Get initial disk usage
    initial_usage = cleanup.get_disk_usage()
    if initial_usage:
        print(f"📊 Initial disk usage: {initial_usage['used_gb']:.1f}GB / {initial_usage['total_gb']:.1f}GB ({initial_usage['percent_used']:.1f}%)")
    
    # Run cleanup
    results = cleanup.run_comprehensive_cleanup()
    
    # Display results
    if results["success"]:
        print(f"\n✅ Cleanup completed successfully!")
        print(f"📁 Files deleted: {results['files_deleted']}")
        print(f"📂 Directories deleted: {results['directories_deleted']}")
        print(f"💾 Space freed: {results['space_freed_mb']:.1f} MB")
        print(f"⏱️ Duration: {results['cleanup_duration']:.2f} seconds")
        
        # Show final disk usage
        final_usage = cleanup.get_disk_usage()
        if final_usage and initial_usage:
            space_freed = initial_usage['used_gb'] - final_usage['used_gb']
            print(f"💽 Space freed: {space_freed:.1f} GB")
    else:
        print(f"\n❌ Cleanup failed!")
        for error in results["errors"]:
            print(f"   Error: {error}")
    
    # Show cleanup history
    stats = cleanup.get_cleanup_stats()
    if stats:
        print(f"\n📈 Recent cleanup history:")
        for stat in stats[-5:]:  # Show last 5 cleanups
            print(f"   {stat['timestamp']}: {stat['files_deleted']} files, {stat['space_freed_mb']:.1f}MB freed")


if __name__ == "__main__":
    main()
