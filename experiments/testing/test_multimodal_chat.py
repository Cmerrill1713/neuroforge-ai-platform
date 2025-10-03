#!/usr/bin/env python3
""'
Comprehensive test of the Multimodal Chat System

Tests all features including image analysis, tool integration, and context saving.
""'

import asyncio
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src'))

from src.core.chat.multimodal_chat import MultimodalChatSystem, ChatRequest


async def test_multimodal_chat():
    """Test the multimodal chat system comprehensively.""'
    print("🧪 Testing Multimodal Chat System')
    print("='*60)

    # Create chat system
    chat_system = MultimodalChatSystem()

    # Test cases
    test_cases = [
        {
            "name": "Defect Detection',
            "request': ChatRequest(
                turn_id="TEST-001',
                text="What"s wrong here?',
                image="samples/board.png',
                tools=["lc:retriever'],
                save_context=True
            )
        },
        {
            "name": "Component Analysis',
            "request': ChatRequest(
                turn_id="TEST-002',
                text="Can you identify the components on this board?',
                image="samples/board.png',
                tools=["lc:retriever'],
                save_context=True
            )
        },
        {
            "name": "Technical Inspection',
            "request': ChatRequest(
                turn_id="TEST-003',
                text="Please perform a technical analysis of this circuit board',
                image="samples/board.png',
                tools=["lc:retriever'],
                save_context=True
            )
        },
        {
            "name": "Text Only',
            "request': ChatRequest(
                turn_id="TEST-004',
                text="What are the common defects in electronic assemblies?',
                tools=["lc:retriever'],
                save_context=True
            )
        }
    ]

    # Run tests
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📋 Test {i}: {test_case["name"]}')
        print("-' * 40)

        try:
            response = await chat_system.chat(test_case["request'])

            print(f"✅ Success!')
            print(f"   Turn ID: {response.turn_id}')
            print(f"   Response ID: {response.response_id}')
            print(f"   Confidence: {response.confidence:.2f}')
            print(f"   Processing Time: {response.processing_time_ms:.2f}ms')
            print(f"   Context Saved: {response.context_saved}')

            if response.image_analysis:
                print(f"   Image Analysis: {response.image_analysis.get("analysis_mode", "unknown")}')
                print(f"   Defects Found: {len(response.image_analysis.get("defects", []))}')
                print(f"   Components Found: {len(response.image_analysis.get("components", []))}')

            if response.tools_executed:
                print(f"   Tools Executed: {", ".join(response.tools_executed)}')

            print(f"   Response Preview: {response.response_text[:100]}...')

        except Exception as e:
            print(f"❌ Failed: {e}')

    # Test context retrieval
    print(f"\n📚 Testing Context Retrieval')
    print("-' * 40)

    try:
        history = chat_system.get_conversation_history("TEST-001')
        print(f"✅ Retrieved {len(history)} conversation turns')

        for turn in history:
            print(f"   Turn {turn.turn_id}: {turn.message_type.value}')
            print(f"     Content: {turn.content[:50]}...')
            if turn.image_path:
                print(f"     Image: {turn.image_path}')
            if turn.tools_used:
                print(f"     Tools: {", ".join(turn.tools_used)}')

    except Exception as e:
        print(f"❌ Context retrieval failed: {e}')

    print(f"\n🎉 Multimodal Chat System Test Complete!')
    print("='*60)


if __name__ == "__main__':
    asyncio.run(test_multimodal_chat())
