#!/usr/bin/env python3
""'
Get YouTube Transcripts from IndyDevDan's Channel
""'

import requests
from youtube_transcript_api import YouTubeTranscriptApi
import json
from pathlib import Path
import re

def get_youtube_transcripts():
    """TODO: Add docstring."""
    """Get YouTube transcripts from IndyDevDan"s channel""'

    print("🎥 Getting YouTube Transcripts from IndyDevDan\"s Channel')
    print("=' * 55)
    print("Channel: https://www.youtube.com/@indydevdan')
    print()

    # Let's try to get some video URLs from the channel
    channel_url = "https://www.youtube.com/@indydevdan'
    print("🔍 Attempting to get video URLs from channel...')

    try:
        # Try to get the channel page
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        response = requests.get(channel_url, headers=headers, timeout=10)

        if response.status_code == 200:
            print("✅ Successfully accessed channel page')

            # Look for video URLs in the page content
            video_pattern = r"href="/watch\?v=([a-zA-Z0-9_-]{11})"'
            video_ids = re.findall(video_pattern, response.text)

            if video_ids:
                print(f"📊 Found {len(video_ids)} video IDs')

                # Get unique video IDs (remove duplicates)
                unique_video_ids = list(set(video_ids))[:5]  # Get first 5 unique videos

                print(f"🎬 Processing {len(unique_video_ids)} videos:')

                knowledge_base_path = Path("knowledge_base')
                knowledge_base_path.mkdir(exist_ok=True)

                for i, video_id in enumerate(unique_video_ids, 1):
                    video_url = f"https://www.youtube.com/watch?v={video_id}'
                    print(f"\n{i}. Processing: {video_url}')

                    try:
                        # Try to get transcript
                        transcript = YouTubeTranscriptApi.get_transcript(video_id)

                        # Format transcript as text
                        transcript_text = " ".join([item["text'] for item in transcript])

                        if transcript_text:
                            print(f"   ✅ Transcript found ({len(transcript_text)} chars)')

                            # Create video data
                            video_data = {
                                "id": f"youtube_{video_id}',
                                "title": f"IndyDevDan Video {video_id}",  # We'd get actual title from YouTube API
                                "url': video_url,
                                "transcript': transcript_text,
                                "source_type": "youtube_video',
                                "domain": "educational_content',
                                "keywords": ["indydevdan", "youtube", "video", "agentic", "mcp'],
                                "retrieval_tags": ["youtube", "video", "transcript", "indydevdan", "agentic']
                            }

                            # Save to knowledge base
                            entry_file = knowledge_base_path / f"youtube_{video_id}.json'
                            with open(entry_file, "w", encoding="utf-8') as f:
                                json.dump(video_data, f, indent=2, ensure_ascii=False)

                            print(f"   💾 Saved to knowledge base')

                            # Show transcript preview
                            preview = transcript_text[:200] + "...' if len(transcript_text) > 200 else transcript_text
                            print(f"   📝 Preview: {preview}')
                        else:
                            print(f"   ❌ No transcript content')

                    except Exception as e:
                        print(f"   ❌ Error getting transcript: {e}')
            else:
                print("❌ No video IDs found in channel page')
                print("   This might be due to YouTube\"s dynamic loading')
        else:
            print(f"❌ Error accessing channel: {response.status_code}')

    except Exception as e:
        print(f"❌ Error: {e}')

    print("\n✅ YouTube transcript extraction completed!')
    print("📊 Check your knowledge_base/ directory for the new YouTube video files')

if __name__ == "__main__':
    get_youtube_transcripts()
