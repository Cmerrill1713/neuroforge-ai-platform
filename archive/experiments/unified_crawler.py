#!/usr/bin/env python3
""'
Unified Content Crawler for Agentic LLM Core
Extends the existing IndyDevDan crawler to handle multiple content sources
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

# Import the existing RAG system
from src.core.rag.vector_database import AdvancedRAGSystem, DocumentType

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class UnifiedCrawler:
    """TODO: Add docstring."""
    """Unified crawler that extends the existing system for multiple content sources""'

    def __init__(self, github_token: Optional[str] = None):
        """TODO: Add docstring."""
        """Initialize the unified crawler with existing system components""'
        self.github_token = github_token or os.getenv("GITHUB_TOKEN')
        self.github = Github(self.github_token) if self.github_token else None
        self.knowledge_base_path = Path("knowledge_base')
        self.knowledge_base_path.mkdir(exist_ok=True)

        # Initialize the existing RAG system
        self.rag_system = AdvancedRAGSystem()

        # YouTube-DL configuration - TRANSCRIPT ONLY
        self.ytdl_opts = {
            "quiet': True,
            "no_warnings': True,
            "extract_flat': True,  # Only get metadata, don't process videos
            "writeinfojson': False,
            "writesubtitles': False,  # Don't write subtitle files
            "writeautomaticsub': False,  # Don't write auto subtitle files
            "skip_download': True,
            "ignoreerrors': True,  # Continue on errors
        }

        self.crawled_data = {
            "github_repos': [],
            "youtube_videos': [],
            "web_docs': [],
            "crawl_timestamp': datetime.now().isoformat(),
            "total_items': 0
        }

    async def crawl_github_repos(self, username: str = "indydevdan') -> List[Dict[str, Any]]:
        """Crawl GitHub repositories for the given username (existing functionality)""'
        logger.info(f"🔍 Crawling GitHub repositories for {username}')

        if not self.github:
            logger.warning("No GitHub token provided, using public API (rate limited)')
            return await self._crawl_github_public(username)

        try:
            user = self.github.get_user(username)
            repos = []

            for repo in user.get_repos():
                repo_data = {
                    'id': f"github_{repo.id}',
                    'title': repo.name,
                    'description': repo.description or '',
                    'url': repo.html_url,
                    'language': repo.language or 'Unknown',
                    'stars': repo.stargazers_count,
                    'forks': repo.forks_count,
                    'created_at': repo.created_at.isoformat(),
                    'updated_at': repo.updated_at.isoformat(),
                    'topics': repo.get_topics(),
                    'readme_content': await self._get_readme_content(repo),
                    'source_type': 'github_repository',
                    'domain': 'software_development',
                    'keywords': self._extract_keywords(repo.name, repo.description or ''),
                    'retrieval_tags': ['github', 'repository', 'code', 'development']
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

    async def crawl_github_organization(self, org_name: str) -> List[Dict[str, Any]]:
        """Crawl all repositories from a GitHub organization""'
        logger.info(f"🔍 Crawling GitHub organization: {org_name}')

        if not self.github:
            logger.warning("No GitHub token provided, skipping organization crawl')
            return []

        try:
            org = self.github.get_organization(org_name)
            repos = []

            for repo in org.get_repos():
                repo_data = {
                    'id': f"github_{repo.id}',
                    'title': repo.name,
                    'description': repo.description or '',
                    'url': repo.html_url,
                    'language': repo.language or 'Unknown',
                    'stars': repo.stargazers_count,
                    'forks': repo.forks_count,
                    'created_at': repo.created_at.isoformat(),
                    'updated_at': repo.updated_at.isoformat(),
                    'topics': repo.get_topics(),
                    'readme_content': await self._get_readme_content(repo),
                    'source_type': 'github_repository',
                    'domain': 'software_development',
                    'keywords': self._extract_keywords(repo.name, repo.description or ''),
                    'retrieval_tags': ['github', 'repository', 'code', 'development', org_name]
                }

                repos.append(repo_data)
                logger.info(f"✅ Crawled repo: {repo.name}')

                # Rate limiting
                await asyncio.sleep(0.1)

            logger.info(f"📊 Crawled {len(repos)} repositories from {org_name}')
            return repos

        except Exception as e:
            logger.error(f"❌ Error crawling organization {org_name}: {e}')
            return []

    async def crawl_web_documentation(self, urls: List[str]) -> List[Dict[str, Any]]:
        """Crawl web documentation from URLs""'
        logger.info(f"📚 Crawling {len(urls)} web documentation URLs')

        docs = []
        for url in urls:
            try:
                doc_data = await self._crawl_web_page(url)
                if doc_data:
                    docs.append(doc_data)
                await asyncio.sleep(1)  # Rate limiting
            except Exception as e:
                logger.error(f"❌ Error crawling {url}: {e}')

        logger.info(f"📊 Crawled {len(docs)} web documentation pages')
        return docs

    async def _crawl_web_page(self, url: str) -> Optional[Dict[str, Any]]:
        """Crawl a single web page""'
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }

            async with aiohttp.ClientSession(headers=headers) as session:
                async with session.get(url, timeout=30) as response:
                    if response.status == 200:
                        html = await response.text()
                        soup = BeautifulSoup(html, 'html.parser')

                        # Extract content
                        title = soup.find('title')
                        title_text = title.get_text().strip() if title else urlparse(url).path

                        # Remove script and style elements
                        for script in soup(["script", "style']):
                            script.decompose()

                        # Get main content
                        main_content = soup.find('main') or soup.find('article') or soup.find('div', class_='content')
                        if not main_content:
                            main_content = soup.find('body')

                        content_text = main_content.get_text() if main_content else soup.get_text()
                        content_text = re.sub(r'\s+', ' ', content_text).strip()

                        doc_data = {
                            'id': f"web_doc_{hash(url)}',
                            'title': title_text,
                            'url': url,
                            'content': content_text[:10000],  # Limit content size
                            'source_type': 'web_documentation',
                            'domain': 'documentation',
                            'keywords': self._extract_keywords(title_text, content_text),
                            'retrieval_tags': ['web', 'documentation', 'tutorial', 'guide']
                        }

                        logger.info(f"✅ Crawled doc: {title_text}')
                        return doc_data

        except Exception as e:
            logger.error(f"❌ Error crawling {url}: {e}')
            return None

    async def _get_readme_content(self, repo) -> str:
        """Get README content from repository""'
        try:
            readme = repo.get_readme()
            return readme.decoded_content.decode('utf-8')
        except:
            return "'

    def _extract_keywords(self, title: str, content: str) -> List[str]:
        """TODO: Add docstring."""
        """Extract keywords from title and content""'
        text = f"{title} {content}'.lower()
        common_keywords = [
            'python', 'javascript', 'typescript', 'react', 'vue', 'angular',
            'nodejs', 'express', 'django', 'flask', 'fastapi', 'nextjs',
            'machine learning', 'ai', 'artificial intelligence', 'deep learning',
            'neural network', 'tensorflow', 'pytorch', 'scikit-learn',
            'data science', 'analytics', 'visualization', 'database',
            'sql', 'nosql', 'mongodb', 'postgresql', 'redis',
            'docker', 'kubernetes', 'aws', 'azure', 'gcp',
            'api', 'rest', 'graphql', 'microservices', 'serverless',
            'testing', 'unit test', 'integration test', 'ci/cd',
            'git', 'github', 'gitlab', 'bitbucket', 'version control'
        ]

        found_keywords = [kw for kw in common_keywords if kw in text]
        return found_keywords[:10]  # Limit to 10 keywords

    async def _crawl_github_public(self, username: str) -> List[Dict[str, Any]]:
        """Fallback method for public GitHub API without token""'
        try:
            url = f"https://api.github.com/users/{username}/repos'
            response = requests.get(url)
            if response.status_code == 200:
                repos_data = response.json()
                repos = []

                for repo_data in repos_data[:10]:  # Limit to 10 repos for public API
                    repo = {
                        'id': f"github_{repo_data['id']}',
                        'title': repo_data['name'],
                        'description': repo_data.get('description', ''),
                        'url': repo_data['html_url'],
                        'language': repo_data.get('language', 'Unknown'),
                        'stars': repo_data['stargazers_count'],
                        'forks': repo_data['forks_count'],
                        'created_at': repo_data['created_at'],
                        'updated_at': repo_data['updated_at'],
                        'topics': [],
                        'readme_content': '',
                        'source_type': 'github_repository',
                        'domain': 'software_development',
                        'keywords': self._extract_keywords(repo_data['name'], repo_data.get('description', '')),
                        'retrieval_tags': ['github', 'repository', 'code', 'development']
                    }
                    repos.append(repo)

                return repos
        except Exception as e:
            logger.error(f"❌ Error with public GitHub API: {e}')
            return []

    async def crawl_all_content(self, sources: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
        """Crawl all content from specified sources""'
        logger.info("🚀 Starting unified content crawl')

        all_repos = []
        all_docs = []

        # Crawl GitHub repositories
        if 'github_users' in sources:
            for username in sources['github_users']:
                repos = await self.crawl_github_repos(username)
                if repos:
                    all_repos.extend(repos)

        if 'github_orgs' in sources:
            for org_name in sources['github_orgs']:
                repos = await self.crawl_github_organization(org_name)
                if repos:
                    all_repos.extend(repos)

        # Crawl web documentation
        if 'web_docs' in sources:
            docs = await self.crawl_web_documentation(sources['web_docs'])
            if docs:
                all_docs.extend(docs)

        self.crawled_data['github_repos'] = all_repos
        self.crawled_data['web_docs'] = all_docs
        self.crawled_data['total_items'] = len(all_repos) + len(all_docs)

        logger.info(f"✅ Crawl complete! Total items: {self.crawled_data['total_items']}')
        return self.crawled_data

    async def save_to_knowledge_base(self, items: List[Dict[str, Any]], category: str):
        """Save crawled items to knowledge base using the existing RAG system""'
        logger.info(f"💾 Saving {len(items)} {category} to knowledge base using RAG system')

        for item in items:
            try:
                # Add to RAG system
                await self.rag_system.add_knowledge(
                    title=item.get('title', 'Untitled'),
                    content=item.get('content', '') or item.get('readme_content', ''),
                    document_type=DocumentType.KNOWLEDGE_BASE,
                    source=item.get('url', ''),
                    metadata={
                        'category': category,
                        'source_type': item.get('source_type', ''),
                        'domain': item.get('domain', ''),
                        'keywords': ', '.join(item.get('keywords', [])),
                        'retrieval_tags': ', '.join(item.get('retrieval_tags', [])),
                        'crawled_at': datetime.now().isoformat()
                    }
                )

                # Also save to JSON for backup
                filename = f"unified_{category}_{item['id']}.json'
                filepath = self.knowledge_base_path / filename

                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(item, f, indent=2, ensure_ascii=False)

            except Exception as e:
                logger.error(f"❌ Error saving {item.get('title', 'unknown')}: {e}')

    async def save_crawl_summary(self):
        """Save crawl summary to knowledge base""'
        summary = {
            'crawl_type': 'unified_content_crawl',
            'timestamp': self.crawled_data['crawl_timestamp'],
            'total_items': self.crawled_data['total_items'],
            'github_repos': len(self.crawled_data['github_repos']),
            'web_docs': len(self.crawled_data['web_docs']),
            'youtube_videos': len(self.crawled_data['youtube_videos'])
        }

        summary_file = self.knowledge_base_path / 'unified_crawl_summary.json'
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)

        logger.info(f"📊 Crawl summary saved: {summary_file}')

async def main():
    """Main function for testing the unified crawler""'
    print("🚀 Unified Content Crawler')
    print("Extends existing system for multiple content sources')
    print("=' * 60)

    crawler = UnifiedCrawler()

    # Define sources to crawl
    sources = {
        'github_users': ['indydevdan'],  # Existing functionality
        'github_orgs': ['meta-llama', 'facebookresearch'],  # New functionality
        'web_docs': [
            'https://huggingface.co/docs/transformers/training',
            'https://pytorch.org/tutorials/beginner/transfer_learning_tutorial.html',
            'https://fairseq.readthedocs.io/en/latest/tutorial_simple_lstm.html'
        ]
    }

    try:
        # Crawl all content
        crawled_data = await crawler.crawl_all_content(sources)

        # Save to knowledge base
        if crawled_data['github_repos']:
            await crawler.save_to_knowledge_base(crawled_data['github_repos'], 'github_repos')

        if crawled_data['web_docs']:
            await crawler.save_to_knowledge_base(crawled_data['web_docs'], 'web_docs')

        # Save summary
        await crawler.save_crawl_summary()

        print(f"\n✅ Crawl Complete!')
        print(f"📊 Total items: {crawled_data['total_items']}')
        print(f"📁 GitHub repos: {len(crawled_data['github_repos'])}')
        print(f"📚 Web docs: {len(crawled_data['web_docs'])}')
        print(f"💾 Saved to: {crawler.knowledge_base_path}')
        print(f"🔍 Added to RAG system for semantic search')

    except Exception as e:
        print(f"❌ Crawl failed: {e}')
        raise

if __name__ == "__main__':
    asyncio.run(main())
