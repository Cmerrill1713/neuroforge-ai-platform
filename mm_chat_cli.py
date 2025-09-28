#!/usr/bin/env python3
"""
Multimodal Chat CLI Interface

Provides a command-line interface matching the user's command format:
/mm.chat turn_id:"R-42" text:"What's wrong here?" image:"samples/board.png" tools:"lc:retriever" save_context:true
"""

import asyncio
import argparse
import logging
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.core.chat.multimodal_chat import MultimodalChatSystem, ChatRequest

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def parse_command_args(command_str: str) -> dict:
    """Parse command string into arguments."""
    args = {}
    
    # Remove the command prefix
    if command_str.startswith("/mm.chat "):
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
    parser = argparse.ArgumentParser(description="Multimodal Chat CLI")
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
        
        # Validate required arguments
        if "turn_id" not in parsed_args:
            print("Error: turn_id is required")
            return 1
        
        if "text" not in parsed_args:
            print("Error: text is required")
            return 1
        
        # Create chat system
        chat_system = MultimodalChatSystem()
        
        # Create request
        request = ChatRequest(
            turn_id=parsed_args.get("turn_id"),
            text=parsed_args.get("text"),
            image=parsed_args.get("image"),
            tools=parsed_args.get("tools", "").split(",") if parsed_args.get("tools") else [],
            save_context=parsed_args.get("save_context", True),
            max_tokens=parsed_args.get("max_tokens", 1024)
        )
        
        # Process chat
        response = await chat_system.chat(request)
        
        # Print results
        print("\n" + "="*80)
        print("MULTIMODAL CHAT RESULT")
        print("="*80)
        print(f"Turn ID: {request.turn_id}")
        print(f"Response ID: {response.response_id}")
        print(f"Confidence: {response.confidence:.2f}")
        print(f"Processing Time: {response.processing_time_ms:.2f}ms")
        print(f"Context Saved: {response.context_saved}")
        
        if response.image_analysis:
            print(f"\n🖼️ Image Analysis:")
            print(f"   Mode: {response.image_analysis.get('analysis_mode', 'unknown')}")
            print(f"   Description: {response.image_analysis.get('description', 'No description')}")
            print(f"   Confidence: {response.image_analysis.get('confidence', 0):.2f}")
            
            if response.image_analysis.get('defects'):
                print(f"   Defects Found: {len(response.image_analysis['defects'])}")
                for defect in response.image_analysis['defects']:
                    print(f"     - {defect.get('defect_type', 'Unknown')}: {defect.get('severity', 'Unknown')}")
            
            if response.image_analysis.get('components'):
                print(f"   Components Found: {len(response.image_analysis['components'])}")
                for component in response.image_analysis['components']:
                    print(f"     - {component.get('component_type', 'Unknown')} ({component.get('identification', 'Unknown')})")
        
        if response.tools_executed:
            print(f"\n🔧 Tools Executed:")
            for tool in response.tools_executed:
                print(f"   - {tool}")
        
        print(f"\n💬 Response:")
        print(f"   {response.response_text}")
        
        return 0
        
    except Exception as e:
        logger.error(f"Multimodal chat failed: {e}")
        return 1


if __name__ == "__main__":
    exit(asyncio.run(main()))
