"""
Agent Reviewer for Agentic LLM Core v0.1

This module provides an intelligent agent reviewer that performs schema validation,
unit testing, and acceptance criteria checks, generating comprehensive review reports.

Created: 2024-09-24
Status: Draft
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import subprocess
import tempfile
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, Tuple
from uuid import uuid4

import pydantic
from pydantic import BaseModel, Field, field_validator

from ..models.contracts import Task, TaskGraph, TaskResult


# ============================================================================
# Review Models
# ============================================================================

class ReviewStatus(str, Enum):
    """Review status enumeration."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    PASSED = "passed"
    FAILED = "failed"
    WARNING = "warning"
    ERROR = "error"


class CheckType(str, Enum):
    """Type of check being performed."""
    SCHEMA = "schema"
    UNIT = "unit"
    ACCEPTANCE = "acceptance"


class ReviewCheck(BaseModel):
    """Individual review check result."""
    check_id: str = Field(default_factory=lambda: str(uuid4()), description="Unique check ID")
    check_type: CheckType = Field(..., description="Type of check")
    name: str = Field(..., description="Name of the check")
    description: str = Field(..., description="Description of the check")
    status: ReviewStatus = Field(default=ReviewStatus.PENDING, description="Check status")
    message: Optional[str] = Field(None, description="Check result message")
    details: Dict[str, Any] = Field(default_factory=dict, description="Additional check details")
    execution_time: Optional[float] = Field(None, description="Execution time in seconds")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Check timestamp")
    
    @field_validator('execution_time')
    @classmethod
    def validate_execution_time(cls, v):
        if v is not None and v < 0:
            raise ValueError("Execution time cannot be negative")
        return v


class ReviewReport(BaseModel):
    """Comprehensive review report."""
    report_id: str = Field(default_factory=lambda: str(uuid4()), description="Unique report ID")
    target_path: str = Field(..., description="Path to the target being reviewed")
    review_type: str = Field(default="comprehensive", description="Type of review")
    status: ReviewStatus = Field(default=ReviewStatus.PENDING, description="Overall review status")
    checks: List[ReviewCheck] = Field(default_factory=list, description="Individual check results")
    summary: Dict[str, Any] = Field(default_factory=dict, description="Review summary")
    recommendations: List[str] = Field(default_factory=list, description="Recommendations")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Report creation timestamp")
    completed_at: Optional[datetime] = Field(None, description="Report completion timestamp")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    def get_overall_status(self) -> ReviewStatus:
        """Get overall review status based on individual checks."""
        if not self.checks:
            return ReviewStatus.PENDING
        
        statuses = [check.status for check in self.checks]
        
        if ReviewStatus.ERROR in statuses:
            return ReviewStatus.ERROR
        elif ReviewStatus.FAILED in statuses:
            return ReviewStatus.FAILED
        elif ReviewStatus.WARNING in statuses:
            return ReviewStatus.WARNING
        elif all(status == ReviewStatus.PASSED for status in statuses):
            return ReviewStatus.PASSED
        else:
            return ReviewStatus.IN_PROGRESS
    
    def get_summary_stats(self) -> Dict[str, int]:
        """Get summary statistics."""
        if not self.checks:
            return {"total": 0, "passed": 0, "failed": 0, "warning": 0, "error": 0}
        
        stats = {"total": len(self.checks)}
        for status in ReviewStatus:
            stats[status.value] = sum(1 for check in self.checks if check.status == status)
        
        return stats


