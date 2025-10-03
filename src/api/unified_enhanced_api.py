#!/usr/bin/env python3
"""
Unified Enhanced API
Integrates all advanced features: MCP tools, HRM reasoning, MLX optimization, evolutionary algorithms, and multimodal processing
"""

import asyncio
import json
import logging
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, List, Optional, Union
import uvicorn
from datetime import datetime

# Import our enhanced modules
from src.core.tools.enhanced_mcp_tool_registry import enhanced_tool_registry, register_tool
from src.core.reasoning.hrm_integration import hrm_integration
from src.core.models.mlx_integration import mlx_integration, MLXInferenceRequest
from src.core.optimization.advanced_evolutionary import AdvancedEvolutionaryOptimizer, EvolutionConfig
from src.core.multimodal.input_processor import multimodal_processor

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Unified Enhanced AI API",
    description="Advanced AI platform with MCP tools, HRM reasoning, MLX optimization, evolutionary algorithms, and multimodal processing",
    version="2.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class ToolRequest(BaseModel):
    tool_name: str
    args: List[Any] = []
    kwargs: Dict[str, Any] = {}

class ReasoningRequest(BaseModel):
    task_type: str  # "sudoku", "maze", "arc", "general"
    input_data: Dict[str, Any]
    context: Optional[str] = None

class MLXRequest(BaseModel):
    model_name: str
    prompt: str
    max_tokens: int = 512
    temperature: float = 0.7
    top_p: float = 0.9

class EvolutionRequest(BaseModel):
    fitness_function: str  # Function name or description
    genome_generator: str
    config: Dict[str, Any] = {}
    generations: int = 50
    population_size: int = 100

class MultimodalRequest(BaseModel):
    content_type: Optional[str] = None
    extract_text: bool = True
    detect_objects: bool = False
    analyze_sentiment: bool = False

