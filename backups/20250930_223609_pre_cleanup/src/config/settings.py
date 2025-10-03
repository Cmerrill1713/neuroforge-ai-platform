#!/usr/bin/env python3
"""
Configuration Settings
"""

import os
from typing import Dict, Any

class Settings:
    """Application settings"""

    def __init__(self):
        self.database_url = os.getenv("DATABASE_URL", "sqlite:///neuroforge.db")
        self.redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
        self.api_port = int(os.getenv("API_PORT", "8000"))

settings = Settings()
