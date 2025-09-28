"""
Knowledge Base Code Generator for Agentic LLM Core v0.1

This module provides intelligent code generation using the knowledge base
to improve code quality, maintain consistency, and leverage existing patterns.

Created: 2024-09-24
Status: Enhanced
"""

from __future__ import annotations

import ast
import json
import logging
import re
from datetime import datetime
from typing import Any, Dict, List, Optional, Union, Tuple, Set
from uuid import uuid4

import pydantic
from pydantic import BaseModel, Field, field_validator

from ..memory.vector_pg import VectorStore, Document, DocumentType
from ..models.contracts import Task, TaskResult, TaskStatus
from ..providers.llm_qwen3 import Qwen3Provider


# ============================================================================
# Code Generation Models
# ============================================================================

class CodePattern(BaseModel):
    """Code pattern extracted from knowledge base."""
    pattern_id: str = Field(default_factory=lambda: str(uuid4()), description="Pattern ID")
    name: str = Field(..., description="Pattern name")
    description: str = Field(..., description="Pattern description")
    code_template: str = Field(..., description="Code template")
    language: str = Field(default="python", description="Programming language")
    category: str = Field(..., description="Pattern category")
    tags: List[str] = Field(default_factory=list, description="Pattern tags")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Template parameters")
    examples: List[str] = Field(default_factory=list, description="Usage examples")
    quality_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Pattern quality score")
    usage_count: int = Field(default=0, description="Number of times used")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")
    
    @field_validator('language')
    @classmethod
    def validate_language(cls, v):
        allowed_languages = ['python', 'javascript', 'typescript', 'go', 'rust', 'java', 'cpp']
        if v not in allowed_languages:
            raise ValueError(f"Language must be one of: {allowed_languages}")
        return v


class CodeGenerationRequest(BaseModel):
    """Request for code generation."""
    request_id: str = Field(default_factory=lambda: str(uuid4()), description="Request ID")
    description: str = Field(..., description="What to generate")
    language: str = Field(default="python", description="Target language")
    context: Optional[str] = Field(None, description="Additional context")
    requirements: List[str] = Field(default_factory=list, description="Specific requirements")
    patterns_to_use: Optional[List[str]] = Field(None, description="Specific patterns to use")
    quality_level: str = Field(default="high", description="Quality level")
    include_tests: bool = Field(default=True, description="Include unit tests")
    include_docs: bool = Field(default=True, description="Include documentation")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    
    @field_validator('quality_level')
    @classmethod
    def validate_quality_level(cls, v):
        allowed_levels = ['basic', 'standard', 'high', 'enterprise']
        if v not in allowed_levels:
            raise ValueError(f"Quality level must be one of: {allowed_levels}")
        return v


class CodeGenerationResult(BaseModel):
    """Result of code generation."""
    request_id: str = Field(..., description="Corresponding request ID")
    generated_code: str = Field(..., description="Generated code")
    test_code: Optional[str] = Field(None, description="Generated test code")
    documentation: Optional[str] = Field(None, description="Generated documentation")
    patterns_used: List[str] = Field(default_factory=list, description="Patterns used")
    knowledge_base_matches: List[Dict[str, Any]] = Field(default_factory=list, description="KB matches")
    quality_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Generated code quality")
    suggestions: List[str] = Field(default_factory=list, description="Improvement suggestions")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    generated_at: datetime = Field(default_factory=datetime.utcnow, description="Generation timestamp")


class CodeAnalysisResult(BaseModel):
    """Result of code analysis."""
    code_id: str = Field(default_factory=lambda: str(uuid4()), description="Analysis ID")
    code: str = Field(..., description="Code to analyze")
    language: str = Field(default="python", description="Code language")
    analysis_type: str = Field(default="comprehensive", description="Type of analysis")
    issues_found: List[Dict[str, Any]] = Field(default_factory=list, description="Issues found")
    suggestions: List[str] = Field(default_factory=list, description="Improvement suggestions")
    patterns_detected: List[str] = Field(default_factory=list, description="Patterns detected")
    quality_metrics: Dict[str, float] = Field(default_factory=dict, description="Quality metrics")
    complexity_score: float = Field(default=0.0, ge=0.0, description="Complexity score")
    maintainability_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Maintainability score")
    analyzed_at: datetime = Field(default_factory=datetime.utcnow, description="Analysis timestamp")


