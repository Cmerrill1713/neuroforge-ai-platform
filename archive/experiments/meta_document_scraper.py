#!/usr/bin/env python3
""'
Focused Meta AI Document Scraper
Specifically targets Meta's AI documentation and research papers
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

class MetaDocumentScraper:
    """TODO: Add docstring."""
    """TODO: Add docstring.""'
    def __init__(self, output_dir: str = "meta_documents'):
        """TODO: Add docstring."""
        """TODO: Add docstring.""'
        self.output_dir = output_dir
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            "Accept-Language": "en-US,en;q=0.9',
            "Connection": "keep-alive'
        })

        # Meta-specific document sources
        self.meta_sources = {
            "research_papers': [
                "https://arxiv.org/search/?query=meta+ai&searchtype=all',
                "https://paperswithcode.com/search?q=meta+ai',
                "https://scholar.google.com/scholar?q=meta+ai+research'
            ],
            "llama_docs': [
                "https://github.com/meta-llama/llama',
                "https://huggingface.co/meta-llama',
                "https://github.com/meta-llama/llama/blob/main/README.md'
            ],
            "github_repos': [
                "https://github.com/facebookresearch',
                "https://github.com/meta-llama',
                "https://github.com/pytorch/pytorch'
            ],
            "official_docs': [
                "https://pytorch.org/docs/',
                "https://ai.meta.com/',
                "https://research.facebook.com/'
            ]
        }

        os.makedirs(self.output_dir, exist_ok=True)

    def scrape_meta_document(self, url: str, category: str) -> Dict[str, Any]:
        """TODO: Add docstring."""
        """Scrape a single Meta document""'
        try:
            logger.info(f"Scraping Meta document: {url}')
            response = self.session.get(url, timeout=30)

            if response.status_code == 200:
                soup = BeautifulSoup(response.content, "html.parser')

                # Extract title
                title = soup.find("title')
                title_text = title.get_text().strip() if title else "Meta Document'

                # Extract content based on source type
                if "github.com' in url:
                    content = self._extract_github_content(soup)
                elif "arxiv.org' in url:
                    content = self._extract_arxiv_content(soup)
                elif "huggingface.co' in url:
                    content = self._extract_huggingface_content(soup)
                else:
                    content = self._extract_generic_content(soup)

                # Extract metadata
                metadata = {
                    "url': url,
                    "title': title_text,
                    "category': category,
                    "source_type': self._get_source_type(url),
                    "scraped_at': datetime.now().isoformat(),
                    "word_count': len(content.split()),
                    "status": "success'
                }

                return {
                    "metadata': metadata,
                    "content': content,
                    "raw_html': str(soup)[:50000]  # Limit size
                }
            else:
                logger.warning(f"HTTP {response.status_code} for {url}')
                return {
                    "metadata': {
                        "url': url,
                        "title": f"Error {response.status_code}',
                        "category': category,
                        "status": "error',
                        "error": f"HTTP {response.status_code}'
                    },
                    "content": "',
                    "raw_html": "'
                }

        except Exception as e:
            logger.error(f"Error scraping {url}: {str(e)}')
            return {
                "metadata': {
                    "url': url,
                    "title": "Scraping Error',
                    "category': category,
                    "status": "error',
                    "error': str(e)
                },
                "content": "',
                "raw_html": "'
            }

    def _extract_github_content(self, soup: BeautifulSoup) -> str:
        """TODO: Add docstring."""
        """Extract content from GitHub pages""'
        # Look for README content
        readme = soup.find("div", {"id": "readme'})
        if readme:
            return readme.get_text(separator="\n', strip=True)

        # Look for repository content
        content = soup.find("div", {"class": "repository-content'})
        if content:
            return content.get_text(separator="\n', strip=True)

        return soup.get_text(separator="\n', strip=True)

    def _extract_arxiv_content(self, soup: BeautifulSoup) -> str:
        """TODO: Add docstring."""
        """Extract content from arXiv pages""'
        # Look for abstract
        abstract = soup.find("blockquote", {"class": "abstract'})
        if abstract:
            return abstract.get_text(separator="\n', strip=True)

        return soup.get_text(separator="\n', strip=True)

    def _extract_huggingface_content(self, soup: BeautifulSoup) -> str:
        """TODO: Add docstring."""
        """Extract content from Hugging Face pages""'
        # Look for model card content
        content = soup.find("div", {"class": "prose'})
        if content:
            return content.get_text(separator="\n', strip=True)

        return soup.get_text(separator="\n', strip=True)

    def _extract_generic_content(self, soup: BeautifulSoup) -> str:
        """TODO: Add docstring."""
        """Extract content from generic pages""'
        # Try common content selectors
        selectors = ["main", "article", ".content", ".post-content", "#content']
        for selector in selectors:
            element = soup.select_one(selector)
            if element:
                return element.get_text(separator="\n', strip=True)

        return soup.get_text(separator="\n', strip=True)

    def _get_source_type(self, url: str) -> str:
        """TODO: Add docstring."""
        """Determine the source type from URL""'
        if "github.com' in url:
            return "github'
        elif "arxiv.org' in url:
            return "arxiv'
        elif "huggingface.co' in url:
            return "huggingface'
        elif "pytorch.org' in url:
            return "pytorch'
        else:
            return "generic'

    def scrape_all_meta_docs(self) -> Dict[str, Any]:
        """TODO: Add docstring."""
        """Scrape all Meta documents""'
        logger.info("Starting Meta document scraping')
        all_results = {}

        for category, urls in self.meta_sources.items():
            logger.info(f"Processing category: {category}')
            results = []

            for url in urls:
                result = self.scrape_meta_document(url, category)
                results.append(result)
                time.sleep(2)  # Be respectful

            all_results[category] = results

            # Save category results
            category_file = os.path.join(self.output_dir, f"{category}.json')
            with open(category_file, "w", encoding="utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)

            logger.info(f"Saved {len(results)} results to {category_file}')

        # Save combined results
        combined_file = os.path.join(self.output_dir, "all_meta_documents.json')
        with open(combined_file, "w", encoding="utf-8') as f:
            json.dump(all_results, f, indent=2, ensure_ascii=False)

        logger.info(f"Saved combined results to {combined_file}')
        return all_results

    def generate_meta_summary(self, results: Dict[str, Any]) -> str:
        """TODO: Add docstring."""
        """Generate summary of Meta documents""'
        total_docs = sum(len(category_results) for category_results in results.values())
        successful_docs = sum(
            len([doc for doc in category_results if doc["metadata"]["status"] == "success'])
            for category_results in results.values()
        )

        summary = f""'Meta AI Document Scraping Summary
================================

Total Meta documents processed: {total_docs}
Successfully scraped: {successful_docs}
Failed: {total_docs - successful_docs}

Categories:
""'

        for category, category_results in results.items():
            success_count = len([doc for doc in category_results if doc["metadata"]["status"] == "success'])
            summary += f"- {category}: {success_count}/{len(category_results)} documents\n'

            if success_count > 0:
                summary += "  Successful documents:\n'
                for doc in category_results:
                    if doc["metadata"]["status"] == "success':
                        summary += f"    - {doc["metadata"]["title"]}\n'
                        summary += f"      Source: {doc["metadata"]["source_type"]}\n'
                        summary += f"      Word count: {doc["metadata"]["word_count"]}\n'

        summary += f"\nScraped at: {datetime.now().isoformat()}\n'
        summary += f"Output directory: {self.output_dir}\n'

        return summary

def main():
    """TODO: Add docstring."""
    """Main function to run Meta document scraper""'
    scraper = MetaDocumentScraper()

    try:
        results = scraper.scrape_all_meta_docs()

        # Generate and print summary
        summary = scraper.generate_meta_summary(results)
        print(summary)

        # Save summary
        summary_file = os.path.join(scraper.output_dir, "meta_scraping_summary.txt')
        with open(summary_file, "w", encoding="utf-8') as f:
            f.write(summary)

        logger.info("Meta document scraping completed successfully!')

    except Exception as e:
        logger.error(f"Meta document scraping failed: {str(e)}')
        raise

if __name__ == "__main__':
    main()
