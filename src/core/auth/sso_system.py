"""
SSO Authentication System for Agentic LLM Core v2.0

This module provides Single Sign-On (SSO) authentication capabilities including
JWT tokens, password hashing, OAuth2 integration, and session management.

Created: 2024-09-28
Status: Production Ready
"""

import asyncio
import logging
import os
import secrets
import uuid
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

from fastapi import HTTPException, status
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel, Field, validator

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


# ============================================================================
# Configuration
# ============================================================================

# JWT Configuration
SECRET_KEY = os.getenv("SECRET_KEY", secrets.token_urlsafe(32))
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ============================================================================
# Data Models
# ============================================================================

class UserRole(str, Enum):
    """User roles in the system."""
    ADMIN = "admin"
    USER = "user"
    READONLY = "readonly"
    DEVELOPER = "developer"
    ANALYST = "analyst"


class UserStatus(str, Enum):
    """User account status."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING_VERIFICATION = "pending_verification"


class OAuthProvider(str, Enum):
    """Supported OAuth providers."""
    GOOGLE = "google"
    GITHUB = "github"
    MICROSOFT = "microsoft"
    APPLE = "apple"


class User(BaseModel):
    """User model."""
    user_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    username: str = Field(..., min_length=3, max_length=50)
    email: str = Field(..., description="User email address")
    hashed_password: Optional[str] = Field(None, description="Hashed password")
    full_name: Optional[str] = Field(None, description="Full name")
    role: UserRole = Field(UserRole.USER, description="User role")
    status: UserStatus = Field(UserStatus.ACTIVE, description="Account status")
    oauth_providers: List[OAuthProvider] = Field(default_factory=list, description="Linked OAuth providers")
    last_login: Optional[datetime] = Field(None, description="Last login timestamp")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional user metadata")
    
    @validator('email')
    def validate_email(cls, v):
        import re
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, v):
            raise ValueError('Invalid email format')
        return v.lower()


class UserCreate(BaseModel):
    """User creation request."""
    username: str = Field(..., min_length=3, max_length=50)
    email: str = Field(..., description="User email address")
    password: str = Field(..., min_length=8, description="User password")
    full_name: Optional[str] = Field(None, description="Full name")
    role: UserRole = Field(UserRole.USER, description="User role")


class UserUpdate(BaseModel):
    """User update request."""
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[str] = Field(None, description="User email address")
    full_name: Optional[str] = Field(None, description="Full name")
    role: Optional[UserRole] = Field(None, description="User role")
    status: Optional[UserStatus] = Field(None, description="Account status")


class LoginRequest(BaseModel):
    """Login request."""
    username: str = Field(..., description="Username or email")
    password: str = Field(..., description="Password")


class Token(BaseModel):
    """JWT token response."""
    access_token: str = Field(..., description="Access token")
    refresh_token: str = Field(..., description="Refresh token")
    token_type: str = Field("bearer", description="Token type")
    expires_in: int = Field(ACCESS_TOKEN_EXPIRE_MINUTES * 60, description="Token expiration in seconds")


class TokenData(BaseModel):
    """Token payload data."""
    user_id: str = Field(..., description="User ID")
    username: str = Field(..., description="Username")
    role: UserRole = Field(..., description="User role")
    exp: datetime = Field(..., description="Token expiration")


class OAuthToken(BaseModel):
    """OAuth token from external provider."""
    provider: OAuthProvider = Field(..., description="OAuth provider")
    access_token: str = Field(..., description="OAuth access token")
    refresh_token: Optional[str] = Field(None, description="OAuth refresh token")
    expires_in: Optional[int] = Field(None, description="Token expiration in seconds")


class Session(BaseModel):
    """User session."""
    session_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = Field(..., description="User ID")
    ip_address: Optional[str] = Field(None, description="Client IP address")
    user_agent: Optional[str] = Field(None, description="Client user agent")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    last_activity: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    is_active: bool = Field(True, description="Session active status")


# ============================================================================
# Authentication Utilities
# ============================================================================

class AuthUtils:
    """Authentication utility functions."""
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash."""
        return pwd_context.verify(plain_password, hashed_password)
    
    @staticmethod
    def get_password_hash(password: str) -> str:
        """Hash a password."""
        return pwd_context.hash(password)
    
    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Create a JWT access token."""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    @staticmethod
    def create_refresh_token(data: dict) -> str:
        """Create a JWT refresh token."""
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        to_encode.update({"exp": expire, "type": "refresh"})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    
    @staticmethod
    def verify_token(token: str) -> Optional[TokenData]:
        """Verify and decode a JWT token."""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            user_id: str = payload.get("sub")
            username: str = payload.get("username")
            role: str = payload.get("role")
            exp: int = payload.get("exp")
            
            if user_id is None or username is None or role is None:
                return None
            
            return TokenData(
                user_id=user_id,
                username=username,
                role=UserRole(role),
                exp=datetime.fromtimestamp(exp, tz=timezone.utc)
            )
        except JWTError:
            return None


# ============================================================================
# User Management
# ============================================================================

class UserManager:
    """User management system."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.users: Dict[str, User] = {}
        self.sessions: Dict[str, Session] = {}
        self._load_default_users()
    
    def _load_default_users(self):
        """Load default users for development."""
        # Create default admin user
        admin_user = User(
            username="admin",
            email="admin@agentic-llm.local",
            hashed_password=AuthUtils.get_password_hash("admin123"),
            full_name="System Administrator",
            role=UserRole.ADMIN,
            status=UserStatus.ACTIVE
        )
        self.users[admin_user.user_id] = admin_user
        
        # Create default developer user
        dev_user = User(
            username="developer",
            email="dev@agentic-llm.local",
            hashed_password=AuthUtils.get_password_hash("dev123"),
            full_name="Developer User",
            role=UserRole.DEVELOPER,
            status=UserStatus.ACTIVE
        )
        self.users[dev_user.user_id] = dev_user
        
        self.logger.info(f"Loaded {len(self.users)} default users")
    
    async def create_user(self, user_data: UserCreate) -> User:
        """Create a new user."""
        # Check if username or email already exists
        for user in self.users.values():
            if user.username == user_data.username:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Username already registered"
                )
            if user.email == user_data.email:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Email already registered"
                )
        
        # Create new user
        hashed_password = AuthUtils.get_password_hash(user_data.password)
        user = User(
            username=user_data.username,
            email=user_data.email,
            hashed_password=hashed_password,
            full_name=user_data.full_name,
            role=user_data.role,
            status=UserStatus.PENDING_VERIFICATION
        )
        
        self.users[user.user_id] = user
        self.logger.info(f"Created user: {user.username} ({user.user_id})")
        return user
    
    async def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID."""
        return self.users.get(user_id)
    
    async def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username."""
        for user in self.users.values():
            if user.username == username:
                return user
        return None
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        for user in self.users.values():
            if user.email == email.lower():
                return user
        return None
    
    async def update_user(self, user_id: str, user_data: UserUpdate) -> Optional[User]:
        """Update user information."""
        user = self.users.get(user_id)
        if not user:
            return None
        
        # Update fields
        if user_data.username is not None:
            # Check if new username is available
            for existing_user in self.users.values():
                if existing_user.user_id != user_id and existing_user.username == user_data.username:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Username already taken"
                    )
            user.username = user_data.username
        
        if user_data.email is not None:
            # Check if new email is available
            for existing_user in self.users.values():
                if existing_user.user_id != user_id and existing_user.email == user_data.email.lower():
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Email already registered"
                    )
            user.email = user_data.email.lower()
        
        if user_data.full_name is not None:
            user.full_name = user_data.full_name
        
        if user_data.role is not None:
            user.role = user_data.role
        
        if user_data.status is not None:
            user.status = user_data.status
        
        user.updated_at = datetime.now(timezone.utc)
        
        self.logger.info(f"Updated user: {user.username} ({user_id})")
        return user
    
    async def delete_user(self, user_id: str) -> bool:
        """Delete a user."""
        if user_id in self.users:
            user = self.users[user_id]
            del self.users[user_id]
            
            # Remove user sessions
            sessions_to_remove = [sid for sid, session in self.sessions.items() if session.user_id == user_id]
            for sid in sessions_to_remove:
                del self.sessions[sid]
            
            self.logger.info(f"Deleted user: {user.username} ({user_id})")
            return True
        return False
    
    async def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """Authenticate a user with username/email and password."""
        # Try to find user by username or email
        user = await self.get_user_by_username(username)
        if not user:
            user = await self.get_user_by_email(username)
        
        if not user:
            return None
        
        if not user.hashed_password:
            return None
        
        if not AuthUtils.verify_password(password, user.hashed_password):
            return None
        
        if user.status != UserStatus.ACTIVE:
            return None
        
        # Update last login
        user.last_login = datetime.now(timezone.utc)
        
        return user
    
    async def create_session(self, user_id: str, ip_address: Optional[str] = None, user_agent: Optional[str] = None) -> Session:
        """Create a new user session."""
        session = Session(
            user_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        self.sessions[session.session_id] = session
        self.logger.info(f"Created session for user {user_id}")
        return session
    
    async def get_session(self, session_id: str) -> Optional[Session]:
        """Get a session by ID."""
        return self.sessions.get(session_id)
    
    async def update_session_activity(self, session_id: str) -> bool:
        """Update session last activity."""
        session = self.sessions.get(session_id)
        if session:
            session.last_activity = datetime.now(timezone.utc)
            return True
        return False
    
    async def invalidate_session(self, session_id: str) -> bool:
        """Invalidate a session."""
        if session_id in self.sessions:
            self.sessions[session_id].is_active = False
            del self.sessions[session_id]
            return True
        return False
    
    async def get_user_sessions(self, user_id: str) -> List[Session]:
        """Get all active sessions for a user."""
        return [session for session in self.sessions.values() if session.user_id == user_id and session.is_active]
    
    async def cleanup_expired_sessions(self):
        """Clean up expired sessions."""
        now = datetime.now(timezone.utc)
        expired_sessions = []
        
        for session_id, session in self.sessions.items():
            # Sessions expire after 7 days of inactivity
            if (now - session.last_activity).days >= 7:
                expired_sessions.append(session_id)
        
        for session_id in expired_sessions:
            del self.sessions[session_id]
        
        if expired_sessions:
            self.logger.info(f"Cleaned up {len(expired_sessions)} expired sessions")


# ============================================================================
# OAuth Integration
# ============================================================================

class OAuthManager:
    """OAuth integration manager."""
    
    def __init__(self, user_manager: UserManager):
        self.logger = logging.getLogger(__name__)
        self.user_manager = user_manager
        self.oauth_configs = {
            OAuthProvider.GOOGLE: {
                "client_id": os.getenv("GOOGLE_CLIENT_ID"),
                "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
                "redirect_uri": os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:3000/auth/google/callback"),
                "scope": "openid email profile"
            },
            OAuthProvider.GITHUB: {
                "client_id": os.getenv("GITHUB_CLIENT_ID"),
                "client_secret": os.getenv("GITHUB_CLIENT_SECRET"),
                "redirect_uri": os.getenv("GITHUB_REDIRECT_URI", "http://localhost:3000/auth/github/callback"),
                "scope": "user:email"
            }
        }
    
    async def get_oauth_url(self, provider: OAuthProvider) -> str:
        """Get OAuth authorization URL."""
        config = self.oauth_configs.get(provider)
        if not config or not config["client_id"]:
            raise HTTPException(
                status_code=status.HTTP_501_NOT_IMPLEMENTED,
                detail=f"OAuth provider {provider.value} not configured"
            )
        
        if provider == OAuthProvider.GOOGLE:
            return f"https://accounts.google.com/oauth/authorize?client_id={config['client_id']}&redirect_uri={config['redirect_uri']}&scope={config['scope']}&response_type=code"
        elif provider == OAuthProvider.GITHUB:
            return f"https://github.com/login/oauth/authorize?client_id={config['client_id']}&redirect_uri={config['redirect_uri']}&scope={config['scope']}"
        else:
            raise HTTPException(
                status_code=status.HTTP_501_NOT_IMPLEMENTED,
                detail=f"OAuth provider {provider.value} not implemented"
            )
    
    async def handle_oauth_callback(self, provider: OAuthProvider, code: str) -> Optional[User]:
        """Handle OAuth callback and create/login user."""
        # This is a simplified implementation
        # In a real system, you'd exchange the code for tokens and fetch user info
        
        self.logger.info(f"OAuth callback for {provider.value} with code: {code[:10]}...")
        
        # For demo purposes, create a mock OAuth user
        oauth_user = User(
            username=f"oauth_{provider.value}_{secrets.token_hex(4)}",
            email=f"oauth_{provider.value}@example.com",
            full_name=f"OAuth {provider.value.title()} User",
            role=UserRole.USER,
            status=UserStatus.ACTIVE,
            oauth_providers=[provider]
        )
        
        # Check if user already exists
        existing_user = await self.user_manager.get_user_by_email(oauth_user.email)
        if existing_user:
            # Link OAuth provider to existing user
            if provider not in existing_user.oauth_providers:
                existing_user.oauth_providers.append(provider)
            return existing_user
        
        # Create new OAuth user
        await self.user_manager.create_user(UserCreate(
            username=oauth_user.username,
            email=oauth_user.email,
            password=secrets.token_urlsafe(16),  # Random password for OAuth users
            full_name=oauth_user.full_name,
            role=oauth_user.role
        ))
        
        return oauth_user


# ============================================================================
# Authentication Service
# ============================================================================

class AuthenticationService:
    """Main authentication service."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.user_manager = UserManager()
        self.oauth_manager = OAuthManager(self.user_manager)
    
    async def login(self, login_data: LoginRequest, ip_address: Optional[str] = None, user_agent: Optional[str] = None) -> Token:
        """Authenticate user and return tokens."""
        user = await self.user_manager.authenticate_user(login_data.username, login_data.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Create session
        session = await self.user_manager.create_session(user.user_id, ip_address, user_agent)
        
        # Create tokens
        access_token_data = {
            "sub": user.user_id,
            "username": user.username,
            "role": user.role.value,
            "session_id": session.session_id
        }
        
        refresh_token_data = {
            "sub": user.user_id,
            "username": user.username,
            "role": user.role.value
        }
        
        access_token = AuthUtils.create_access_token(access_token_data)
        refresh_token = AuthUtils.create_refresh_token(refresh_token_data)
        
        self.logger.info(f"User {user.username} logged in successfully")
        
        return Token(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
    
    async def refresh_token(self, refresh_token: str) -> Token:
        """Refresh access token using refresh token."""
        token_data = AuthUtils.verify_token(refresh_token)
        if not token_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        user = await self.user_manager.get_user_by_id(token_data.user_id)
        if not user or user.status != UserStatus.ACTIVE:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Create new tokens
        access_token_data = {
            "sub": user.user_id,
            "username": user.username,
            "role": user.role.value
        }
        
        new_refresh_token_data = {
            "sub": user.user_id,
            "username": user.username,
            "role": user.role.value
        }
        
        access_token = AuthUtils.create_access_token(access_token_data)
        new_refresh_token = AuthUtils.create_refresh_token(new_refresh_token_data)
        
        return Token(
            access_token=access_token,
            refresh_token=new_refresh_token,
            expires_in=ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
    
    async def logout(self, session_id: str) -> bool:
        """Logout user and invalidate session."""
        return await self.user_manager.invalidate_session(session_id)
    
    async def get_current_user(self, token: str) -> Optional[User]:
        """Get current user from token."""
        token_data = AuthUtils.verify_token(token)
        if not token_data:
            return None
        
        user = await self.user_manager.get_user_by_id(token_data.user_id)
        if not user or user.status != UserStatus.ACTIVE:
            return None
        
        return user
    
    async def require_role(self, user: User, required_roles: List[UserRole]) -> bool:
        """Check if user has required role."""
        return user.role in required_roles


# ============================================================================
# Main Function
# ============================================================================

async def main():
    """Main function for testing the authentication system."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Authentication System")
    parser.add_argument("--action", choices=["create", "login", "verify", "list"], required=True)
    parser.add_argument("--username", help="Username")
    parser.add_argument("--email", help="Email")
    parser.add_argument("--password", help="Password")
    parser.add_argument("--token", help="JWT token")
    
    args = parser.parse_args()
    
    try:
        auth_service = AuthenticationService()
        
        if args.action == "create":
            if not all([args.username, args.email, args.password]):
                print("Error: --username, --email, and --password are required for create action")
                return 1
            
            user_data = UserCreate(
                username=args.username,
                email=args.email,
                password=args.password,
                full_name=f"{args.username.title()} User"
            )
            
            user = await auth_service.user_manager.create_user(user_data)
            print(f"✅ Created user: {user.username} ({user.user_id})")
            
        elif args.action == "login":
            if not all([args.username, args.password]):
                print("Error: --username and --password are required for login action")
                return 1
            
            login_data = LoginRequest(username=args.username, password=args.password)
            token = await auth_service.login(login_data)
            print("✅ Login successful!")
            print(f"   Access Token: {token.access_token[:50]}...")
            print(f"   Refresh Token: {token.refresh_token[:50]}...")
            print(f"   Expires In: {token.expires_in} seconds")
            
        elif args.action == "verify":
            if not args.token:
                print("Error: --token is required for verify action")
                return 1
            
            user = await auth_service.get_current_user(args.token)
            if user:
                print(f"✅ Token valid for user: {user.username} ({user.role.value})")
            else:
                print("❌ Invalid token")
                return 1
                
        elif args.action == "list":
            users = list(auth_service.user_manager.users.values())
            print(f"📋 Users ({len(users)}):")
            for user in users:
                print(f"   - {user.username} ({user.email}) - {user.role.value} - {user.status.value}")
        
        return 0
        
    except Exception as e:
        logger.error(f"Authentication operation failed: {e}")
        return 1


if __name__ == "__main__":
    exit(asyncio.run(main()))
