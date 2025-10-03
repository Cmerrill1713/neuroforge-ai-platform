"""
Secure Authentication Service - JWT-based authentication
"""

import logging
from typing import Optional, Dict, Any
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class SecureAuthService:
    """Secure authentication service with JWT tokens."""

    def __init__(self, secret_key: str = "dev-secret-key"):
        """Initialize the auth service."""
        logger.info("🚀 Initializing Secure Auth Service")
        self.secret_key = secret_key
        self.users = {
            "admin": {"password": "admin123", "role": "admin"},
            "user": {"password": "user123", "role": "user"}
        }
        logger.info("✅ Auth service ready")

    def authenticate_user(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """Authenticate a user."""
        user = self.users.get(username)
        if user and user["password"] == password:
            return {
                "username": username,
                "role": user["role"],
                "authenticated": True
            }
        return None

    def create_token(self, user_data: Dict[str, Any]) -> str:
        """Create a JWT token (simplified for demo)."""
        # In production, use proper JWT library
        import base64
        import json

        payload = {
            "user": user_data["username"],
            "role": user_data["role"],
            "exp": (datetime.now() + timedelta(hours=1)).timestamp()
        }

        # Simple base64 encoding (NOT secure for production)
        token_data = base64.b64encode(json.dumps(payload).encode()).decode()
        return f"jwt.{token_data}"

    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify a JWT token (simplified for demo)."""
        try:
            if not token.startswith("jwt."):
                return None

            import base64
            import json

            payload_data = token.split(".", 1)[1]
            payload = json.loads(base64.b64decode(payload_data).decode())

            if datetime.now().timestamp() > payload["exp"]:
                return None

            return payload
        except Exception:
            return None

# Global auth service instance
auth_service = SecureAuthService()

# Dependency functions (simplified)
def get_current_user(token: str = "Bearer jwt.fake") -> Optional[Dict[str, Any]]:
    """Get current user from token."""
    if token.startswith("Bearer "):
        token = token[7:]  # Remove "Bearer " prefix
    return auth_service.verify_token(token)

def require_permission(permission: str):
    """Require a specific permission (simplified)."""
    def dependency(user: Optional[Dict[str, Any]] = None):
        if not user:
            raise Exception("Authentication required")
        # Simple role-based check
        if permission == "admin" and user.get("role") != "admin":
            raise Exception("Admin permission required")
        return user
    return dependency
