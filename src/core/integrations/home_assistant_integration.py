#!/usr/bin/env python3
"""
Autonomous Home Assistant Integration
Automatically discovers, connects, and integrates with Home Assistant
"""

import asyncio
import json
import logging
import socket
import requests
import websockets
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import aiohttp
import yaml
import os
from pathlib import Path

logger = logging.getLogger(__name__)

@dataclass
class HADevice:
    """Home Assistant device representation"""
    entity_id: str
    name: str
    state: str
    attributes: Dict[str, Any]
    device_class: Optional[str] = None
    domain: str = ""
    friendly_name: str = ""

@dataclass
class HAAutomation:
    """Home Assistant automation representation"""
    automation_id: str
    name: str
    description: str
    trigger: Dict[str, Any]
    action: List[Dict[str, Any]]
    condition: List[Dict[str, Any]]
    enabled: bool = True

@dataclass
class HAConfig:
    """Home Assistant configuration"""
    base_url: str
    token: Optional[str] = None
    port: int = 8123
    ssl: bool = False
    verify_ssl: bool = True
    timeout: int = 10

class HomeAssistantDiscovery:
    """Autonomous Home Assistant discovery and connection"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.discovered_instances = []
        self.config = None
        
    async def discover_instances(self) -> List[HAConfig]:
        """Automatically discover Home Assistant instances"""
        self.logger.info("🔍 Discovering Home Assistant instances...")
        
        instances = []
        
        # Common Home Assistant ports and URLs
        discovery_targets = [
            # Local instances (prioritize our local setup)
            ("localhost", 8123),
            ("127.0.0.1", 8123),
            ("homeassistant.local", 8123),
            ("hassio.local", 8123),
            
            # Docker/container instances
            ("homeassistant", 8123),
            ("hass", 8123),
            ("ha", 8123),
            
            # Common network ranges (limited to avoid long scans)
            ("192.168.1.100", 8123),
            ("192.168.1.101", 8123),
            ("192.168.0.100", 8123),
            ("192.168.0.101", 8123),
        ]
        
        # Test each target
        for host, port in discovery_targets:
            try:
                if await self._test_ha_instance(host, port):
                    config = HAConfig(
                        base_url=f"http://{host}:{port}",
                        port=port,
                        ssl=False
                    )
                    instances.append(config)
                    self.logger.info(f"✅ Found Home Assistant at {host}:{port}")
            except Exception as e:
                self.logger.debug(f"❌ {host}:{port} - {e}")
                continue
        
        # Test HTTPS instances
        for host, port in discovery_targets:
            try:
                if await self._test_ha_instance(host, port, ssl=True):
                    config = HAConfig(
                        base_url=f"https://{host}:{port}",
                        port=port,
                        ssl=True
                    )
                    instances.append(config)
                    self.logger.info(f"✅ Found Home Assistant (HTTPS) at {host}:{port}")
            except Exception as e:
                self.logger.debug(f"❌ HTTPS {host}:{port} - {e}")
                continue
        
        self.discovered_instances = instances
        return instances
    
    async def _test_ha_instance(self, host: str, port: int, ssl: bool = False) -> bool:
        """Test if a Home Assistant instance is running at the given address"""
        try:
            protocol = "https" if ssl else "http"
            url = f"{protocol}://{host}:{port}/api/"
            
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=3)) as session:
                async with session.get(url) as response:
                    if response.status == 401:  # Unauthorized but HA is there
                        return True
                    elif response.status == 200:
                        try:
                            data = await response.json()
                            if "message" in data and "Home Assistant" in data["message"]:
                                return True
                        except:
                            # If JSON parsing fails but we got 200, it's still likely HA
                            return True
        except Exception:
            pass
        return False
    
    async def auto_configure(self) -> Optional[HAConfig]:
        """Automatically configure Home Assistant connection"""
        instances = await self.discover_instances()
        
        if not instances:
            self.logger.warning("⚠️ No Home Assistant instances found")
            return None
        
        # Try to get a token for the first instance
        for instance in instances:
            try:
                token = await self._get_long_lived_token(instance)
                if token:
                    instance.token = token
                    self.config = instance
                    self.logger.info(f"✅ Auto-configured Home Assistant at {instance.base_url}")
                    return instance
            except Exception as e:
                self.logger.debug(f"❌ Failed to get token for {instance.base_url}: {e}")
                continue
        
        # If no token, return the first instance without token
        self.config = instances[0]
        self.logger.info(f"⚠️ Found Home Assistant at {self.config.base_url} but no token available")
        return self.config
    
    async def _get_long_lived_token(self, config: HAConfig) -> Optional[str]:
        """Attempt to get a long-lived access token"""
        # This would typically require user interaction
        # For now, we'll try common locations or return None
        token_paths = [
            Path.home() / ".homeassistant" / "long_lived_token.txt",
            Path.home() / ".homeassistant" / "token.txt",
            Path("/config") / "long_lived_token.txt",
            Path("/config") / "token.txt",
        ]
        
        for token_path in token_paths:
            if token_path.exists():
                try:
                    token = token_path.read_text().strip()
                    if token and len(token) > 20:  # Basic validation
                        return token
                except Exception:
                    continue
        
        return None

class HomeAssistantAPI:
    """Home Assistant API client with autonomous capabilities"""
    
    def __init__(self, config: HAConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.session = None
        self.websocket = None
        self.devices = {}
        self.automations = {}
        self.states = {}
        
    async def initialize(self) -> bool:
        """Initialize the Home Assistant API connection"""
        try:
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=self.config.timeout),
                connector=aiohttp.TCPConnector(ssl=self.config.verify_ssl)
            )
            
            # Test connection
            if await self._test_connection():
                # Load initial data
                await self._load_devices()
                await self._load_automations()
                await self._load_states()
                
                self.logger.info("✅ Home Assistant API initialized successfully")
                return True
            else:
                self.logger.error("❌ Failed to connect to Home Assistant")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Home Assistant API initialization failed: {e}")
            return False
    
    async def _test_connection(self) -> bool:
        """Test the Home Assistant API connection"""
        try:
            headers = {}
            if self.config.token:
                headers["Authorization"] = f"Bearer {self.config.token}"
            
            url = f"{self.config.base_url}/api/"
            async with self.session.get(url, headers=headers) as response:
                if response.status in [200, 401]:  # 401 is OK if no token
                    return True
        except Exception as e:
            self.logger.debug(f"Connection test failed: {e}")
        return False
    
    async def _load_devices(self):
        """Load all devices from Home Assistant"""
        try:
            headers = {}
            if self.config.token:
                headers["Authorization"] = f"Bearer {self.config.token}"
            
            url = f"{self.config.base_url}/api/states"
            async with self.session.get(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    for entity in data:
                        device = HADevice(
                            entity_id=entity["entity_id"],
                            name=entity["entity_id"],
                            state=entity["state"],
                            attributes=entity.get("attributes", {}),
                            device_class=entity.get("attributes", {}).get("device_class"),
                            domain=entity["entity_id"].split(".")[0],
                            friendly_name=entity.get("attributes", {}).get("friendly_name", entity["entity_id"])
                        )
                        self.devices[entity["entity_id"]] = device
                        
            self.logger.info(f"📱 Loaded {len(self.devices)} devices")
        except Exception as e:
            self.logger.error(f"❌ Failed to load devices: {e}")
    
    async def _load_automations(self):
        """Load all automations from Home Assistant"""
        try:
            headers = {}
            if self.config.token:
                headers["Authorization"] = f"Bearer {self.config.token}"
            
            url = f"{self.config.base_url}/api/config/automation/config"
            async with self.session.get(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    for automation in data:
                        ha_automation = HAAutomation(
                            automation_id=automation.get("id", ""),
                            name=automation.get("alias", "Unnamed"),
                            description=automation.get("description", ""),
                            trigger=automation.get("trigger", {}),
                            action=automation.get("action", []),
                            condition=automation.get("condition", []),
                            enabled=automation.get("enabled", True)
                        )
                        self.automations[automation.get("id", "")] = ha_automation
                        
            self.logger.info(f"🤖 Loaded {len(self.automations)} automations")
        except Exception as e:
            self.logger.error(f"❌ Failed to load automations: {e}")
    
    async def _load_states(self):
        """Load current states from Home Assistant"""
        try:
            headers = {}
            if self.config.token:
                headers["Authorization"] = f"Bearer {self.config.token}"
            
            url = f"{self.config.base_url}/api/states"
            async with self.session.get(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    for entity in data:
                        self.states[entity["entity_id"]] = {
                            "state": entity["state"],
                            "attributes": entity.get("attributes", {}),
                            "last_changed": entity.get("last_changed"),
                            "last_updated": entity.get("last_updated")
                        }
                        
            self.logger.info(f"📊 Loaded {len(self.states)} states")
        except Exception as e:
            self.logger.error(f"❌ Failed to load states: {e}")
    
    async def get_devices_by_domain(self, domain: str) -> List[HADevice]:
        """Get devices filtered by domain (light, switch, sensor, etc.)"""
        return [device for device in self.devices.values() if device.domain == domain]
    
    async def get_device_state(self, entity_id: str) -> Optional[Dict[str, Any]]:
        """Get current state of a specific device"""
        return self.states.get(entity_id)
    
    async def call_service(self, domain: str, service: str, entity_id: str = None, **kwargs) -> bool:
        """Call a Home Assistant service"""
        try:
            headers = {}
            if self.config.token:
                headers["Authorization"] = f"Bearer {self.config.token}"
            headers["Content-Type"] = "application/json"
            
            service_data = kwargs
            if entity_id:
                service_data["entity_id"] = entity_id
            
            url = f"{self.config.base_url}/api/services/{domain}/{service}"
            async with self.session.post(url, headers=headers, json=service_data) as response:
                if response.status in [200, 201]:
                    self.logger.info(f"✅ Called {domain}.{service} for {entity_id}")
                    return True
                else:
                    self.logger.error(f"❌ Failed to call {domain}.{service}: {response.status}")
                    return False
                    
        except Exception as e:
            self.logger.error(f"❌ Service call failed: {e}")
            return False
    
    async def turn_on(self, entity_id: str, **kwargs) -> bool:
        """Turn on a device"""
        domain = entity_id.split(".")[0]
        return await self.call_service(domain, "turn_on", entity_id, **kwargs)
    
    async def turn_off(self, entity_id: str, **kwargs) -> bool:
        """Turn off a device"""
        domain = entity_id.split(".")[0]
        return await self.call_service(domain, "turn_off", entity_id, **kwargs)
    
    async def set_temperature(self, entity_id: str, temperature: float) -> bool:
        """Set temperature for a climate device"""
        return await self.call_service("climate", "set_temperature", entity_id, temperature=temperature)
    
    async def set_brightness(self, entity_id: str, brightness: int) -> bool:
        """Set brightness for a light (0-255)"""
        return await self.call_service("light", "turn_on", entity_id, brightness=brightness)
    
    async def set_color(self, entity_id: str, rgb_color: List[int]) -> bool:
        """Set color for a light"""
        return await self.call_service("light", "turn_on", entity_id, rgb_color=rgb_color)
    
    async def get_automation_status(self, automation_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a specific automation"""
        return self.automations.get(automation_id)
    
    async def trigger_automation(self, automation_id: str) -> bool:
        """Trigger an automation"""
        return await self.call_service("automation", "trigger", automation_id)
    
    async def enable_automation(self, automation_id: str) -> bool:
        """Enable an automation"""
        return await self.call_service("automation", "enable", automation_id)
    
    async def disable_automation(self, automation_id: str) -> bool:
        """Disable an automation"""
        return await self.call_service("automation", "disable", automation_id)
    
    async def get_system_info(self) -> Dict[str, Any]:
        """Get Home Assistant system information"""
        try:
            headers = {}
            if self.config.token:
                headers["Authorization"] = f"Bearer {self.config.token}"
            
            url = f"{self.config.base_url}/api/config"
            async with self.session.get(url, headers=headers) as response:
                if response.status == 200:
                    return await response.json()
        except Exception as e:
            self.logger.error(f"❌ Failed to get system info: {e}")
        return {}
    
    async def close(self):
        """Close the API connection"""
        if self.session:
            await self.session.close()
        if self.websocket:
            await self.websocket.close()

