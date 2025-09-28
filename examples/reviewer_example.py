"""
Agent Reviewer Example

This example demonstrates how to use the agent reviewer to perform
comprehensive code reviews including schema validation, unit testing,
and acceptance criteria checks.

Created: 2024-09-24
Status: Draft
"""

import asyncio
import json
import logging
import tempfile
from pathlib import Path
from typing import Dict, Any

from src.core.runtime.reviewer import (
    create_agent_reviewer,
    create_review_config,
    ReviewStatus,
    CheckType
)


# ============================================================================
# Example Usage
# ============================================================================

async def main():
    """Main example function."""
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    logger.info("Starting Agent Reviewer Example")
    
    try:
        # 1. Create sample code for review
        logger.info("Creating sample code for review...")
        sample_code_dir = await create_sample_code()
        
        # 2. Example 1: Comprehensive Review
        logger.info("Example 1: Comprehensive Review")
        await example_comprehensive_review(sample_code_dir)
        
        # 3. Example 2: Schema-Only Review
        logger.info("Example 2: Schema-Only Review")
        await example_schema_only_review(sample_code_dir)
        
        # 4. Example 3: Unit Test Review
        logger.info("Example 3: Unit Test Review")
        await example_unit_test_review(sample_code_dir)
        
        # 5. Example 4: Acceptance Criteria Review
        logger.info("Example 4: Acceptance Criteria Review")
        await example_acceptance_review(sample_code_dir)
        
        # 6. Example 5: Custom Configuration Review
        logger.info("Example 5: Custom Configuration Review")
        await example_custom_config_review(sample_code_dir)
        
        # 7. Example 6: Review Report Analysis
        logger.info("Example 6: Review Report Analysis")
        await example_report_analysis(sample_code_dir)
        
        logger.info("Agent Reviewer Example completed successfully!")
        
    except Exception as e:
        logger.error(f"Example failed: {e}")
        raise


