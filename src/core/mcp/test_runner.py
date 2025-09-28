"""
MCP Test Runner for Agentic LLM Core v0.1

This module provides comprehensive testing capabilities for MCP tools and servers.

Created: 2024-09-24
Status: Draft
"""

from __future__ import annotations

import asyncio
import json
import logging
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from uuid import uuid4

import aiohttp
import jsonschema
from pydantic import BaseModel, Field

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


# ============================================================================
# Data Models
# ============================================================================

class TestStatus(str, Enum):
    """Test execution status."""
    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    ERROR = "error"
    SKIPPED = "skipped"


class TestResult(BaseModel):
    """Test execution result."""
    test_id: str = Field(default_factory=lambda: str(uuid4()), description="Unique test identifier")
    test_name: str = Field(..., description="Test name")
    status: TestStatus = Field(default=TestStatus.PENDING, description="Test status")
    start_time: Optional[datetime] = Field(None, description="Test start time")
    end_time: Optional[datetime] = Field(None, description="Test end time")
    duration_ms: Optional[float] = Field(None, description="Test duration in milliseconds")
    input_data: Dict[str, Any] = Field(default_factory=dict, description="Test input data")
    output_data: Optional[Dict[str, Any]] = Field(None, description="Test output data")
    error_message: Optional[str] = Field(None, description="Error message if test failed")
    validation_results: Dict[str, Any] = Field(default_factory=dict, description="Validation results")
    retry_count: int = Field(default=0, description="Number of retries attempted")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional test metadata")


class TestConfig(BaseModel):
    """Test configuration."""
    timeout: float = Field(default=30.0, description="Test timeout in seconds")
    retries: int = Field(default=3, description="Number of retries on failure")
    validate_schema: bool = Field(default=True, description="Enable schema validation")
    validate_response: bool = Field(default=True, description="Enable response validation")
    mock_mode: bool = Field(default=False, description="Run in mock mode")
    verbose: bool = Field(default=False, description="Verbose output")


class SupabaseTestInput(BaseModel):
    """Supabase test input data."""
    method: str = Field(..., description="HTTP method")
    endpoint: str = Field(..., description="API endpoint")
    headers: Dict[str, str] = Field(default_factory=dict, description="HTTP headers")
    params: Dict[str, Any] = Field(default_factory=dict, description="Query parameters")
    body: Optional[Dict[str, Any]] = Field(None, description="Request body")
    timeout: int = Field(default=30, description="Request timeout")


class SupabaseTestResponse(BaseModel):
    """Supabase test response."""
    status: str = Field(..., description="Response status")
    data: List[Dict[str, Any]] = Field(default_factory=list, description="Response data")
    message: Optional[str] = Field(None, description="Response message")
    status_code: int = Field(..., description="HTTP status code")
    headers: Dict[str, str] = Field(default_factory=dict, description="Response headers")


# ============================================================================
# Schema Validator
# ============================================================================

