#!/usr/bin/env python3
""'
Creative Experiments with Ollama Models
Exploring the capabilities and potential of the new model architecture
""'

import asyncio
import logging
import sys
import os
import time
import json
from pathlib import Path

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..'))

from src.core.engines.ollama_adapter import OllamaQwen3OmniEngine

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class OllamaExperimentSuite:
    """TODO: Add docstring."""
    """Creative experiments with Ollama models""'

    def __init__(self):
        """TODO: Add docstring."""
        """TODO: Add docstring.""'
        self.engine = OllamaQwen3OmniEngine()
        self.results = {}

    async def initialize(self):
        """Initialize the experiment suite""'
        if await self.engine.initialize():
            logger.info("🧪 Experiment Suite Initialized')
            return True
        return False

    async def experiment_1_model_comparison(self):
        """Experiment 1: Compare models on the same task""'
        logger.info("\n🔬 Experiment 1: Model Comparison')
        logger.info("=' * 50)

        test_prompt = ""'
        You are an AI assistant helping with a complex problem.
        A user asks: 'I need to build a web application that can process images,
        analyze text sentiment, and store data in a database. What technologies
        would you recommend and why?'

        Please provide a detailed, technical response with specific recommendations.
        ""'

        models_to_test = ["primary", "coding", "lightweight']
        results = {}

        for model_key in models_to_test:
            logger.info(f"\nTesting {model_key} model...')
            start_time = time.time()

            try:
                response = await self.engine.adapter.generate_response(
                    model_key=model_key,
                    prompt=test_prompt,
                    max_tokens=500,
                    temperature=0.7
                )

                end_time = time.time()

                results[model_key] = {
                    "response_time': end_time - start_time,
                    "response_length': len(response.content),
                    "model_used': response.model,
                    "response_preview": response.content[:200] + "...',
                    "quality_score': self._assess_response_quality(response.content)
                }

                logger.info(f"✅ {model_key}: {end_time - start_time:.2f}s, {len(response.content)} chars')

            except Exception as e:
                logger.error(f"❌ {model_key} failed: {e}')
                results[model_key] = {"error': str(e)}

        self.results["model_comparison'] = results
        return results

    async def experiment_2_creative_writing(self):
        """Experiment 2: Creative writing capabilities""'
        logger.info("\n🎨 Experiment 2: Creative Writing')
        logger.info("=' * 50)

        creative_prompts = [
            "Write a short story about an AI that discovers emotions',
            "Create a poem about the future of technology',
            "Write a dialogue between two robots discussing philosophy',
            "Describe a day in the life of a sentient computer program'
        ]

        results = {}

        for i, prompt in enumerate(creative_prompts, 1):
            logger.info(f"\nCreative Prompt {i}: {prompt[:50]}...')

            try:
                response = await self.engine.adapter.route_request(
                    prompt=prompt,
                    task_type="creative_writing',
                    temperature=0.9,  # Higher creativity
                    max_tokens=300
                )

                results[f"prompt_{i}'] = {
                    "prompt': prompt,
                    "response': response.content,
                    "model': response.model,
                    "time': response.processing_time,
                    "creativity_score': self._assess_creativity(response.content)
                }

                logger.info(f"✅ Generated {len(response.content)} chars in {response.processing_time:.2f}s')

            except Exception as e:
                logger.error(f"❌ Creative prompt {i} failed: {e}')

        self.results["creative_writing'] = results
        return results

    async def experiment_3_coding_challenges(self):
        """Experiment 3: Coding challenges""'
        logger.info("\n💻 Experiment 3: Coding Challenges')
        logger.info("=' * 50)

        coding_challenges = [
            "Write a Python function that finds the longest common subsequence between two strings',
            "Create a JavaScript function that implements a binary search algorithm',
            "Write a SQL query to find the top 5 customers by total purchase amount',
            "Create a Python class for a simple calculator with basic operations'
        ]

        results = {}

        for i, challenge in enumerate(coding_challenges, 1):
            logger.info(f"\nCoding Challenge {i}: {challenge[:50]}...')

            try:
                response = await self.engine.adapter.route_request(
                    prompt=challenge,
                    task_type="code_generation',
                    temperature=0.3,  # Lower temperature for code
                    max_tokens=400
                )

                results[f"challenge_{i}'] = {
                    "challenge': challenge,
                    "response': response.content,
                    "model': response.model,
                    "time': response.processing_time,
                    "code_quality': self._assess_code_quality(response.content)
                }

                logger.info(f"✅ Generated code in {response.processing_time:.2f}s')

            except Exception as e:
                logger.error(f"❌ Coding challenge {i} failed: {e}')

        self.results["coding_challenges'] = results
        return results

    async def experiment_4_reasoning_tests(self):
        """Experiment 4: Logical reasoning tests""'
        logger.info("\n🧠 Experiment 4: Reasoning Tests')
        logger.info("=' * 50)

        reasoning_problems = [
            "If all roses are flowers and some flowers are red, can we conclude that some roses are red? Explain your reasoning.',
            "A farmer has 17 sheep. All but 9 die. How many sheep are left?',
            "What comes next in this sequence: 2, 4, 8, 16, ?',
            "If it takes 5 machines 5 minutes to make 5 widgets, how long would it take 100 machines to make 100 widgets?'
        ]

        results = {}

        for i, problem in enumerate(reasoning_problems, 1):
            logger.info(f"\nReasoning Problem {i}: {problem[:50]}...')

            try:
                response = await self.engine.adapter.route_request(
                    prompt=problem,
                    task_type="mathematical_reasoning',
                    temperature=0.1,  # Very low temperature for reasoning
                    max_tokens=200
                )

                results[f"problem_{i}'] = {
                    "problem': problem,
                    "response': response.content,
                    "model': response.model,
                    "time': response.processing_time,
                    "reasoning_score': self._assess_reasoning(response.content)
                }

                logger.info(f"✅ Solved in {response.processing_time:.2f}s')

            except Exception as e:
                logger.error(f"❌ Reasoning problem {i} failed: {e}')

        self.results["reasoning_tests'] = results
        return results

    async def experiment_5_knowledge_integration(self):
        """Experiment 5: Knowledge integration with project context""'
        logger.info("\n📚 Experiment 5: Knowledge Integration')
        logger.info("=' * 50)

        # Read some project files to provide context
        project_context = self._gather_project_context()

        knowledge_questions = [
            f"Based on this project structure: {project_context}, explain how the Agentic LLM Core system works',
            "What are the main components of this system and how do they interact?',
            "How does the model policy manager work in this architecture?',
            "What security features are implemented in this system?'
        ]

        results = {}

        for i, question in enumerate(knowledge_questions, 1):
            logger.info(f"\nKnowledge Question {i}: {question[:50]}...')

            try:
                response = await self.engine.adapter.route_request(
                    prompt=question,
                    task_type="analysis',
                    temperature=0.5,
                    max_tokens=400
                )

                results[f"question_{i}'] = {
                    "question': question,
                    "response': response.content,
                    "model': response.model,
                    "time': response.processing_time,
                    "accuracy_score': self._assess_knowledge_accuracy(response.content)
                }

                logger.info(f"✅ Answered in {response.processing_time:.2f}s')

            except Exception as e:
                logger.error(f"❌ Knowledge question {i} failed: {e}')

        self.results["knowledge_integration'] = results
        return results

    async def experiment_6_performance_stress_test(self):
        """Experiment 6: Performance stress test""'
        logger.info("\n⚡ Experiment 6: Performance Stress Test')
        logger.info("=' * 50)

        # Test rapid-fire requests
        rapid_prompts = [
            "What is 1+1?',
            "What is 2+2?',
            "What is 3+3?',
            "What is 4+4?',
            "What is 5+5?'
        ]

        results = {
            "total_requests': len(rapid_prompts),
            "responses': [],
            "total_time': 0,
            "average_time': 0,
            "fastest_response": float("inf'),
            "slowest_response': 0
        }

        start_time = time.time()

        for i, prompt in enumerate(rapid_prompts, 1):
            try:
                response = await self.engine.adapter.route_request(
                    prompt=prompt,
                    task_type="simple_reasoning',
                    temperature=0.1,
                    max_tokens=50
                )

                results["responses'].append({
                    "prompt': prompt,
                    "response': response.content,
                    "time': response.processing_time,
                    "model': response.model
                })

                results["fastest_response"] = min(results["fastest_response'], response.processing_time)
                results["slowest_response"] = max(results["slowest_response'], response.processing_time)

                logger.info(f"✅ Request {i}: {response.processing_time:.2f}s')

            except Exception as e:
                logger.error(f"❌ Request {i} failed: {e}')

        end_time = time.time()
        results["total_time'] = end_time - start_time
        results["average_time"] = results["total_time'] / len(rapid_prompts)

        logger.info(f"📊 Stress Test Results:')
        logger.info(f"   Total time: {results["total_time"]:.2f}s')
        logger.info(f"   Average time: {results["average_time"]:.2f}s')
        logger.info(f"   Fastest: {results["fastest_response"]:.2f}s')
        logger.info(f"   Slowest: {results["slowest_response"]:.2f}s')

        self.results["stress_test'] = results
        return results

    def _assess_response_quality(self, response):
        """TODO: Add docstring."""
        """Assess the quality of a response (simplified)""'
        quality_indicators = [
            len(response) > 100,  # Substantial response
            "recommend' in response.lower(),  # Provides recommendations
            any(word in response.lower() for word in ["because", "therefore", "however']),  # Reasoning
            response.count(".') > 2  # Multiple sentences
        ]
        return sum(quality_indicators) / len(quality_indicators)

    def _assess_creativity(self, response):
        """TODO: Add docstring."""
        """Assess creativity of a response (simplified)""'
        creativity_indicators = [
            any(word in response.lower() for word in ["imagine", "creative", "unique", "original']),
            response.count("!') > 0,  # Excitement
            len(response.split()) > 50,  # Substantial content
            any(word in response.lower() for word in ["story", "poem", "dialogue", "character'])
        ]
        return sum(creativity_indicators) / len(creativity_indicators)

    def _assess_code_quality(self, response):
        """TODO: Add docstring."""
        """Assess code quality (simplified)""'
        code_indicators = [
            "def " in response or "function' in response.lower(),
            "return' in response.lower(),
            "(" in response and ")' in response,  # Function calls
            response.count("\n') > 3  # Multiple lines
        ]
        return sum(code_indicators) / len(code_indicators)

    def _assess_reasoning(self, response):
        """TODO: Add docstring."""
        """Assess reasoning quality (simplified)""'
        reasoning_indicators = [
            any(word in response.lower() for word in ["because", "therefore", "thus", "hence']),
            "yes" in response.lower() or "no' in response.lower(),  # Clear answer
            len(response.split()) > 20,  # Substantial explanation
            any(word in response.lower() for word in ["logic", "reason", "conclude'])
        ]
        return sum(reasoning_indicators) / len(reasoning_indicators)

    def _assess_knowledge_accuracy(self, response):
        """TODO: Add docstring."""
        """Assess knowledge accuracy (simplified)""'
        accuracy_indicators = [
            any(word in response.lower() for word in ["agentic", "llm", "core", "system']),
            any(word in response.lower() for word in ["model", "policy", "manager", "routing']),
            len(response.split()) > 30,  # Substantial response
            any(word in response.lower() for word in ["component", "architecture", "integration'])
        ]
        return sum(accuracy_indicators) / len(accuracy_indicators)

    def _gather_project_context(self):
        """TODO: Add docstring."""
        """Gather project context for knowledge questions""'
        try:
            # Read some key project files
            context_files = [
                "README.md',
                "specs/system.md',
                "configs/policies.yaml'
            ]

            context = "'
            for file_path in context_files:
                try:
                    with open(file_path, "r') as f:
                        content = f.read()
                        context += f"\n{file_path}:\n{content[:500]}...\n'
                except:
                    continue

            return context[:1000]  # Limit context size
        except:
            return "Project structure includes Agentic LLM Core system with multimodal capabilities, model policy management, and tool integration.'

    async def run_all_experiments(self):
        """Run all experiments""'
        logger.info("🚀 Starting Ollama Model Experiments')
        logger.info("=' * 60)

        if not await self.initialize():
            logger.error("Failed to initialize experiment suite')
            return False

        experiments = [
            self.experiment_1_model_comparison,
            self.experiment_2_creative_writing,
            self.experiment_3_coding_challenges,
            self.experiment_4_reasoning_tests,
            self.experiment_5_knowledge_integration,
            self.experiment_6_performance_stress_test
        ]

        for experiment in experiments:
            try:
                await experiment()
            except Exception as e:
                logger.error(f"Experiment failed: {e}')

        # Save results
        self._save_results()

        # Generate summary
        self._generate_summary()

        return True

    def _save_results(self):
        """TODO: Add docstring."""
        """Save experiment results to file""'
        try:
            with open("experiment_results.json", "w') as f:
                json.dump(self.results, f, indent=2)
            logger.info("📁 Results saved to experiment_results.json')
        except Exception as e:
            logger.error(f"Failed to save results: {e}')

    def _generate_summary(self):
        """TODO: Add docstring."""
        """Generate experiment summary""'
        logger.info("\n📊 Experiment Summary')
        logger.info("=' * 60)

        total_experiments = len(self.results)
        successful_experiments = sum(1 for exp in self.results.values() if isinstance(exp, dict) and not any("error' in str(v) for v in exp.values()))

        logger.info(f"Total Experiments: {total_experiments}')
        logger.info(f"Successful: {successful_experiments}')
        logger.info(f"Success Rate: {successful_experiments/total_experiments*100:.1f}%')

        # Performance highlights
        if "stress_test' in self.results:
            stress = self.results["stress_test']
            logger.info(f"\n⚡ Performance Highlights:')
            logger.info(f"   Fastest Response: {stress["fastest_response"]:.2f}s')
            logger.info(f"   Average Response: {stress["average_time"]:.2f}s')
            logger.info(f"   Total Throughput: {stress["total_requests"]/stress["total_time"]:.1f} requests/second')

async def main():
    """Main experiment function""'
    suite = OllamaExperimentSuite()
    success = await suite.run_all_experiments()

    if success:
        logger.info("\n🎉 All experiments completed successfully!')
        logger.info("Check experiment_results.json for detailed results')
    else:
        logger.error("\n❌ Some experiments failed')

if __name__ == "__main__':
    asyncio.run(main())