async def create_sample_code() -> str:
    """Create sample code for review examples."""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Create sample Python module with Pydantic models
        sample_module = temp_path / "sample_models.py"
        with open(sample_module, 'w') as f:
            f.write('''
"""
Sample Pydantic models for review testing.
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class UserRole(str, Enum):
    """User role enumeration."""
    ADMIN = "admin"
    USER = "user"
    GUEST = "guest"


class User(BaseModel):
    """User model with validation."""
    id: int = Field(..., description="User ID", gt=0)
    username: str = Field(..., description="Username", min_length=3, max_length=50)
    email: str = Field(..., description="Email address")
    role: UserRole = Field(default=UserRole.USER, description="User role")
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")
    is_active: bool = Field(default=True, description="Whether user is active")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata")
    
    @validator('email')
    def validate_email(cls, v):
        if '@' not in v:
            raise ValueError('Invalid email format')
        return v.lower()
    
    @validator('username')
    def validate_username(cls, v):
        if not v.isalnum():
            raise ValueError('Username must be alphanumeric')
        return v


class Task(BaseModel):
    """Task model for task management."""
    id: str = Field(..., description="Task ID")
    title: str = Field(..., description="Task title", min_length=1, max_length=200)
    description: Optional[str] = Field(None, description="Task description")
    assignee_id: Optional[int] = Field(None, description="Assignee user ID")
    priority: int = Field(default=1, description="Task priority", ge=1, le=5)
    status: str = Field(default="pending", description="Task status")
    due_date: Optional[datetime] = Field(None, description="Due date")
    tags: List[str] = Field(default_factory=list, description="Task tags")
    created_by: int = Field(..., description="Creator user ID")
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")
    
    @validator('status')
    def validate_status(cls, v):
        valid_statuses = ['pending', 'in_progress', 'completed', 'cancelled']
        if v not in valid_statuses:
            raise ValueError(f'Status must be one of: {valid_statuses}')
        return v
    
    @validator('tags')
    def validate_tags(cls, v):
        if len(v) > 10:
            raise ValueError('Maximum 10 tags allowed')
        return v


class Project(BaseModel):
    """Project model."""
    id: str = Field(..., description="Project ID")
    name: str = Field(..., description="Project name", min_length=1, max_length=100)
    description: Optional[str] = Field(None, description="Project description")
    owner_id: int = Field(..., description="Project owner user ID")
    team_members: List[int] = Field(default_factory=list, description="Team member user IDs")
    tasks: List[Task] = Field(default_factory=list, description="Project tasks")
    start_date: Optional[datetime] = Field(None, description="Project start date")
    end_date: Optional[datetime] = Field(None, description="Project end date")
    budget: Optional[float] = Field(None, description="Project budget", ge=0)
    status: str = Field(default="planning", description="Project status")
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")
    
    @validator('end_date')
    def validate_end_date(cls, v, values):
        if v and 'start_date' in values and values['start_date']:
            if v <= values['start_date']:
                raise ValueError('End date must be after start date')
        return v
    
    @validator('team_members')
    def validate_team_members(cls, v):
        if len(v) > 50:
            raise ValueError('Maximum 50 team members allowed')
        return v
''')
        
        # Create sample test file
        sample_tests = temp_path / "test_sample_models.py"
        with open(sample_tests, 'w') as f:
            f.write('''
"""
Tests for sample models.
"""

import pytest
from datetime import datetime, timedelta
from sample_models import User, Task, Project, UserRole


class TestUser:
    """Test User model."""
    
    def test_user_creation(self):
        """Test basic user creation."""
        user = User(
            id=1,
            username="testuser",
            email="test@example.com"
        )
        
        assert user.id == 1
        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.role == UserRole.USER
        assert user.is_active is True
        assert user.created_at is not None
    
    def test_user_validation(self):
        """Test user validation."""
        # Valid user
        user = User(id=1, username="validuser", email="valid@example.com")
        assert user.username == "validuser"
        
        # Invalid email
        with pytest.raises(ValueError):
            User(id=1, username="test", email="invalid-email")
        
        # Invalid username
        with pytest.raises(ValueError):
            User(id=1, username="test-user!", email="test@example.com")
        
        # Invalid ID
        with pytest.raises(ValueError):
            User(id=0, username="test", email="test@example.com")


class TestTask:
    """Test Task model."""
    
    def test_task_creation(self):
        """Test basic task creation."""
        task = Task(
            id="task-1",
            title="Test Task",
            created_by=1
        )
        
        assert task.id == "task-1"
        assert task.title == "Test Task"
        assert task.priority == 1
        assert task.status == "pending"
        assert task.created_by == 1
        assert task.created_at is not None
    
    def test_task_validation(self):
        """Test task validation."""
        # Valid task
        task = Task(id="task-1", title="Valid Task", created_by=1)
        assert task.status == "pending"
        
        # Invalid status
        with pytest.raises(ValueError):
            Task(id="task-1", title="Test", created_by=1, status="invalid")
        
        # Too many tags
        with pytest.raises(ValueError):
            Task(
                id="task-1",
                title="Test",
                created_by=1,
                tags=["tag"] * 11
            )


class TestProject:
    """Test Project model."""
    
    def test_project_creation(self):
        """Test basic project creation."""
        project = Project(
            id="proj-1",
            name="Test Project",
            owner_id=1
        )
        
        assert project.id == "proj-1"
        assert project.name == "Test Project"
        assert project.owner_id == 1
        assert project.status == "planning"
        assert project.created_at is not None
    
    def test_project_validation(self):
        """Test project validation."""
        # Valid project
        project = Project(id="proj-1", name="Valid Project", owner_id=1)
        assert project.status == "planning"
        
        # Invalid end date
        start_date = datetime.now()
        end_date = start_date - timedelta(days=1)
        
        with pytest.raises(ValueError):
            Project(
                id="proj-1",
                name="Test",
                owner_id=1,
                start_date=start_date,
                end_date=end_date
            )
        
        # Too many team members
        with pytest.raises(ValueError):
            Project(
                id="proj-1",
                name="Test",
                owner_id=1,
                team_members=list(range(51))
            )
''')
        
        # Create acceptance criteria file
        acceptance_criteria = temp_path / "acceptance_criteria.md"
        with open(acceptance_criteria, 'w') as f:
            f.write('''
# Acceptance Criteria for Sample Models

## User Management

### Functional Requirements

- The system should support user creation with valid email addresses
- The system must validate username format (alphanumeric only)
- The system will enforce user role assignments (admin, user, guest)
- The system can handle user metadata storage
- The system should support user activation/deactivation

### Non-Functional Requirements

- User creation should complete within 100ms
- The system must support 10,000 concurrent users
- User data must be encrypted at rest
- User validation should have 99.9% accuracy

## Task Management

### Functional Requirements

- The system should support task creation and assignment
- The system must validate task priority levels (1-5)
- The system will track task status changes
- The system can handle task due dates and scheduling
- The system should support task tagging and categorization

### Non-Functional Requirements

- Task operations should complete within 50ms
- The system must support 100,000 tasks per project
- Task data must be searchable within 200ms
- Task notifications should be delivered within 5 seconds

## Project Management

### Functional Requirements

- The system should support project creation and management
- The system must validate project team member limits
- The system will enforce project date constraints
- The system can handle project budget tracking
- The system should support project status workflows

### Non-Functional Requirements

- Project operations should complete within 200ms
- The system must support 1,000 projects per organization
- Project data must be backed up daily
- Project reports should generate within 30 seconds
''')
        
        # Create requirements file
        requirements = temp_path / "requirements.json"
        with open(requirements, 'w') as f:
            json.dump({
                "criteria": [
                    {
                        "id": "req-001",
                        "description": "User authentication system",
                        "type": "functional",
                        "priority": "high",
                        "testable": True
                    },
                    {
                        "id": "req-002", 
                        "description": "Task management workflow",
                        "type": "functional",
                        "priority": "high",
                        "testable": True
                    },
                    {
                        "id": "req-003",
                        "description": "Project collaboration features",
                        "type": "functional", 
                        "priority": "medium",
                        "testable": True
                    },
                    {
                        "id": "req-004",
                        "description": "System performance requirements",
                        "type": "non-functional",
                        "priority": "high",
                        "testable": True
                    }
                ]
            }, f, indent=2)
        
        return str(temp_path)


