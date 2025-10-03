#!/usr/bin/env python3
"""
Document Processing Agent
Handles document migration, processing, and management in Docker environment
"""

import asyncio
import json
import logging
import os
import time
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import requests
import redis
import weaviate
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
import psycopg2
from psycopg2.extras import RealDictCursor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("/app/logs/document_agent.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class AgentConfig:
    """Agent configuration"""
    agent_id: str = os.getenv("AGENT_ID", "doc-processor-001")
    agent_role: str = os.getenv("AGENT_ROLE", "document_migration")
    weaviate_host: str = os.getenv("WEAVIATE_HOST", "weaviate")
    weaviate_http_port: int = int(os.getenv("WEAVIATE_HTTP_PORT", "8090"))
    weaviate_grpc_port: int = int(os.getenv("WEAVIATE_GRPC_PORT", "50051"))
    knowledge_base_url: str = os.getenv("KNOWLEDGE_BASE_URL", "http://knowledge-base:8004")
    redis_url: str = os.getenv("REDIS_URL", "redis://redis:6379")
    postgres_url: str = os.getenv("POSTGRES_URL", "postgresql://postgres:password@postgres:5432/agentic_platform")
    log_level: str = os.getenv("LOG_LEVEL", "INFO")

class DocumentMigrationRequest(BaseModel):
    """Request model for document migration"""
    source_system: str = "knowledge_base"
    target_system: str = "weaviate"
    batch_size: int = 50
    max_documents: Optional[int] = None
    search_terms: List[str] = []

class AgentStatus(BaseModel):
    """Agent status model"""
    agent_id: str
    status: str
    role: str
    last_heartbeat: str
    tasks_completed: int
    documents_processed: int
    errors: int

class DocumentProcessingAgent:
    """Document Processing Agent"""
    
    def __init__(self, config: AgentConfig):
        self.config = config
        self.app = FastAPI(title="Document Processing Agent", version="1.0.0")
        self.redis_client = None
        self.weaviate_client = None
        self.postgres_conn = None
        self.status = {
            "agent_id": config.agent_id,
            "status": "initializing",
            "role": config.agent_role,
            "last_heartbeat": datetime.now().isoformat(),
            "tasks_completed": 0,
            "documents_processed": 0,
            "errors": 0
        }
        
        # Setup routes
        self._setup_routes()
        
    def _setup_routes(self):
        """Setup FastAPI routes"""
        
        @self.app.get("/health")
        async def health_check():
            """Health check endpoint"""
            return {"status": "healthy", "agent_id": self.config.agent_id}
        
        @self.app.get("/status")
        async def get_status():
            """Get agent status"""
            return self.status
        
        @self.app.post("/migrate")
        async def migrate_documents(request: DocumentMigrationRequest, background_tasks: BackgroundTasks):
            """Start document migration"""
            try:
                background_tasks.add_task(self._migrate_documents_task, request)
                return {"message": "Migration started", "task_id": f"migrate_{int(time.time())}"}
            except Exception as e:
                logger.error(f"Failed to start migration: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/migration/progress")
        async def get_migration_progress():
            """Get migration progress"""
            try:
                progress = await self._get_migration_progress()
                return progress
            except Exception as e:
                logger.error(f"Failed to get progress: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/process/documents")
        async def process_documents(background_tasks: BackgroundTasks):
            """Process documents from knowledge base"""
            try:
                background_tasks.add_task(self._process_documents_task)
                return {"message": "Document processing started"}
            except Exception as e:
                logger.error(f"Failed to start processing: {e}")
                raise HTTPException(status_code=500, detail=str(e))
    
    async def initialize(self):
        """Initialize agent connections"""
        try:
            logger.info(f"🤖 Initializing Document Processing Agent: {self.config.agent_id}")
            
            # Connect to Redis
            self.redis_client = redis.from_url(self.config.redis_url)
            await self._test_redis_connection()
            
            # Connect to Weaviate
            await self._connect_to_weaviate()
            
            # Connect to PostgreSQL
            await self._connect_to_postgres()
            
            # Update status
            self.status["status"] = "ready"
            self.status["last_heartbeat"] = datetime.now().isoformat()
            
            logger.info("✅ Document Processing Agent initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize agent: {e}")
            self.status["status"] = "error"
            self.status["errors"] += 1
            raise
    
    async def _test_redis_connection(self):
        """Test Redis connection"""
        try:
            self.redis_client.ping()
            logger.info("✅ Redis connection successful")
        except Exception as e:
            logger.error(f"❌ Redis connection failed: {e}")
            raise
    
    async def _connect_to_weaviate(self):
        """Connect to Weaviate"""
        try:
            self.weaviate_client = weaviate.connect_to_custom(
                http_host=self.config.weaviate_host,
                http_port=self.config.weaviate_http_port,
                grpc_host=self.config.weaviate_host,
                grpc_port=self.config.weaviate_grpc_port,
                http_secure=False,
                grpc_secure=False
            )
            logger.info("✅ Weaviate connection successful")
        except Exception as e:
            logger.error(f"❌ Weaviate connection failed: {e}")
            raise
    
    async def _connect_to_postgres(self):
        """Connect to PostgreSQL"""
        try:
            self.postgres_conn = psycopg2.connect(self.config.postgres_url)
            logger.info("✅ PostgreSQL connection successful")
        except Exception as e:
            logger.error(f"❌ PostgreSQL connection failed: {e}")
            raise
    
    async def _migrate_documents_task(self, request: DocumentMigrationRequest):
        """Background task for document migration"""
        try:
            logger.info(f"🚀 Starting document migration: {request.source_system} -> {request.target_system}")
            
            # Get documents from source system
            documents = await self._get_documents_from_source(request)
            logger.info(f"📚 Retrieved {len(documents)} documents from {request.source_system}")
            
            # Migrate to target system
            migrated_count = await self._migrate_to_target(documents, request)
            
            # Update status
            self.status["tasks_completed"] += 1
            self.status["documents_processed"] += migrated_count
            
            logger.info(f"✅ Migration completed: {migrated_count} documents migrated")
            
        except Exception as e:
            logger.error(f"❌ Migration task failed: {e}")
            self.status["errors"] += 1
    
    async def _get_documents_from_source(self, request: DocumentMigrationRequest) -> List[Dict[str, Any]]:
        """Get documents from source system"""
        if request.source_system == "knowledge_base":
            return await self._get_documents_from_knowledge_base(request)
        else:
            raise ValueError(f"Unsupported source system: {request.source_system}")
    
    async def _get_documents_from_knowledge_base(self, request: DocumentMigrationRequest) -> List[Dict[str, Any]]:
        """Get documents from knowledge base using search"""
        all_documents = []
        seen_urls = set()
        
        # Use provided search terms or default ones
        search_terms = request.search_terms or [
            "test", "document", "content", "data", "information", "text", "file",
            "github", "wikipedia", "youtube", "api", "docker", "python", "javascript",
            "machine learning", "artificial intelligence", "programming", "development"
        ]
        
        for term in search_terms:
            try:
                response = requests.post(
                    f"{self.config.knowledge_base_url}/api/knowledge/search",
                    json={"query": term, "limit": 100},
                    timeout=30
                )
                
                if response.status_code == 200:
                    results = response.json().get('results', [])
                    logger.info(f"🔍 Search '{term}': found {len(results)} results")
                    
                    for result in results:
                        url = result.get('url', '')
                        if url and url not in seen_urls:
                            doc = {
                                "content": result.get('content', ''),
                                "title": result.get('source', 'Unknown'),
                                "url": url,
                                "source_type": "migrated",
                                "domain": "knowledge_base",
                                "keywords": [term]
                            }
                            all_documents.append(doc)
                            seen_urls.add(url)
                            
                            # Check max documents limit
                            if request.max_documents and len(all_documents) >= request.max_documents:
                                return all_documents
                
            except Exception as e:
                logger.warning(f"⚠️ Search failed for '{term}': {e}")
                continue
        
        return all_documents
    
    async def _migrate_to_target(self, documents: List[Dict[str, Any]], request: DocumentMigrationRequest) -> int:
        """Migrate documents to target system"""
        if request.target_system == "weaviate":
            return await self._migrate_to_weaviate(documents, request)
        else:
            raise ValueError(f"Unsupported target system: {request.target_system}")
    
    async def _migrate_to_weaviate(self, documents: List[Dict[str, Any]], request: DocumentMigrationRequest) -> int:
        """Migrate documents to Weaviate"""
        try:
            # Ensure collection exists
            await self._ensure_weaviate_collection()
            
            collection = self.weaviate_client.collections.get("KnowledgeDocument")
            migrated_count = 0
            
            # Process in batches
            for i in range(0, len(documents), request.batch_size):
                batch = documents[i:i + request.batch_size]
                logger.info(f"📦 Processing batch {i//request.batch_size + 1}/{(len(documents)-1)//request.batch_size + 1}")
                
                with collection.batch() as batch_client:
                    for doc in batch:
                        try:
                            weaviate_doc = {
                                "content": doc.get("content", ""),
                                "title": doc.get("title", "Unknown"),
                                "url": doc.get("url", ""),
                                "source_type": doc.get("source_type", "unknown"),
                                "domain": doc.get("domain", "unknown"),
                                "keywords": doc.get("keywords", [])
                            }
                            
                            batch_client.add_data_object(
                                data_object=weaviate_doc,
                                class_name="KnowledgeDocument"
                            )
                            migrated_count += 1
                            
                        except Exception as e:
                            logger.warning(f"⚠️ Failed to migrate document {doc.get('title', 'Unknown')}: {e}")
                            continue
                
                logger.info(f"✅ Migrated batch, total: {migrated_count}")
            
            return migrated_count
            
        except Exception as e:
            logger.error(f"❌ Weaviate migration failed: {e}")
            raise
    
    async def _ensure_weaviate_collection(self):
        """Ensure KnowledgeDocument collection exists"""
        try:
            collection = self.weaviate_client.collections.get("KnowledgeDocument")
            logger.info("✅ KnowledgeDocument collection exists")
        except:
            # Create collection
            collection = self.weaviate_client.collections.create(
                name="KnowledgeDocument",
                description="Migrated documents from knowledge base",
                properties=[
                    weaviate.classes.config.Property(
                        name="content",
                        data_type=weaviate.classes.config.DataType.TEXT,
                        description="Document content"
                    ),
                    weaviate.classes.config.Property(
                        name="title", 
                        data_type=weaviate.classes.config.DataType.TEXT,
                        description="Document title"
                    ),
                    weaviate.classes.config.Property(
                        name="url",
                        data_type=weaviate.classes.config.DataType.TEXT,
                        description="Document URL"
                    ),
                    weaviate.classes.config.Property(
                        name="source_type",
                        data_type=weaviate.classes.config.DataType.TEXT,
                        description="Source type"
                    ),
                    weaviate.classes.config.Property(
                        name="domain",
                        data_type=weaviate.classes.config.DataType.TEXT,
                        description="Document domain"
                    ),
                    weaviate.classes.config.Property(
                        name="keywords",
                        data_type=weaviate.classes.config.DataType.TEXT_ARRAY,
                        description="Document keywords"
                    )
                ]
            )
            logger.info("✅ Created KnowledgeDocument collection")
    
    async def _process_documents_task(self):
        """Background task for document processing"""
        try:
            logger.info("🔄 Starting document processing task")
            
            # Get documents from knowledge base
            request = DocumentMigrationRequest()
            documents = await self._get_documents_from_knowledge_base(request)
            
            # Process and enhance documents
            processed_count = await self._process_and_enhance_documents(documents)
            
            # Update status
            self.status["tasks_completed"] += 1
            self.status["documents_processed"] += processed_count
            
            logger.info(f"✅ Document processing completed: {processed_count} documents processed")
            
        except Exception as e:
            logger.error(f"❌ Document processing task failed: {e}")
            self.status["errors"] += 1
    
    async def _process_and_enhance_documents(self, documents: List[Dict[str, Any]]) -> int:
        """Process and enhance documents"""
        processed_count = 0
        
        for doc in documents:
            try:
                # Add processing metadata
                doc["processed_at"] = datetime.now().isoformat()
                doc["agent_id"] = self.config.agent_id
                doc["processing_version"] = "1.0"
                
                # Store in Redis for caching
                cache_key = f"doc:{doc['url']}"
                self.redis_client.setex(cache_key, 3600, json.dumps(doc))
                
                processed_count += 1
                
            except Exception as e:
                logger.warning(f"⚠️ Failed to process document {doc.get('title', 'Unknown')}: {e}")
                continue
        
        return processed_count
    
    async def _get_migration_progress(self) -> Dict[str, Any]:
        """Get migration progress"""
        try:
            # Get current Weaviate document count
            collection = self.weaviate_client.collections.get("KnowledgeDocument")
            weaviate_count = collection.aggregate.over_all(total_count=True).total_count
            
            # Get knowledge base stats
            response = requests.get(f"{self.config.knowledge_base_url}/api/knowledge/stats")
            kb_stats = response.json() if response.status_code == 200 else {}
            
            return {
                "weaviate_documents": weaviate_count,
                "knowledge_base_documents": kb_stats.get("total_documents", 0),
                "migration_progress": f"{weaviate_count}/{kb_stats.get('total_documents', 0)}",
                "agent_status": self.status
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get migration progress: {e}")
            return {"error": str(e)}
    
    async def start_heartbeat(self):
        """Start heartbeat to update status"""
        while True:
            try:
                self.status["last_heartbeat"] = datetime.now().isoformat()
                
                # Store status in Redis
                status_key = f"agent:status:{self.config.agent_id}"
                self.redis_client.setex(status_key, 60, json.dumps(self.status))
                
                await asyncio.sleep(30)  # Heartbeat every 30 seconds
                
            except Exception as e:
                logger.error(f"❌ Heartbeat failed: {e}")
                await asyncio.sleep(30)
    
    async def run(self):
        """Run the agent"""
        try:
            # Initialize
            await self.initialize()
            
            # Start heartbeat
            heartbeat_task = asyncio.create_task(self.start_heartbeat())
            
            # Start FastAPI server
            import uvicorn
            config = uvicorn.Config(
                self.app,
                host="0.0.0.0",
                port=8006,
                log_level="info"
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
    agent = DocumentProcessingAgent(config)
    await agent.run()

if __name__ == "__main__":
    asyncio.run(main())
