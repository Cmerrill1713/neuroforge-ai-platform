#!/usr/bin/env python3
"""
Lightweight Document Agent
Resource-efficient agent for document processing with existing grading system integration
"""

import asyncio
import json
import logging
import os
import time
import psutil
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import requests
import redis
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel

# Import your existing grading system
try:
    from src.core.assessment.grading_integration import GradingIntegrationSystem, UnifiedGrade
    from src.core.monitoring.model_grading_system import grade_response, GradeLevel
    GRADING_AVAILABLE = True
except ImportError:
    GRADING_AVAILABLE = False
    logger.warning("⚠️ Existing grading system not available - using basic monitoring")

# Configure minimal logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/agent.log") if os.path.exists("logs") else logging.StreamHandler(),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class AgentConfig:
    """Lightweight agent configuration"""
    agent_id: str = os.getenv("AGENT_ID", "doc-agent-001")
    max_memory_mb: int = int(os.getenv("MAX_MEMORY_MB", "512"))
    max_cpu_percent: int = int(os.getenv("MAX_CPU_PERCENT", "50"))
    batch_size: int = int(os.getenv("BATCH_SIZE", "10"))
    max_concurrent_tasks: int = int(os.getenv("MAX_CONCURRENT_TASKS", "2"))
    weaviate_host: str = os.getenv("WEAVIATE_HOST", "weaviate")
    weaviate_http_port: int = int(os.getenv("WEAVIATE_HTTP_PORT", "8090"))
    knowledge_base_url: str = os.getenv("KNOWLEDGE_BASE_URL", "http://knowledge-base:8004")
    redis_url: str = os.getenv("REDIS_URL", "redis://redis:6379")

class ResourceMonitor:
    """Monitor agent resource usage"""
    
    def __init__(self, config: AgentConfig):
        self.config = config
        self.process = psutil.Process()
        
    def get_memory_usage(self) -> float:
        """Get memory usage in MB"""
        return self.process.memory_info().rss / 1024 / 1024
    
    def get_cpu_usage(self) -> float:
        """Get CPU usage percentage"""
        return self.process.cpu_percent()
    
    def is_resource_healthy(self) -> bool:
        """Check if resources are within limits"""
        memory_mb = self.get_memory_usage()
        cpu_percent = self.get_cpu_usage()
        
        memory_ok = memory_mb < self.config.max_memory_mb
        cpu_ok = cpu_percent < self.config.max_cpu_percent
        
        if not memory_ok:
            logger.warning(f"⚠️ Memory usage high: {memory_mb:.1f}MB / {self.config.max_memory_mb}MB")
        if not cpu_ok:
            logger.warning(f"⚠️ CPU usage high: {cpu_percent:.1f}% / {self.config.max_cpu_percent}%")
            
        return memory_ok and cpu_ok
    
    def get_resource_status(self) -> Dict[str, Any]:
        """Get current resource status"""
        return {
            "memory_mb": round(self.get_memory_usage(), 1),
            "memory_limit_mb": self.config.max_memory_mb,
            "cpu_percent": round(self.get_cpu_usage(), 1),
            "cpu_limit_percent": self.config.max_cpu_percent,
            "healthy": self.is_resource_healthy()
        }

