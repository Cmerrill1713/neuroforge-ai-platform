#!/usr/bin/env python3
"""
Import Guardian - Permanent solution to prevent recurring import issues
"""

import sys
import logging
from typing import Any, Optional, Dict, Callable
from functools import wraps

logger = logging.getLogger(__name__)

class ImportGuardian:
    """Permanent solution for import stability and graceful degradation"""
    
    def __init__(self):
        self.failed_imports = set()
        self.alternatives = {}
        self.fallback_handlers = {}
        
    def safe_import(self, module_name: str, fallback_value: Any = None, 
                   alternative_module: Optional[str] = None) -> Any:
        """
        Safely import a module with permanent fallback handling
        
        Args:
            module_name: The module to import
            fallback_value: Value to return if import fails
            alternative_module: Alternative module to try
            
        Returns:
            Imported module or fallback value
        """
        if module_name in self.failed_imports:
            logger.warning(f"Import {module_name} previously failed, using fallback")
            return fallback_value
            
        try:
            # Try primary import
            module = __import__(module_name, fromlist=[''])
            logger.debug(f"Successfully imported {module_name}")
            return module
            
        except ImportError as e:
            logger.warning(f"Failed to import {module_name}: {e}")
            self.failed_imports.add(module_name)
            
            # Try alternative if provided
            if alternative_module:
                try:
                    alternative = __import__(alternative_module, fromlist=[''])
                    logger.info(f"Using alternative module {alternative_module} for {module_name}")
                    self.alternatives[module_name] = alternative_module
                    return alternative
                except ImportError:
                    logger.warning(f"Alternative module {alternative_module} also failed")
            
            return fallback_value
    
    def safe_class_import(self, module_path: str, class_name: str, 
                         fallback_class: Any = None) -> Any:
        """Safely import a specific class from a module"""
        try:
            module = __import__(module_path, fromlist=[class_name])
            return getattr(module, class_name)
        except (ImportError, AttributeError) as e:
            logger.warning(f"Failed to import {class_name} from {module_path}: {e}")
            self.failed_imports.add(f"{module_path}.{class_name}")
            return fallback_class
    
    def register_fallback(self, import_name: str, fallback_handler: Callable):
        """Register a fallback handler for failed imports"""
        self.fallback_handlers[import_name] = fallback_handler
    
    def get_status(self) -> Dict[str, Any]:
        """Get current import status for monitoring"""
        return {
            "failed_imports": list(self.failed_imports),
            "alternatives": self.alternatives.copy(),
            "fallback_handlers": list(self.fallback_handlers.keys())
        }

# Global instance
import_guardian = ImportGuardian()

def safe_import_decorator(fallback_value=None, alternative_module=None):
    """Decorator to make imports safe in functions"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except ImportError as e:
                logger.warning(f"Import failed in {func.__name__}: {e}")
                return fallback_value
        return wrapper
    return decorator