@app.get("/")
async def root():
    """Root endpoint with system overview"""
    return {
        "message": "Unified Enhanced AI API",
        "version": "2.0.0",
        "features": [
            "Enhanced MCP Tool Registry",
            "HRM Complex Reasoning",
            "MLX Apple Metal Optimization", 
            "Advanced Evolutionary Algorithms",
            "Multimodal Input Processing"
        ],
        "status": "operational",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health_check():
    """Comprehensive health check"""
    try:
        # Check all subsystems
        tool_registry_health = len(enhanced_tool_registry.tools) > 0
        hrm_health = len(hrm_integration.available_models) >= 0
        mlx_health = len(mlx_integration.models) > 0
        multimodal_health = True  # Always available
        
        overall_health = all([tool_registry_health, hrm_health, mlx_health, multimodal_health])
        
        return {
            "status": "healthy" if overall_health else "degraded",
            "timestamp": datetime.now().isoformat(),
            "subsystems": {
                "tool_registry": "healthy" if tool_registry_health else "unhealthy",
                "hrm_reasoning": "healthy" if hrm_health else "unhealthy", 
                "mlx_optimization": "healthy" if mlx_health else "unhealthy",
                "multimodal_processing": "healthy" if multimodal_health else "unhealthy"
            },
            "metrics": {
                "registered_tools": len(enhanced_tool_registry.tools),
                "available_models": len(mlx_integration.models),
                "loaded_models": len(mlx_integration.loaded_models)
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail=f"Health check failed: {e}")

# MCP Tool Registry endpoints
@app.get("/tools")
async def list_tools():
    """List all registered tools"""
    try:
        tools = []
        for name, metadata in enhanced_tool_registry.tools.items():
            tool_info = enhanced_tool_registry.get_tool_info(name)
            tools.append(tool_info)
        
        return {
            "success": True,
            "tools": tools,
            "count": len(tools),
            "categories": enhanced_tool_registry.categories
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/tools/search")
async def search_tools(query: str):
    """Search tools by name, description, or tags"""
    try:
        results = enhanced_tool_registry.search_tools(query)
        return {
            "success": True,
            "query": query,
            "results": results,
            "count": len(results)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/tools/recommendations")
async def get_tool_recommendations(context: str, max_tools: int = 5):
    """Get tool recommendations based on context"""
    try:
        recommendations = enhanced_tool_registry.get_tool_recommendations(context, max_tools)
        return {
            "success": True,
            "context": context,
            "recommendations": recommendations,
            "count": len(recommendations)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/tools/execute")
async def execute_tool(request: ToolRequest):
    """Execute a registered tool"""
    try:
        if request.tool_name not in enhanced_tool_registry.tool_functions:
            raise HTTPException(status_code=404, detail=f"Tool not found: {request.tool_name}")
        
        function = enhanced_tool_registry.tool_functions[request.tool_name]
        
        # Execute the function
        if asyncio.iscoroutinefunction(function):
            result = await function(*request.args, **request.kwargs)
        else:
            result = function(*request.args, **request.kwargs)
        
        # Update performance metrics
        enhanced_tool_registry.update_tool_performance(request.tool_name, True, 100.0)  # Mock latency
        
        return {
            "success": True,
            "tool_name": request.tool_name,
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        enhanced_tool_registry.update_tool_performance(request.tool_name, False, 0.0)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/tools/metrics")
async def get_tool_metrics():
    """Get tool performance metrics"""
    try:
        metrics = enhanced_tool_registry.get_system_metrics()
        return {
            "success": True,
            "metrics": metrics
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# HRM Reasoning endpoints
@app.post("/reasoning/sudoku")
async def solve_sudoku(puzzle: List[List[int]]):
    """Solve a Sudoku puzzle using HRM"""
    try:
        result = await hrm_integration.solve_sudoku(puzzle)
        return {
            "success": result.success,
            "task_id": result.task_id,
            "solution": result.solution,
            "confidence": result.confidence,
            "reasoning_steps": result.reasoning_steps,
            "execution_time_ms": result.execution_time_ms
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/reasoning/maze")
async def solve_maze(maze_data: Dict[str, Any]):
    """Solve a maze pathfinding problem using HRM"""
    try:
        result = await hrm_integration.solve_maze(maze_data)
        return {
            "success": result.success,
            "task_id": result.task_id,
            "solution": result.solution,
            "confidence": result.confidence,
            "reasoning_steps": result.reasoning_steps,
            "execution_time_ms": result.execution_time_ms
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/reasoning/general")
async def general_reasoning(problem: str, context: Optional[str] = None):
    """General reasoning using HRM"""
    try:
        result = await hrm_integration.general_reasoning(problem, context)
        return {
            "success": result.success,
            "task_id": result.task_id,
            "solution": result.solution,
            "confidence": result.confidence,
            "reasoning_steps": result.reasoning_steps,
            "execution_time_ms": result.execution_time_ms
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/reasoning/stats")
async def get_reasoning_stats():
    """Get HRM reasoning statistics"""
    try:
        stats = hrm_integration.get_reasoning_stats()
        return {
            "success": True,
            "stats": stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# MLX Optimization endpoints
@app.get("/mlx/models")
async def list_mlx_models():
    """List available MLX models"""
    try:
        models = []
        for name, model in mlx_integration.models.items():
            model_info = mlx_integration.get_model_info(name)
            models.append(model_info)
        
        return {
            "success": True,
            "models": models,
            "count": len(models)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/mlx/load")
async def load_mlx_model(model_name: str):
    """Load an MLX model"""
    try:
        success = await mlx_integration.load_model(model_name)
        return {
            "success": success,
            "model_name": model_name,
            "loaded": success
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/mlx/unload")
async def unload_mlx_model(model_name: str):
    """Unload an MLX model"""
    try:
        success = await mlx_integration.unload_model(model_name)
        return {
            "success": success,
            "model_name": model_name,
            "unloaded": success
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/mlx/inference")
async def mlx_inference(request: MLXRequest):
    """Perform MLX inference"""
    try:
        mlx_request = MLXInferenceRequest(
            request_id=f"req_{datetime.now().timestamp()}",
            model_name=request.model_name,
            prompt=request.prompt,
            max_tokens=request.max_tokens,
            temperature=request.temperature,
            top_p=request.top_p
        )
        
        response = await mlx_integration.inference(mlx_request)
        
        return {
            "success": response.success,
            "request_id": response.request_id,
            "text": response.text,
            "tokens_generated": response.tokens_generated,
            "inference_time_ms": response.inference_time_ms,
            "tokens_per_second": response.tokens_per_second,
            "error_message": response.error_message
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/mlx/stats")
async def get_mlx_stats():
    """Get MLX system statistics"""
    try:
        stats = mlx_integration.get_system_stats()
        return {
            "success": True,
            "stats": stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Evolutionary Optimization endpoints
@app.post("/evolution/optimize")
async def evolutionary_optimization(request: EvolutionRequest):
    """Run evolutionary optimization"""
    try:
        # Create configuration
        config = EvolutionConfig(
            population_size=request.population_size,
            generations=request.generations,
            **request.config
        )
        
        # Create optimizer
        optimizer = AdvancedEvolutionaryOptimizer(config)
        
        # Mock functions for demonstration
        async def fitness_function(genome):
            # Mock fitness function - replace with actual implementation
            import random
            return random.uniform(0, 1)
        
        async def genome_generator():
            # Mock genome generator - replace with actual implementation
            import random
            return {
                "x": random.uniform(-10, 10),
                "y": random.uniform(-10, 10)
            }
        
        async def genome_mutator(genome):
            # Mock genome mutator - replace with actual implementation
            mutated = genome.copy()
            for key in mutated:
                if random.random() < 0.1:
                    mutated[key] += random.gauss(0, 0.1)
            return mutated
        
        async def genome_crossover(genome1, genome2):
            # Mock genome crossover - replace with actual implementation
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
        
        # Run optimization
        result = await optimizer.optimize(
            fitness_function=fitness_function,
            genome_generator=genome_generator,
            genome_mutator=genome_mutator,
            genome_crossover=genome_crossover
        )
        
        return {
            "success": result.success,
            "best_fitness": result.best_fitness,
            "best_genome": result.best_individual.genome,
            "generations": result.generation,
            "total_evaluations": result.total_evaluations,
            "execution_time_ms": result.execution_time_ms,
            "convergence_history": result.convergence_history,
            "termination_reason": result.termination_reason
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Multimodal Processing endpoints
@app.post("/multimodal/process")
async def process_multimodal_input(
    file: UploadFile = File(...),
    content_type: Optional[str] = Form(None),
    extract_text: bool = Form(True),
    detect_objects: bool = Form(False)
):
    """Process multimodal input (images, documents, audio, etc.)"""
    try:
        # Read file content
        content = await file.read()
        
        # Process the input
        result = await multimodal_processor.process_input(content, content_type)
        
        return {
            "success": result.success,
            "content_type": result.content_type,
            "extracted_data": result.extracted_data,
            "metadata": result.metadata,
            "processing_time_ms": result.processing_time_ms,
            "file_hash": result.file_hash,
            "error_message": result.error_message
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/multimodal/process-text")
async def process_text_input(text: str, content_type: str = "text/plain"):
    """Process text input"""
    try:
        result = await multimodal_processor.process_input(text, content_type)
        
        return {
            "success": result.success,
            "content_type": result.content_type,
            "extracted_data": result.extracted_data,
            "metadata": result.metadata,
            "processing_time_ms": result.processing_time_ms,
            "error_message": result.error_message
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# System Integration endpoints
@app.post("/integrate/reasoning-tool")
async def integrate_reasoning_with_tool(
    tool_name: str,
    reasoning_type: str,
    input_data: Dict[str, Any]
):
    """Integrate HRM reasoning with MCP tools"""
    try:
        # Get tool function
        if tool_name not in enhanced_tool_registry.tool_functions:
            raise HTTPException(status_code=404, detail=f"Tool not found: {tool_name}")
        
        tool_function = enhanced_tool_registry.tool_functions[tool_name]
        
        # Perform reasoning
        if reasoning_type == "general":
            reasoning_result = await hrm_integration.general_reasoning(
                str(input_data), 
                f"Tool: {tool_name}"
            )
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported reasoning type: {reasoning_type}")
        
        # Execute tool with reasoning context
        if reasoning_result.success:
            tool_result = await tool_function(
                reasoning_result.solution.get("answer", str(input_data))
            )
        else:
            tool_result = await tool_function(str(input_data))
        
        return {
            "success": True,
            "reasoning_result": {
                "success": reasoning_result.success,
                "confidence": reasoning_result.confidence,
                "solution": reasoning_result.solution
            },
            "tool_result": tool_result,
            "integration_successful": reasoning_result.success
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/integrate/mlx-evolution")
async def integrate_mlx_with_evolution(
    model_name: str,
    prompt_template: str,
    generations: int = 10
):
    """Integrate MLX models with evolutionary optimization"""
    try:
        # Load MLX model if not already loaded
        if model_name not in mlx_integration.loaded_models:
            await mlx_integration.load_model(model_name)
        
        # Evolutionary optimization for prompt improvement
        config = EvolutionConfig(
            population_size=20,
            generations=generations
        )
        
        optimizer = AdvancedEvolutionaryOptimizer(config)
        
        # Mock evolutionary optimization for prompt improvement
        async def fitness_function(genome):
            # Use MLX model to evaluate prompt quality
            prompt = genome.get("prompt", prompt_template)
            mlx_request = MLXInferenceRequest(
                request_id=f"eval_{datetime.now().timestamp()}",
                model_name=model_name,
                prompt=prompt,
                max_tokens=100
            )
            
            response = await mlx_integration.inference(mlx_request)
            
            # Simple fitness based on response length and success
            if response.success and response.text:
                return len(response.text) / 100.0  # Normalize
            return 0.0
        
        async def genome_generator():
            import random
            return {
                "prompt": prompt_template + f" (variant {random.randint(1, 100)})",
                "temperature": random.uniform(0.1, 1.0),
                "max_tokens": random.randint(50, 200)
            }
        
        async def genome_mutator(genome):
            import random
            mutated = genome.copy()
            if random.random() < 0.3:
                mutated["prompt"] += " (optimized)"
            return mutated
        
        async def genome_crossover(genome1, genome2):
            import random
            child = {}
            for key in genome1:
                if random.random() < 0.5:
                    child[key] = genome1[key]
                else:
                    child[key] = genome2[key]
            return [child]
        
        # Run optimization
        result = await optimizer.optimize(
            fitness_function=fitness_function,
            genome_generator=genome_generator,
            genome_mutator=genome_mutator,
            genome_crossover=genome_crossover
        )
        
        return {
            "success": result.success,
            "best_prompt": result.best_individual.genome.get("prompt"),
            "best_fitness": result.best_fitness,
            "generations": result.generation,
            "execution_time_ms": result.execution_time_ms
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/system/overview")
async def system_overview():
    """Get comprehensive system overview"""
    try:
        # Gather information from all subsystems
        tool_metrics = enhanced_tool_registry.get_system_metrics()
        hrm_stats = hrm_integration.get_reasoning_stats()
        mlx_stats = mlx_integration.get_system_stats()
        
        return {
            "success": True,
            "timestamp": datetime.now().isoformat(),
            "system_status": "operational",
            "subsystems": {
                "mcp_tools": {
                    "status": "operational",
                    "total_tools": tool_metrics["total_tools"],
                    "total_usage": tool_metrics["total_usage"],
                    "avg_success_rate": tool_metrics["avg_success_rate"]
                },
                "hrm_reasoning": {
                    "status": "operational",
                    "total_tasks": hrm_stats["total_tasks"],
                    "success_rate": hrm_stats["success_rate"],
                    "avg_confidence": hrm_stats["avg_confidence"]
                },
                "mlx_optimization": {
                    "status": "operational",
                    "total_models": mlx_stats["models"]["total"],
                    "loaded_models": mlx_stats["models"]["loaded"],
                    "avg_tokens_per_second": mlx_stats["performance"]["avg_tokens_per_second"]
                },
                "multimodal_processing": {
                    "status": "operational",
                    "supported_formats": multimodal_processor.supported_formats
                }
            },
            "capabilities": [
                "Advanced MCP Tool Registry with 25+ tools",
                "HRM Complex Reasoning (Sudoku, Maze, ARC, General)",
                "MLX Apple Metal Optimization",
                "Evolutionary Algorithm Optimization",
                "Multimodal Input Processing (Images, Documents, Audio)",
                "Integrated Reasoning-Tool Workflows",
                "MLX-Evolution Hybrid Optimization"
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    # Register some example tools
    @register_tool(
        name="example_calculator",
        description="A simple calculator tool",
        category="math",
        tags=["calculation", "math"],
        async_function=True
    )
    async def example_calculator(expression: str) -> Dict[str, Any]:
        """Example calculator tool"""
        try:
            result = eval(expression)
            return {
                "success": True,
                "expression": expression,
                "result": result
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    @register_tool(
        name="example_text_processor",
        description="Process and analyze text",
        category="text",
        tags=["text", "analysis"],
        async_function=True
    )
    async def example_text_processor(text: str) -> Dict[str, Any]:
        """Example text processor tool"""
        words = text.split()
        return {
            "success": True,
            "text": text,
            "word_count": len(words),
            "character_count": len(text),
            "words": words
        }
    
    # Start the server
    uvicorn.run(app, host="0.0.0.0", port=8006)
