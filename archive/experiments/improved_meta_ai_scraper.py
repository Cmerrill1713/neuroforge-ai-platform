#!/usr/bin/env python3
""'
Improved Meta AI Document Scraper with Better Error Handling
""'

import requests
import json
import os
import time
from datetime import datetime
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import re
from typing import List, Dict, Any, Optional
import logging
import hashlib
from dataclasses import dataclass
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class DocumentMetadata:
    """TODO: Add docstring."""
    """Metadata for scraped documents""'
    url: str
    title: str
    category: str
    content_hash: str
    word_count: int
    scraped_at: str
    status: str
    error: Optional[str] = None

class ImprovedMetaAIScraper:
    """TODO: Add docstring."""
    """TODO: Add docstring.""'
    def __init__(self, output_dir: str = "meta_ai_docs'):
        """TODO: Add docstring."""
        """TODO: Add docstring.""'
        self.output_dir = Path(output_dir)
        self.session = requests.Session()

        # Enhanced headers to avoid blocking
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            "Accept-Language": "en-US,en;q=0.9',
            "Accept-Encoding": "gzip, deflate, br',
            "Connection": "keep-alive',
            "Upgrade-Insecure-Requests": "1',
            "Sec-Fetch-Dest": "document',
            "Sec-Fetch-Mode": "navigate',
            "Sec-Fetch-Site": "none',
            "Cache-Control": "max-age=0'
        })

        # Alternative sources that are more accessible
        self.sources = {
            "research_papers': [
                "https://arxiv.org/search/?query=meta+ai&searchtype=all',
                "https://paperswithcode.com/search?q=meta+ai',
                "https://scholar.google.com/scholar?q=meta+ai+research'
            ],
            "github_repos': [
                "https://github.com/facebookresearch',
                "https://github.com/meta-llama',
                "https://github.com/pytorch/pytorch'
            ],
            "documentation': [
                "https://pytorch.org/docs/',
                "https://huggingface.co/meta-llama',
                "https://github.com/meta-llama/llama/blob/main/README.md'
            ],
            "blog_posts': [
                "https://about.fb.com/news/tag/artificial-intelligence/',
                "https://engineering.fb.com/category/artificial-intelligence/'
            ]
        }

        # Create output directories
        self.output_dir.mkdir(exist_ok=True)
        (self.output_dir / "raw').mkdir(exist_ok=True)
        (self.output_dir / "processed').mkdir(exist_ok=True)
        (self.output_dir / "summaries').mkdir(exist_ok=True)

    def scrape_url(self, url: str, category: str) -> Dict[str, Any]:
        """TODO: Add docstring."""
        """Scrape content from a single URL with improved error handling""'
        try:
            logger.info(f"Scraping {url}')

            # Add delay to be respectful
            time.sleep(1)

            response = self.session.get(url, timeout=30, allow_redirects=True)

            # Check if we got a successful response
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, "html.parser')

                # Extract title
                title = soup.find("title')
                title_text = title.get_text().strip() if title else "No title'

                # Extract main content
                content_selectors = [
                    "main", "article", ".content", ".post-content',
                    ".entry-content", "#content", ".main-content',
                    ".markdown-body", ".repository-content'
                ]

                content = "'
                for selector in content_selectors:
                    element = soup.select_one(selector)
                    if element:
                        content = element.get_text(separator="\n', strip=True)
                        break

                if not content:
                    content = soup.get_text(separator="\n', strip=True)

                # Extract links
                links = []
                for link in soup.find_all("a', href=True):
                    href = link["href']
                    if href.startswith("http") or href.startswith("/'):
                        full_url = urljoin(url, href)
                        links.append({
                            "text': link.get_text().strip(),
                            "url': full_url
                        })

                # Extract images
                images = []
                for img in soup.find_all("img', src=True):
                    src = img["src']
                    if src.startswith("http") or src.startswith("/'):
                        full_url = urljoin(url, src)
                        images.append({
                            "alt": img.get("alt", "'),
                            "src': full_url
                        })

                # Create content hash
                content_hash = hashlib.md5(content.encode()).hexdigest()
                word_count = len(content.split())

                # Create metadata
                metadata = DocumentMetadata(
                    url=url,
                    title=title_text,
                    category=category,
                    content_hash=content_hash,
                    word_count=word_count,
                    scraped_at=datetime.now().isoformat(),
                    status="success'
                )

                return {
                    "metadata': metadata.__dict__,
                    "content': content,
                    "links': links,
                    "images': images,
                    "status_code': response.status_code
                }

            else:
                logger.warning(f"HTTP {response.status_code} for {url}')
                metadata = DocumentMetadata(
                    url=url,
                    title=f"HTTP {response.status_code}',
                    category=category,
                    content_hash="',
                    word_count=0,
                    scraped_at=datetime.now().isoformat(),
                    status="error',
                    error=f"HTTP {response.status_code}'
                )
                return {
                    "metadata': metadata.__dict__,
                    "content": "',
                    "links': [],
                    "images': [],
                    "status_code': response.status_code
                }

        except requests.exceptions.RequestException as e:
            logger.error(f"Request error for {url}: {str(e)}')
            metadata = DocumentMetadata(
                url=url,
                title="Request Error',
                category=category,
                content_hash="',
                word_count=0,
                scraped_at=datetime.now().isoformat(),
                status="error',
                error=str(e)
            )
            return {
                "metadata': metadata.__dict__,
                "content": "',
                "links': [],
                "images': [],
                "status_code': 0
            }
        except Exception as e:
            logger.error(f"Unexpected error for {url}: {str(e)}')
            metadata = DocumentMetadata(
                url=url,
                title="Unexpected Error',
                category=category,
                content_hash="',
                word_count=0,
                scraped_at=datetime.now().isoformat(),
                status="error',
                error=str(e)
            )
            return {
                "metadata': metadata.__dict__,
                "content": "',
                "links': [],
                "images': [],
                "status_code': 0
            }

    def scrape_category(self, category: str, urls: List[str]) -> List[Dict[str, Any]]:
        """TODO: Add docstring."""
        """Scrape all URLs in a category""'
        logger.info(f"Scraping category: {category}')
        results = []

        for url in urls:
            result = self.scrape_url(url, category)
            results.append(result)
            time.sleep(2)  # Be respectful with requests

        return results

    def scrape_all(self) -> Dict[str, Any]:
        """TODO: Add docstring."""
        """Scrape all Meta AI documentation sources""'
        logger.info("Starting improved Meta AI document scraping')
        all_results = {}

        for category, urls in self.sources.items():
            logger.info(f"Processing category: {category}')
            results = self.scrape_category(category, urls)
            all_results[category] = results

            # Save category results
            category_file = self.output_dir / "processed" / f"{category}.json'
            with open(category_file, "w", encoding="utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)

            logger.info(f"Saved {len(results)} results to {category_file}')

        # Save combined results
        combined_file = self.output_dir / "all_meta_ai_docs.json'
        with open(combined_file, "w", encoding="utf-8') as f:
            json.dump(all_results, f, indent=2, ensure_ascii=False)

        logger.info(f"Saved combined results to {combined_file}')
        return all_results

    def generate_summary(self, results: Dict[str, Any]) -> str:
        """TODO: Add docstring."""
        """Generate a summary of scraped content""'
        total_docs = sum(len(category_results) for category_results in results.values())
        successful_docs = sum(
            len([doc for doc in category_results if doc["metadata"]["status"] == "success'])
            for category_results in results.values()
        )

        summary = f""'Meta AI Document Scraping Summary
================================

Total URLs processed: {total_docs}
Successfully scraped: {successful_docs}
Failed: {total_docs - successful_docs}

Categories:
""'

        for category, category_results in results.items():
            success_count = len([doc for doc in category_results if doc["metadata"]["status"] == "success'])
            summary += f"- {category}: {success_count}/{len(category_results)} documents\n'

            if success_count > 0:
                summary += "  Successful URLs:\n'
                for doc in category_results:
                    if doc["metadata"]["status"] == "success':
                        summary += f"    - {doc["metadata"]["title"]}\n'
                        summary += f"      URL: {doc["metadata"]["url"]}\n'
                        summary += f"      Word count: {doc["metadata"]["word_count"]}\n'

        summary += f"\nScraped at: {datetime.now().isoformat()}\n'
        summary += f"Output directory: {self.output_dir}\n'

        return summary

def main():
    """TODO: Add docstring."""
    """Main function to run the improved scraper""'
    scraper = ImprovedMetaAIScraper()

    try:
        results = scraper.scrape_all()

        # Generate and print summary
        summary = scraper.generate_summary(results)
        print(summary)

        # Save summary
        summary_file = scraper.output_dir / "summaries" / "scraping_summary.txt'
        with open(summary_file, "w", encoding="utf-8') as f:
            f.write(summary)

        logger.info("Improved scraping completed successfully!')

    except Exception as e:
        logger.error(f"Scraping failed: {str(e)}')
        raise

if __name__ == "__main__':
    main()