class ReviewConfig(BaseModel):
    """Configuration for the reviewer."""
    enable_schema_checks: bool = Field(default=True, description="Enable schema validation checks")
    enable_unit_checks: bool = Field(default=True, description="Enable unit test checks")
    enable_acceptance_checks: bool = Field(default=True, description="Enable acceptance criteria checks")
    
    # Schema check configuration
    schema_strict_mode: bool = Field(default=True, description="Use strict schema validation")
    schema_ignore_unknown: bool = Field(default=False, description="Ignore unknown fields in schema")
    
    # Unit test configuration
    test_framework: str = Field(default="pytest", description="Test framework to use")
    test_timeout: float = Field(default=300.0, ge=1.0, description="Test execution timeout in seconds")
    test_coverage_threshold: float = Field(default=80.0, ge=0.0, le=100.0, description="Minimum test coverage percentage")
    
    # Acceptance criteria configuration
    acceptance_timeout: float = Field(default=600.0, ge=1.0, description="Acceptance test timeout in seconds")
    acceptance_retries: int = Field(default=3, ge=0, le=10, description="Number of retries for acceptance tests")
    
    # Output configuration
    output_format: str = Field(default="json", description="Output format: json, yaml, html")
    include_details: bool = Field(default=True, description="Include detailed check results")
    include_recommendations: bool = Field(default=True, description="Include recommendations")


# ============================================================================
# Check Implementations
# ============================================================================

class ReviewCheckBase(ABC):
    """Abstract base class for review checks."""
    
    def __init__(self, config: ReviewConfig):
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
    
    @abstractmethod
    async def check(self, target_path: str, context: Dict[str, Any]) -> ReviewCheck:
        """Perform the check."""
        pass
    
    @abstractmethod
    def get_check_name(self) -> str:
        """Get the name of this check."""
        pass
    
    @abstractmethod
    def get_check_description(self) -> str:
        """Get the description of this check."""
        pass


class SchemaValidator(ReviewCheckBase):
    """Schema validation checker."""
    
    def get_check_name(self) -> str:
        return "Schema Validation"
    
    def get_check_description(self) -> str:
        return "Validates Pydantic schemas and data contracts"
    
    async def check(self, target_path: str, context: Dict[str, Any]) -> ReviewCheck:
        """Perform schema validation check."""
        start_time = datetime.now()
        
        try:
            check = ReviewCheck(
                check_type=CheckType.SCHEMA,
                name=self.get_check_name(),
                description=self.get_check_description(),
                status=ReviewStatus.IN_PROGRESS
            )
            
            # Find Python files
            python_files = self._find_python_files(target_path)
            schema_issues = []
            
            for file_path in python_files:
                issues = await self._validate_file_schemas(file_path)
                schema_issues.extend(issues)
            
            # Determine overall status
            if not schema_issues:
                check.status = ReviewStatus.PASSED
                check.message = f"All {len(python_files)} files passed schema validation"
            else:
                check.status = ReviewStatus.FAILED
                check.message = f"Found {len(schema_issues)} schema issues"
            
            check.details = {
                "files_checked": len(python_files),
                "issues_found": len(schema_issues),
                "issues": schema_issues
            }
            
            execution_time = (datetime.now() - start_time).total_seconds()
            check.execution_time = execution_time
            
            return check
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            return ReviewCheck(
                check_type=CheckType.SCHEMA,
                name=self.get_check_name(),
                description=self.get_check_description(),
                status=ReviewStatus.ERROR,
                message=f"Schema validation failed: {str(e)}",
                execution_time=execution_time
            )
    
    def _find_python_files(self, target_path: str) -> List[str]:
        """Find Python files in the target path."""
        python_files = []
        path = Path(target_path)
        
        if path.is_file() and path.suffix == '.py':
            python_files.append(str(path))
        elif path.is_dir():
            for py_file in path.rglob('*.py'):
                # Skip __pycache__ and test files for now
                if '__pycache__' not in str(py_file) and 'test_' not in py_file.name:
                    python_files.append(str(py_file))
        
        return python_files
    
    async def _validate_file_schemas(self, file_path: str) -> List[Dict[str, Any]]:
        """Validate schemas in a Python file."""
        issues = []
        
        try:
            # Read file content
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for Pydantic models
            if 'BaseModel' in content or 'pydantic' in content:
                # Try to import and validate the module
                try:
                    # This is a simplified check - in practice, you'd use AST parsing
                    if 'class ' in content and 'BaseModel' in content:
                        # Check for common schema issues
                        if 'Field(' in content:
                            # Check for proper Field usage
                            if 'Field(...)' in content and 'required' not in content:
                                issues.append({
                                    "file": file_path,
                                    "line": "unknown",
                                    "issue": "Required field without explicit required=True",
                                    "severity": "warning"
                                })
                        
                        # Check for validator usage
                        if '@validator' in content and 'pydantic' in content:
                            if 'pydantic.v1' in content:
                                issues.append({
                                    "file": file_path,
                                    "line": "unknown", 
                                    "issue": "Using deprecated pydantic v1 validator",
                                    "severity": "error"
                                })
                
                except Exception as e:
                    issues.append({
                        "file": file_path,
                        "line": "unknown",
                        "issue": f"Could not parse schema: {str(e)}",
                        "severity": "error"
                    })
        
        except Exception as e:
            issues.append({
                "file": file_path,
                "line": "unknown",
                "issue": f"Could not read file: {str(e)}",
                "severity": "error"
            })
        
        return issues


