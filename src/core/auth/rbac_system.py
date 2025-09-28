"""
Role-Based Access Control (RBAC) System for Agentic LLM Core v2.0

This module provides comprehensive RBAC capabilities including permissions,
roles, resource access control, and audit logging.

Created: 2024-09-28
Status: Production Ready
"""

import asyncio
import logging
import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Set

from pydantic import BaseModel, Field

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


# ============================================================================
# Data Models
# ============================================================================

class Permission(str, Enum):
    """System permissions."""
    # User Management
    USER_CREATE = "user:create"
    USER_READ = "user:read"
    USER_UPDATE = "user:update"
    USER_DELETE = "user:delete"
    USER_LIST = "user:list"
    
    # Agent Management
    AGENT_CREATE = "agent:create"
    AGENT_READ = "agent:read"
    AGENT_UPDATE = "agent:update"
    AGENT_DELETE = "agent:delete"
    AGENT_EXECUTE = "agent:execute"
    AGENT_LIST = "agent:list"
    
    # Model Management
    MODEL_CREATE = "model:create"
    MODEL_READ = "model:read"
    MODEL_UPDATE = "model:update"
    MODEL_DELETE = "model:delete"
    MODEL_DEPLOY = "model:deploy"
    MODEL_LIST = "model:list"
    
    # Knowledge Base
    KB_CREATE = "kb:create"
    KB_READ = "kb:read"
    KB_UPDATE = "kb:update"
    KB_DELETE = "kb:delete"
    KB_SEARCH = "kb:search"
    KB_LIST = "kb:list"
    
    # Monitoring
    MONITOR_READ = "monitor:read"
    MONITOR_ALERTS = "monitor:alerts"
    MONITOR_METRICS = "monitor:metrics"
    MONITOR_LOGS = "monitor:logs"
    
    # System Administration
    SYSTEM_CONFIG = "system:config"
    SYSTEM_BACKUP = "system:backup"
    SYSTEM_RESTORE = "system:restore"
    SYSTEM_LOGS = "system:logs"
    SYSTEM_MAINTENANCE = "system:maintenance"
    
    # API Access
    API_READ = "api:read"
    API_WRITE = "api:write"
    API_ADMIN = "api:admin"
    
    # Chat and Interaction
    CHAT_SEND = "chat:send"
    CHAT_READ = "chat:read"
    CHAT_HISTORY = "chat:history"
    CHAT_DELETE = "chat:delete"
    
    # File Operations
    FILE_UPLOAD = "file:upload"
    FILE_DOWNLOAD = "file:download"
    FILE_DELETE = "file:delete"
    FILE_LIST = "file:list"


class ResourceType(str, Enum):
    """Resource types in the system."""
    USER = "user"
    AGENT = "agent"
    MODEL = "model"
    KNOWLEDGE_BASE = "knowledge_base"
    CONVERSATION = "conversation"
    FILE = "file"
    SYSTEM = "system"
    API = "api"


class ActionType(str, Enum):
    """Action types for audit logging."""
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    EXECUTE = "execute"
    LOGIN = "login"
    LOGOUT = "logout"
    ACCESS_DENIED = "access_denied"


class Role(BaseModel):
    """Role definition."""
    role_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str = Field(..., description="Role name")
    description: str = Field(..., description="Role description")
    permissions: Set[Permission] = Field(default_factory=set, description="Role permissions")
    is_system_role: bool = Field(False, description="System-defined role")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = Field(default_factory=dict)