class HomeAssistantIntegration:
    """Main Home Assistant integration class"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.discovery = HomeAssistantDiscovery()
        self.api = None
        self.initialized = False
        
    async def auto_initialize(self) -> bool:
        """Automatically discover and initialize Home Assistant"""
        try:
            self.logger.info("🏠 Starting autonomous Home Assistant integration...")
            
            # Step 1: Discover instances
            config = await self.discovery.auto_configure()
            if not config:
                self.logger.warning("⚠️ No Home Assistant instances found")
                return False
            
            # Step 2: Initialize API
            self.api = HomeAssistantAPI(config)
            if await self.api.initialize():
                self.initialized = True
                self.logger.info("✅ Home Assistant integration initialized successfully")
                return True
            else:
                self.logger.error("❌ Failed to initialize Home Assistant API")
                return False
                
        except Exception as e:
            self.logger.error(f"❌ Home Assistant integration failed: {e}")
            return False
    
    async def get_devices_summary(self) -> Dict[str, Any]:
        """Get a summary of all devices"""
        if not self.initialized:
            return {"error": "Home Assistant not initialized"}
        
        summary = {
            "total_devices": len(self.api.devices),
            "domains": {},
            "lights": [],
            "switches": [],
            "sensors": [],
            "climate": [],
            "media_players": []
        }
        
        # Count by domain
        for device in self.api.devices.values():
            domain = device.domain
            if domain not in summary["domains"]:
                summary["domains"][domain] = 0
            summary["domains"][domain] += 1
            
            # Categorize common device types
            if domain == "light":
                summary["lights"].append({
                    "entity_id": device.entity_id,
                    "name": device.friendly_name,
                    "state": device.state,
                    "brightness": device.attributes.get("brightness")
                })
            elif domain == "switch":
                summary["switches"].append({
                    "entity_id": device.entity_id,
                    "name": device.friendly_name,
                    "state": device.state
                })
            elif domain == "sensor":
                summary["sensors"].append({
                    "entity_id": device.entity_id,
                    "name": device.friendly_name,
                    "state": device.state,
                    "unit": device.attributes.get("unit_of_measurement")
                })
            elif domain == "climate":
                summary["climate"].append({
                    "entity_id": device.entity_id,
                    "name": device.friendly_name,
                    "state": device.state,
                    "temperature": device.attributes.get("temperature"),
                    "target_temperature": device.attributes.get("target_temp_high")
                })
            elif domain == "media_player":
                summary["media_players"].append({
                    "entity_id": device.entity_id,
                    "name": device.friendly_name,
                    "state": device.state,
                    "volume": device.attributes.get("volume_level")
                })
        
        return summary
    
    async def control_device(self, entity_id: str, action: str, **kwargs) -> Dict[str, Any]:
        """Control a device with the specified action"""
        if not self.initialized:
            return {"error": "Home Assistant not initialized"}
        
        try:
            success = False
            if action == "turn_on":
                success = await self.api.turn_on(entity_id, **kwargs)
            elif action == "turn_off":
                success = await self.api.turn_off(entity_id, **kwargs)
            elif action == "set_temperature":
                temperature = kwargs.get("temperature")
                if temperature:
                    success = await self.api.set_temperature(entity_id, temperature)
            elif action == "set_brightness":
                brightness = kwargs.get("brightness")
                if brightness:
                    success = await self.api.set_brightness(entity_id, brightness)
            elif action == "set_color":
                color = kwargs.get("color")
                if color:
                    success = await self.api.set_color(entity_id, color)
            
            if success:
                # Refresh device state
                await self.api._load_states()
                current_state = await self.api.get_device_state(entity_id)
                
                return {
                    "success": True,
                    "entity_id": entity_id,
                    "action": action,
                    "current_state": current_state
                }
            else:
                return {
                    "success": False,
                    "error": f"Failed to {action} {entity_id}"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_automations_summary(self) -> Dict[str, Any]:
        """Get a summary of all automations"""
        if not self.initialized:
            return {"error": "Home Assistant not initialized"}
        
        summary = {
            "total_automations": len(self.api.automations),
            "enabled": 0,
            "disabled": 0,
            "automations": []
        }
        
        for automation in self.api.automations.values():
            if automation.enabled:
                summary["enabled"] += 1
            else:
                summary["disabled"] += 1
                
            summary["automations"].append({
                "id": automation.automation_id,
                "name": automation.name,
                "description": automation.description,
                "enabled": automation.enabled
            })
        
        return summary
    
    async def trigger_automation(self, automation_id: str) -> Dict[str, Any]:
        """Trigger a specific automation"""
        if not self.initialized:
            return {"error": "Home Assistant not initialized"}
        
        try:
            success = await self.api.trigger_automation(automation_id)
            return {
                "success": success,
                "automation_id": automation_id,
                "message": "Automation triggered" if success else "Failed to trigger automation"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def close(self):
        """Close the integration"""
        if self.api:
            await self.api.close()
        self.initialized = False

# Global instance
ha_integration = HomeAssistantIntegration()

async def get_home_assistant() -> HomeAssistantIntegration:
    """Get the global Home Assistant integration instance"""
    if not ha_integration.initialized:
        await ha_integration.auto_initialize()
    return ha_integration