class LightweightDocumentAgent:
    """Lightweight Document Processing Agent"""
    
    def __init__(self, config: AgentConfig):
        self.config = config
        self.app = FastAPI(title="Lightweight Document Agent", version="1.0.0")
        self.redis_client = None
        self.resource_monitor = ResourceMonitor(config)
        self.active_tasks = 0
        self.documents_processed = 0
        self.last_grading_report = None
        
        # Initialize grading system if available
        if GRADING_AVAILABLE:
            self.grading_system = GradingIntegrationSystem()
            logger.info("✅ Integrated with existing grading system")
        else:
            self.grading_system = None
            logger.warning("⚠️ Using basic monitoring (grading system not available)")
        
        # Setup routes
        self._setup_routes()
        
    def _setup_routes(self):
        """Setup FastAPI routes"""
        
        @self.app.get("/health")
        async def health_check():
            """Health check with resource monitoring"""
            resource_status = self.resource_monitor.get_resource_status()
            
            if not resource_status["healthy"]:
                return {
                    "status": "unhealthy",
                    "agent_id": self.config.agent_id,
                    "resources": resource_status,
                    "message": "Resource limits exceeded"
                }
            
            return {
                "status": "healthy",
                "agent_id": self.config.agent_id,
                "resources": resource_status,
                "active_tasks": self.active_tasks,
                "documents_processed": self.documents_processed
            }
        
        @self.app.get("/status")
        async def get_status():
            """Get detailed agent status"""
            return {
                "agent_id": self.config.agent_id,
                "resources": self.resource_monitor.get_resource_status(),
                "active_tasks": self.active_tasks,
                "documents_processed": self.documents_processed,
                "last_grading_report": self.last_grading_report,
                "timestamp": datetime.now().isoformat()
            }
        
        @self.app.post("/migrate")
        async def migrate_documents(request: Dict[str, Any], background_tasks: BackgroundTasks):
            """Start lightweight document migration"""
            try:
                # Check resource limits before starting
                if not self.resource_monitor.is_resource_healthy():
                    raise HTTPException(
                        status_code=429, 
                        detail="Resource limits exceeded. Cannot start migration."
                    )
                
                # Check concurrent task limit
                if self.active_tasks >= self.config.max_concurrent_tasks:
                    raise HTTPException(
                        status_code=429,
                        detail=f"Maximum concurrent tasks ({self.config.max_concurrent_tasks}) reached"
                    )
                
                # Start migration task
                background_tasks.add_task(self._migrate_documents_task, request)
                
                return {
                    "message": "Migration started",
                    "agent_id": self.config.agent_id,
                    "batch_size": self.config.batch_size,
                    "resource_status": self.resource_monitor.get_resource_status()
                }
                
            except Exception as e:
                logger.error(f"❌ Failed to start migration: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/grading/report")
        async def get_grading_report():
            """Get grading system report using existing grading system"""
            try:
                if self.grading_system:
                    # Use existing grading system to assess agent performance
                    agent_performance = await self._assess_agent_performance()
                    self.last_grading_report = agent_performance
                    return agent_performance
                else:
                    return {
                        "agent_id": self.config.agent_id,
                        "status": "basic_monitoring",
                        "message": "Using basic monitoring - grading system not available",
                        "resources": self.resource_monitor.get_resource_status(),
                        "documents_processed": self.documents_processed
                    }
            except Exception as e:
                return {"error": f"Failed to get grading report: {e}"}
    
    async def initialize(self):
        """Initialize lightweight agent"""
        try:
            logger.info(f"🤖 Initializing Lightweight Document Agent: {self.config.agent_id}")
            
            # Connect to Redis (lightweight connection)
            self.redis_client = redis.from_url(self.config.redis_url, decode_responses=True)
            await self._test_redis_connection()
            
            # Register with grading system
            await self._register_with_grading_system()
            
            logger.info("✅ Lightweight Document Agent initialized successfully")
            logger.info(f"📊 Resource limits: {self.config.max_memory_mb}MB RAM, {self.config.max_cpu_percent}% CPU")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize agent: {e}")
            raise
    
    async def _test_redis_connection(self):
        """Test Redis connection"""
        try:
            self.redis_client.ping()
            logger.info("✅ Redis connection successful")
        except Exception as e:
            logger.error(f"❌ Redis connection failed: {e}")
            raise
    
    async def _register_with_grading_system(self):
        """Register agent with existing grading system"""
        try:
            if self.grading_system:
                # Store agent info in Redis for grading system access
                agent_info = {
                    "agent_id": self.config.agent_id,
                    "agent_type": "document_processor",
                    "resource_limits": {
                        "max_memory_mb": self.config.max_memory_mb,
                        "max_cpu_percent": self.config.max_cpu_percent,
                        "max_concurrent_tasks": self.config.max_concurrent_tasks
                    },
                    "capabilities": ["document_migration", "resource_monitoring"],
                    "registered_at": datetime.now().isoformat()
                }
                
                # Store in Redis for grading system to access
                self.redis_client.setex(
                    f"agent:info:{self.config.agent_id}", 
                    3600, 
                    json.dumps(agent_info)
                )
                
                logger.info("✅ Registered with existing grading system")
            else:
                logger.info("ℹ️ Using basic monitoring mode")
                
        except Exception as e:
            logger.warning(f"⚠️ Could not register with grading system: {e}")
    
    async def _migrate_documents_task(self, request: Dict[str, Any]):
        """Lightweight document migration task"""
        try:
            self.active_tasks += 1
            logger.info(f"🚀 Starting lightweight migration (Task {self.active_tasks})")
            
            # Get documents from knowledge base (small batches)
            documents = await self._get_documents_batch()
            logger.info(f"📚 Retrieved {len(documents)} documents")
            
            # Process documents in small batches
            processed_count = 0
            for i in range(0, len(documents), self.config.batch_size):
                batch = documents[i:i + self.config.batch_size]
                
                # Check resources before processing batch
                if not self.resource_monitor.is_resource_healthy():
                    logger.warning("⚠️ Resource limits exceeded, pausing migration")
                    await asyncio.sleep(30)  # Wait for resources to free up
                    continue
                
                # Process batch
                batch_processed = await self._process_document_batch(batch)
                processed_count += batch_processed
                
                # Report progress to grading system
                await self._report_progress_to_grading_system(processed_count, len(documents))
                
                # Small delay to prevent resource overload
                await asyncio.sleep(1)
            
            # Update counters
            self.documents_processed += processed_count
            self.active_tasks -= 1
            
            logger.info(f"✅ Migration completed: {processed_count} documents processed")
            
        except Exception as e:
            logger.error(f"❌ Migration task failed: {e}")
            self.active_tasks -= 1
    
    async def _get_documents_batch(self) -> List[Dict[str, Any]]:
        """Get a batch of documents from knowledge base with varied queries"""
        try:
            # Use different search terms to get variety
            search_terms = ["python", "machine learning", "artificial intelligence", "data science", "programming", "algorithm", "database", "web development", "api", "docker"]
            import random
            search_term = random.choice(search_terms)
            
            # Use unified search endpoint to get documents from all knowledge bases
            response = requests.get(
                f"{self.config.knowledge_base_url}/unified-search",
                params={
                    "q": search_term,
                    "limit": self.config.batch_size * 2  # Get more documents
                },
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                results = data.get('results', [])
                
                # Convert to document format
                documents = []
                seen_urls = set()
                
                for result in results:
                    url = result.get('url', '')
                    if url and url not in seen_urls:
                        doc = {
                            "content": result.get('content', ''),
                            "title": result.get('title', 'Unknown'),
                            "url": url,
                            "source_type": result.get('source_type', 'migrated'),
                            "domain": result.get('domain', 'knowledge_base'),
                            "keywords": ["python", "migrated"]
                        }
                        documents.append(doc)
                        seen_urls.add(url)
                        
                        if len(documents) >= self.config.batch_size:
                            break
                
                logger.info(f"📚 Retrieved {len(documents)} documents from unified knowledge base")
                return documents
            else:
                logger.warning(f"⚠️ Failed to get documents: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"❌ Failed to get documents: {e}")
            return []
    
    async def _process_document_batch(self, documents: List[Dict[str, Any]]) -> int:
        """Process a batch of documents"""
        processed_count = 0
        
        for doc in documents:
            try:
                # Simple document processing
                doc["processed_at"] = datetime.now().isoformat()
                doc["agent_id"] = self.config.agent_id
                doc["processing_version"] = "lightweight-1.0"
                
                # Store in Redis cache (lightweight)
                cache_key = f"doc:{doc['url']}"
                self.redis_client.setex(cache_key, 3600, json.dumps(doc))
                
                processed_count += 1
                
            except Exception as e:
                logger.warning(f"⚠️ Failed to process document {doc.get('title', 'Unknown')}: {e}")
                continue
        
        return processed_count
    
    async def _report_progress_to_grading_system(self, processed: int, total: int):
        """Report progress to existing grading system"""
        try:
            progress_data = {
                "agent_id": self.config.agent_id,
                "task_type": "document_migration",
                "progress": {
                    "processed": processed,
                    "total": total,
                    "percentage": round((processed / total) * 100, 1) if total > 0 else 0
                },
                "resources": self.resource_monitor.get_resource_status(),
                "timestamp": datetime.now().isoformat()
            }
            
            # Store progress in Redis for grading system access
            self.redis_client.setex(
                f"agent:progress:{self.config.agent_id}", 
                300, 
                json.dumps(progress_data)
            )
            
        except Exception as e:
            logger.warning(f"⚠️ Failed to report progress: {e}")
    
    async def _assess_agent_performance(self) -> Dict[str, Any]:
        """Assess agent performance using existing grading system"""
        try:
            if not self.grading_system:
                return {"error": "Grading system not available"}
            
            # Create a mock response for agent performance assessment
            agent_response = f"""
            Agent Performance Summary:
            - Agent ID: {self.config.agent_id}
            - Documents Processed: {self.documents_processed}
            - Active Tasks: {self.active_tasks}
            - Resource Status: {self.resource_monitor.get_resource_status()}
            - Last Activity: {datetime.now().isoformat()}
            """
            
            # Use existing grading system to assess agent performance
            unified_grade = await self.grading_system.unified_assessment(
                model_name=f"agent-{self.config.agent_id}",
                prompt="Assess agent performance and resource efficiency",
                response=agent_response,
                confidence=0.8,  # High confidence in agent reporting
                fallback_used=False,
                security_flags=0,
                context={
                    "agent_type": "document_processor",
                    "documents_processed": self.documents_processed,
                    "resource_status": self.resource_monitor.get_resource_status()
                }
            )
            
            return {
                "agent_id": self.config.agent_id,
                "overall_grade": unified_grade.overall_grade.value,
                "numeric_score": unified_grade.numeric_score,
                "confidence_level": unified_grade.confidence_level,
                "risk_level": unified_grade.risk_level,
                "recommended_actions": unified_grade.recommended_actions,
                "quality_metrics": {k.value: v for k, v in unified_grade.quality_metrics.items()},
                "resources": self.resource_monitor.get_resource_status(),
                "documents_processed": self.documents_processed,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to assess agent performance: {e}")
            return {
                "agent_id": self.config.agent_id,
                "error": str(e),
                "fallback_status": "basic_monitoring",
                "resources": self.resource_monitor.get_resource_status()
            }
    
    async def start_document_processing(self):
        """Start active document processing loop"""
        logger.info("🔄 Starting document processing loop...")
        
        while True:
            try:
                # Check if we have capacity for more tasks
                if self.active_tasks >= self.config.max_concurrent_tasks:
                    await asyncio.sleep(5)  # Wait 5 seconds before checking again
                    continue
                
                # Get documents to process
                documents = await self._get_documents_batch()
                
                if documents:
                    logger.info(f"📚 Processing {len(documents)} documents...")
                    
                    # Process documents concurrently
                    tasks = []
                    for doc in documents:
                        if self.active_tasks < self.config.max_concurrent_tasks:
                            task = asyncio.create_task(self._process_document(doc))
                            tasks.append(task)
                            self.active_tasks += 1
                    
                    # Wait for all tasks to complete
                    if tasks:
                        await asyncio.gather(*tasks, return_exceptions=True)
                        logger.info(f"✅ Completed processing {len(tasks)} documents")
                
                # Wait before next batch
                await asyncio.sleep(10)  # Process every 10 seconds
                
            except Exception as e:
                logger.error(f"❌ Document processing failed: {e}")
                await asyncio.sleep(10)
    
    async def _process_document(self, document: Dict[str, Any]):
        """Process a single document with CPU-intensive work"""
        try:
            # Simulate more intensive document processing
            content = document.get('content', '')
            
            # CPU-intensive operations
            # 1. Text analysis
            words = content.split()
            word_count = len(words)
            
            # 2. Character frequency analysis
            char_freq = {}
            for char in content.lower():
                char_freq[char] = char_freq.get(char, 0) + 1
            
            # 3. Simple text processing simulation
            processed_content = ""
            for i, word in enumerate(words):
                if i % 100 == 0:  # Process every 100th word intensively
                    # Simulate complex processing
                    processed_word = word.upper() + str(len(word)) + str(hash(word) % 1000)
                    processed_content += processed_word + " "
                else:
                    processed_content += word + " "
            
            # 4. Simulate some computation
            import time
            start_time = time.time()
            while time.time() - start_time < 0.05:  # 50ms of CPU work
                # Simulate computation
                dummy = sum(i * i for i in range(100))
            
            # Update metrics
            self.documents_processed += 1
            
            # Report progress
            await self._report_progress_to_grading_system(
                self.documents_processed,
                self.documents_processed + 50  # Estimate remaining
            )
            
            logger.debug(f"📄 Processed document: {document.get('title', 'Unknown')} ({word_count} words)")
            
        except Exception as e:
            logger.error(f"❌ Failed to process document: {e}")
        finally:
            self.active_tasks -= 1

    async def start_resource_monitoring(self):
        """Start resource monitoring"""
        while True:
            try:
                # Check resources every 30 seconds
                resource_status = self.resource_monitor.get_resource_status()
                
                if not resource_status["healthy"]:
                    logger.warning(f"⚠️ Resource warning: {resource_status}")
                
                # Report to grading system
                await self._report_progress_to_grading_system(
                    self.documents_processed, 
                    self.documents_processed + 100  # Estimate
                )
                
                await asyncio.sleep(30)
                
            except Exception as e:
                logger.error(f"❌ Resource monitoring failed: {e}")
                await asyncio.sleep(30)
    
    async def run(self):
        """Run the lightweight agent"""
        try:
            # Initialize
            await self.initialize()
            
            # Start resource monitoring
            monitoring_task = asyncio.create_task(self.start_resource_monitoring())
            
            # Start document processing
            processing_task = asyncio.create_task(self.start_document_processing())
            
            # Start FastAPI server
            import uvicorn
            config = uvicorn.Config(
                self.app,
                host="0.0.0.0",
                port=8010,
                log_level="info",
                workers=1  # Single worker for resource efficiency
            )
            server = uvicorn.Server(config)
            
            # Run server
            await server.serve()
            
        except Exception as e:
            logger.error(f"❌ Agent failed: {e}")
            raise

async def main():
    """Main function"""
    config = AgentConfig()
    agent = LightweightDocumentAgent(config)
    await agent.run()

if __name__ == "__main__":
    asyncio.run(main())