async def example_comprehensive_review(sample_code_dir: str):
    """Example: Comprehensive review with all checks."""
    logger = logging.getLogger(__name__)
    
    # Create reviewer with default configuration
    reviewer = create_agent_reviewer()
    
    logger.info("Running comprehensive review...")
    
    # Run review
    report = await reviewer.review(sample_code_dir, {
        "review_type": "comprehensive",
        "target": "sample_models",
        "version": "1.0.0"
    })
    
    # Display results
    logger.info(f"Review Status: {report.status}")
    logger.info(f"Total Checks: {len(report.checks)}")
    logger.info(f"Summary: {report.summary}")
    
    # Show individual check results
    for check in report.checks:
        logger.info(f"  {check.name}: {check.status}")
        logger.info(f"    Message: {check.message}")
        logger.info(f"    Execution Time: {check.execution_time:.2f}s")
    
    # Show recommendations
    if report.recommendations:
        logger.info("Recommendations:")
        for rec in report.recommendations:
            logger.info(f"  - {rec}")
    
    # Save report
    output_path = Path(sample_code_dir) / "comprehensive_review_report.json"
    await reviewer.save_report(report, str(output_path))
    logger.info(f"Report saved to: {output_path}")


async def example_schema_only_review(sample_code_dir: str):
    """Example: Schema-only review."""
    logger = logging.getLogger(__name__)
    
    # Create reviewer with only schema checks
    reviewer = create_agent_reviewer(
        enable_schema=True,
        enable_unit=False,
        enable_acceptance=False
    )
    
    logger.info("Running schema-only review...")
    
    # Run review
    report = await reviewer.review(sample_code_dir)
    
    # Display results
    logger.info(f"Schema Review Status: {report.status}")
    logger.info(f"Schema Checks: {len(report.checks)}")
    
    for check in report.checks:
        logger.info(f"  {check.name}: {check.status}")
        if check.details:
            logger.info(f"    Details: {check.details}")
    
    # Save report
    output_path = Path(sample_code_dir) / "schema_review_report.json"
    await reviewer.save_report(report, str(output_path))


