"""
Comprehensive System Checker for Agentic LLM Core v0.1

This module performs comprehensive checks including:
- Test coverage analysis (minimum 80%)
- Specification compliance validation
- Critical issue detection
- Fail-fast error reporting

Created: 2024-09-24
Status: Draft
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union
from uuid import uuid4

import yaml
from pydantic import BaseModel, Field

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


# ============================================================================
# Data Models
# ============================================================================

class CheckStatus(str, Enum):
    """Check status."""
    PASS = "pass"
    FAIL = "fail"
    WARNING = "warning"
    SKIP = "skip"


class CheckSeverity(str, Enum):
    """Check severity."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class CheckResult(BaseModel):
    """Individual check result."""
    check_id: str = Field(default_factory=lambda: str(uuid4()), description="Check ID")
    name: str = Field(..., description="Check name")
    status: CheckStatus = Field(..., description="Check status")
    severity: CheckSeverity = Field(..., description="Check severity")
    message: str = Field(..., description="Check message")
    details: Dict[str, Any] = Field(default_factory=dict, description="Check details")
    execution_time: float = Field(0.0, description="Execution time in seconds")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Check timestamp")


class CoverageReport(BaseModel):
    """Test coverage report."""
    total_coverage: float = Field(..., description="Total coverage percentage")
    file_coverage: Dict[str, float] = Field(default_factory=dict, description="Per-file coverage")
    missing_lines: Dict[str, List[int]] = Field(default_factory=dict, description="Missing lines per file")
    total_lines: int = Field(0, description="Total lines of code")
    covered_lines: int = Field(0, description="Covered lines of code")


class SpecComplianceReport(BaseModel):
    """Specification compliance report."""
    spec_files: List[str] = Field(default_factory=list, description="Specification files found")
    implemented_features: List[str] = Field(default_factory=list, description="Implemented features")
    missing_features: List[str] = Field(default_factory=list, description="Missing features")
    compliance_score: float = Field(0.0, description="Compliance score (0-100)")


class SystemCheckReport(BaseModel):
    """Comprehensive system check report."""
    report_id: str = Field(default_factory=lambda: str(uuid4()), description="Report ID")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Report timestamp")
    total_checks: int = Field(0, description="Total checks performed")
    passed_checks: int = Field(0, description="Passed checks")
    failed_checks: int = Field(0, description="Failed checks")
    warning_checks: int = Field(0, description="Warning checks")
    skipped_checks: int = Field(0, description="Skipped checks")
    coverage_report: Optional[CoverageReport] = Field(None, description="Coverage report")
    spec_compliance_report: Optional[SpecComplianceReport] = Field(None, description="Spec compliance report")
    check_results: List[CheckResult] = Field(default_factory=list, description="Individual check results")
    critical_issues: List[CheckResult] = Field(default_factory=list, description="Critical issues found")
    recommendations: List[str] = Field(default_factory=list, description="Recommendations")
    overall_status: CheckStatus = Field(CheckStatus.PASS, description="Overall system status")


# ============================================================================
# System Checker
# ============================================================================

