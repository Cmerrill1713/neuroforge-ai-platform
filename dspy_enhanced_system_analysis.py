#!/usr/bin/env python3
"""
DSPy-Enhanced System Analysis
Uses DSPy optimization to help AI models better understand and work with existing systems
"""

import asyncio
import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.core.prompting.mipro_optimizer import MIPROPromptOptimizer, PromptExample, PromptOptimizationSettings
from src.core.agents import PromptAgentProfile

# Setup logging
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DSPyEnhancedSystemAnalysis:
    """Use DSPy to optimize prompts for better system understanding."""
    
    def __init__(self):
        self.conversation_log = []
        self.optimization_results = []
        self.models = [
            ("llama3.1:8b", "Lead Developer", "Coordinates implementation and writes core code"),
            ("qwen2.5:7b", "Frontend Developer", "Implements UI/UX improvements and frontend features"),
            ("mistral:7b", "Backend Developer", "Optimizes performance and implements backend enhancements"),
            ("phi3:3.8b", "Integration Specialist", "Connects components and ensures compatibility"),
            ("llama3.2:3b", "DevOps Engineer", "Handles deployment, containerization, and infrastructure")
        ]
        self.existing_system_info = self.gather_system_info()
        self.optimizer = MIPROPromptOptimizer()
    
    def gather_system_info(self) -> str:
        """Gather comprehensive information about our existing system."""
        
        system_info = """
EXISTING AGENTIC LLM CORE SYSTEM - COMPREHENSIVE ANALYSIS:

CORE ARCHITECTURE:
- FastAPI server (api_server.py) with REST API and WebSocket endpoints
- WebSocket support for real-time chat (/ws/chat)
- CORS middleware configured for frontend integration
- Built-in HTML test interface at /test endpoint
- Integration with EnhancedAgentSelector and KnowledgeBase
- Model routing and intelligent agent selection
- Parallel reasoning engine integration

EXISTING COMPONENTS TO BUILD UPON:
1. src/core/memory/vector_pg.py - PostgreSQL vector store with embeddings
2. src/core/engines/ollama_adapter.py - Ollama model integration with caching
3. src/core/tools/pydantic_ai_mcp.py - MCP tools with Pydantic AI validation
4. src/core/reasoning/parallel_reasoning_engine.py - Parallel reasoning capabilities
5. src/core/prompting/mipro_optimizer.py - DSPy MIPROv2 prompt optimization
6. api_server.py - Working FastAPI backend with all endpoints
7. configs/policies.yaml - Model routing and agent configuration
8. configs/agents.yaml - Agent profiles and capabilities

EXISTING FEATURES ALREADY WORKING:
- Intelligent agent selection with parallel reasoning
- Knowledge base integration with PostgreSQL vector store
- Real-time chat with streaming responses via WebSocket
- Model performance monitoring and switching
- MCP (Model Context Protocol) integration
- Multiple Ollama model support with routing
- DSPy prompt optimization capabilities
- Built-in test interface for all endpoints

TECHNICAL STACK ALREADY IMPLEMENTED:
- Python FastAPI backend with WebSocket support
- PostgreSQL with vector extensions for embeddings
- Ollama integration for local LLM models
- Pydantic AI for type-safe agent interactions
- DSPy MIPROv2 for prompt optimization
- HTML/CSS/JavaScript frontend with real-time capabilities

CURRENT CAPABILITIES:
- Chat with intelligent agent selection
- Knowledge base search and retrieval using vector embeddings
- System metrics and performance monitoring
- Model status checking and switching
- Real-time streaming responses
- Parallel reasoning for complex tasks
- Tool execution and monitoring via MCP
- Prompt optimization using DSPy

IMPORTANT: DO NOT BUILD NEW SYSTEMS - ENHANCE EXISTING ONES
"""
        return system_info
    
    def create_optimization_dataset(self) -> List[PromptExample]:
        """Create a dataset for optimizing prompts to work with existing systems."""
        
        return [
            PromptExample(
                input_text="Analyze the existing system and suggest improvements",
                expected_output="I will analyze the existing FastAPI backend, PostgreSQL vector store, Ollama adapter, and MCP integration. I'll suggest enhancements to api_server.py, improvements to the KnowledgeBase class, and optimizations to the OllamaAdapter caching. I will NOT suggest building new systems from scratch.",
                context="System analysis task",
                metadata={"task_type": "system_analysis", "focus": "existing_systems"}
            ),
            PromptExample(
                input_text="Design a new caching system",
                expected_output="I will enhance the existing OllamaAdapter caching in src/core/engines/ollama_adapter.py by adding Redis integration, improving cache invalidation, and optimizing memory usage. I will NOT suggest building a separate caching system.",
                context="Caching improvement task",
                metadata={"task_type": "caching", "focus": "enhance_existing"}
            ),
            PromptExample(
                input_text="Improve the knowledge base search",
                expected_output="I will enhance the existing KnowledgeBase class in src/core/memory/vector_pg.py by adding better search algorithms, improving PostgreSQL queries, and optimizing vector similarity search. I will NOT suggest replacing it with Elasticsearch.",
                context="Knowledge base task",
                metadata={"task_type": "knowledge_base", "focus": "enhance_existing"}
            ),
            PromptExample(
                input_text="Add new API endpoints",
                expected_output="I will add new endpoints to the existing api_server.py FastAPI application, integrating with the current WebSocket setup and existing agent selection system. I will NOT suggest building a separate API server.",
                context="API development task",
                metadata={"task_type": "api_development", "focus": "enhance_existing"}
            ),
            PromptExample(
                input_text="Optimize performance",
                expected_output="I will optimize the existing components: improve OllamaAdapter response times, enhance PostgreSQL vector queries, optimize WebSocket connections, and improve agent selection algorithms. I will NOT suggest replacing the entire system.",
                context="Performance optimization task",
                metadata={"task_type": "performance", "focus": "optimize_existing"}
            )
        ]
    
    async def optimize_model_prompts(self):
        """Use DSPy to optimize prompts for each model role."""
        
        print("🧠 DSPy Prompt Optimization for System Understanding")
        print("-" * 60)
        
        dataset = self.create_optimization_dataset()
        
        for model_name, role, expertise in self.models:
            print(f"🔧 Optimizing prompts for {role} ({model_name})...")
            
            # Create a profile for this role
            profile = PromptAgentProfile(
                name=f"{role.lower().replace(' ', '_')}",
                description=f"{role} with expertise in {expertise}",
                system_prompt=f"""You are {role} with expertise in: {expertise}

CRITICAL INSTRUCTION: You must work with EXISTING systems, not build new ones.

EXISTING SYSTEM COMPONENTS TO ENHANCE:
{self.existing_system_info}

YOUR APPROACH:
1. ANALYZE existing components and identify specific improvements
2. ENHANCE existing code rather than replacing it
3. INTEGRATE with current architecture and APIs
4. BUILD UPON existing capabilities
5. MAINTAIN compatibility with current system

NEVER suggest:
- Building new systems from scratch
- Replacing existing working components
- Creating parallel systems
- Ignoring existing architecture

ALWAYS suggest:
- Enhancing existing files and classes
- Improving current implementations
- Adding features to existing systems
- Optimizing current performance
- Extending existing capabilities""",
                capabilities=["system_analysis", "code_enhancement", "integration"],
                metadata={"role": role, "expertise": expertise}
            )
            
            try:
                # Optimize the prompt using DSPy
                optimized_profile, report = self.optimizer.optimize_profile(
                    profile=profile,
                    dataset=dataset,
                    settings=PromptOptimizationSettings(
                        auto="light",
                        max_bootstrapped_demos=3,
                        max_labeled_demos=2
                    )
                )
                
                self.optimization_results.append({
                    "model": model_name,
                    "role": role,
                    "original_prompt": profile.system_prompt,
                    "optimized_prompt": optimized_profile.system_prompt,
                    "score": report.score,
                    "report": report
                })
                
                print(f"✅ {role} prompt optimized (score: {report.score:.2f})")
                
            except Exception as e:
                print(f"❌ Failed to optimize {role}: {e}")
                # Use original prompt if optimization fails
                self.optimization_results.append({
                    "model": model_name,
                    "role": role,
                    "original_prompt": profile.system_prompt,
                    "optimized_prompt": profile.system_prompt,
                    "score": 0.0,
                    "report": None
                })
    
    async def run_enhanced_analysis(self):
        """Run system analysis with DSPy-optimized prompts."""
        
        print("🚀 DSPy-Enhanced System Analysis")
        print("=" * 60)
        print("Using DSPy-optimized prompts to better understand existing systems")
        print()
        
        # First optimize the prompts
        await self.optimize_model_prompts()
        
        # Then run analysis with optimized prompts
        await self.run_analysis_with_optimized_prompts()
        
        # Print results
        self.print_enhanced_results()
        
        # Save results
        self.save_enhanced_analysis()
    
    async def run_analysis_with_optimized_prompts(self):
        """Run analysis using the DSPy-optimized prompts."""
        
        print("\n🔍 Running Analysis with Optimized Prompts")
        print("-" * 50)
        
        for i, (model_name, role, expertise) in enumerate(self.models):
            # Get the optimized prompt for this model
            optimization_result = self.optimization_results[i]
            optimized_prompt = optimization_result["optimized_prompt"]
            
            prompt = f"""{optimized_prompt}

ANALYSIS TASK: Analyze our existing Agentic LLM Core system and suggest specific improvements.

EXISTING SYSTEM DETAILS:
{self.existing_system_info}

YOUR TASK: Provide specific, actionable improvements that enhance our existing system.

Format your response as:
**ROLE**: {role}
**EXISTING COMPONENTS ANALYZED**: [Which existing files/components you analyzed]
**SPECIFIC IMPROVEMENTS**: [Exact improvements to existing code]
**FILE MODIFICATIONS**: [Which existing files to modify and how]
**INTEGRATION APPROACH**: [How improvements integrate with existing system]
**CODE EXAMPLES**: [Specific code changes for existing files]

Focus on enhancing what we have, not building new systems."""

            response = await self.run_model(model_name, prompt)
            
            self.conversation_log.append({
                "model": model_name,
                "role": role,
                "optimized_prompt_used": True,
                "optimization_score": optimization_result["score"],
                "response": response,
                "timestamp": datetime.now().isoformat()
            })
            
            print(f"✅ {role} ({model_name}) completed enhanced analysis")
    
    async def run_model(self, model_name: str, prompt: str) -> str:
        """Run a model with the given prompt."""
        
        try:
            process = subprocess.Popen(
                ["ollama", "run", model_name, prompt],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            stdout, stderr = process.communicate()
            
            if process.returncode == 0:
                return stdout.strip()
            else:
                return f"Error: {stderr}"
                
        except Exception as e:
            return f"Error: {str(e)}"
    
    def print_enhanced_results(self):
        """Print the enhanced analysis results."""
        
        print("\n" + "="*80)
        print("🧠 DSPy-Enhanced System Analysis Results")
        print("="*80)
        
        print("\n📊 Prompt Optimization Results:")
        print("-" * 40)
        for result in self.optimization_results:
            print(f"🤖 {result['role']} ({result['model']})")
            print(f"   Optimization Score: {result['score']:.2f}")
            print(f"   Prompt Enhanced: {'Yes' if result['score'] > 0 else 'No'}")
            print()
        
        print("\n🔍 Enhanced Analysis Results:")
        print("-" * 40)
        for entry in self.conversation_log:
            print(f"\n🎯 {entry['role']} ({entry['model']})")
            print(f"   Optimization Score: {entry['optimization_score']:.2f}")
            print("-" * 60)
            print(entry['response'])
            print()
    
    def save_enhanced_analysis(self):
        """Save the enhanced analysis results."""
        
        analysis_data = {
            "timestamp": datetime.now().isoformat(),
            "optimization_results": self.optimization_results,
            "conversation_log": self.conversation_log,
            "existing_system_info": self.existing_system_info
        }
        
        with open("dspy_enhanced_system_analysis.json", "w") as f:
            json.dump(analysis_data, f, indent=2)
        
        print("💾 Enhanced analysis saved to dspy_enhanced_system_analysis.json")

async def main():
    """Main function."""
    
    analysis = DSPyEnhancedSystemAnalysis()
    await analysis.run_enhanced_analysis()
    
    print("\n🎉 DSPy-enhanced system analysis completed!")
    print("📄 Results saved to dspy_enhanced_system_analysis.json")

if __name__ == "__main__":
    asyncio.run(main())
