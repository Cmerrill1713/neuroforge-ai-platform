#!/usr/bin/env python3
"""
Event Tracker for NeuroForge
Provides centralized logging and event tracking for AI interactions
"""

import asyncio
import json
import logging
import time
from typing import Dict, Any, Optional, List
from datetime import datetime
from dataclasses import dataclass, asdict
from pathlib import Path

logger = logging.getLogger(__name__)

@dataclass
class TrackedEvent:
    """A tracked event with metadata"""
    event_type: str
    timestamp: str
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    request_id: Optional[str] = None
    model_name: Optional[str] = None
    prompt_length: Optional[int] = None
    response_length: Optional[int] = None
    processing_time: Optional[float] = None
    success: bool = True
    error_message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class EventTracker:
    """
    Centralized event tracking for NeuroForge operations
    """

    def __init__(self, log_file: Optional[str] = None, enable_console: bool = True):
        self.log_file = log_file or "logs/neuroforge_events.log"
        self.enable_console = enable_console
        self.event_queue: List[TrackedEvent] = []
        self._ensure_log_directory()

    def _ensure_log_directory(self):
        """Ensure the log directory exists"""
        log_path = Path(self.log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

    async def log_event(self, event_data: Dict[str, Any]) -> None:
        """
        Log an event asynchronously

        Args:
            event_data: Event data dictionary
        """
        try:
            # Create tracked event
            event = TrackedEvent(
                event_type=event_data.get("event_type", "unknown"),
                timestamp=event_data.get("timestamp", datetime.now().isoformat()),
                user_id=event_data.get("user_id"),
                session_id=event_data.get("session_id"),
                request_id=event_data.get("request_id"),
                model_name=event_data.get("model"),
                prompt_length=event_data.get("message_length"),
                response_length=event_data.get("response_length"),
                processing_time=event_data.get("processing_time"),
                success=event_data.get("success", True),
                error_message=event_data.get("error_message"),
                metadata=event_data.get("metadata", {})
            )

            # Add to queue for async processing
            self.event_queue.append(event)

            # Process queue
            await self._process_event_queue()

        except Exception as e:
            logger.error(f"Failed to log event: {e}")

    async def _process_event_queue(self) -> None:
        """Process queued events"""
        while self.event_queue:
            event = self.event_queue.pop(0)
            await self._write_event(event)

    async def _write_event(self, event: TrackedEvent) -> None:
        """Write event to log file and console"""
        try:
            # Convert to JSON
            event_dict = asdict(event)
            event_json = json.dumps(event_dict, default=str)

            # Write to file
            async with asyncio.Lock():  # Simple file lock
                with open(self.log_file, 'a', encoding='utf-8') as f:
                    f.write(f"{event_json}\n")

            # Console output if enabled
            if self.enable_console:
                status = "✅" if event.success else "❌"
                logger.info(f"{status} {event.event_type}: {event.request_id or 'unknown'} "
                           f"({event.processing_time:.2f}s)" if event.processing_time else "")

        except Exception as e:
            logger.error(f"Failed to write event: {e}")

    async def get_recent_events(
        self,
        event_type: Optional[str] = None,
        limit: int = 100
    ) -> List[TrackedEvent]:
        """
        Get recent events from log file

        Args:
            event_type: Filter by event type
            limit: Maximum number of events to return

        Returns:
            List of recent events
        """
        try:
            events = []

            if not Path(self.log_file).exists():
                return events

            with open(self.log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()[-limit:]  # Get last N lines

            for line in reversed(lines):  # Most recent first
                try:
                    event_dict = json.loads(line.strip())
                    event = TrackedEvent(**event_dict)

                    if event_type is None or event.event_type == event_type:
                        events.append(event)

                    if len(events) >= limit:
                        break

                except json.JSONDecodeError:
                    continue

            return events

        except Exception as e:
            logger.error(f"Failed to read events: {e}")
            return []

    async def get_event_stats(self) -> Dict[str, Any]:
        """Get statistics about logged events"""
        try:
            events = await self.get_recent_events(limit=1000)

            stats = {
                "total_events": len(events),
                "event_types": {},
                "success_rate": 0.0,
                "avg_processing_time": 0.0,
                "models_used": set()
            }

            processing_times = []
            success_count = 0

            for event in events:
                # Count event types
                stats["event_types"][event.event_type] = stats["event_types"].get(event.event_type, 0) + 1

                # Track success
                if event.success:
                    success_count += 1

                # Track processing times
                if event.processing_time:
                    processing_times.append(event.processing_time)

                # Track models
                if event.model_name:
                    stats["models_used"].add(event.model_name)

            # Calculate rates
            if events:
                stats["success_rate"] = success_count / len(events)

            if processing_times:
                stats["avg_processing_time"] = sum(processing_times) / len(processing_times)

            stats["models_used"] = list(stats["models_used"])

            return stats

        except Exception as e:
            logger.error(f"Failed to calculate stats: {e}")
            return {}

# Global instance
event_tracker = EventTracker()

# Convenience function
async def log_event(event_data: Dict[str, Any]) -> None:
    """Convenience function for logging events"""
    await event_tracker.log_event(event_data)

# Export main classes and functions
__all__ = [
    "TrackedEvent",
    "EventTracker",
    "event_tracker",
    "log_event"
]
