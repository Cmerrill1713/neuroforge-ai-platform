"""
Security Policy Manager for Agentic LLM Core v0.1

This module implements comprehensive security policies including data redaction,
tool allowlisting, and side effects logging.

Created: 2024-09-24
Status: Draft
"""

from __future__ import annotations

import asyncio
import json
import logging
import re
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from uuid import uuid4

import yaml
from pydantic import BaseModel, Field

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


# ============================================================================
# Data Models
# ============================================================================

class RedactionMode(str, Enum):
    """Redaction modes."""
    STRICT = "strict"
    MODERATE = "moderate"
    LENIENT = "lenient"


class SideEffectMode(str, Enum):
    """Side effect modes."""
    LOG_ONLY = "log-only"
    BLOCK = "block"
    ALLOW_WITH_LOG = "allow-with-log"


class SecurityLevel(str, Enum):
    """Security levels."""
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"


class RedactionPattern(BaseModel):
    """Redaction pattern definition."""
    enabled: bool = Field(True, description="Whether pattern is enabled")
    patterns: List[str] = Field(..., description="Regex patterns to match")
    replacement: str = Field(..., description="Replacement text")
    case_sensitive: bool = Field(False, description="Case sensitivity")


class ToolPermission(BaseModel):
    """Tool permission definition."""
    name: str = Field(..., description="Tool name")
    category: str = Field(..., description="Tool category")
    description: str = Field(..., description="Tool description")
    permissions: List[str] = Field(..., description="Allowed permissions")
    restrictions: List[str] = Field(default_factory=list, description="Restrictions")


class SecurityEvent(BaseModel):
    """Security event record."""
    event_id: str = Field(default_factory=lambda: str(uuid4()), description="Event ID")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Event timestamp")
    event_type: str = Field(..., description="Type of security event")
    severity: str = Field(..., description="Event severity")
    user_id: Optional[str] = Field(None, description="User ID")
    session_id: Optional[str] = Field(None, description="Session ID")
    tool_name: Optional[str] = Field(None, description="Tool name")
    details: Dict[str, Any] = Field(default_factory=dict, description="Event details")
    redacted_data: Optional[str] = Field(None, description="Redacted data if applicable")


class RedactionResult(BaseModel):
    """Redaction result."""
    original_text: str = Field(..., description="Original text")
    redacted_text: str = Field(..., description="Redacted text")
    redaction_count: int = Field(0, description="Number of redactions made")
    redaction_types: List[str] = Field(default_factory=list, description="Types of redactions")
    redaction_details: List[Dict[str, Any]] = Field(default_factory=list, description="Redaction details")


class ToolAccessResult(BaseModel):
    """Tool access result."""
    allowed: bool = Field(..., description="Whether access is allowed")
    reason: str = Field(..., description="Reason for decision")
    restrictions: List[str] = Field(default_factory=list, description="Applied restrictions")
    permissions: List[str] = Field(default_factory=list, description="Granted permissions")


# ============================================================================
# Security Policy Manager
# ============================================================================

