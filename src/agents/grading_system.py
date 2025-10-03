#!/usr/bin/env python3
"""
Grading System Integration
Monitors and grades agent performance
"""

import asyncio
import json
import logging
import os
from typing import Dict, List, Any
from datetime import datetime
import requests
import redis
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("/app/logs/grading.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class AgentReport(BaseModel):
    """Agent performance report"""
    agent_id: str
    performance_score: float
    resource_efficiency: float
    task_completion_rate: float
    error_rate: float
    recommendations: List[str]
    timestamp: str

class GradingSystem:
    """Grading System for Agent Monitoring"""
    
    def __init__(self):
        self.app = FastAPI(title="Agent Grading System", version="1.0.0")
        self.redis_client = redis.from_url(os.getenv("REDIS_URL", "redis://redis:6379"))
        self.registered_agents = {}
        self.agent_metrics = {}
        
        # Setup routes
        self._setup_routes()
        
    def _setup_routes(self):
        """Setup FastAPI routes"""
        
        @self.app.get("/health")
        async def health_check():
            """Health check"""
            return {"status": "healthy", "system": "grading"}
        
        @self.app.post("/agents/register")
        async def register_agent(agent_data: Dict[str, Any]):
            """Register agent for grading"""
            try:
                agent_id = agent_data.get("agent_id")
                if not agent_id:
                    raise HTTPException(status_code=400, detail="agent_id required")
                
                self.registered_agents[agent_id] = {
                    "agent_id": agent_id,
                    "agent_type": agent_data.get("agent_type", "unknown"),
                    "resource_limits": agent_data.get("resource_limits", {}),
                    "capabilities": agent_data.get("capabilities", []),
                    "registered_at": agent_data.get("registered_at", datetime.now().isoformat())
                }
                
                # Initialize metrics
                self.agent_metrics[agent_id] = {
                    "tasks_completed": 0,
                    "tasks_failed": 0,
                    "total_processing_time": 0,
                    "resource_violations": 0,
                    "last_activity": datetime.now().isoformat()
                }
                
                logger.info(f"✅ Agent registered: {agent_id}")
                return {"message": f"Agent {agent_id} registered for grading"}
                
            except Exception as e:
                logger.error(f"❌ Registration failed: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.post("/agents/progress")
        async def report_progress(progress_data: Dict[str, Any]):
            """Report agent progress"""
            try:
                agent_id = progress_data.get("agent_id")
                if agent_id not in self.registered_agents:
                    raise HTTPException(status_code=404, detail="Agent not registered")
                
                # Update metrics
                metrics = self.agent_metrics[agent_id]
                metrics["last_activity"] = datetime.now().isoformat()
                
                # Check resource violations
                resources = progress_data.get("resources", {})
                if not resources.get("healthy", True):
                    metrics["resource_violations"] += 1
                
                # Store progress in Redis
                progress_key = f"agent:progress:{agent_id}"
                self.redis_client.setex(progress_key, 3600, json.dumps(progress_data))
                
                logger.info(f"📊 Progress reported for {agent_id}")
                return {"message": "Progress recorded"}
                
            except Exception as e:
                logger.error(f"❌ Progress reporting failed: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/agents/report/{agent_id}")
        async def get_agent_report(agent_id: str):
            """Get agent performance report"""
            try:
                if agent_id not in self.registered_agents:
                    raise HTTPException(status_code=404, detail="Agent not found")
                
                # Calculate performance metrics
                metrics = self.agent_metrics.get(agent_id, {})
                agent_info = self.registered_agents[agent_id]
                
                # Performance scoring
                performance_score = self._calculate_performance_score(agent_id, metrics)
                resource_efficiency = self._calculate_resource_efficiency(agent_id, metrics)
                task_completion_rate = self._calculate_completion_rate(agent_id, metrics)
                error_rate = self._calculate_error_rate(agent_id, metrics)
                
                # Generate recommendations
                recommendations = self._generate_recommendations(agent_id, metrics, performance_score)
                
                report = AgentReport(
                    agent_id=agent_id,
                    performance_score=performance_score,
                    resource_efficiency=resource_efficiency,
                    task_completion_rate=task_completion_rate,
                    error_rate=error_rate,
                    recommendations=recommendations,
                    timestamp=datetime.now().isoformat()
                )
                
                return report.dict()
                
            except Exception as e:
                logger.error(f"❌ Report generation failed: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/agents")
        async def list_agents():
            """List all registered agents"""
            return {
                "agents": list(self.registered_agents.values()),
                "total_agents": len(self.registered_agents)
            }
    
    def _calculate_performance_score(self, agent_id: str, metrics: Dict[str, Any]) -> float:
        """Calculate performance score (0-100)"""
        try:
            # Base score
            score = 70.0
            
            # Task completion bonus
            tasks_completed = metrics.get("tasks_completed", 0)
            if tasks_completed > 0:
                score += min(20.0, tasks_completed * 2)
            
            # Resource efficiency bonus
            resource_violations = metrics.get("resource_violations", 0)
            if resource_violations == 0:
                score += 10.0
            else:
                score -= min(20.0, resource_violations * 5)
            
            # Activity bonus
            last_activity = metrics.get("last_activity")
            if last_activity:
                activity_time = datetime.fromisoformat(last_activity)
                time_since_activity = (datetime.now() - activity_time).total_seconds()
                if time_since_activity < 300:  # Active within 5 minutes
                    score += 5.0
            
            return min(100.0, max(0.0, score))
            
        except Exception as e:
            logger.error(f"❌ Performance calculation failed: {e}")
            return 50.0
    
    def _calculate_resource_efficiency(self, agent_id: str, metrics: Dict[str, Any]) -> float:
        """Calculate resource efficiency (0-100)"""
        try:
            resource_violations = metrics.get("resource_violations", 0)
            if resource_violations == 0:
                return 100.0
            else:
                return max(0.0, 100.0 - (resource_violations * 20))
        except:
            return 50.0
    
    def _calculate_completion_rate(self, agent_id: str, metrics: Dict[str, Any]) -> float:
        """Calculate task completion rate (0-100)"""
        try:
            completed = metrics.get("tasks_completed", 0)
            failed = metrics.get("tasks_failed", 0)
            total = completed + failed
            
            if total == 0:
                return 0.0
            
            return (completed / total) * 100.0
        except:
            return 0.0
    
    def _calculate_error_rate(self, agent_id: str, metrics: Dict[str, Any]) -> float:
        """Calculate error rate (0-100)"""
        try:
            completed = metrics.get("tasks_completed", 0)
            failed = metrics.get("tasks_failed", 0)
            total = completed + failed
            
            if total == 0:
                return 0.0
            
            return (failed / total) * 100.0
        except:
            return 0.0
    
    def _generate_recommendations(self, agent_id: str, metrics: Dict[str, Any], performance_score: float) -> List[str]:
        """Generate performance recommendations"""
        recommendations = []
        
        # Resource efficiency recommendations
        resource_violations = metrics.get("resource_violations", 0)
        if resource_violations > 0:
            recommendations.append("Consider reducing batch size to stay within resource limits")
            recommendations.append("Monitor memory usage more closely")
        
        # Performance recommendations
        if performance_score < 70:
            recommendations.append("Performance below optimal - check error logs")
            recommendations.append("Consider increasing monitoring frequency")
        
        if performance_score > 90:
            recommendations.append("Excellent performance - consider increasing batch size")
        
        # Activity recommendations
        last_activity = metrics.get("last_activity")
        if last_activity:
            activity_time = datetime.fromisoformat(last_activity)
            time_since_activity = (datetime.now() - activity_time).total_seconds()
            if time_since_activity > 600:  # Inactive for 10 minutes
                recommendations.append("Agent appears inactive - check health status")
        
        if not recommendations:
            recommendations.append("Agent performing well - continue current configuration")
        
        return recommendations
    
    async def run(self):
        """Run the grading system"""
        try:
            import uvicorn
            config = uvicorn.Config(
                self.app,
                host="0.0.0.0",
                port=8009,
                log_level="info",
                workers=1
            )
            server = uvicorn.Server(config)
            await server.serve()
            
        except Exception as e:
            logger.error(f"❌ Grading system failed: {e}")
            raise

async def main():
    """Main function"""
    grading_system = GradingSystem()
    await grading_system.run()

if __name__ == "__main__":
    asyncio.run(main())
