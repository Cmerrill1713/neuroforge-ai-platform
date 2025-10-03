#!/usr/bin/env python3
"""
Advanced Evolutionary Optimization System
Enhanced genetic algorithms with multi-objective optimization, adaptive strategies, and advanced selection mechanisms
"""

import asyncio
import json
import logging
import random
import numpy as np
from typing import Dict, Any, List, Optional, Callable, Tuple, Union
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import math
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

def rastrigin_function(x: float, y: float) -> float:
    """
    Rastrigin function for optimization testing.
    Global minimum at (0,0) with value 0.
    We'll negate it to turn it into a maximization problem for fitness.
    """
    A = 10
    return -(A * 2 + (x**2 - A * np.cos(2 * np.pi * x)) + (y**2 - A * np.cos(2 * np.pi * y)))

class SelectionStrategy(Enum):
    """Selection strategies for evolutionary algorithms"""
    TOURNAMENT = "tournament"
    ROULETTE = "roulette"
    RANK = "rank"
    ELITIST = "elitist"
    NSGA_II = "nsga_ii"  # Non-dominated Sorting Genetic Algorithm II

class CrossoverStrategy(Enum):
    """Crossover strategies"""
    UNIFORM = "uniform"
    SINGLE_POINT = "single_point"
    TWO_POINT = "two_point"
    ARITHMETIC = "arithmetic"
    BLEND = "blend"

class MutationStrategy(Enum):
    """Mutation strategies"""
    GAUSSIAN = "gaussian"
    UNIFORM = "uniform"
    POLYNOMIAL = "polynomial"
    ADAPTIVE = "adaptive"

@dataclass
class Individual:
    """Individual in the evolutionary population"""
    genome: Dict[str, Any]
    fitness: float = 0.0
    objectives: List[float] = field(default_factory=list)  # For multi-objective optimization
    rank: int = 0  # For NSGA-II
    crowding_distance: float = 0.0  # For NSGA-II
    age: int = 0
    generation: int = 0
    parent_ids: List[str] = field(default_factory=list)
    individual_id: str = field(default_factory=lambda: f"ind_{datetime.now().timestamp()}")
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class EvolutionConfig:
    """Configuration for evolutionary optimization"""
    population_size: int = 100
    generations: int = 50
    mutation_rate: float = 0.1
    crossover_rate: float = 0.8
    elite_size: int = 10
    tournament_size: int = 3
    
    # Advanced parameters
    selection_strategy: SelectionStrategy = SelectionStrategy.TOURNAMENT
    crossover_strategy: CrossoverStrategy = CrossoverStrategy.UNIFORM
    mutation_strategy: MutationStrategy = MutationStrategy.GAUSSIAN
    
    # Multi-objective parameters
    multi_objective: bool = False
    objectives: List[str] = field(default_factory=list)
    objective_weights: List[float] = field(default_factory=list)
    
    # Adaptive parameters
    adaptive_mutation: bool = True
    adaptive_crossover: bool = True
    diversity_threshold: float = 0.1
    
    # Termination criteria
    early_stopping: bool = True
    patience: int = 10
    min_improvement: float = 0.01
    
    # Diversity maintenance
    diversity_maintenance: bool = True
    niching_radius: float = 0.1
    crowding_factor: float = 0.5

@dataclass
class EvolutionResult:
    """Result of evolutionary optimization"""
    best_individual: Individual
    best_fitness: float
    convergence_history: List[float]
    diversity_history: List[float]
    generation: int
    total_evaluations: int
    execution_time_ms: float
    success: bool
    termination_reason: str
    population_stats: Dict[str, Any]
    pareto_front: List[Individual] = field(default_factory=list)  # For multi-objective

