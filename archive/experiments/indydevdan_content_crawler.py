#!/usr/bin/env python3
""'
IndyDevDan Content Crawler for Agentic LLM Core
Crawls GitHub repositories and YouTube content from indydevdan and adds to knowledge base
""'

import asyncio
import json
import logging
import os
import re
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from urllib.parse import urljoin, urlparse

import aiohttp
import yt_dlp
from bs4 import BeautifulSoup
import requests
from github import Github

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class IndyDevDanCrawler:
    """TODO: Add docstring."""
    """Main crawler class for indydevdan content""'

    def __init__(self, github_token: Optional[str] = None):
        """TODO: Add docstring."""
        """TODO: Add docstring.""'
        self.github_token = github_token or os.getenv("GITHUB_TOKEN')
        self.github = Github(self.github_token) if self.github_token else None
        self.knowledge_base_path = Path("knowledge_base')
        self.knowledge_base_path.mkdir(exist_ok=True)

        # YouTube-DL configuration - TRANSCRIPT ONLY
        self.ytdl_opts = {
            "quiet': True,
            "no_warnings': True,
            "extract_flat": True,  # Only get metadata, don't process videos
            "writeinfojson': False,
            "writesubtitles": False,  # Don't write subtitle files
            "writeautomaticsub": False,  # Don't write auto subtitle files
            "skip_download': True,
            "ignoreerrors': True,  # Continue on errors
        }

        self.crawled_data = {
            "github_repos': [],
            "youtube_videos': [],
            "crawl_timestamp': datetime.now().isoformat(),
            "total_items': 0
        }

    async def crawl_github_repos(self, username: str = "indydevdan') -> List[Dict[str, Any]]:
        """Crawl GitHub repositories for the given username""'

        logger.info(f"🔍 Crawling GitHub repositories for {username}')

        if not self.github:
            logger.warning("No GitHub token provided, using public API (rate limited)')
            return await self._crawl_github_public(username)

        try:
            user = self.github.get_user(username)
            repos = []

            for repo in user.get_repos():
                repo_data = {
                    "id": f"github_{repo.id}',
                    "title': repo.name,
                    "description": repo.description or "',
                    "url': repo.html_url,
                    "language": repo.language or "Unknown',
                    "stars': repo.stargazers_count,
                    "forks': repo.forks_count,
                    "created_at': repo.created_at.isoformat(),
                    "updated_at': repo.updated_at.isoformat(),
                    "topics': repo.get_topics(),
                    "readme_content': await self._get_readme_content(repo),
                    "source_type": "github_repository',
                    "domain": "software_development',
                    "keywords": self._extract_keywords(repo.name, repo.description or "'),
                    "retrieval_tags": ["github", "repository", "code", "development']
                }

                repos.append(repo_data)
                logger.info(f"✅ Crawled repo: {repo.name}')

                # Rate limiting
                await asyncio.sleep(0.1)

            logger.info(f"📊 Crawled {len(repos)} GitHub repositories')
            return repos

        except Exception as e:
            logger.error(f"❌ Error crawling GitHub: {e}')
            return []

    async def _crawl_github_public(self, username: str) -> List[Dict[str, Any]]:
        """Crawl GitHub using public API (rate limited)""'

        async with aiohttp.ClientSession() as session:
            url = f"https://api.github.com/users/{username}/repos'
            headers = {"Accept": "application/vnd.github.v3+json'}

            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    repos_data = await response.json()
                    repos = []

                    for repo in repos_data:
                        repo_data = {
                            "id": f"github_{repo["id"]}',
                            "title": repo["name'],
                            "description": repo["description"] or "',
                            "url": repo["html_url'],
                            "language": repo["language"] or "Unknown',
                            "stars": repo["stargazers_count'],
                            "forks": repo["forks_count'],
                            "created_at": repo["created_at'],
                            "updated_at": repo["updated_at'],
                            "topics": repo.get("topics', []),
                            "readme_content": await self._get_readme_content_public(session, repo["full_name']),
                            "source_type": "github_repository',
                            "domain": "software_development',
                            "keywords": self._extract_keywords(repo["name"], repo["description"] or "'),
                            "retrieval_tags": ["github", "repository", "code", "development']
                        }
                        repos.append(repo_data)

                    return repos
                else:
                    logger.error(f"❌ GitHub API error: {response.status}')
                    return []

    async def _get_readme_content(self, repo) -> str:
        """Get README content from GitHub repository""'
        try:
            readme = repo.get_readme()
            return readme.decoded_content.decode("utf-8')
        except Exception:
            return "'

    async def _get_readme_content_public(self, session: aiohttp.ClientSession, full_name: str) -> str:
        """Get README content using public API""'
        try:
            url = f"https://api.github.com/repos/{full_name}/readme'
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    import base64
                    return base64.b64decode(data["content"]).decode("utf-8')
        except Exception:
            pass
        return "'

    async def crawl_youtube_channel(self, channel_url: str) -> List[Dict[str, Any]]:
        """Crawl YouTube channel for videos and transcripts""'

        logger.info(f"🎥 Crawling YouTube channel: {channel_url}')

        videos = []

        try:
            with yt_dlp.YoutubeDL(self.ytdl_opts) as ydl:
                # Get channel info
                channel_info = ydl.extract_info(channel_url, download=False)

                if "entries' in channel_info:
                    for entry in channel_info["entries']:
                        if entry:
                            video_data = await self._process_youtube_video(entry)
                            if video_data:
                                videos.append(video_data)
                                logger.info(f"✅ Processed video: {video_data["title"]}')

                                # Rate limiting
                                await asyncio.sleep(1)

                logger.info(f"📊 Crawled {len(videos)} YouTube videos')
                return videos

        except Exception as e:
            logger.error(f"❌ Error crawling YouTube: {e}')
            return []

    async def _process_youtube_video(self, video_info: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process individual YouTube video""'

        try:
            video_id = video_info.get("id", "')
            title = video_info.get("title", "')
            description = video_info.get("description", "')
            upload_date = video_info.get("upload_date", "')
            duration = video_info.get("duration', 0)
            view_count = video_info.get("view_count', 0)

            # Get transcript
            transcript = await self._get_video_transcript(video_id)

            video_data = {
                "id": f"youtube_{video_id}',
                "title': title,
                "description': description,
                "url": f"https://www.youtube.com/watch?v={video_id}',
                "upload_date': upload_date,
                "duration': duration,
                "view_count': view_count,
                "transcript': transcript,
                "source_type": "youtube_video',
                "domain": "educational_content',
                "keywords': self._extract_keywords(title, description),
                "retrieval_tags": ["youtube", "video", "tutorial", "education'],
                "content_hash': self._generate_content_hash(title + description + transcript)
            }

            return video_data

        except Exception as e:
            logger.error(f"❌ Error processing video {video_info.get("id", "unknown")}: {e}')
            return None

    async def _get_video_transcript(self, video_id: str) -> str:
        """Get transcript for a YouTube video - TRANSCRIPT ONLY""'

        try:
            # Simple transcript extraction using yt-dlp
            transcript_opts = {
                "quiet': True,
                "no_warnings': True,
                "skip_download': True,
                "writesubtitles': False,
                "writeautomaticsub': False,
                "listsubtitles': False,
            }

            with yt_dlp.YoutubeDL(transcript_opts) as ydl:
                # Get video info
                info = ydl.extract_info(f"https://www.youtube.com/watch?v={video_id}', download=False)

                # Try to get automatic captions
                if "automatic_captions" in info and "en" in info["automatic_captions']:
                    caption_url = info["automatic_captions"]["en"][0]["url']

                    # Fetch transcript content
                    async with aiohttp.ClientSession() as session:
                        async with session.get(caption_url) as response:
                            if response.status == 200:
                                caption_data = await response.text()
                                return self._parse_caption_data(caption_data)

                # Try manual captions if no automatic ones
                elif "subtitles" in info and "en" in info["subtitles']:
                    caption_url = info["subtitles"]["en"][0]["url']

                    async with aiohttp.ClientSession() as session:
                        async with session.get(caption_url) as response:
                            if response.status == 200:
                                caption_data = await response.text()
                                return self._parse_caption_data(caption_data)

                return "'

        except Exception as e:
            logger.error(f"❌ Error getting transcript for {video_id}: {e}')
            return "'

    def _parse_caption_data(self, caption_data: str) -> str:
        """TODO: Add docstring."""
        """Parse YouTube caption data to extract text""'

        try:
            # Simple XML parsing for captions
            soup = BeautifulSoup(caption_data, "xml')
            text_elements = soup.find_all("text')

            transcript_parts = []
            for element in text_elements:
                text = element.get_text()
                if text:
                    transcript_parts.append(text)

            return " '.join(transcript_parts)

        except Exception as e:
            logger.error(f"❌ Error parsing caption data: {e}')
            return "'

    def _extract_keywords(self, title: str, description: str) -> List[str]:
        """TODO: Add docstring."""
        """Extract keywords from title and description""'

        text = f"{title} {description}'.lower()

        # Common technical keywords
        keywords = []
        tech_terms = [
            "python", "javascript", "react", "nodejs", "typescript", "docker',
            "kubernetes", "aws", "azure", "gcp", "machine learning", "ai',
            "web development", "mobile development", "devops", "tutorial',
            "coding", "programming", "software engineering", "api", "database',
            "frontend", "backend", "fullstack", "git", "github", "deployment'
        ]

        for term in tech_terms:
            if term in text:
                keywords.append(term)

        return keywords

    def _generate_content_hash(self, content: str) -> str:
        """TODO: Add docstring."""
        """Generate hash for content""'
        import hashlib
        return hashlib.md5(content.encode()).hexdigest()

    async def save_to_knowledge_base(self, data: List[Dict[str, Any]], source_type: str):
        """Save crawled data to knowledge base""'

        logger.info(f"💾 Saving {len(data)} {source_type} items to knowledge base')

        for item in data:
            # Create individual entry file
            entry_file = self.knowledge_base_path / f"{item["id"]}.json'

            with open(entry_file, "w", encoding="utf-8') as f:
                json.dump(item, f, indent=2, ensure_ascii=False)

            logger.info(f"✅ Saved {item["id"]} to knowledge base')

        # Update main index
        await self._update_knowledge_base_index(data, source_type)

    async def _update_knowledge_base_index(self, data: List[Dict[str, Any]], source_type: str):
        """Update the main knowledge base index""'

        index_file = self.knowledge_base_path / "index.json'

        # Load existing index
        if index_file.exists():
            with open(index_file, "r", encoding="utf-8') as f:
                index_data = json.load(f)
        else:
            index_data = {"entries': []}

        # Add new entries
        for item in data:
            entry = {
                "id": item["id'],
                "title": item["title'],
                "keywords": item["keywords'],
                "retrieval_tags": item["retrieval_tags'],
                "domain": item["domain'],
                "source_type': source_type
            }
            index_data["entries'].append(entry)

        # Save updated index
        with open(index_file, "w", encoding="utf-8') as f:
            json.dump(index_data, f, indent=2, ensure_ascii=False)

        logger.info(f"📋 Updated knowledge base index with {len(data)} {source_type} entries')

    async def run_full_crawl(self, github_username: str = "indydevdan', youtube_channel: str = None):
        """Run full crawl of GitHub and YouTube content""'

        logger.info("🚀 Starting full crawl of indydevdan content')
        start_time = time.time()

        # Crawl GitHub
        github_repos = await self.crawl_github_repos(github_username)
        if github_repos:
            await self.save_to_knowledge_base(github_repos, "github_repository')
            self.crawled_data["github_repos'] = github_repos

        # Crawl YouTube (if channel URL provided)
        if youtube_channel:
            youtube_videos = await self.crawl_youtube_channel(youtube_channel)
            if youtube_videos:
                await self.save_to_knowledge_base(youtube_videos, "youtube_video')
                self.crawled_data["youtube_videos'] = youtube_videos

        # Save crawl summary
        self.crawled_data["total_items"] = len(github_repos) + len(self.crawled_data.get("youtube_videos', []))
        self.crawled_data["crawl_duration'] = time.time() - start_time

        summary_file = self.knowledge_base_path / "indydevdan_crawl_summary.json'
        with open(summary_file, "w", encoding="utf-8') as f:
            json.dump(self.crawled_data, f, indent=2, ensure_ascii=False)

        logger.info(f"🎉 Crawl completed! Processed {self.crawled_data["total_items"]} items in {self.crawled_data["crawl_duration"]:.1f}s')
        logger.info(f"📊 GitHub repos: {len(github_repos)}')
        logger.info(f"📊 YouTube videos: {len(self.crawled_data.get("youtube_videos", []))}')

        return self.crawled_data

async def main():
    """Main function""'

    print("🔍 IndyDevDan Content Crawler')
    print("=' * 50)

    # Get configuration
    github_token = os.getenv("GITHUB_TOKEN')
    youtube_channel = input("Enter YouTube channel URL (or press Enter to skip): ').strip()

    if not youtube_channel:
        youtube_channel = None

    # Initialize crawler
    crawler = IndyDevDanCrawler(github_token)

    # Run crawl
    try:
        results = await crawler.run_full_crawl(
            github_username="indydevdan',
            youtube_channel=youtube_channel
        )

        print("\n📊 CRAWL RESULTS:')
        print(f"Total items processed: {results["total_items"]}')
        print(f"GitHub repositories: {len(results["github_repos"])}')
        print(f"YouTube videos: {len(results.get("youtube_videos", []))}')
        print(f"Crawl duration: {results["crawl_duration"]:.1f}s')

        print("\n✅ Content successfully added to knowledge base!')
        print("📁 Check the "knowledge_base/" directory for individual files')
        print("📋 Check "knowledge_base/index.json" for the updated index')

    except Exception as e:
        logger.error(f"❌ Crawl failed: {e}')
        print(f"\n❌ Error: {e}')

if __name__ == "__main__':
    asyncio.run(main())
