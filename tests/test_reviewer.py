"""
Tests for Agent Reviewer

Comprehensive test suite for the agent reviewer including:
- Schema validation checks
- Unit test execution and coverage
- Acceptance criteria validation
- Review report generation
- Error handling and edge cases

Created: 2024-09-24
Status: Draft
"""

import asyncio
import json
import pytest
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import Mock, AsyncMock, patch, mock_open
from typing import Dict, Any, List

from src.core.runtime.reviewer import (
    # Enums
    ReviewStatus,
    CheckType,
    
    # Models
    ReviewCheck,
    ReviewReport,
    ReviewConfig,
    
    # Check implementations
    ReviewCheckBase,
    SchemaValidator,
    UnitTestRunner,
    AcceptanceCriteriaValidator,
    
    # Main reviewer
    AgentReviewer,
    
    # Factory functions
    create_agent_reviewer,
    create_review_config,
)


# ============================================================================
# Test Fixtures
# ============================================================================

@pytest.fixture
def sample_review_config():
    """Sample review configuration for testing."""
    return ReviewConfig(
        enable_schema_checks=True,
        enable_unit_checks=True,
        enable_acceptance_checks=True,
        schema_strict_mode=True,
        test_coverage_threshold=80.0,
        test_timeout=300.0,
        acceptance_timeout=600.0,
        output_format="json"
    )


@pytest.fixture
def sample_review_check():
    """Sample review check for testing."""
    return ReviewCheck(
        check_type=CheckType.SCHEMA,
        name="Test Schema Check",
        description="Test schema validation",
        status=ReviewStatus.PASSED,
        message="Schema validation passed",
        details={"files_checked": 5, "issues_found": 0},
        execution_time=1.5,
        timestamp=datetime.now(timezone.utc)
    )


@pytest.fixture
def sample_review_report():
    """Sample review report for testing."""
    checks = [
        ReviewCheck(
            check_type=CheckType.SCHEMA,
            name="Schema Validation",
            description="Validates Pydantic schemas",
            status=ReviewStatus.PASSED,
            message="All schemas valid",
            execution_time=1.0
        ),
        ReviewCheck(
            check_type=CheckType.UNIT,
            name="Unit Tests",
            description="Runs unit tests",
            status=ReviewStatus.PASSED,
            message="All tests passed",
            execution_time=2.0
        ),
        ReviewCheck(
            check_type=CheckType.ACCEPTANCE,
            name="Acceptance Criteria",
            description="Validates acceptance criteria",
            status=ReviewStatus.PASSED,
            message="All criteria met",
            execution_time=0.5
        )
    ]
    
    return ReviewReport(
        target_path="/test/path",
        review_type="comprehensive",
        status=ReviewStatus.PASSED,
        checks=checks,
        summary={"total": 3, "passed": 3, "failed": 0, "warning": 0, "error": 0},
        recommendations=["All checks passed!"],
        created_at=datetime.now(timezone.utc),
        completed_at=datetime.now(timezone.utc)
    )