async def example_unit_test_review(sample_code_dir: str):
    """Example: Unit test review."""
    logger = logging.getLogger(__name__)
    
    # Create reviewer with only unit test checks
    reviewer = create_agent_reviewer(
        enable_schema=False,
        enable_unit=True,
        enable_acceptance=False
    )
    
    logger.info("Running unit test review...")
    
    # Run review
    report = await reviewer.review(sample_code_dir)
    
    # Display results
    logger.info(f"Unit Test Review Status: {report.status}")
    logger.info(f"Unit Test Checks: {len(report.checks)}")
    
    for check in report.checks:
        logger.info(f"  {check.name}: {check.status}")
        if check.details:
            test_results = check.details.get("test_results", {})
            coverage_results = check.details.get("coverage_results", {})
            
            logger.info(f"    Tests: {test_results.get('passed', 0)} passed, {test_results.get('failed', 0)} failed")
            logger.info(f"    Coverage: {coverage_results.get('coverage', 0):.1f}%")
    
    # Save report
    output_path = Path(sample_code_dir) / "unit_test_review_report.json"
    await reviewer.save_report(report, str(output_path))


async def example_acceptance_review(sample_code_dir: str):
    """Example: Acceptance criteria review."""
    logger = logging.getLogger(__name__)
    
    # Create reviewer with only acceptance criteria checks
    reviewer = create_agent_reviewer(
        enable_schema=False,
        enable_unit=False,
        enable_acceptance=True
    )
    
    logger.info("Running acceptance criteria review...")
    
    # Run review
    report = await reviewer.review(sample_code_dir)
    
    # Display results
    logger.info(f"Acceptance Review Status: {report.status}")
    logger.info(f"Acceptance Checks: {len(report.checks)}")
    
    for check in report.checks:
        logger.info(f"  {check.name}: {check.status}")
        if check.details:
            criteria_results = check.details.get("criteria", [])
            logger.info(f"    Criteria Found: {len(criteria_results)}")
            
            for criterion_result in criteria_results[:3]:  # Show first 3
                if "result" in criterion_result:
                    result = criterion_result["result"]
                    logger.info(f"      - {result.get('description', 'Unknown')}: {'✓' if result.get('passed') else '✗'}")
    
    # Save report
    output_path = Path(sample_code_dir) / "acceptance_review_report.json"
    await reviewer.save_report(report, str(output_path))


async def example_custom_config_review(sample_code_dir: str):
    """Example: Review with custom configuration."""
    logger = logging.getLogger(__name__)
    
    # Create custom configuration
    config = create_review_config(
        schema_strict=True,
        test_coverage_threshold=90.0,  # Higher threshold
        test_timeout=600.0,  # Longer timeout
        acceptance_timeout=1200.0,
        output_format="json"
    )
    
    # Create reviewer with custom config
    reviewer = create_agent_reviewer(
        enable_schema=True,
        enable_unit=True,
        enable_acceptance=True,
        **config.dict()
    )
    
    logger.info("Running review with custom configuration...")
    logger.info(f"Test Coverage Threshold: {config.test_coverage_threshold}%")
    logger.info(f"Test Timeout: {config.test_timeout}s")
    
    # Run review
    report = await reviewer.review(sample_code_dir)
    
    # Display results
    logger.info(f"Custom Config Review Status: {report.status}")
    
    # Check if coverage threshold was met
    for check in report.checks:
        if check.check_type == CheckType.UNIT and check.details:
            coverage_results = check.details.get("coverage_results", {})
            coverage = coverage_results.get("coverage", 0)
            
            if coverage >= config.test_coverage_threshold:
                logger.info(f"✓ Coverage threshold met: {coverage:.1f}% >= {config.test_coverage_threshold}%")
            else:
                logger.info(f"✗ Coverage threshold not met: {coverage:.1f}% < {config.test_coverage_threshold}%")
    
    # Save report
    output_path = Path(sample_code_dir) / "custom_config_review_report.json"
    await reviewer.save_report(report, str(output_path))


