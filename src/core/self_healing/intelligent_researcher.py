#!/usr/bin/env python3
"""
Intelligent Research Component for Self-Healing System
Automatically researches and learns how to fix unknown issues
"""

import os
import re
import json
import logging
import subprocess
import asyncio
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import importlib.util
import sys
from datetime import datetime

# Import the parallel research crawler
try:
    from .parallel_research_crawler import parallel_research_crawler
except ImportError:
    # Fallback for direct imports
    import sys
    sys.path.append(os.path.dirname(__file__))
    try:
        from parallel_research_crawler import parallel_research_crawler
    except ImportError:
        parallel_research_crawler = None

class IntelligentResearcher:
    """Intelligent researcher that learns how to fix unknown issues."""
    
    def __init__(self):
        """Initialize the intelligent researcher."""
        self.logger = logging.getLogger(__name__)
        self.research_cache = {}
        self.knowledge_base_path = "knowledge_base/research_solutions.json"
        self._load_research_knowledge()
    
    def _load_research_knowledge(self):
        """Load existing research knowledge."""
        try:
            if os.path.exists(self.knowledge_base_path):
                with open(self.knowledge_base_path, 'r') as f:
                    self.research_cache = json.load(f)
                self.logger.info(f"Loaded {len(self.research_cache)} research solutions")
            else:
                self.research_cache = {}
        except Exception as e:
            self.logger.warning(f"Failed to load research knowledge: {e}")
            self.research_cache = {}
    
    def _save_research_knowledge(self):
        """Save research knowledge to file."""
        try:
            os.makedirs(os.path.dirname(self.knowledge_base_path), exist_ok=True)
            with open(self.knowledge_base_path, 'w') as f:
                json.dump(self.research_cache, f, indent=2)
            self.logger.info("Research knowledge saved")
        except Exception as e:
            self.logger.error(f"Failed to save research knowledge: {e}")
    
    def research_solution(self, error_message: str) -> Dict[str, Any]:
        """Research a solution for an unknown error."""
        self.logger.info(f"🔍 Researching solution for: {error_message[:100]}...")
        
        # Check if we already have a solution
        error_key = self._generate_error_key(error_message)
        if error_key in self.research_cache:
            self.logger.info(f"📚 Found cached solution for: {error_key}")
            return self.research_cache[error_key]
        
        # Use parallel research crawler if available
        if parallel_research_crawler:
            try:
                # Run async research in sync context
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    solution = loop.run_until_complete(
                        parallel_research_crawler.research_error_parallel(error_message)
                    )
                    
                    if solution and solution.get("solution_found"):
                        # Convert parallel result to expected format
                        converted_solution = {
                            "error_type": solution.get("solution_type", "unknown"),
                            "solution_type": solution.get("solution_type", "unknown"),
                            "fix_instructions": solution.get("fix_instructions", []),
                            "confidence": solution.get("confidence", 0.0),
                            "research_method": "parallel_crawling",
                            "details": solution.get("details", ""),
                            "sources_analyzed": solution.get("sources_analyzed", 0),
                            "content_analyzed": solution.get("content_analyzed", 0)
                        }
                        
                        # Cache the solution
                        self.research_cache[error_key] = converted_solution
                        self._save_research_knowledge()
                        self.logger.info(f"✅ Parallel research completed: {solution.get('solution_type', 'unknown')} (confidence: {solution.get('confidence', 0):.2f})")
                        
                        return converted_solution
                    else:
                        self.logger.warning("Parallel research crawler found no solution, falling back to basic research")
                        
                finally:
                    loop.close()
                    
            except Exception as e:
                self.logger.warning(f"Parallel research crawler failed: {e}, falling back to basic research")
        
        # Fallback to basic research
        solution = self._conduct_research(error_message)
        
        # Cache the solution
        if solution:
            self.research_cache[error_key] = solution
            self._save_research_knowledge()
            self.logger.info(f"💾 Cached new solution for: {error_key}")
        
        return solution
    
    def _generate_error_key(self, error_message: str) -> str:
        """Generate a unique key for the error message."""
        # Extract key components from error message
        key_parts = []
        
        # Look for import errors
        if "cannot import name" in error_message:
            match = re.search(r"cannot import name '([^']+)' from '([^']+)'", error_message)
            if match:
                key_parts.extend(["import", match.group(1), match.group(2)])
        
        # Look for attribute errors
        elif "has no attribute" in error_message:
            match = re.search(r"'([^']+)' object has no attribute '([^']+)'", error_message)
            if match:
                key_parts.extend(["attribute", match.group(1), match.group(2)])
        
        # Look for module not found
        elif "No module named" in error_message:
            match = re.search(r"No module named '([^']+)'", error_message)
            if match:
                key_parts.extend(["module", match.group(1)])
        
        # Look for dimension mismatches
        elif "Incompatible dimension" in error_message:
            key_parts.extend(["dimension_mismatch"])
        
        # Fallback to first few words
        if not key_parts:
            key_parts = error_message.split()[:3]
        
        return "_".join(key_parts).replace("'", "").replace('"', "")
    
    def _conduct_research(self, error_message: str) -> Optional[Dict[str, Any]]:
        """Conduct research to find a solution."""
        try:
            # Try multiple research strategies
            strategies = [
                self._research_codebase_analysis,
                self._research_file_structure,
                self._research_import_patterns,
                self._research_common_solutions
            ]
            
            for strategy in strategies:
                solution = strategy(error_message)
                if solution:
                    self.logger.info(f"✅ Found solution using strategy: {strategy.__name__}")
                    return solution
            
            self.logger.warning("❌ No solution found through research")
            return None
            
        except Exception as e:
            self.logger.error(f"Research failed: {e}")
            return None
    
    def _research_codebase_analysis(self, error_message: str) -> Optional[Dict[str, Any]]:
        """Analyze the codebase to find solutions."""
        self.logger.info("🔍 Analyzing codebase structure...")
        
        # Look for import errors
        if "cannot import name" in error_message:
            match = re.search(r"cannot import name '([^']+)' from '([^']+)'", error_message)
            if match:
                class_name = match.group(1)
                module_path = match.group(2)
                
                # Check if the module exists
                module_file = module_path.replace('.', '/') + '.py'
                if os.path.exists(module_file):
                    # Check if the class exists in the file
                    with open(module_file, 'r') as f:
                        content = f.read()
                        if f"class {class_name}" not in content:
                            return {
                                "error_type": "import_error",
                                "solution_type": "create_missing_class",
                                "details": {
                                    "class_name": class_name,
                                    "module_path": module_path,
                                    "module_file": module_file
                                },
                                "fix_instructions": [
                                    f"Create class {class_name} in {module_file}",
                                    "Add basic implementation with required methods",
                                    "Ensure proper imports and exports"
                                ],
                                "confidence": 0.9,
                                "research_method": "codebase_analysis"
                            }
        
        # Look for attribute errors
        elif "has no attribute" in error_message:
            match = re.search(r"'([^']+)' object has no attribute '([^']+)'", error_message)
            if match:
                class_name = match.group(1)
                method_name = match.group(2)
                
                return {
                    "error_type": "missing_method",
                    "solution_type": "add_missing_method",
                    "details": {
                        "class_name": class_name,
                        "method_name": method_name
                    },
                    "fix_instructions": [
                        f"Add method {method_name} to class {class_name}",
                        "Implement basic functionality",
                        "Add proper error handling"
                    ],
                    "confidence": 0.95,
                    "research_method": "codebase_analysis"
                }
        
        return None
    
    def _research_file_structure(self, error_message: str) -> Optional[Dict[str, Any]]:
        """Research file structure to understand the issue."""
        self.logger.info("📁 Analyzing file structure...")
        
        if "No module named" in error_message:
            match = re.search(r"No module named '([^']+)'", error_message)
            if match:
                module_name = match.group(1)
                
                # Check if it's a local module
                local_paths = [
                    f"{module_name}.py",
                    f"{module_name}/__init__.py",
                    f"src/{module_name}.py",
                    f"src/{module_name}/__init__.py"
                ]
                
                for path in local_paths:
                    if os.path.exists(path):
                        return {
                            "error_type": "module_not_found",
                            "solution_type": "fix_import_path",
                            "details": {
                                "module_name": module_name,
                                "found_path": path
                            },
                            "fix_instructions": [
                                f"Fix import path for {module_name}",
                                f"Use correct path: {path}",
                                "Update __init__.py files if needed"
                            ],
                            "confidence": 0.8,
                            "research_method": "file_structure"
                        }
        
        return None
    
    def _research_import_patterns(self, error_message: str) -> Optional[Dict[str, Any]]:
        """Research import patterns in the codebase."""
        self.logger.info("📦 Analyzing import patterns...")
        
        if "cannot import name" in error_message:
            match = re.search(r"cannot import name '([^']+)' from '([^']+)'", error_message)
            if match:
                class_name = match.group(1)
                module_path = match.group(2)
                
                # Look for similar imports in the codebase
                similar_imports = self._find_similar_imports(class_name, module_path)
                if similar_imports:
                    return {
                        "error_type": "import_error",
                        "solution_type": "fix_import_pattern",
                        "details": {
                            "class_name": class_name,
                            "module_path": module_path,
                            "similar_imports": similar_imports
                        },
                        "fix_instructions": [
                            "Check existing import patterns",
                            "Ensure class is properly exported",
                            "Verify module structure"
                        ],
                        "confidence": 0.7,
                        "research_method": "import_patterns"
                    }
        
        return None
    
    def _research_common_solutions(self, error_message: str) -> Optional[Dict[str, Any]]:
        """Research common solutions for known error patterns."""
        self.logger.info("💡 Checking common solutions...")
        
        # Common Python error patterns and solutions
        common_solutions = {
            "cannot import name": {
                "error_type": "import_error",
                "solution_type": "generic_import_fix",
                "fix_instructions": [
                    "Check if the class/function exists in the module",
                    "Verify the module path is correct",
                    "Ensure __init__.py files are present",
                    "Check for circular imports"
                ],
                "confidence": 0.6
            },
            "has no attribute": {
                "error_type": "missing_attribute",
                "solution_type": "add_missing_attribute",
                "fix_instructions": [
                    "Add the missing attribute/method to the class",
                    "Check if the attribute should be inherited",
                    "Verify the object type is correct"
                ],
                "confidence": 0.8
            },
            "No module named": {
                "error_type": "module_not_found",
                "solution_type": "install_or_fix_module",
                "fix_instructions": [
                    "Install the missing module with pip",
                    "Check PYTHONPATH environment variable",
                    "Verify module name and path"
                ],
                "confidence": 0.7
            }
        }
        
        for pattern, solution in common_solutions.items():
            if pattern in error_message:
                solution_copy = solution.copy()
                solution_copy["research_method"] = "common_solutions"
                solution_copy["details"] = {"error_message": error_message}
                return solution_copy
        
        return None
    
    def _find_similar_imports(self, class_name: str, module_path: str) -> List[str]:
        """Find similar imports in the codebase."""
        similar_imports = []
        
        try:
            # Search for similar import patterns
            for root, dirs, files in os.walk("."):
                for file in files:
                    if file.endswith('.py'):
                        file_path = os.path.join(root, file)
                        try:
                            with open(file_path, 'r') as f:
                                content = f.read()
                                if f"from {module_path}" in content:
                                    similar_imports.append(file_path)
                        except Exception:
                            continue
                        
                        if len(similar_imports) >= 5:  # Limit results
                            break
                
                if len(similar_imports) >= 5:
                    break
        
        except Exception as e:
            self.logger.warning(f"Error finding similar imports: {e}")
        
        return similar_imports
    
    def generate_fix_implementation(self, solution: Dict[str, Any]) -> Optional[str]:
        """Generate actual fix implementation based on research."""
        if not solution:
            return None
        
        solution_type = solution.get("solution_type")
        details = solution.get("details", {})
        
        if solution_type == "create_missing_class":
            return self._generate_missing_class_fix(details)
        elif solution_type == "add_missing_method":
            return self._generate_missing_method_fix(details)
        elif solution_type == "fix_import_path":
            return self._generate_import_fix(details)
        elif solution_type == "generic_import_fix":
            return self._generate_generic_import_fix(details)
        elif solution_type == "install_or_fix_module":
            return self._generate_module_install_fix(details)
        elif solution_type == "add_missing_attribute":
            return self._generate_missing_attribute_fix(details)
        
        return None
    
    def _generate_generic_import_fix(self, details: Dict[str, Any]) -> str:
        """Generate code for generic import fix."""
        error_message = details.get("error_message", "")
        
        # Extract class/module name from error
        if "cannot import name" in error_message:
            match = re.search(r"cannot import name '([^']+)' from '([^']+)'", error_message)
            if match:
                class_name = match.group(1)
                module_path = match.group(2)
                
                return f'''# Fix for import error: {error_message}
# Option 1: Create missing class/function
class {class_name}:
    """Auto-generated class for {class_name}"""
    
    def __init__(self):
        """Initialize {class_name}"""
        pass
    
    def get_stats(self):
        """Get basic stats"""
        return {{"status": "auto-generated", "timestamp": "{datetime.now().isoformat()}"}}
    
    def clear_all(self):
        """Clear all data"""
        pass

# Option 2: Fix import path
# from {module_path.replace('.', '/')}.{class_name} import {class_name}
# or
# from {module_path} import {class_name}
'''
        
        return f"# Generic import fix for: {error_message}"
    
    def _generate_module_install_fix(self, details: Dict[str, Any]) -> str:
        """Generate code for module installation fix."""
        error_message = details.get("error_message", "")
        
        if "No module named" in error_message:
            match = re.search(r"No module named '([^']+)'", error_message)
            if match:
                module_name = match.group(1)
                
                return f'''# Fix for missing module: {error_message}
# Option 1: Install the module
# pip install {module_name}

# Option 2: Create local module if it should exist
import os
from pathlib import Path

# Create the module structure
module_path = Path("{module_name}")
module_path.mkdir(parents=True, exist_ok=True)

# Create __init__.py
init_file = module_path / "__init__.py"
if not init_file.exists():
    init_file.write_text("# {module_name} module\\n")

# Create basic module file
module_file = module_path / "{module_name}.py"
if not module_file.exists():
    module_file.write_text(f"""# {module_name} module
class {module_name.title()}:
    def __init__(self):
        pass
    
    def get_stats(self):
        return {{"status": "auto-generated"}}
""")
'''
        
        return f"# Module installation fix for: {error_message}"
    
    def _generate_missing_attribute_fix(self, details: Dict[str, Any]) -> str:
        """Generate code for missing attribute fix."""
        error_message = details.get("error_message", "")
        
        if "has no attribute" in error_message:
            match = re.search(r"'([^']+)' object has no attribute '([^']+)'", error_message)
            if match:
                class_name = match.group(1)
                method_name = match.group(2)
                
                return f'''# Fix for missing attribute: {error_message}
# Add missing method to {class_name} class

def {method_name}(self, *args, **kwargs):
    """Auto-generated method for {method_name}"""
    # Basic implementation
    return None

# Add this method to the {class_name} class definition
'''
        
        return f"# Missing attribute fix for: {error_message}"
    
    def _generate_missing_class_fix(self, details: Dict[str, Any]) -> str:
        """Generate code for missing class."""
        class_name = details.get("class_name", "UnknownClass")
        module_file = details.get("module_file", "")
        
        # Basic class template
        class_code = f'''class {class_name}:
    """Auto-generated class for {class_name}"""
    
    def __init__(self):
        """Initialize {class_name}"""
        pass
    
    def get_stats(self):
        """Get basic stats"""
        return {{"status": "auto-generated", "timestamp": "2025-10-02T17:30:32.551223"}}
    
    def clear_all(self):
        """Clear all data"""
        pass
'''
        
        return class_code
    
    def _generate_missing_method_fix(self, details: Dict[str, Any]) -> str:
        """Generate code for missing method."""
        class_name = details.get("class_name", "UnknownClass")
        method_name = details.get("method_name", "unknown_method")
        
        # Basic method template
        method_code = f'''def {method_name}(self):
        """Auto-generated method for {method_name}"""
        return {{"status": "auto-generated", "method": "{method_name}"}}'''
        
        return method_code
    
    def _generate_import_fix(self, details: Dict[str, Any]) -> str:
        """Generate import fix."""
        module_name = details.get("module_name", "")
        found_path = details.get("found_path", "")
        
        return f"# Fix import for {module_name}\n# Found at: {found_path}\n# Update import statement accordingly"
    
    def get_research_stats(self) -> Dict[str, Any]:
        """Get research statistics."""
        return {
            "total_research_entries": len(self.research_cache),
            "research_methods": list(set(entry.get("research_method", "unknown") for entry in self.research_cache.values())),
            "solution_types": list(set(entry.get("solution_type", "unknown") for entry in self.research_cache.values())),
            "average_confidence": sum(entry.get("confidence", 0) for entry in self.research_cache.values()) / len(self.research_cache) if self.research_cache else 0
        }
