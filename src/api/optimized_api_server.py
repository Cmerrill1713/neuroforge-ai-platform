#!/usr/bin/env python3
"""
Optimized FastAPI Web Server
"""

import asyncio
import logging
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="NeuroForge API")

class ChatRequest(BaseModel):
    message: str

@app.get("/health")
async def health():
    return {"status": "healthy"}

@app.post("/chat")
async def chat(request: ChatRequest):
    return {"response": f"Echo: {request.message}"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
