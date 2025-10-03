#!/usr/bin/env python3
"""
Golden Dataset Builder
Extracts high-quality examples from your existing data for evolutionary optimization

Creates a curated dataset of:
- Real user queries
- Expected/validated outputs
- Quality metadata
- Task type labels
"""

import json
import logging
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GoldenDatasetBuilder:
    """Build golden dataset from existing sources"""
    
    def __init__(self, output_path: Path = None):
        self.output_path = output_path or Path("data/golden_dataset.json")
        self.output_path.parent.mkdir(exist_ok=True)
        
        self.examples: List[Dict[str, Any]] = []
        
    def add_example(
        self,
        query: str,
        expected_output: str,
        context: str = "",
        intent: str = "text_generation",
        quality_score: float = 1.0,
        metadata: Dict[str, Any] = None
    ):
        """Add a single example to the dataset"""
        example = {
            "query": query,
            "expected_output": expected_output,
            "context": context,
            "intent": intent,
            "quality_score": quality_score,
            "metadata": metadata or {},
            "added_at": datetime.now().isoformat()
        }
        
        self.examples.append(example)
        logger.info(f"✅ Added example: {query[:50]}...")
    
    def load_from_logs(self, log_path: Path):
        """Extract examples from production logs"""
        logger.info(f"📄 Loading from logs: {log_path}")
        
        try:
            if not log_path.exists():
                logger.warning(f"Log file not found: {log_path}")
                return
            
            with open(log_path, 'r') as f:
                logs = json.load(f)
            
            for entry in logs:
                # Extract only high-quality responses
                if entry.get("quality_score", 0) >= 0.8:
                    self.add_example(
                        query=entry.get("query", ""),
                        expected_output=entry.get("response", ""),
                        context=entry.get("context", ""),
                        intent=entry.get("intent", "text_generation"),
                        quality_score=entry.get("quality_score", 1.0),
                        metadata={
                            "source": "production_logs",
                            "user_rating": entry.get("user_rating"),
                            "latency_ms": entry.get("latency_ms")
                        }
                    )
            
            logger.info(f"✅ Loaded {len(self.examples)} examples from logs")
            
        except Exception as e:
            logger.error(f"Failed to load logs: {e}")
    
    def load_from_knowledge_base(self, kb_path: Path):
        """Extract examples from knowledge base"""
        logger.info(f"📚 Loading from knowledge base: {kb_path}")
        
        try:
            # Example: Extract Q&A pairs from knowledge base
            if not kb_path.exists():
                logger.warning(f"KB path not found: {kb_path}")
                return
            
            # Load knowledge base documents
            for kb_file in kb_path.glob("*.json"):
                with open(kb_file, 'r') as f:
                    doc = json.load(f)
                
                # Extract Q&A if available
                if "qa_pairs" in doc:
                    for qa in doc["qa_pairs"]:
                        self.add_example(
                            query=qa["question"],
                            expected_output=qa["answer"],
                            context=doc.get("title", ""),
                            intent="question_answering",
                            quality_score=1.0,
                            metadata={
                                "source": "knowledge_base",
                                "document": kb_file.name
                            }
                        )
            
            logger.info(f"✅ Loaded {len(self.examples)} examples from KB")
            
        except Exception as e:
            logger.error(f"Failed to load KB: {e}")
    
    def add_manual_examples(self):
        """Add hand-curated high-quality examples"""
        logger.info("✍️ Adding manual examples...")
        
        # Coding tasks
        self.add_example(
            query="Write a Python function to calculate fibonacci numbers",
            expected_output="""def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)""",
            context="coding task",
            intent="code_generation",
            quality_score=1.0,
            metadata={"task_type": "coding", "difficulty": "easy"}
        )
        
        self.add_example(
            query="Create a REST API endpoint for user authentication",
            expected_output="""from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

class LoginRequest(BaseModel):
    username: str
    password: str

@app.post("/auth/login")
async def login(request: LoginRequest):
    # Verify credentials
    if verify_credentials(request.username, request.password):
        return {"token": generate_token(request.username)}
    raise HTTPException(status_code=401, detail="Invalid credentials")""",
            context="API development",
            intent="code_generation",
            quality_score=1.0,
            metadata={"task_type": "coding", "difficulty": "medium"}
        )
        
        # Explanations
        self.add_example(
            query="Explain how neural networks work",
            expected_output="""Neural networks are computational models inspired by the human brain. They consist of layers of interconnected nodes (neurons):

1. Input Layer: Receives raw data
2. Hidden Layers: Process information through weighted connections
3. Output Layer: Produces final predictions

Key concepts:
- Weights: Learned parameters that determine connection strength
- Activation Functions: Introduce non-linearity (e.g., ReLU, sigmoid)
- Backpropagation: Algorithm for updating weights based on errors
- Gradient Descent: Optimization method to minimize loss

Training involves feeding data through the network, calculating errors, and adjusting weights to improve accuracy.""",
            context="educational explanation",
            intent="explanation",
            quality_score=1.0,
            metadata={"task_type": "explanation", "topic": "AI/ML"}
        )
        
        # Analysis
        self.add_example(
            query="Analyze the pros and cons of microservices architecture",
            expected_output="""Microservices Architecture Analysis:

PROS:
✅ Scalability: Individual services can scale independently
✅ Flexibility: Different tech stacks per service
✅ Resilience: Failures isolated to specific services
✅ Deployment: Independent deployment cycles
✅ Team Autonomy: Teams own specific services

CONS:
❌ Complexity: Distributed system challenges
❌ Network Overhead: Inter-service communication latency
❌ Data Consistency: Managing transactions across services
❌ Testing: Integration testing more complex
❌ Monitoring: Requires sophisticated observability

Best Use Cases:
- Large, complex applications
- Teams with independent release cycles
- Need for high scalability

Avoid When:
- Small applications
- Limited DevOps maturity
- Tight coupling requirements""",
            context="technical analysis",
            intent="analysis",
            quality_score=1.0,
            metadata={"task_type": "analysis", "domain": "software_architecture"}
        )
        
        # Quick responses
        self.add_example(
            query="What's the capital of France?",
            expected_output="Paris",
            context="factual question",
            intent="quicktake",
            quality_score=1.0,
            metadata={"task_type": "factual", "difficulty": "easy"}
        )
        
        self.add_example(
            query="Current best practices for React state management?",
            expected_output="""Current React State Management Best Practices (2025):

1. **Context API** - For simple global state
2. **Zustand** - Lightweight, growing popularity
3. **Redux Toolkit** - Still strong for complex apps
4. **TanStack Query** - Server state management
5. **Jotai/Recoil** - Atomic state management

Trend: Move away from Redux for simpler alternatives unless complexity demands it.""",
            context="technical advice",
            intent="quicktake",
            quality_score=1.0,
            metadata={"task_type": "technical_advice", "recency": "current"}
        )
        
        logger.info(f"✅ Added {6} manual examples")
    
    def add_prd_based_examples(self):
        """Add examples based on PRD requirements (ST-101 to ST-111)"""
        logger.info("📋 Adding PRD-based examples...")
        
        # Trading strategy examples
        self.add_example(
            query="Generate a backtesting report for a mean reversion strategy",
            expected_output="""Backtesting Report: Mean Reversion Strategy

Period: 2024-01-01 to 2024-12-31
Initial Capital: $100,000

Performance Metrics:
- Total Return: 23.4%
- Sharpe Ratio: 1.85
- Max Drawdown: -8.3%
- Win Rate: 62%
- Total Trades: 147

Strategy Parameters:
- Lookback Period: 20 days
- Entry Threshold: 2 std deviations
- Exit Threshold: Mean
- Position Size: 5% of capital

Risk Metrics:
- VaR (95%): -2.1%
- Sortino Ratio: 2.43
- Calmar Ratio: 2.82

Conclusion: Strategy shows consistent performance with acceptable risk levels.""",
            context="trading analytics",
            intent="analysis",
            quality_score=1.0,
            metadata={"prd_id": "ST-104", "domain": "trading"}
        )
        
        # Security examples
        self.add_example(
            query="Explain API key rotation best practices",
            expected_output="""API Key Rotation Best Practices:

1. **Rotation Frequency**
   - Critical keys: Every 30 days
   - Standard keys: Every 90 days
   - Low-risk keys: Every 180 days

2. **Zero-Downtime Rotation**
   - Support dual keys temporarily
   - Gradual transition period
   - Monitor both keys during transition

3. **Automation**
   - Scheduled rotation via CI/CD
   - Automatic secret management (Vault, AWS Secrets Manager)
   - Alert on rotation failures

4. **Audit Trail**
   - Log all rotations with timestamps
   - Track key usage before/after rotation
   - Maintain rotation history

5. **Emergency Procedures**
   - Immediate rotation on suspected compromise
   - Revoke old keys after transition
   - Notify affected services""",
            context="security guidance",
            intent="explanation",
            quality_score=1.0,
            metadata={"prd_id": "ST-108", "domain": "security"}
        )
        
        logger.info(f"✅ Added PRD-based examples")
    
    def deduplicate(self):
        """Remove duplicate examples"""
        before = len(self.examples)
        
        # Use query as dedup key
        seen_queries = set()
        deduped = []
        
        for ex in self.examples:
            query_key = ex["query"].lower().strip()
            if query_key not in seen_queries:
                seen_queries.add(query_key)
                deduped.append(ex)
        
        self.examples = deduped
        after = len(self.examples)
        
        if before != after:
            logger.info(f"🗑️ Removed {before - after} duplicates")
    
    def filter_quality(self, min_score: float = 0.8):
        """Keep only high-quality examples"""
        before = len(self.examples)
        
        self.examples = [
            ex for ex in self.examples 
            if ex.get("quality_score", 0) >= min_score
        ]
        
        after = len(self.examples)
        
        if before != after:
            logger.info(f"🔍 Filtered to {after} high-quality examples (removed {before - after})")
    
    def balance_categories(self, max_per_intent: int = 50):
        """Balance examples across intent categories"""
        from collections import defaultdict
        
        by_intent = defaultdict(list)
        for ex in self.examples:
            by_intent[ex["intent"]].append(ex)
        
        balanced = []
        for intent, examples in by_intent.items():
            # Keep top N by quality score
            examples.sort(key=lambda x: x.get("quality_score", 0), reverse=True)
            balanced.extend(examples[:max_per_intent])
            logger.info(f"   {intent}: {len(examples[:max_per_intent])} examples")
        
        self.examples = balanced
        logger.info(f"⚖️ Balanced dataset: {len(self.examples)} examples")
    
    def save(self):
        """Save golden dataset to file"""
        dataset = {
            "metadata": {
                "created_at": datetime.now().isoformat(),
                "total_examples": len(self.examples),
                "version": "1.0"
            },
            "examples": self.examples
        }
        
        self.output_path.write_text(json.dumps(dataset, indent=2))
        logger.info(f"💾 Saved {len(self.examples)} examples to {self.output_path}")
        
        # Print summary
        self._print_summary()
    
    def _print_summary(self):
        """Print dataset summary"""
        from collections import Counter
        
        print("\n" + "="*80)
        print("GOLDEN DATASET SUMMARY")
        print("="*80)
        
        print(f"\nTotal Examples: {len(self.examples)}")
        
        # By intent
        intents = Counter(ex["intent"] for ex in self.examples)
        print(f"\nBy Intent:")
        for intent, count in intents.most_common():
            print(f"  {intent}: {count}")
        
        # By quality
        quality_dist = {
            "excellent (1.0)": sum(1 for ex in self.examples if ex["quality_score"] == 1.0),
            "high (0.9-0.99)": sum(1 for ex in self.examples if 0.9 <= ex["quality_score"] < 1.0),
            "good (0.8-0.89)": sum(1 for ex in self.examples if 0.8 <= ex["quality_score"] < 0.9),
        }
        print(f"\nBy Quality:")
        for level, count in quality_dist.items():
            print(f"  {level}: {count}")
        
        # By source
        sources = Counter(ex.get("metadata", {}).get("source", "manual") for ex in self.examples)
        print(f"\nBy Source:")
        for source, count in sources.most_common():
            print(f"  {source}: {count}")
        
        print("\n" + "="*80 + "\n")


def main():
    """Build golden dataset"""
    logger.info("🚀 Building Golden Dataset for Evolutionary Optimization")
    
    builder = GoldenDatasetBuilder(
        output_path=Path("data/golden_dataset.json")
    )
    
    # Add from various sources
    builder.add_manual_examples()
    builder.add_prd_based_examples()
    
    # Optional: Load from logs (if available)
    log_path = Path("logs/production_responses.json")
    if log_path.exists():
        builder.load_from_logs(log_path)
    
    # Optional: Load from knowledge base
    kb_path = Path("knowledge_base")
    if kb_path.exists():
        builder.load_from_knowledge_base(kb_path)
    
    # Clean up
    builder.deduplicate()
    builder.filter_quality(min_score=0.8)
    builder.balance_categories(max_per_intent=50)
    
    # Save
    builder.save()
    
    logger.info("✅ Golden dataset built successfully!")
    logger.info(f"📍 Location: {builder.output_path}")
    logger.info(f"📊 Size: {len(builder.examples)} examples")


if __name__ == "__main__":
    main()

