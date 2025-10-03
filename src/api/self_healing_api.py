#!/usr/bin/env python3
"""
Self-Healing API - Intelligent error detection and automatic fixes
Provides endpoints for monitoring and triggering self-healing capabilities
"""

import logging
import asyncio
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from datetime import datetime
import traceback

from ..core.self_healing.intelligent_healer import intelligent_healer

logger = logging.getLogger(__name__)

# Request/response models
class HealingRequest(BaseModel):
    """Self-healing request"""
    error_message: str = Field(..., min_length=1, max_length=5000, description="Error message to analyze and fix")
    context: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional context about the error")
    auto_heal: bool = Field(default=True, description="Whether to automatically attempt healing")

class HealingResponse(BaseModel):
    """Self-healing response"""
    success: bool
    error_analysis: Optional[Dict[str, Any]] = None
    healing_result: Optional[Dict[str, Any]] = None
    execution_time_ms: float
    timestamp: str

class HealingStatsResponse(BaseModel):
    """Healing statistics response"""
    total_healing_attempts: int
    successful_heals: int
    failed_heals: int
    success_rate: float
    known_error_types: List[str]
    successful_fixes: List[str]
    failed_fixes: List[str]
    recent_heals: List[Dict[str, Any]]

class SystemHealthCheck(BaseModel):
    """System health check request"""
    check_services: bool = Field(default=True, description="Check service health")
    check_errors: bool = Field(default=True, description="Check for recent errors")
    auto_heal: bool = Field(default=False, description="Automatically heal detected issues")

class ResearchRequest(BaseModel):
    """Research request for unknown issues"""
    error_message: str = Field(..., min_length=1, max_length=5000, description="Unknown error message to research")
    context: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional context about the error")

class ResearchResponse(BaseModel):
    """Research response"""
    success: bool
    solution_found: bool
    solution: Optional[Dict[str, Any]] = None
    fix_implementation: Optional[str] = None
    confidence: float = 0.0
    research_method: str = ""
    execution_time_ms: float
    timestamp: str

# Create router
router = APIRouter(prefix="/api/healing", tags=["Self-Healing"])

@router.post("/analyze-and-heal", response_model=HealingResponse)
async def analyze_and_heal_error(request: HealingRequest):
    """Analyze an error message and attempt to heal it"""
    try:
        import time
        start_time = time.time()
        
        logger.info(f"🔍 Analyzing error for self-healing: {request.error_message[:100]}...")
        
        # Analyze the error
        error_analysis = await intelligent_healer.analyze_error(
            request.error_message, 
            request.context
        )
        
        healing_result = None
        success = False
        
        if error_analysis:
            logger.info(f"✅ Error analysis complete: {error_analysis['error_type']}")
            
            if request.auto_heal and error_analysis["can_fix"]:
                # Attempt healing
                healing_result = await intelligent_healer.attempt_healing(error_analysis)
                success = healing_result.get("success", False)
                
                if success:
                    logger.info(f"🎉 Successfully healed {error_analysis['error_type']}")
                else:
                    logger.warning(f"⚠️ Healing failed for {error_analysis['error_type']}")
            else:
                success = False
                healing_result = {"success": False, "reason": "Auto-healing disabled or error not fixable"}
        else:
            logger.warning("⚠️ Error could not be analyzed or is unknown type")
            error_analysis = {"error_type": "unknown", "can_fix": False}
        
        execution_time_ms = (time.time() - start_time) * 1000
        
        return HealingResponse(
            success=success,
            error_analysis=error_analysis,
            healing_result=healing_result,
            execution_time_ms=execution_time_ms,
            timestamp=datetime.now().isoformat()
        )
        
    except Exception as e:
        logger.error(f"Self-healing analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Self-healing failed: {str(e)}")

@router.get("/stats", response_model=HealingStatsResponse)
async def get_healing_stats():
    """Get statistics about self-healing attempts"""
    try:
        stats = intelligent_healer.get_healing_stats()
        
        return HealingStatsResponse(
            total_healing_attempts=stats["total_healing_attempts"],
            successful_heals=stats["successful_heals"],
            failed_heals=stats["failed_heals"],
            success_rate=stats["success_rate"],
            known_error_types=stats["known_error_types"],
            successful_fixes=stats["successful_fixes"],
            failed_fixes=stats["failed_fixes"],
            recent_heals=stats["recent_heals"]
        )
        
    except Exception as e:
        logger.error(f"Failed to get healing stats: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get healing stats: {str(e)}")