class UnitTestRunner(ReviewCheckBase):
    """Unit test runner checker."""
    
    def get_check_name(self) -> str:
        return "Unit Tests"
    
    def get_check_description(self) -> str:
        return "Runs unit tests and checks coverage"
    
    async def check(self, target_path: str, context: Dict[str, Any]) -> ReviewCheck:
        """Perform unit test check."""
        start_time = datetime.now()
        
        try:
            check = ReviewCheck(
                check_type=CheckType.UNIT,
                name=self.get_check_name(),
                description=self.get_check_description(),
                status=ReviewStatus.IN_PROGRESS
            )
            
            # Find test files
            test_files = self._find_test_files(target_path)
            
            if not test_files:
                check.status = ReviewStatus.WARNING
                check.message = "No test files found"
                check.details = {"test_files_found": 0}
                return check
            
            # Run tests
            test_results = await self._run_tests(test_files)
            
            # Check coverage
            coverage_results = await self._check_coverage(target_path)
            
            # Determine overall status
            if test_results["passed"] and coverage_results["coverage"] >= self.config.test_coverage_threshold:
                check.status = ReviewStatus.PASSED
                check.message = f"All tests passed with {coverage_results['coverage']:.1f}% coverage"
            elif test_results["passed"]:
                check.status = ReviewStatus.WARNING
                check.message = f"Tests passed but coverage ({coverage_results['coverage']:.1f}%) below threshold ({self.config.test_coverage_threshold}%)"
            else:
                check.status = ReviewStatus.FAILED
                check.message = f"{test_results['failed']} tests failed"
            
            check.details = {
                "test_files": test_files,
                "test_results": test_results,
                "coverage_results": coverage_results
            }
            
            execution_time = (datetime.now() - start_time).total_seconds()
            check.execution_time = execution_time
            
            return check
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            return ReviewCheck(
                check_type=CheckType.UNIT,
                name=self.get_check_name(),
                description=self.get_check_description(),
                status=ReviewStatus.ERROR,
                message=f"Unit test execution failed: {str(e)}",
                execution_time=execution_time
            )
    
    def _find_test_files(self, target_path: str) -> List[str]:
        """Find test files in the target path."""
        test_files = []
        path = Path(target_path)
        
        if path.is_file() and ('test_' in path.name or path.name.endswith('_test.py')):
            test_files.append(str(path))
        elif path.is_dir():
            for test_file in path.rglob('test_*.py'):
                test_files.append(str(test_file))
            for test_file in path.rglob('*_test.py'):
                test_files.append(str(test_file))
        
        return test_files
    
    async def _run_tests(self, test_files: List[str]) -> Dict[str, Any]:
        """Run unit tests."""
        try:
            # Run pytest on test files
            cmd = [self.config.test_framework, "-v", "--tb=short"] + test_files
            
            result = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await asyncio.wait_for(
                result.communicate(),
                timeout=self.config.test_timeout
            )
            
            # Parse pytest output (simplified)
            output = stdout.decode() if stdout else ""
            error_output = stderr.decode() if stderr else ""
            
            # Count passed/failed tests (simplified parsing)
            passed = output.count("PASSED")
            failed = output.count("FAILED")
            
            return {
                "passed": passed,
                "failed": failed,
                "total": passed + failed,
                "output": output,
                "error_output": error_output,
                "return_code": result.returncode
            }
            
        except asyncio.TimeoutError:
            return {
                "passed": 0,
                "failed": 0,
                "total": 0,
                "output": "",
                "error_output": "Test execution timed out",
                "return_code": -1
            }
        except Exception as e:
            return {
                "passed": 0,
                "failed": 0,
                "total": 0,
                "output": "",
                "error_output": str(e),
                "return_code": -1
            }
    
    async def _check_coverage(self, target_path: str) -> Dict[str, Any]:
        """Check test coverage."""
        try:
            # Run coverage analysis
            cmd = ["coverage", "run", "-m", "pytest", target_path]
            
            result = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            await asyncio.wait_for(
                result.communicate(),
                timeout=self.config.test_timeout
            )
            
            # Get coverage report
            report_cmd = ["coverage", "report", "--show-missing"]
            
            report_result = await asyncio.create_subprocess_exec(
                *report_cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await report_result.communicate()
            
            # Parse coverage percentage (simplified)
            output = stdout.decode() if stdout else ""
            coverage = 0.0
            
            if "TOTAL" in output:
                # Extract coverage percentage from pytest-cov output
                lines = output.split('\n')
                for line in lines:
                    if "TOTAL" in line:
                        parts = line.split()
                        for part in parts:
                            if part.endswith('%'):
                                try:
                                    coverage = float(part[:-1])
                                    break
                                except ValueError:
                                    continue
            
            return {
                "coverage": coverage,
                "output": output,
                "error_output": stderr.decode() if stderr else ""
            }
            
        except Exception as e:
            return {
                "coverage": 0.0,
                "output": "",
                "error_output": str(e)
            }


class AcceptanceCriteriaValidator(ReviewCheckBase):
    """Acceptance criteria validator."""
    
    def get_check_name(self) -> str:
        return "Acceptance Criteria"
    
    def get_check_description(self) -> str:
        return "Validates acceptance criteria and requirements"
    
    async def check(self, target_path: str, context: Dict[str, Any]) -> ReviewCheck:
        """Perform acceptance criteria check."""
        start_time = datetime.now()
        
        try:
            check = ReviewCheck(
                check_type=CheckType.ACCEPTANCE,
                name=self.get_check_name(),
                description=self.get_check_description(),
                status=ReviewStatus.IN_PROGRESS
            )
            
            # Look for acceptance criteria files
            criteria_files = self._find_acceptance_files(target_path)
            
            if not criteria_files:
                check.status = ReviewStatus.WARNING
                check.message = "No acceptance criteria files found"
                check.details = {"criteria_files_found": 0}
                return check
            
            # Validate acceptance criteria
            validation_results = await self._validate_acceptance_criteria(criteria_files, target_path)
            
            # Determine overall status
            if validation_results["passed"]:
                check.status = ReviewStatus.PASSED
                check.message = f"All {validation_results['total']} acceptance criteria validated"
            else:
                check.status = ReviewStatus.FAILED
                check.message = f"{validation_results['failed']} acceptance criteria failed"
            
            check.details = validation_results
            
            execution_time = (datetime.now() - start_time).total_seconds()
            check.execution_time = execution_time
            
            return check
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            return ReviewCheck(
                check_type=CheckType.ACCEPTANCE,
                name=self.get_check_name(),
                description=self.get_check_description(),
                status=ReviewStatus.ERROR,
                message=f"Acceptance criteria validation failed: {str(e)}",
                execution_time=execution_time
            )
    
    def _find_acceptance_files(self, target_path: str) -> List[str]:
        """Find acceptance criteria files."""
        criteria_files = []
        path = Path(target_path)
        
        # Look for common acceptance criteria file patterns
        patterns = [
            "acceptance_criteria.md",
            "acceptance_criteria.json",
            "requirements.md",
            "requirements.json",
            "criteria.md",
            "criteria.json"
        ]
        
        if path.is_file():
            if any(pattern in path.name for pattern in patterns):
                criteria_files.append(str(path))
        elif path.is_dir():
            for pattern in patterns:
                for file_path in path.rglob(pattern):
                    criteria_files.append(str(file_path))
        
        return criteria_files
    
    async def _validate_acceptance_criteria(self, criteria_files: List[str], target_path: str) -> Dict[str, Any]:
        """Validate acceptance criteria."""
        results = {
            "total": 0,
            "passed": 0,
            "failed": 0,
            "criteria": []
        }
        
        for file_path in criteria_files:
            try:
                criteria = await self._parse_criteria_file(file_path)
                
                for criterion in criteria:
                    results["total"] += 1
                    
                    # Validate individual criterion
                    validation_result = await self._validate_criterion(criterion, target_path)
                    
                    if validation_result["passed"]:
                        results["passed"] += 1
                    else:
                        results["failed"] += 1
                    
                    results["criteria"].append({
                        "file": file_path,
                        "criterion": criterion,
                        "result": validation_result
                    })
            
            except Exception as e:
                results["criteria"].append({
                    "file": file_path,
                    "error": str(e)
                })
        
        return results
    
    async def _parse_criteria_file(self, file_path: str) -> List[Dict[str, Any]]:
        """Parse acceptance criteria file."""
        path = Path(file_path)
        
        if path.suffix == '.json':
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get("criteria", [])
        else:
            # Parse markdown file (simplified)
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Simple parsing - look for criteria patterns
            criteria = []
            lines = content.split('\n')
            
            for line in lines:
                line = line.strip()
                if line.startswith('- ') or line.startswith('* '):
                    criteria.append({
                        "description": line[2:],
                        "type": "functional"
                    })
                elif line.startswith('##') or line.startswith('###'):
                    criteria.append({
                        "description": line[2:].strip(),
                        "type": "requirement"
                    })
            
            return criteria
    
    async def _validate_criterion(self, criterion: Dict[str, Any], target_path: str) -> Dict[str, Any]:
        """Validate individual acceptance criterion."""
        # This is a simplified validation - in practice, you'd have more sophisticated logic
        description = criterion.get("description", "")
        
        # Check if criterion is testable
        testable_keywords = ["should", "must", "will", "can", "able to", "support", "handle"]
        is_testable = any(keyword in description.lower() for keyword in testable_keywords)
        
        # Check if criterion has clear success criteria
        has_success_criteria = any(word in description.lower() for word in ["pass", "fail", "success", "error", "exception"])
        
        return {
            "passed": is_testable and has_success_criteria,
            "is_testable": is_testable,
            "has_success_criteria": has_success_criteria,
            "description": description
        }


# ============================================================================
# Main Agent Reviewer
# ============================================================================

class AgentReviewer:
    """Main agent reviewer that orchestrates all review checks."""
    
    def __init__(self, config: Optional[ReviewConfig] = None):
        self.config = config or ReviewConfig()
        self.logger = logging.getLogger(__name__)
        
        # Initialize checkers
        self.checkers: List[ReviewCheckBase] = []
        
        if self.config.enable_schema_checks:
            self.checkers.append(SchemaValidator(self.config))
        
        if self.config.enable_unit_checks:
            self.checkers.append(UnitTestRunner(self.config))
        
        if self.config.enable_acceptance_checks:
            self.checkers.append(AcceptanceCriteriaValidator(self.config))
        
        # Statistics
        self.total_reviews = 0
        self.successful_reviews = 0
        self.failed_reviews = 0
    
    async def review(self, target_path: str, context: Optional[Dict[str, Any]] = None) -> ReviewReport:
        """Perform comprehensive review of the target."""
        context = context or {}
        
        self.logger.info(f"Starting review of: {target_path}")
        
        # Create report
        report = ReviewReport(
            target_path=target_path,
            review_type="comprehensive",
            status=ReviewStatus.IN_PROGRESS,
            metadata=context
        )
        
        try:
            # Run all checks
            for checker in self.checkers:
                self.logger.info(f"Running {checker.get_check_name()} check")
                
                check_result = await checker.check(target_path, context)
                report.checks.append(check_result)
            
            # Update overall status
            report.status = report.get_overall_status()
            report.completed_at = datetime.now(timezone.utc)
            
            # Generate summary and recommendations
            report.summary = report.get_summary_stats()
            report.recommendations = await self._generate_recommendations(report)
            
            # Update statistics
            self.total_reviews += 1
            if report.status == ReviewStatus.PASSED:
                self.successful_reviews += 1
            else:
                self.failed_reviews += 1
            
            self.logger.info(f"Review completed with status: {report.status}")
            
            return report
            
        except Exception as e:
            self.logger.error(f"Review failed: {e}")
            report.status = ReviewStatus.ERROR
            report.completed_at = datetime.now(timezone.utc)
            report.summary = {"error": str(e)}
            
            self.failed_reviews += 1
            
            return report
    
    async def _generate_recommendations(self, report: ReviewReport) -> List[str]:
        """Generate recommendations based on review results."""
        recommendations = []
        
        # Analyze check results
        failed_checks = [check for check in report.checks if check.status == ReviewStatus.FAILED]
        warning_checks = [check for check in report.checks if check.status == ReviewStatus.WARNING]
        
        # Schema recommendations
        schema_checks = [check for check in failed_checks if check.check_type == CheckType.SCHEMA]
        if schema_checks:
            recommendations.append("Fix schema validation issues by ensuring all Pydantic models have proper field definitions and validators")
        
        # Unit test recommendations
        unit_checks = [check for check in failed_checks if check.check_type == CheckType.UNIT]
        if unit_checks:
            recommendations.append("Improve test coverage and fix failing unit tests")
        
        # Acceptance criteria recommendations
        acceptance_checks = [check for check in failed_checks if check.check_type == CheckType.ACCEPTANCE]
        if acceptance_checks:
            recommendations.append("Define clear acceptance criteria with testable requirements")
        
        # General recommendations
        if not failed_checks and not warning_checks:
            recommendations.append("All checks passed! Consider adding more comprehensive tests for edge cases")
        
        return recommendations
    
    async def save_report(self, report: ReviewReport, output_path: str) -> None:
        """Save review report to file."""
        try:
            if self.config.output_format == "json":
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(report.dict(), f, indent=2, default=str)
            else:
                # For other formats, save as JSON for now
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(report.dict(), f, indent=2, default=str)
            
            self.logger.info(f"Review report saved to: {output_path}")
            
        except Exception as e:
            self.logger.error(f"Failed to save report: {e}")
            raise
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get reviewer statistics."""
        success_rate = (self.successful_reviews / self.total_reviews * 100) if self.total_reviews > 0 else 0
        
        return {
            "total_reviews": self.total_reviews,
            "successful_reviews": self.successful_reviews,
            "failed_reviews": self.failed_reviews,
            "success_rate": success_rate,
            "enabled_checks": [checker.get_check_name() for checker in self.checkers]
        }


# ============================================================================
# Factory Functions
# ============================================================================

def create_agent_reviewer(
    enable_schema: bool = True,
    enable_unit: bool = True,
    enable_acceptance: bool = True,
    **kwargs
) -> AgentReviewer:
    """Create an agent reviewer with specified configuration."""
    config = ReviewConfig(
        enable_schema_checks=enable_schema,
        enable_unit_checks=enable_unit,
        enable_acceptance_checks=enable_acceptance,
        **kwargs
    )
    return AgentReviewer(config)


def create_review_config(
    schema_strict: bool = True,
    test_coverage_threshold: float = 80.0,
    test_timeout: float = 300.0,
    **kwargs
) -> ReviewConfig:
    """Create a review configuration."""
    return ReviewConfig(
        schema_strict_mode=schema_strict,
        test_coverage_threshold=test_coverage_threshold,
        test_timeout=test_timeout,
        **kwargs
    )


# ============================================================================
# Export all classes and functions
# ============================================================================

__all__ = [
    # Enums
    "ReviewStatus",
    "CheckType",
    
    # Models
    "ReviewCheck",
    "ReviewReport",
    "ReviewConfig",
    
    # Check implementations
    "ReviewCheckBase",
    "SchemaValidator",
    "UnitTestRunner",
    "AcceptanceCriteriaValidator",
    
    # Main reviewer
    "AgentReviewer",
    
    # Factory functions
    "create_agent_reviewer",
    "create_review_config",
]