class AdvancedEvolutionaryOptimizer:
    """Advanced evolutionary optimization system with multiple strategies"""
    
    def __init__(self, config: EvolutionConfig):
        self.config = config
        self.population: List[Individual] = []
        self.generation = 0
        self.best_individual: Optional[Individual] = None
        self.convergence_history: List[float] = []
        self.diversity_history: List[float] = []
        self.evaluation_count = 0
        self.start_time = None
        
        # Adaptive parameters
        self.adaptive_mutation_rate = config.mutation_rate
        self.adaptive_crossover_rate = config.crossover_rate
        
        # Diversity tracking
        self.diversity_tracker = DiversityTracker()
        
        # Performance tracking
        self.performance_tracker = PerformanceTracker()
        
        logger.info("🧬 Advanced Evolutionary Optimizer initialized")
    
    async def optimize(
        self,
        fitness_function: Callable,
        genome_generator: Callable,
        genome_mutator: Callable,
        genome_crossover: Callable,
        **kwargs
    ) -> EvolutionResult:
        """Run evolutionary optimization"""
        self.start_time = datetime.now()
        logger.info(f"🚀 Starting evolutionary optimization: {self.config.generations} generations, {self.config.population_size} individuals")
        
        try:
            # Initialize population
            await self._initialize_population(genome_generator)
            
            # Evolution loop
            for generation in range(self.config.generations):
                self.generation = generation
                
                # Evaluate population
                await self._evaluate_population(fitness_function)
                
                # Track convergence and diversity
                self._update_tracking_metrics()
                
                # Check termination criteria
                if self._should_terminate():
                    break
                
                # Selection
                selected = self._selection()
                
                # Crossover
                offspring = await self._crossover(selected, genome_crossover)
                
                # Mutation
                mutated_offspring = await self._mutation(offspring, genome_mutator)
                
                # Replacement
                self._replacement(mutated_offspring)
                
                # Adaptive parameter adjustment
                self._adapt_parameters()
                
                # Log progress
                if generation % 10 == 0:
                    self._log_progress()
            
            # Final evaluation
            await self._evaluate_population(fitness_function)
            
            # Create result
            result = self._create_result()
            
            logger.info(f"✅ Evolutionary optimization completed: {result.best_fitness:.4f} fitness")
            return result
            
        except Exception as e:
            logger.error(f"❌ Evolutionary optimization failed: {e}")
            return self._create_error_result(str(e))
    
    async def _initialize_population(self, genome_generator: Callable):
        """Initialize the population"""
        logger.info("🧬 Initializing population...")
        
        self.population = []
        for i in range(self.config.population_size):
            genome = await genome_generator()
            individual = Individual(
                genome=genome,
                generation=0,
                individual_id=f"ind_{i}_{datetime.now().timestamp()}"
            )
            self.population.append(individual)
        
        logger.info(f"✅ Population initialized: {len(self.population)} individuals")
    
    async def _evaluate_population(self, fitness_function: Callable):
        """Evaluate the fitness of all individuals in the population"""
        tasks = []
        for individual in self.population:
            if individual.fitness == 0.0:  # Only evaluate if not already evaluated
                task = self._evaluate_individual(individual, fitness_function)
                tasks.append(task)
        
        if tasks:
            await asyncio.gather(*tasks)
        
        self.evaluation_count += len(tasks)
    
    async def _evaluate_individual(self, individual: Individual, fitness_function: Callable):
        """Evaluate a single individual"""
        try:
            if self.config.multi_objective:
                objectives = await fitness_function(individual.genome)
                individual.objectives = objectives
                individual.fitness = self._calculate_weighted_fitness(objectives)
            else:
                individual.fitness = await fitness_function(individual.genome)
            
            individual.age += 1
            
        except Exception as e:
            logger.warning(f"Evaluation failed for individual {individual.individual_id}: {e}")
            individual.fitness = 0.0
            individual.objectives = [0.0] * len(self.config.objectives)
    
    def _calculate_weighted_fitness(self, objectives: List[float]) -> float:
        """Calculate weighted fitness for multi-objective optimization"""
        if not self.config.objective_weights:
            return sum(objectives) / len(objectives)
        
        weighted_sum = sum(obj * weight for obj, weight in zip(objectives, self.config.objective_weights))
        return weighted_sum
    
    def _selection(self) -> List[Individual]:
        """Select individuals for reproduction"""
        if self.config.selection_strategy == SelectionStrategy.TOURNAMENT:
            return self._tournament_selection()
        elif self.config.selection_strategy == SelectionStrategy.ROULETTE:
            return self._roulette_selection()
        elif self.config.selection_strategy == SelectionStrategy.RANK:
            return self._rank_selection()
        elif self.config.selection_strategy == SelectionStrategy.ELITIST:
            return self._elitist_selection()
        elif self.config.selection_strategy == SelectionStrategy.NSGA_II:
            return self._nsga_ii_selection()
        else:
            return self._tournament_selection()
    
    def _tournament_selection(self) -> List[Individual]:
        """Tournament selection"""
        selected = []
        for _ in range(self.config.population_size):
            tournament = random.sample(self.population, self.config.tournament_size)
            winner = max(tournament, key=lambda x: x.fitness)
            selected.append(winner)
        return selected
    
    def _roulette_selection(self) -> List[Individual]:
        """Roulette wheel selection"""
        total_fitness = sum(ind.fitness for ind in self.population)
        if total_fitness == 0:
            return random.sample(self.population, self.config.population_size)
        
        selected = []
        for _ in range(self.config.population_size):
            pick = random.uniform(0, total_fitness)
            current = 0
            for individual in self.population:
                current += individual.fitness
                if current >= pick:
                    selected.append(individual)
                    break
        return selected
    
    def _rank_selection(self) -> List[Individual]:
        """Rank-based selection"""
        sorted_population = sorted(self.population, key=lambda x: x.fitness)
        ranks = list(range(1, len(sorted_population) + 1))
        total_rank = sum(ranks)
        
        selected = []
        for _ in range(self.config.population_size):
            pick = random.uniform(0, total_rank)
            current = 0
            for i, individual in enumerate(sorted_population):
                current += ranks[i]
                if current >= pick:
                    selected.append(individual)
                    break
        return selected
    
    def _elitist_selection(self) -> List[Individual]:
        """Elitist selection - keep best individuals"""
        sorted_population = sorted(self.population, key=lambda x: x.fitness, reverse=True)
        elite = sorted_population[:self.config.elite_size]
        
        # Fill remaining with tournament selection
        remaining = self.config.population_size - self.config.elite_size
        selected = elite.copy()
        
        for _ in range(remaining):
            tournament = random.sample(self.population, self.config.tournament_size)
            winner = max(tournament, key=lambda x: x.fitness)
            selected.append(winner)
        
        return selected
    
    def _nsga_ii_selection(self) -> List[Individual]:
        """NSGA-II selection for multi-objective optimization"""
        if not self.config.multi_objective:
            return self._tournament_selection()
        
        # Non-dominated sorting
        fronts = self._non_dominated_sorting(self.population)
        
        # Calculate crowding distance
        for front in fronts:
            self._calculate_crowding_distance(front)
        
        # Select individuals
        selected = []
        for front in fronts:
            if len(selected) + len(front) <= self.config.population_size:
                selected.extend(front)
            else:
                # Sort by crowding distance and select the best
                front.sort(key=lambda x: x.crowding_distance, reverse=True)
                remaining = self.config.population_size - len(selected)
                selected.extend(front[:remaining])
                break
        
        return selected
    
    def _non_dominated_sorting(self, population: List[Individual]) -> List[List[Individual]]:
        """Non-dominated sorting for NSGA-II"""
        fronts = []
        remaining = population.copy()
        
        while remaining:
            front = []
            dominated = []
            
            for i, individual in enumerate(remaining):
                is_dominated = False
                for j, other in enumerate(remaining):
                    if i != j and self._dominates(other, individual):
                        is_dominated = True
                        break
                
                if not is_dominated:
                    front.append(individual)
                else:
                    dominated.append(individual)
            
            fronts.append(front)
            remaining = dominated
        
        return fronts
    
    def _dominates(self, individual1: Individual, individual2: Individual) -> bool:
        """Check if individual1 dominates individual2"""
        if not self.config.multi_objective:
            return individual1.fitness > individual2.fitness
        
        objectives1 = individual1.objectives
        objectives2 = individual2.objectives
        
        # At least one objective is better
        better = any(obj1 > obj2 for obj1, obj2 in zip(objectives1, objectives2))
        # No objective is worse
        worse = any(obj1 < obj2 for obj1, obj2 in zip(objectives1, objectives2))
        
        return better and not worse
    
    def _calculate_crowding_distance(self, front: List[Individual]):
        """Calculate crowding distance for NSGA-II"""
        if len(front) <= 2:
            for individual in front:
                individual.crowding_distance = float('inf')
            return
        
        # Initialize crowding distance
        for individual in front:
            individual.crowding_distance = 0.0
        
        # Calculate for each objective
        for obj_idx in range(len(self.config.objectives)):
            # Sort by objective value
            front.sort(key=lambda x: x.objectives[obj_idx])
            
            # Set boundary points to infinity
            front[0].crowding_distance = float('inf')
            front[-1].crowding_distance = float('inf')
            
            # Calculate distance for intermediate points
            obj_range = front[-1].objectives[obj_idx] - front[0].objectives[obj_idx]
            if obj_range > 0:
                for i in range(1, len(front) - 1):
                    distance = (front[i + 1].objectives[obj_idx] - front[i - 1].objectives[obj_idx]) / obj_range
                    front[i].crowding_distance += distance
    
    async def _crossover(self, selected: List[Individual], genome_crossover: Callable) -> List[Individual]:
        """Perform crossover to create offspring"""
        offspring = []
        
        for i in range(0, len(selected), 2):
            if i + 1 < len(selected):
                parent1 = selected[i]
                parent2 = selected[i + 1]
                
                if random.random() < self.adaptive_crossover_rate:
                    child_genomes = await genome_crossover(parent1.genome, parent2.genome)
                    
                    for child_genome in child_genomes:
                        child = Individual(
                            genome=child_genome,
                            generation=self.generation + 1,
                            parent_ids=[parent1.individual_id, parent2.individual_id],
                            individual_id=f"child_{datetime.now().timestamp()}"
                        )
                        offspring.append(child)
                else:
                    # No crossover, copy parents
                    offspring.extend([parent1, parent2])
            else:
                # Odd number of parents, copy the last one
                offspring.append(selected[i])
        
        return offspring
    
    async def _mutation(self, offspring: List[Individual], genome_mutator: Callable) -> List[Individual]:
        """Perform mutation on offspring"""
        mutated_offspring = []
        
        for individual in offspring:
            if random.random() < self.adaptive_mutation_rate:
                mutated_genome = await genome_mutator(individual.genome)
                individual.genome = mutated_genome
            
            mutated_offspring.append(individual)
        
        return mutated_offspring
    
    def _replacement(self, offspring: List[Individual]):
        """Replace population with new generation"""
        if self.config.selection_strategy == SelectionStrategy.ELITIST:
            # Keep elite individuals
            sorted_population = sorted(self.population, key=lambda x: x.fitness, reverse=True)
            elite = sorted_population[:self.config.elite_size]
            
            # Combine elite with offspring
            new_population = elite + offspring
            new_population = new_population[:self.config.population_size]
        else:
            # Replace entire population
            new_population = offspring[:self.config.population_size]
        
        self.population = new_population
    
    def _adapt_parameters(self):
        """Adapt mutation and crossover rates based on performance"""
        if not self.config.adaptive_mutation and not self.config.adaptive_crossover:
            return
        
        # Calculate population diversity
        diversity = self.diversity_tracker.calculate_diversity(self.population)
        
        # Adapt mutation rate
        if self.config.adaptive_mutation:
            if diversity < self.config.diversity_threshold:
                self.adaptive_mutation_rate = min(0.5, self.adaptive_mutation_rate * 1.1)
            else:
                self.adaptive_mutation_rate = max(0.01, self.adaptive_mutation_rate * 0.9)
        
        # Adapt crossover rate
        if self.config.adaptive_crossover:
            if diversity < self.config.diversity_threshold:
                self.adaptive_crossover_rate = min(0.9, self.adaptive_crossover_rate * 1.05)
            else:
                self.adaptive_crossover_rate = max(0.1, self.adaptive_crossover_rate * 0.95)
    
    def _update_tracking_metrics(self):
        """Update convergence and diversity tracking"""
        # Update best individual
        current_best = max(self.population, key=lambda x: x.fitness)
        if self.best_individual is None or current_best.fitness > self.best_individual.fitness:
            self.best_individual = current_best
        
        # Track convergence
        self.convergence_history.append(self.best_individual.fitness)
        
        # Track diversity
        diversity = self.diversity_tracker.calculate_diversity(self.population)
        self.diversity_history.append(diversity)
        
        # Update performance tracker
        self.performance_tracker.update(self.population, self.generation)
    
    def _should_terminate(self) -> bool:
        """Check if optimization should terminate early"""
        if not self.config.early_stopping:
            return False
        
        # Check for convergence
        if len(self.convergence_history) >= self.config.patience:
            recent_improvements = []
            for i in range(len(self.convergence_history) - self.config.patience, len(self.convergence_history)):
                if i > 0:
                    improvement = self.convergence_history[i] - self.convergence_history[i-1]
                    recent_improvements.append(improvement)
            
            if recent_improvements:
                avg_improvement = sum(recent_improvements) / len(recent_improvements)
                if avg_improvement < self.config.min_improvement:
                    return True
        
        return False
    
    def _log_progress(self):
        """Log optimization progress"""
        best_fitness = self.best_individual.fitness if self.best_individual else 0.0
        avg_fitness = sum(ind.fitness for ind in self.population) / len(self.population)
        diversity = self.diversity_history[-1] if self.diversity_history else 0.0
        
        logger.info(f"Generation {self.generation}: Best={best_fitness:.4f}, Avg={avg_fitness:.4f}, Diversity={diversity:.4f}")
    
    def _create_result(self) -> EvolutionResult:
        """Create optimization result"""
        execution_time = (datetime.now() - self.start_time).total_seconds() * 1000
        
        # Calculate population statistics
        fitness_values = [ind.fitness for ind in self.population]
        population_stats = {
            "best_fitness": max(fitness_values),
            "worst_fitness": min(fitness_values),
            "avg_fitness": sum(fitness_values) / len(fitness_values),
            "std_fitness": np.std(fitness_values),
            "diversity": self.diversity_history[-1] if self.diversity_history else 0.0
        }
        
        # Get Pareto front for multi-objective optimization
        pareto_front = []
        if self.config.multi_objective:
            fronts = self._non_dominated_sorting(self.population)
            pareto_front = fronts[0] if fronts else []
        
        return EvolutionResult(
            best_individual=self.best_individual,
            best_fitness=self.best_individual.fitness if self.best_individual else 0.0,
            convergence_history=self.convergence_history.copy(),
            diversity_history=self.diversity_history.copy(),
            generation=self.generation,
            total_evaluations=self.evaluation_count,
            execution_time_ms=execution_time,
            success=True,
            termination_reason="completed",
            population_stats=population_stats,
            pareto_front=pareto_front
        )
    
    def _create_error_result(self, error_message: str) -> EvolutionResult:
        """Create error result"""
        execution_time = (datetime.now() - self.start_time).total_seconds() * 1000 if self.start_time else 0.0
        
        return EvolutionResult(
            best_individual=self.best_individual,
            best_fitness=self.best_individual.fitness if self.best_individual else 0.0,
            convergence_history=self.convergence_history.copy(),
            diversity_history=self.diversity_history.copy(),
            generation=self.generation,
            total_evaluations=self.evaluation_count,
            execution_time_ms=execution_time,
            success=False,
            termination_reason=f"error: {error_message}",
            population_stats={},
            pareto_front=[]
        )