async def example_report_analysis(sample_code_dir: str):
    """Example: Analyze review reports."""
    logger = logging.getLogger(__name__)
    
    logger.info("Analyzing review reports...")
    
    # Load and analyze reports
    report_files = [
        "comprehensive_review_report.json",
        "schema_review_report.json", 
        "unit_test_review_report.json",
        "acceptance_review_report.json",
        "custom_config_review_report.json"
    ]
    
    reports = []
    for report_file in report_files:
        report_path = Path(sample_code_dir) / report_file
        if report_path.exists():
            with open(report_path, 'r') as f:
                report_data = json.load(f)
                reports.append(report_data)
    
    # Analyze reports
    logger.info(f"Found {len(reports)} review reports")
    
    # Compare different review types
    comprehensive_report = next((r for r in reports if r.get("review_type") == "comprehensive"), None)
    if comprehensive_report:
        logger.info("Comprehensive Review Analysis:")
        logger.info(f"  Overall Status: {comprehensive_report['status']}")
        logger.info(f"  Total Checks: {comprehensive_report['summary']['total']}")
        logger.info(f"  Passed: {comprehensive_report['summary']['passed']}")
        logger.info(f"  Failed: {comprehensive_report['summary']['failed']}")
        logger.info(f"  Warnings: {comprehensive_report['summary']['warning']}")
        logger.info(f"  Errors: {comprehensive_report['summary']['error']}")
        
        # Analyze check performance
        total_time = sum(check.get("execution_time", 0) for check in comprehensive_report["checks"])
        logger.info(f"  Total Execution Time: {total_time:.2f}s")
        
        # Show slowest checks
        sorted_checks = sorted(comprehensive_report["checks"], key=lambda x: x.get("execution_time", 0), reverse=True)
        logger.info("  Slowest Checks:")
        for check in sorted_checks[:3]:
            logger.info(f"    {check['name']}: {check.get('execution_time', 0):.2f}s")
    
    # Show reviewer statistics
    reviewer = create_agent_reviewer()
    stats = reviewer.get_statistics()
    logger.info("Reviewer Statistics:")
    logger.info(f"  Total Reviews: {stats['total_reviews']}")
    logger.info(f"  Success Rate: {stats['success_rate']:.1f}%")
    logger.info(f"  Enabled Checks: {', '.join(stats['enabled_checks'])}")


# ============================================================================
# Advanced Examples
# ============================================================================

async def advanced_example():
    """Advanced example with custom check implementation."""
    logger = logging.getLogger(__name__)
    
    from src.core.runtime.reviewer import ReviewCheckBase, ReviewCheck, CheckType, ReviewStatus
    
    class CustomSecurityCheck(ReviewCheckBase):
        """Custom security check implementation."""
        
        def get_check_name(self) -> str:
            return "Security Check"
        
        def get_check_description(self) -> str:
            return "Custom security validation check"
        
        async def check(self, target_path: str, context: Dict[str, Any]) -> ReviewCheck:
            """Perform custom security check."""
            import time
            start_time = time.time()
            
            try:
                check = ReviewCheck(
                    check_type=CheckType.SCHEMA,  # Using schema type for custom check
                    name=self.get_check_name(),
                    description=self.get_check_description(),
                    status=ReviewStatus.IN_PROGRESS
                )
                
                # Custom security checks
                security_issues = []
                
                # Check for hardcoded secrets
                path = Path(target_path)
                for py_file in path.rglob('*.py'):
                    try:
                        with open(py_file, 'r') as f:
                            content = f.read()
                            
                        # Simple secret detection
                        secret_patterns = ['password=', 'secret=', 'api_key=', 'token=']
                        for pattern in secret_patterns:
                            if pattern in content.lower():
                                security_issues.append({
                                    "file": str(py_file),
                                    "issue": f"Potential hardcoded secret: {pattern}",
                                    "severity": "high"
                                })
                    except Exception:
                        continue
                
                # Determine status
                if not security_issues:
                    check.status = ReviewStatus.PASSED
                    check.message = "No security issues found"
                else:
                    check.status = ReviewStatus.WARNING
                    check.message = f"Found {len(security_issues)} potential security issues"
                
                check.details = {
                    "files_checked": len(list(path.rglob('*.py'))),
                    "issues_found": len(security_issues),
                    "issues": security_issues
                }
                
                check.execution_time = time.time() - start_time
                return check
                
            except Exception as e:
                check = ReviewCheck(
                    check_type=CheckType.SCHEMA,
                    name=self.get_check_name(),
                    description=self.get_check_description(),
                    status=ReviewStatus.ERROR,
                    message=f"Security check failed: {str(e)}",
                    execution_time=time.time() - start_time
                )
                return check
    
    # Create reviewer with custom check
    reviewer = create_agent_reviewer()
    reviewer.checkers.append(CustomSecurityCheck(reviewer.config))
    
    # Run review with custom check
    logger.info("Running review with custom security check...")
    report = await reviewer.review("/path/to/code")
    
    logger.info(f"Review with custom check: {report.status}")
    for check in report.checks:
        if check.name == "Security Check":
            logger.info(f"  Security Check: {check.status}")
            logger.info(f"    Message: {check.message}")
            if check.details:
                logger.info(f"    Issues Found: {check.details.get('issues_found', 0)}")


