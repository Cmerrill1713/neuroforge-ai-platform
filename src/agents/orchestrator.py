#!/usr/bin/env python3
"""
Agent Orchestrator
Manages and coordinates multiple agents in the Docker environment
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
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
import psycopg2
from psycopg2.extras import RealDictCursor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("/app/logs/orchestrator.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class OrchestratorConfig:
    """Orchestrator configuration"""
    orchestrator_id: str = os.getenv("ORCHESTRATOR_ID", "orchestrator-001")
    redis_url: str = os.getenv("REDIS_URL", "redis://redis:6379")
    postgres_url: str = os.getenv("POSTGRES_URL", "postgresql://postgres:password@postgres:5432/agentic_platform")
    weaviate_host: str = os.getenv("WEAVIATE_HOST", "weaviate")
    log_level: str = os.getenv("LOG_LEVEL", "INFO")

class AgentTask(BaseModel):
    """Agent task model"""
    task_id: str
    agent_id: str
    task_type: str
    parameters: Dict[str, Any]
    status: str = "pending"
    created_at: str
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class OrchestratorStatus(BaseModel):
    """Orchestrator status model"""
    orchestrator_id: str
    status: str
    agents_registered: int
    tasks_completed: int
    tasks_failed: int
    last_heartbeat: str

class AgentOrchestrator:
    """Agent Orchestrator"""
    
    def __init__(self, config: OrchestratorConfig):
        self.config = config
        self.app = FastAPI(title="Agent Orchestrator", version="1.0.0")
        self.redis_client = None
        self.postgres_conn = None
        self.registered_agents = {}
        self.active_tasks = {}
        self.status = {
            "orchestrator_id": config.orchestrator_id,
            "status": "initializing",
            "agents_registered": 0,
            "tasks_completed": 0,
            "tasks_failed": 0,
            "last_heartbeat": datetime.now().isoformat()
        }
        
        # Setup routes
        self._setup_routes()
        
    def _setup_routes(self):
        """Setup FastAPI routes"""
        
        @self.app.get("/health")
        async def health_check():
            """Health check endpoint"""
            return {"status": "healthy", "orchestrator_id": self.config.orchestrator_id}
        
        @self.app.get("/status")
        async def get_status():
            """Get orchestrator status"""
            return self.status
        
        @self.app.get("/agents")
        async def get_agents():
            """Get registered agents"""
            return {"agents": list(self.registered_agents.values())}
        
        @self.app.post("/agents/register")
        async def register_agent(agent_data: Dict[str, Any]):
            """Register a new agent"""
            try:
                agent_id = agent_data.get("agent_id")
                if not agent_id:
                    raise HTTPException(status_code=400, detail="agent_id is required")
                
                self.registered_agents[agent_id] = {
                    "agent_id": agent_id,
                    "role": agent_data.get("role", "unknown"),
                    "status": agent_data.get("status", "unknown"),
                    "registered_at": datetime.now().isoformat(),
                    "last_heartbeat": datetime.now().isoformat()
                }
                
                self.status["agents_registered"] = len(self.registered_agents)
                
                logger.info(f"✅ Agent registered: {agent_id}")
                return {"message": f"Agent {agent_id} registered successfully"}
                
            except Exception as e:
                logger.error(f"❌ Failed to register agent: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/tasks/create")
        async def create_task(task_data: Dict[str, Any]):
            """Create a new task"""
            try:
                task_id = f"task_{int(time.time())}_{task_data.get('agent_id', 'unknown')}"
                
                task = AgentTask(
                    task_id=task_id,
                    agent_id=task_data.get("agent_id"),
                    task_type=task_data.get("task_type"),
                    parameters=task_data.get("parameters", {}),
                    created_at=datetime.now().isoformat()
                )
                
                self.active_tasks[task_id] = task
                
                # Queue task for agent
                await self._queue_task_for_agent(task)
                
                logger.info(f"✅ Task created: {task_id}")
                return {"task_id": task_id, "status": "queued"}
                
            except Exception as e:
                logger.error(f"❌ Failed to create task: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/tasks/{task_id}")
        async def get_task(task_id: str):
            """Get task status"""
            if task_id not in self.active_tasks:
                raise HTTPException(status_code=404, detail="Task not found")
            
            return self.active_tasks[task_id]
        
        @self.app.get("/tasks")
        async def get_all_tasks():
            """Get all tasks"""
            return {"tasks": list(self.active_tasks.values())}
        
        @self.app.post("/tasks/{task_id}/complete")
        async def complete_task(task_id: str, result: Dict[str, Any]):
            """Mark task as completed"""
            if task_id not in self.active_tasks:
                raise HTTPException(status_code=404, detail="Task not found")
            
            task = self.active_tasks[task_id]
            task.status = "completed"
            task.completed_at = datetime.now().isoformat()
            task.result = result
            
            self.status["tasks_completed"] += 1
            
            logger.info(f"✅ Task completed: {task_id}")
            return {"message": "Task completed successfully"}
        
        @self.app.post("/tasks/{task_id}/fail")
        async def fail_task(task_id: str, error: str):
            """Mark task as failed"""
            if task_id not in self.active_tasks:
                raise HTTPException(status_code=404, detail="Task not found")
            
            task = self.active_tasks[task_id]
            task.status = "failed"
            task.completed_at = datetime.now().isoformat()
            task.error = error
            
            self.status["tasks_failed"] += 1
            
            logger.error(f"❌ Task failed: {task_id} - {error}")
            return {"message": "Task marked as failed"}
        
        @self.app.post("/migrate/documents")
        async def start_document_migration(background_tasks: BackgroundTasks):
            """Start document migration task"""
            try:
                # Find document processing agent
                doc_agent = None
                for agent_id, agent_data in self.registered_agents.items():
                    if agent_data.get("role") == "document_migration":
                        doc_agent = agent_id
                        break
                
                if not doc_agent:
                    raise HTTPException(status_code=404, detail="Document processing agent not found")
                
                # Create migration task
                task_data = {
                    "agent_id": doc_agent,
                    "task_type": "migrate_documents",
                    "parameters": {
                        "source_system": "knowledge_base",
                        "target_system": "weaviate",
                        "batch_size": 50,
                        "max_documents": None
                    }
                }
                
                background_tasks.add_task(self._execute_migration_task, task_data)
                
                return {"message": "Document migration started", "agent_id": doc_agent}
                
            except Exception as e:
                logger.error(f"❌ Failed to start migration: {e}")
                raise HTTPException(status_code=500, detail=str(e))
    
    async def initialize(self):
        """Initialize orchestrator"""
        try:
            logger.info(f"🎯 Initializing Agent Orchestrator: {self.config.orchestrator_id}")
            
            # Connect to Redis
            self.redis_client = redis.from_url(self.config.redis_url)
            await self._test_redis_connection()
            
            # Connect to PostgreSQL
            await self._connect_to_postgres()
            
            # Load existing agents from Redis
            await self._load_existing_agents()
            
            # Update status
            self.status["status"] = "ready"
            self.status["last_heartbeat"] = datetime.now().isoformat()
            
            logger.info("✅ Agent Orchestrator initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize orchestrator: {e}")
            self.status["status"] = "error"
            raise
    
    async def _test_redis_connection(self):
        """Test Redis connection"""
        try:
            self.redis_client.ping()
            logger.info("✅ Redis connection successful")
        except Exception as e:
            logger.error(f"❌ Redis connection failed: {e}")
            raise
    
    async def _connect_to_postgres(self):
        """Connect to PostgreSQL"""
        try:
            self.postgres_conn = psycopg2.connect(self.config.postgres_url)
            logger.info("✅ PostgreSQL connection successful")
        except Exception as e:
            logger.error(f"❌ PostgreSQL connection failed: {e}")
            raise
    
    async def _load_existing_agents(self):
        """Load existing agents from Redis"""
        try:
            # Get all agent status keys
            agent_keys = self.redis_client.keys("agent:status:*")
            
            for key in agent_keys:
                agent_data = self.redis_client.get(key)
                if agent_data:
                    agent_info = json.loads(agent_data)
                    agent_id = agent_info.get("agent_id")
                    if agent_id:
                        self.registered_agents[agent_id] = {
                            "agent_id": agent_id,
                            "role": agent_info.get("role", "unknown"),
                            "status": agent_info.get("status", "unknown"),
                            "registered_at": datetime.now().isoformat(),
                            "last_heartbeat": agent_info.get("last_heartbeat", datetime.now().isoformat())
                        }
            
            self.status["agents_registered"] = len(self.registered_agents)
            logger.info(f"📋 Loaded {len(self.registered_agents)} existing agents")
            
        except Exception as e:
            logger.warning(f"⚠️ Failed to load existing agents: {e}")
    
    async def _queue_task_for_agent(self, task: AgentTask):
        """Queue task for specific agent"""
        try:
            # Store task in Redis queue
            queue_key = f"agent:queue:{task.agent_id}"
            self.redis_client.lpush(queue_key, json.dumps({
                "task_id": task.task_id,
                "task_type": task.task_type,
                "parameters": task.parameters,
                "created_at": task.created_at
            }))
            
            # Update task status
            task.status = "queued"
            task.started_at = datetime.now().isoformat()
            
            logger.info(f"📋 Task queued for agent {task.agent_id}: {task.task_id}")
            
        except Exception as e:
            logger.error(f"❌ Failed to queue task: {e}")
            raise
    
    async def _execute_migration_task(self, task_data: Dict[str, Any]):
        """Execute document migration task"""
        try:
            agent_id = task_data["agent_id"]
            parameters = task_data["parameters"]
            
            # Call agent migration endpoint
            agent_url = f"http://{agent_id}:8006/migrate"
            
            response = requests.post(agent_url, json=parameters, timeout=300)
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"✅ Migration task executed successfully: {result}")
            else:
                logger.error(f"❌ Migration task failed: {response.status_code} - {response.text}")
                
        except Exception as e:
            logger.error(f"❌ Failed to execute migration task: {e}")
    
    async def start_heartbeat(self):
        """Start heartbeat to update status"""
        while True:
            try:
                self.status["last_heartbeat"] = datetime.now().isoformat()
                
                # Store status in Redis
                status_key = f"orchestrator:status:{self.config.orchestrator_id}"
                self.redis_client.setex(status_key, 60, json.dumps(self.status))
                
                # Check agent heartbeats
                await self._check_agent_heartbeats()
                
                await asyncio.sleep(30)  # Heartbeat every 30 seconds
                
            except Exception as e:
                logger.error(f"❌ Heartbeat failed: {e}")
                await asyncio.sleep(30)
    
    async def _check_agent_heartbeats(self):
        """Check agent heartbeats and update status"""
        try:
            for agent_id in list(self.registered_agents.keys()):
                status_key = f"agent:status:{agent_id}"
                agent_data = self.redis_client.get(status_key)
                
                if agent_data:
                    agent_info = json.loads(agent_data)
                    self.registered_agents[agent_id]["last_heartbeat"] = agent_info.get("last_heartbeat")
                    self.registered_agents[agent_id]["status"] = agent_info.get("status", "unknown")
                else:
                    # Agent heartbeat missing, mark as offline
                    self.registered_agents[agent_id]["status"] = "offline"
                    logger.warning(f"⚠️ Agent {agent_id} heartbeat missing")
            
        except Exception as e:
            logger.error(f"❌ Failed to check agent heartbeats: {e}")
    
    async def run(self):
        """Run the orchestrator"""
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
                port=8007,
                log_level="info"
            )
            server = uvicorn.Server(config)
            
            # Run server
            await server.serve()
            
        except Exception as e:
            logger.error(f"❌ Orchestrator failed: {e}")
            raise

async def main():
    """Main function"""
    config = OrchestratorConfig()
    orchestrator = AgentOrchestrator(config)
    await orchestrator.run()

if __name__ == "__main__":
    asyncio.run(main())