class Resource(BaseModel):
    """Resource definition."""
    resource_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    resource_type: ResourceType = Field(..., description="Type of resource")
    resource_name: str = Field(..., description="Resource name")
    owner_id: Optional[str] = Field(None, description="Resource owner user ID")
    permissions: Dict[str, Set[Permission]] = Field(default_factory=dict, description="Resource-specific permissions")
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class AccessRule(BaseModel):
    """Access control rule."""
    rule_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    role_id: str = Field(..., description="Role ID")
    resource_type: ResourceType = Field(..., description="Resource type")
    permissions: Set[Permission] = Field(default_factory=set, description="Allowed permissions")
    conditions: Dict[str, Any] = Field(default_factory=dict, description="Access conditions")
    is_active: bool = Field(True, description="Rule active status")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class AuditLog(BaseModel):
    """Audit log entry."""
    log_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = Field(..., description="User who performed the action")
    action: ActionType = Field(..., description="Action performed")
    resource_type: ResourceType = Field(..., description="Resource type")
    resource_id: Optional[str] = Field(None, description="Resource ID")
    resource_name: Optional[str] = Field(None, description="Resource name")
    permission: Optional[Permission] = Field(None, description="Permission used")
    success: bool = Field(..., description="Action success status")
    details: Dict[str, Any] = Field(default_factory=dict, description="Additional details")
    ip_address: Optional[str] = Field(None, description="Client IP address")
    user_agent: Optional[str] = Field(None, description="Client user agent")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class AccessRequest(BaseModel):
    """Access request."""
    user_id: str = Field(..., description="User requesting access")
    resource_type: ResourceType = Field(..., description="Resource type")
    resource_id: Optional[str] = Field(None, description="Resource ID")
    permission: Permission = Field(..., description="Requested permission")
    context: Dict[str, Any] = Field(default_factory=dict, description="Request context")


class AccessDecision(BaseModel):
    """Access decision result."""
    granted: bool = Field(..., description="Access granted")
    reason: str = Field(..., description="Decision reason")
    required_permissions: Set[Permission] = Field(default_factory=set, description="Required permissions")
    user_permissions: Set[Permission] = Field(default_factory=set, description="User permissions")
    applicable_rules: List[str] = Field(default_factory=list, description="Applicable access rules")


# ============================================================================
# RBAC System
# ============================================================================