@router.post("/health-check")
async def comprehensive_health_check(request: SystemHealthCheck, background_tasks: BackgroundTasks):
    """Perform comprehensive system health check and auto-heal if requested"""
    try:
        health_report = {
            "timestamp": datetime.now().isoformat(),
            "services": {},
            "errors_detected": [],
            "healing_attempts": [],
            "overall_status": "unknown"
        }
        
        # Check service health
        if request.check_services:
            services_to_check = [
                ("consolidated_api", "http://localhost:8004/api/system/health"),
                ("tts_service", "http://localhost:8087/health"),
                ("whisper_service", "http://localhost:8087/health"),
                ("ollama", "http://localhost:11434/api/tags"),
                ("frontend", "http://localhost:3000")
            ]
            
            for service_name, health_url in services_to_check:
                try:
                    import aiohttp
                    async with aiohttp.ClientSession() as session:
                        async with session.get(health_url, timeout=5) as response:
                            health_report["services"][service_name] = {
                                "status": "healthy" if response.status == 200 else "unhealthy",
                                "status_code": response.status,
                                "response_time_ms": 0  # Could add timing
                            }
                except Exception as e:
                    health_report["services"][service_name] = {
                        "status": "unavailable",
                        "error": str(e)
                    }
        
        # Check for common errors (simulate by checking logs or known issues)
        if request.check_errors:
            common_errors = [
                "Incompatible dimension for X and Y matrices",
                "object has no attribute",
                "cannot import name",
                "No module named",
                "Connection error"
            ]
            
            # This is a simplified check - in a real system, you'd parse actual logs
            for error_pattern in common_errors:
                health_report["errors_detected"].append({
                    "pattern": error_pattern,
                    "severity": "medium",
                    "detected_at": datetime.now().isoformat()
                })
        
        # Auto-heal if requested
        if request.auto_heal and health_report["errors_detected"]:
            background_tasks.add_task(auto_heal_detected_issues, health_report["errors_detected"])
        
        # Determine overall status
        service_statuses = [s.get("status") for s in health_report["services"].values()]
        if all(status == "healthy" for status in service_statuses):
            health_report["overall_status"] = "healthy"
        elif any(status == "unhealthy" for status in service_statuses):
            health_report["overall_status"] = "degraded"
        else:
            health_report["overall_status"] = "unhealthy"
        
        return health_report
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")

