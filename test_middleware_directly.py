#!/usr/bin/env python3
"""
Test Middleware Directly
Create a simple FastAPI app to test middleware functionality.
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
import time

# Create a simple test app
app = FastAPI()

# Add middleware
@app.middleware("http")
async def performance_middleware(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

app.add_middleware(GZipMiddleware, minimum_size=0)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/test")
async def test_endpoint():
    return {"message": "Middleware test", "data": "x" * 100}  # Make it larger for compression

if __name__ == "__main__":
    import uvicorn
    print("🧪 Starting middleware test server on port 8007...")
    uvicorn.run(app, host="0.0.0.0", port=8007)
