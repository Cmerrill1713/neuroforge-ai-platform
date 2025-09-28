"""
Tool Catalog Parser and Validator for Agentic LLM Core v0.1

This module provides functionality to parse, validate, and manage tool catalogs
from YAML configuration files.

Created: 2024-09-24
Status: Draft
"""

from __future__ import annotations

import yaml
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from enum import Enum
from pathlib import Path

from pydantic import BaseModel, Field, validator, ValidationError

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


# ============================================================================
# Data Models
# ============================================================================

class SafetyLevel(str, Enum):
    """Tool safety levels."""
    SAFE = "safe"
    MODERATE = "moderate"
    DANGEROUS = "dangerous"
    CRITICAL = "critical"


class ValidationSeverity(str, Enum):
    """Validation severity levels."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


class ToolParameter(BaseModel):
    """Tool parameter specification."""
    name: str = Field(..., description="Parameter name")
    type: str = Field(..., description="Parameter type")
    required: bool = Field(default=False, description="Whether parameter is required")
    default: Optional[Any] = Field(None, description="Default value")
    description: str = Field(..., description="Parameter description")
    validation: Optional[Dict[str, Any]] = Field(None, description="Validation rules")


class ToolSpec(BaseModel):
    """Tool specification."""
    name: str = Field(..., description="Tool name")
    category: str = Field(..., description="Tool category")
    description: str = Field(..., description="Tool description")
    parameters: List[ToolParameter] = Field(default_factory=list, description="Tool parameters")
    returns: Dict[str, str] = Field(default_factory=dict, description="Return value specifications")
    safety_level: SafetyLevel = Field(..., description="Tool safety level")
    requires_permissions: List[str] = Field(default_factory=list, description="Required permissions")


class ToolCategory(BaseModel):
    """Tool category specification."""
    name: str = Field(..., description="Category name")
    description: str = Field(..., description="Category description")
    priority: str = Field(..., description="Category priority")
    offline_compatible: bool = Field(..., description="Offline compatibility")


class ValidationRule(BaseModel):
    """Validation rule specification."""
    name: str = Field(..., description="Rule name")
    description: str = Field(..., description="Rule description")
    severity: ValidationSeverity = Field(..., description="Rule severity")


class ToolCatalog(BaseModel):
    """Complete tool catalog."""
    version: str = Field(..., description="Catalog version")
    last_updated: str = Field(..., description="Last update timestamp")
    description: str = Field(..., description="Catalog description")
    categories: List[ToolCategory] = Field(default_factory=list, description="Tool categories")
    tools: List[ToolSpec] = Field(default_factory=list, description="Tool specifications")
    validation: Optional[Dict[str, Any]] = Field(None, description="Validation rules")
    policies: Optional[Dict[str, Any]] = Field(None, description="Tool policies")


class CatalogValidationResult(BaseModel):
    """Tool catalog validation result."""
    is_valid: bool = Field(..., description="Whether catalog is valid")
    errors: List[str] = Field(default_factory=list, description="Validation errors")
    warnings: List[str] = Field(default_factory=list, description="Validation warnings")
    info: List[str] = Field(default_factory=list, description="Validation info")
    tool_count: int = Field(0, description="Number of tools")
    category_count: int = Field(0, description="Number of categories")
    validation_summary: Dict[str, Any] = Field(default_factory=dict, description="Validation summary")


class ToolSummary(BaseModel):
    """Tool summary for reporting."""
    name: str = Field(..., description="Tool name")
    category: str = Field(..., description="Tool category")
    description: str = Field(..., description="Tool description")
    safety_level: SafetyLevel = Field(..., description="Safety level")
    parameter_count: int = Field(0, description="Number of parameters")
    required_permissions: List[str] = Field(default_factory=list, description="Required permissions")
    offline_compatible: bool = Field(True, description="Offline compatibility")


# ============================================================================
# Tool Catalog Parser
# ============================================================================

class ToolCatalogParser:
    """Parser for tool catalog YAML files."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def parse_file(self, file_path: Union[str, Path]) -> ToolCatalog:
        """Parse a tool catalog from YAML file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            
            self.logger.info(f"Successfully loaded tool catalog from {file_path}")
            return self._parse_data(data)
            
        except FileNotFoundError:
            raise FileNotFoundError(f"Tool catalog file not found: {file_path}")
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML format in {file_path}: {e}")
        except Exception as e:
            raise RuntimeError(f"Failed to parse tool catalog from {file_path}: {e}")
    
    def _parse_data(self, data: Dict[str, Any]) -> ToolCatalog:
        """Parse tool catalog data."""
        try:
            # Parse tool catalog structure
            catalog_data = data.get('tool_catalog', {})
            tools_data = data.get('tools', [])
            validation_data = data.get('validation', {})
            policies_data = data.get('policies', {})
            
            # Parse categories
            categories = []
            for cat_data in catalog_data.get('categories', []):
                categories.append(ToolCategory(**cat_data))
            
            # Parse tools
            tools = []
            for tool_data in tools_data:
                # Parse parameters
                parameters = []
                for param_data in tool_data.get('parameters', []):
                    parameters.append(ToolParameter(**param_data))
                
                tool_data['parameters'] = parameters
                tools.append(ToolSpec(**tool_data))
            
            return ToolCatalog(
                version=catalog_data.get('version', '0.1.0'),
                last_updated=catalog_data.get('last_updated', datetime.now().isoformat()),
                description=catalog_data.get('description', 'Tool catalog'),
                categories=categories,
                tools=tools,
                validation=validation_data,
                policies=policies_data
            )
            
        except ValidationError as e:
            raise ValueError(f"Invalid tool catalog structure: {e}")
        except Exception as e:
            raise RuntimeError(f"Failed to parse tool catalog data: {e}")


# ============================================================================
# Tool Catalog Validator
# ============================================================================

class ToolCatalogValidator:
    """Validator for tool catalogs."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def validate(self, catalog: ToolCatalog) -> CatalogValidationResult:
        """Validate a tool catalog."""
        errors = []
        warnings = []
        info = []
        
        # Basic validation
        self._validate_basic_structure(catalog, errors, warnings, info)
        
        # Tool validation
        self._validate_tools(catalog, errors, warnings, info)
        
        # Category validation
        self._validate_categories(catalog, errors, warnings, info)
        
        # Policy validation
        self._validate_policies(catalog, errors, warnings, info)
        
        # Generate summary
        validation_summary = self._generate_validation_summary(catalog, errors, warnings, info)
        
        return CatalogValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            info=info,
            tool_count=len(catalog.tools),
            category_count=len(catalog.categories),
            validation_summary=validation_summary
        )
    
    def _validate_basic_structure(self, catalog: ToolCatalog, errors: List[str], warnings: List[str], info: List[str]):
        """Validate basic catalog structure."""
        if not catalog.tools:
            errors.append("Tool catalog must contain at least one tool")
        
        if not catalog.categories:
            warnings.append("Tool catalog contains no categories")
        
        if catalog.version == "0.1.0":
            info.append("Using initial version of tool catalog")
    
    def _validate_tools(self, catalog: ToolCatalog, errors: List[str], warnings: List[str], info: List[str]):
        """Validate tool specifications."""
        tool_names = set()
        category_names = {cat.name for cat in catalog.categories}
        
        for tool in catalog.tools:
            # Check for duplicate tool names
            if tool.name in tool_names:
                errors.append(f"Duplicate tool name: {tool.name}")
            tool_names.add(tool.name)
            
            # Check category exists
            if tool.category not in category_names:
                errors.append(f"Tool '{tool.name}' references unknown category: {tool.category}")
            
            # Check parameter validation
            for param in tool.parameters:
                if param.required and param.default is not None:
                    warnings.append(f"Tool '{tool.name}' parameter '{param.name}' is required but has default value")
            
            # Check safety level
            if tool.safety_level in [SafetyLevel.DANGEROUS, SafetyLevel.CRITICAL]:
                if not tool.requires_permissions:
                    warnings.append(f"Tool '{tool.name}' has {tool.safety_level} safety level but no required permissions")
    
    def _validate_categories(self, catalog: ToolCatalog, errors: List[str], warnings: List[str], info: List[str]):
        """Validate category specifications."""
        category_names = set()
        
        for category in catalog.categories:
            if category.name in category_names:
                errors.append(f"Duplicate category name: {category.name}")
            category_names.add(category.name)
            
            if category.priority not in ["low", "medium", "high", "critical"]:
                warnings.append(f"Category '{category.name}' has invalid priority: {category.priority}")
    
    def _validate_policies(self, catalog: ToolCatalog, errors: List[str], warnings: List[str], info: List[str]):
        """Validate tool policies."""
        if catalog.policies:
            policies = catalog.policies
            
            # Check execution policies
            if 'execution' in policies:
                exec_policies = policies['execution']
                if exec_policies.get('max_concurrent_tools', 0) <= 0:
                    errors.append("max_concurrent_tools must be positive")
                
                if exec_policies.get('default_timeout', 0) <= 0:
                    errors.append("default_timeout must be positive")
            
            # Check security policies
            if 'security' in policies:
                sec_policies = policies['security']
                if not sec_policies.get('require_authentication', False):
                    warnings.append("Authentication is not required - consider enabling for production")
    
    def _generate_validation_summary(self, catalog: ToolCatalog, errors: List[str], warnings: List[str], info: List[str]) -> Dict[str, Any]:
        """Generate validation summary."""
        return {
            "total_tools": len(catalog.tools),
            "total_categories": len(catalog.categories),
            "tools_by_category": self._count_tools_by_category(catalog),
            "tools_by_safety_level": self._count_tools_by_safety_level(catalog),
            "validation_issues": {
                "errors": len(errors),
                "warnings": len(warnings),
                "info": len(info)
            },
            "offline_compatible_tools": self._count_offline_compatible_tools(catalog),
            "tools_requiring_permissions": self._count_tools_requiring_permissions(catalog)
        }
    
    def _count_tools_by_category(self, catalog: ToolCatalog) -> Dict[str, int]:
        """Count tools by category."""
        counts = {}
        for tool in catalog.tools:
            counts[tool.category] = counts.get(tool.category, 0) + 1
        return counts
    
    def _count_tools_by_safety_level(self, catalog: ToolCatalog) -> Dict[str, int]:
        """Count tools by safety level."""
        counts = {}
        for tool in catalog.tools:
            counts[tool.safety_level.value] = counts.get(tool.safety_level.value, 0) + 1
        return counts
    
    def _count_offline_compatible_tools(self, catalog: ToolCatalog) -> int:
        """Count offline compatible tools."""
        compatible_categories = {cat.name for cat in catalog.categories if cat.offline_compatible}
        return sum(1 for tool in catalog.tools if tool.category in compatible_categories)
    
    def _count_tools_requiring_permissions(self, catalog: ToolCatalog) -> int:
        """Count tools requiring permissions."""
        return sum(1 for tool in catalog.tools if tool.requires_permissions)


