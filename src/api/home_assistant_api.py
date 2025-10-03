#!/usr/bin/env python3
"""
Home Assistant API Routes
Provides REST API endpoints for Home Assistant integration
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from datetime import datetime

from src.core.integrations.home_assistant_integration import (
    ha_integration, 
    get_home_assistant,
    HomeAssistantIntegration
)

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/home-assistant", tags=["home-assistant"])

# Request/Response models
class DeviceControlRequest(BaseModel):
    entity_id: str = Field(..., description="Entity ID of the device to control")
    action: str = Field(..., description="Action to perform (turn_on, turn_off, set_temperature, etc.)")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Additional parameters for the action")

class AutomationTriggerRequest(BaseModel):
    automation_id: str = Field(..., description="ID of the automation to trigger")

class DeviceSearchRequest(BaseModel):
    domain: Optional[str] = Field(None, description="Filter by domain (light, switch, sensor, etc.)")
    name_contains: Optional[str] = Field(None, description="Filter by name containing text")
    state: Optional[str] = Field(None, description="Filter by current state")

class DeviceSearchResponse(BaseModel):
    devices: List[Dict[str, Any]]
    total_found: int
    filters_applied: Dict[str, Any]

class SystemInfoResponse(BaseModel):
    initialized: bool
    base_url: Optional[str] = None
    total_devices: int = 0
    total_automations: int = 0
    domains: Dict[str, int] = {}
    last_updated: datetime

# Health and Status Endpoints
@router.get("/status")
async def get_ha_status():
    """Get Home Assistant integration status"""
    try:
        ha = await get_home_assistant()
        
        if ha.initialized:
            system_info = await ha.api.get_system_info()
            devices_summary = await ha.get_devices_summary()
            
            return {
                "status": "connected",
                "initialized": True,
                "base_url": ha.api.config.base_url,
                "total_devices": devices_summary.get("total_devices", 0),
                "total_automations": len(ha.api.automations),
                "domains": devices_summary.get("domains", {}),
                "system_info": system_info,
                "last_updated": datetime.now().isoformat()
            }
        else:
            return {
                "status": "disconnected",
                "initialized": False,
                "message": "Home Assistant not initialized or not found"
            }
    except Exception as e:
        logger.error(f"Status check failed: {e}")
        return {
            "status": "error",
            "initialized": False,
            "error": str(e)
        }

@router.post("/initialize")
async def initialize_ha():
    """Manually initialize Home Assistant integration"""
    try:
        ha = await get_home_assistant()
        success = await ha.auto_initialize()
        
        if success:
            return {
                "success": True,
                "message": "Home Assistant initialized successfully",
                "base_url": ha.api.config.base_url,
                "total_devices": len(ha.api.devices)
            }
        else:
            return {
                "success": False,
                "message": "Failed to initialize Home Assistant"
            }
    except Exception as e:
        logger.error(f"Initialization failed: {e}")
        raise HTTPException(status_code=500, detail=f"Initialization failed: {str(e)}")

# Device Management Endpoints
@router.get("/devices")
async def get_all_devices():
    """Get all Home Assistant devices"""
    try:
        ha = await get_home_assistant()
        if not ha.initialized:
            raise HTTPException(status_code=503, detail="Home Assistant not initialized")
        
        devices_summary = await ha.get_devices_summary()
        return devices_summary
    except Exception as e:
        logger.error(f"Failed to get devices: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/devices/{domain}")
async def get_devices_by_domain(domain: str):
    """Get devices filtered by domain"""
    try:
        ha = await get_home_assistant()
        if not ha.initialized:
            raise HTTPException(status_code=503, detail="Home Assistant not initialized")
        
        devices = await ha.api.get_devices_by_domain(domain)
        return {
            "domain": domain,
            "devices": [asdict(device) for device in devices],
            "total": len(devices)
        }
    except Exception as e:
        logger.error(f"Failed to get devices by domain: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/device/{entity_id}")
async def get_device_state(entity_id: str):
    """Get current state of a specific device"""
    try:
        ha = await get_home_assistant()
        if not ha.initialized:
            raise HTTPException(status_code=503, detail="Home Assistant not initialized")
        
        device_state = await ha.api.get_device_state(entity_id)
        if device_state is None:
            raise HTTPException(status_code=404, detail=f"Device {entity_id} not found")
        
        return {
            "entity_id": entity_id,
            "state": device_state
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get device state: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/device/control")
async def control_device(request: DeviceControlRequest):
    """Control a Home Assistant device"""
    try:
        ha = await get_home_assistant()
        if not ha.initialized:
            raise HTTPException(status_code=503, detail="Home Assistant not initialized")
        
        result = await ha.control_device(
            entity_id=request.entity_id,
            action=request.action,
            **request.parameters
        )
        
        if result.get("success"):
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get("error", "Control failed"))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Device control failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/device/{entity_id}/turn_on")
async def turn_on_device(entity_id: str, parameters: Dict[str, Any] = {}):
    """Turn on a device"""
    try:
        ha = await get_home_assistant()
        if not ha.initialized:
            raise HTTPException(status_code=503, detail="Home Assistant not initialized")
        
        result = await ha.control_device(entity_id, "turn_on", **parameters)
        return result
    except Exception as e:
        logger.error(f"Turn on failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/device/{entity_id}/turn_off")
async def turn_off_device(entity_id: str):
    """Turn off a device"""
    try:
        ha = await get_home_assistant()
        if not ha.initialized:
            raise HTTPException(status_code=503, detail="Home Assistant not initialized")
        
        result = await ha.control_device(entity_id, "turn_off")
        return result
    except Exception as e:
        logger.error(f"Turn off failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/device/{entity_id}/set_temperature")
async def set_device_temperature(entity_id: str, temperature: float):
    """Set temperature for a climate device"""
    try:
        ha = await get_home_assistant()
        if not ha.initialized:
            raise HTTPException(status_code=503, detail="Home Assistant not initialized")
        
        result = await ha.control_device(entity_id, "set_temperature", temperature=temperature)
        return result
    except Exception as e:
        logger.error(f"Set temperature failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/device/{entity_id}/set_brightness")
async def set_device_brightness(entity_id: str, brightness: int):
    """Set brightness for a light (0-255)"""
    try:
        ha = await get_home_assistant()
        if not ha.initialized:
            raise HTTPException(status_code=503, detail="Home Assistant not initialized")
        
        if not 0 <= brightness <= 255:
            raise HTTPException(status_code=400, detail="Brightness must be between 0 and 255")
        
        result = await ha.control_device(entity_id, "set_brightness", brightness=brightness)
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Set brightness failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/device/{entity_id}/set_color")
async def set_device_color(entity_id: str, color: List[int]):
    """Set color for a light (RGB values)"""
    try:
        ha = await get_home_assistant()
        if not ha.initialized:
            raise HTTPException(status_code=503, detail="Home Assistant not initialized")
        
        if len(color) != 3 or not all(0 <= c <= 255 for c in color):
            raise HTTPException(status_code=400, detail="Color must be 3 RGB values between 0 and 255")
        
        result = await ha.control_device(entity_id, "set_color", color=color)
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Set color failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Automation Management Endpoints
@router.get("/automations")
async def get_all_automations():
    """Get all Home Assistant automations"""
    try:
        ha = await get_home_assistant()
        if not ha.initialized:
            raise HTTPException(status_code=503, detail="Home Assistant not initialized")
        
        automations_summary = await ha.get_automations_summary()
        return automations_summary
    except Exception as e:
        logger.error(f"Failed to get automations: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/automation/{automation_id}")
async def get_automation_status(automation_id: str):
    """Get status of a specific automation"""
    try:
        ha = await get_home_assistant()
        if not ha.initialized:
            raise HTTPException(status_code=503, detail="Home Assistant not initialized")
        
        automation_status = await ha.api.get_automation_status(automation_id)
        if automation_status is None:
            raise HTTPException(status_code=404, detail=f"Automation {automation_id} not found")
        
        return {
            "automation_id": automation_id,
            "status": automation_status
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get automation status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/automation/trigger")
async def trigger_automation(request: AutomationTriggerRequest):
    """Trigger a Home Assistant automation"""
    try:
        ha = await get_home_assistant()
        if not ha.initialized:
            raise HTTPException(status_code=503, detail="Home Assistant not initialized")
        
        result = await ha.trigger_automation(request.automation_id)
        return result
    except Exception as e:
        logger.error(f"Automation trigger failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/automation/{automation_id}/trigger")
async def trigger_automation_by_id(automation_id: str):
    """Trigger a specific automation by ID"""
    try:
        ha = await get_home_assistant()
        if not ha.initialized:
            raise HTTPException(status_code=503, detail="Home Assistant not initialized")
        
        result = await ha.trigger_automation(automation_id)
        return result
    except Exception as e:
        logger.error(f"Automation trigger failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Search and Discovery Endpoints
@router.post("/search/devices")
async def search_devices(request: DeviceSearchRequest):
    """Search for devices with filters"""
    try:
        ha = await get_home_assistant()
        if not ha.initialized:
            raise HTTPException(status_code=503, detail="Home Assistant not initialized")
        
        devices = []
        for device in ha.api.devices.values():
            # Apply filters
            if request.domain and device.domain != request.domain:
                continue
            if request.name_contains and request.name_contains.lower() not in device.friendly_name.lower():
                continue
            if request.state and device.state != request.state:
                continue
            
            devices.append({
                "entity_id": device.entity_id,
                "name": device.friendly_name,
                "domain": device.domain,
                "state": device.state,
                "attributes": device.attributes
            })
        
        return DeviceSearchResponse(
            devices=devices,
            total_found=len(devices),
            filters_applied={
                "domain": request.domain,
                "name_contains": request.name_contains,
                "state": request.state
            }
        )
    except Exception as e:
        logger.error(f"Device search failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Utility Endpoints
@router.get("/discover")
async def discover_ha_instances():
    """Discover Home Assistant instances on the network"""
    try:
        ha = await get_home_assistant()
        instances = await ha.discovery.discover_instances()
        
        return {
            "discovered_instances": [
                {
                    "base_url": instance.base_url,
                    "port": instance.port,
                    "ssl": instance.ssl
                }
                for instance in instances
            ],
            "total_found": len(instances)
        }
    except Exception as e:
        logger.error(f"Discovery failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/system-info")
async def get_system_info():
    """Get Home Assistant system information"""
    try:
        ha = await get_home_assistant()
        if not ha.initialized:
            raise HTTPException(status_code=503, detail="Home Assistant not initialized")
        
        system_info = await ha.api.get_system_info()
        return system_info
    except Exception as e:
        logger.error(f"Failed to get system info: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Chat Integration Endpoint
@router.post("/chat/command")
async def process_ha_chat_command(command: str):
    """Process natural language commands for Home Assistant"""
    try:
        ha = await get_home_assistant()
        if not ha.initialized:
            return {
                "success": False,
                "message": "Home Assistant not initialized. Please run the initialization first.",
                "suggestion": "Try saying: 'Initialize Home Assistant' or 'Connect to Home Assistant'"
            }
        
        # Parse the command and determine action
        command_lower = command.lower()
        
        # Device control commands
        if "turn on" in command_lower or "switch on" in command_lower:
            # Extract device name and perform action
            return await _handle_turn_on_command(ha, command)
        elif "turn off" in command_lower or "switch off" in command_lower:
            return await _handle_turn_off_command(ha, command)
        elif "set temperature" in command_lower or "change temperature" in command_lower:
            return await _handle_temperature_command(ha, command)
        elif "set brightness" in command_lower or "dim" in command_lower or "brighten" in command_lower:
            return await _handle_brightness_command(ha, command)
        elif "list devices" in command_lower or "show devices" in command_lower:
            return await _handle_list_devices_command(ha)
        elif "list automations" in command_lower or "show automations" in command_lower:
            return await _handle_list_automations_command(ha)
        elif "trigger" in command_lower and "automation" in command_lower:
            return await _handle_trigger_automation_command(ha, command)
        else:
            return {
                "success": False,
                "message": f"I don't understand the command: '{command}'",
                "suggestions": [
                    "Try: 'Turn on the lights'",
                    "Try: 'Set temperature to 72 degrees'",
                    "Try: 'List all devices'",
                    "Try: 'Show automations'"
                ]
            }
            
    except Exception as e:
        logger.error(f"Chat command processing failed: {e}")
        return {
            "success": False,
            "error": str(e)
        }

async def _handle_turn_on_command(ha: HomeAssistantIntegration, command: str) -> Dict[str, Any]:
    """Handle turn on commands"""
    # Simple device name extraction (can be enhanced with NLP)
    devices = await ha.get_devices_summary()
    
    # Look for lights first
    lights = devices.get("lights", [])
    if lights:
        # Turn on the first light (or implement smarter selection)
        light = lights[0]
        result = await ha.control_device(light["entity_id"], "turn_on")
        return {
            "success": True,
            "message": f"Turning on {light['name']}",
            "action": "turn_on",
            "device": light["name"],
            "result": result
        }
    
    # If no lights, try switches
    switches = devices.get("switches", [])
    if switches:
        switch = switches[0]
        result = await ha.control_device(switch["entity_id"], "turn_on")
        return {
            "success": True,
            "message": f"Turning on {switch['name']}",
            "action": "turn_on",
            "device": switch["name"],
            "result": result
        }
    
    return {
        "success": False,
        "message": "No controllable devices found to turn on"
    }

async def _handle_turn_off_command(ha: HomeAssistantIntegration, command: str) -> Dict[str, Any]:
    """Handle turn off commands"""
    devices = await ha.get_devices_summary()
    
    lights = devices.get("lights", [])
    if lights:
        light = lights[0]
        result = await ha.control_device(light["entity_id"], "turn_off")
        return {
            "success": True,
            "message": f"Turning off {light['name']}",
            "action": "turn_off",
            "device": light["name"],
            "result": result
        }
    
    # If no lights, try switches
    switches = devices.get("switches", [])
    if switches:
        switch = switches[0]
        result = await ha.control_device(switch["entity_id"], "turn_off")
        return {
            "success": True,
            "message": f"Turning off {switch['name']}",
            "action": "turn_off",
            "device": switch["name"],
            "result": result
        }
    
    return {
        "success": False,
        "message": "No controllable devices found to turn off"
    }

async def _handle_temperature_command(ha: HomeAssistantIntegration, command: str) -> Dict[str, Any]:
    """Handle temperature commands"""
    # Extract temperature value (simple regex could be enhanced)
    import re
    temp_match = re.search(r'(\d+)', command)
    if temp_match:
        temperature = float(temp_match.group(1))
        
        devices = await ha.get_devices_summary()
        climate_devices = devices.get("climate", [])
        
        if climate_devices:
            climate = climate_devices[0]
            result = await ha.control_device(climate["entity_id"], "set_temperature", temperature=temperature)
            return {
                "success": True,
                "message": f"Setting temperature to {temperature}°F",
                "action": "set_temperature",
                "device": climate["name"],
                "temperature": temperature,
                "result": result
            }
    
    return {
        "success": False,
        "message": "Could not find temperature value or climate device"
    }

async def _handle_brightness_command(ha: HomeAssistantIntegration, command: str) -> Dict[str, Any]:
    """Handle brightness commands"""
    import re
    brightness_match = re.search(r'(\d+)', command)
    if brightness_match:
        brightness = int(brightness_match.group(1))
        brightness = max(0, min(255, brightness))  # Clamp to valid range
        
        devices = await ha.get_devices_summary()
        lights = devices.get("lights", [])
        
        if lights:
            light = lights[0]
            result = await ha.control_device(light["entity_id"], "set_brightness", brightness=brightness)
            return {
                "success": True,
                "message": f"Setting brightness to {brightness}",
                "action": "set_brightness",
                "device": light["name"],
                "brightness": brightness,
                "result": result
            }
    
    return {
        "success": False,
        "message": "Could not find brightness value or light device"
    }

async def _handle_list_devices_command(ha: HomeAssistantIntegration) -> Dict[str, Any]:
    """Handle list devices command"""
    devices_summary = await ha.get_devices_summary()
    return {
        "success": True,
        "message": f"Found {devices_summary['total_devices']} devices",
        "data": devices_summary
    }

async def _handle_list_automations_command(ha: HomeAssistantIntegration) -> Dict[str, Any]:
    """Handle list automations command"""
    automations_summary = await ha.get_automations_summary()
    return {
        "success": True,
        "message": f"Found {automations_summary['total_automations']} automations",
        "data": automations_summary
    }

async def _handle_trigger_automation_command(ha: HomeAssistantIntegration, command: str) -> Dict[str, Any]:
    """Handle trigger automation command"""
    # Simple automation name extraction
    automations = await ha.get_automations_summary()
    automation_list = automations.get("automations", [])
    
    if automation_list:
        automation = automation_list[0]  # Use first automation
        result = await ha.trigger_automation(automation["id"])
        return {
            "success": True,
            "message": f"Triggering automation: {automation['name']}",
            "automation": automation["name"],
            "result": result
        }
    
    return {
        "success": False,
        "message": "No automations found to trigger"
    }
