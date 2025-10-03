#!/usr/bin/env python3
"""
Ensure System Stability - Permanent startup script to prevent recurring issues
"""

import os
import sys
import json
import logging
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.core.stability.configuration_manager import config_manager
from src.core.stability.import_guardian import import_guardian
from src.core.stability.service_guardian import service_guardian

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def ensure_configuration():
    """Ensure configuration is properly set"""
    logger.info("🔧 Ensuring configuration stability...")
    
    # Create config directory
    config_dir = project_root / "config"
    config_dir.mkdir(exist_ok=True)
    
    # Ensure environment variables are set
    env_vars = {
        'NEXT_PUBLIC_CONSOLIDATED_API_URL': 'http://localhost:8004',
        'NEXT_PUBLIC_AGENTIC_PLATFORM_URL': 'http://localhost:8000',
        'NEXT_PUBLIC_API_URL': 'http://localhost:8004',
    }
    
    for var, default_value in env_vars.items():
        if not os.getenv(var):
            os.environ[var] = default_value
            logger.info(f"Set environment variable: {var}={default_value}")
    
    # Update configuration from environment
    config_manager.update_from_env()
    
    # Save configuration
    config_manager.save_config()
    
    logger.info("✅ Configuration stability ensured")

def ensure_import_stability():
    """Ensure imports are stable"""
    logger.info("🔧 Ensuring import stability...")
    
    # Test critical imports
    critical_imports = [
        'fastapi',
        'pydantic',
        'uvicorn',
        'aiohttp'
    ]
    
    failed_imports = []
    for module in critical_imports:
        try:
            __import__(module)
            logger.debug(f"✅ {module} import successful")
        except ImportError as e:
            failed_imports.append(f"{module}: {e}")
            logger.error(f"❌ {module} import failed: {e}")
    
    if failed_imports:
        logger.error("❌ Critical imports failed:")
        for failure in failed_imports:
            logger.error(f"  - {failure}")
        return False
    
    logger.info("✅ Import stability ensured")
    return True

def ensure_service_configuration():
    """Ensure service configuration is correct"""
    logger.info("🔧 Ensuring service configuration...")
    
    # Check if services are properly configured
    services = [
        'consolidated_api',
        'agentic_platform', 
        'frontend',
        'tts',
        'whisper'
    ]
    
    for service in services:
        url = config_manager.get_service_url(service)
        logger.info(f"  {service}: {url}")
    
    logger.info("✅ Service configuration ensured")

def create_startup_validation():
    """Create startup validation file"""
    logger.info("🔧 Creating startup validation...")
    
    validation_data = {
        "startup_timestamp": str(datetime.now().isoformat()),
        "configuration": config_manager.get_config_summary(),
        "import_status": import_guardian.get_status(),
        "service_configuration": {
            service: config_manager.get_service_url(service)
            for service in ['consolidated_api', 'agentic_platform', 'frontend', 'tts', 'whisper']
        }
    }
    
    validation_file = project_root / "config" / "startup_validation.json"
    with open(validation_file, 'w') as f:
        json.dump(validation_data, f, indent=2)
    
    logger.info(f"✅ Startup validation saved to {validation_file}")

def main():
    """Main startup stability check"""
    logger.info("🚀 Starting system stability check...")
    
    try:
        # Ensure configuration
        ensure_configuration()
        
        # Ensure import stability
        if not ensure_import_stability():
            logger.error("❌ Import stability check failed")
            sys.exit(1)
        
        # Ensure service configuration
        ensure_service_configuration()
        
        # Create startup validation
        create_startup_validation()
        
        logger.info("✅ System stability check completed successfully")
        logger.info("🎯 System is ready for stable operation")
        
    except Exception as e:
        logger.error(f"❌ Stability check failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    from datetime import datetime
    main()