@pytest.fixture
def temp_directory():
    """Create a temporary directory for testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir


@pytest.fixture
def sample_python_file(temp_directory):
    """Create a sample Python file for testing."""
    python_content = '''
from pydantic import BaseModel, Field
from typing import Optional

class TestModel(BaseModel):
    name: str = Field(..., description="Name field")
    age: Optional[int] = Field(None, description="Age field")
    
    @validator('age')
    def validate_age(cls, v):
        if v is not None and v < 0:
            raise ValueError("Age cannot be negative")
        return v
'''
    
    file_path = Path(temp_directory) / "test_model.py"
    with open(file_path, 'w') as f:
        f.write(python_content)
    
    return str(file_path)


@pytest.fixture
def sample_test_file(temp_directory):
    """Create a sample test file for testing."""
    test_content = '''
import pytest
from test_model import TestModel

def test_model_creation():
    model = TestModel(name="test", age=25)
    assert model.name == "test"
    assert model.age == 25

def test_model_validation():
    with pytest.raises(ValueError):
        TestModel(name="test", age=-1)
'''
    
    file_path = Path(temp_directory) / "test_test_model.py"
    with open(file_path, 'w') as f:
        f.write(test_content)
    
    return str(file_path)


@pytest.fixture
def sample_acceptance_file(temp_directory):
    """Create a sample acceptance criteria file for testing."""
    criteria_content = '''
# Acceptance Criteria

## Functional Requirements

- The system should support user authentication
- The system must handle file uploads up to 10MB
- The system will provide real-time notifications
- The system can process multiple file formats

## Non-Functional Requirements

- Response time should be under 200ms
- System must support 1000 concurrent users
- Uptime must be 99.9% or higher
'''
    
    file_path = Path(temp_directory) / "acceptance_criteria.md"
    with open(file_path, 'w') as f:
        f.write(criteria_content)
    
    return str(file_path)


# ============================================================================
# Model Tests
# ============================================================================

class TestReviewStatus:
    """Test ReviewStatus enum."""
    
    def test_review_status_values(self):
        """Test review status enum values."""
        assert ReviewStatus.PENDING == "pending"
        assert ReviewStatus.IN_PROGRESS == "in_progress"
        assert ReviewStatus.PASSED == "passed"
        assert ReviewStatus.FAILED == "failed"
        assert ReviewStatus.WARNING == "warning"
        assert ReviewStatus.ERROR == "error"


class TestCheckType:
    """Test CheckType enum."""
    
    def test_check_type_values(self):
        """Test check type enum values."""
        assert CheckType.SCHEMA == "schema"
        assert CheckType.UNIT == "unit"
        assert CheckType.ACCEPTANCE == "acceptance"


class TestReviewCheck:
    """Test ReviewCheck model."""
    
    def test_review_check_creation(self, sample_review_check):
        """Test review check creation."""
        assert sample_review_check.check_type == CheckType.SCHEMA
        assert sample_review_check.name == "Test Schema Check"
        assert sample_review_check.description == "Test schema validation"
        assert sample_review_check.status == ReviewStatus.PASSED
        assert sample_review_check.message == "Schema validation passed"
        assert sample_review_check.execution_time == 1.5
        assert sample_review_check.check_id is not None
        assert sample_review_check.timestamp is not None
    
    def test_review_check_defaults(self):
        """Test review check defaults."""
        check = ReviewCheck(
            check_type=CheckType.UNIT,
            name="Test Check",
            description="Test description"
        )
        
        assert check.status == ReviewStatus.PENDING
        assert check.message is None
        assert check.details == {}
        assert check.execution_time is None
        assert check.check_id is not None
        assert check.timestamp is not None
    
    def test_review_check_validation(self):
        """Test review check validation."""
        # Valid check
        valid_check = ReviewCheck(
            check_type=CheckType.SCHEMA,
            name="Test",
            description="Test",
            execution_time=1.0
        )
        assert valid_check.execution_time == 1.0
        
        # Invalid execution time
        with pytest.raises(ValueError):
            ReviewCheck(
                check_type=CheckType.SCHEMA,
                name="Test",
                description="Test",
                execution_time=-1.0
            )


class TestReviewReport:
    """Test ReviewReport model."""
    
    def test_review_report_creation(self, sample_review_report):
        """Test review report creation."""
        assert sample_review_report.target_path == "/test/path"
        assert sample_review_report.review_type == "comprehensive"
        assert sample_review_report.status == ReviewStatus.PASSED
        assert len(sample_review_report.checks) == 3
        assert sample_review_report.report_id is not None
        assert sample_review_report.created_at is not None
        assert sample_review_report.completed_at is not None
    
    def test_review_report_defaults(self):
        """Test review report defaults."""
        report = ReviewReport(target_path="/test")
        
        assert report.review_type == "comprehensive"
        assert report.status == ReviewStatus.PENDING
        assert report.checks == []
        assert report.summary == {}
        assert report.recommendations == []
        assert report.created_at is not None
        assert report.completed_at is None
        assert report.metadata == {}
    
    def test_get_overall_status(self):
        """Test overall status calculation."""
        # All passed
        report = ReviewReport(
            target_path="/test",
            checks=[
                ReviewCheck(check_type=CheckType.SCHEMA, name="Test", description="Test", status=ReviewStatus.PASSED),
                ReviewCheck(check_type=CheckType.UNIT, name="Test", description="Test", status=ReviewStatus.PASSED)
            ]
        )
        assert report.get_overall_status() == ReviewStatus.PASSED
        
        # Has error
        report.checks.append(ReviewCheck(check_type=CheckType.ACCEPTANCE, name="Test", description="Test", status=ReviewStatus.ERROR))
        assert report.get_overall_status() == ReviewStatus.ERROR
        
        # Has failed
        report.checks = [ReviewCheck(check_type=CheckType.SCHEMA, name="Test", description="Test", status=ReviewStatus.FAILED)]
        assert report.get_overall_status() == ReviewStatus.FAILED
        
        # Has warning
        report.checks = [ReviewCheck(check_type=CheckType.SCHEMA, name="Test", description="Test", status=ReviewStatus.WARNING)]
        assert report.get_overall_status() == ReviewStatus.WARNING
    
    def test_get_summary_stats(self):
        """Test summary statistics calculation."""
        report = ReviewReport(
            target_path="/test",
            checks=[
                ReviewCheck(check_type=CheckType.SCHEMA, name="Test", description="Test", status=ReviewStatus.PASSED),
                ReviewCheck(check_type=CheckType.UNIT, name="Test", description="Test", status=ReviewStatus.FAILED),
                ReviewCheck(check_type=CheckType.ACCEPTANCE, name="Test", description="Test", status=ReviewStatus.WARNING)
            ]
        )
        
        stats = report.get_summary_stats()
        assert stats["total"] == 3
        assert stats["passed"] == 1
        assert stats["failed"] == 1
        assert stats["warning"] == 1
        assert stats["error"] == 0


class TestReviewConfig:
    """Test ReviewConfig model."""
    
    def test_review_config_creation(self, sample_review_config):
        """Test review config creation."""
        assert sample_review_config.enable_schema_checks is True
        assert sample_review_config.enable_unit_checks is True
        assert sample_review_config.enable_acceptance_checks is True
        assert sample_review_config.schema_strict_mode is True
        assert sample_review_config.test_coverage_threshold == 80.0
        assert sample_review_config.test_timeout == 300.0
        assert sample_review_config.output_format == "json"
    
    def test_review_config_defaults(self):
        """Test review config defaults."""
        config = ReviewConfig()
        
        assert config.enable_schema_checks is True
        assert config.enable_unit_checks is True
        assert config.enable_acceptance_checks is True
        assert config.schema_strict_mode is True
        assert config.schema_ignore_unknown is False
        assert config.test_framework == "pytest"
        assert config.test_timeout == 300.0
        assert config.test_coverage_threshold == 80.0
        assert config.acceptance_timeout == 600.0
        assert config.acceptance_retries == 3
        assert config.output_format == "json"
        assert config.include_details is True
        assert config.include_recommendations is True
    
    def test_review_config_validation(self):
        """Test review config validation."""
        # Valid config
        valid_config = ReviewConfig(
            test_coverage_threshold=90.0,
            test_timeout=600.0,
            acceptance_timeout=1200.0,
            acceptance_retries=5
        )
        assert valid_config.test_coverage_threshold == 90.0
        
        # Invalid coverage threshold
        with pytest.raises(ValueError):
            ReviewConfig(test_coverage_threshold=150.0)
        
        # Invalid timeout
        with pytest.raises(ValueError):
            ReviewConfig(test_timeout=0.5)


# ============================================================================
# Check Implementation Tests
# ============================================================================

class TestSchemaValidator:
    """Test SchemaValidator."""
    
    @pytest.fixture
    def schema_validator(self, sample_review_config):
        """Create schema validator."""
        return SchemaValidator(sample_review_config)
    
    def test_get_check_name(self, schema_validator):
        """Test check name."""
        assert schema_validator.get_check_name() == "Schema Validation"
    
    def test_get_check_description(self, schema_validator):
        """Test check description."""
        assert schema_validator.get_check_description() == "Validates Pydantic schemas and data contracts"
    
    def test_find_python_files(self, schema_validator, sample_python_file):
        """Test finding Python files."""
        # Test with file
        files = schema_validator._find_python_files(sample_python_file)
        assert len(files) == 1
        assert files[0] == sample_python_file
        
        # Test with directory
        directory = str(Path(sample_python_file).parent)
        files = schema_validator._find_python_files(directory)
        assert len(files) == 1
        assert files[0] == sample_python_file
    
    @pytest.mark.asyncio
    async def test_validate_file_schemas(self, schema_validator, sample_python_file):
        """Test file schema validation."""
        issues = await schema_validator._validate_file_schemas(sample_python_file)
        
        # Should find some issues or pass validation
        assert isinstance(issues, list)
        # The specific issues depend on the file content
    
    @pytest.mark.asyncio
    async def test_check_success(self, schema_validator, sample_python_file):
        """Test successful schema check."""
        check = await schema_validator.check(sample_python_file, {})
        
        assert isinstance(check, ReviewCheck)
        assert check.check_type == CheckType.SCHEMA
        assert check.name == "Schema Validation"
        assert check.status in [ReviewStatus.PASSED, ReviewStatus.FAILED, ReviewStatus.WARNING]
        assert check.execution_time is not None
        assert check.timestamp is not None
    
    @pytest.mark.asyncio
    async def test_check_error(self, schema_validator):
        """Test schema check error handling."""
        # Test with non-existent file
        check = await schema_validator.check("/non/existent/file.py", {})
        
        assert isinstance(check, ReviewCheck)
        assert check.status == ReviewStatus.ERROR
        assert "error" in check.message.lower()


class TestUnitTestRunner:
    """Test UnitTestRunner."""
    
    @pytest.fixture
    def unit_test_runner(self, sample_review_config):
        """Create unit test runner."""
        return UnitTestRunner(sample_review_config)
    
    def test_get_check_name(self, unit_test_runner):
        """Test check name."""
        assert unit_test_runner.get_check_name() == "Unit Tests"
    
    def test_get_check_description(self, unit_test_runner):
        """Test check description."""
        assert unit_test_runner.get_check_description() == "Runs unit tests and checks coverage"
    
    def test_find_test_files(self, unit_test_runner, sample_test_file):
        """Test finding test files."""
        # Test with file
        files = unit_test_runner._find_test_files(sample_test_file)
        assert len(files) == 1
        assert files[0] == sample_test_file
        
        # Test with directory
        directory = str(Path(sample_test_file).parent)
        files = unit_test_runner._find_test_files(directory)
        assert len(files) == 1
        assert files[0] == sample_test_file
    
    @pytest.mark.asyncio
    async def test_run_tests(self, unit_test_runner, sample_test_file):
        """Test running tests."""
        with patch('asyncio.create_subprocess_exec') as mock_subprocess:
            # Mock successful test run
            mock_process = AsyncMock()
            mock_process.communicate.return_value = (b"test passed", b"")
            mock_process.returncode = 0
            mock_subprocess.return_value = mock_process
            
            result = await unit_test_runner._run_tests([sample_test_file])
            
            assert isinstance(result, dict)
            assert "passed" in result
            assert "failed" in result
            assert "total" in result
    
    @pytest.mark.asyncio
    async def test_check_coverage(self, unit_test_runner, sample_test_file):
        """Test coverage checking."""
        with patch('asyncio.create_subprocess_exec') as mock_subprocess:
            # Mock coverage run
            mock_process = AsyncMock()
            mock_process.communicate.return_value = (b"", b"")
            mock_subprocess.return_value = mock_process
            
            result = await unit_test_runner._check_coverage(sample_test_file)
            
            assert isinstance(result, dict)
            assert "coverage" in result
            assert "output" in result
    
    @pytest.mark.asyncio
    async def test_check_no_tests(self, unit_test_runner, temp_directory):
        """Test check with no test files."""
        check = await unit_test_runner.check(temp_directory, {})
        
        assert isinstance(check, ReviewCheck)
        assert check.status == ReviewStatus.WARNING
        assert "no test files" in check.message.lower()


class TestAcceptanceCriteriaValidator:
    """Test AcceptanceCriteriaValidator."""
    
    @pytest.fixture
    def acceptance_validator(self, sample_review_config):
        """Create acceptance criteria validator."""
        return AcceptanceCriteriaValidator(sample_review_config)
    
    def test_get_check_name(self, acceptance_validator):
        """Test check name."""
        assert acceptance_validator.get_check_name() == "Acceptance Criteria"
    
    def test_get_check_description(self, acceptance_validator):
        """Test check description."""
        assert acceptance_validator.get_check_description() == "Validates acceptance criteria and requirements"
    
    def test_find_acceptance_files(self, acceptance_validator, sample_acceptance_file):
        """Test finding acceptance files."""
        # Test with file
        files = acceptance_validator._find_acceptance_files(sample_acceptance_file)
        assert len(files) == 1
        assert files[0] == sample_acceptance_file
        
        # Test with directory
        directory = str(Path(sample_acceptance_file).parent)
        files = acceptance_validator._find_acceptance_files(directory)
        assert len(files) == 1
        assert files[0] == sample_acceptance_file
    
    @pytest.mark.asyncio
    async def test_parse_criteria_file(self, acceptance_validator, sample_acceptance_file):
        """Test parsing criteria file."""
        criteria = await acceptance_validator._parse_criteria_file(sample_acceptance_file)
        
        assert isinstance(criteria, list)
        assert len(criteria) > 0
        assert all("description" in criterion for criterion in criteria)
    
    @pytest.mark.asyncio
    async def test_validate_criterion(self, acceptance_validator):
        """Test validating individual criterion."""
        # Testable criterion
        criterion = {"description": "The system should support user authentication"}
        result = await acceptance_validator._validate_criterion(criterion, "/test")
        
        assert isinstance(result, dict)
        assert "passed" in result
        assert "is_testable" in result
        assert "has_success_criteria" in result
    
    @pytest.mark.asyncio
    async def test_check_no_criteria(self, acceptance_validator, temp_directory):
        """Test check with no criteria files."""
        check = await acceptance_validator.check(temp_directory, {})
        
        assert isinstance(check, ReviewCheck)
        assert check.status == ReviewStatus.WARNING
        assert "no acceptance criteria" in check.message.lower()


# ============================================================================
# Agent Reviewer Tests
# ============================================================================

class TestAgentReviewer:
    """Test AgentReviewer."""
    
    @pytest.fixture
    def reviewer(self, sample_review_config):
        """Create agent reviewer."""
        return AgentReviewer(sample_review_config)
    
    def test_reviewer_initialization(self, reviewer):
        """Test reviewer initialization."""
        assert len(reviewer.checkers) == 3  # All checks enabled
        assert reviewer.total_reviews == 0
        assert reviewer.successful_reviews == 0
        assert reviewer.failed_reviews == 0
    
    def test_reviewer_initialization_partial(self):
        """Test reviewer initialization with partial checks."""
        config = ReviewConfig(
            enable_schema_checks=True,
            enable_unit_checks=False,
            enable_acceptance_checks=True
        )
        reviewer = AgentReviewer(config)
        
        assert len(reviewer.checkers) == 2  # Only schema and acceptance
        assert any(isinstance(checker, SchemaValidator) for checker in reviewer.checkers)
        assert not any(isinstance(checker, UnitTestRunner) for checker in reviewer.checkers)
        assert any(isinstance(checker, AcceptanceCriteriaValidator) for checker in reviewer.checkers)
    
    @pytest.mark.asyncio
    async def test_review_success(self, reviewer, sample_python_file):
        """Test successful review."""
        report = await reviewer.review(sample_python_file, {"test": "context"})
        
        assert isinstance(report, ReviewReport)
        assert report.target_path == sample_python_file
        assert report.review_type == "comprehensive"
        assert len(report.checks) == 3  # All three checks
        assert report.status in [ReviewStatus.PASSED, ReviewStatus.FAILED, ReviewStatus.WARNING]
        assert report.completed_at is not None
        assert report.summary is not None
        assert reviewer.total_reviews == 1
    
    @pytest.mark.asyncio
    async def test_review_error(self, reviewer):
        """Test review error handling."""
        # Test with non-existent path
        report = await reviewer.review("/non/existent/path", {})
        
        assert isinstance(report, ReviewReport)
        assert report.status == ReviewStatus.ERROR
        assert reviewer.failed_reviews == 1
    
    @pytest.mark.asyncio
    async def test_generate_recommendations(self, reviewer):
        """Test recommendation generation."""
        # Create report with failed checks
        failed_check = ReviewCheck(
            check_type=CheckType.SCHEMA,
            name="Schema Check",
            description="Schema validation",
            status=ReviewStatus.FAILED
        )
        
        report = ReviewReport(
            target_path="/test",
            checks=[failed_check]
        )
        
        recommendations = await reviewer._generate_recommendations(report)
        
        assert isinstance(recommendations, list)
        assert len(recommendations) > 0
        assert any("schema" in rec.lower() for rec in recommendations)
    
    @pytest.mark.asyncio
    async def test_save_report(self, reviewer, sample_review_report, temp_directory):
        """Test saving report."""
        output_path = Path(temp_directory) / "report.json"
        
        await reviewer.save_report(sample_review_report, str(output_path))
        
        assert output_path.exists()
        
        # Verify JSON content
        with open(output_path, 'r') as f:
            data = json.load(f)
        
        assert data["target_path"] == sample_review_report.target_path
        assert data["status"] == sample_review_report.status.value
        assert len(data["checks"]) == len(sample_review_report.checks)
    
    def test_get_statistics(self, reviewer):
        """Test reviewer statistics."""
        # Update statistics
        reviewer.total_reviews = 10
        reviewer.successful_reviews = 8
        reviewer.failed_reviews = 2
        
        stats = reviewer.get_statistics()
        
        assert stats["total_reviews"] == 10
        assert stats["successful_reviews"] == 8
        assert stats["failed_reviews"] == 2
        assert stats["success_rate"] == 80.0
        assert len(stats["enabled_checks"]) == 3


# ============================================================================
# Factory Function Tests
# ============================================================================

class TestFactoryFunctions:
    """Test factory functions."""
    
    def test_create_agent_reviewer(self):
        """Test create_agent_reviewer function."""
        reviewer = create_agent_reviewer()
        
        assert isinstance(reviewer, AgentReviewer)
        assert len(reviewer.checkers) == 3  # All checks enabled by default
    
    def test_create_agent_reviewer_partial(self):
        """Test create_agent_reviewer with partial checks."""
        reviewer = create_agent_reviewer(
            enable_schema=True,
            enable_unit=False,
            enable_acceptance=True
        )
        
        assert isinstance(reviewer, AgentReviewer)
        assert len(reviewer.checkers) == 2  # Only schema and acceptance
    
    def test_create_review_config(self):
        """Test create_review_config function."""
        config = create_review_config(
            schema_strict=True,
            test_coverage_threshold=90.0,
            test_timeout=600.0
        )
        
        assert isinstance(config, ReviewConfig)
        assert config.schema_strict_mode is True
        assert config.test_coverage_threshold == 90.0
        assert config.test_timeout == 600.0


# ============================================================================
# Integration Tests
# ============================================================================

class TestReviewerIntegration:
    """Integration tests for the reviewer."""
    
    @pytest.mark.asyncio
    async def test_end_to_end_review(self, temp_directory, sample_python_file, sample_test_file, sample_acceptance_file):
        """Test end-to-end review process."""
        # Create reviewer
        reviewer = create_agent_reviewer()
        
        # Run review
        report = await reviewer.review(temp_directory, {"test": "integration"})
        
        # Verify report
        assert isinstance(report, ReviewReport)
        assert report.target_path == temp_directory
        assert len(report.checks) == 3  # All three checks
        assert report.status is not None
        assert report.completed_at is not None
        assert report.summary is not None
        assert isinstance(report.recommendations, list)
        
        # Verify individual checks
        check_types = [check.check_type for check in report.checks]
        assert CheckType.SCHEMA in check_types
        assert CheckType.UNIT in check_types
        assert CheckType.ACCEPTANCE in check_types
        
        # Save report
        output_path = Path(temp_directory) / "review_report.json"
        await reviewer.save_report(report, str(output_path))
        
        assert output_path.exists()
        
        # Verify saved report
        with open(output_path, 'r') as f:
            saved_data = json.load(f)
        
        assert saved_data["target_path"] == temp_directory
        assert len(saved_data["checks"]) == 3
    
    @pytest.mark.asyncio
    async def test_review_with_different_configs(self, temp_directory):
        """Test review with different configurations."""
        # Schema-only review
        schema_reviewer = create_agent_reviewer(
            enable_schema=True,
            enable_unit=False,
            enable_acceptance=False
        )
        
        schema_report = await schema_reviewer.review(temp_directory)
        assert len(schema_report.checks) == 1
        assert schema_report.checks[0].check_type == CheckType.SCHEMA
        
        # Unit-only review
        unit_reviewer = create_agent_reviewer(
            enable_schema=False,
            enable_unit=True,
            enable_acceptance=False
        )
        
        unit_report = await unit_reviewer.review(temp_directory)
        assert len(unit_report.checks) == 1
        assert unit_report.checks[0].check_type == CheckType.UNIT
        
        # Acceptance-only review
        acceptance_reviewer = create_agent_reviewer(
            enable_schema=False,
            enable_unit=False,
            enable_acceptance=True
        )
        
        acceptance_report = await acceptance_reviewer.review(temp_directory)
        assert len(acceptance_report.checks) == 1
        assert acceptance_report.checks[0].check_type == CheckType.ACCEPTANCE


# ============================================================================
# Performance Tests
# ============================================================================

class TestReviewerPerformance:
    """Performance tests for the reviewer."""
    
    @pytest.mark.asyncio
    async def test_review_performance(self, temp_directory):
        """Test review performance."""
        import time
        
        # Create multiple files for performance testing
        for i in range(10):
            file_path = Path(temp_directory) / f"test_file_{i}.py"
            with open(file_path, 'w') as f:
                f.write(f'''
from pydantic import BaseModel, Field

class TestModel{i}(BaseModel):
    name: str = Field(..., description="Name field")
    value: int = Field(..., description="Value field")
''')
        
        reviewer = create_agent_reviewer()
        
        # Measure review time
        start_time = time.time()
        report = await reviewer.review(temp_directory)
        end_time = time.time()
        
        review_time = end_time - start_time
        
        # Should complete within reasonable time
        assert review_time < 30.0  # Should complete within 30 seconds
        assert isinstance(report, ReviewReport)
    
    @pytest.mark.asyncio
    async def test_concurrent_reviews(self, temp_directory):
        """Test concurrent review performance."""
        # Create reviewer
        reviewer = create_agent_reviewer()
        
        # Create multiple test directories
        test_dirs = []
        for i in range(3):
            test_dir = Path(temp_directory) / f"test_dir_{i}"
            test_dir.mkdir()
            
            # Add a test file
            test_file = test_dir / "test.py"
            with open(test_file, 'w') as f:
                f.write(f'''
from pydantic import BaseModel

class TestModel{i}(BaseModel):
    name: str
''')
            
            test_dirs.append(str(test_dir))
        
        # Run concurrent reviews
        start_time = time.time()
        reports = await asyncio.gather(*[
            reviewer.review(test_dir) for test_dir in test_dirs
        ])
        end_time = time.time()
        
        total_time = end_time - start_time
        
        # All reports should be valid
        assert len(reports) == 3
        assert all(isinstance(report, ReviewReport) for report in reports)
        
        # Should complete within reasonable time
        assert total_time < 45.0  # Should complete within 45 seconds


# ============================================================================
# Error Handling Tests
# ============================================================================

class TestReviewerErrorHandling:
    """Error handling tests for the reviewer."""
    
    @pytest.mark.asyncio
    async def test_invalid_path_handling(self):
        """Test handling of invalid paths."""
        reviewer = create_agent_reviewer()
        
        # Test with non-existent path
        report = await reviewer.review("/non/existent/path")
        
        assert isinstance(report, ReviewReport)
        assert report.status == ReviewStatus.ERROR
    
    @pytest.mark.asyncio
    async def test_permission_error_handling(self, temp_directory):
        """Test handling of permission errors."""
        reviewer = create_agent_reviewer()
        
        # Create a file and remove read permission
        test_file = Path(temp_directory) / "no_read.py"
        with open(test_file, 'w') as f:
            f.write("test content")
        
        # On Unix systems, remove read permission
        if hasattr(os, 'chmod'):
            os.chmod(test_file, 0o000)
            
            try:
                report = await reviewer.review(str(test_file))
                assert isinstance(report, ReviewReport)
            finally:
                # Restore permission for cleanup
                os.chmod(test_file, 0o644)
    
    @pytest.mark.asyncio
    async def test_malformed_file_handling(self, temp_directory):
        """Test handling of malformed files."""
        reviewer = create_agent_reviewer()
        
        # Create malformed Python file
        malformed_file = Path(temp_directory) / "malformed.py"
        with open(malformed_file, 'w') as f:
            f.write("invalid python syntax {")
        
        report = await reviewer.review(str(malformed_file))
        
        assert isinstance(report, ReviewReport)
        # Should handle gracefully without crashing


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
