#!/usr/bin/env python3
"""
Evolutionary Optimizer API Routes
FastAPI endpoints for the frontend Evolution panel
"""

import logging
import json
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

# Router
router = APIRouter(prefix="/api/evolutionary", tags=["evolutionary"])

# Global state (will be initialized on app startup)
evolutionary_integration = None


class OptimizationConfig(BaseModel):
    """Configuration for evolution run"""
    num_generations: int = Field(default=3, ge=1, le=50)
    use_mipro: bool = Field(default=False)
    population_size: int = Field(default=12, ge=4, le=50)


class EvolutionStatsResponse(BaseModel):
    """Evolution statistics response"""
    current_generation: int
    best_score: float
    mean_score: float
    population_size: int
    status: str  # "idle", "running", "complete"


def set_integration(integration):
    """Set the global integration instance"""
    global evolutionary_integration
    evolutionary_integration = integration


@router.post("/optimize")
async def start_optimization(config: OptimizationConfig) -> Dict[str, Any]:
    """
    Start evolutionary optimization
    
    Returns:
        - top_genomes: List of best genomes found
        - fitness_history: Generation-by-generation progress
        - best_genome: Details of the best genome
    """
    if not evolutionary_integration:
        raise HTTPException(status_code=503, detail="Evolutionary integration not initialized")
    
    try:
        logger.info(f"🧬 Starting evolution: {config.num_generations} generations, MIPROv2={config.use_mipro}")
        
        # Load golden dataset
        dataset_path = Path("data/golden_dataset.json")
        if not dataset_path.exists():
            raise HTTPException(status_code=404, detail="Golden dataset not found. Run: python scripts/build_golden_dataset.py")
        
        with open(dataset_path) as f:
            data = json.load(f)
        
        golden_examples = data["examples"]
        
        # Run evolution
        best_genome = await evolutionary_integration.optimize_comprehensive(
            base_prompt="You are a helpful AI assistant. Be clear, specific, and actionable.",
            golden_dataset=golden_examples,
            num_generations=config.num_generations,
            use_mipro=config.use_mipro
        )
        
        # Format response
        fitness_history = [
            {
                "gen": h["generation"],
                "best": h["best_score"],
                "mean": h["mean_score"]
            }
            for h in evolutionary_integration.evolutionary.fitness_history
        ]
        
        top_genomes = [
            {
                "genome_id": genome.genome_id,
                "temperature": genome.temp,
                "max_tokens": genome.max_tokens,
                "model_key": genome.model_key,
                "generation": genome.generation,
                "fitness_score": score
            }
            for score, genome in sorted(evolutionary_integration.evolutionary.best_genomes, reverse=True)[:5]
        ]
        
        logger.info(f"✅ Evolution complete: best score = {best_genome.temp}")
        
        return {
            "success": True,
            "best_genome": {
                "genome_id": best_genome.genome_id,
                "temperature": best_genome.temp,
                "max_tokens": best_genome.max_tokens,
                "model_key": best_genome.model_key,
                "generation": best_genome.generation
            },
            "top_genomes": top_genomes,
            "fitness_history": fitness_history,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Evolution failed: {e}")
        raise HTTPException(status_code=500, detail=f"Evolution failed: {str(e)}")


@router.get("/stats", response_model=EvolutionStatsResponse)
async def get_evolution_stats() -> EvolutionStatsResponse:
    """
    Get current evolution statistics
    
    Returns real-time stats about the evolutionary optimizer state
    """
    if not evolutionary_integration:
        return EvolutionStatsResponse(
            current_generation=0,
            best_score=0.0,
            mean_score=0.0,
            population_size=12,
            status="not_initialized"
        )
    
    try:
        # Get latest stats
        best_score = 0.0
        mean_score = 0.0
        current_gen = evolutionary_integration.evolutionary.generation
        
        if evolutionary_integration.evolutionary.fitness_history:
            latest = evolutionary_integration.evolutionary.fitness_history[-1]
            best_score = latest["best_score"]
            mean_score = latest["mean_score"]
        
        return EvolutionStatsResponse(
            current_generation=current_gen,
            best_score=best_score,
            mean_score=mean_score,
            population_size=evolutionary_integration.evolutionary.population_size,
            status="idle"  # Would track actual running state
        )
        
    except Exception as e:
        logger.error(f"Failed to get stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/bandit/stats")
async def get_bandit_stats() -> Dict[str, Any]:
    """
    Get Thompson sampling bandit statistics
    
    Returns performance data for each genome in production
    """
    if not evolutionary_integration or not evolutionary_integration.bandit:
        return {}
    
    try:
        return evolutionary_integration.bandit.get_stats()
    except Exception as e:
        logger.error(f"Failed to get bandit stats: {e}")
        return {}


@router.get("/history")
async def get_fitness_history() -> Dict[str, Any]:
    """Get complete fitness history across all generations"""
    if not evolutionary_integration:
        return {"history": []}
    
    try:
        return {
            "history": evolutionary_integration.evolutionary.fitness_history,
            "total_generations": evolutionary_integration.evolutionary.generation
        }
    except Exception as e:
        logger.error(f"Failed to get history: {e}")
        return {"history": [], "error": str(e)}


@router.get("/genomes")
async def get_all_genomes() -> Dict[str, Any]:
    """Get all genomes from evolution history"""
    if not evolutionary_integration:
        return {"genomes": []}
    
    try:
        genomes = [
            {
                "genome_id": genome.genome_id,
                "temperature": genome.temp,
                "max_tokens": genome.max_tokens,
                "model_key": genome.model_key,
                "generation": genome.generation,
                "fitness_score": score,
                "cot": genome.cot,
                "use_consensus": genome.use_consensus
            }
            for score, genome in evolutionary_integration.evolutionary.best_genomes
        ]
        
        return {
            "genomes": genomes,
            "total": len(genomes)
        }
    except Exception as e:
        logger.error(f"Failed to get genomes: {e}")
        return {"genomes": [], "error": str(e)}

