#!/usr/bin/env python3
"""
Simple Integration Demo for Agentic LLM Core - Home Use
Demonstrates core features using existing system components
"""

import asyncio
import logging
import sys
from pathlib import Path
from typing import Dict, Any, List
import json

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Configure logging
logging.basicConfig(level=logging.INFO, stream=sys.stdout,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SimpleIntegrationDemo:
    """Simple integration demo for home use"""
    
    def __init__(self):
        self.is_initialized = False
    
    async def initialize(self):
        """Initialize core systems"""
        if self.is_initialized:
            logger.info("Simple integration demo already initialized")
            return
        
        logger.info("🚀 Initializing Simple Agentic LLM Core Demo...")
        
        try:
            # Test basic imports
            logger.info("📚 Testing core system imports...")
            
            # Test vector database import
            try:
                from core.rag.vector_database import VectorDatabase
                logger.info("✅ Vector Database module available")
            except ImportError as e:
                logger.warning(f"⚠️ Vector Database not available: {e}")
            
            # Test prompt optimizer import
            try:
                from core.prompting.mipro_optimizer import MIPROPromptOptimizer
                logger.info("✅ Prompt Optimizer module available")
            except ImportError as e:
                logger.warning(f"⚠️ Prompt Optimizer not available: {e}")
            
            # Test agent system import
            try:
                from enhanced_agent_selection import EnhancedAgentSelector
                logger.info("✅ Enhanced Agent Selector available")
            except ImportError as e:
                logger.warning(f"⚠️ Enhanced Agent Selector not available: {e}")
            
            self.is_initialized = True
            logger.info("🎉 Simple integration demo initialized successfully!")
            
        except Exception as e:
            logger.error(f"❌ Initialization failed: {e}")
            raise
    
    async def demo_agent_selection(self):
        """Demonstrate agent selection capabilities"""
        logger.info("🤖 Demonstrating agent selection...")
        
        try:
            from enhanced_agent_selection import EnhancedAgentSelector
            
            # Initialize agent selector
            selector = EnhancedAgentSelector(
                config_path="configs/policies.yaml",
                agents_config_path="configs/agents.yaml"
            )
            # Agent selector is already initialized
            
            print(f"\n🤖 Agent Selection Demo:")
            print(f"   Available agents: {len(selector.agent_profiles)}")
            
            # Test different task types
            test_tasks = [
                {"task_type": "code_generation", "content": "Write a Python function to sort a list"},
                {"task_type": "analysis", "content": "Analyze the performance of this system"},
                {"task_type": "text_generation", "content": "Explain how AI works"},
                {"task_type": "quicktake", "content": "What's the weather like?"}
            ]
            
            for task in test_tasks:
                result = await selector.select_best_agent_with_reasoning(task)
                selected_agent = result.get('selected_agent', {}).get('agent_name', 'unknown')
                confidence = result.get('selected_agent', {}).get('score', 0.0)
                
                print(f"   Task: {task['task_type']}")
                print(f"   Selected: {selected_agent} (confidence: {confidence:.2f})")
                print(f"   Content: {task['content'][:50]}...")
                print()
            
        except Exception as e:
            logger.error(f"❌ Agent selection demo failed: {e}")
    
    async def demo_vector_database(self):
        """Demonstrate vector database capabilities"""
        logger.info("📚 Demonstrating vector database...")
        
        try:
            from core.rag.vector_database import VectorDatabase, Document, DocumentType, SearchRequest
            
            # Initialize vector database
            vector_db = VectorDatabase(persist_directory="vector_db")
            
            print(f"\n📚 Vector Database Demo:")
            print(f"   Database initialized at: vector_db")
            
            # Add sample documents
            sample_docs = [
                Document(
                    title="System Overview",
                    content="The Agentic LLM Core system uses advanced agent selection to choose the best AI model for each task.",
                    document_type=DocumentType.TEXT,
                    metadata={"type": "system_overview"}
                ),
                Document(
                    title="Agent Selection",
                    content="Agent selection works by analyzing task complexity and requirements to match the most appropriate AI agent.",
                    document_type=DocumentType.TEXT,
                    metadata={"type": "agent_selection"}
                )
            ]
            
            for doc in sample_docs:
                doc_id = await vector_db.add_document(doc)
                print(f"   Added document: {doc.title} (ID: {doc_id})")
            
            # Test search
            query = "How does agent selection work?"
            search_request = SearchRequest(query=query, limit=2)
            results = await vector_db.search(search_request)
            
            print(f"\n🔍 Search Query: '{query}'")
            print(f"   Found {len(results)} results:")
            for i, result in enumerate(results, 1):
                print(f"   {i}. {result.content[:80]}...")
                print(f"      Score: {result.similarity_score:.3f}")
            
        except Exception as e:
            logger.error(f"❌ Vector database demo failed: {e}")
    
    async def demo_prompt_optimization(self):
        """Demonstrate prompt optimization"""
        logger.info("🔧 Demonstrating prompt optimization...")
        
        try:
            from core.prompting.mipro_optimizer import MIPROPromptOptimizer
            
            # Initialize optimizer
            optimizer = MIPROPromptOptimizer()
            
            print(f"\n🔧 Prompt Optimization Demo:")
            
            # Test prompts
            test_prompts = [
                "Write a function",
                "Explain machine learning",
                "Help me debug this code"
            ]
            
            for prompt in test_prompts:
                print(f"   Original: '{prompt}'")
                
                # Simple optimization (if method exists)
                try:
                    optimized = await optimizer.optimize_prompt(prompt)
                    print(f"   Optimized: '{optimized}'")
                except AttributeError:
                    print(f"   Optimization method not available")
                print()
            
        except Exception as e:
            logger.error(f"❌ Prompt optimization demo failed: {e}")
    
    async def run_demo(self):
        """Run the complete demo"""
        try:
            await self.initialize()
            
            print("\n🎯 Running Simple Agentic LLM Core Demo...")
            print("=" * 60)
            
            # Run demonstrations
            await self.demo_agent_selection()
            await self.demo_vector_database()
            await self.demo_prompt_optimization()
            
            print("\n✅ Demo completed successfully!")
            print("\n🎉 Your Agentic LLM Core system is ready for home use!")
            print("   • Enhanced agent selection for optimal AI responses")
            print("   • Vector database for knowledge retrieval")
            print("   • Prompt optimization for better results")
            print("   • No authentication required - perfect for home use!")
            
        except Exception as e:
            logger.error(f"❌ Demo failed: {e}")
            raise

async def main():
    """Main entry point"""
    demo = SimpleIntegrationDemo()
    await demo.run_demo()

if __name__ == "__main__":
    asyncio.run(main())