class SecurityPolicyManager:
    """Manages security policies and enforcement."""
    
    def __init__(self, config_path: Optional[Union[str, Path]] = None):
        self.logger = logging.getLogger(__name__)
        self.redaction_patterns: Dict[str, RedactionPattern] = {}
        self.allowed_tools: Dict[str, ToolPermission] = {}
        self.blocked_tools: List[str] = []
        self.side_effect_mode = SideEffectMode.LOG_ONLY
        self.security_events: List[SecurityEvent] = []
        
        if config_path:
            self.load_config(config_path)
        else:
            self._load_default_config()
    
    def load_config(self, config_path: Union[str, Path]):
        """Load security policy configuration."""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                if str(config_path).endswith('.yaml') or str(config_path).endswith('.yml'):
                    config_data = yaml.safe_load(f)
                else:
                    config_data = json.load(f)
            
            security_policy = config_data.get('security_policy', {})
            
            # Load redaction patterns
            redaction_config = security_policy.get('redaction', {})
            patterns_config = redaction_config.get('patterns', {})
            for pattern_name, pattern_data in patterns_config.items():
                pattern = RedactionPattern(**pattern_data)
                self.redaction_patterns[pattern_name] = pattern
            
            # Load tool permissions
            tool_security = security_policy.get('tool_security', {})
            allowed_tools_config = tool_security.get('allowed_tools', [])
            for tool_data in allowed_tools_config:
                tool_permission = ToolPermission(**tool_data)
                self.allowed_tools[tool_permission.name] = tool_permission
            
            # Load blocked tools
            blocked_tools_config = tool_security.get('blocked_tools', [])
            self.blocked_tools = [tool['name'] for tool in blocked_tools_config]
            
            # Load side effect mode
            side_effects = security_policy.get('side_effects', {})
            self.side_effect_mode = SideEffectMode(side_effects.get('mode', 'log-only'))
            
            self.logger.info(f"Loaded security policy configuration from {config_path}")
            self.logger.info(f"Loaded {len(self.redaction_patterns)} redaction patterns")
            self.logger.info(f"Loaded {len(self.allowed_tools)} allowed tools")
            self.logger.info(f"Loaded {len(self.blocked_tools)} blocked tools")
            
        except FileNotFoundError:
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        except (json.JSONDecodeError, yaml.YAMLError) as e:
            raise ValueError(f"Invalid configuration format: {e}")
        except Exception as e:
            raise RuntimeError(f"Failed to load configuration: {e}")
    
    def _load_default_config(self):
        """Load default security configuration."""
        # Default redaction patterns
        self.redaction_patterns = {
            "api_keys": RedactionPattern(
                patterns=["api[_-]?key", "apikey", "access[_-]?token"],
                replacement="[REDACTED_API_KEY]"
            ),
            "secrets": RedactionPattern(
                patterns=["password", "secret", "private[_-]?key"],
                replacement="[REDACTED_SECRET]"
            ),
            "emails": RedactionPattern(
                patterns=["[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}"],
                replacement="[REDACTED_EMAIL]"
            )
        }
        
        # Default allowed tools
        self.allowed_tools = {
            "mcp:sql": ToolPermission(
                name="mcp:sql",
                category="mcp",
                description="SQL database operations",
                permissions=["read", "write", "schema_query"],
                restrictions=["no_drop_table", "no_delete_all"]
            ),
            "mcp:fs": ToolPermission(
                name="mcp:fs",
                category="mcp",
                description="File system operations",
                permissions=["read", "write", "list_directory"],
                restrictions=["no_system_files", "no_executable_files"]
            ),
            "lc:retriever": ToolPermission(
                name="lc:retriever",
                category="langchain",
                description="Document retrieval",
                permissions=["search", "retrieve", "embed"],
                restrictions=["no_personal_data", "max_results: 100"]
            )
        }
        
        # Default blocked tools
        self.blocked_tools = ["system:shell", "network:curl", "crypto:encrypt"]
        
        self.side_effect_mode = SideEffectMode.LOG_ONLY
    
    def redact_text(self, text: str, context: Optional[Dict[str, Any]] = None) -> RedactionResult:
        """Redact sensitive information from text."""
        if not text:
            return RedactionResult(original_text=text, redacted_text=text)
        
        redacted_text = text
        redaction_count = 0
        redaction_types = []
        redaction_details = []
        
        # Collect all matches first to avoid double-redaction
        all_matches = []
        
        for pattern_name, pattern in self.redaction_patterns.items():
            if not pattern.enabled:
                continue
            
            for regex_pattern in pattern.patterns:
                try:
                    flags = 0 if pattern.case_sensitive else re.IGNORECASE
                    matches = list(re.finditer(regex_pattern, text, flags))  # Use original text
                    
                    for match in matches:
                        all_matches.append({
                            "pattern_name": pattern_name,
                            "matched_text": match.group(),
                            "start": match.start(),
                            "end": match.end(),
                            "replacement": pattern.replacement,
                            "regex_pattern": regex_pattern,
                            "flags": flags
                        })
                        
                except re.error as e:
                    self.logger.warning(f"Invalid regex pattern '{regex_pattern}' for {pattern_name}: {e}")
                    continue
        
        # Sort matches by start position (descending) to redact from end to beginning
        all_matches.sort(key=lambda x: x["start"], reverse=True)
        
        # Apply redactions from end to beginning to avoid position shifts
        for match_info in all_matches:
            redaction_count += 1
            if match_info["pattern_name"] not in redaction_types:
                redaction_types.append(match_info["pattern_name"])
            
            redaction_details.append({
                "pattern_name": match_info["pattern_name"],
                "matched_text": match_info["matched_text"],
                "start": match_info["start"],
                "end": match_info["end"],
                "replacement": match_info["replacement"]
            })
            
            # Replace the matched text
            redacted_text = (redacted_text[:match_info["start"]] + 
                           match_info["replacement"] + 
                           redacted_text[match_info["end"]:])
        
        # Log redaction event if any redactions were made
        if redaction_count > 0:
            self._log_security_event(
                event_type="data_redaction",
                severity="INFO",
                details={
                    "redaction_count": redaction_count,
                    "redaction_types": redaction_types,
                    "context": context
                }
            )
        
        return RedactionResult(
            original_text=text,
            redacted_text=redacted_text,
            redaction_count=redaction_count,
            redaction_types=redaction_types,
            redaction_details=redaction_details
        )
    
    def check_tool_access(self, tool_name: str, user_context: Optional[Dict[str, Any]] = None) -> ToolAccessResult:
        """Check if tool access is allowed."""
        # Check if tool is explicitly blocked
        if tool_name in self.blocked_tools:
            self._log_security_event(
                event_type="tool_access_denied",
                severity="WARNING",
                tool_name=tool_name,
                details={"reason": "Tool is in blocked list", "user_context": user_context}
            )
            return ToolAccessResult(
                allowed=False,
                reason=f"Tool '{tool_name}' is blocked by security policy",
                restrictions=["blocked_tool"]
            )
        
        # Check if tool is in allowlist
        if tool_name not in self.allowed_tools:
            self._log_security_event(
                event_type="tool_access_denied",
                severity="WARNING",
                tool_name=tool_name,
                details={"reason": "Tool not in allowlist", "user_context": user_context}
            )
            return ToolAccessResult(
                allowed=False,
                reason=f"Tool '{tool_name}' is not in the allowed tools list",
                restrictions=["not_allowlisted"]
            )
        
        # Tool is allowed
        tool_permission = self.allowed_tools[tool_name]
        self._log_security_event(
            event_type="tool_access_granted",
            severity="INFO",
            tool_name=tool_name,
            details={
                "permissions": tool_permission.permissions,
                "restrictions": tool_permission.restrictions,
                "user_context": user_context
            }
        )
        
        return ToolAccessResult(
            allowed=True,
            reason=f"Tool '{tool_name}' is allowed",
            permissions=tool_permission.permissions,
            restrictions=tool_permission.restrictions
        )
    
    def log_side_effect(self, effect_type: str, details: Dict[str, Any], user_context: Optional[Dict[str, Any]] = None):
        """Log side effects based on policy."""
        severity_map = {
            "data_access": "INFO",
            "data_modification": "WARNING",
            "external_communication": "WARNING",
            "system_changes": "ERROR",
            "security_events": "ERROR"
        }
        
        severity = severity_map.get(effect_type, "INFO")
        
        # Redact sensitive data in details
        redacted_details = {}
        for key, value in details.items():
            if isinstance(value, str):
                redaction_result = self.redact_text(value)
                redacted_details[key] = redaction_result.redacted_text
            else:
                redacted_details[key] = value
        
        self._log_security_event(
            event_type=f"side_effect_{effect_type}",
            severity=severity,
            details={
                "effect_type": effect_type,
                "original_details": details,
                "redacted_details": redacted_details,
                "user_context": user_context
            }
        )
    
    def _log_security_event(self, event_type: str, severity: str, user_id: Optional[str] = None,
                           session_id: Optional[str] = None, tool_name: Optional[str] = None,
                           details: Optional[Dict[str, Any]] = None):
        """Log a security event."""
        event = SecurityEvent(
            event_type=event_type,
            severity=severity,
            user_id=user_id,
            session_id=session_id,
            tool_name=tool_name,
            details=details or {}
        )
        
        self.security_events.append(event)
        
        # Log to console/file based on severity
        if severity == "ERROR":
            self.logger.error(f"Security Event [{event_type}]: {details}")
        elif severity == "WARNING":
            self.logger.warning(f"Security Event [{event_type}]: {details}")
        else:
            self.logger.info(f"Security Event [{event_type}]: {details}")
    
    def get_security_summary(self) -> Dict[str, Any]:
        """Get security policy summary."""
        return {
            "redaction_patterns": len(self.redaction_patterns),
            "allowed_tools": len(self.allowed_tools),
            "blocked_tools": len(self.blocked_tools),
            "side_effect_mode": self.side_effect_mode.value,
            "security_events_count": len(self.security_events),
            "recent_events": self.security_events[-10:] if self.security_events else []
        }
    
    def print_security_summary(self):
        """Print security policy summary."""
        print("\n" + "="*80)
        print("SECURITY POLICY SUMMARY")
        print("="*80)
        
        print(f"\n🔒 Redaction Patterns ({len(self.redaction_patterns)}):")
        for pattern_name, pattern in self.redaction_patterns.items():
            status_emoji = "✅" if pattern.enabled else "❌"
            print(f"   {status_emoji} {pattern_name}")
            print(f"     Patterns: {len(pattern.patterns)} regex patterns")
            print(f"     Replacement: {pattern.replacement}")
            print(f"     Case Sensitive: {'Yes' if pattern.case_sensitive else 'No'}")
        
        print(f"\n🛠️ Allowed Tools ({len(self.allowed_tools)}):")
        for tool_name, tool_permission in self.allowed_tools.items():
            category_emoji = {
                "mcp": "🔌",
                "langchain": "🔗",
                "utility": "⚙️",
                "file_system": "📁",
                "database": "🗄️"
            }.get(tool_permission.category, "🔧")
            
            print(f"   {category_emoji} {tool_name}")
            print(f"     Category: {tool_permission.category}")
            print(f"     Permissions: {', '.join(tool_permission.permissions)}")
            if tool_permission.restrictions:
                print(f"     Restrictions: {', '.join(tool_permission.restrictions)}")
        
        print(f"\n🚫 Blocked Tools ({len(self.blocked_tools)}):")
        for tool_name in self.blocked_tools:
            print(f"   ❌ {tool_name}")
        
        print(f"\n📊 Side Effects Mode: {self.side_effect_mode.value}")
        
        print(f"\n📈 Security Events: {len(self.security_events)} total")
        if self.security_events:
            recent_events = self.security_events[-5:]
            print("   Recent events:")
            for event in recent_events:
                severity_emoji = {
                    "ERROR": "🔴",
                    "WARNING": "🟡",
                    "INFO": "🔵"
                }.get(event.severity, "⚪")
                print(f"     {severity_emoji} {event.event_type} ({event.severity})")


