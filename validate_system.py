#!/usr/bin/env python3
"""
System Validation Before Implementation
Comprehensive validation to identify real gaps and priorities
"""

import asyncio
import logging
import time
import requests
import json
import subprocess
import os
from typing import Dict, List, Any, Optional
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SystemValidator:
    """Comprehensive system validation before implementation"""
    
    def __init__(self):
        self.validation_results = {
            "services": {},
            "models": {},
            "capabilities": {},
            "performance": {},
            "gaps": {},
            "priorities": {}
        }
        self.critical_issues = []
        self.implementation_ready = []
    
    async def validate_services(self):
        """Validate all system services"""
        logger.info("🔍 Validating system services...")
        
        services = {
            "main_api": "http://localhost:8004",
            "evolutionary_api": "http://localhost:8005",
            "unified_kb": "http://localhost:8001",
            "weaviate": "http://localhost:8090",
            "redis": "redis://localhost:6379",
            "postgres": "postgresql://postgres:password@localhost:5433/agentic_db"
        }
        
        for service_name, endpoint in services.items():
            try:
                if service_name == "redis":
                    # Test Redis connection
                    import redis.asyncio as redis
                    client = redis.from_url(endpoint)
                    await client.ping()
                    await client.aclose()
                    self.validation_results["services"][service_name] = {
                        "status": "working",
                        "response_time_ms": 0,
                        "details": "Redis connection successful"
                    }
                elif service_name == "postgres":
                    # Test PostgreSQL connection
                    import asyncpg
                    conn = await asyncpg.connect(endpoint)
                    result = await conn.fetchval("SELECT 1")
                    await conn.close()
                    self.validation_results["services"][service_name] = {
                        "status": "working",
                        "response_time_ms": 0,
                        "details": "PostgreSQL connection successful"
                    }
                else:
                    # Test HTTP endpoints
                    start_time = time.time()
                    response = requests.get(f"{endpoint}/health", timeout=10)
                    response_time = (time.time() - start_time) * 1000
                    
                    self.validation_results["services"][service_name] = {
                        "status": "working" if response.status_code == 200 else "error",
                        "response_time_ms": response_time,
                        "status_code": response.status_code,
                        "details": f"HTTP {response.status_code}"
                    }
                
                logger.info(f"✅ {service_name}: {self.validation_results['services'][service_name]['status']}")
                
            except Exception as e:
                self.validation_results["services"][service_name] = {
                    "status": "error",
                    "error": str(e),
                    "details": f"Service not accessible: {e}"
                }
                logger.error(f"❌ {service_name}: {e}")
    
    async def validate_models(self):
        """Validate available AI models"""
        logger.info("🔍 Validating AI models...")
        
        try:
            # Check Ollama models
            response = requests.get("http://localhost:11434/api/tags", timeout=10)
            if response.status_code == 200:
                models_data = response.json()
                available_models = [model["name"] for model in models_data.get("models", [])]
                
                # Test each model
                for model_name in available_models:
                    try:
                        start_time = time.time()
                        test_response = requests.post(
                            "http://localhost:11434/api/generate",
                            json={
                                "model": model_name,
                                "prompt": "Test response",
                                "stream": False
                            },
                            timeout=30
                        )
                        response_time = (time.time() - start_time) * 1000
                        
                        if test_response.status_code == 200:
                            self.validation_results["models"][model_name] = {
                                "status": "working",
                                "response_time_ms": response_time,
                                "size_gb": self._estimate_model_size(model_name),
                                "details": "Model responding correctly"
                            }
                        else:
                            self.validation_results["models"][model_name] = {
                                "status": "error",
                                "response_time_ms": response_time,
                                "status_code": test_response.status_code,
                                "details": f"Model error: {test_response.status_code}"
                            }
                        
                        logger.info(f"✅ {model_name}: {self.validation_results['models'][model_name]['status']}")
                        
                    except Exception as e:
                        self.validation_results["models"][model_name] = {
                            "status": "error",
                            "error": str(e),
                            "details": f"Model test failed: {e}"
                        }
                        logger.error(f"❌ {model_name}: {e}")
            else:
                logger.error("❌ Cannot access Ollama API")
                
        except Exception as e:
            logger.error(f"❌ Model validation failed: {e}")
    
    def _estimate_model_size(self, model_name: str) -> float:
        """Estimate model size based on name"""
        size_mapping = {
            "qwen2.5:72b": 47.0,
            "qwen2.5:14b": 9.0,
            "qwen2.5:7b": 4.7,
            "mistral:7b": 4.4,
            "llama3.2:3b": 2.0,
            "llava:7b": 4.7,
            "gpt-oss:20b": 14.0
        }
        return size_mapping.get(model_name, 1.0)
    
    async def validate_capabilities(self):
        """Validate system capabilities"""
        logger.info("🔍 Validating system capabilities...")
        
        capabilities = {
            "vision_analysis": await self._test_vision_capability(),
            "voice_tts": await self._test_voice_tts(),
            "voice_stt": await self._test_voice_stt(),
            "web_browsing": await self._test_web_browsing(),
            "file_operations": await self._test_file_operations(),
            "calculator": await self._test_calculator(),
            "rag_search": await self._test_rag_search(),
            "agent_selection": await self._test_agent_selection(),
            "evolutionary_optimization": await self._test_evolutionary_optimization()
        }
        
        self.validation_results["capabilities"] = capabilities
        
        for cap_name, result in capabilities.items():
            status = "✅" if result["working"] else "❌"
            logger.info(f"{status} {cap_name}: {result['details']}")
    
    async def _test_vision_capability(self) -> Dict[str, Any]:
        """Test vision analysis capability"""
        try:
            # Check if LLaVA model is available and working
            if "llava:7b" in self.validation_results.get("models", {}):
                model_status = self.validation_results["models"]["llava:7b"]
                if model_status["status"] == "working":
                    return {
                        "working": True,
                        "details": "LLaVA model available and working",
                        "model": "llava:7b"
                    }
            
            return {
                "working": False,
                "details": "LLaVA model not available or not working",
                "model": None
            }
        except Exception as e:
            return {
                "working": False,
                "details": f"Vision test failed: {e}",
                "error": str(e)
            }
    
    async def _test_voice_tts(self) -> Dict[str, Any]:
        """Test text-to-speech capability"""
        try:
            # Check if TTS service is available
            response = requests.get("http://localhost:8004/api/voice/options", timeout=5)
            if response.status_code == 200:
                return {
                    "working": True,
                    "details": "TTS service available",
                    "endpoint": "/api/voice/options"
                }
            else:
                return {
                    "working": False,
                    "details": f"TTS service not available: {response.status_code}",
                    "status_code": response.status_code
                }
        except Exception as e:
            return {
                "working": False,
                "details": f"TTS test failed: {e}",
                "error": str(e)
            }
    
    async def _test_voice_stt(self) -> Dict[str, Any]:
        """Test speech-to-text capability"""
        try:
            # Check if Whisper/STT service is available
            # This would typically be a different endpoint
            return {
                "working": False,
                "details": "STT service not implemented",
                "status": "not_implemented"
            }
        except Exception as e:
            return {
                "working": False,
                "details": f"STT test failed: {e}",
                "error": str(e)
            }
    
    async def _test_web_browsing(self) -> Dict[str, Any]:
        """Test web browsing capability"""
        try:
            # Test web browsing through chat
            response = requests.post(
                "http://localhost:8004/api/chat/",
                json={
                    "message": "Browse to google.com and tell me what you see",
                    "agent_id": None,
                    "show_browser_windows": False
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if "browse" in result.get("response", "").lower() or "web" in result.get("response", "").lower():
                    return {
                        "working": True,
                        "details": "Web browsing capability detected",
                        "response": result.get("response", "")[:100]
                    }
                else:
                    return {
                        "working": False,
                        "details": "Web browsing not functional - returns generic response",
                        "response": result.get("response", "")[:100]
                    }
            else:
                return {
                    "working": False,
                    "details": f"Web browsing test failed: {response.status_code}",
                    "status_code": response.status_code
                }
        except Exception as e:
            return {
                "working": False,
                "details": f"Web browsing test failed: {e}",
                "error": str(e)
            }
    
    async def _test_file_operations(self) -> Dict[str, Any]:
        """Test file operations capability"""
        try:
            # Test file operations through chat
            response = requests.post(
                "http://localhost:8004/api/chat/",
                json={
                    "message": "List files in the current directory",
                    "agent_id": None,
                    "show_browser_windows": False
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if "ls" in result.get("response", "").lower() or "directory" in result.get("response", "").lower():
                    return {
                        "working": True,
                        "details": "File operations capability detected",
                        "response": result.get("response", "")[:100]
                    }
                else:
                    return {
                        "working": False,
                        "details": "File operations not functional - returns generic response",
                        "response": result.get("response", "")[:100]
                    }
            else:
                return {
                    "working": False,
                    "details": f"File operations test failed: {response.status_code}",
                    "status_code": response.status_code
                }
        except Exception as e:
            return {
                "working": False,
                "details": f"File operations test failed: {e}",
                "error": str(e)
            }
    
    async def _test_calculator(self) -> Dict[str, Any]:
        """Test calculator capability"""
        try:
            # Test calculator through chat
            response = requests.post(
                "http://localhost:8004/api/chat/",
                json={
                    "message": "Calculate 15 * 23 + 7",
                    "agent_id": None,
                    "show_browser_windows": False
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                response_text = result.get("response", "")
                if "352" in response_text or "15 * 23 + 7" in response_text:
                    return {
                        "working": True,
                        "details": "Calculator capability working",
                        "response": response_text[:100]
                    }
                else:
                    return {
                        "working": False,
                        "details": "Calculator not functional - returns generic response",
                        "response": response_text[:100]
                    }
            else:
                return {
                    "working": False,
                    "details": f"Calculator test failed: {response.status_code}",
                    "status_code": response.status_code
                }
        except Exception as e:
            return {
                "working": False,
                "details": f"Calculator test failed: {e}",
                "error": str(e)
            }
    
    async def _test_rag_search(self) -> Dict[str, Any]:
        """Test RAG search capability"""
        try:
            # Test RAG search
            response = requests.post(
                "http://localhost:8005/api/rag/query",
                json={
                    "query": "test search",
                    "limit": 5
                },
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                if "results" in result and len(result["results"]) > 0:
                    return {
                        "working": True,
                        "details": f"RAG search working - {len(result['results'])} results",
                        "results_count": len(result["results"])
                    }
                else:
                    return {
                        "working": False,
                        "details": "RAG search returns no results",
                        "results_count": 0
                    }
            else:
                return {
                    "working": False,
                    "details": f"RAG search failed: {response.status_code}",
                    "status_code": response.status_code
                }
        except Exception as e:
            return {
                "working": False,
                "details": f"RAG search test failed: {e}",
                "error": str(e)
            }
    
    async def _test_agent_selection(self) -> Dict[str, Any]:
        """Test agent selection capability"""
        try:
            from src.core.optimization.optimized_agent_selector import initialize_agent_selector, SelectionCriteria
            
            selector = await initialize_agent_selector()
            criteria = SelectionCriteria(
                task_type="validation_test",
                complexity="medium",
                priority="normal",
                context={"test": "capability"}
            )
            
            start_time = time.time()
            result = await selector.select_agent(criteria)
            selection_time = (time.time() - start_time) * 1000
            
            return {
                "working": True,
                "details": f"Agent selection working - {result.selected_agent.name}",
                "selection_time_ms": selection_time,
                "agent_name": result.selected_agent.name
            }
        except Exception as e:
            return {
                "working": False,
                "details": f"Agent selection test failed: {e}",
                "error": str(e)
            }
    
    async def _test_evolutionary_optimization(self) -> Dict[str, Any]:
        """Test evolutionary optimization capability"""
        try:
            # Test evolutionary optimization
            response = requests.get("http://localhost:8005/api/evolutionary/stats", timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "working": True,
                    "details": "Evolutionary optimization service available",
                    "status": result.get("status", "unknown")
                }
            else:
                return {
                    "working": False,
                    "details": f"Evolutionary optimization failed: {response.status_code}",
                    "status_code": response.status_code
                }
        except Exception as e:
            return {
                "working": False,
                "details": f"Evolutionary optimization test failed: {e}",
                "error": str(e)
            }
    
    async def validate_performance(self):
        """Validate system performance"""
        logger.info("🔍 Validating system performance...")
        
        performance_tests = {
            "chat_response_time": await self._test_chat_performance(),
            "agent_selection_time": await self._test_agent_selection_performance(),
            "rag_query_time": await self._test_rag_performance(),
            "model_load_time": await self._test_model_performance()
        }
        
        self.validation_results["performance"] = performance_tests
        
        for test_name, result in performance_tests.items():
            logger.info(f"📊 {test_name}: {result['value']:.1f}ms")
    
    async def _test_chat_performance(self) -> Dict[str, Any]:
        """Test chat response performance"""
        try:
            times = []
            for i in range(3):
                start_time = time.time()
                response = requests.post(
                    "http://localhost:8004/api/chat/",
                    json={
                        "message": f"Performance test {i+1}",
                        "agent_id": None,
                        "show_browser_windows": False
                    },
                    timeout=30
                )
                response_time = (time.time() - start_time) * 1000
                times.append(response_time)
            
            avg_time = sum(times) / len(times)
            return {
                "value": avg_time,
                "times": times,
                "status": "good" if avg_time < 2000 else "needs_improvement"
            }
        except Exception as e:
            return {
                "value": 0,
                "error": str(e),
                "status": "error"
            }
    
    async def _test_agent_selection_performance(self) -> Dict[str, Any]:
        """Test agent selection performance"""
        try:
            from src.core.optimization.optimized_agent_selector import initialize_agent_selector, SelectionCriteria
            
            selector = await initialize_agent_selector()
            criteria = SelectionCriteria(
                task_type="performance_test",
                complexity="medium",
                priority="normal",
                context={"test": "performance"}
            )
            
            times = []
            for i in range(5):
                start_time = time.time()
                await selector.select_agent(criteria)
                selection_time = (time.time() - start_time) * 1000
                times.append(selection_time)
            
            avg_time = sum(times) / len(times)
            return {
                "value": avg_time,
                "times": times,
                "status": "excellent" if avg_time < 10 else "good" if avg_time < 100 else "needs_improvement"
            }
        except Exception as e:
            return {
                "value": 0,
                "error": str(e),
                "status": "error"
            }
    
    async def _test_rag_performance(self) -> Dict[str, Any]:
        """Test RAG query performance"""
        try:
            times = []
            for i in range(3):
                start_time = time.time()
                response = requests.post(
                    "http://localhost:8005/api/rag/query",
                    json={
                        "query": f"performance test {i+1}",
                        "limit": 5
                    },
                    timeout=10
                )
                response_time = (time.time() - start_time) * 1000
                times.append(response_time)
            
            avg_time = sum(times) / len(times)
            return {
                "value": avg_time,
                "times": times,
                "status": "good" if avg_time < 1000 else "needs_improvement"
            }
        except Exception as e:
            return {
                "value": 0,
                "error": str(e),
                "status": "error"
            }
    
    async def _test_model_performance(self) -> Dict[str, Any]:
        """Test model loading performance"""
        try:
            # Test model response time
            start_time = time.time()
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": "llama3.2:3b",
                    "prompt": "Quick test",
                    "stream": False
                },
                timeout=30
            )
            response_time = (time.time() - start_time) * 1000
            
            return {
                "value": response_time,
                "status": "good" if response_time < 5000 else "needs_improvement"
            }
        except Exception as e:
            return {
                "value": 0,
                "error": str(e),
                "status": "error"
            }
    
    def analyze_gaps_and_priorities(self):
        """Analyze gaps and determine implementation priorities"""
        logger.info("🔍 Analyzing gaps and priorities...")
        
        # Analyze service gaps
        service_gaps = []
        for service, status in self.validation_results["services"].items():
            if status["status"] != "working":
                service_gaps.append({
                    "service": service,
                    "issue": status.get("error", "Service not working"),
                    "priority": "critical" if service in ["main_api", "redis", "postgres"] else "high"
                })
        
        # Analyze capability gaps
        capability_gaps = []
        for capability, status in self.validation_results["capabilities"].items():
            if not status["working"]:
                priority = "critical" if capability in ["vision_analysis", "voice_tts", "web_browsing"] else "high" if capability in ["file_operations", "calculator"] else "medium"
                capability_gaps.append({
                    "capability": capability,
                    "issue": status.get("details", "Capability not working"),
                    "priority": priority
                })
        
        # Analyze performance gaps
        performance_gaps = []
        for metric, status in self.validation_results["performance"].items():
            if status["status"] in ["needs_improvement", "error"]:
                performance_gaps.append({
                    "metric": metric,
                    "value": status["value"],
                    "issue": status.get("error", "Performance needs improvement"),
                    "priority": "medium"
                })
        
        self.validation_results["gaps"] = {
            "services": service_gaps,
            "capabilities": capability_gaps,
            "performance": performance_gaps
        }
        
        # Determine implementation priorities
        critical_issues = [gap for gap in service_gaps + capability_gaps if gap["priority"] == "critical"]
        high_priority = [gap for gap in service_gaps + capability_gaps if gap["priority"] == "high"]
        medium_priority = [gap for gap in service_gaps + capability_gaps + performance_gaps if gap["priority"] == "medium"]
        
        self.validation_results["priorities"] = {
            "critical": critical_issues,
            "high": high_priority,
            "medium": medium_priority
        }
        
        self.critical_issues = critical_issues
        self.implementation_ready = [gap for gap in service_gaps + capability_gaps if gap["priority"] in ["critical", "high"]]
    
    def display_validation_results(self):
        """Display comprehensive validation results"""
        logger.info("📊 SYSTEM VALIDATION RESULTS")
        logger.info("=" * 60)
        
        # Services
        logger.info("🌐 SERVICES:")
        for service, status in self.validation_results["services"].items():
            status_icon = "✅" if status["status"] == "working" else "❌"
            logger.info(f"   {status_icon} {service}: {status['details']}")
        
        # Models
        logger.info("🤖 MODELS:")
        for model, status in self.validation_results["models"].items():
            status_icon = "✅" if status["status"] == "working" else "❌"
            size = status.get("size_gb", 0)
            logger.info(f"   {status_icon} {model}: {status['details']} ({size}GB)")
        
        # Capabilities
        logger.info("🔧 CAPABILITIES:")
        for capability, status in self.validation_results["capabilities"].items():
            status_icon = "✅" if status["working"] else "❌"
            logger.info(f"   {status_icon} {capability}: {status['details']}")
        
        # Performance
        logger.info("📊 PERFORMANCE:")
        for metric, status in self.validation_results["performance"].items():
            status_icon = "✅" if status["status"] == "good" else "⚠️" if status["status"] == "needs_improvement" else "❌"
            logger.info(f"   {status_icon} {metric}: {status['value']:.1f}ms")
        
        # Gaps and Priorities
        logger.info("🚨 CRITICAL ISSUES:")
        for issue in self.critical_issues:
            logger.info(f"   ❌ {issue['service'] if 'service' in issue else issue['capability']}: {issue['issue']}")
        
        logger.info("⚠️ HIGH PRIORITY ISSUES:")
        for issue in self.validation_results["priorities"]["high"]:
            logger.info(f"   ⚠️ {issue['service'] if 'service' in issue else issue['capability']}: {issue['issue']}")
        
        logger.info("=" * 60)
    
    async def run_validation(self):
        """Run comprehensive system validation"""
        logger.info("🚀 Starting comprehensive system validation...")
        logger.info("=" * 60)
        
        start_time = time.time()
        
        try:
            # Run all validations
            await self.validate_services()
            await self.validate_models()
            await self.validate_capabilities()
            await self.validate_performance()
            
            # Analyze results
            self.analyze_gaps_and_priorities()
            
            # Display results
            self.display_validation_results()
            
            total_time = time.time() - start_time
            logger.info(f"✅ Validation completed in {total_time:.2f} seconds")
            
            return self.validation_results
            
        except Exception as e:
            logger.error(f"❌ Validation failed: {e}")
            raise

async def main():
    """Main validation function"""
    validator = SystemValidator()
    
    try:
        results = await validator.run_validation()
        
        # Save results to file
        with open("system_validation_results.json", "w") as f:
            json.dump(results, f, indent=2, default=str)
        
        logger.info("📄 Validation results saved to system_validation_results.json")
        
        # Summary
        total_services = len(results["services"])
        working_services = len([s for s in results["services"].values() if s["status"] == "working"])
        
        total_capabilities = len(results["capabilities"])
        working_capabilities = len([c for c in results["capabilities"].values() if c["working"]])
        
        logger.info(f"📊 SUMMARY: {working_services}/{total_services} services working, {working_capabilities}/{total_capabilities} capabilities working")
        
        return True
        
    except Exception as e:
        logger.error(f"System validation failed: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    if success:
        print("\n🎉 System validation completed successfully!")
        print("📊 Comprehensive analysis of current system state")
        print("🎯 Implementation priorities identified")
    else:
        print("\n❌ System validation failed!")