# ============================================================================
# Knowledge Base Code Generator
# ============================================================================

class KnowledgeBaseCodeGenerator:
    """Intelligent code generator using knowledge base patterns."""
    
    def __init__(
        self,
        vector_store: VectorStore,
        llm_provider: Qwen3Provider,
        generator_name: str = "kb_code_generator"
    ):
        self.vector_store = vector_store
        self.llm_provider = llm_provider
        self.generator_name = generator_name
        self.logger = logging.getLogger(__name__)
        
        # Pattern registry
        self.pattern_registry: Dict[str, CodePattern] = {}
        self._load_default_patterns()
        
        # Code templates
        self.templates = self._load_code_templates()
    
    def _load_default_patterns(self):
        """Load default code patterns."""
        default_patterns = [
            CodePattern(
                name="async_function",
                description="Async function with error handling",
                code_template="""
async def {function_name}({parameters}):
    \"\"\"{description}\"\"\"
    try:
        # Implementation here
        {implementation}
        return result
    except Exception as e:
        logger.error(f"Error in {function_name}: {e}")
        raise
""",
                category="function",
                tags=["async", "error_handling", "logging"],
                parameters={
                    "function_name": {"type": "string", "required": True},
                    "parameters": {"type": "string", "default": ""},
                    "description": {"type": "string", "default": "Function description"},
                    "implementation": {"type": "string", "required": True}
                },
                quality_score=0.9
            ),
            CodePattern(
                name="pydantic_model",
                description="Pydantic model with validation",
                code_template="""
class {class_name}(BaseModel):
    \"\"\"{description}\"\"\"
    {fields}
    
    @field_validator('{field_name}')
    @classmethod
    def validate_{field_name}(cls, v):
        {validation_logic}
        return v
    
    class Config:
        {config_options}
""",
                category="model",
                tags=["pydantic", "validation", "data_model"],
                parameters={
                    "class_name": {"type": "string", "required": True},
                    "description": {"type": "string", "default": "Model description"},
                    "fields": {"type": "string", "required": True},
                    "field_name": {"type": "string", "required": True},
                    "validation_logic": {"type": "string", "required": True},
                    "config_options": {"type": "string", "default": "pass"}
                },
                quality_score=0.95
            ),
            CodePattern(
                name="test_function",
                description="Unit test function with fixtures",
                code_template="""
@pytest.mark.asyncio
async def test_{function_name}({fixtures}):
    \"\"\"Test {function_name}.\"\"\"
    # Arrange
    {arrange_code}
    
    # Act
    result = await {function_name}({test_parameters})
    
    # Assert
    {assertions}
""",
                category="test",
                tags=["pytest", "async", "unit_test"],
                parameters={
                    "function_name": {"type": "string", "required": True},
                    "fixtures": {"type": "string", "default": ""},
                    "arrange_code": {"type": "string", "required": True},
                    "test_parameters": {"type": "string", "required": True},
                    "assertions": {"type": "string", "required": True}
                },
                quality_score=0.85
            ),
            CodePattern(
                name="mcp_tool",
                description="MCP tool implementation",
                code_template="""
async def {tool_name}({parameters}) -> Dict[str, Any]:
    \"\"\"{description}\"\"\"
    try:
        # Tool implementation
        {implementation}
        
        return {{
            "success": True,
            "result": result,
            "metadata": {{
                "execution_time": execution_time,
                "tool_name": "{tool_name}"
            }}
        }}
    except Exception as e:
        logger.error(f"Tool {tool_name} failed: {e}")
        return {{
            "success": False,
            "error": str(e),
            "metadata": {{
                "tool_name": "{tool_name}",
                "error_type": type(e).__name__
            }}
        }}
""",
                category="tool",
                tags=["mcp", "async", "error_handling"],
                parameters={
                    "tool_name": {"type": "string", "required": True},
                    "parameters": {"type": "string", "required": True},
                    "description": {"type": "string", "default": "Tool description"},
                    "implementation": {"type": "string", "required": True}
                },
                quality_score=0.9
            )
        ]
        
        for pattern in default_patterns:
            self.pattern_registry[pattern.name] = pattern
    
    def _load_code_templates(self) -> Dict[str, str]:
        """Load code templates for different scenarios."""
        return {
            "imports": """
from __future__ import annotations

import asyncio
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from uuid import uuid4

import pydantic
from pydantic import BaseModel, Field, field_validator
""",
            "class_header": """
class {class_name}(BaseModel):
    \"\"\"{description}\"\"\"
""",
            "async_method": """
    async def {method_name}(self, {parameters}) -> {return_type}:
        \"\"\"{description}\"\"\"
        try:
            {implementation}
        except Exception as e:
            self.logger.error(f"Error in {method_name}: {e}")
            raise
""",
            "test_template": """
import pytest
from unittest.mock import AsyncMock, Mock

from {module_path} import {class_name}


@pytest.mark.asyncio
class Test{class_name}:
    \"\"\"Test suite for {class_name}.\"\"\"
    
    async def test_{method_name}(self):
        \"\"\"Test {method_name}.\"\"\"
        # Arrange
        {arrange_code}
        
        # Act
        result = await instance.{method_name}({test_parameters})
        
        # Assert
        {assertions}
"""
        }
    
    async def generate_code(
        self,
        request: CodeGenerationRequest
    ) -> CodeGenerationResult:
        """Generate code using knowledge base patterns."""
        try:
            # Search knowledge base for relevant patterns
            kb_matches = await self._search_knowledge_base(request)
            
            # Select appropriate patterns
            selected_patterns = self._select_patterns(request, kb_matches)
            
            # Generate code using patterns
            generated_code = await self._generate_with_patterns(request, selected_patterns)
            
            # Generate tests if requested
            test_code = None
            if request.include_tests:
                test_code = await self._generate_tests(request, generated_code)
            
            # Generate documentation if requested
            documentation = None
            if request.include_docs:
                documentation = await self._generate_documentation(request, generated_code)
            
            # Calculate quality score
            quality_score = self._calculate_quality_score(generated_code, selected_patterns)
            
            # Generate suggestions
            suggestions = self._generate_suggestions(generated_code, quality_score)
            
            return CodeGenerationResult(
                request_id=request.request_id,
                generated_code=generated_code,
                test_code=test_code,
                documentation=documentation,
                patterns_used=[p.name for p in selected_patterns],
                knowledge_base_matches=kb_matches,
                quality_score=quality_score,
                suggestions=suggestions,
                metadata={
                    "generator": self.generator_name,
                    "language": request.language,
                    "quality_level": request.quality_level
                }
            )
            
        except Exception as e:
            self.logger.error(f"Code generation failed: {e}")
            raise
    
    async def _search_knowledge_base(
        self,
        request: CodeGenerationRequest
    ) -> List[Dict[str, Any]]:
        """Search knowledge base for relevant code patterns."""
        if not self.vector_store:
            return []
        
        # Create search query
        query_parts = [request.description]
        if request.context:
            query_parts.append(request.context)
        query_parts.extend(request.requirements)
        
        search_query = " ".join(query_parts)
        
        try:
            # Search for relevant documents
            results = await self.vector_store.search(
                query=search_query,
                limit=10,
                similarity_threshold=0.6,
                document_types=[DocumentType.CODE, DocumentType.DOCUMENTATION]
            )
            
            return [
                {
                    "content": result.document.content,
                    "metadata": result.document.metadata,
                    "similarity": result.similarity,
                    "source": result.document.source
                }
                for result in results
            ]
            
        except Exception as e:
            self.logger.error(f"Knowledge base search failed: {e}")
            return []
    
    def _select_patterns(
        self,
        request: CodeGenerationRequest,
        kb_matches: List[Dict[str, Any]]
    ) -> List[CodePattern]:
        """Select appropriate patterns for code generation."""
        selected_patterns = []
        
        # If specific patterns requested, use them
        if request.patterns_to_use:
            for pattern_name in request.patterns_to_use:
                if pattern_name in self.pattern_registry:
                    selected_patterns.append(self.pattern_registry[pattern_name])
            return selected_patterns
        
        # Otherwise, select based on description and requirements
        description_lower = request.description.lower()
        
        # Pattern selection logic
        if "async" in description_lower or "await" in description_lower:
            if "async_function" in self.pattern_registry:
                selected_patterns.append(self.pattern_registry["async_function"])
        
        if "model" in description_lower or "pydantic" in description_lower:
            if "pydantic_model" in self.pattern_registry:
                selected_patterns.append(self.pattern_registry["pydantic_model"])
        
        if "test" in description_lower or "unit test" in description_lower:
            if "test_function" in self.pattern_registry:
                selected_patterns.append(self.pattern_registry["test_function"])
        
        if "tool" in description_lower or "mcp" in description_lower:
            if "mcp_tool" in self.pattern_registry:
                selected_patterns.append(self.pattern_registry["mcp_tool"])
        
        # If no patterns selected, use default async function pattern
        if not selected_patterns and "async_function" in self.pattern_registry:
            selected_patterns.append(self.pattern_registry["async_function"])
        
        return selected_patterns
    
    async def _generate_with_patterns(
        self,
        request: CodeGenerationRequest,
        patterns: List[CodePattern]
    ) -> str:
        """Generate code using selected patterns."""
        if not patterns:
            return await self._generate_basic_code(request)
        
        # Use the highest quality pattern
        best_pattern = max(patterns, key=lambda p: p.quality_score)
        
        # Generate code using LLM with pattern as context
        prompt = self._create_generation_prompt(request, best_pattern)
        
        try:
            response = await self.llm_provider.generate_text(
                prompt=prompt,
                max_tokens=2000,
                temperature=0.3
            )
            
            # Extract code from response
            code = self._extract_code_from_response(response)
            
            # Apply pattern template if needed
            if best_pattern.code_template:
                code = self._apply_pattern_template(best_pattern, code, request)
            
            return code
            
        except Exception as e:
            self.logger.error(f"LLM generation failed: {e}")
            return await self._generate_basic_code(request)
    
    def _create_generation_prompt(
        self,
        request: CodeGenerationRequest,
        pattern: CodePattern
    ) -> str:
        """Create prompt for code generation."""
        return f"""
Generate {request.language} code for: {request.description}

Context: {request.context or "No additional context"}

Requirements:
{chr(10).join(f"- {req}" for req in request.requirements)}

Use this pattern as reference:
Name: {pattern.name}
Description: {pattern.description}
Template: {pattern.code_template}

Quality Level: {request.quality_level}

Generate clean, well-documented, production-ready code.
Include proper error handling, logging, and type hints.
"""
    
    def _extract_code_from_response(self, response: str) -> str:
        """Extract code from LLM response."""
        # Look for code blocks
        code_pattern = r'```(?:python|py)?\n(.*?)\n```'
        matches = re.findall(code_pattern, response, re.DOTALL)
        
        if matches:
            return matches[0].strip()
        
        # If no code blocks, return the response as-is
        return response.strip()
    
    def _apply_pattern_template(
        self,
        pattern: CodePattern,
        code: str,
        request: CodeGenerationRequest
    ) -> str:
        """Apply pattern template to generated code."""
        # Extract function/class name from description
        function_name = self._extract_name_from_description(request.description)
        
        # Apply template substitutions
        template = pattern.code_template
        substitutions = {
            "function_name": function_name,
            "class_name": function_name.title().replace("_", ""),
            "description": request.description,
            "parameters": self._extract_parameters_from_description(request.description),
            "implementation": code,
            "field_name": "name",  # Default field name
            "validation_logic": "if not v:\n            raise ValueError('Value cannot be empty')",
            "config_options": "pass"
        }
        
        # Apply substitutions
        for key, value in substitutions.items():
            template = template.replace(f"{{{key}}}", str(value))
        
        return template
    
    def _extract_name_from_description(self, description: str) -> str:
        """Extract function/class name from description."""
        # Simple extraction - look for "function", "class", etc.
        words = description.lower().split()
        
        if "function" in words:
            idx = words.index("function")
            if idx > 0:
                return words[idx - 1].replace("_", "_")
        
        if "class" in words:
            idx = words.index("class")
            if idx > 0:
                return words[idx - 1].replace("_", "_")
        
        # Default to first word
        return words[0].replace("_", "_") if words else "generated_code"
    
    def _extract_parameters_from_description(self, description: str) -> str:
        """Extract parameters from description."""
        # Simple parameter extraction
        if "no parameters" in description.lower():
            return ""
        
        # Look for parameter hints
        if "with parameters" in description.lower():
            # Extract parameters after "with parameters"
            parts = description.lower().split("with parameters")
            if len(parts) > 1:
                param_text = parts[1].split(".")[0]
                return param_text.strip()
        
        return "self"
    
    async def _generate_basic_code(self, request: CodeGenerationRequest) -> str:
        """Generate basic code without patterns."""
        prompt = f"""
Generate {request.language} code for: {request.description}

Context: {request.context or "No additional context"}

Requirements:
{chr(10).join(f"- {req}" for req in request.requirements)}

Generate clean, well-documented, production-ready code.
"""
        
        try:
            response = await self.llm_provider.generate_text(
                prompt=prompt,
                max_tokens=1500,
                temperature=0.3
            )
            return self._extract_code_from_response(response)
        except Exception as e:
            self.logger.error(f"Basic code generation failed: {e}")
            return f"# Generated code for: {request.description}\n# Implementation needed"
    
    async def _generate_tests(
        self,
        request: CodeGenerationRequest,
        code: str
    ) -> str:
        """Generate unit tests for the code."""
        prompt = f"""
Generate unit tests for this {request.language} code:

{code}

Generate comprehensive pytest tests with:
- Test cases for normal operation
- Test cases for error conditions
- Proper mocking where needed
- Clear test names and documentation
"""
        
        try:
            response = await self.llm_provider.generate_text(
                prompt=prompt,
                max_tokens=1000,
                temperature=0.2
            )
            return self._extract_code_from_response(response)
        except Exception as e:
            self.logger.error(f"Test generation failed: {e}")
            return f"# Tests for: {request.description}\n# Test implementation needed"
    
    async def _generate_documentation(
        self,
        request: CodeGenerationRequest,
        code: str
    ) -> str:
        """Generate documentation for the code."""
        prompt = f"""
Generate documentation for this {request.language} code:

{code}

Generate:
- Module-level documentation
- Function/class documentation
- Usage examples
- API reference
"""
        
        try:
            response = await self.llm_provider.generate_text(
                prompt=prompt,
                max_tokens=800,
                temperature=0.2
            )
            return response.strip()
        except Exception as e:
            self.logger.error(f"Documentation generation failed: {e}")
            return f"# Documentation for: {request.description}\n# Documentation needed"
    
    def _calculate_quality_score(
        self,
        code: str,
        patterns_used: List[CodePattern]
    ) -> float:
        """Calculate quality score for generated code."""
        score = 0.0
        
        # Base score from patterns
        if patterns_used:
            pattern_score = sum(p.quality_score for p in patterns_used) / len(patterns_used)
            score += pattern_score * 0.4
        
        # Code quality checks
        if "async def" in code:
            score += 0.1  # Async functions are good
        
        if "try:" in code and "except" in code:
            score += 0.1  # Error handling
        
        if "logger" in code:
            score += 0.1  # Logging
        
        if "type:" in code or "->" in code:
            score += 0.1  # Type hints
        
        if '"""' in code:
            score += 0.1  # Documentation
        
        if "pytest" in code or "test_" in code:
            score += 0.1  # Tests
        
        return min(score, 1.0)
    
    def _generate_suggestions(
        self,
        code: str,
        quality_score: float
    ) -> List[str]:
        """Generate improvement suggestions."""
        suggestions = []
        
        if quality_score < 0.7:
            suggestions.append("Consider adding more error handling")
            suggestions.append("Add comprehensive documentation")
        
        if "async def" not in code and "def " in code:
            suggestions.append("Consider making functions async for better performance")
        
        if "logger" not in code:
            suggestions.append("Add logging for better debugging")
        
        if "type:" not in code and "->" not in code:
            suggestions.append("Add type hints for better code clarity")
        
        if "test_" not in code:
            suggestions.append("Add unit tests for better reliability")
        
        return suggestions
    
    async def analyze_code(self, code: str, language: str = "python") -> CodeAnalysisResult:
        """Analyze existing code for quality and patterns."""
        try:
            # Basic analysis
            issues_found = []
            suggestions = []
            patterns_detected = []
            quality_metrics = {}
            
            # Check for common issues
            if "TODO" in code or "FIXME" in code:
                issues_found.append({
                    "type": "todo",
                    "message": "Contains TODO or FIXME comments",
                    "severity": "low"
                })
            
            if "print(" in code:
                issues_found.append({
                    "type": "logging",
                    "message": "Uses print() instead of logger",
                    "severity": "medium"
                })
                suggestions.append("Replace print() statements with proper logging")
            
            if "except:" in code:
                issues_found.append({
                    "type": "error_handling",
                    "message": "Bare except clause",
                    "severity": "high"
                })
                suggestions.append("Specify exception types in except clauses")
            
            # Detect patterns
            if "async def" in code:
                patterns_detected.append("async_function")
            
            if "class " in code and "BaseModel" in code:
                patterns_detected.append("pydantic_model")
            
            if "pytest" in code or "test_" in code:
                patterns_detected.append("test_function")
            
            # Calculate metrics
            lines_of_code = len(code.split('\n'))
            complexity_score = self._calculate_complexity(code)
            maintainability_score = self._calculate_maintainability(code, issues_found)
            
            quality_metrics = {
                "lines_of_code": lines_of_code,
                "complexity_score": complexity_score,
                "maintainability_score": maintainability_score,
                "documentation_coverage": self._calculate_doc_coverage(code),
                "test_coverage": self._calculate_test_coverage(code)
            }
            
            return CodeAnalysisResult(
                code=code,
                language=language,
                issues_found=issues_found,
                suggestions=suggestions,
                patterns_detected=patterns_detected,
                quality_metrics=quality_metrics,
                complexity_score=complexity_score,
                maintainability_score=maintainability_score
            )
            
        except Exception as e:
            self.logger.error(f"Code analysis failed: {e}")
            raise
    
    def _calculate_complexity(self, code: str) -> float:
        """Calculate code complexity score."""
        # Simple complexity calculation
        complexity_indicators = [
            "if ", "for ", "while ", "try:", "except", "def ", "class ",
            "and ", "or ", "not ", "lambda", "yield", "async def"
        ]
        
        complexity_count = sum(code.count(indicator) for indicator in complexity_indicators)
        lines = len(code.split('\n'))
        
        return complexity_count / max(lines, 1)
    
    def _calculate_maintainability(self, code: str, issues: List[Dict[str, Any]]) -> float:
        """Calculate maintainability score."""
        score = 1.0
        
        # Deduct for issues
        for issue in issues:
            severity = issue.get("severity", "low")
            if severity == "high":
                score -= 0.2
            elif severity == "medium":
                score -= 0.1
            else:
                score -= 0.05
        
        # Bonus for good practices
        if "logger" in code:
            score += 0.1
        if '"""' in code:
            score += 0.1
        if "type:" in code or "->" in code:
            score += 0.1
        
        return max(0.0, min(score, 1.0))
    
    def _calculate_doc_coverage(self, code: str) -> float:
        """Calculate documentation coverage."""
        functions = len(re.findall(r'def\s+\w+', code))
        documented_functions = len(re.findall(r'def\s+\w+.*?\n\s*""".*?"""', code, re.DOTALL))
        
        if functions == 0:
            return 1.0
        
        return documented_functions / functions
    
    def _calculate_test_coverage(self, code: str) -> float:
        """Calculate test coverage estimate."""
        functions = len(re.findall(r'def\s+\w+', code))
        test_functions = len(re.findall(r'def\s+test_\w+', code))
        
        if functions == 0:
            return 1.0
        
        return min(test_functions / functions, 1.0)
    
    def register_pattern(self, pattern: CodePattern):
        """Register a new code pattern."""
        self.pattern_registry[pattern.name] = pattern
        self.logger.info(f"Registered pattern: {pattern.name}")
    
    def get_pattern_catalog(self) -> Dict[str, CodePattern]:
        """Get the complete pattern catalog."""
        return self.pattern_registry.copy()


# ============================================================================
# Factory Functions
# ============================================================================

async def create_code_generator(
    vector_store: VectorStore,
    llm_provider: Qwen3Provider,
    generator_name: str = "kb_code_generator"
) -> KnowledgeBaseCodeGenerator:
    """Create a new knowledge base code generator."""
    return KnowledgeBaseCodeGenerator(vector_store, llm_provider, generator_name)


def create_generation_request(
    description: str,
    language: str = "python",
    context: Optional[str] = None,
    requirements: Optional[List[str]] = None,
    quality_level: str = "high"
) -> CodeGenerationRequest:
    """Create a code generation request."""
    return CodeGenerationRequest(
        description=description,
        language=language,
        context=context,
        requirements=requirements or [],
        quality_level=quality_level
    )


# ============================================================================
# Example Usage
# ============================================================================

async def example_usage():
    """Example usage of the knowledge base code generator."""
    # This would be used in actual implementation
    pass
