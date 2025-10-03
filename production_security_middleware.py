#!/usr/bin/env python3
"""
Production Security Middleware
Comprehensive security hardening for production deployment
"""

import time
import hashlib
import secrets
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from collections import defaultdict
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import asyncio

logger = logging.getLogger(__name__)

class SecurityMiddleware(BaseHTTPMiddleware):
    """Production-grade security middleware"""
    
    def __init__(self, app, config: Dict[str, Any]):
        super().__init__(app)
        self.config = config
        self.rate_limits = defaultdict(list)
        self.blocked_ips = set()
        self.suspicious_patterns = [
            r'<script', r'javascript:', r'vbscript:', r'onload=',
            r'../', r'..\\', r'cmd/', r'exec', r'eval',
            r'union.*select', r'drop.*table', r'insert.*into',
            r'<iframe', r'<object', r'<embed'
        ]
        self.max_requests_per_minute = config.get('RATE_LIMIT_REQUESTS', 100)
        self.max_requests_per_hour = config.get('RATE_LIMIT_HOUR', 1000)
        self.block_duration_minutes = config.get('BLOCK_DURATION', 60)
        
    async def dispatch(self, request: Request, call_next):
        """Main security check pipeline"""
        start_time = time.time()
        client_ip = self._get_client_ip(request)
        
        # Check if IP is blocked
        if client_ip in self.blocked_ips:
            logger.warning(f"Blocked IP attempted access: {client_ip}")
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="IP temporarily blocked due to suspicious activity"
            )
        
        # Rate limiting
        if not self._check_rate_limit(client_ip):
            logger.warning(f"Rate limit exceeded for IP: {client_ip}")
            self._block_ip(client_ip)
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded"
            )
        
        # Input validation
        if not self._validate_request(request):
            logger.warning(f"Suspicious request from IP: {client_ip}")
            self._block_ip(client_ip)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid request detected"
            )
        
        # Add security headers
        response = await call_next(request)
        self._add_security_headers(response)
        
        # Log security event
        processing_time = time.time() - start_time
        self._log_security_event(client_ip, request, response, processing_time)
        
        return response
    
    def _get_client_ip(self, request: Request) -> str:
        """Extract real client IP"""
        # Check for forwarded headers
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip
        
        return request.client.host if request.client else "unknown"
    
    def _check_rate_limit(self, client_ip: str) -> bool:
        """Check if client is within rate limits"""
        now = time.time()
        minute_ago = now - 60
        hour_ago = now - 3600
        
        # Clean old entries
        self.rate_limits[client_ip] = [
            req_time for req_time in self.rate_limits[client_ip] 
            if req_time > hour_ago
        ]
        
        # Count requests in last minute and hour
        recent_requests = [
            req_time for req_time in self.rate_limits[client_ip]
            if req_time > minute_ago
        ]
        
        hourly_requests = len(self.rate_limits[client_ip])
        
        # Add current request
        self.rate_limits[client_ip].append(now)
        
        return (
            len(recent_requests) < self.max_requests_per_minute and
            hourly_requests < self.max_requests_per_hour
        )
    
    def _validate_request(self, request: Request) -> bool:
        """Validate request for suspicious patterns"""
        try:
            # Check URL for suspicious patterns
            url = str(request.url)
            for pattern in self.suspicious_patterns:
                if pattern.lower() in url.lower():
                    return False
            
            # Check headers for suspicious content
            for header_name, header_value in request.headers.items():
                if any(pattern.lower() in str(header_value).lower() 
                      for pattern in self.suspicious_patterns):
                    return False
            
            # Check query parameters
            for param_name, param_value in request.query_params.items():
                if any(pattern.lower() in str(param_value).lower() 
                      for pattern in self.suspicious_patterns):
                    return False
            
            return True
        except Exception as e:
            logger.error(f"Request validation error: {e}")
            return False
    
    def _block_ip(self, client_ip: str):
        """Block IP for specified duration"""
        self.blocked_ips.add(client_ip)
        logger.warning(f"Blocked IP: {client_ip} for {self.block_duration_minutes} minutes")
        
        # Schedule unblock
        asyncio.create_task(self._unblock_ip_after_delay(client_ip))
    
    async def _unblock_ip_after_delay(self, client_ip: str):
        """Unblock IP after delay"""
        await asyncio.sleep(self.block_duration_minutes * 60)
        self.blocked_ips.discard(client_ip)
        logger.info(f"Unblocked IP: {client_ip}")
    
    def _add_security_headers(self, response: JSONResponse):
        """Add security headers to response"""
        security_headers = {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "Content-Security-Policy": "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Permissions-Policy": "geolocation=(), microphone=(), camera=()"
        }
        
        for header, value in security_headers.items():
            response.headers[header] = value
    
    def _log_security_event(self, client_ip: str, request: Request, 
                           response: JSONResponse, processing_time: float):
        """Log security events for monitoring"""
        event = {
            "timestamp": datetime.utcnow().isoformat(),
            "client_ip": client_ip,
            "method": request.method,
            "url": str(request.url),
            "status_code": response.status_code,
            "processing_time": processing_time,
            "user_agent": request.headers.get("user-agent", "unknown"),
            "referer": request.headers.get("referer", "none")
        }
        
        # Log to security log file
        logger.info(f"SECURITY_EVENT: {json.dumps(event)}")
        
        # Alert on suspicious activity
        if response.status_code in [400, 401, 403, 429]:
            logger.warning(f"SUSPICIOUS_ACTIVITY: {json.dumps(event)}")

class AuthenticationMiddleware(BaseHTTPMiddleware):
    """API Key authentication middleware"""
    
    def __init__(self, app, api_keys: List[str]):
        super().__init__(app)
        self.api_keys = set(api_keys)
        self.valid_api_key_hash = self._hash_api_keys()
    
    def _hash_api_keys(self) -> str:
        """Create hash of valid API keys for comparison"""
        combined_keys = "|".join(sorted(self.api_keys))
        return hashlib.sha256(combined_keys.encode()).hexdigest()
    
    async def dispatch(self, request: Request, call_next):
        """Check API key authentication"""
        # Skip auth for health checks and public endpoints
        if request.url.path in ["/health", "/docs", "/openapi.json", "/"]:
            return await call_next(request)
        
        api_key = request.headers.get("X-API-Key")
        if not api_key:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="API key required"
            )
        
        if api_key not in self.api_keys:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid API key"
            )
        
        return await call_next(request)

def create_production_middleware_stack(app, config: Dict[str, Any]):
    """Create complete production middleware stack"""
    
    # Security middleware
    app.add_middleware(SecurityMiddleware, config=config)
    
    # Authentication middleware (if API keys configured)
    api_keys = config.get('API_KEYS', '').split(',')
    if api_keys and api_keys[0]:
        app.add_middleware(AuthenticationMiddleware, api_keys=api_keys)
    
    # Trusted host middleware
    allowed_hosts = config.get_list('ALLOWED_HOSTS', ['localhost', '127.0.0.1'])
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=allowed_hosts)
    
    logger.info("Production security middleware stack initialized")