class SystemChecker:
    """Comprehensive system checker."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.logger = logging.getLogger(__name__)
        self.config = config or {}
        self.coverage_min = self.config.get('coverage_min', 80.0)
        self.spec_compliance_required = self.config.get('spec_compliance', True)
        self.fail_fast = self.config.get('fail_fast', True)
        self.check_results: List[CheckResult] = []
        self.critical_issues: List[CheckResult] = []
        
    async def run_comprehensive_check(self) -> SystemCheckReport:
        """Run comprehensive system check."""
        start_time = time.time()
        self.logger.info("Starting comprehensive system check...")
        
        # Initialize report
        report = SystemCheckReport()
        
        try:
            # Run all checks
            checks = [
                self._check_project_structure,
                self._check_dependencies,
                self._check_test_coverage,
                self._check_spec_compliance,
                self._check_security_policies,
                self._check_model_policies,
                self._check_code_quality,
                self._check_documentation,
                self._check_configuration,
                self._check_performance_requirements
            ]
            
            for check_func in checks:
                try:
                    result = await check_func()
                    self.check_results.append(result)
                    
                    if result.status == CheckStatus.FAIL:
                        if result.severity == CheckSeverity.CRITICAL:
                            self.critical_issues.append(result)
                            if self.fail_fast:
                                self.logger.error(f"Critical issue found: {result.message}")
                                break
                        else:
                            self.logger.warning(f"Check failed: {result.message}")
                    elif result.status == CheckStatus.WARNING:
                        self.logger.warning(f"Check warning: {result.message}")
                    else:
                        self.logger.info(f"Check passed: {result.name}")
                        
                except Exception as e:
                    error_result = CheckResult(
                        name=check_func.__name__,
                        status=CheckStatus.FAIL,
                        severity=CheckSeverity.CRITICAL,
                        message=f"Check execution failed: {str(e)}",
                        details={"error": str(e)}
                    )
                    self.check_results.append(error_result)
                    self.critical_issues.append(error_result)
                    
                    if self.fail_fast:
                        self.logger.error(f"Critical error in {check_func.__name__}: {e}")
                        break
            
            # Compile report
            report.check_results = self.check_results
            report.critical_issues = self.critical_issues
            report.total_checks = len(self.check_results)
            report.passed_checks = len([r for r in self.check_results if r.status == CheckStatus.PASS])
            report.failed_checks = len([r for r in self.check_results if r.status == CheckStatus.FAIL])
            report.warning_checks = len([r for r in self.check_results if r.status == CheckStatus.WARNING])
            report.skipped_checks = len([r for r in self.check_results if r.status == CheckStatus.SKIP])
            
            # Determine overall status
            if self.critical_issues:
                report.overall_status = CheckStatus.FAIL
            elif report.failed_checks > 0:
                report.overall_status = CheckStatus.WARNING
            else:
                report.overall_status = CheckStatus.PASS
            
            # Generate recommendations
            report.recommendations = self._generate_recommendations(report)
            
            execution_time = time.time() - start_time
            self.logger.info(f"Comprehensive check completed in {execution_time:.2f}s")
            self.logger.info(f"Overall status: {report.overall_status.value}")
            
        except Exception as e:
            self.logger.error(f"System check failed: {e}")
            report.overall_status = CheckStatus.FAIL
            report.recommendations = [f"System check failed: {str(e)}"]
        
        return report
    
    async def _check_project_structure(self) -> CheckResult:
        """Check project structure compliance."""
        start_time = time.time()
        
        required_dirs = [
            "src/core",
            "src/core/models",
            "src/core/providers", 
            "src/core/tools",
            "src/core/memory",
            "src/core/runtime",
            "src/core/security",
            "tests",
            "configs",
            "specs",
            "plans",
            "tasks"
        ]
        
        required_files = [
            "src/core/models/contracts.py",
            "src/core/providers/llm_qwen3.py",
            "src/core/tools/mcp_adapter.py",
            "src/core/memory/vector_pg.py",
            "src/core/runtime/planner.py",
            "src/core/runtime/reviewer.py",
            "src/core/runtime/runner.py",
            "src/core/security/policy_manager.py",
            "configs/policies.yaml",
            "specs/problem.md",
            "specs/system.md"
        ]
        
        missing_dirs = []
        missing_files = []
        
        for dir_path in required_dirs:
            if not Path(dir_path).exists():
                missing_dirs.append(dir_path)
        
        for file_path in required_files:
            if not Path(file_path).exists():
                missing_files.append(file_path)
        
        execution_time = time.time() - start_time
        
        if missing_dirs or missing_files:
            return CheckResult(
                name="project_structure",
                status=CheckStatus.FAIL,
                severity=CheckSeverity.HIGH,
                message=f"Missing {len(missing_dirs)} directories and {len(missing_files)} files",
                details={
                    "missing_dirs": missing_dirs,
                    "missing_files": missing_files
                },
                execution_time=execution_time
            )
        else:
            return CheckResult(
                name="project_structure",
                status=CheckStatus.PASS,
                severity=CheckSeverity.LOW,
                message="Project structure is compliant",
                details={
                    "checked_dirs": len(required_dirs),
                    "checked_files": len(required_files)
                },
                execution_time=execution_time
            )
    
    async def _check_dependencies(self) -> CheckResult:
        """Check dependency requirements."""
        start_time = time.time()
        
        required_packages = [
            "pydantic",
            "torch",
            "psutil",
            "yaml",
            "asyncio"
        ]
        
        missing_packages = []
        
        for package in required_packages:
            try:
                __import__(package)
            except ImportError:
                missing_packages.append(package)
        
        execution_time = time.time() - start_time
        
        if missing_packages:
            return CheckResult(
                name="dependencies",
                status=CheckStatus.FAIL,
                severity=CheckSeverity.CRITICAL,
                message=f"Missing required packages: {', '.join(missing_packages)}",
                details={"missing_packages": missing_packages},
                execution_time=execution_time
            )
        else:
            return CheckResult(
                name="dependencies",
                status=CheckStatus.PASS,
                severity=CheckSeverity.LOW,
                message="All required dependencies are available",
                details={"checked_packages": len(required_packages)},
                execution_time=execution_time
            )
    
    async def _check_test_coverage(self) -> CheckResult:
        """Check test coverage."""
        start_time = time.time()
        
        try:
            # Run pytest with coverage
            result = subprocess.run([
                "python3", "-m", "pytest", 
                "--cov=src", 
                "--cov-report=json",
                "--cov-report=term-missing",
                "-q"
            ], capture_output=True, text=True, timeout=60)
            
            # Parse coverage report
            coverage_file = Path(".coverage.json")
            if coverage_file.exists():
                with open(coverage_file, 'r') as f:
                    coverage_data = json.load(f)
                
                total_coverage = coverage_data.get('totals', {}).get('percent_covered', 0.0)
                
                execution_time = time.time() - start_time
                
                if total_coverage >= self.coverage_min:
                    return CheckResult(
                        name="test_coverage",
                        status=CheckStatus.PASS,
                        severity=CheckSeverity.LOW,
                        message=f"Test coverage {total_coverage:.1f}% meets minimum requirement {self.coverage_min}%",
                        details={
                            "total_coverage": total_coverage,
                            "minimum_required": self.coverage_min,
                            "coverage_data": coverage_data
                        },
                        execution_time=execution_time
                    )
                else:
                    return CheckResult(
                        name="test_coverage",
                        status=CheckStatus.FAIL,
                        severity=CheckSeverity.HIGH,
                        message=f"Test coverage {total_coverage:.1f}% below minimum requirement {self.coverage_min}%",
                        details={
                            "total_coverage": total_coverage,
                            "minimum_required": self.coverage_min,
                            "coverage_data": coverage_data
                        },
                        execution_time=execution_time
                    )
            else:
                return CheckResult(
                    name="test_coverage",
                    status=CheckStatus.FAIL,
                    severity=CheckSeverity.HIGH,
                    message="Coverage report not generated",
                    details={"error": "No .coverage.json file found"},
                    execution_time=time.time() - start_time
                )
                
        except subprocess.TimeoutExpired:
            return CheckResult(
                name="test_coverage",
                status=CheckStatus.FAIL,
                severity=CheckSeverity.HIGH,
                message="Test execution timed out",
                details={"error": "pytest execution exceeded 60 seconds"},
                execution_time=time.time() - start_time
            )
        except Exception as e:
            return CheckResult(
                name="test_coverage",
                status=CheckStatus.FAIL,
                severity=CheckSeverity.HIGH,
                message=f"Test coverage check failed: {str(e)}",
                details={"error": str(e)},
                execution_time=time.time() - start_time
            )
    
    async def _check_spec_compliance(self) -> CheckResult:
        """Check specification compliance."""
        start_time = time.time()
        
        spec_files = ["specs/problem.md", "specs/system.md"]
        missing_specs = []
        implemented_features = []
        missing_features = []
        
        for spec_file in spec_files:
            if not Path(spec_file).exists():
                missing_specs.append(spec_file)
        
        # Check for implemented features based on existing files
        feature_checks = {
            "Core Models": Path("src/core/models/contracts.py").exists(),
            "Qwen3 Provider": Path("src/core/providers/llm_qwen3.py").exists(),
            "MCP Adapter": Path("src/core/tools/mcp_adapter.py").exists(),
            "Vector Store": Path("src/core/memory/vector_pg.py").exists(),
            "Agent Planner": Path("src/core/runtime/planner.py").exists(),
            "Agent Reviewer": Path("src/core/runtime/reviewer.py").exists(),
            "Task Runner": Path("src/core/runtime/runner.py").exists(),
            "Security Policies": Path("src/core/security/policy_manager.py").exists(),
            "Model Policies": Path("src/core/models/policy_manager.py").exists()
        }
        
        for feature, implemented in feature_checks.items():
            if implemented:
                implemented_features.append(feature)
            else:
                missing_features.append(feature)
        
        execution_time = time.time() - start_time
        
        if missing_specs:
            return CheckResult(
                name="spec_compliance",
                status=CheckStatus.FAIL,
                severity=CheckSeverity.CRITICAL,
                message=f"Missing specification files: {', '.join(missing_specs)}",
                details={
                    "missing_specs": missing_specs,
                    "implemented_features": implemented_features,
                    "missing_features": missing_features
                },
                execution_time=execution_time
            )
        elif missing_features:
            return CheckResult(
                name="spec_compliance",
                status=CheckStatus.WARNING,
                severity=CheckSeverity.MEDIUM,
                message=f"Missing {len(missing_features)} features from specifications",
                details={
                    "implemented_features": implemented_features,
                    "missing_features": missing_features
                },
                execution_time=execution_time
            )
        else:
            return CheckResult(
                name="spec_compliance",
                status=CheckStatus.PASS,
                severity=CheckSeverity.LOW,
                message="All specification requirements are met",
                details={
                    "implemented_features": implemented_features,
                    "missing_features": missing_features
                },
                execution_time=execution_time
            )
    
    async def _check_security_policies(self) -> CheckResult:
        """Check security policy implementation."""
        start_time = time.time()
        
        try:
            # Import and test security policy manager
            sys.path.insert(0, "src")
            from core.security.policy_manager import SecurityPolicyManager
            
            manager = SecurityPolicyManager("configs/policies.yaml")
            
            # Test redaction
            test_text = "My API key is sk-1234567890abcdef and email is user@example.com"
            redaction_result = manager.redact_text(test_text)
            
            # Test tool access
            tool_result = manager.check_tool_access("mcp:sql")
            
            execution_time = time.time() - start_time
            
            if redaction_result.redaction_count > 0 and tool_result.allowed:
                return CheckResult(
                    name="security_policies",
                    status=CheckStatus.PASS,
                    severity=CheckSeverity.LOW,
                    message="Security policies are properly implemented",
                    details={
                        "redaction_patterns": len(manager.redaction_patterns),
                        "allowed_tools": len(manager.allowed_tools),
                        "blocked_tools": len(manager.blocked_tools),
                        "test_redaction_count": redaction_result.redaction_count,
                        "test_tool_access": tool_result.allowed
                    },
                    execution_time=execution_time
                )
            else:
                return CheckResult(
                    name="security_policies",
                    status=CheckStatus.FAIL,
                    severity=CheckSeverity.HIGH,
                    message="Security policy tests failed",
                    details={
                        "redaction_test": redaction_result.redaction_count > 0,
                        "tool_access_test": tool_result.allowed
                    },
                    execution_time=execution_time
                )
                
        except Exception as e:
            return CheckResult(
                name="security_policies",
                status=CheckStatus.FAIL,
                severity=CheckSeverity.CRITICAL,
                message=f"Security policy check failed: {str(e)}",
                details={"error": str(e)},
                execution_time=time.time() - start_time
            )
    
    async def _check_model_policies(self) -> CheckResult:
        """Check model policy implementation."""
        start_time = time.time()
        
        try:
            # Import and test model policy manager
            sys.path.insert(0, "src")
            from core.models.policy_manager import ModelPolicyManager
            
            manager = ModelPolicyManager("configs/policies.yaml")
            
            # Test model selection
            from core.models.policy_manager import ModelRequest
            request = ModelRequest(
                input_type="multimodal",
                input_tokens=1000,
                capabilities_required=[]
            )
            
            selection = await manager.select_model(request)
            
            execution_time = time.time() - start_time
            
            if selection.selected_model and selection.confidence > 0:
                return CheckResult(
                    name="model_policies",
                    status=CheckStatus.PASS,
                    severity=CheckSeverity.LOW,
                    message="Model policies are properly implemented",
                    details={
                        "available_models": len(manager.models),
                        "routing_rules": len(manager.routing_rules),
                        "test_selection": selection.selected_model,
                        "test_confidence": selection.confidence
                    },
                    execution_time=execution_time
                )
            else:
                return CheckResult(
                    name="model_policies",
                    status=CheckStatus.FAIL,
                    severity=CheckSeverity.HIGH,
                    message="Model policy tests failed",
                    details={
                        "test_selection": selection.selected_model,
                        "test_confidence": selection.confidence
                    },
                    execution_time=execution_time
                )
                
        except Exception as e:
            return CheckResult(
                name="model_policies",
                status=CheckStatus.FAIL,
                severity=CheckSeverity.CRITICAL,
                message=f"Model policy check failed: {str(e)}",
                details={"error": str(e)},
                execution_time=time.time() - start_time
            )
    
    async def _check_code_quality(self) -> CheckResult:
        """Check code quality."""
        start_time = time.time()
        
        # Check for common code quality issues
        issues = []
        
        # Check for TODO comments
        for py_file in Path("src").rglob("*.py"):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if "TODO" in content or "FIXME" in content:
                        issues.append(f"{py_file}: Contains TODO/FIXME comments")
            except Exception:
                pass
        
        # Check for missing docstrings
        for py_file in Path("src").rglob("*.py"):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if "def " in content and '"""' not in content:
                        issues.append(f"{py_file}: Missing docstrings")
            except Exception:
                pass
        
        execution_time = time.time() - start_time
        
        if issues:
            return CheckResult(
                name="code_quality",
                status=CheckStatus.WARNING,
                severity=CheckSeverity.MEDIUM,
                message=f"Found {len(issues)} code quality issues",
                details={"issues": issues},
                execution_time=execution_time
            )
        else:
            return CheckResult(
                name="code_quality",
                status=CheckStatus.PASS,
                severity=CheckSeverity.LOW,
                message="Code quality is acceptable",
                details={"checked_files": len(list(Path("src").rglob("*.py")))},
                execution_time=execution_time
            )
    
    async def _check_documentation(self) -> CheckResult:
        """Check documentation completeness."""
        start_time = time.time()
        
        required_docs = [
            "specs/problem.md",
            "specs/system.md",
            "plans/architecture.md",
            "plans/milestones.md"
        ]
        
        missing_docs = []
        for doc in required_docs:
            if not Path(doc).exists():
                missing_docs.append(doc)
        
        execution_time = time.time() - start_time
        
        if missing_docs:
            return CheckResult(
                name="documentation",
                status=CheckStatus.FAIL,
                severity=CheckSeverity.MEDIUM,
                message=f"Missing documentation: {', '.join(missing_docs)}",
                details={"missing_docs": missing_docs},
                execution_time=execution_time
            )
        else:
            return CheckResult(
                name="documentation",
                status=CheckStatus.PASS,
                severity=CheckSeverity.LOW,
                message="Documentation is complete",
                details={"checked_docs": len(required_docs)},
                execution_time=execution_time
            )
    
    async def _check_configuration(self) -> CheckResult:
        """Check configuration files."""
        start_time = time.time()
        
        config_files = ["configs/policies.yaml"]
        invalid_configs = []
        
        for config_file in config_files:
            try:
                with open(config_file, 'r') as f:
                    yaml.safe_load(f)
            except Exception as e:
                invalid_configs.append(f"{config_file}: {str(e)}")
        
        execution_time = time.time() - start_time
        
        if invalid_configs:
            return CheckResult(
                name="configuration",
                status=CheckStatus.FAIL,
                severity=CheckSeverity.HIGH,
                message=f"Invalid configuration files: {', '.join(invalid_configs)}",
                details={"invalid_configs": invalid_configs},
                execution_time=execution_time
            )
        else:
            return CheckResult(
                name="configuration",
                status=CheckStatus.PASS,
                severity=CheckSeverity.LOW,
                message="Configuration files are valid",
                details={"checked_configs": len(config_files)},
                execution_time=execution_time
            )
    
    async def _check_performance_requirements(self) -> CheckResult:
        """Check performance requirements."""
        start_time = time.time()
        
        # Check if performance-critical files exist
        performance_files = [
            "src/core/providers/llm_qwen3.py",
            "src/core/runtime/runner.py",
            "src/core/memory/vector_pg.py"
        ]
        
        missing_files = []
        for file_path in performance_files:
            if not Path(file_path).exists():
                missing_files.append(file_path)
        
        execution_time = time.time() - start_time
        
        if missing_files:
            return CheckResult(
                name="performance_requirements",
                status=CheckStatus.FAIL,
                severity=CheckSeverity.HIGH,
                message=f"Missing performance-critical files: {', '.join(missing_files)}",
                details={"missing_files": missing_files},
                execution_time=execution_time
            )
        else:
            return CheckResult(
                name="performance_requirements",
                status=CheckStatus.PASS,
                severity=CheckSeverity.LOW,
                message="Performance-critical components are present",
                details={"checked_files": len(performance_files)},
                execution_time=execution_time
            )
    
    def _generate_recommendations(self, report: SystemCheckReport) -> List[str]:
        """Generate recommendations based on check results."""
        recommendations = []
        
        if report.failed_checks > 0:
            recommendations.append(f"Address {report.failed_checks} failed checks")
        
        if report.warning_checks > 0:
            recommendations.append(f"Review {report.warning_checks} warning checks")
        
        if report.coverage_report and report.coverage_report.total_coverage < self.coverage_min:
            recommendations.append(f"Increase test coverage from {report.coverage_report.total_coverage:.1f}% to {self.coverage_min}%")
        
        if report.critical_issues:
            recommendations.append(f"Fix {len(report.critical_issues)} critical issues immediately")
        
        if report.overall_status == CheckStatus.PASS:
            recommendations.append("System is in good condition - consider adding more comprehensive tests")
        
        return recommendations