# ============================================================================
# Performance Benchmark
# ============================================================================

async def performance_benchmark():
    """Performance benchmark for the reviewer."""
    logger = logging.getLogger(__name__)
    
    import time
    
    # Create test scenarios
    scenarios = [
        {
            "name": "Small Codebase",
            "files": 5,
            "tests": 10,
            "criteria": 5
        },
        {
            "name": "Medium Codebase", 
            "files": 20,
            "tests": 50,
            "criteria": 20
        },
        {
            "name": "Large Codebase",
            "files": 100,
            "tests": 200,
            "criteria": 50
        }
    ]
    
    logger.info("Running Performance Benchmark...")
    
    for scenario in scenarios:
        logger.info(f"Scenario: {scenario['name']}")
        
        # Create test codebase
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create files
            for i in range(scenario["files"]):
                file_path = temp_path / f"module_{i}.py"
                with open(file_path, 'w') as f:
                    f.write(f'''
from pydantic import BaseModel, Field

class Module{i}(BaseModel):
    name: str = Field(..., description="Module name")
    value: int = Field(..., description="Module value")
''')
            
            # Create tests
            test_dir = temp_path / "tests"
            test_dir.mkdir()
            
            for i in range(scenario["tests"]):
                test_file = test_dir / f"test_module_{i}.py"
                with open(test_file, 'w') as f:
                    f.write(f'''
import pytest
from module_{i} import Module{i}

def test_module_{i}():
    module = Module{i}(name="test", value=42)
    assert module.name == "test"
    assert module.value == 42
''')
            
            # Create acceptance criteria
            criteria_file = temp_path / "acceptance_criteria.md"
            with open(criteria_file, 'w') as f:
                f.write("# Acceptance Criteria\n\n")
                for i in range(scenario["criteria"]):
                    f.write(f"- Requirement {i+1}: The system should handle requirement {i+1}\n")
            
            # Benchmark review
            reviewer = create_agent_reviewer()
            
            start_time = time.time()
            report = await reviewer.review(str(temp_path))
            end_time = time.time()
            
            review_time = end_time - start_time
            
            logger.info(f"  Files: {scenario['files']}")
            logger.info(f"  Tests: {scenario['tests']}")
            logger.info(f"  Criteria: {scenario['criteria']}")
            logger.info(f"  Review Time: {review_time:.2f}s")
            logger.info(f"  Status: {report.status}")
            logger.info(f"  Checks: {len(report.checks)}")


# ============================================================================
# Main execution
# ============================================================================

if __name__ == "__main__":
    # Run the main example
    asyncio.run(main())
    
    # Uncomment to run advanced examples
    # asyncio.run(advanced_example())
    # asyncio.run(performance_benchmark())