class RBACSystem:
    """Role-Based Access Control system."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.roles: Dict[str, Role] = {}
        self.resources: Dict[str, Resource] = {}
        self.access_rules: Dict[str, AccessRule] = {}
        self.audit_logs: List[AuditLog] = []
        self._initialize_default_roles()
    
    def _initialize_default_roles(self):
        """Initialize default system roles."""
        # Admin role - full access
        admin_role = Role(
            name="admin",
            description="System Administrator - Full access to all resources",
            permissions={
                Permission.USER_CREATE, Permission.USER_READ, Permission.USER_UPDATE, Permission.USER_DELETE, Permission.USER_LIST,
                Permission.AGENT_CREATE, Permission.AGENT_READ, Permission.AGENT_UPDATE, Permission.AGENT_DELETE, Permission.AGENT_EXECUTE, Permission.AGENT_LIST,
                Permission.MODEL_CREATE, Permission.MODEL_READ, Permission.MODEL_UPDATE, Permission.MODEL_DELETE, Permission.MODEL_DEPLOY, Permission.MODEL_LIST,
                Permission.KB_CREATE, Permission.KB_READ, Permission.KB_UPDATE, Permission.KB_DELETE, Permission.KB_SEARCH, Permission.KB_LIST,
                Permission.MONITOR_READ, Permission.MONITOR_ALERTS, Permission.MONITOR_METRICS, Permission.MONITOR_LOGS,
                Permission.SYSTEM_CONFIG, Permission.SYSTEM_BACKUP, Permission.SYSTEM_RESTORE, Permission.SYSTEM_LOGS, Permission.SYSTEM_MAINTENANCE,
                Permission.API_READ, Permission.API_WRITE, Permission.API_ADMIN,
                Permission.CHAT_SEND, Permission.CHAT_READ, Permission.CHAT_HISTORY, Permission.CHAT_DELETE,
                Permission.FILE_UPLOAD, Permission.FILE_DOWNLOAD, Permission.FILE_DELETE, Permission.FILE_LIST
            },
            is_system_role=True
        )
        self.roles[admin_role.role_id] = admin_role
        
        # Developer role - development and testing access
        developer_role = Role(
            name="developer",
            description="Developer - Access to development and testing resources",
            permissions={
                Permission.USER_READ, Permission.USER_LIST,
                Permission.AGENT_CREATE, Permission.AGENT_READ, Permission.AGENT_UPDATE, Permission.AGENT_EXECUTE, Permission.AGENT_LIST,
                Permission.MODEL_CREATE, Permission.MODEL_READ, Permission.MODEL_UPDATE, Permission.MODEL_DEPLOY, Permission.MODEL_LIST,
                Permission.KB_CREATE, Permission.KB_READ, Permission.KB_UPDATE, Permission.KB_SEARCH, Permission.KB_LIST,
                Permission.MONITOR_READ, Permission.MONITOR_METRICS,
                Permission.API_READ, Permission.API_WRITE,
                Permission.CHAT_SEND, Permission.CHAT_READ, Permission.CHAT_HISTORY,
                Permission.FILE_UPLOAD, Permission.FILE_DOWNLOAD, Permission.FILE_LIST
            },
            is_system_role=True
        )
        self.roles[developer_role.role_id] = developer_role
        
        # User role - basic user access
        user_role = Role(
            name="user",
            description="Regular User - Basic access to user features",
            permissions={
                Permission.AGENT_READ, Permission.AGENT_EXECUTE, Permission.AGENT_LIST,
                Permission.MODEL_READ, Permission.MODEL_LIST,
                Permission.KB_READ, Permission.KB_SEARCH, Permission.KB_LIST,
                Permission.API_READ,
                Permission.CHAT_SEND, Permission.CHAT_READ, Permission.CHAT_HISTORY,
                Permission.FILE_UPLOAD, Permission.FILE_DOWNLOAD, Permission.FILE_LIST
            },
            is_system_role=True
        )
        self.roles[user_role.role_id] = user_role
        
        # Readonly role - read-only access
        readonly_role = Role(
            name="readonly",
            description="Read-Only User - Limited read access",
            permissions={
                Permission.AGENT_READ, Permission.AGENT_LIST,
                Permission.MODEL_READ, Permission.MODEL_LIST,
                Permission.KB_READ, Permission.KB_LIST,
                Permission.API_READ,
                Permission.CHAT_READ, Permission.CHAT_HISTORY,
                Permission.FILE_LIST
            },
            is_system_role=True
        )
        self.roles[readonly_role.role_id] = readonly_role
        
        # Analyst role - analysis and monitoring access
        analyst_role = Role(
            name="analyst",
            description="Analyst - Access to analysis and monitoring tools",
            permissions={
                Permission.USER_READ, Permission.USER_LIST,
                Permission.AGENT_READ, Permission.AGENT_LIST,
                Permission.MODEL_READ, Permission.MODEL_LIST,
                Permission.KB_READ, Permission.KB_SEARCH, Permission.KB_LIST,
                Permission.MONITOR_READ, Permission.MONITOR_METRICS, Permission.MONITOR_LOGS,
                Permission.API_READ,
                Permission.CHAT_READ, Permission.CHAT_HISTORY,
                Permission.FILE_DOWNLOAD, Permission.FILE_LIST
            },
            is_system_role=True
        )
        self.roles[analyst_role.role_id] = analyst_role
        
        self.logger.info(f"Initialized {len(self.roles)} default roles")
    
    async def create_role(self, name: str, description: str, permissions: Set[Permission], metadata: Optional[Dict[str, Any]] = None) -> Role:
        """Create a new role."""
        # Check if role name already exists
        for role in self.roles.values():
            if role.name == name:
                raise ValueError(f"Role '{name}' already exists")
        
        role = Role(
            name=name,
            description=description,
            permissions=permissions,
            metadata=metadata or {}
        )
        
        self.roles[role.role_id] = role
        self.logger.info(f"Created role: {name} with {len(permissions)} permissions")
        return role
    
    async def get_role(self, role_id: str) -> Optional[Role]:
        """Get role by ID."""
        return self.roles.get(role_id)
    
    async def get_role_by_name(self, name: str) -> Optional[Role]:
        """Get role by name."""
        for role in self.roles.values():
            if role.name == name:
                return role
        return None
    
    async def update_role(self, role_id: str, permissions: Optional[Set[Permission]] = None, description: Optional[str] = None) -> Optional[Role]:
        """Update role permissions or description."""
        role = self.roles.get(role_id)
        if not role:
            return None
        
        if role.is_system_role:
            raise ValueError("Cannot modify system roles")
        
        if permissions is not None:
            role.permissions = permissions
        
        if description is not None:
            role.description = description
        
        role.updated_at = datetime.now(timezone.utc)
        
        self.logger.info(f"Updated role: {role.name}")
        return role
    
    async def delete_role(self, role_id: str) -> bool:
        """Delete a role."""
        role = self.roles.get(role_id)
        if not role:
            return False
        
        if role.is_system_role:
            raise ValueError("Cannot delete system roles")
        
        del self.roles[role_id]
        self.logger.info(f"Deleted role: {role.name}")
        return True
    
    async def create_resource(self, resource_type: ResourceType, resource_name: str, owner_id: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None) -> Resource:
        """Create a new resource."""
        resource = Resource(
            resource_type=resource_type,
            resource_name=resource_name,
            owner_id=owner_id,
            metadata=metadata or {}
        )
        
        self.resources[resource.resource_id] = resource
        self.logger.info(f"Created resource: {resource_name} ({resource_type.value})")
        return resource
    
    async def get_resource(self, resource_id: str) -> Optional[Resource]:
        """Get resource by ID."""
        return self.resources.get(resource_id)
    
    async def update_resource_permissions(self, resource_id: str, permissions: Dict[str, Set[Permission]]) -> Optional[Resource]:
        """Update resource-specific permissions."""
        resource = self.resources.get(resource_id)
        if not resource:
            return None
        
        resource.permissions = permissions
        resource.updated_at = datetime.now(timezone.utc)
        
        self.logger.info(f"Updated permissions for resource: {resource.resource_name}")
        return resource
    
    async def delete_resource(self, resource_id: str) -> bool:
        """Delete a resource."""
        if resource_id in self.resources:
            resource = self.resources[resource_id]
            del self.resources[resource_id]
            self.logger.info(f"Deleted resource: {resource.resource_name}")
            return True
        return False
    
    async def create_access_rule(self, role_id: str, resource_type: ResourceType, permissions: Set[Permission], conditions: Optional[Dict[str, Any]] = None) -> AccessRule:
        """Create an access control rule."""
        rule = AccessRule(
            role_id=role_id,
            resource_type=resource_type,
            permissions=permissions,
            conditions=conditions or {}
        )
        
        self.access_rules[rule.rule_id] = rule
        self.logger.info(f"Created access rule for role {role_id} on {resource_type.value}")
        return rule
    
    async def check_access(self, request: AccessRequest, user_role: Role) -> AccessDecision:
        """Check if user has access to a resource."""
        # Check if user role has the required permission
        if request.permission not in user_role.permissions:
            await self._log_access_attempt(request, False, "Permission not in user role")
            return AccessDecision(
                granted=False,
                reason="User role does not have required permission",
                required_permissions={request.permission},
                user_permissions=user_role.permissions
            )
        
        # Check resource-specific permissions if resource exists
        if request.resource_id:
            resource = await self.get_resource(request.resource_id)
            if resource and resource.permissions:
                # Check if resource has specific permission requirements
                resource_permissions = resource.permissions.get(user_role.name, set())
                if resource_permissions and request.permission not in resource_permissions:
                    await self._log_access_attempt(request, False, "Resource-specific permission denied")
                    return AccessDecision(
                        granted=False,
                        reason="Resource-specific permission denied",
                        required_permissions=resource_permissions,
                        user_permissions=user_role.permissions
                    )
        
        # Check access rules
        applicable_rules = []
        for rule in self.access_rules.values():
            if (rule.role_id == user_role.role_id and 
                rule.resource_type == request.resource_type and 
                rule.is_active and
                request.permission in rule.permissions):
                applicable_rules.append(rule.rule_id)
        
        # Log successful access
        await self._log_access_attempt(request, True, "Access granted")
        
        return AccessDecision(
            granted=True,
            reason="Access granted",
            required_permissions={request.permission},
            user_permissions=user_role.permissions,
            applicable_rules=applicable_rules
        )
    
    async def _log_access_attempt(self, request: AccessRequest, success: bool, reason: str):
        """Log access attempt for audit."""
        log_entry = AuditLog(
            user_id=request.user_id,
            action=ActionType.ACCESS_DENIED if not success else ActionType.READ,
            resource_type=request.resource_type,
            resource_id=request.resource_id,
            permission=request.permission,
            success=success,
            details={
                "reason": reason,
                "context": request.context
            }
        )
        
        self.audit_logs.append(log_entry)
        
        # Keep only last 10000 audit logs
        if len(self.audit_logs) > 10000:
            self.audit_logs = self.audit_logs[-10000:]
    
    async def log_action(self, user_id: str, action: ActionType, resource_type: ResourceType, resource_id: Optional[str] = None, resource_name: Optional[str] = None, permission: Optional[Permission] = None, success: bool = True, details: Optional[Dict[str, Any]] = None, ip_address: Optional[str] = None, user_agent: Optional[str] = None):
        """Log a user action for audit."""
        log_entry = AuditLog(
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            resource_name=resource_name,
            permission=permission,
            success=success,
            details=details or {},
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        self.audit_logs.append(log_entry)
        
        # Keep only last 10000 audit logs
        if len(self.audit_logs) > 10000:
            self.audit_logs = self.audit_logs[-10000:]
    
    async def get_audit_logs(self, user_id: Optional[str] = None, resource_type: Optional[ResourceType] = None, action: Optional[ActionType] = None, limit: int = 100) -> List[AuditLog]:
        """Get audit logs with optional filtering."""
        logs = self.audit_logs
        
        if user_id:
            logs = [log for log in logs if log.user_id == user_id]
        
        if resource_type:
            logs = [log for log in logs if log.resource_type == resource_type]
        
        if action:
            logs = [log for log in logs if log.action == action]
        
        # Sort by timestamp (newest first)
        logs.sort(key=lambda x: x.timestamp, reverse=True)
        
        return logs[:limit]
    
    async def get_user_permissions(self, user_role: Role, resource_type: Optional[ResourceType] = None) -> Set[Permission]:
        """Get user permissions, optionally filtered by resource type."""
        permissions = user_role.permissions.copy()
        
        if resource_type:
            # Filter permissions by resource type
            resource_permissions = {
                Permission.USER_CREATE, Permission.USER_READ, Permission.USER_UPDATE, Permission.USER_DELETE, Permission.USER_LIST
            } if resource_type == ResourceType.USER else set()
            
            if resource_type == ResourceType.AGENT:
                resource_permissions = {
                    Permission.AGENT_CREATE, Permission.AGENT_READ, Permission.AGENT_UPDATE, Permission.AGENT_DELETE, Permission.AGENT_EXECUTE, Permission.AGENT_LIST
                }
            elif resource_type == ResourceType.MODEL:
                resource_permissions = {
                    Permission.MODEL_CREATE, Permission.MODEL_READ, Permission.MODEL_UPDATE, Permission.MODEL_DELETE, Permission.MODEL_DEPLOY, Permission.MODEL_LIST
                }
            elif resource_type == ResourceType.KNOWLEDGE_BASE:
                resource_permissions = {
                    Permission.KB_CREATE, Permission.KB_READ, Permission.KB_UPDATE, Permission.KB_DELETE, Permission.KB_SEARCH, Permission.KB_LIST
                }
            elif resource_type == ResourceType.CONVERSATION:
                resource_permissions = {
                    Permission.CHAT_SEND, Permission.CHAT_READ, Permission.CHAT_HISTORY, Permission.CHAT_DELETE
                }
            elif resource_type == ResourceType.FILE:
                resource_permissions = {
                    Permission.FILE_UPLOAD, Permission.FILE_DOWNLOAD, Permission.FILE_DELETE, Permission.FILE_LIST
                }
            elif resource_type == ResourceType.SYSTEM:
                resource_permissions = {
                    Permission.SYSTEM_CONFIG, Permission.SYSTEM_BACKUP, Permission.SYSTEM_RESTORE, Permission.SYSTEM_LOGS, Permission.SYSTEM_MAINTENANCE
                }
            elif resource_type == ResourceType.API:
                resource_permissions = {
                    Permission.API_READ, Permission.API_WRITE, Permission.API_ADMIN
                }
            
            permissions = permissions.intersection(resource_permissions)
        
        return permissions
    
    async def get_system_stats(self) -> Dict[str, Any]:
        """Get RBAC system statistics."""
        return {
            "total_roles": len(self.roles),
            "total_resources": len(self.resources),
            "total_access_rules": len(self.access_rules),
            "total_audit_logs": len(self.audit_logs),
            "system_roles": len([r for r in self.roles.values() if r.is_system_role]),
            "custom_roles": len([r for r in self.roles.values() if not r.is_system_role])
        }


# ============================================================================
# Main Function
# ============================================================================

async def main():
    """Main function for testing the RBAC system."""
    import argparse
    
    parser = argparse.ArgumentParser(description="RBAC System")
    parser.add_argument("--action", choices=["check", "create_role", "list_roles", "audit", "stats"], required=True)
    parser.add_argument("--user_id", help="User ID")
    parser.add_argument("--role", help="Role name")
    parser.add_argument("--permission", help="Permission to check")
    parser.add_argument("--resource_type", help="Resource type")
    parser.add_argument("--resource_id", help="Resource ID")
    
    args = parser.parse_args()
    
    try:
        rbac = RBACSystem()
        
        if args.action == "check":
            if not all([args.user_id, args.role, args.permission, args.resource_type]):
                print("Error: --user_id, --role, --permission, and --resource_type are required for check action")
                return 1
            
            # Get role
            role = await rbac.get_role_by_name(args.role)
            if not role:
                print(f"❌ Role '{args.role}' not found")
                return 1
            
            # Create access request
            request = AccessRequest(
                user_id=args.user_id,
                resource_type=ResourceType(args.resource_type),
                resource_id=args.resource_id,
                permission=Permission(args.permission)
            )
            
            # Check access
            decision = await rbac.check_access(request, role)
            
            print("🔐 Access Check Result:")
            print(f"   Granted: {'✅ Yes' if decision.granted else '❌ No'}")
            print(f"   Reason: {decision.reason}")
            print(f"   Required: {', '.join([p.value for p in decision.required_permissions])}")
            print(f"   User Has: {', '.join([p.value for p in decision.user_permissions])}")
            
        elif args.action == "create_role":
            if not args.role:
                print("Error: --role is required for create_role action")
                return 1
            
            # Create a custom role with basic permissions
            permissions = {
                Permission.USER_READ, Permission.USER_LIST,
                Permission.AGENT_READ, Permission.AGENT_LIST,
                Permission.API_READ
            }
            
            role = await rbac.create_role(
                name=args.role,
                description=f"Custom role: {args.role}",
                permissions=permissions
            )
            
            print(f"✅ Created role: {role.name} ({role.role_id})")
            print(f"   Permissions: {', '.join([p.value for p in role.permissions])}")
            
        elif args.action == "list_roles":
            print("📋 Available Roles:")
            for role in rbac.roles.values():
                print(f"   - {role.name}: {role.description}")
                print(f"     Permissions: {len(role.permissions)}")
                print(f"     System Role: {'Yes' if role.is_system_role else 'No'}")
                print()
                
        elif args.action == "audit":
            logs = await rbac.get_audit_logs(limit=10)
            print(f"📊 Recent Audit Logs ({len(logs)}):")
            for log in logs:
                status = "✅" if log.success else "❌"
                print(f"   {status} {log.user_id} - {log.action.value} - {log.resource_type.value} - {log.timestamp}")
                
        elif args.action == "stats":
            stats = await rbac.get_system_stats()
            print("📊 RBAC System Statistics:")
            for key, value in stats.items():
                print(f"   {key}: {value}")
        
        return 0
        
    except Exception as e:
        logger.error(f"RBAC operation failed: {e}")
        return 1


if __name__ == "__main__":
    exit(asyncio.run(main()))
