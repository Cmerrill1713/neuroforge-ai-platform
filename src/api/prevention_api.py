#!/usr/bin/env python3
"""
Prevention API - Endpoints for Issue Tracking and Circular Fix Prevention
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from ..core.monitoring.issue_tracker import (
    IssueTracker, IssueStatus, IssueSeverity, 
    track_issue, mark_issue_fixed, mark_issue_verified
)
from ..core.monitoring.circular_fix_prevention import (
    CircularFixPrevention, FixPattern,
    record_fix_attempt, check_fix_prevention, get_prevention_recommendations
)
from ..core.monitoring.automated_health_monitor import (
    AutomatedHealthMonitor, HealthStatus, ComponentType,
    get_health_summary, get_prevention_recommendations as get_health_recommendations
)

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/prevention", tags=["prevention"])

# Pydantic models
class IssueCreate(BaseModel):
    title: str = Field(..., description="Issue title")
    description: str = Field(..., description="Issue description")
    severity: str = Field(default="medium", description="Issue severity")
    tags: List[str] = Field(default=[], description="Issue tags")
    affected_components: List[str] = Field(default=[], description="Affected components")

class IssueUpdate(BaseModel):
    status: str = Field(..., description="New issue status")
    fix_description: Optional[str] = Field(None, description="Fix description")
    verification_steps: Optional[List[str]] = Field(None, description="Verification steps")
    prevention_measures: Optional[List[str]] = Field(None, description="Prevention measures")

class FixAttempt(BaseModel):
    issue_id: str = Field(..., description="Issue ID")
    fix_description: str = Field(..., description="Fix description")
    affected_components: List[str] = Field(..., description="Affected components")
    success: bool = Field(..., description="Whether fix was successful")
    verification_passed: bool = Field(default=False, description="Whether verification passed")

class PreventionCheck(BaseModel):
    fix_description: str = Field(..., description="Fix description")
    affected_components: List[str] = Field(..., description="Affected components")

# Initialize instances
issue_tracker = IssueTracker()
circular_fix_prevention = CircularFixPrevention()
health_monitor = AutomatedHealthMonitor()

@router.get("/issues")
async def get_issues():
    """Get all issues"""
    try:
        issues = []
        for issue in issue_tracker.issues.values():
            issues.append({
                "id": issue.id,
                "title": issue.title,
                "description": issue.description,
                "status": issue.status.value,
                "severity": issue.severity.value,
                "created_at": issue.created_at.isoformat(),
                "updated_at": issue.updated_at.isoformat(),
                "fix_attempts": issue.fix_attempts,
                "recurrence_count": issue.recurrence_count,
                "tags": issue.tags,
                "affected_components": issue.affected_components
            })
        return {"issues": issues, "total": len(issues)}
    except Exception as e:
        logger.error(f"Error getting issues: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/issues")
async def create_issue(issue_data: IssueCreate):
    """Create a new issue"""
    try:
        severity = IssueSeverity(issue_data.severity.lower())
        issue_id = issue_tracker.create_issue(
            title=issue_data.title,
            description=issue_data.description,
            severity=severity,
            tags=issue_data.tags,
            affected_components=issue_data.affected_components
        )
        return {"issue_id": issue_id, "message": "Issue created successfully"}
    except Exception as e:
        logger.error(f"Error creating issue: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/issues/{issue_id}")
async def update_issue(issue_id: str, update_data: IssueUpdate):
    """Update an issue"""
    try:
        if issue_id not in issue_tracker.issues:
            raise HTTPException(status_code=404, detail="Issue not found")
        
        status = IssueStatus(update_data.status.lower())
        issue_tracker.update_issue_status(
            issue_id=issue_id,
            status=status,
            fix_description=update_data.fix_description,
            verification_steps=update_data.verification_steps,
            prevention_measures=update_data.prevention_measures
        )
        
        return {"message": "Issue updated successfully"}
    except Exception as e:
        logger.error(f"Error updating issue: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/issues/{issue_id}")
async def get_issue(issue_id: str):
    """Get a specific issue"""
    try:
        if issue_id not in issue_tracker.issues:
            raise HTTPException(status_code=404, detail="Issue not found")
        
        issue = issue_tracker.issues[issue_id]
        return {
            "id": issue.id,
            "title": issue.title,
            "description": issue.description,
            "status": issue.status.value,
            "severity": issue.severity.value,
            "created_at": issue.created_at.isoformat(),
            "updated_at": issue.updated_at.isoformat(),
            "fixed_at": issue.fixed_at.isoformat() if issue.fixed_at else None,
            "verified_at": issue.verified_at.isoformat() if issue.verified_at else None,
            "closed_at": issue.closed_at.isoformat() if issue.closed_at else None,
            "fix_attempts": issue.fix_attempts,
            "recurrence_count": issue.recurrence_count,
            "tags": issue.tags,
            "affected_components": issue.affected_components,
            "fix_description": issue.fix_description,
            "verification_steps": issue.verification_steps,
            "prevention_measures": issue.prevention_measures
        }
    except Exception as e:
        logger.error(f"Error getting issue: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/fixes")
async def record_fix(fix_data: FixAttempt):
    """Record a fix attempt"""
    try:
        fix_record = record_fix_attempt(
            issue_id=fix_data.issue_id,
            fix_description=fix_data.fix_description,
            affected_components=fix_data.affected_components,
            success=fix_data.success,
            verification_passed=fix_data.verification_passed
        )
        
        return {
            "message": "Fix recorded successfully",
            "fix_record": {
                "issue_id": fix_record.issue_id,
                "fix_timestamp": fix_record.fix_timestamp.isoformat(),
                "fix_description": fix_record.fix_description,
                "fix_pattern": fix_record.fix_pattern.value,
                "success": fix_record.success,
                "verification_passed": fix_record.verification_passed,
                "prevention_applied": fix_record.prevention_applied
            }
        }
    except Exception as e:
        logger.error(f"Error recording fix: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/prevention/check")
async def check_prevention(prevention_data: PreventionCheck):
    """Check if a fix should be prevented"""
    try:
        should_prevent, reason = check_fix_prevention(
            fix_description=prevention_data.fix_description,
            affected_components=prevention_data.affected_components
        )
        
        return {
            "should_prevent": should_prevent,
            "reason": reason,
            "recommendations": get_prevention_recommendations(prevention_data.affected_components[0]) if prevention_data.affected_components else []
        }
    except Exception as e:
        logger.error(f"Error checking prevention: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/prevention/recommendations/{component}")
async def get_component_recommendations(component: str):
    """Get prevention recommendations for a component"""
    try:
        recommendations = get_prevention_recommendations(component)
        return {"component": component, "recommendations": recommendations}
    except Exception as e:
        logger.error(f"Error getting recommendations: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def get_health_status():
    """Get system health status"""
    try:
        health_summary = get_health_summary()
        health_recommendations = get_health_recommendations()
        
        return {
            "health_summary": health_summary,
            "recommendations": health_recommendations,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting health status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/statistics")
async def get_prevention_statistics():
    """Get prevention statistics"""
    try:
        issue_summary = issue_tracker.get_issue_summary()
        fix_statistics = circular_fix_prevention.get_fix_statistics()
        health_summary = get_health_summary()
        
        return {
            "issues": issue_summary,
            "fixes": fix_statistics,
            "health": health_summary,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/recurring")
async def get_recurring_issues():
    """Get recurring issues"""
    try:
        recurring_issues = issue_tracker.get_recurring_issues()
        recurring_patterns = circular_fix_prevention.get_recurring_fix_patterns()
        
        issues_data = []
        for issue in recurring_issues:
            issues_data.append({
                "id": issue.id,
                "title": issue.title,
                "recurrence_count": issue.recurrence_count,
                "fix_attempts": issue.fix_attempts,
                "affected_components": issue.affected_components,
                "prevention_measures": issue.prevention_measures
            })
        
        patterns_data = {}
        for pattern, count in recurring_patterns.items():
            patterns_data[pattern.value] = count
        
        return {
            "recurring_issues": issues_data,
            "recurring_patterns": patterns_data,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting recurring issues: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/health/monitoring/start")
async def start_health_monitoring():
    """Start health monitoring"""
    try:
        import asyncio
        asyncio.create_task(health_monitor.start_monitoring())
        return {"message": "Health monitoring started"}
    except Exception as e:
        logger.error(f"Error starting health monitoring: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/health/monitoring/stop")
async def stop_health_monitoring():
    """Stop health monitoring"""
    try:
        health_monitor.stop_monitoring()
        return {"message": "Health monitoring stopped"}
    except Exception as e:
        logger.error(f"Error stopping health monitoring: {e}")
        raise HTTPException(status_code=500, detail=str(e))
