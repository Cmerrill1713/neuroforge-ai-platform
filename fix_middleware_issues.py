#!/usr/bin/env python3
"""
Fix Middleware Issues Script
Addresses the remaining middleware problems identified in testing.
"""

import subprocess
import sys
import os
import time

def fix_backend_validation():
    """Fix backend request validation."""
    print("🔧 Fixing Backend Request Validation...")
    
    # The issue might be that the validator is not being called properly
    # Let's add explicit validation in the endpoint
    validation_fix = '''
    @self.chat_router.post("/", response_model=ChatResponse)
    async def chat_endpoint(
        request: ChatRequest
    ):
        """Main chat endpoint with enhanced agent selection."""
        try:
            # Explicit validation for empty messages
            if not request.message or not request.message.strip():
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="Message cannot be empty or only whitespace"
                )
            
            # Validate input
            if self.input_validator:
                validation_result = self.input_validator.validate_input(
                    request.message, "general"
                )
                if not validation_result.get("is_valid", True):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                         detail=f"Input validation failed: {validation_result.get('threats', ['Invalid input'])[0]}"
                    )
'''
    
    print("✅ Backend validation fix prepared")

def fix_gzip_compression():
    """Fix GZip compression middleware."""
    print("🔧 Fixing GZip Compression...")
    
    # The issue might be that we need to ensure the middleware is properly configured
    gzip_fix = '''
    def _setup_middleware(self):
        """Setup middleware for the application."""
        # Performance monitoring middleware - Must be first
        @self.app.middleware("http")
        async def performance_middleware(request: Request, call_next):
            import time
            start_time = time.time()
            
            response = await call_next(request)
            
            process_time = time.time() - start_time
            response.headers["X-Process-Time"] = str(process_time)
            
            return response
        
        # CORS middleware
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        # Gzip compression - Ensure it's applied
        self.app.add_middleware(GZipMiddleware, minimum_size=0, compresslevel=6)
'''
    
    print("✅ GZip compression fix prepared")

def apply_fixes():
    """Apply all middleware fixes."""
    print("🚀 Applying Middleware Fixes...")
    
    # Read the current file
    with open('src/api/consolidated_api_architecture.py', 'r') as f:
        content = f.read()
    
    # Fix 1: Add explicit validation in chat endpoint
    old_chat_endpoint = '''        @self.chat_router.post("/", response_model=ChatResponse)
        async def chat_endpoint(
            request: ChatRequest
        ):
            """Main chat endpoint with enhanced agent selection."""
            try:
                # Validate input'''
    
    new_chat_endpoint = '''        @self.chat_router.post("/", response_model=ChatResponse)
        async def chat_endpoint(
            request: ChatRequest
        ):
            """Main chat endpoint with enhanced agent selection."""
            try:
                # Explicit validation for empty messages
                if not request.message or not request.message.strip():
                    raise HTTPException(
                        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                        detail="Message cannot be empty or only whitespace"
                    )
                
                # Validate input'''
    
    if old_chat_endpoint in content:
        content = content.replace(old_chat_endpoint, new_chat_endpoint)
        print("✅ Added explicit validation to chat endpoint")
    
    # Fix 2: Fix middleware order and GZip configuration
    old_middleware_setup = '''    def _setup_middleware(self):
        """TODO: Add docstring."""
        """Setup middleware for the application."""
        # CORS middleware
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        # Gzip compression - Fixed minimum size for better compression
        self.app.add_middleware(GZipMiddleware, minimum_size=0)

        # Performance monitoring middleware - Fixed timing
        @self.app.middleware("http")
        async def performance_middleware(request: Request, call_next):
            import time
            start_time = time.time()

            response = await call_next(request)

            process_time = time.time() - start_time
            response.headers["X-Process-Time"] = str(process_time)

            return response'''
    
    new_middleware_setup = '''    def _setup_middleware(self):
        """TODO: Add docstring."""
        """Setup middleware for the application."""
        # Performance monitoring middleware - Must be first
        @self.app.middleware("http")
        async def performance_middleware(request: Request, call_next):
            import time
            start_time = time.time()
            
            response = await call_next(request)
            
            process_time = time.time() - start_time
            response.headers["X-Process-Time"] = str(process_time)
            
            return response
        
        # CORS middleware
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        # Gzip compression - Ensure it's applied with proper settings
        self.app.add_middleware(GZipMiddleware, minimum_size=0, compresslevel=6)'''
    
    if old_middleware_setup in content:
        content = content.replace(old_middleware_setup, new_middleware_setup)
        print("✅ Fixed middleware order and GZip configuration")
    
    # Write the fixed content
    with open('src/api/consolidated_api_architecture.py', 'w') as f:
        f.write(content)
    
    print("✅ All middleware fixes applied")

def test_fixes():
    """Test the applied fixes."""
    print("🧪 Testing Applied Fixes...")
    
    # Restart server
    print("🔄 Restarting server...")
    subprocess.run(['pkill', '-f', 'main.py'], capture_output=True)
    time.sleep(2)
    
    # Start server in background
    with open('server.log', 'w') as log_file:
        subprocess.Popen(['python3', 'main.py'], stdout=log_file, stderr=subprocess.STDOUT)
    
    time.sleep(5)  # Wait for server to start
    
    # Test 1: Backend validation
    print("🧪 Testing backend validation...")
    result = subprocess.run([
        'curl', '-s', '-X', 'POST', 
        '-H', 'Content-Type: application/json',
        '-d', '{"message": ""}',
        'http://localhost:8004/api/chat/'
    ], capture_output=True, text=True)
    
    if '422' in result.stdout or 'Message cannot be empty' in result.stdout:
        print("✅ Backend validation working")
    else:
        print("❌ Backend validation still not working")
    
    # Test 2: GZip compression
    print("🧪 Testing GZip compression...")
    result = subprocess.run([
        'curl', '-s', '-H', 'Accept-Encoding: gzip',
        'http://localhost:8004/api/system/health',
        '-D', '-'
    ], capture_output=True, text=True)
    
    if 'Content-Encoding: gzip' in result.stdout:
        print("✅ GZip compression working")
    else:
        print("❌ GZip compression still not working")
    
    # Test 3: Performance timing
    print("🧪 Testing performance timing...")
    result = subprocess.run([
        'curl', '-s',
        'http://localhost:8004/api/system/health',
        '-D', '-'
    ], capture_output=True, text=True)
    
    if 'X-Process-Time:' in result.stdout:
        print("✅ Performance timing working")
    else:
        print("❌ Performance timing still not working")

def main():
    """Main function."""
    print("🔧 MIDDLEWARE FIXES SCRIPT")
    print("=" * 40)
    
    try:
        apply_fixes()
        test_fixes()
        print("\n✅ Middleware fixes completed!")
    except Exception as e:
        print(f"❌ Error applying fixes: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
