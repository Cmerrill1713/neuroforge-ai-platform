#!/usr/bin/env python3
"""
Log Tailing CLI Interface

Provides a command-line interface matching the user's command format:
/logs.tail level:"INFO" follow:true filter:"runner|mcp|planner"
"""

import asyncio
import argparse
import logging
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.core.logging.log_tailer import LogTailer, TailConfig, LogFilter, LogLevel

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def parse_command_args(command_str: str) -> dict:
    """Parse command string into arguments."""
    args = {}
    
    # Remove the command prefix
    if command_str.startswith("/logs.tail "):
        command_str = command_str[9:]
    
    # Parse key:value pairs
    import re
    pattern = r'(\w+):"([^"]*)"'
    matches = re.findall(pattern, command_str)
    
    for key, value in matches:
        # Convert boolean strings
        if value.lower() in ['true', 'false']:
            args[key] = value.lower() == 'true'
        # Convert numeric strings
        elif value.isdigit():
            args[key] = int(value)
        else:
            args[key] = value
    
    return args


async def main():
    """Main function for CLI interface."""
    parser = argparse.ArgumentParser(description="Log Tailing CLI")
    parser.add_argument("command", nargs="*", help="Command string to parse")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    try:
        # Parse command if provided
        if args.command:
            command_str = " ".join(args.command)
            parsed_args = parse_command_args(command_str)
        else:
            # Interactive mode
            command_str = input("Enter command: ")
            parsed_args = parse_command_args(command_str)
        
        # Parse filter
        components = None
        if parsed_args.get("filter"):
            components = parsed_args["filter"].split("|")
        
        # Create filter configuration
        filter_config = LogFilter(
            level=LogLevel(parsed_args["level"]) if parsed_args.get("level") else None,
            components=components
        )
        
        # Create tail configuration
        tail_config = TailConfig(
            log_files=["logs/system.log", "logs/error.log"],
            follow=parsed_args.get("follow", False),
            lines=parsed_args.get("lines", 50),
            filter_config=filter_config,
            refresh_interval=parsed_args.get("refresh", 1.0)
        )
        
        # Create log tailer
        tailer = LogTailer(tail_config)
        
        if parsed_args.get("follow"):
            # Follow mode
            print(f"Following logs with filter: {parsed_args.get('filter', 'none')}")
            print(f"Level: {parsed_args.get('level', 'all')}")
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
        logger.error(f"Log tailing failed: {e}")
        return 1


if __name__ == "__main__":
    exit(asyncio.run(main()))
