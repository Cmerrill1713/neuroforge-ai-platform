#!/usr/bin/env python3
""'
Get YouTube Transcripts from IndyDevDan's Channel
Uses youtube-transcript-api to get transcripts and saves to knowledge base
""'

import json
import requests
from pathlib import Path
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter
import re

def get_channel_videos(channel_url):
    """TODO: Add docstring."""
    """Get video URLs from a YouTube channel""'
    # This is a simplified approach - in practice you'd need to scrape the channel page
    # or use YouTube API with proper authentication

    # For now, let"s use some known video URLs from IndyDevDan's channel
    # These would typically be obtained by scraping the channel page or using YouTube API

    sample_videos = [
        # These are placeholder URLs - we'd need to get actual URLs from the channel
        "https://www.youtube.com/watch?v=VIDEO_ID_1',
        "https://www.youtube.com/watch?v=VIDEO_ID_2',
        "https://www.youtube.com/watch?v=VIDEO_ID_3'
    ]

    print(f"📋 Sample video URLs (replace with actual URLs from {channel_url}):')
    for i, url in enumerate(sample_videos, 1):
        print(f"{i}. {url}')

    return sample_videos

def extract_video_id(url):
    """TODO: Add docstring."""
    """Extract video ID from YouTube URL""'
    patterns = [
        r"(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([^&\n?#]+)',
        r"youtube\.com\/watch\?.*v=([^&\n?#]+)'
    ]

    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None

def get_video_transcript(video_id):
    """TODO: Add docstring."""
    """Get transcript for a YouTube video""'
    try:
        # Get transcript
        transcript = YouTubeTranscriptApi.get_transcript(video_id)

        # Format as text
        formatter = TextFormatter()
        text_transcript = formatter.format_transcript(transcript)

        return text_transcript
    except Exception as e:
        print(f"❌ Error getting transcript for {video_id}: {e}')
        return None

def save_to_knowledge_base(video_data, knowledge_base_path):
    """TODO: Add docstring."""
    """Save video data to knowledge base""'

    # Create individual entry file
    entry_file = knowledge_base_path / f"youtube_{video_data["video_id"]}.json'

    with open(entry_file, "w", encoding="utf-8') as f:
        json.dump(video_data, f, indent=2, ensure_ascii=False)

    print(f"✅ Saved {video_data["video_id"]} to knowledge base')

def main():
    """TODO: Add docstring."""
    """Main function to get YouTube transcripts""'

    print("🎥 Getting YouTube Transcripts from IndyDevDan"s Channel')
    print("=' * 55)

    knowledge_base_path = Path("knowledge_base')
    knowledge_base_path.mkdir(exist_ok=True)

    # Get channel videos
    channel_url = "https://www.youtube.com/@indydevdan'
    video_urls = get_channel_videos(channel_url)

    print("\n🔧 To get actual transcripts:')
    print("1. Go to https://www.youtube.com/@indydevdan')
    print("2. Copy video URLs from his channel')
    print("3. Replace the placeholder URLs in this script')
    print("4. Run the script again')

    print("\n📝 Example of how to use with actual video URLs:')
    print(""'
# Replace these with actual video URLs from IndyDevDan's channel:
actual_videos = [
    "https://www.youtube.com/watch?v=ACTUAL_VIDEO_ID_1',
    "https://www.youtube.com/watch?v=ACTUAL_VIDEO_ID_2',
    "https://www.youtube.com/watch?v=ACTUAL_VIDEO_ID_3'
]

for url in actual_videos:
    video_id = extract_video_id(url)
    if video_id:
        transcript = get_video_transcript(video_id)
        if transcript:
            video_data = {
                "id": f"youtube_{video_id}',
                "title": f"Video {video_id}",  # You'd get this from YouTube API
                "url': url,
                "transcript': transcript,
                "source_type": "youtube_video',
                "domain": "educational_content',
                "keywords": ["indydevdan", "youtube", "video'],
                "retrieval_tags": ["youtube", "video", "transcript", "indydevdan']
            }
            save_to_knowledge_base(video_data, knowledge_base_path)
    ""')

    print("\n✅ YouTube transcript extraction script is ready!')
    print("📊 Your MCP tools interface should also have YouTube transcript tools available')

if __name__ == "__main__':
    main()