# ============================================================================
# Tool Catalog Manager
# ============================================================================

class ToolCatalogManager:
    """Manager for tool catalogs."""
    
    def __init__(self):
        self.parser = ToolCatalogParser()
        self.validator = ToolCatalogValidator()
        self.logger = logging.getLogger(__name__)
    
    def load_and_validate(self, file_path: Union[str, Path], validate: bool = True) -> tuple[ToolCatalog, Optional[CatalogValidationResult]]:
        """Load and optionally validate a tool catalog."""
        catalog = self.parser.parse_file(file_path)
        
        validation_result = None
        if validate:
            validation_result = self.validator.validate(catalog)
            
            if not validation_result.is_valid:
                self.logger.error(f"Tool catalog validation failed with {len(validation_result.errors)} errors")
            else:
                self.logger.info(f"Tool catalog validation passed with {len(validation_result.warnings)} warnings")
        
        return catalog, validation_result
    
    def generate_tool_summaries(self, catalog: ToolCatalog) -> List[ToolSummary]:
        """Generate tool summaries."""
        summaries = []
        category_map = {cat.name: cat for cat in catalog.categories}
        
        for tool in catalog.tools:
            category = category_map.get(tool.category)
            summary = ToolSummary(
                name=tool.name,
                category=tool.category,
                description=tool.description,
                safety_level=tool.safety_level,
                parameter_count=len(tool.parameters),
                required_permissions=tool.requires_permissions,
                offline_compatible=category.offline_compatible if category else True
            )
            summaries.append(summary)
        
        return summaries
    
    def print_summaries(self, summaries: List[ToolSummary]):
        """Print tool summaries in a formatted way."""
        print("\n" + "="*80)
        print("TOOL CATALOG SUMMARIES")
        print("="*80)
        
        # Group by category
        by_category = {}
        for summary in summaries:
            if summary.category not in by_category:
                by_category[summary.category] = []
            by_category[summary.category].append(summary)
        
        for category, tools in by_category.items():
            print(f"\n📁 {category.upper()} ({len(tools)} tools)")
            print("-" * 50)
            
            for tool in tools:
                safety_emoji = {
                    SafetyLevel.SAFE: "🟢",
                    SafetyLevel.MODERATE: "🟡", 
                    SafetyLevel.DANGEROUS: "🟠",
                    SafetyLevel.CRITICAL: "🔴"
                }.get(tool.safety_level, "⚪")
                
                offline_emoji = "🏠" if tool.offline_compatible else "🌐"
                perm_emoji = "🔐" if tool.required_permissions else "🔓"
                
                print(f"  {safety_emoji} {tool.name}")
                print(f"    Description: {tool.description}")
                print(f"    Parameters: {tool.parameter_count}")
                print(f"    Safety: {tool.safety_level.value}")
                print(f"    {offline_emoji} Offline: {'Yes' if tool.offline_compatible else 'No'}")
                print(f"    {perm_emoji} Permissions: {', '.join(tool.required_permissions) if tool.required_permissions else 'None'}")
                print()


