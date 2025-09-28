"""
Integration Script for Agentic LLM Core v2.0 Advanced Features

This script integrates all the new advanced features:
- Vector Database (ChromaDB) for advanced RAG
- SSO Authentication System
- RBAC (Role-Based Access Control)
- Advanced Prompt Optimization Tools

Created: 2024-09-28
Status: Production Ready
"""

import asyncio
import logging
import sys
from pathlib import Path
from typing import Dict, Any, Optional

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from core.rag.vector_database import VectorDatabase, AdvancedRAGSystem, Document, DocumentType
from core.auth.sso_system import AuthenticationService, UserCreate, LoginRequest, UserRole
from core.auth.rbac_system import RBACSystem, AccessRequest, ResourceType, Permission
from core.prompts.optimization_tools import PromptOptimizationEngine, PromptCategory, PromptType

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class AgenticLLMCoreIntegration:
    """Main integration class for all advanced features."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Initialize all systems
        self.vector_db = VectorDatabase()
        self.rag_system = AdvancedRAGSystem(self.vector_db)
        self.auth_service = AuthenticationService()
        self.rbac_system = RBACSystem()
        self.prompt_engine = PromptOptimizationEngine()
        
        self.logger.info("🚀 Agentic LLM Core Integration initialized")
    
    async def initialize_systems(self):
        """Initialize all systems with default data."""
        self.logger.info("🔧 Initializing systems with default data...")
        
        # Add some default knowledge to the vector database
        await self._add_default_knowledge()
        
        # Create some default users
        await self._create_default_users()
        
        # Create some default prompts
        await self._create_default_prompts()
        
        self.logger.info("✅ All systems initialized successfully")
    
    async def _add_default_knowledge(self):
        """Add default knowledge to the vector database."""
        knowledge_items = [
            {
                "title": "Agentic LLM Core Overview",
                "content": "Agentic LLM Core is an advanced AI system that combines multiple AI agents, self-improvement capabilities, and enterprise-grade features. It includes agent selection, parallel reasoning, monitoring, and optimization systems.",
                "category": DocumentType.KNOWLEDGE_BASE
            },
            {
                "title": "Agent Selection System",
                "content": "The agent selection system intelligently chooses the best AI agent for each task based on task type, complexity, and performance requirements. It supports multiple agents including generalist, codesmith, analyst, and specialized reasoning agents.",
                "category": DocumentType.KNOWLEDGE_BASE
            },
            {
                "title": "MLX Integration",
                "content": "MLX integration provides Apple Silicon optimization for local AI models. It supports Qwen3-30B and DIA-1.6B models with 4-bit quantization for efficient local execution.",
                "category": DocumentType.KNOWLEDGE_BASE
            },
            {
                "title": "Self-Improvement System",
                "content": "The self-improvement system continuously monitors performance and automatically optimizes the system. It includes intelligent monitoring, performance degradation detection, and autonomous optimization capabilities.",
                "category": DocumentType.KNOWLEDGE_BASE
            },
            {
                "title": "Vector Database Features",
                "content": "The vector database provides advanced RAG capabilities with ChromaDB integration. It supports semantic search, document chunking, and retrieval optimization for enhanced knowledge management.",
                "category": DocumentType.KNOWLEDGE_BASE
            }
        ]
        
        for item in knowledge_items:
            await self.rag_system.add_knowledge(
                title=item["title"],
                content=item["content"],
                document_type=item["category"]
            )
        
        self.logger.info(f"Added {len(knowledge_items)} knowledge items to vector database")
    
    async def _create_default_users(self):
        """Create default users for testing."""
        users_to_create = [
            {
                "username": "testuser",
                "email": "test@agentic-llm.local",
                "password": "test123",
                "full_name": "Test User",
                "role": UserRole.USER
            },
            {
                "username": "analyst",
                "email": "analyst@agentic-llm.local",
                "password": "analyst123",
                "full_name": "Data Analyst",
                "role": UserRole.ANALYST
            }
        ]
        
        for user_data in users_to_create:
            try:
                user_create = UserCreate(**user_data)
                await self.auth_service.user_manager.create_user(user_create)
                self.logger.info(f"Created user: {user_data['username']}")
            except Exception as e:
                self.logger.warning(f"User {user_data['username']} may already exist: {e}")
    
    async def _create_default_prompts(self):
        """Create default prompts for testing."""
        prompts_to_create = [
            {
                "name": "Enterprise Assistant",
                "description": "Enterprise-grade AI assistant with security and compliance focus",
                "category": PromptCategory.GENERAL,
                "content": "You are an enterprise AI assistant. Provide accurate, secure, and compliant responses. Always consider security implications and follow enterprise policies.",
                "tags": ["enterprise", "security", "compliance"]
            },
            {
                "name": "Research Assistant",
                "description": "Specialized research and analysis assistant",
                "category": PromptCategory.ANALYSIS,
                "content": "You are a research assistant. Conduct thorough analysis, cite sources, and provide evidence-based conclusions. Always verify information and present balanced perspectives.",
                "tags": ["research", "analysis", "evidence"]
            },
            {
                "name": "Code Review Assistant",
                "description": "Code review and quality assurance assistant",
                "category": PromptCategory.CODING,
                "content": "You are a code review assistant. Analyze code for quality, security, performance, and best practices. Provide specific, actionable feedback with examples.",
                "tags": ["code", "review", "quality", "security"]
            }
        ]
        
        for prompt_data in prompts_to_create:
            await self.prompt_engine.create_prompt(
                name=prompt_data["name"],
                description=prompt_data["description"],
                category=prompt_data["category"],
                content=prompt_data["content"],
                tags=prompt_data["tags"]
            )
            self.logger.info(f"Created prompt: {prompt_data['name']}")
    
    async def demonstrate_features(self):
        """Demonstrate all the advanced features."""
        self.logger.info("🎯 Demonstrating advanced features...")
        
        # 1. Demonstrate Vector Database / RAG
        await self._demonstrate_rag()
        
        # 2. Demonstrate Authentication
        await self._demonstrate_auth()
        
        # 3. Demonstrate RBAC
        await self._demonstrate_rbac()
        
        # 4. Demonstrate Prompt Optimization
        await self._demonstrate_prompt_optimization()
        
        self.logger.info("✅ Feature demonstration completed")
    
    async def _demonstrate_rag(self):
        """Demonstrate RAG capabilities."""
        self.logger.info("🔍 Demonstrating RAG capabilities...")
        
        # Search for information about agents
        results = await self.rag_system.retrieve_relevant_context("Tell me about agent selection", limit=3)
        
        print("\n📚 RAG Search Results:")
        print("=" * 50)
        for i, result in enumerate(results, 1):
            print(f"\n{i}. Similarity: {result.similarity_score:.3f}")
            print(f"   Content: {result.content[:150]}...")
            print(f"   Source: {result.document_title}")
        
        # Generate contextual response
        context_response = await self.rag_system.generate_contextual_response("How does the agent selection work?")
        
        print(f"\n🤖 Contextual Response:")
        print(f"   Context Sources: {len(context_response['context_sources'])}")
        print(f"   Context Count: {context_response['context_count']}")
        print(f"   Context Preview: {context_response['context'][:200]}...")
    
    async def _demonstrate_auth(self):
        """Demonstrate authentication capabilities."""
        self.logger.info("🔐 Demonstrating authentication...")
        
        # Login as test user
        login_request = LoginRequest(username="analyst", password="analyst123")
        token = await self.auth_service.login(login_request)
        
        print(f"\n🔑 Authentication Demo:")
        print(f"   Access Token: {token.access_token[:50]}...")
        print(f"   Token Type: {token.token_type}")
        print(f"   Expires In: {token.expires_in} seconds")
        
        # Verify token
        user = await self.auth_service.get_current_user(token.access_token)
        if user:
            print(f"   Verified User: {user.username} ({user.role.value})")
            print(f"   User Status: {user.status.value}")
        
        # Demonstrate OAuth (mock)
        oauth_url = await self.auth_service.oauth_manager.get_oauth_url("google")
        print(f"   OAuth URL: {oauth_url[:100]}...")
    
    async def _demonstrate_rbac(self):
        """Demonstrate RBAC capabilities."""
        self.logger.info("🛡️ Demonstrating RBAC...")
        
        # Get user role
        user_role = await self.rbac_system.get_role_by_name("user")
        if user_role:
            print(f"\n👤 RBAC Demo:")
            print(f"   Role: {user_role.name}")
            print(f"   Permissions: {len(user_role.permissions)}")
            print(f"   Sample Permissions: {', '.join(list(user_role.permissions)[:5])}")
            
            # Test access control
            access_request = AccessRequest(
                user_id="analyst",
                resource_type=ResourceType.AGENT,
                permission=Permission.AGENT_EXECUTE
            )
            
            decision = await self.rbac_system.check_access(access_request, user_role)
            print(f"   Access to AGENT_EXECUTE: {'✅ Granted' if decision.granted else '❌ Denied'}")
            print(f"   Reason: {decision.reason}")
        
        # Show system stats
        stats = await self.rbac_system.get_system_stats()
        print(f"   System Roles: {stats['total_roles']}")
        print(f"   System Resources: {stats['total_resources']}")
        print(f"   Audit Logs: {stats['total_audit_logs']}")
    
    async def _demonstrate_prompt_optimization(self):
        """Demonstrate prompt optimization capabilities."""
        self.logger.info("⚡ Demonstrating prompt optimization...")
        
        # Get a prompt
        prompts = list(self.prompt_engine.prompts.values())
        if prompts:
            prompt = prompts[0]
            
            print(f"\n🎯 Prompt Optimization Demo:")
            print(f"   Prompt: {prompt.name}")
            print(f"   Category: {prompt.category.value}")
            print(f"   Usage Count: {prompt.usage_count}")
            print(f"   Success Rate: {prompt.success_rate:.1%}")
            
            # Execute the prompt
            execution = await self.prompt_engine.execute_prompt(
                prompt.prompt_id,
                {"query": "What is artificial intelligence?"}
            )
            
            print(f"   Execution Success: {execution.success}")
            print(f"   Response Time: {execution.response_time:.3f}s")
            print(f"   Quality Score: {execution.quality_score}")
            
            # Generate optimization suggestions
            suggestions = await self.prompt_engine.generate_optimization_suggestions(prompt.prompt_id)
            print(f"   Optimization Suggestions: {len(suggestions)}")
            
            for i, suggestion in enumerate(suggestions[:2], 1):
                print(f"     {i}. {suggestion.strategy.value}: {suggestion.improvement_reason}")
                print(f"        Expected Improvement: {suggestion.expected_improvement:.1%}")
        
        # Show system stats
        stats = await self.prompt_engine.get_system_stats()
        print(f"   Total Prompts: {stats['total_prompts']}")
        print(f"   Total Executions: {stats['total_executions']}")
        print(f"   Active A/B Tests: {stats['active_ab_tests']}")
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status."""
        return {
            "vector_database": {
                "status": "operational",
                "total_documents": len(self.vector_db.collection.get()['ids']) if hasattr(self.vector_db, 'collection') else 0
            },
            "authentication": {
                "status": "operational",
                "total_users": len(self.auth_service.user_manager.users),
                "active_sessions": len(self.auth_service.user_manager.sessions)
            },
            "rbac": {
                "status": "operational",
                "total_roles": len(self.rbac_system.roles),
                "total_resources": len(self.rbac_system.resources),
                "audit_logs": len(self.rbac_system.audit_logs)
            },
            "prompt_optimization": {
                "status": "operational",
                "total_prompts": len(self.prompt_engine.prompts),
                "total_executions": len(self.prompt_engine.executions),
                "active_tests": len([t for t in self.prompt_engine.ab_tests.values() if t.status.value == "running"])
            }
        }


# ============================================================================
# Main Function
# ============================================================================

async def main():
    """Main function to run the integration demo."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Agentic LLM Core Integration Demo")
    parser.add_argument("--action", choices=["init", "demo", "status"], default="demo", help="Action to perform")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    try:
        # Initialize integration
        integration = AgenticLLMCoreIntegration()
        
        if args.action == "init":
            print("🔧 Initializing Agentic LLM Core Advanced Features...")
            await integration.initialize_systems()
            print("✅ Initialization completed successfully!")
            
        elif args.action == "demo":
            print("🎯 Running Agentic LLM Core Advanced Features Demo...")
            print("=" * 60)
            
            await integration.demonstrate_features()
            
            print("\n" + "=" * 60)
            print("🎉 Demo completed successfully!")
            
        elif args.action == "status":
            print("📊 Agentic LLM Core System Status:")
            print("=" * 40)
            
            status = await integration.get_system_status()
            
            for system, info in status.items():
                print(f"\n{system.replace('_', ' ').title()}:")
                for key, value in info.items():
                    print(f"  {key}: {value}")
        
        return 0
        
    except Exception as e:
        logger.error(f"Integration demo failed: {e}")
        return 1


if __name__ == "__main__":
    exit(asyncio.run(main()))
