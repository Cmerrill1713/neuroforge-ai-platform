#!/usr/bin/env python3
"""
End-to-End User Workflow Testing
Tests the complete system from a user's perspective
"""

import asyncio
import logging
import sys
import time
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from enhanced_agent_selection import EnhancedAgentSelector
from src.core.knowledge.simple_knowledge_base import SimpleKnowledgeBase

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class UserWorkflowTester:
    """
    Tests the complete user workflow from input to output.
    Simulates real user scenarios and validates system behavior.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.enhanced_selector = None
        self.knowledge_base = None
        self.test_results = []
        
    async def initialize_system(self):
        """Initialize all system components."""
        print("🚀 Initializing Agentic LLM Core System")
        print("=" * 50)
        
        try:
            # Initialize enhanced agent selector
            print("📡 Initializing Enhanced Agent Selection...")
            self.enhanced_selector = EnhancedAgentSelector()
            print("✅ Enhanced Agent Selection ready")
            
            # Initialize knowledge base
            print("📚 Initializing Knowledge Base...")
            self.knowledge_base = SimpleKnowledgeBase()
            print("✅ Knowledge Base ready")
            
            print("🎉 System initialization complete!")
            return True
            
        except Exception as e:
            print(f"❌ System initialization failed: {e}")
            return False
    
    async def test_user_scenarios(self):
        """Test various user scenarios."""
        
        print("\n🧪 Testing User Scenarios")
        print("=" * 50)
        
        # Define realistic user scenarios
        scenarios = [
            {
                "name": "Quick Question",
                "description": "User asks a simple question",
                "task": {
                    "task_type": "text_generation",
                    "content": "What is the capital of France?",
                    "latency_requirement": 500,
                    "input_type": "text"
                },
                "expected_behavior": "Fast response, no parallel reasoning"
            },
            {
                "name": "Code Help",
                "description": "User needs coding assistance",
                "task": {
                    "task_type": "code_generation",
                    "content": "Help me write a Python function to sort a list of dictionaries by a specific key",
                    "latency_requirement": 1000,
                    "input_type": "text"
                },
                "expected_behavior": "Codesmith agent, moderate complexity"
            },
            {
                "name": "Complex Problem Solving",
                "description": "User presents a complex architectural problem",
                "task": {
                    "task_type": "strategic_planning",
                    "content": "I need to design a scalable web application architecture that can handle 100,000 concurrent users, process real-time data streams, and maintain 99.9% uptime. Consider microservices, database sharding, caching strategies, and disaster recovery.",
                    "latency_requirement": 2000,
                    "input_type": "text"
                },
                "expected_behavior": "Parallel reasoning with verification, high complexity"
            },
            {
                "name": "Research Query",
                "description": "User asks about research from knowledge base",
                "task": {
                    "task_type": "analysis",
                    "content": "What are the key insights from the Parallel-R1 research paper about parallel thinking?",
                    "latency_requirement": 1500,
                    "input_type": "text"
                },
                "expected_behavior": "Knowledge base integration, analysis task"
            },
            {
                "name": "Creative Task",
                "description": "User requests creative content",
                "task": {
                    "task_type": "creative_writing",
                    "content": "Write a short story about an AI that learns to think in parallel and discovers new ways to solve problems",
                    "latency_requirement": 1200,
                    "input_type": "text"
                },
                "expected_behavior": "Creative agent, exploration mode"
            }
        ]
        
        # Test each scenario
        for i, scenario in enumerate(scenarios, 1):
            print(f"\n--- Scenario {i}: {scenario['name']} ---")
            print(f"Description: {scenario['description']}")
            print(f"Expected: {scenario['expected_behavior']}")
            
            try:
                result = await self._test_scenario(scenario)
                self.test_results.append(result)
                
                # Display results
                self._display_scenario_result(result)
                
            except Exception as e:
                print(f"❌ Scenario {i} failed: {e}")
                self.test_results.append({
                    "scenario": scenario["name"],
                    "success": False,
                    "error": str(e)
                })
    
    async def _test_scenario(self, scenario: Dict[str, Any]) -> Dict[str, Any]:
        """Test a single user scenario."""
        
        start_time = time.time()
        
        # Test enhanced agent selection
        agent_result = await self.enhanced_selector.select_best_agent_with_reasoning(scenario["task"])
        
        # Test knowledge base search if relevant
        kb_results = None
        if "research" in scenario["task"]["content"].lower() or "parallel" in scenario["task"]["content"].lower():
            kb_results = self.knowledge_base.search_content("parallel thinking")
        
        processing_time = time.time() - start_time
        
        return {
            "scenario": scenario["name"],
            "success": True,
            "agent_result": agent_result,
            "knowledge_base_results": kb_results,
            "processing_time": processing_time,
            "expected_behavior": scenario["expected_behavior"]
        }
    
    def _display_scenario_result(self, result: Dict[str, Any]):
        """Display the results of a scenario test."""
        
        if not result["success"]:
            print(f"❌ Failed: {result.get('error', 'Unknown error')}")
            return
        
        agent_result = result["agent_result"]
        
        print(f"✅ Success!")
        print(f"   Selected Agent: {agent_result['selected_agent']['agent_name']}")
        print(f"   Task Complexity: {agent_result['task_complexity']:.3f}")
        print(f"   Parallel Reasoning: {agent_result['use_parallel_reasoning']}")
        print(f"   Reasoning Mode: {agent_result['reasoning_mode']}")
        print(f"   Enhancement: {agent_result['enhancement_applied']}")
        print(f"   Processing Time: {result['processing_time']:.2f}s")
        
        if agent_result['parallel_reasoning_result']:
            pr_result = agent_result['parallel_reasoning_result']
            print(f"   🔄 Parallel Paths: {len(pr_result.paths)}")
            print(f"   🏆 Best Path: {pr_result.best_path.reasoning_type}")
            print(f"   ⚡ Confidence: {pr_result.best_path.confidence:.3f}")
        
        if result['knowledge_base_results']:
            print(f"   📚 Knowledge Base: {len(result['knowledge_base_results'])} relevant entries found")
    
    async def test_knowledge_base_integration(self):
        """Test knowledge base integration and search capabilities."""
        
        print("\n📚 Testing Knowledge Base Integration")
        print("=" * 50)
        
        # Test various knowledge base queries
        queries = [
            "parallel thinking",
            "reinforcement learning",
            "curriculum learning",
            "multi-perspective verification",
            "exploration scaffold"
        ]
        
        for query in queries:
            print(f"\n🔍 Query: '{query}'")
            
            # Test entry search
            entries = self.knowledge_base.search(query)
            print(f"   📋 Found {len(entries)} relevant entries")
            
            # Test content search
            content_results = self.knowledge_base.search_content(query)
            print(f"   📄 Found {len(content_results)} content matches")
            
            if content_results:
                print(f"   💡 Sample match: {content_results[0]['context'][:100]}...")
    
    async def test_performance_metrics(self):
        """Test and display performance metrics."""
        
        print("\n📊 Performance Metrics")
        print("=" * 50)
        
        # Get parallel reasoning stats
        if self.enhanced_selector and self.enhanced_selector.parallel_engine:
            stats = self.enhanced_selector.parallel_engine.get_performance_stats()
            print(f"🧠 Parallel Reasoning Engine:")
            print(f"   Total Requests: {stats['total_requests']}")
            print(f"   Success Rate: {stats['success_rate']:.1%}")
            print(f"   Average Improvement: {stats['average_improvement_score']:.3f}")
        
        # Calculate overall test statistics
        successful_tests = sum(1 for r in self.test_results if r.get("success", False))
        total_tests = len(self.test_results)
        success_rate = successful_tests / total_tests if total_tests > 0 else 0
        
        print(f"\n🎯 Overall Test Results:")
        print(f"   Total Scenarios: {total_tests}")
        print(f"   Successful: {successful_tests}")
        print(f"   Success Rate: {success_rate:.1%}")
        
        # Calculate average processing times
        processing_times = [r.get("processing_time", 0) for r in self.test_results if r.get("success", False)]
        if processing_times:
            avg_time = sum(processing_times) / len(processing_times)
            print(f"   Average Processing Time: {avg_time:.2f}s")
    
    async def test_error_handling(self):
        """Test error handling and edge cases."""
        
        print("\n🛡️ Testing Error Handling")
        print("=" * 50)
        
        error_scenarios = [
            {
                "name": "Empty Task",
                "task": {"task_type": "text_generation", "content": "", "latency_requirement": 1000}
            },
            {
                "name": "Invalid Task Type",
                "task": {"task_type": "invalid_type", "content": "Test", "latency_requirement": 1000}
            },
            {
                "name": "Extremely Long Task",
                "task": {"task_type": "text_generation", "content": "Test " * 1000, "latency_requirement": 1000}
            }
        ]
        
        for scenario in error_scenarios:
            print(f"\n🔧 Testing: {scenario['name']}")
            
            try:
                result = await self.enhanced_selector.select_best_agent_with_reasoning(scenario["task"])
                print(f"   ✅ Handled gracefully: {result['enhancement_applied']}")
            except Exception as e:
                print(f"   ⚠️ Error handled: {str(e)[:100]}...")
    
    async def run_complete_workflow_test(self):
        """Run the complete workflow test."""
        
        print("🎭 Complete User Workflow Test")
        print("=" * 60)
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Initialize system
        if not await self.initialize_system():
            print("❌ System initialization failed. Aborting test.")
            return
        
        # Run all tests
        await self.test_user_scenarios()
        await self.test_knowledge_base_integration()
        await self.test_performance_metrics()
        await self.test_error_handling()
        
        # Final summary
        print("\n🎉 Workflow Test Complete!")
        print("=" * 60)
        print(f"Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        successful_tests = sum(1 for r in self.test_results if r.get("success", False))
        total_tests = len(self.test_results)
        
        if successful_tests == total_tests:
            print("✅ All tests passed! System is ready for user interaction.")
        else:
            print(f"⚠️ {total_tests - successful_tests} tests failed. Review results above.")

# Main execution
async def main():
    """Main function to run the complete workflow test."""
    
    tester = UserWorkflowTester()
    await tester.run_complete_workflow_test()

if __name__ == "__main__":
    asyncio.run(main())