# ============================================================================
# Main Function
# ============================================================================

def main():
    """Main function for command-line usage."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Tool Catalog Parser and Validator")
    parser.add_argument("source", help="Path to the tool catalog YAML file")
    parser.add_argument("--validate", action="store_true", help="Validate the catalog")
    parser.add_argument("--print-summaries", action="store_true", help="Print tool summaries")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    try:
        manager = ToolCatalogManager()
        catalog, validation_result = manager.load_and_validate(args.source, validate=args.validate)
        
        print(f"✅ Successfully loaded tool catalog: {catalog.description}")
        print(f"📊 Version: {catalog.version}")
        print(f"📅 Last Updated: {catalog.last_updated}")
        print(f"🔧 Tools: {len(catalog.tools)}")
        print(f"📁 Categories: {len(catalog.categories)}")
        
        if validation_result:
            print(f"\n🔍 Validation Results:")
            print(f"   Status: {'✅ Valid' if validation_result.is_valid else '❌ Invalid'}")
            print(f"   Errors: {len(validation_result.errors)}")
            print(f"   Warnings: {len(validation_result.warnings)}")
            print(f"   Info: {len(validation_result.info)}")
            
            if validation_result.errors:
                print("\n❌ Errors:")
                for error in validation_result.errors:
                    print(f"   - {error}")
            
            if validation_result.warnings:
                print("\n⚠️  Warnings:")
                for warning in validation_result.warnings:
                    print(f"   - {warning}")
        
        if args.print_summaries:
            summaries = manager.generate_tool_summaries(catalog)
            manager.print_summaries(summaries)
        
    except Exception as e:
        logger.error(f"Failed to process tool catalog: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