# ============================================================================
# Main Function
# ============================================================================

async def main():
    """Main function for command-line usage."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Security Policy Manager")
    parser.add_argument("--config", help="Path to security policy configuration file")
    parser.add_argument("--test-redaction", help="Test redaction with sample text")
    parser.add_argument("--test-tool", help="Test tool access for specific tool")
    parser.add_argument("--show-policy", action="store_true", help="Show security policy summary")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    try:
        # Create security policy manager
        manager = SecurityPolicyManager(args.config)
        
        if args.show_policy:
            manager.print_security_summary()
        
        if args.test_redaction:
            # Test redaction
            result = manager.redact_text(args.test_redaction)
            print("\n🔍 Redaction Test:")
            print(f"   Original: {result.original_text}")
            print(f"   Redacted: {result.redacted_text}")
            print(f"   Redactions: {result.redaction_count}")
            print(f"   Types: {', '.join(result.redaction_types)}")
        
        if args.test_tool:
            # Test tool access
            result = manager.check_tool_access(args.test_tool)
            print("\n🛠️ Tool Access Test:")
            print(f"   Tool: {args.test_tool}")
            print(f"   Allowed: {'✅' if result.allowed else '❌'}")
            print(f"   Reason: {result.reason}")
            if result.permissions:
                print(f"   Permissions: {', '.join(result.permissions)}")
            if result.restrictions:
                print(f"   Restrictions: {', '.join(result.restrictions)}")
        
    except Exception as e:
        logger.error(f"Security policy manager error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(asyncio.run(main()))
