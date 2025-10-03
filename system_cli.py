#!/usr/bin/env python3
"""
System Management CLI
Comprehensive command-line interface for system operations
"""

import argparse
import subprocess
import json
import requests
import sys
from pathlib import Path

class SystemCLI:
    """System management CLI"""
    
    def __init__(self):
        self.services = {
            "consolidated_api": {"port": 8004, "url": "http://localhost:8004/api/system/health"},
            "main_api": {"port": 8000, "url": "http://localhost:8000/health"},
            "frontend": {"port": 3000, "url": "http://localhost:3000"},
            "weaviate": {"port": 8090, "url": "http://localhost:8090/v1/meta"},
            "redis": {"port": 6379, "url": "redis://localhost:6379"},
            "elasticsearch": {"port": 9200, "url": "http://localhost:9200/_cluster/health"},
            "ollama": {"port": 11434, "url": "http://localhost:11434/api/tags"},
            "tts": {"port": 8086, "url": "http://localhost:8086/health"},
            "whisper": {"port": 8087, "url": "http://localhost:8087/health"}
        }
    
    def check_service(self, service_name: str) -> dict:
        """Check if a service is running"""
        if service_name not in self.services:
            return {"status": "unknown", "error": f"Unknown service: {service_name}"}
        
        service = self.services[service_name]
        try:
            if service_name == "redis":
                # Special handling for Redis
                result = subprocess.run(["redis-cli", "ping"], capture_output=True, text=True)
                return {"status": "healthy" if result.returncode == 0 else "down"}
            else:
                response = requests.get(service["url"], timeout=5)
                return {"status": "healthy" if response.status_code == 200 else "down"}
        except Exception as e:
            return {"status": "down", "error": str(e)}
    
    def check_all_services(self) -> dict:
        """Check all services"""
        results = {}
        for service_name in self.services:
            results[service_name] = self.check_service(service_name)
        return results
    
    def start_service(self, service_name: str):
        """Start a service"""
        scripts = {
            "consolidated_api": "python3 consolidated_api_optimized.py",
            "frontend": "cd frontend && npm run dev",
            "docker": "docker-compose up -d",
            "ollama": "ollama serve"
        }
        
        if service_name in scripts:
            print(f"🚀 Starting {service_name}...")
            subprocess.run(scripts[service_name], shell=True)
        else:
            print(f"❌ No start script for {service_name}")
    
    def get_system_stats(self) -> dict:
        """Get system statistics"""
        try:
            import psutil
            return {
                "cpu_percent": psutil.cpu_percent(),
                "memory_percent": psutil.virtual_memory().percent,
                "disk_percent": psutil.disk_usage('/').percent,
                "cpu_count": psutil.cpu_count(),
                "memory_total": psutil.virtual_memory().total,
                "memory_available": psutil.virtual_memory().available
            }
        except ImportError:
            return {"error": "psutil not available"}
    
    def list_models(self) -> dict:
        """List available Ollama models"""
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=5)
            if response.status_code == 200:
                data = response.json()
                return {"models": data.get("models", [])}
            else:
                return {"error": f"Ollama API error: {response.status_code}"}
        except Exception as e:
            return {"error": str(e)}
    
    def get_rag_stats(self) -> dict:
        """Get RAG system statistics"""
        try:
            response = requests.get("http://localhost:8004/api/knowledge/stats", timeout=5)
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"RAG API error: {response.status_code}"}
        except Exception as e:
            return {"error": str(e)}

def main():
    parser = argparse.ArgumentParser(
        description="System Management CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Check all services
  python3 system_cli.py status
  
  # Check specific service
  python3 system_cli.py status --service consolidated_api
  
  # Start services
  python3 system_cli.py start --service consolidated_api
  python3 system_cli.py start --service docker
  
  # System information
  python3 system_cli.py stats
  
  # List models
  python3 system_cli.py models
  
  # RAG statistics
  python3 system_cli.py rag
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Status command
    status_parser = subparsers.add_parser("status", help="Check service status")
    status_parser.add_argument("--service", "-s", help="Check specific service")
    status_parser.add_argument("--json", "-j", action="store_true", help="JSON output")
    
    # Start command
    start_parser = subparsers.add_parser("start", help="Start services")
    start_parser.add_argument("--service", "-s", required=True, help="Service to start")
    
    # Stats command
    stats_parser = subparsers.add_parser("stats", help="Get system statistics")
    stats_parser.add_argument("--json", action="store_true", help="Output as JSON")
    
    # Models command
    models_parser = subparsers.add_parser("models", help="List available models")
    models_parser.add_argument("--json", action="store_true", help="Output as JSON")
    
    # RAG command
    rag_parser = subparsers.add_parser("rag", help="Get RAG statistics")
    rag_parser.add_argument("--json", action="store_true", help="Output as JSON")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    cli = SystemCLI()
    
    if args.command == "status":
        if args.service:
            result = cli.check_service(args.service)
            if args.json:
                print(json.dumps({args.service: result}, indent=2))
            else:
                status = result.get("status", "unknown")
                emoji = "✅" if status == "healthy" else "❌"
                print(f"{emoji} {args.service}: {status}")
                if "error" in result:
                    print(f"   Error: {result['error']}")
        else:
            results = cli.check_all_services()
            if args.json:
                print(json.dumps(results, indent=2))
            else:
                print("🔍 Service Status Check")
                print("=" * 30)
                for service, result in results.items():
                    status = result.get("status", "unknown")
                    emoji = "✅" if status == "healthy" else "❌"
                    print(f"{emoji} {service}: {status}")
                    if "error" in result:
                        print(f"   Error: {result['error']}")
    
    elif args.command == "start":
        cli.start_service(args.service)
    
    elif args.command == "stats":
        stats = cli.get_system_stats()
        if args.json:
            print(json.dumps(stats, indent=2))
        else:
            print("📊 System Statistics")
            print("=" * 20)
            if "error" in stats:
                print(f"❌ Error: {stats['error']}")
            else:
                print(f"🖥️  CPU: {stats['cpu_percent']:.1f}%")
                print(f"🧠 Memory: {stats['memory_percent']:.1f}%")
                print(f"💾 Disk: {stats['disk_percent']:.1f}%")
                print(f"🔢 CPU Cores: {stats['cpu_count']}")
    
    elif args.command == "models":
        models = cli.list_models()
        if args.json:
            print(json.dumps(models, indent=2))
        else:
            print("🤖 Available Models")
            print("=" * 20)
            if "error" in models:
                print(f"❌ Error: {models['error']}")
            else:
                for model in models.get("models", []):
                    name = model.get("name", "unknown")
                    size = model.get("size", 0)
                    print(f"📦 {name} ({size:,} bytes)")
    
    elif args.command == "rag":
        rag_stats = cli.get_rag_stats()
        if args.json:
            print(json.dumps(rag_stats, indent=2))
        else:
            print("🔍 RAG Statistics")
            print("=" * 20)
            if "error" in rag_stats:
                print(f"❌ Error: {rag_stats['error']}")
            else:
                print(f"📚 Documents: {rag_stats.get('total_documents', 0)}")
                print(f"📊 Status: {rag_stats.get('status', 'unknown')}")
                print(f"💾 Cache Size: {rag_stats.get('cache_size', 0)}")

if __name__ == "__main__":
    main()
