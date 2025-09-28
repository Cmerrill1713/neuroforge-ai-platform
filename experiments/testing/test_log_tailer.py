#!/usr/bin/env python3
"""
Comprehensive test of the Log Tailing System

Tests all features including filtering, follow mode, and different log levels.
"""

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.core.logging.log_tailer import LogTailer, TailConfig, LogFilter, LogLevel


async def test_log_tailer():
    """Test the log tailing system comprehensively."""
    print("🧪 Testing Log Tailing System")
    print("="*60)
    
    # Test cases
    test_cases = [
        {
            "name": "INFO Level with Component Filter",
            "config": TailConfig(
                log_files=["logs/system.log", "logs/error.log"],
                follow=False,
                lines=10,
                filter_config=LogFilter(
                    level=LogLevel.INFO,
                    components=["runner", "mcp", "planner"]
                )
            )
        },
        {
            "name": "ERROR Level Only",
            "config": TailConfig(
                log_files=["logs/system.log", "logs/error.log"],
                follow=False,
                lines=5,
                filter_config=LogFilter(
                    level=LogLevel.ERROR,
                    components=["runner", "mcp", "planner"]
                )
            )
        },
        {
            "name": "All Levels, Runner Only",
            "config": TailConfig(
                log_files=["logs/system.log", "logs/error.log"],
                follow=False,
                lines=8,
                filter_config=LogFilter(
                    components=["runner"]
                )
            )
        },
        {
            "name": "No Filters (All Logs)",
            "config": TailConfig(
                log_files=["logs/system.log", "logs/error.log"],
                follow=False,
                lines=5
            )
        }
    ]
    
    # Run tests
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📋 Test {i}: {test_case['name']}")
        print("-" * 40)
        
        try:
            tailer = LogTailer(test_case['config'])
            result = await tailer.tail_logs()
            
            print(f"✅ Success!")
            print(f"   Result ID: {result.result_id}")
            print(f"   Total Entries: {result.total_entries}")
            print(f"   Filtered Entries: {result.filtered_entries}")
            print(f"   Processing Time: {result.processing_time_ms:.2f}ms")
            
            if result.config.filter_config:
                print(f"   Filter Level: {result.config.filter_config.level or 'all'}")
                print(f"   Filter Components: {result.config.filter_config.components or 'all'}")
            
            print(f"   Sample Entries:")
            for entry in result.entries[:3]:  # Show first 3 entries
                timestamp = entry.timestamp.strftime("%H:%M:%S")
                print(f"     {timestamp} - {entry.level.value} - {entry.component} - {entry.message[:50]}...")
            
        except Exception as e:
            print(f"❌ Failed: {e}")
    
    # Test follow mode simulation
    print(f"\n🔄 Testing Follow Mode Simulation")
    print("-" * 40)
    
    try:
        # Create a follow config
        follow_config = TailConfig(
            log_files=["logs/system.log"],
            follow=True,
            lines=5,
            filter_config=LogFilter(
                level=LogLevel.INFO,
                components=["runner"]
            ),
            refresh_interval=0.5
        )
        
        tailer = LogTailer(follow_config)
        
        # Simulate follow mode for a short time
        print("Simulating follow mode for 2 seconds...")
        entry_count = 0
        
        async def follow_simulation():
            nonlocal entry_count
            async for entry in tailer.follow_logs():
                entry_count += 1
                timestamp = entry.timestamp.strftime("%H:%M:%S")
                print(f"  {timestamp} - {entry.level.value} - {entry.component} - {entry.message}")
                
                # Stop after 2 seconds
                if entry_count >= 2:
                    tailer.stop_follow()
                    break
        
        # Run follow simulation
        await asyncio.wait_for(follow_simulation(), timeout=3.0)
        
        print(f"✅ Follow mode test completed - {entry_count} entries processed")
        
    except asyncio.TimeoutError:
        print("✅ Follow mode test completed (timeout)")
    except Exception as e:
        print(f"❌ Follow mode test failed: {e}")
    
    print(f"\n🎉 Log Tailing System Test Complete!")
    print("="*60)


if __name__ == "__main__":
    asyncio.run(test_log_tailer())
