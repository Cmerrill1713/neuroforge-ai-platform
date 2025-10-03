#!/usr/bin/env python3
"""
Security Sanitizer for NeuroForge
Provides input sanitization and security validation
"""

import re
import html
import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class SanitizedText:
    """Result of text sanitization"""
    text: str
    flags: List[str]  # Security flags/warnings
    original_length: int
    sanitized_length: int

class InputSanitizer:
    """
    Comprehensive input sanitizer for user-generated content
    """

    def __init__(self):
        # Dangerous patterns to detect
        self.dangerous_patterns = [
            r'<script[^>]*>.*?</script>',  # Script tags
            r'javascript:',                # JavaScript URLs
            r'on\w+\s*=',                  # Event handlers
            r'<iframe[^>]*>.*?</iframe>', # Iframes
            r'<object[^>]*>.*?</object>', # Object/embed tags
            r'<embed[^>]*>',              # Embed tags
            r'eval\s*\(',                 # eval() calls
            r'document\.',                # DOM manipulation
            r'window\.',                  # Window object access
        ]

        # Suspicious patterns to flag
        self.suspicious_patterns = [
            r'\b(?:SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER)\b',  # SQL keywords
            r'<[^>]*>',                    # Any HTML tags
            r'[\x00-\x1F\x7F-\x9F]',     # Control characters
            r'(?:http|https|ftp)://[^\s]*', # URLs
        ]

    def sanitize_user_text(self, text: str) -> SanitizedText:
        """
        Sanitize user input text for security

        Args:
            text: Raw user input

        Returns:
            SanitizedText object with cleaned text and security flags
        """
        if not isinstance(text, str):
            text = str(text)

        original_length = len(text)
        flags = []

        # Basic sanitization
        sanitized = text.strip()

        # HTML escape
        sanitized = html.escape(sanitized)

        # Remove dangerous patterns
        for pattern in self.dangerous_patterns:
            if re.search(pattern, sanitized, re.IGNORECASE | re.DOTALL):
                flags.append("dangerous_content_detected")
                # Remove the dangerous content
                sanitized = re.sub(pattern, "[REMOVED]", sanitized, flags=re.IGNORECASE | re.DOTALL)

        # Check for suspicious patterns (don't remove, just flag)
        for pattern in self.suspicious_patterns:
            if re.search(pattern, sanitized, re.IGNORECASE):
                flags.append("suspicious_content_detected")

        # Length limits
        max_length = 10000  # Reasonable limit
        if len(sanitized) > max_length:
            sanitized = sanitized[:max_length]
            flags.append("content_truncated")

        # Remove excessive whitespace
        sanitized = re.sub(r'\s+', ' ', sanitized)

        sanitized_length = len(sanitized)

        # Log security events
        if flags:
            logger.warning(f"Security flags detected in user input: {flags}")

        return SanitizedText(
            text=sanitized,
            flags=flags,
            original_length=original_length,
            sanitized_length=sanitized_length
        )

class ContentValidator:
    """
    Advanced content validation for AI interactions
    """

    def __init__(self):
        self.sanitizer = InputSanitizer()

    def validate_prompt(self, prompt: str) -> Dict[str, Any]:
        """
        Validate a prompt for AI generation

        Args:
            prompt: The prompt to validate

        Returns:
            Validation results
        """
        sanitized = self.sanitizer.sanitize_user_text(prompt)

        result = {
            "valid": True,
            "sanitized_prompt": sanitized.text,
            "warnings": sanitized.flags,
            "original_length": sanitized.original_length,
            "sanitized_length": sanitized.sanitized_length
        }

        # Check for critical issues
        critical_flags = ["dangerous_content_detected"]
        if any(flag in sanitized.flags for flag in critical_flags):
            result["valid"] = False
            result["error"] = "Prompt contains dangerous content"

        return result

    def validate_response(self, response: str) -> Dict[str, Any]:
        """
        Validate an AI response for output safety

        Args:
            response: The response to validate

        Returns:
            Validation results
        """
        # For responses, we're mainly checking for completeness and safety
        result = {
            "valid": True,
            "response": response,
            "length": len(response),
            "warnings": []
        }

        # Basic checks
        if len(response.strip()) == 0:
            result["valid"] = False
            result["error"] = "Empty response"

        # Check for incomplete responses (common with local models)
        if response.endswith(("...", "…", "```", ":", "-")):
            result["warnings"].append("response_appears_incomplete")

        return result

# Global instances
sanitizer = InputSanitizer()
validator = ContentValidator()

# Convenience functions
def sanitize_user_text(text: str) -> SanitizedText:
    """Convenience function for text sanitization"""
    return sanitizer.sanitize_user_text(text)

def validate_user_prompt(prompt: str) -> Dict[str, Any]:
    """Convenience function for prompt validation"""
    return validator.validate_prompt(prompt)

def validate_ai_response(response: str) -> Dict[str, Any]:
    """Convenience function for response validation"""
    return validator.validate_response(response)

# Export main classes and functions
__all__ = [
    "SanitizedText",
    "InputSanitizer",
    "ContentValidator",
    "sanitize_user_text",
    "validate_user_prompt",
    "validate_ai_response"
]
