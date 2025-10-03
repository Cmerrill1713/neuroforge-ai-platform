#!/usr/bin/env python3
""'
Meta AI Document Scraper
Scrapes Meta's AI research papers, documentation, and resources
""'

import requests
import json
import os
import time
from datetime import datetime
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import re
from typing import List, Dict, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MetaAIScraper:
    """TODO: Add docstring."""
    """TODO: Add docstring.""'
    def __init__(self, output_dir: str = "meta_ai_docs'):
        """TODO: Add docstring."""
        """TODO: Add docstring.""'
        self.output_dir = output_dir
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

        # Meta AI documentation sources
        self.sources = {
            "research_papers': [
                "https://ai.meta.com/research/',
                "https://research.facebook.com/publications/',
                "https://arxiv.org/search/?query=meta+ai&searchtype=all'
            ],
            "llama_docs': [
                "https://ai.meta.com/llama/',
                "https://github.com/meta-llama/llama',
                "https://huggingface.co/meta-llama'
            ],
            "ai_tools': [
                "https://ai.meta.com/tools/',
                "https://github.com/facebookresearch',
                "https://pytorch.org/'
            ],
            "blog_posts': [
                "https://ai.meta.com/blog/',
                "https://about.fb.com/news/tag/artificial-intelligence/'
            ]
        }

        os.makedirs(self.output_dir, exist_ok=True)

    def scrape_url(self, url: str, category: str) -> Dict[str, Any]:
        """TODO: Add docstring."""
        """Scrape content from a single URL""'
        try:
            logger.info(f"Scraping {url}')
            response = self.session.get(url, timeout=30)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, "html.parser')

            # Extract metadata
            title = soup.find("title')
            title_text = title.get_text().strip() if title else "No title'

            # Extract main content
            content_selectors = [
                "main", "article", ".content", ".post-content',
                ".entry-content", "#content", ".main-content'
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

            return {
                "url': url,
                "title': title_text,
                "content': content,
                "links': links,
                "images': images,
                "category': category,
                "scraped_at': datetime.now().isoformat(),
                "status": "success'
            }

        except Exception as e:
            logger.error(f"Error scraping {url}: {str(e)}')
            return {
                "url': url,
                "title": "Error',
                "content": "',
                "links': [],
                "images': [],
                "category': category,
                "scraped_at': datetime.now().isoformat(),
                "status": "error',
                "error': str(e)
            }

    def scrape_category(self, category: str, urls: List[str]) -> List[Dict[str, Any]]:
        """TODO: Add docstring."""
        """Scrape all URLs in a category""'
        logger.info(f"Scraping category: {category}')
        results = []

        for url in urls:
            result = self.scrape_url(url, category)
            results.append(result)
            time.sleep(1)  # Be respectful with requests

        return results

    def scrape_all(self) -> Dict[str, Any]:
        """TODO: Add docstring."""
        """Scrape all Meta AI documentation sources""'
        logger.info("Starting Meta AI document scraping')
        all_results = {}

        for category, urls in self.sources.items():
            logger.info(f"Processing category: {category}')
            results = self.scrape_category(category, urls)
            all_results[category] = results

            # Save category results
            category_file = os.path.join(self.output_dir, f"{category}.json')
            with open(category_file, "w", encoding="utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)

            logger.info(f"Saved {len(results)} results to {category_file}')

        # Save combined results
        combined_file = os.path.join(self.output_dir, "all_meta_ai_docs.json')
        with open(combined_file, "w", encoding="utf-8') as f:
            json.dump(all_results, f, indent=2, ensure_ascii=False)

        logger.info(f"Saved combined results to {combined_file}')
        return all_results

    def extract_research_papers(self, content: str) -> List[Dict[str, str]]:
        """TODO: Add docstring."""
        """Extract research paper information from content""'
        papers = []

        # Look for paper patterns
        paper_patterns = [
            r"([A-Z][^.!?]*\?[^.!?]*\.)',  # Questions
            r"([A-Z][^.!?]*\.[^.!?]*\.)',  # Statements
        ]

        for pattern in paper_patterns:
            matches = re.findall(pattern, content)
            for match in matches:
                if len(match) > 50:  # Filter out short matches
                    papers.append({
                        "text': match.strip(),
                        "type": "research_insight'
                    })

        return papers

    def generate_summary(self, results: Dict[str, Any]) -> str:
        """TODO: Add docstring."""
        """Generate a summary of scraped content""'
        total_docs = sum(len(category_results) for category_results in results.values())
        successful_docs = sum(
            len([doc for doc in category_results if doc["status"] == "success'])
            for category_results in results.values()
        )

        summary = f""'
Meta AI Document Scraping Summary
================================

Total URLs processed: {total_docs}
Successfully scraped: {successful_docs}
Failed: {total_docs - successful_docs}

Categories:
""'

        for category, category_results in results.items():
            success_count = len([doc for doc in category_results if doc["status"] == "success'])
            summary += f"- {category}: {success_count}/{len(category_results)} documents\n'

        summary += f"\nScraped at: {datetime.now().isoformat()}\n'
        summary += f"Output directory: {self.output_dir}\n'

        return summary

def main():
    """TODO: Add docstring."""
    """Main function to run the scraper""'
    scraper = MetaAIScraper()

    try:
        results = scraper.scrape_all()

        # Generate summary
        summary = scraper.generate_summary(results)
        print(summary)

        # Save summary
        summary_file = os.path.join(scraper.output_dir, "scraping_summary.txt')
        with open(summary_file, "w", encoding="utf-8') as f:
            f.write(summary)

        logger.info("Scraping completed successfully!')

    except Exception as e:
        logger.error(f"Scraping failed: {str(e)}')
        raise

if __name__ == "__main__':
    main()
