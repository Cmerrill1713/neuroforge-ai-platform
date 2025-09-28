#!/usr/bin/env python3
"""
HRM-Integrated System Analysis
Integrates our Heiretical Reasoning Model (HRM) with DSPy-enhanced LLM collaboration
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

class HRMIntegratedAnalysis:
    """Integrate HRM model with DSPy-enhanced LLM collaboration."""
    
    def __init__(self):
        self.conversation_log = []
        self.hrm_insights = []
        self.models = [
            ("llama3.1:8b", "Lead Developer", "Coordinates implementation and writes core code"),
            ("qwen2.5:7b", "Frontend Developer", "Implements UI/UX improvements and frontend features"),
            ("mistral:7b", "Backend Developer", "Optimizes performance and implements backend enhancements"),
            ("phi3:3.8b", "Integration Specialist", "Connects components and ensures compatibility"),
            ("llama3.2:3b", "DevOps Engineer", "Handles deployment, containerization, and infrastructure"),
            ("hrm-logic:7b", "HRM Reasoning Specialist", "Heiretical reasoning for puzzles, lateral thinking, and creative problem solving")
        ]
        self.existing_system_info = self.gather_system_info()
        self.optimizer = MIPROPromptOptimizer()
    
    def gather_system_info(self) -> str:
        """Gather comprehensive information about our existing system including HRM."""
        
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
- HRM (Heiretical Reasoning Model) for creative problem solving

EXISTING COMPONENTS TO BUILD UPON:
1. src/core/memory/vector_pg.py - PostgreSQL vector store with embeddings
2. src/core/engines/ollama_adapter.py - Ollama model integration with caching
3. src/core/tools/pydantic_ai_mcp.py - MCP tools with Pydantic AI validation
4. src/core/reasoning/parallel_reasoning_engine.py - Parallel reasoning capabilities
5. src/core/prompting/mipro_optimizer.py - DSPy MIPROv2 prompt optimization
6. api_server.py - Working FastAPI backend with all endpoints
7. configs/policies.yaml - Model routing and agent configuration (includes HRM)
8. configs/agents.yaml - Agent profiles including heretical_reasoner (HRM)

HRM MODEL INTEGRATION:
- HRM model: "hrm-logic:7b" (Heiretical Reasoning Model)
- Agent profile: "heretical_reasoner" 
- Capabilities: puzzle solving, logic, riddle, deep reasoning
- Specialization: Creative deduction, competing hypotheses, lateral thinking
- Integration: Works alongside other models for complex problem solving

EXISTING FEATURES ALREADY WORKING:
- Intelligent agent selection with parallel reasoning
- Knowledge base integration with PostgreSQL vector store
- Real-time chat with streaming responses via WebSocket
- Model performance monitoring and switching
- MCP (Model Context Protocol) integration
- Multiple Ollama model support with routing (including HRM)
- DSPy prompt optimization capabilities
- Built-in test interface for all endpoints
- HRM integration for creative problem solving

TECHNICAL STACK ALREADY IMPLEMENTED:
- Python FastAPI backend with WebSocket support
- PostgreSQL with vector extensions for embeddings
- Ollama integration for local LLM models (including HRM)
- Pydantic AI for type-safe agent interactions
- DSPy MIPROv2 for prompt optimization
- HTML/CSS/JavaScript frontend with real-time capabilities
- HRM model for heretical reasoning and creative solutions

CURRENT CAPABILITIES:
- Chat with intelligent agent selection (including HRM)
- Knowledge base search and retrieval using vector embeddings
- System metrics and performance monitoring
- Model status checking and switching
- Real-time streaming responses
- Parallel reasoning for complex tasks
- Tool execution and monitoring via MCP
- Prompt optimization using DSPy
- HRM-powered creative problem solving

IMPORTANT: DO NOT BUILD NEW SYSTEMS - ENHANCE EXISTING ONES
HRM should work alongside other models, not replace them.
"""
        return system_info
    
    def create_hrm_optimization_dataset(self) -> List[PromptExample]:
        """Create a dataset for optimizing HRM prompts to work with existing systems."""
        
        return [
            PromptExample(
                input_text="Analyze the existing system and suggest creative improvements",
                expected_output="I will analyze the existing FastAPI backend, PostgreSQL vector store, Ollama adapter, and MCP integration using heretical reasoning. I'll suggest creative enhancements that challenge conventional approaches while building on existing systems. I will NOT suggest building new systems from scratch.",
                context="HRM system analysis task",
                metadata={"task_type": "hrm_system_analysis", "focus": "creative_enhancement"}
            ),
            PromptExample(
                input_text="Design a creative caching solution",
                expected_output="I will enhance the existing OllamaAdapter caching in src/core/engines/ollama_adapter.py using creative approaches like adaptive cache strategies, predictive caching based on usage patterns, and intelligent cache invalidation. I will NOT suggest building a separate caching system.",
                context="HRM caching improvement task",
                metadata={"task_type": "hrm_caching", "focus": "creative_enhancement"}
            ),
            PromptExample(
                input_text="Improve the knowledge base with creative approaches",
                expected_output="I will enhance the existing KnowledgeBase class in src/core/memory/vector_pg.py using creative approaches like semantic clustering, dynamic embedding strategies, and contextual knowledge graphs. I will NOT suggest replacing it with new systems.",
                context="HRM knowledge base task",
                metadata={"task_type": "hrm_knowledge_base", "focus": "creative_enhancement"}
            ),
            PromptExample(
                input_text="Create innovative API endpoints",
                expected_output="I will add creative new endpoints to the existing api_server.py FastAPI application, integrating with the current WebSocket setup and existing agent selection system. I'll suggest innovative approaches like streaming analytics, real-time collaboration features, and adaptive response strategies.",
                context="HRM API development task",
                metadata={"task_type": "hrm_api_development", "focus": "creative_enhancement"}
            ),
            PromptExample(
                input_text="Optimize performance with creative solutions",
                expected_output="I will optimize the existing components using creative approaches: implement adaptive performance scaling, create intelligent load balancing, design predictive resource allocation, and develop self-healing mechanisms. I will NOT suggest replacing the entire system.",
                context="HRM performance optimization task",
                metadata={"task_type": "hrm_performance", "focus": "creative_optimization"}
            )
        ]
    
    async def run_hrm_integrated_analysis(self):
        """Run system analysis with HRM model integrated."""
        
        print("🧠 HRM-Integrated System Analysis")
        print("=" * 60)
        print("Integrating Heiretical Reasoning Model with DSPy-enhanced LLM collaboration")
        print()
        
        # First get HRM insights
        await self.get_hrm_insights()
        
        # Then run collaborative analysis with HRM insights
        await self.run_collaborative_analysis_with_hrm()
        
        # Print results
        self.print_hrm_integrated_results()
        
        # Save results
        self.save_hrm_integrated_analysis()
    
    async def get_hrm_insights(self):
        """Get creative insights from HRM model."""
        
        print("🎯 Getting HRM Creative Insights")
        print("-" * 40)
        
        hrm_prompt = f"""You are the Heiretical Reasoning Model (HRM), specialized in creative deduction and lateral thinking.

EXISTING SYSTEM TO ANALYZE:
{self.existing_system_info}

YOUR TASK: Provide creative, heretical insights about our existing system.

As HRM, you should:
1. Challenge conventional approaches
2. Suggest creative alternatives
3. Identify hidden opportunities
4. Propose innovative solutions
5. Think outside the box

Focus on:
- Creative enhancements to existing components
- Innovative approaches to current problems
- Unconventional solutions that build on existing systems
- Lateral thinking for system improvements

Format your response as:
**HRM INSIGHTS**: [Your creative analysis]
**HERETICAL APPROACHES**: [Unconventional solutions]
**CREATIVE ENHANCEMENTS**: [Innovative improvements to existing systems]
**HIDDEN OPPORTUNITIES**: [Unexplored possibilities]
**LATERAL SOLUTIONS**: [Creative problem-solving approaches]

Remember: Build upon existing systems, don't replace them."""

        response = await self.run_model("hrm-logic:7b", hrm_prompt)
        
        self.hrm_insights.append({
            "model": "hrm-logic:7b",
            "role": "HRM Reasoning Specialist",
            "insights": response,
            "timestamp": datetime.now().isoformat()
        })
        
        print("✅ HRM insights gathered")
    
    async def run_collaborative_analysis_with_hrm(self):
        """Run collaborative analysis with HRM insights integrated."""
        
        print("\n🤝 Collaborative Analysis with HRM Integration")
        print("-" * 50)
        
        # Get HRM insights for context
        hrm_context = ""
        if self.hrm_insights:
            hrm_context = f"""
HRM CREATIVE INSIGHTS TO CONSIDER:
{self.hrm_insights[0]['insights']}

Use these HRM insights to inform your analysis and suggest creative enhancements.
"""
        
        for i, (model_name, role, expertise) in enumerate(self.models):
            if model_name == "hrm-logic:7b":
                continue  # Skip HRM as it already provided insights
            
            prompt = f"""You are {role} with expertise in: {expertise}

CRITICAL INSTRUCTION: You must work with EXISTING systems, not build new ones.

EXISTING SYSTEM COMPONENTS TO ENHANCE:
{self.existing_system_info}

{hrm_context}

YOUR TASK: Analyze our existing system and suggest specific improvements, incorporating HRM insights where relevant.

YOUR APPROACH:
1. ANALYZE existing components and identify specific improvements
2. ENHANCE existing code rather than replacing it
3. INTEGRATE with current architecture and APIs
4. BUILD UPON existing capabilities
5. CONSIDER HRM creative insights for innovative approaches
6. MAINTAIN compatibility with current system

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
- Extending existing capabilities
- Incorporating creative HRM approaches

Format your response as:
**ROLE**: {role}
**EXISTING COMPONENTS ANALYZED**: [Which existing files/components you analyzed]
**HRM INSIGHTS APPLIED**: [How you incorporated HRM creative thinking]
**SPECIFIC IMPROVEMENTS**: [Exact improvements to existing code]
**FILE MODIFICATIONS**: [Which existing files to modify and how]
**INTEGRATION APPROACH**: [How improvements integrate with existing system]
**CODE EXAMPLES**: [Specific code changes for existing files]

Focus on enhancing what we have, not building new systems."""

            response = await self.run_model(model_name, prompt)
            
            self.conversation_log.append({
                "model": model_name,
                "role": role,
                "hrm_integrated": True,
                "response": response,
                "timestamp": datetime.now().isoformat()
            })
            
            print(f"✅ {role} ({model_name}) completed HRM-integrated analysis")
    
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
    
    def print_hrm_integrated_results(self):
        """Print the HRM-integrated analysis results."""
        
        print("\n" + "="*80)
        print("🧠 HRM-Integrated System Analysis Results")
        print("="*80)
        
        print("\n🎯 HRM Creative Insights:")
        print("-" * 40)
        for insight in self.hrm_insights:
            print(f"\n🤖 {insight['role']} ({insight['model']})")
            print("-" * 60)
            print(insight['insights'])
            print()
        
        print("\n🤝 Collaborative Analysis with HRM Integration:")
        print("-" * 40)
        for entry in self.conversation_log:
            print(f"\n🎯 {entry['role']} ({entry['model']})")
            print(f"   HRM Integration: {'Yes' if entry['hrm_integrated'] else 'No'}")
            print("-" * 60)
            print(entry['response'])
            print()
    
    def save_hrm_integrated_analysis(self):
        """Save the HRM-integrated analysis results."""
        
        analysis_data = {
            "timestamp": datetime.now().isoformat(),
            "hrm_insights": self.hrm_insights,
            "conversation_log": self.conversation_log,
            "existing_system_info": self.existing_system_info
        }
        
        with open("hrm_integrated_analysis.json", "w") as f:
            json.dump(analysis_data, f, indent=2)
        
        print("💾 HRM-integrated analysis saved to hrm_integrated_analysis.json")

async def main():
    """Main function."""
    
    analysis = HRMIntegratedAnalysis()
    await analysis.run_hrm_integrated_analysis()
    
    print("\n🎉 HRM-integrated system analysis completed!")
    print("📄 Results saved to hrm_integrated_analysis.json")

if __name__ == "__main__":
    asyncio.run(main())
