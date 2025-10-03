#!/usr/bin/env python3
"""
Centralized Environment Configuration Management
Ensures consistent environment variable usage across the entire system
"""

import os
import logging
from typing import Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

class EnvironmentConfig:
    """Centralized environment configuration manager"""

    # Default values for all environment variables
    DEFAULTS = {
        # Core Service URLs
        'CONSOLIDATED_API_URL': 'http://localhost:8004',
        'AGENTIC_PLATFORM_URL': 'http://localhost:8000',
        'RAG_SERVICE_URL': 'http://localhost:8005',
        'TTS_SERVICE_URL': 'http://localhost:8087',
        'OLLAMA_URL': 'http://localhost:11434',

        # Database Configuration
        'POSTGRES_URL': 'postgresql://postgres:password@localhost:5432/agentic_platform',
        'REDIS_URL': 'redis://localhost:6379',
        'WEAVIATE_HOST': 'localhost',
        'WEAVIATE_HTTP_PORT': '8090',
        'WEAVIATE_GRPC_PORT': '50051',
        'WEAVIATE_CLASS': 'KnowledgeDocumentBGE',
        'ELASTIC_URL': 'http://localhost:9200',
        'ELASTIC_INDEX': 'docs',

        # AI/ML Configuration
        'OLLAMA_MODEL': 'qwen2.5:7b',
        'EMBEDDER_MODEL': 'BAAI/bge-large-en-v1.5',
        'RERANKER_MODEL': 'cross-encoder/ms-marco-MiniLM-L-6-v2',
        'DEFAULT_TEMPERATURE': '0.7',
        'MAX_TOKENS': '500',

        # Agent Configuration
        'AGENT_ID': 'ai-assistant-001',
        'AGENT_ROLE': 'general_assistant',
        'MAX_MEMORY_MB': '1024',
        'MAX_CPU_PERCENT': '80',
        'BATCH_SIZE': '10',
        'MAX_CONCURRENT_TASKS': '3',

        # Security Configuration
        'SECRET_KEY': 'change-this-in-production',
        'JWT_SECRET': 'change-this-in-production',
        'API_KEY': '',
        'CORS_ORIGINS': 'http://localhost:3000,http://localhost:3001,http://localhost:3002,http://localhost:3003,http://localhost:3004',

        # Logging Configuration
        'LOG_LEVEL': 'INFO',
        'LOG_FORMAT': 'json',
        'LOG_FILE': 'logs/app.log',

        # Performance Configuration
        'MAX_REQUEST_SIZE': '50MB',
        'REQUEST_TIMEOUT': '30',
        'RATE_LIMIT_REQUESTS': '100',
        'RATE_LIMIT_WINDOW': '60',

        # Feature Flags
        'ENABLE_VOICE': 'true',
        'ENABLE_RAG': 'true',
        'ENABLE_EVOLUTION': 'true',
        'ENABLE_MCP': 'true',
        'ENABLE_CACHING': 'true',
        'ENABLE_METRICS': 'true',

        # External Service URLs
        'KNOWLEDGE_BASE_URL': 'http://localhost:8004',
        'ORCHESTRATOR_URL': 'http://localhost:8007',
        'MONITOR_URL': 'http://localhost:8006',

        # Frontend Configuration (for SSR)
        'NEXT_PUBLIC_CONSOLIDATED_API_URL': 'http://localhost:8004',
        'NEXT_PUBLIC_AGENTIC_PLATFORM_URL': 'http://localhost:8000',
        'NEXT_PUBLIC_RAG_SERVICE_URL': 'http://localhost:8005',
        'NEXT_PUBLIC_TTS_SERVICE_URL': 'http://localhost:8087',
    }

    def __init__(self, env_file: Optional[str] = None):
        self._config = {}
        self._load_defaults()
        self._load_from_file(env_file)
        self._load_from_env()
        self._validate_config()

    def _load_defaults(self):
        """Load default values"""
        self._config.update(self.DEFAULTS.copy())

    def _load_from_file(self, env_file: Optional[str]):
        """Load configuration from .env file"""
        if not env_file:
            # Try common env file locations
            possible_files = [
                Path('.env'),
                Path('.env.local'),
                Path('.env.production'),
                Path('env.local'),
                Path('env.production')
            ]
            for file_path in possible_files:
                if file_path.exists():
                    env_file = str(file_path)
                    break

        if env_file and Path(env_file).exists():
            logger.info(f"Loading environment from: {env_file}")
            try:
                with open(env_file, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#'):
                            key, _, value = line.partition('=')
                            if key and value:
                                self._config[key.strip()] = value.strip().strip('"\'')
            except Exception as e:
                logger.warning(f"Failed to load env file {env_file}: {e}")

    def _load_from_env(self):
        """Load configuration from environment variables"""
        for key in self._config.keys():
            env_value = os.getenv(key)
            if env_value is not None:
                self._config[key] = env_value

    def _validate_config(self):
        """Validate configuration values"""
        # Validate URLs
        url_keys = ['CONSOLIDATED_API_URL', 'AGENTIC_PLATFORM_URL', 'RAG_SERVICE_URL',
                   'TTS_SERVICE_URL', 'OLLAMA_URL', 'KNOWLEDGE_BASE_URL']
        for key in url_keys:
            if key in self._config:
                value = self._config[key]
                if not (value.startswith('http://') or value.startswith('https://')):
                    logger.warning(f"Invalid URL format for {key}: {value}")

        # Validate numeric values
        numeric_keys = ['WEAVIATE_HTTP_PORT', 'WEAVIATE_GRPC_PORT', 'MAX_MEMORY_MB',
                       'MAX_CPU_PERCENT', 'BATCH_SIZE', 'MAX_CONCURRENT_TASKS']
        for key in numeric_keys:
            if key in self._config:
                try:
                    int(self._config[key])
                except ValueError:
                    logger.warning(f"Invalid numeric value for {key}: {self._config[key]}")

        # Validate boolean values
        boolean_keys = ['ENABLE_VOICE', 'ENABLE_RAG', 'ENABLE_EVOLUTION',
                       'ENABLE_MCP', 'ENABLE_CACHING', 'ENABLE_METRICS']
        for key in boolean_keys:
            if key in self._config:
                value = self._config[key].lower()
                if value not in ['true', 'false', '1', '0', 'yes', 'no']:
                    logger.warning(f"Invalid boolean value for {key}: {self._config[key]}")

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        return self._config.get(key, default)

    def get_int(self, key: str, default: int = 0) -> int:
        """Get configuration value as integer"""
        try:
            return int(self._config.get(key, default))
        except (ValueError, TypeError):
            return default

    def get_float(self, key: str, default: float = 0.0) -> float:
        """Get configuration value as float"""
        try:
            return float(self._config.get(key, default))
        except (ValueError, TypeError):
            return default

    def get_bool(self, key: str, default: bool = False) -> bool:
        """Get configuration value as boolean"""
        value = self._config.get(key, str(default)).lower()
        return value in ['true', '1', 'yes', 'on']

    def get_list(self, key: str, default: list = None, separator: str = ',') -> list:
        """Get configuration value as list"""
        if default is None:
            default = []
        value = self._config.get(key, '')
        if not value:
            return default
        return [item.strip() for item in value.split(separator)]

    def set(self, key: str, value: Any):
        """Set configuration value"""
        self._config[key] = str(value)

    def all(self) -> Dict[str, Any]:
        """Get all configuration values"""
        return self._config.copy()

    def save_to_file(self, file_path: str):
        """Save current configuration to file"""
        try:
            with open(file_path, 'w') as f:
                f.write("# NeuroForge Environment Configuration\n")
                f.write("# Generated automatically - DO NOT EDIT MANUALLY\n\n")
                for key, value in sorted(self._config.items()):
                    f.write(f"{key}={value}\n")
            logger.info(f"Configuration saved to: {file_path}")
        except Exception as e:
            logger.error(f"Failed to save configuration: {e}")

    def print_config(self):
        """Print current configuration"""
        print("=== Current Environment Configuration ===")
        for key, value in sorted(self._config.items()):
            print(f"{key}={value}")
        print("=" * 50)

# Global configuration instance
_config_instance = None

def get_config(env_file: Optional[str] = None) -> EnvironmentConfig:
    """Get global configuration instance"""
    global _config_instance
    if _config_instance is None:
        _config_instance = EnvironmentConfig(env_file)
    return _config_instance

# Convenience functions for backward compatibility
def get_env_var(key: str, default: Any = None) -> Any:
    """Get environment variable (backward compatibility)"""
    return get_config().get(key, default)

def get_env_var_int(key: str, default: int = 0) -> int:
    """Get environment variable as integer (backward compatibility)"""
    return get_config().get_int(key, default)

def get_env_var_bool(key: str, default: bool = False) -> bool:
    """Get environment variable as boolean (backward compatibility)"""
    return get_config().get_bool(key, default)
