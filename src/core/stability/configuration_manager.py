#!/usr/bin/env python3
"""
Configuration Manager - Permanent solution for configuration stability
"""

import os
import json
import logging
from typing import Dict, Any, Optional
from pathlib import Path
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)

@dataclass
class SystemConfiguration:
    """System-wide configuration that persists across restarts"""
    # API Configuration
    consolidated_api_url: str = "http://localhost:8004"
    agentic_platform_url: str = "http://localhost:8000"
    frontend_url: str = "http://localhost:3000"
    
    # Service URLs
    tts_url: str = "http://localhost:8087"
    whisper_url: str = "http://localhost:8087"
    ollama_url: str = "http://localhost:11434"
    
    # Feature Flags
    enable_home_assistant: bool = False
    enable_voice_services: bool = True
    enable_mcp_tools: bool = True
    enable_rag_system: bool = True
    enable_self_healing: bool = True
    
    # Performance Settings
    request_timeout: float = 30.0
    max_retries: int = 3
    retry_delay: float = 1.0
    
    # Fallback Settings
    use_fallback_responses: bool = True
    log_fallback_usage: bool = True

class ConfigurationManager:
    """Permanent solution for configuration management and persistence"""
    
    def __init__(self, config_file: str = "config/system_config.json"):
        self.config_file = Path(config_file)
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        self.config = SystemConfiguration()
        self.load_config()
        
    def load_config(self):
        """Load configuration from file"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r') as f:
                    config_data = json.load(f)
                    # Update config with loaded data
                    for key, value in config_data.items():
                        if hasattr(self.config, key):
                            setattr(self.config, key, value)
                logger.info(f"Loaded configuration from {self.config_file}")
            else:
                logger.info("No existing config file, using defaults")
                self.save_config()
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            logger.info("Using default configuration")
    
    def save_config(self):
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(asdict(self.config), f, indent=2)
            logger.info(f"Saved configuration to {self.config_file}")
        except Exception as e:
            logger.error(f"Failed to save configuration: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value"""
        return getattr(self.config, key, default)
    
    def set(self, key: str, value: Any):
        """Set a configuration value and save"""
        if hasattr(self.config, key):
            setattr(self.config, key, value)
            self.save_config()
            logger.info(f"Updated configuration: {key} = {value}")
        else:
            logger.warning(f"Unknown configuration key: {key}")
    
    def update_from_env(self):
        """Update configuration from environment variables"""
        env_mappings = {
            'CONSOLIDATED_API_URL': 'consolidated_api_url',
            'AGENTIC_PLATFORM_URL': 'agentic_platform_url',
            'FRONTEND_URL': 'frontend_url',
            'TTS_URL': 'tts_url',
            'WHISPER_URL': 'whisper_url',
            'OLLAMA_URL': 'ollama_url',
            'ENABLE_HOME_ASSISTANT': ('enable_home_assistant', bool),
            'ENABLE_VOICE_SERVICES': ('enable_voice_services', bool),
            'ENABLE_MCP_TOOLS': ('enable_mcp_tools', bool),
            'ENABLE_RAG_SYSTEM': ('enable_rag_system', bool),
            'ENABLE_SELF_HEALING': ('enable_self_healing', bool),
        }
        
        for env_var, config_key in env_mappings.items():
            env_value = os.getenv(env_var)
            if env_value is not None:
                if isinstance(config_key, tuple):
                    key, value_type = config_key
                    if value_type == bool:
                        env_value = env_value.lower() in ('true', '1', 'yes', 'on')
                    else:
                        env_value = value_type(env_value)
                else:
                    key = config_key
                
                self.set(key, env_value)
                logger.debug(f"Updated {key} from environment: {env_value}")
    
    def get_service_url(self, service_name: str) -> str:
        """Get URL for a specific service"""
        url_mappings = {
            'consolidated_api': self.config.consolidated_api_url,
            'agentic_platform': self.config.agentic_platform_url,
            'frontend': self.config.frontend_url,
            'tts': self.config.tts_url,
            'whisper': self.config.whisper_url,
            'ollama': self.config.ollama_url,
        }
        return url_mappings.get(service_name, f"http://localhost:8000")
    
    def is_feature_enabled(self, feature: str) -> bool:
        """Check if a feature is enabled"""
        feature_mappings = {
            'home_assistant': self.config.enable_home_assistant,
            'voice_services': self.config.enable_voice_services,
            'mcp_tools': self.config.enable_mcp_tools,
            'rag_system': self.config.enable_rag_system,
            'self_healing': self.config.enable_self_healing,
        }
        return feature_mappings.get(feature, False)
    
    def get_config_summary(self) -> Dict[str, Any]:
        """Get a summary of current configuration"""
        return {
            "config_file": str(self.config_file),
            "config_exists": self.config_file.exists(),
            "services": {
                "consolidated_api": self.config.consolidated_api_url,
                "agentic_platform": self.config.agentic_platform_url,
                "frontend": self.config.frontend_url,
                "tts": self.config.tts_url,
                "whisper": self.config.whisper_url,
            },
            "features": {
                "home_assistant": self.config.enable_home_assistant,
                "voice_services": self.config.enable_voice_services,
                "mcp_tools": self.config.enable_mcp_tools,
                "rag_system": self.config.enable_rag_system,
                "self_healing": self.config.enable_self_healing,
            },
            "performance": {
                "request_timeout": self.config.request_timeout,
                "max_retries": self.config.max_retries,
                "retry_delay": self.config.retry_delay,
            }
        }

# Global instance
config_manager = ConfigurationManager()

# Initialize from environment
config_manager.update_from_env()
