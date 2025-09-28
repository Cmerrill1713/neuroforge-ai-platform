"""
Log Tailing System for Agentic LLM Core v0.1

This module provides real-time log monitoring with filtering, level control,
and follow capabilities for system debugging and monitoring.

Created: 2024-09-24
Status: Draft
"""

from __future__ import annotations

import asyncio
import re
import time
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, AsyncGenerator
from uuid import uuid4

from pydantic import BaseModel, Field, validator


# ============================================================================
# Data Models
# ============================================================================

class LogLevel(str, Enum):
    """Log levels in order of severity."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class LogEntry(BaseModel):
    """Parsed log entry."""
    timestamp: datetime = Field(..., description="Log timestamp")
    level: LogLevel = Field(..., description="Log level")
    component: str = Field(..., description="Component that generated the log")
    message: str = Field(..., description="Log message")
    raw_line: str = Field(..., description="Original log line")
    line_number: int = Field(..., description="Line number in file")
    file_path: str = Field(..., description="Source log file path")


class LogFilter(BaseModel):
    """Log filtering configuration."""
    level: Optional[LogLevel] = Field(None, description="Minimum log level to include")
    components: Optional[List[str]] = Field(None, description="Components to include (regex patterns)")
    exclude_components: Optional[List[str]] = Field(None, description="Components to exclude (regex patterns)")
    message_pattern: Optional[str] = Field(None, description="Message content pattern (regex)")
    exclude_pattern: Optional[str] = Field(None, description="Message content to exclude (regex)")
    time_range: Optional[tuple] = Field(None, description="Time range filter (start, end) timestamps")


class TailConfig(BaseModel):
    """Log tailing configuration."""
    log_files: List[str] = Field(..., description="Log files to monitor")
    follow: bool = Field(False, description="Follow new log entries in real-time")
    lines: int = Field(50, ge=1, le=10000, description="Number of recent lines to show initially")
    filter_config: Optional[LogFilter] = Field(None, description="Log filtering configuration")
    refresh_interval: float = Field(1.0, ge=0.1, le=10.0, description="Refresh interval for follow mode")
    max_buffer_size: int = Field(1000, ge=100, le=10000, description="Maximum buffer size for log entries")


class TailResult(BaseModel):
    """Log tailing result."""
    result_id: str = Field(default_factory=lambda: str(uuid4()), description="Result ID")
    config: TailConfig = Field(..., description="Configuration used")
    entries: List[LogEntry] = Field(default_factory=list, description="Matching log entries")
    total_entries: int = Field(0, description="Total entries processed")
    filtered_entries: int = Field(0, description="Entries that matched filters")
    processing_time_ms: float = Field(..., description="Processing time in milliseconds")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Result timestamp")


# ============================================================================
# Log Tailing System
# ============================================================================

class LogTailer:
    """Real-time log monitoring and filtering system."""
    
    def __init__(self, config: TailConfig):
        self.config = config
        self.log_pattern = re.compile(
            r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}) - (\w+) - (\w+) - (.+)'
        )
        self._running = False
        self._file_positions: Dict[str, int] = {}
    
    async def tail_logs(self) -> TailResult:
        """Tail logs based on configuration."""
        start_time = time.time()
        
        try:
            entries = []
            total_entries = 0
            
            # Read initial lines from each log file
            for log_file in self.config.log_files:
                file_entries = await self._read_log_file(log_file)
                entries.extend(file_entries)
                total_entries += len(file_entries)
            
            # Apply filters
            filtered_entries = self._apply_filters(entries)
            
            # Sort by timestamp
            filtered_entries.sort(key=lambda x: x.timestamp)
            
            # Limit to requested number of lines
            if len(filtered_entries) > self.config.lines:
                filtered_entries = filtered_entries[-self.config.lines:]
            
            processing_time = (time.time() - start_time) * 1000
            
            return TailResult(
                config=self.config,
                entries=filtered_entries,
                total_entries=total_entries,
                filtered_entries=len(filtered_entries),
                processing_time_ms=processing_time
            )
            
        except Exception as e:
            processing_time = (time.time() - start_time) * 1000
            return TailResult(
                config=self.config,
                entries=[],
                total_entries=0,
                filtered_entries=0,
                processing_time_ms=processing_time
            )
    
    async def follow_logs(self) -> AsyncGenerator[LogEntry, None]:
        """Follow logs in real-time."""
        self._running = True
        
        try:
            # Initialize file positions
            for log_file in self.config.log_files:
                if Path(log_file).exists():
                    self._file_positions[log_file] = Path(log_file).stat().st_size
            
            while self._running:
                new_entries = []
                
                for log_file in self.config.log_files:
                    if not Path(log_file).exists():
                        continue
                    
                    # Read new content
                    file_entries = await self._read_new_content(log_file)
                    new_entries.extend(file_entries)
                
                # Apply filters and yield new entries
                filtered_entries = self._apply_filters(new_entries)
                for entry in filtered_entries:
                    yield entry
                
                # Wait for next refresh
                await asyncio.sleep(self.config.refresh_interval)
                
        except Exception as e:
            # Yield error as a special log entry
            error_entry = LogEntry(
                timestamp=datetime.now(timezone.utc),
                level=LogLevel.ERROR,
                component="log_tailer",
                message=f"Follow mode error: {str(e)}",
                raw_line=f"ERROR - log_tailer - Follow mode error: {str(e)}",
                line_number=0,
                file_path="system"
            )
            yield error_entry
    
    def stop_follow(self):
        """Stop following logs."""
        self._running = False
    
    async def _read_log_file(self, log_file: str) -> List[LogEntry]:
        """Read log file and parse entries."""
        entries = []
        
        try:
            if not Path(log_file).exists():
                return entries
            
            with open(log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            for line_num, line in enumerate(lines, 1):
                entry = self._parse_log_line(line.strip(), log_file, line_num)
                if entry:
                    entries.append(entry)
            
        except Exception as e:
            # Create error entry
            error_entry = LogEntry(
                timestamp=datetime.now(timezone.utc),
                level=LogLevel.ERROR,
                component="log_tailer",
                message=f"Failed to read {log_file}: {str(e)}",
                raw_line=f"ERROR - log_tailer - Failed to read {log_file}: {str(e)}",
                line_number=0,
                file_path=log_file
            )
            entries.append(error_entry)
        
        return entries
    
    async def _read_new_content(self, log_file: str) -> List[LogEntry]:
        """Read new content from log file since last position."""
        entries = []
        
        try:
            if not Path(log_file).exists():
                return entries
            
            current_size = Path(log_file).stat().st_size
            last_position = self._file_positions.get(log_file, 0)
            
            if current_size <= last_position:
                return entries
            
            with open(log_file, 'r', encoding='utf-8') as f:
                f.seek(last_position)
                new_content = f.read()
            
            # Update position
            self._file_positions[log_file] = current_size
            
            # Parse new lines
            lines = new_content.strip().split('\n')
            for line_num, line in enumerate(lines, 1):
                if line.strip():
                    entry = self._parse_log_line(line.strip(), log_file, line_num)
                    if entry:
                        entries.append(entry)
            
        except Exception as e:
            # Create error entry
            error_entry = LogEntry(
                timestamp=datetime.now(timezone.utc),
                level=LogLevel.ERROR,
                component="log_tailer",
                message=f"Failed to read new content from {log_file}: {str(e)}",
                raw_line=f"ERROR - log_tailer - Failed to read new content from {log_file}: {str(e)}",
                line_number=0,
                file_path=log_file
            )
            entries.append(error_entry)
        
        return entries
    
    def _parse_log_line(self, line: str, file_path: str, line_number: int) -> Optional[LogEntry]:
        """Parse a single log line into LogEntry."""
        try:
            match = self.log_pattern.match(line)
            if not match:
                return None
            
            timestamp_str, level_str, component, message = match.groups()
            
            # Parse timestamp
            timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S,%f')
            
            # Parse level
            try:
                level = LogLevel(level_str)
            except ValueError:
                level = LogLevel.INFO
            
            return LogEntry(
                timestamp=timestamp,
                level=level,
                component=component,
                message=message,
                raw_line=line,
                line_number=line_number,
                file_path=file_path
            )
            
        except Exception:
            return None
    
    def _apply_filters(self, entries: List[LogEntry]) -> List[LogEntry]:
        """Apply filters to log entries."""
        if not self.config.filter_config:
            return entries
        
        filter_config = self.config.filter_config
        filtered_entries = []
        
        for entry in entries:
            # Level filter
            if filter_config.level:
                level_order = [LogLevel.DEBUG, LogLevel.INFO, LogLevel.WARNING, LogLevel.ERROR, LogLevel.CRITICAL]
                if level_order.index(entry.level) < level_order.index(filter_config.level):
                    continue
            
            # Component include filter
            if filter_config.components:
                if not any(re.search(pattern, entry.component, re.IGNORECASE) for pattern in filter_config.components):
                    continue
            
            # Component exclude filter
            if filter_config.exclude_components:
                if any(re.search(pattern, entry.component, re.IGNORECASE) for pattern in filter_config.exclude_components):
                    continue
            
            # Message pattern filter
            if filter_config.message_pattern:
                if not re.search(filter_config.message_pattern, entry.message, re.IGNORECASE):
                    continue
            
            # Exclude pattern filter
            if filter_config.exclude_pattern:
                if re.search(filter_config.exclude_pattern, entry.message, re.IGNORECASE):
                    continue
            
            # Time range filter
            if filter_config.time_range:
                start_time, end_time = filter_config.time_range
                if not (start_time <= entry.timestamp <= end_time):
                    continue
            
            filtered_entries.append(entry)
        
        return filtered_entries


# ============================================================================
# Main Function
# ============================================================================

async def main():
    """Main function for command-line usage."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Log Tailing System")
    parser.add_argument("--level", choices=[l.value for l in LogLevel], help="Minimum log level")
    parser.add_argument("--follow", action="store_true", help="Follow logs in real-time")
    parser.add_argument("--filter", help="Component filter (regex patterns separated by |)")
    parser.add_argument("--lines", type=int, default=50, help="Number of recent lines to show")
    parser.add_argument("--files", nargs="*", default=["logs/system.log", "logs/error.log"], help="Log files to monitor")
    parser.add_argument("--refresh", type=float, default=1.0, help="Refresh interval for follow mode")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    try:
        # Parse filter
        components = None
        if args.filter:
            components = args.filter.split("|")
        
        # Create filter configuration
        filter_config = LogFilter(
            level=LogLevel(args.level) if args.level else None,
            components=components
        )
        
        # Create tail configuration
        tail_config = TailConfig(
            log_files=args.files,
            follow=args.follow,
            lines=args.lines,
            filter_config=filter_config,
            refresh_interval=args.refresh
        )
        
        # Create log tailer
        tailer = LogTailer(tail_config)
        
        if args.follow:
            # Follow mode
            print(f"Following logs with filter: {args.filter or 'none'}")
            print(f"Level: {args.level or 'all'}")
            print("Press Ctrl+C to stop...")
            print("-" * 80)
            
            try:
                async for entry in tailer.follow_logs():
                    timestamp = entry.timestamp.strftime("%Y-%m-%d %H:%M:%S")
                    print(f"{timestamp} - {entry.level.value} - {entry.component} - {entry.message}")
            except KeyboardInterrupt:
                print("\nStopping log follow...")
                tailer.stop_follow()
        else:
            # One-time tail
            result = await tailer.tail_logs()
            
            print("\n" + "="*80)
            print("LOG TAIL RESULT")
            print("="*80)
            print(f"Result ID: {result.result_id}")
            print(f"Files: {', '.join(result.config.log_files)}")
            print(f"Total Entries: {result.total_entries}")
            print(f"Filtered Entries: {result.filtered_entries}")
            print(f"Processing Time: {result.processing_time_ms:.2f}ms")
            
            if result.config.filter_config:
                print(f"Filter Level: {result.config.filter_config.level or 'all'}")
                print(f"Filter Components: {result.config.filter_config.components or 'all'}")
            
            print(f"\n📋 Recent Log Entries:")
            print("-" * 80)
            
            for entry in result.entries:
                timestamp = entry.timestamp.strftime("%Y-%m-%d %H:%M:%S")
                print(f"{timestamp} - {entry.level.value} - {entry.component} - {entry.message}")
        
        return 0
        
    except Exception as e:
        print(f"Log tailing failed: {e}")
        return 1


if __name__ == "__main__":
    exit(asyncio.run(main()))
