#!/usr/bin/env python3
"""
Agent Monitor Dashboard
Provides monitoring and management interface for agents
"""

import asyncio
import json
import logging
import os
from typing import Dict, List, Any
from datetime import datetime
import requests
import redis
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("/app/logs/monitor.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class AgentMonitor:
    """Agent Monitor Dashboard"""
    
    def __init__(self):
        self.app = FastAPI(title="Agent Monitor", version="1.0.0")
        self.redis_client = redis.from_url(os.getenv("REDIS_URL", "redis://redis:6379"))
        self.orchestrator_url = os.getenv("ORCHESTRATOR_URL", "http://agent-orchestrator:8007")
        
        # Setup routes
        self._setup_routes()
        
    def _setup_routes(self):
        """Setup FastAPI routes"""
        
        @self.app.get("/", response_class=HTMLResponse)
        async def dashboard(request: Request):
            """Main dashboard"""
            try:
                # Get orchestrator status
                orchestrator_status = await self._get_orchestrator_status()
                
                # Get agents
                agents = await self._get_agents()
                
                # Get tasks
                tasks = await self._get_tasks()
                
                # Get system metrics
                metrics = await self._get_system_metrics()
                
                return self._render_dashboard({
                    "orchestrator": orchestrator_status,
                    "agents": agents,
                    "tasks": tasks,
                    "metrics": metrics
                })
                
            except Exception as e:
                logger.error(f"❌ Dashboard error: {e}")
                return self._render_error(str(e))
        
        @self.app.get("/api/status")
        async def get_status():
            """Get system status"""
            try:
                orchestrator_status = await self._get_orchestrator_status()
                agents = await self._get_agents()
                tasks = await self._get_tasks()
                metrics = await self._get_system_metrics()
                
                return {
                    "orchestrator": orchestrator_status,
                    "agents": agents,
                    "tasks": tasks,
                    "metrics": metrics,
                    "timestamp": datetime.now().isoformat()
                }
                
            except Exception as e:
                logger.error(f"❌ Status API error: {e}")
                return {"error": str(e)}
        
        @self.app.post("/api/migrate")
        async def start_migration():
            """Start document migration"""
            try:
                response = requests.post(f"{self.orchestrator_url}/migrate/documents")
                if response.status_code == 200:
                    return {"message": "Migration started", "data": response.json()}
                else:
                    return {"error": f"Migration failed: {response.status_code}"}
                    
            except Exception as e:
                logger.error(f"❌ Migration API error: {e}")
                return {"error": str(e)}
    
    async def _get_orchestrator_status(self) -> Dict[str, Any]:
        """Get orchestrator status"""
        try:
            response = requests.get(f"{self.orchestrator_url}/status", timeout=10)
            if response.status_code == 200:
                return response.json()
            else:
                return {"status": "error", "message": f"HTTP {response.status_code}"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    async def _get_agents(self) -> List[Dict[str, Any]]:
        """Get registered agents"""
        try:
            response = requests.get(f"{self.orchestrator_url}/agents", timeout=10)
            if response.status_code == 200:
                data = response.json()
                return data.get("agents", [])
            else:
                return []
        except Exception as e:
            logger.error(f"❌ Failed to get agents: {e}")
            return []
    
    async def _get_tasks(self) -> List[Dict[str, Any]]:
        """Get active tasks"""
        try:
            response = requests.get(f"{self.orchestrator_url}/tasks", timeout=10)
            if response.status_code == 200:
                data = response.json()
                return data.get("tasks", [])
            else:
                return []
        except Exception as e:
            logger.error(f"❌ Failed to get tasks: {e}")
            return []
    
    async def _get_system_metrics(self) -> Dict[str, Any]:
        """Get system metrics"""
        try:
            # Get Redis metrics
            redis_info = self.redis_client.info()
            
            # Get Weaviate metrics (if available)
            weaviate_metrics = {}
            try:
                weaviate_response = requests.get("http://weaviate:8090/v1/meta", timeout=5)
                if weaviate_response.status_code == 200:
                    weaviate_metrics = weaviate_response.json()
            except:
                pass
            
            return {
                "redis": {
                    "connected_clients": redis_info.get("connected_clients", 0),
                    "used_memory": redis_info.get("used_memory_human", "0B"),
                    "keyspace": redis_info.get("db0", {}).get("keys", 0)
                },
                "weaviate": weaviate_metrics,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to get metrics: {e}")
            return {"error": str(e)}
    
    def _render_dashboard(self, data: Dict[str, Any]) -> str:
        """Render dashboard HTML"""
        return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Agent Monitor Dashboard</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        .header {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }}
        .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
        }}
        .card {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .status-healthy {{ color: #10b981; }}
        .status-error {{ color: #ef4444; }}
        .status-warning {{ color: #f59e0b; }}
        .metric {{
            display: flex;
            justify-content: space-between;
            margin: 10px 0;
            padding: 10px;
            background: #f8f9fa;
            border-radius: 4px;
        }}
        .btn {{
            background: #3b82f6;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 4px;
            cursor: pointer;
            margin: 5px;
        }}
        .btn:hover {{ background: #2563eb; }}
        .agent-card {{
            border-left: 4px solid #10b981;
            margin: 10px 0;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 4px;
        }}
        .task-card {{
            border-left: 4px solid #3b82f6;
            margin: 10px 0;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 4px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 Agent Monitor Dashboard</h1>
            <p>Real-time monitoring of document processing agents</p>
            <button class="btn" onclick="startMigration()">Start Document Migration</button>
            <button class="btn" onclick="refreshData()">Refresh</button>
        </div>
        
        <div class="grid">
            <div class="card">
                <h3>🎯 Orchestrator Status</h3>
                <div class="metric">
                    <span>Status:</span>
                    <span class="status-{data['orchestrator'].get('status', 'unknown')}">
                        {data['orchestrator'].get('status', 'unknown').upper()}
                    </span>
                </div>
                <div class="metric">
                    <span>Agents Registered:</span>
                    <span>{data['orchestrator'].get('agents_registered', 0)}</span>
                </div>
                <div class="metric">
                    <span>Tasks Completed:</span>
                    <span>{data['orchestrator'].get('tasks_completed', 0)}</span>
                </div>
                <div class="metric">
                    <span>Tasks Failed:</span>
                    <span>{data['orchestrator'].get('tasks_failed', 0)}</span>
                </div>
            </div>
            
            <div class="card">
                <h3>📊 System Metrics</h3>
                <div class="metric">
                    <span>Redis Clients:</span>
                    <span>{data['metrics'].get('redis', {}).get('connected_clients', 0)}</span>
                </div>
                <div class="metric">
                    <span>Redis Memory:</span>
                    <span>{data['metrics'].get('redis', {}).get('used_memory', '0B')}</span>
                </div>
                <div class="metric">
                    <span>Redis Keys:</span>
                    <span>{data['metrics'].get('redis', {}).get('keyspace', 0)}</span>
                </div>
            </div>
            
            <div class="card">
                <h3>🤖 Registered Agents ({len(data['agents'])})</h3>
                {self._render_agents(data['agents'])}
            </div>
            
            <div class="card">
                <h3>📋 Active Tasks ({len(data['tasks'])})</h3>
                {self._render_tasks(data['tasks'])}
            </div>
        </div>
    </div>
    
    <script>
        function startMigration() {{
            fetch('/api/migrate', {{method: 'POST'}})
                .then(response => response.json())
                .then(data => {{
                    alert(data.message || data.error);
                    refreshData();
                }})
                .catch(error => {{
                    alert('Error: ' + error);
                }});
        }}
        
        function refreshData() {{
            location.reload();
        }}
        
        // Auto-refresh every 30 seconds
        setInterval(refreshData, 30000);
    </script>
</body>
</html>
        """
    
    def _render_agents(self, agents: List[Dict[str, Any]]) -> str:
        """Render agents section"""
        if not agents:
            return "<p>No agents registered</p>"
        
        html = ""
        for agent in agents:
            status_class = f"status-{agent.get('status', 'unknown')}"
            html += f"""
            <div class="agent-card">
                <strong>{agent.get('agent_id', 'Unknown')}</strong>
                <span class="{status_class}">{agent.get('status', 'unknown').upper()}</span>
                <br>
                <small>Role: {agent.get('role', 'unknown')}</small>
                <br>
                <small>Last Heartbeat: {agent.get('last_heartbeat', 'never')}</small>
            </div>
            """
        return html
    
    def _render_tasks(self, tasks: List[Dict[str, Any]]) -> str:
        """Render tasks section"""
        if not tasks:
            return "<p>No active tasks</p>"
        
        html = ""
        for task in tasks:
            status_class = f"status-{task.get('status', 'unknown')}"
            html += f"""
            <div class="task-card">
                <strong>{task.get('task_id', 'Unknown')}</strong>
                <span class="{status_class}">{task.get('status', 'unknown').upper()}</span>
                <br>
                <small>Type: {task.get('task_type', 'unknown')}</small>
                <br>
                <small>Agent: {task.get('agent_id', 'unknown')}</small>
                <br>
                <small>Created: {task.get('created_at', 'unknown')}</small>
            </div>
            """
        return html
    
    def _render_error(self, error: str) -> str:
        """Render error page"""
        return f"""
<!DOCTYPE html>
<html>
<head>
    <title>Agent Monitor - Error</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        .error {{ color: #ef4444; background: #fef2f2; padding: 20px; border-radius: 8px; }}
    </style>
</head>
<body>
    <h1>❌ Agent Monitor Error</h1>
    <div class="error">
        <strong>Error:</strong> {error}
    </div>
    <button onclick="location.reload()">Retry</button>
</body>
</html>
        """
    
    async def run(self):
        """Run the monitor"""
        try:
            import uvicorn
            config = uvicorn.Config(
                self.app,
                host="0.0.0.0",
                port=8008,
                log_level="info"
            )
            server = uvicorn.Server(config)
            await server.serve()
            
        except Exception as e:
            logger.error(f"❌ Monitor failed: {e}")
            raise

async def main():
    """Main function"""
    monitor = AgentMonitor()
    await monitor.run()

if __name__ == "__main__":
    asyncio.run(main())