@router.post("/emergency-heal")
async def emergency_heal():
    """Emergency healing - attempt to fix all known critical issues"""
    try:
        logger.info("🚨 Emergency healing initiated")
        
        emergency_fixes = [
            {
                "error_message": "Incompatible dimension for X and Y matrices: X.shape[1] == 384 while Y.shape[1] == 768",
                "context": {"emergency": True}
            },
            {
                "error_message": "'AdvancedRAGSystem' object has no attribute 'get_database_stats'",
                "context": {"emergency": True}
            },
            {
                "error_message": "'OptimizedResponseCache' object has no attribute 'clear_all'",
                "context": {"emergency": True}
            },
            {
                "error_message": "cannot import name 'SimpleKnowledgeBase' from 'src.core.knowledge.simple_knowledge_base'",
                "context": {"emergency": True}
            }
        ]
        
        results = []
        for fix_attempt in emergency_fixes:
            try:
                # Analyze and heal
                error_analysis = await intelligent_healer.analyze_error(
                    fix_attempt["error_message"],
                    fix_attempt["context"]
                )
                
                if error_analysis and error_analysis["can_fix"]:
                    healing_result = await intelligent_healer.attempt_healing(error_analysis)
                    results.append({
                        "error_type": error_analysis["error_type"],
                        "success": healing_result.get("success", False),
                        "details": healing_result.get("details", "")
                    })
                else:
                    results.append({
                        "error_type": "unknown",
                        "success": False,
                        "details": "Could not analyze or fix"
                    })
                    
            except Exception as e:
                results.append({
                    "error_type": "exception",
                    "success": False,
                    "details": str(e)
                })
        
        successful_fixes = len([r for r in results if r["success"]])
        total_attempts = len(results)
        
        return {
            "message": "Emergency healing completed",
            "total_attempts": total_attempts,
            "successful_fixes": successful_fixes,
            "success_rate": successful_fixes / total_attempts if total_attempts > 0 else 0,
            "results": results,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Emergency healing failed: {e}")
        raise HTTPException(status_code=500, detail=f"Emergency healing failed: {str(e)}")

@router.get("/health")
async def healing_health_check():
    """Health check for the self-healing system"""
    try:
        stats = intelligent_healer.get_healing_stats()
        
        return {
            "status": "healthy",
            "healing_system_operational": True,
            "total_healing_attempts": stats["total_healing_attempts"],
            "success_rate": stats["success_rate"],
            "known_error_patterns": len(stats["known_error_types"]),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Healing system health check failed: {e}")
        return {
            "status": "unhealthy",
            "healing_system_operational": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@router.post("/research-unknown-error", response_model=ResearchResponse)
async def research_unknown_error(request: ResearchRequest):
    """Research and learn how to fix unknown errors using parallel crawling and knowledge base integration"""
    start_time = datetime.now()
    
    try:
        logger.info(f"🔬 Researching unknown error: {request.error_message[:100]}...")
        
        # Use the researcher directly (now with enhanced research system)
        researcher = intelligent_healer.researcher
        solution = researcher.research_solution(request.error_message)
        
        if solution:
            # Generate fix implementation
            fix_implementation = researcher.generate_fix_implementation(solution)
            
            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            
            logger.info(f"✅ Parallel research completed: {solution.get('solution_type', 'unknown')} (confidence: {solution.get('confidence', 0):.2f})")
            
            return ResearchResponse(
                success=True,
                solution_found=True,
                solution=solution,
                fix_implementation=fix_implementation,
                confidence=solution.get('confidence', 0.0),
                research_method=solution.get('research_method', 'parallel_crawling'),
                execution_time_ms=execution_time,
                timestamp=datetime.now().isoformat()
            )
        else:
            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            
            logger.warning(f"❌ No solution found through parallel research")
            
            return ResearchResponse(
                success=True,
                solution_found=False,
                solution=None,
                fix_implementation=None,
                confidence=0.0,
                research_method="parallel_crawling",
                execution_time_ms=execution_time,
                timestamp=datetime.now().isoformat()
            )
        
    except Exception as e:
        execution_time = (datetime.now() - start_time).total_seconds() * 1000
        logger.error(f"Parallel research failed: {e}")
        traceback.print_exc()
        
        return ResearchResponse(
            success=False,
            solution_found=False,
            solution=None,
            fix_implementation=None,
            confidence=0.0,
            research_method="error",
            execution_time_ms=execution_time,
            timestamp=datetime.now().isoformat()
        )

async def auto_heal_detected_issues(errors_detected: List[Dict[str, Any]]):
    """Background task to automatically heal detected issues"""
    try:
        logger.info(f"🔧 Auto-healing {len(errors_detected)} detected issues")
        
        for error_info in errors_detected:
            try:
                # Create a generic error message for the pattern
                error_message = f"Detected error pattern: {error_info['pattern']}"
                context = {
                    "auto_detected": True,
                    "severity": error_info.get("severity", "medium"),
                    "detected_at": error_info.get("detected_at")
                }
                
                # Analyze and heal
                error_analysis = await intelligent_healer.analyze_error(error_message, context)
                if error_analysis and error_analysis["can_fix"]:
                    healing_result = await intelligent_healer.attempt_healing(error_analysis)
                    logger.info(f"🔧 Auto-healing result: {healing_result.get('success', False)}")
                    
            except Exception as e:
                logger.warning(f"Auto-healing failed for pattern {error_info['pattern']}: {e}")
                
    except Exception as e:
        logger.error(f"Auto-healing background task failed: {e}")

# Include the router in the main API
def include_self_healing_routes(app):
    """Include self-healing routes in the FastAPI app"""
    app.include_router(router)
    logger.info("Self-healing API routes included")
