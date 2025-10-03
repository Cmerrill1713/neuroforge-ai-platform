#!/usr/bin/env python3
"""
Enhanced Features Demo
Demonstrates the new advanced capabilities of the AI platform
"""

import asyncio
import json
import time
from datetime import datetime

# Import our enhanced modules
from src.core.tools.enhanced_mcp_tool_registry import enhanced_tool_registry, register_tool
from src.core.reasoning.hrm_integration import hrm_integration
from src.core.models.mlx_integration import mlx_integration, MLXInferenceRequest
from src.core.optimization.advanced_evolutionary import AdvancedEvolutionaryOptimizer, EvolutionConfig
from src.core.multimodal.input_processor import multimodal_processor

async def demo_enhanced_tool_registry():
    """Demonstrate enhanced MCP tool registry"""
    print("🔧 Enhanced MCP Tool Registry Demo")
    print("=" * 50)
    
    # Register some example tools
    async def advanced_calculator(expression: str) -> dict:
        """Advanced calculator tool"""
        try:
            # Add some scientific functions
            import math
            safe_dict = {
                "sin": math.sin, "cos": math.cos, "tan": math.tan,
                "log": math.log, "sqrt": math.sqrt, "pi": math.pi,
                "e": math.e, "abs": abs, "round": round
            }
            result = eval(expression, {"__builtins__": {}}, safe_dict)
            return {
                "success": True,
                "expression": expression,
                "result": result,
                "type": type(result).__name__
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def text_analyzer(text: str) -> dict:
        """Advanced text analyzer"""
        words = text.split()
        sentences = text.split('.')
        
        # Basic analysis
        analysis = {
            "word_count": len(words),
            "sentence_count": len(sentences),
            "character_count": len(text),
            "avg_word_length": sum(len(word) for word in words) / len(words) if words else 0,
            "unique_words": len(set(word.lower() for word in words)),
            "most_common_words": {}
        }
        
        # Word frequency
        word_freq = {}
        for word in words:
            word = word.lower().strip('.,!?;:"()[]{}')
            if len(word) > 2:
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # Top 5 most common words
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        analysis["most_common_words"] = dict(sorted_words[:5])
        
        return {"success": True, "analysis": analysis}
    
    # Register the tools
    from src.core.tools.enhanced_mcp_tool_registry import ToolMetadata
    
    calculator_metadata = ToolMetadata(
        name="advanced_calculator",
        description="Advanced calculator with scientific functions",
        category="math",
        tags=["calculation", "scientific", "math"],
        async_function=True
    )
    enhanced_tool_registry.register_tool("advanced_calculator", advanced_calculator, calculator_metadata)
    
    analyzer_metadata = ToolMetadata(
        name="text_analyzer",
        description="Advanced text analysis and NLP",
        category="nlp",
        tags=["text", "analysis", "nlp"],
        async_function=True
    )
    enhanced_tool_registry.register_tool("text_analyzer", text_analyzer, analyzer_metadata)
    
    # Test tool registry functionality
    print(f"📊 Registered {len(enhanced_tool_registry.tools)} tools")
    print(f"📁 Categories: {list(enhanced_tool_registry.categories.keys())}")
    
    # Test tool search
    search_results = enhanced_tool_registry.search_tools("calculator")
    print(f"🔍 Search results for 'calculator': {len(search_results)} tools")
    
    # Test tool recommendations
    recommendations = enhanced_tool_registry.get_tool_recommendations("I need to calculate something")
    print(f"💡 Tool recommendations: {len(recommendations)} tools")
    
    # Test tool execution
    calc_result = await advanced_calculator("sin(pi/2) + cos(0)")
    print(f"🧮 Calculator result: {calc_result}")
    
    text_result = await text_analyzer("The quick brown fox jumps over the lazy dog. The fox is very quick.")
    print(f"📝 Text analysis result: {text_result}")
    
    # Get system metrics
    metrics = enhanced_tool_registry.get_system_metrics()
    print(f"📈 System metrics: {metrics['total_tools']} tools, {metrics['total_usage']} total usage")
    
    print()

async def demo_hrm_reasoning():
    """Demonstrate HRM complex reasoning"""
    print("🧠 HRM Complex Reasoning Demo")
    print("=" * 50)
    
    # Test Sudoku solving
    sudoku_puzzle = [
        [5, 3, 0, 0, 7, 0, 0, 0, 0],
        [6, 0, 0, 1, 9, 5, 0, 0, 0],
        [0, 9, 8, 0, 0, 0, 0, 6, 0],
        [8, 0, 0, 0, 6, 0, 0, 0, 3],
        [4, 0, 0, 8, 0, 3, 0, 0, 1],
        [7, 0, 0, 0, 2, 0, 0, 0, 6],
        [0, 6, 0, 0, 0, 0, 2, 8, 0],
        [0, 0, 0, 4, 1, 9, 0, 0, 5],
        [0, 0, 0, 0, 8, 0, 0, 7, 9]
    ]
    
    print("🔢 Solving Sudoku puzzle...")
    sudoku_result = await hrm_integration.solve_sudoku(sudoku_puzzle)
    print(f"✅ Sudoku result: Success={sudoku_result.success}, Confidence={sudoku_result.confidence:.2f}")
    print(f"⏱️ Execution time: {sudoku_result.execution_time_ms:.1f}ms")
    
    # Test maze solving
    maze_data = {
        "grid": [
            [1, 1, 1, 1, 1],
            [1, 0, 0, 0, 1],
            [1, 0, 1, 0, 1],
            [1, 0, 0, 0, 1],
            [1, 1, 1, 1, 1]
        ],
        "start": [1, 1],
        "end": [3, 3],
        "width": 5,
        "height": 5
    }
    
    print("🌀 Solving maze pathfinding...")
    maze_result = await hrm_integration.solve_maze(maze_data)
    print(f"✅ Maze result: Success={maze_result.success}, Confidence={maze_result.confidence:.2f}")
    print(f"⏱️ Execution time: {maze_result.execution_time_ms:.1f}ms")
    
    # Test general reasoning
    print("🤔 General reasoning problem...")
    reasoning_result = await hrm_integration.general_reasoning(
        "How can we optimize the performance of a machine learning model?",
        "Consider both training and inference optimization techniques."
    )
    print(f"✅ Reasoning result: Success={reasoning_result.success}, Confidence={reasoning_result.confidence:.2f}")
    print(f"💭 Solution: {reasoning_result.solution.get('answer', 'No solution')[:100]}...")
    
    # Get reasoning statistics
    stats = hrm_integration.get_reasoning_stats()
    print(f"📊 Reasoning stats: {stats['total_tasks']} tasks, {stats['success_rate']:.1%} success rate")
    
    print()

async def demo_mlx_optimization():
    """Demonstrate MLX Apple Metal optimization"""
    print("⚡ MLX Apple Metal Optimization Demo")
    print("=" * 50)
    
    # List available models
    print(f"🤖 Available MLX models: {list(mlx_integration.models.keys())}")
    
    # Test model loading
    if mlx_integration.models:
        model_name = list(mlx_integration.models.keys())[0]
        print(f"📥 Loading model: {model_name}")
        
        success = await mlx_integration.load_model(model_name)
        print(f"✅ Model loaded: {success}")
        
        if success:
            # Test inference
            print("🧠 Testing MLX inference...")
            request = MLXInferenceRequest(
                request_id="demo_1",
                model_name=model_name,
                prompt="Explain the benefits of Apple Metal optimization for AI models.",
                max_tokens=100,
                temperature=0.7
            )
            
            response = await mlx_integration.inference(request)
            print(f"✅ Inference result: Success={response.success}")
            print(f"📝 Response: {response.text[:100]}..." if response.text else "No response")
            print(f"⚡ Tokens/sec: {response.tokens_per_second:.1f}")
            print(f"⏱️ Inference time: {response.inference_time_ms:.1f}ms")
    
    # Get system statistics
    stats = mlx_integration.get_system_stats()
    print(f"📊 MLX stats: {stats['models']['total']} total models, {stats['models']['loaded']} loaded")
    print(f"💾 Memory usage: {stats['memory']['total_used_gb']:.1f}GB")
    print(f"🚀 Avg performance: {stats['performance']['avg_tokens_per_second']:.1f} tokens/sec")
    
    print()

async def demo_evolutionary_optimization():
    """Demonstrate advanced evolutionary optimization"""
    print("🧬 Advanced Evolutionary Optimization Demo")
    print("=" * 50)
    
    # Define a complex optimization problem (Rastrigin function)
    async def rastrigin_fitness(genome):
        """Rastrigin function - complex multimodal optimization problem"""
        import math
        x = genome.get("x", 0)
        y = genome.get("y", 0)
        
        # Rastrigin function: f(x,y) = 20 + x² + y² - 10(cos(2πx) + cos(2πy))
        result = 20 + x**2 + y**2 - 10 * (math.cos(2 * math.pi * x) + math.cos(2 * math.pi * y))
        return -result  # Negative for maximization
    
    async def genome_generator():
        """Generate random genome for Rastrigin function"""
        import random
        return {
            "x": random.uniform(-5.12, 5.12),
            "y": random.uniform(-5.12, 5.12)
        }
    
    async def genome_mutator(genome):
        """Mutate genome with Gaussian noise"""
        import random
        mutated = genome.copy()
        for key in mutated:
            mutated[key] += random.gauss(0, 0.1)
            # Clamp to bounds
            mutated[key] = max(-5.12, min(5.12, mutated[key]))
        return mutated
    
    async def genome_crossover(genome1, genome2):
        """Crossover two genomes"""
        import random
        child1 = {}
        child2 = {}
        
        for key in genome1:
            if random.random() < 0.5:
                child1[key] = genome1[key]
                child2[key] = genome2[key]
            else:
                child1[key] = genome2[key]
                child2[key] = genome1[key]
        
        return [child1, child2]
    
    # Create advanced configuration
    config = EvolutionConfig(
        population_size=50,
        generations=30,
        mutation_rate=0.15,
        crossover_rate=0.8,
        selection_strategy="tournament",
        adaptive_mutation=True,
        adaptive_crossover=True,
        early_stopping=True,
        patience=5,
        min_improvement=0.001
    )
    
    # Create optimizer
    optimizer = AdvancedEvolutionaryOptimizer(config)
    
    print("🚀 Starting evolutionary optimization...")
    print(f"📊 Population: {config.population_size}, Generations: {config.generations}")
    
    start_time = time.time()
    result = await optimizer.optimize(
        fitness_function=rastrigin_fitness,
        genome_generator=genome_generator,
        genome_mutator=genome_mutator,
        genome_crossover=genome_crossover
    )
    end_time = time.time()
    
    print(f"✅ Optimization completed: {result.success}")
    print(f"🏆 Best fitness: {result.best_fitness:.4f}")
    print(f"🧬 Best genome: x={result.best_individual.genome['x']:.4f}, y={result.best_individual.genome['y']:.4f}")
    print(f"📈 Generations: {result.generation}")
    print(f"⏱️ Execution time: {result.execution_time_ms:.0f}ms")
    print(f"🔄 Total evaluations: {result.total_evaluations}")
    print(f"📊 Termination reason: {result.termination_reason}")
    
    # Show convergence history
    if result.convergence_history:
        print(f"📈 Convergence: {result.convergence_history[0]:.4f} → {result.convergence_history[-1]:.4f}")
    
    print()

async def demo_multimodal_processing():
    """Demonstrate multimodal input processing"""
    print("🎭 Multimodal Input Processing Demo")
    print("=" * 50)
    
    # Test text processing
    text_content = """
    Artificial Intelligence (AI) is transforming the world of technology.
    Machine learning algorithms can now process vast amounts of data and
    make predictions with unprecedented accuracy. Deep learning models
    have revolutionized fields like computer vision, natural language
    processing, and speech recognition.
    """
    
    print("📝 Processing text content...")
    text_result = await multimodal_processor.process_input(text_content, "text/plain")
    print(f"✅ Text processing: Success={text_result.success}")
    print(f"📊 Word count: {text_result.extracted_data.get('word_count', 0)}")
    print(f"📄 Summary: {text_result.extracted_data.get('summary', 'No summary')[:100]}...")
    
    # Test JSON processing
    json_content = '''
    {
        "name": "AI Assistant",
        "capabilities": ["reasoning", "optimization", "multimodal"],
        "performance": {
            "accuracy": 0.95,
            "latency_ms": 150
        },
        "models": ["GPT-4", "Claude", "Llama"]
    }
    '''
    
    print("📋 Processing JSON content...")
    json_result = await multimodal_processor.process_input(json_content, "application/json")
    print(f"✅ JSON processing: Success={json_result.success}")
    print(f"📊 Parsed data keys: {list(json_result.extracted_data.get('parsed_data', {}).keys())}")
    
    # Test CSV processing
    csv_content = """name,age,department,salary
John Doe,30,Engineering,75000
Jane Smith,25,Marketing,65000
Bob Johnson,35,Engineering,80000
Alice Brown,28,HR,60000"""
    
    print("📊 Processing CSV content...")
    csv_result = await multimodal_processor.process_input(csv_content, "text/csv")
    print(f"✅ CSV processing: Success={csv_result.success}")
    csv_data = csv_result.extracted_data.get('parsed_data', {})
    print(f"📊 Headers: {csv_data.get('headers', [])}")
    print(f"📊 Row count: {csv_data.get('row_count', 0)}")
    
    # Test XML processing
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
    <configuration>
        <database>
            <host>localhost</host>
            <port>5432</port>
            <name>ai_system</name>
        </database>
        <models>
            <model name="gpt-4" enabled="true"/>
            <model name="claude" enabled="true"/>
        </models>
    </configuration>"""
    
    print("📄 Processing XML content...")
    xml_result = await multimodal_processor.process_input(xml_content, "application/xml")
    print(f"✅ XML processing: Success={xml_result.success}")
    xml_data = xml_result.extracted_data.get('parsed_data', {})
    print(f"📊 XML structure: {list(xml_data.keys())}")
    
    print()

async def demo_integrated_workflow():
    """Demonstrate integrated workflow combining multiple features"""
    print("🔄 Integrated Workflow Demo")
    print("=" * 50)
    
    # Step 1: Use multimodal processing to analyze input
    problem_text = "Optimize the performance of a machine learning model for image classification"
    
    print("1️⃣ Processing problem with multimodal analyzer...")
    text_result = await multimodal_processor.process_input(problem_text, "text/plain")
    keywords = text_result.extracted_data.get('keywords', [])
    print(f"📊 Extracted keywords: {keywords}")
    
    # Step 2: Use HRM reasoning to break down the problem
    print("2️⃣ Using HRM reasoning to analyze the problem...")
    reasoning_result = await hrm_integration.general_reasoning(
        problem_text,
        "Focus on optimization techniques for image classification models"
    )
    print(f"🧠 Reasoning confidence: {reasoning_result.confidence:.2f}")
    
    # Step 3: Use evolutionary optimization to find optimal parameters
    print("3️⃣ Using evolutionary optimization to find optimal parameters...")
    
    async def ml_optimization_fitness(genome):
        """Fitness function for ML model optimization"""
        learning_rate = genome.get("learning_rate", 0.001)
        batch_size = genome.get("batch_size", 32)
        dropout = genome.get("dropout", 0.5)
        
        # Simulate model performance based on parameters
        # In reality, this would train and evaluate the actual model
        performance = 0.8 + (0.1 * (1 - abs(learning_rate - 0.001))) + \
                     (0.05 * (1 - abs(batch_size - 64) / 64)) + \
                     (0.05 * (1 - abs(dropout - 0.3)))
        
        return min(performance, 1.0)
    
    async def ml_genome_generator():
        """Generate ML optimization genome"""
        import random
        return {
            "learning_rate": random.uniform(0.0001, 0.01),
            "batch_size": random.choice([16, 32, 64, 128]),
            "dropout": random.uniform(0.1, 0.8)
        }
    
    async def ml_genome_mutator(genome):
        """Mutate ML genome"""
        import random
        mutated = genome.copy()
        
        if random.random() < 0.3:
            mutated["learning_rate"] *= random.uniform(0.5, 2.0)
            mutated["learning_rate"] = max(0.0001, min(0.01, mutated["learning_rate"]))
        
        if random.random() < 0.3:
            mutated["batch_size"] = random.choice([16, 32, 64, 128])
        
        if random.random() < 0.3:
            mutated["dropout"] += random.uniform(-0.1, 0.1)
            mutated["dropout"] = max(0.1, min(0.8, mutated["dropout"]))
        
        return mutated
    
    async def ml_genome_crossover(genome1, genome2):
        """Crossover ML genomes"""
        import random
        child = {}
        for key in genome1:
            if random.random() < 0.5:
                child[key] = genome1[key]
            else:
                child[key] = genome2[key]
        return [child]
    
    # Run optimization
    config = EvolutionConfig(
        population_size=20,
        generations=15,
        mutation_rate=0.2,
        crossover_rate=0.8
    )
    
    optimizer = AdvancedEvolutionaryOptimizer(config)
    optimization_result = await optimizer.optimize(
        fitness_function=ml_optimization_fitness,
        genome_generator=ml_genome_generator,
        genome_mutator=ml_genome_mutator,
        genome_crossover=ml_genome_crossover
    )
    
    print(f"🧬 Optimization result: {optimization_result.best_fitness:.4f} fitness")
    print(f"📊 Best parameters: {optimization_result.best_individual.genome}")
    
    # Step 4: Use MLX for final model generation
    print("4️⃣ Using MLX for model generation...")
    if mlx_integration.models:
        model_name = list(mlx_integration.models.keys())[0]
        await mlx_integration.load_model(model_name)
        
        prompt = f"""
        Based on the optimization analysis, generate a machine learning model configuration:
        - Learning rate: {optimization_result.best_individual.genome['learning_rate']:.6f}
        - Batch size: {optimization_result.best_individual.genome['batch_size']}
        - Dropout: {optimization_result.best_individual.genome['dropout']:.3f}
        
        Provide a detailed configuration for an image classification model.
        """
        
        request = MLXInferenceRequest(
            request_id="workflow_1",
            model_name=model_name,
            prompt=prompt,
            max_tokens=200
        )
        
        response = await mlx_integration.inference(request)
        print(f"⚡ MLX response: {response.success}")
        print(f"📝 Generated configuration: {response.text[:150]}..." if response.text else "No response")
    
    print("✅ Integrated workflow completed successfully!")
    print()

async def main():
    """Run all demos"""
    print("🚀 Enhanced AI Platform Features Demo")
    print("=" * 60)
    print(f"🕐 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        # Run individual demos
        await demo_enhanced_tool_registry()
        await demo_hrm_reasoning()
        await demo_mlx_optimization()
        await demo_evolutionary_optimization()
        await demo_multimodal_processing()
        
        # Run integrated workflow
        await demo_integrated_workflow()
        
        print("🎉 All demos completed successfully!")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