class SchemaValidator:
    """JSON Schema validator for test responses."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def validate_response(self, response_data: Dict[str, Any], schema: Dict[str, Any]) -> Dict[str, Any]:
        """Validate response data against schema."""
        try:
            jsonschema.validate(response_data, schema)
            return {
                "valid": True,
                "errors": [],
                "message": "Schema validation passed"
            }
        except jsonschema.ValidationError as e:
            return {
                "valid": False,
                "errors": [str(e)],
                "message": f"Schema validation failed: {e.message}"
            }
        except Exception as e:
            return {
                "valid": False,
                "errors": [str(e)],
                "message": f"Schema validation error: {str(e)}"
            }
    
    def validate_input(self, input_data: Dict[str, Any], schema: Dict[str, Any]) -> Dict[str, Any]:
        """Validate input data against schema."""
        return self.validate_response(input_data, schema)


# ============================================================================
# Supabase REST Test Runner
# ============================================================================

class SupabaseRestTestRunner:
    """Test runner for Supabase REST API."""
    
    def __init__(self, config: TestConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.schema_validator = SchemaValidator()
    
    async def run_test(self, test_input: SupabaseTestInput, expected_schema: Optional[Dict[str, Any]] = None, input_schema: Optional[Dict[str, Any]] = None) -> TestResult:
        """Run a Supabase REST test."""
        test_result = TestResult(
            test_name="supabase-rest:postgrestRequest",
            input_data=test_input.model_dump()
        )
        
        try:
            test_result.start_time = datetime.now(timezone.utc)
            self.logger.info(f"Starting test: {test_result.test_name}")
            
            # Validate input if schema provided
            if input_schema and self.config.validate_schema:
                input_validation = self.schema_validator.validate_input(
                    test_input.model_dump(), 
                    input_schema
                )
                test_result.validation_results["input_validation"] = input_validation
                
                if not input_validation["valid"]:
                    test_result.status = TestStatus.FAILED
                    test_result.error_message = f"Input validation failed: {input_validation['message']}"
                    return test_result
            
            # Execute test
            if self.config.mock_mode:
                output_data = await self._mock_request(test_input)
            else:
                output_data = await self._execute_request(test_input)
            
            test_result.output_data = output_data
            
            # Validate response if schema provided
            if expected_schema and self.config.validate_response:
                response_validation = self.schema_validator.validate_response(
                    output_data, 
                    expected_schema
                )
                test_result.validation_results["response_validation"] = response_validation
                
                if not response_validation["valid"]:
                    test_result.status = TestStatus.FAILED
                    test_result.error_message = f"Response validation failed: {response_validation['message']}"
                    return test_result
            
            # Check response status
            if output_data.get("status_code", 0) >= 200 and output_data.get("status_code", 0) < 300:
                test_result.status = TestStatus.PASSED
                test_result.metadata["message"] = "Test passed successfully"
            else:
                test_result.status = TestStatus.FAILED
                test_result.error_message = f"HTTP error: {output_data.get('status_code', 'unknown')}"
            
        except Exception as e:
            test_result.status = TestStatus.ERROR
            test_result.error_message = str(e)
            self.logger.error(f"Test execution error: {e}")
        
        finally:
            test_result.end_time = datetime.now(timezone.utc)
            if test_result.start_time:
                duration = (test_result.end_time - test_result.start_time).total_seconds() * 1000
                test_result.duration_ms = duration
        
        return test_result
    
    async def _execute_request(self, test_input: SupabaseTestInput) -> Dict[str, Any]:
        """Execute actual HTTP request."""
        try:
            async with aiohttp.ClientSession() as session:
                # Prepare request
                url = f"https://test-project.supabase.co{test_input.endpoint}"
                
                # Add query parameters
                params = test_input.params if test_input.params else {}
                
                # Make request
                async with session.request(
                    method=test_input.method,
                    url=url,
                    headers=test_input.headers,
                    params=params,
                    json=test_input.body,
                    timeout=aiohttp.ClientTimeout(total=test_input.timeout)
                ) as response:
                    # Parse response
                    response_data = await response.json() if response.content_type == 'application/json' else {}
                    
                    return {
                        "status": "success" if response.status < 400 else "error",
                        "data": response_data,
                        "message": f"Request completed with status {response.status}",
                        "status_code": response.status,
                        "headers": dict(response.headers)
                    }
                    
        except aiohttp.ClientError as e:
            return {
                "status": "error",
                "data": [],
                "message": f"Client error: {str(e)}",
                "status_code": 0,
                "headers": {}
            }
        except Exception as e:
            return {
                "status": "error",
                "data": [],
                "message": f"Request error: {str(e)}",
                "status_code": 0,
                "headers": {}
            }
    
    async def _mock_request(self, test_input: SupabaseTestInput) -> Dict[str, Any]:
        """Execute mock request for testing."""
        # Simulate network delay
        await asyncio.sleep(0.1)
        
        # Return mock response based on endpoint
        if test_input.endpoint == "/rest/v1/":
            return {
                "status": "success",
                "data": [
                    {
                        "table_name": "users",
                        "table_schema": "public",
                        "table_type": "BASE TABLE"
                    },
                    {
                        "table_name": "posts",
                        "table_schema": "public",
                        "table_type": "BASE TABLE"
                    },
                    {
                        "table_name": "comments",
                        "table_schema": "public",
                        "table_type": "BASE TABLE"
                    }
                ],
                "message": "Tables retrieved successfully",
                "status_code": 200,
                "headers": {
                    "Content-Type": "application/json",
                    "X-Total-Count": "3"
                }
            }
        else:
            return {
                "status": "error",
                "data": [],
                "message": f"Mock endpoint not found: {test_input.endpoint}",
                "status_code": 404,
                "headers": {}
            }


# ============================================================================
# MCP Test Manager
# ============================================================================

class MCPTestManager:
    """Manages MCP tool tests."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.test_runners = {
            "supabase-rest": SupabaseRestTestRunner
        }
    
    def load_test_config(self, config_path: Union[str, Path]) -> Dict[str, Any]:
        """Load test configuration from file."""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            self.logger.info(f"Loaded test configuration from {config_path}")
            return config_data
            
        except FileNotFoundError:
            raise FileNotFoundError(f"Test configuration file not found: {config_path}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in test configuration: {e}")
        except Exception as e:
            raise RuntimeError(f"Failed to load test configuration: {e}")
    
    async def run_test_from_config(self, config_path: Union[str, Path], mock_mode: bool = False) -> TestResult:
        """Run test from configuration file."""
        config_data = self.load_test_config(config_path)
        
        # Extract test information
        test_name = config_data.get("test_name", "unknown")
        server_type = config_data.get("server_type", "unknown")
        config_data.get("tool_name", "unknown")
        input_data = config_data.get("input_data", {})
        expected_response = config_data.get("expected_response", {})
        test_config_data = config_data.get("test_config", {})
        
        # Create test configuration
        test_config_data["mock_mode"] = mock_mode
        test_config = TestConfig(**test_config_data)
        
        # Get schemas
        input_schema = config_data.get("input_schema")
        expected_schema = expected_response.get("schema") if expected_response else None
        
        # Create appropriate test runner
        if server_type not in self.test_runners:
            raise ValueError(f"Unsupported server type: {server_type}")
        
        runner_class = self.test_runners[server_type]
        runner = runner_class(test_config)
        
        # Create test input
        if server_type == "supabase-rest":
            test_input = SupabaseTestInput(**input_data)
        else:
            raise ValueError(f"Unsupported server type for test input: {server_type}")
        
        # Run test
        self.logger.info(f"Running test: {test_name}")
        result = await runner.run_test(test_input, expected_schema, input_schema)
        
        return result
    
    def print_test_result(self, result: TestResult):
        """Print test result in formatted way."""
        status_emoji = {
            TestStatus.PASSED: "✅",
            TestStatus.FAILED: "❌",
            TestStatus.ERROR: "💥",
            TestStatus.SKIPPED: "⏭️",
            TestStatus.PENDING: "⏳",
            TestStatus.RUNNING: "🔄"
        }.get(result.status, "❓")
        
        print("\n" + "="*80)
        print("MCP TEST RESULT")
        print("="*80)
        
        print(f"\n{status_emoji} Test: {result.test_name}")
        print(f"   Status: {result.status.value}")
        print(f"   Duration: {result.duration_ms:.2f}ms" if result.duration_ms else "   Duration: N/A")
        print(f"   Retries: {result.retry_count}")
        
        if result.error_message:
            print(f"   Error: {result.error_message}")
        
        # Print validation results
        if result.validation_results:
            print("\n🔍 Validation Results:")
            for validation_type, validation_result in result.validation_results.items():
                validation_emoji = "✅" if validation_result.get("valid", False) else "❌"
                print(f"   {validation_emoji} {validation_type}: {validation_result.get('message', 'N/A')}")
                if not validation_result.get("valid", True) and validation_result.get("errors"):
                    for error in validation_result["errors"]:
                        print(f"      - {error}")
        
        # Print input data summary
        if result.input_data:
            print("\n📥 Input Data:")
            for key, value in result.input_data.items():
                if isinstance(value, dict) and len(str(value)) > 100:
                    print(f"   {key}: {type(value).__name__} ({len(value)} items)")
                else:
                    print(f"   {key}: {value}")
        
        # Print output data summary
        if result.output_data:
            print("\n📤 Output Data:")
            for key, value in result.output_data.items():
                if isinstance(value, (list, dict)) and len(str(value)) > 100:
                    print(f"   {key}: {type(value).__name__} ({len(value)} items)")
                else:
                    print(f"   {key}: {value}")
        
        print()


# ============================================================================
# Main Function
# ============================================================================

async def main():
    """Main function for command-line usage."""
    import argparse
    
    parser = argparse.ArgumentParser(description="MCP Test Runner")
    parser.add_argument("--name", required=True, help="Test name (server:tool)")
    parser.add_argument("--sample-input", required=True, help="Path to sample input JSON file")
    parser.add_argument("--expect-schema", action="store_true", help="Expect schema validation")
    parser.add_argument("--mock", action="store_true", help="Run in mock mode")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    try:
        # Create test manager
        manager = MCPTestManager()
        
        # Run test
        result = await manager.run_test_from_config(args.sample_input, mock_mode=args.mock)
        
        # Print results
        manager.print_test_result(result)
        
        # Exit with appropriate code
        if result.status == TestStatus.PASSED:
            print("🎉 Test completed successfully!")
            return 0
        else:
            print("💥 Test failed!")
            return 1
            
    except Exception as e:
        logger.error(f"Test execution failed: {e}")
        return 1


if __name__ == "__main__":
    exit(asyncio.run(main()))