# ============================================================================
# Main Function
# ============================================================================

async def main():
    """Main function for command-line usage."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Comprehensive System Checker")
    parser.add_argument("--coverage-min", type=float, default=80.0, help="Minimum coverage percentage")
    parser.add_argument("--spec-compliance", action="store_true", help="Require spec compliance")
    parser.add_argument("--fail-fast", action="store_true", help="Fail fast on critical issues")
    parser.add_argument("--output", help="Output file for report")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    config = {
        "coverage_min": args.coverage_min,
        "spec_compliance": args.spec_compliance,
        "fail_fast": args.fail_fast
    }
    
    try:
        checker = SystemChecker(config)
        report = await checker.run_comprehensive_check()
        
        # Print summary
        print("\n" + "="*80)
        print("COMPREHENSIVE SYSTEM CHECK REPORT")
        print("="*80)
        print(f"Report ID: {report.report_id}")
        print(f"Timestamp: {report.timestamp}")
        print(f"Overall Status: {report.overall_status.value.upper()}")
        print(f"Total Checks: {report.total_checks}")
        print(f"Passed: {report.passed_checks} ✅")
        print(f"Failed: {report.failed_checks} ❌")
        print(f"Warnings: {report.warning_checks} ⚠️")
        print(f"Skipped: {report.skipped_checks} ⏭️")
        
        if report.critical_issues:
            print(f"\n🚨 CRITICAL ISSUES ({len(report.critical_issues)}):")
            for issue in report.critical_issues:
                print(f"   ❌ {issue.name}: {issue.message}")
        
        if report.recommendations:
            print(f"\n💡 RECOMMENDATIONS:")
            for rec in report.recommendations:
                print(f"   • {rec}")
        
        # Save report if requested
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(report.model_dump(), f, indent=2, default=str)
            print(f"\n📄 Report saved to: {args.output}")
        
        return 0 if report.overall_status == CheckStatus.PASS else 1
        
    except Exception as e:
        logger.error(f"System check failed: {e}")
        return 1


if __name__ == "__main__":
    exit(asyncio.run(main()))