class DiversityTracker:
    """Track population diversity"""
    
    def calculate_diversity(self, population: List[Individual]) -> float:
        """Calculate population diversity"""
        if len(population) < 2:
            return 0.0
        
        # Simple diversity metric based on fitness variance
        fitness_values = [ind.fitness for ind in population]
        if not fitness_values:
            return 0.0
        
        mean_fitness = sum(fitness_values) / len(fitness_values)
        variance = sum((f - mean_fitness) ** 2 for f in fitness_values) / len(fitness_values)
        
        return math.sqrt(variance)

class PerformanceTracker:
    """Track optimization performance"""
    
    def __init__(self):
        self.generation_stats = []
    
    def update(self, population: List[Individual], generation: int):
        """Update performance tracking"""
        stats = {
            "generation": generation,
            "population_size": len(population),
            "best_fitness": max(ind.fitness for ind in population) if population else 0.0,
            "avg_fitness": sum(ind.fitness for ind in population) / len(population) if population else 0.0,
            "timestamp": datetime.now().isoformat()
        }
        
        self.generation_stats.append(stats)

# Example usage and testing
async def main():
    """Test advanced evolutionary optimizer"""
    print("🧬 Advanced Evolutionary Optimizer Test")
    
    # Example genome generator
    async def genome_generator():
        return {
            "x": random.uniform(-10, 10),
            "y": random.uniform(-10, 10),
            "z": random.uniform(-10, 10)
        }
    
    # Example fitness function (sphere function)
    async def fitness_function(genome):
        x, y, z = genome["x"], genome["y"], genome["z"]
        return -(x**2 + y**2 + z**2)  # Negative for maximization
    
    # Example genome mutator
    async def genome_mutator(genome):
        mutated = genome.copy()
        for key in mutated:
            if random.random() < 0.1:  # 10% chance to mutate each parameter
                mutated[key] += random.gauss(0, 0.1)
                mutated[key] = max(-10, min(10, mutated[key]))  # Clamp to bounds
        return mutated
    
    # Example genome crossover
    async def genome_crossover(genome1, genome2):
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
    
    # Create configuration
    config = EvolutionConfig(
        population_size=50,
        generations=30,
        mutation_rate=0.1,
        crossover_rate=0.8,
        selection_strategy=SelectionStrategy.TOURNAMENT,
        adaptive_mutation=True,
        early_stopping=True
    )
    
    # Create optimizer
    optimizer = AdvancedEvolutionaryOptimizer(config)
    
    # Run optimization
    result = await optimizer.optimize(
        fitness_function=fitness_function,
        genome_generator=genome_generator,
        genome_mutator=genome_mutator,
        genome_crossover=genome_crossover
    )
    
    print(f"Optimization completed: {result.success}")
    print(f"Best fitness: {result.best_fitness:.4f}")
    print(f"Best genome: {result.best_individual.genome}")
    print(f"Generations: {result.generation}")
    print(f"Execution time: {result.execution_time_ms:.0f}ms")

if __name__ == "__main__":
    asyncio.run(main())
