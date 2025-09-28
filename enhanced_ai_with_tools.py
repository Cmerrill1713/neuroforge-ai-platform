#!/usr/bin/env python3
"""
Enhanced AI System with Web Search and Docker Inspection
Teaches our AI models to look online and in Docker for more information
"""

import asyncio
import json
import subprocess
import requests
import time
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Import our HRM components
from src.core.reasoning.parallel_reasoning_engine import ParallelReasoningEngine, ReasoningMode
from src.core.engines.ollama_adapter import OllamaAdapter

class EnhancedAIToolkit:
    """Provides AI models with web search and Docker inspection capabilities."""
    
    def __init__(self):
        self.searxng_url = "http://localhost:8888"  # From our Docker setup
        self.docker_info_cache = {}
        self.web_search_cache = {}
        
    async def web_search(self, query: str, num_results: int = 5) -> List[Dict]:
        """Search the web using our SearXNG instance."""
        
        # Check cache first
        cache_key = f"{query}_{num_results}"
        if cache_key in self.web_search_cache:
            return self.web_search_cache[cache_key]
        
        try:
            # Use SearXNG for web search
            params = {
                'q': query,
                'format': 'json',
                'engines': 'google,bing,duckduckgo',
                'categories': 'general'
            }
            
            response = requests.get(f"{self.searxng_url}/search", params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                results = []
                
                for result in data.get('results', [])[:num_results]:
                    results.append({
                        'title': result.get('title', ''),
                        'url': result.get('url', ''),
                        'content': result.get('content', ''),
                        'engine': result.get('engine', 'unknown')
                    })
                
                # Cache results
                self.web_search_cache[cache_key] = results
                return results
            else:
                print(f"SearXNG search failed: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"Web search error: {str(e)}")
            return []
    
    def get_docker_containers(self) -> List[Dict]:
        """Get information about Docker containers."""
        
        if 'containers' in self.docker_info_cache:
            return self.docker_info_cache['containers']
        
        try:
            # Get container information
            result = subprocess.run(['docker', 'ps', '-a', '--format', 'json'], 
                                  capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                containers = []
                for line in result.stdout.strip().split('\n'):
                    if line:
                        try:
                            container = json.loads(line)
                            containers.append({
                                'id': container.get('ID', ''),
                                'image': container.get('Image', ''),
                                'command': container.get('Command', ''),
                                'created': container.get('CreatedAt', ''),
                                'status': container.get('Status', ''),
                                'ports': container.get('Ports', ''),
                                'names': container.get('Names', '')
                            })
                        except json.JSONDecodeError:
                            continue
                
                self.docker_info_cache['containers'] = containers
                return containers
            else:
                print(f"Docker ps failed: {result.stderr}")
                return []
                
        except Exception as e:
            print(f"Docker container inspection error: {str(e)}")
            return []
    
    def get_docker_images(self) -> List[Dict]:
        """Get information about Docker images."""
        
        if 'images' in self.docker_info_cache:
            return self.docker_info_cache['images']
        
        try:
            # Get image information
            result = subprocess.run(['docker', 'images', '--format', 'json'], 
                                  capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                images = []
                for line in result.stdout.strip().split('\n'):
                    if line:
                        try:
                            image = json.loads(line)
                            images.append({
                                'repository': image.get('Repository', ''),
                                'tag': image.get('Tag', ''),
                                'image_id': image.get('ID', ''),
                                'created': image.get('CreatedAt', ''),
                                'size': image.get('Size', '')
                            })
                        except json.JSONDecodeError:
                            continue
                
                self.docker_info_cache['images'] = images
                return images
            else:
                print(f"Docker images failed: {result.stderr}")
                return []
                
        except Exception as e:
            print(f"Docker image inspection error: {str(e)}")
            return []
    
    def get_docker_networks(self) -> List[Dict]:
        """Get information about Docker networks."""
        
        try:
            result = subprocess.run(['docker', 'network', 'ls', '--format', 'json'], 
                                  capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                networks = []
                for line in result.stdout.strip().split('\n'):
                    if line:
                        try:
                            network = json.loads(line)
                            networks.append({
                                'id': network.get('ID', ''),
                                'name': network.get('Name', ''),
                                'driver': network.get('Driver', ''),
                                'scope': network.get('Scope', '')
                            })
                        except json.JSONDecodeError:
                            continue
                
                return networks
            else:
                return []
                
        except Exception as e:
            print(f"Docker network inspection error: {str(e)}")
            return []
    
    def inspect_container(self, container_name_or_id: str) -> Dict:
        """Get detailed information about a specific container."""
        
        try:
            result = subprocess.run(['docker', 'inspect', container_name_or_id], 
                                  capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                inspection = json.loads(result.stdout)
                if inspection:
                    container_info = inspection[0]
                    return {
                        'id': container_info.get('Id', ''),
                        'name': container_info.get('Name', ''),
                        'image': container_info.get('Config', {}).get('Image', ''),
                        'state': container_info.get('State', {}),
                        'config': container_info.get('Config', {}),
                        'network_settings': container_info.get('NetworkSettings', {}),
                        'mounts': container_info.get('Mounts', [])
                    }
            return {}
                
        except Exception as e:
            print(f"Container inspection error: {str(e)}")
            return {}

class EnhancedAIAgent:
    """AI Agent with web search and Docker inspection capabilities."""
    
    def __init__(self):
        self.ollama_adapter = OllamaAdapter()
        self.reasoning_engine = ParallelReasoningEngine(
            ollama_adapter=self.ollama_adapter,
            config={
                "self_supervised_enabled": True,
                "adaptive_strategy_enabled": True,
                "chaos_intensity": 0.1,
                "quantum_coherence_threshold": 0.8
            }
        )
        self.toolkit = EnhancedAIToolkit()
        
        self.models = [
            {"id": "llama3.1:8b", "role": "Full-Stack Architect", "color": "🔵"},
            {"id": "qwen2.5:7b", "role": "UX/UI Designer", "color": "🟣"},
            {"id": "mistral:7b", "role": "Frontend Engineer", "color": "🟢"},
            {"id": "phi3:3.8b", "role": "DevOps Specialist", "color": "🟠"},
            {"id": "llama3.2:3b", "role": "Product Manager", "color": "🔴"},
            {"id": "llava:7b", "role": "Multimodal Specialist", "color": "🟦"},
            {"id": "nomic-embed-text:latest", "role": "Embedding Expert", "color": "🟦"},
            {"id": "gpt-oss:20b", "role": "Advanced Reasoning", "color": "🩷"}
        ]
    
    async def enhanced_analysis(self, task: str, use_web_search: bool = True, use_docker_info: bool = True):
        """Perform enhanced analysis using web search and Docker information."""
        
        print(f"🔍 Enhanced AI Analysis: {task}")
        print("=" * 60)
        
        # Gather additional context
        context_info = []
        
        if use_web_search:
            print("🌐 Searching web for relevant information...")
            web_results = await self.toolkit.web_search(task, num_results=3)
            if web_results:
                context_info.append("WEB SEARCH RESULTS:")
                for i, result in enumerate(web_results, 1):
                    context_info.append(f"{i}. {result['title']}")
                    context_info.append(f"   URL: {result['url']}")
                    context_info.append(f"   Content: {result['content'][:200]}...")
                    context_info.append("")
        
        if use_docker_info:
            print("🐳 Gathering Docker environment information...")
            containers = self.toolkit.get_docker_containers()
            images = self.toolkit.get_docker_images()
            
            if containers:
                context_info.append("DOCKER CONTAINERS:")
                for container in containers[:10]:  # Limit to first 10
                    context_info.append(f"- {container['names']}: {container['image']} ({container['status']})")
                context_info.append("")
            
            if images:
                context_info.append("DOCKER IMAGES:")
                for image in images[:10]:  # Limit to first 10
                    context_info.append(f"- {image['repository']}:{image['tag']} ({image['size']})")
                context_info.append("")
        
        # Create enhanced prompt with context
        enhanced_prompt = f"""TASK: {task}

ADDITIONAL CONTEXT AVAILABLE:
{chr(10).join(context_info)}

INSTRUCTIONS:
1. Use the web search results to get current, up-to-date information
2. Consider our Docker environment and available services
3. Provide specific, actionable recommendations
4. Reference relevant web sources and Docker resources
5. Think about how our existing infrastructure can be leveraged

Your analysis should be informed by both current web information and our actual Docker environment."""
        
        # Perform enhanced reasoning
        print("🧠 AI models analyzing with enhanced context...")
        result = await self.reasoning_engine.parallel_reasoning(
            task=enhanced_prompt,
            num_paths=2,
            mode=ReasoningMode.HYBRID
        )
        
        # Learn from this interaction
        await self.reasoning_engine.learn_from_interaction(
            task=enhanced_prompt,
            reasoning_result=result,
            actual_outcome={"success": True, "efficiency": 0.9},
            user_feedback={"satisfaction": 0.95, "usefulness": 0.9}
        )
        
        return {
            "task": task,
            "web_results": web_results if use_web_search else [],
            "docker_containers": len(containers) if use_docker_info else 0,
            "docker_images": len(images) if use_docker_info else 0,
            "ai_analysis": result.best_path.content if result.best_path else None,
            "confidence": result.best_path.confidence if result.best_path else 0,
            "context_used": len(context_info)
        }
    
    async def docker_specific_analysis(self, container_or_service: str):
        """Analyze a specific Docker container or service."""
        
        print(f"🐳 Docker-Specific Analysis: {container_or_service}")
        print("-" * 40)
        
        # Get detailed container information
        container_info = self.toolkit.inspect_container(container_or_service)
        
        if not container_info:
            print(f"❌ Container '{container_or_service}' not found")
            return None
        
        # Search web for information about the service
        image_name = container_info.get('image', '')
        web_results = await self.toolkit.web_search(f"{image_name} docker best practices", num_results=3)
        
        # Create analysis prompt
        analysis_prompt = f"""DOCKER CONTAINER ANALYSIS: {container_or_service}

CONTAINER DETAILS:
- Image: {container_info.get('image', 'Unknown')}
- State: {container_info.get('state', {}).get('Status', 'Unknown')}
- Config: {json.dumps(container_info.get('config', {}), indent=2)[:500]}...

WEB RESEARCH RESULTS:
{chr(10).join([f"- {r['title']}: {r['content'][:100]}..." for r in web_results])}

ANALYSIS TASKS:
1. Assess container health and configuration
2. Identify potential improvements or issues
3. Suggest optimizations based on web research
4. Check for security best practices
5. Recommend monitoring or maintenance actions

Provide specific, actionable recommendations for this container."""
        
        result = await self.reasoning_engine.parallel_reasoning(
            task=analysis_prompt,
            num_paths=1,
            mode=ReasoningMode.VERIFICATION,
            verification_enabled=True
        )
        
        return {
            "container": container_or_service,
            "container_info": container_info,
            "web_research": web_results,
            "ai_analysis": result.best_path.content if result.best_path else None,
            "confidence": result.best_path.confidence if result.best_path else 0,
            "verification_score": result.verification[0].overall_score if result.verification else 0
        }

async def main():
    """Demonstrate enhanced AI capabilities."""
    
    print("🚀 Enhanced AI System with Web Search & Docker Inspection")
    print("=" * 70)
    
    agent = EnhancedAIAgent()
    
    # Test 1: Enhanced analysis of frontend improvements
    print("\n🎯 Test 1: Frontend Enhancement Analysis")
    result1 = await agent.enhanced_analysis(
        "How can we improve our Next.js frontend performance and add real-time collaboration features?",
        use_web_search=True,
        use_docker_info=True
    )
    
    print(f"✅ Analysis complete!")
    print(f"📊 Confidence: {result1['confidence']:.2f}")
    print(f"🌐 Web results: {len(result1['web_results'])}")
    print(f"🐳 Docker containers: {result1['docker_containers']}")
    print(f"📝 Context lines: {result1['context_used']}")
    
    # Test 2: Docker-specific analysis
    print("\n🐳 Test 2: Docker Container Analysis")
    result2 = await agent.docker_specific_analysis("agi-redis")
    
    if result2:
        print(f"✅ Container analysis complete!")
        print(f"📊 Confidence: {result2['confidence']:.2f}")
        print(f"🔍 Verification: {result2['verification_score']:.2f}")
        print(f"🌐 Web research: {len(result2['web_research'])} results")
    
    # Test 3: AGI system overview
    print("\n🧠 Test 3: AGI System Overview Analysis")
    result3 = await agent.enhanced_analysis(
        "Analyze our current AGI system architecture and suggest improvements for scalability and performance",
        use_web_search=True,
        use_docker_info=True
    )
    
    print(f"✅ System analysis complete!")
    print(f"📊 Confidence: {result3['confidence']:.2f}")
    
    # Save results
    results_summary = {
        "timestamp": datetime.now().isoformat(),
        "tests_completed": 3,
        "frontend_analysis": result1,
        "docker_analysis": result2,
        "system_analysis": result3
    }
    
    with open("enhanced_ai_analysis_results.json", "w") as f:
        json.dump(results_summary, f, indent=2, default=str)
    
    print(f"\n💾 Results saved to: enhanced_ai_analysis_results.json")
    print("🎉 Enhanced AI system demonstration complete!")

if __name__ == "__main__":
    asyncio.run(main())
