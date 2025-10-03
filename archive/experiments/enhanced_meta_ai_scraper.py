#!/usr/bin/env python3
""'
Enhanced Meta AI Document Scraper with Advanced Content Processing
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

class AdvancedMetaAIScraper:
    """TODO: Add docstring."""
    """TODO: Add docstring.""'
    def __init__(self, output_dir: str = "meta_ai_docs'):
        """TODO: Add docstring."""
        """TODO: Add docstring.""'
        self.output_dir = Path(output_dir)
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            "Accept-Language": "en-US,en;q=0.5',
            "Accept-Encoding": "gzip, deflate',
            "Connection": "keep-alive',
        })

        # Enhanced Meta AI documentation sources
        self.sources = {
            "research_papers': [
                "https://ai.meta.com/research/',
                "https://research.facebook.com/publications/',
                "https://arxiv.org/search/?query=meta+ai&searchtype=all',
                "https://paperswithcode.com/search?q=meta+ai'
            ],
            "llama_docs': [
                "https://ai.meta.com/llama/',
                "https://github.com/meta-llama/llama',
                "https://huggingface.co/meta-llama',
                "https://llama.meta.com/'
            ],
            "ai_tools': [
                "https://ai.meta.com/tools/',
                "https://github.com/facebookresearch',
                "https://pytorch.org/',
                "https://github.com/pytorch/pytorch'
            ],
            "blog_posts': [
                "https://ai.meta.com/blog/',
                "https://about.fb.com/news/tag/artificial-intelligence/',
                "https://engineering.fb.com/category/artificial-intelligence/'
            ],
            "code_repositories': [
                "https://github.com/facebookresearch/segment-anything',
                "https://github.com/facebookresearch/detectron2',
                "https://github.com/facebookresearch/fairseq',
                "https://github.com/facebookresearch/mae'
            ]
        }

        # Create output directories
        self.output_dir.mkdir(exist_ok=True)
        (self.output_dir / "raw').mkdir(exist_ok=True)
        (self.output_dir / "processed').mkdir(exist_ok=True)
        (self.output_dir / "summaries').mkdir(exist_ok=True)

    def extract_structured_content(self, soup: BeautifulSoup, url: str) -> Dict[str, Any]:
        """TODO: Add docstring."""
        """Extract structured content from HTML""'
        content = {
            "headings': [],
            "paragraphs': [],
            "code_blocks': [],
            "tables': [],
            "lists': [],
            "links': [],
            "images': [],
            "metadata': {}
        }

        # Extract headings
        for i in range(1, 7):
            headings = soup.find_all(f"h{i}')
            for heading in headings:
                content["headings'].append({
                    "level': i,
                    "text': heading.get_text().strip(),
                    "id": heading.get("id", "')
                })

        # Extract paragraphs
        paragraphs = soup.find_all("p')
        for p in paragraphs:
            text = p.get_text().strip()
            if text and len(text) > 20:  # Filter out short paragraphs
                content["paragraphs'].append(text)

        # Extract code blocks
        code_blocks = soup.find_all(["code", "pre'])
        for code in code_blocks:
            content["code_blocks'].append({
                "text': code.get_text().strip(),
                "language": code.get("class", [""])[0].replace("language-", "") if code.get("class") else "'
            })

        # Extract tables
        tables = soup.find_all("table')
        for table in tables:
            rows = []
            for tr in table.find_all("tr'):
                cells = [td.get_text().strip() for td in tr.find_all(["td", "th'])]
                if cells:
                    rows.append(cells)
            if rows:
                content["tables'].append(rows)

        # Extract lists
        lists = soup.find_all(["ul", "ol'])
        for list_elem in lists:
            items = [li.get_text().strip() for li in list_elem.find_all("li')]
            content["lists'].append({
                "type': list_elem.name,
                "items': items
            })

        # Extract links
        links = soup.find_all("a', href=True)
        for link in links:
            href = link["href']
            if href.startswith("http") or href.startswith("/'):
                full_url = urljoin(url, href)
                content["links'].append({
                    "text': link.get_text().strip(),
                    "url': full_url,
                    "is_external': not urlparse(full_url).netloc == urlparse(url).netloc
                })

        # Extract images
        images = soup.find_all("img', src=True)
        for img in images:
            src = img["src']
            if src.startswith("http") or src.startswith("/'):
                full_url = urljoin(url, src)
                content["images'].append({
                    "alt": img.get("alt", "'),
                    "src': full_url,
                    "title": img.get("title", "')
                })

        # Extract metadata
        meta_tags = soup.find_all("meta')
        for meta in meta_tags:
            name = meta.get("name") or meta.get("property')
            content_val = meta.get("content')
            if name and content_val:
                content["metadata'][name] = content_val

        return content

    def extract_research_insights(self, content: Dict[str, Any]) -> List[Dict[str, str]]:
        """TODO: Add docstring."""
        """Extract research insights and key findings""'
        insights = []

        # Look for research patterns in paragraphs
        research_patterns = [
            r"(?:we|our|this|the)\s+(?:study|research|paper|work|method|approach|model|system|algorithm)',
            r"(?:results?|findings?|conclusions?|observations?)',
            r"(?:propose|introduce|present|develop|create|build)',
            r"(?:achieve|obtain|demonstrate|show|prove)',
            r"(?:performance|accuracy|efficiency|effectiveness)',
        ]

        for paragraph in content["paragraphs']:
            for pattern in research_patterns:
                if re.search(pattern, paragraph.lower()):
                    insights.append({
                        "text': paragraph,
                        "type": "research_insight',
                        "pattern': pattern
                    })
                    break

        return insights

    def extract_technical_specifications(self, content: Dict[str, Any]) -> List[Dict[str, str]]:
        """TODO: Add docstring."""
        """Extract technical specifications and parameters""'
        specs = []

        # Look for technical specifications
        spec_patterns = [
            r"(\d+(?:\.\d+)?)\s*(?:GB|MB|KB|TB|parameters?|layers?|neurons?|epochs?)',
            r"(?:batch\s+size|learning\s+rate|optimizer|loss\s+function)',
            r"(?:GPU|CPU|memory|RAM|storage)',
            r"(?:accuracy|precision|recall|F1|BLEU|ROUGE)',
        ]

        for paragraph in content["paragraphs']:
            for pattern in spec_patterns:
                matches = re.findall(pattern, paragraph, re.IGNORECASE)
                if matches:
                    specs.append({
                        "text': paragraph,
                        "specifications': matches,
                        "type": "technical_spec'
                    })

        return specs

    def scrape_url(self, url: str, category: str) -> Dict[str, Any]:
        """TODO: Add docstring."""
        """Enhanced scraping with structured content extraction""'
        try:
            logger.info(f"Scraping {url}')
            response = self.session.get(url, timeout=30)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, "html.parser')

            # Extract title
            title = soup.find("title')
            title_text = title.get_text().strip() if title else "No title'

            # Extract structured content
            structured_content = self.extract_structured_content(soup, url)

            # Extract insights and specifications
            insights = self.extract_research_insights(structured_content)
            specs = self.extract_technical_specifications(structured_content)

            # Create content hash
            content_text = " ".join(structured_content["paragraphs'])
            content_hash = hashlib.md5(content_text.encode()).hexdigest()

            # Calculate word count
            word_count = len(content_text.split())

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

            result = {
                "metadata': metadata.__dict__,
                "structured_content': structured_content,
                "insights': insights,
                "specifications': specs,
                "raw_html": str(soup) if len(str(soup)) < 100000 else "HTML too large to store'
            }

            return result

        except Exception as e:
            logger.error(f"Error scraping {url}: {str(e)}')
            metadata = DocumentMetadata(
                url=url,
                title="Error',
                category=category,
                content_hash="',
                word_count=0,
                scraped_at=datetime.now().isoformat(),
                status="error',
                error=str(e)
            )
            return {
                "metadata': metadata.__dict__,
                "structured_content': {},
                "insights': [],
                "specifications': [],
                "raw_html": "'
            }

    def save_document(self, result: Dict[str, Any], category: str) -> str:
        """TODO: Add docstring."""
        """Save individual document with structured format""'
        metadata = result["metadata']
        filename = f"{category}_{metadata["content_hash"][:8]}.json'
        filepath = self.output_dir / "raw' / filename

        with open(filepath, "w", encoding="utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)

        return str(filepath)

    def generate_markdown_summary(self, results: Dict[str, Any]) -> str:
        """TODO: Add docstring."""
        """Generate markdown summary of scraped content""'
        md_content = f""'# Meta AI Documentation Scraping Report

**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S')}

## Overview

""'

        total_docs = sum(len(category_results) for category_results in results.values())
        successful_docs = sum(
            len([doc for doc in category_results if doc["metadata"]["status"] == "success'])
            for category_results in results.values()
        )

        md_content += f"- **Total URLs processed:** {total_docs}\n'
        md_content += f"- **Successfully scraped:** {successful_docs}\n'
        md_content += f"- **Failed:** {total_docs - successful_docs}\n\n'

        md_content += "## Categories\n\n'

        for category, category_results in results.items():
            success_count = len([doc for doc in category_results if doc["metadata"]["status"] == "success'])
            md_content += f"### {category.replace("_", " ").title()}\n'
            md_content += f"- **Success rate:** {success_count}/{len(category_results)}\n'

            if success_count > 0:
                md_content += "- **Documents:**\n'
                for doc in category_results:
                    if doc["metadata"]["status"] == "success':
                        md_content += f"  - [{doc["metadata"]["title"]}]({doc["metadata"]["url"]})\n'
                        md_content += f"    - Word count: {doc["metadata"]["word_count"]}\n'
                        md_content += f"    - Insights: {len(doc["insights"])}\n'
                        md_content += f"    - Specifications: {len(doc["specifications"])}\n'
            md_content += "\n'

        return md_content

    def scrape_all(self) -> Dict[str, Any]:
        """TODO: Add docstring."""
        """Scrape all Meta AI documentation sources with enhanced processing""'
        logger.info("Starting enhanced Meta AI document scraping')
        all_results = {}

        for category, urls in self.sources.items():
            logger.info(f"Processing category: {category}')
            results = []

            for url in urls:
                result = self.scrape_url(url, category)
                results.append(result)

                # Save individual document
                if result["metadata"]["status"] == "success':
                    self.save_document(result, category)

                time.sleep(2)  # Be respectful with requests

            all_results[category] = results

            # Save category results
            category_file = self.output_dir / "processed" / f"{category}.json'
            with open(category_file, "w", encoding="utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)

            logger.info(f"Saved {len(results)} results to {category_file}')

        # Generate and save markdown summary
        md_summary = self.generate_markdown_summary(all_results)
        summary_file = self.output_dir / "summaries" / "scraping_report.md'
        with open(summary_file, "w", encoding="utf-8') as f:
            f.write(md_summary)

        # Save combined results
        combined_file = self.output_dir / "all_meta_ai_docs.json'
        with open(combined_file, "w", encoding="utf-8') as f:
            json.dump(all_results, f, indent=2, ensure_ascii=False)

        logger.info(f"Saved combined results to {combined_file}')
        logger.info(f"Saved markdown summary to {summary_file}')

        return all_results

def main():
    """TODO: Add docstring."""
    """Main function to run the enhanced scraper""'
    scraper = AdvancedMetaAIScraper()

    try:
        results = scraper.scrape_all()

        # Print summary
        total_docs = sum(len(category_results) for category_results in results.values())
        successful_docs = sum(
            len([doc for doc in category_results if doc["metadata"]["status"] == "success'])
            for category_results in results.values()
        )

        print(f"\n{"="*50}')
        print("Meta AI Document Scraping Complete!')
        print(f"{"="*50}')
        print(f"Total URLs processed: {total_docs}')
        print(f"Successfully scraped: {successful_docs}')
        print(f"Failed: {total_docs - successful_docs}')
        print(f"Output directory: {scraper.output_dir}')
        print(f"{"="*50}\n')

        logger.info("Enhanced scraping completed successfully!')

    except Exception as e:
        logger.error(f"Scraping failed: {str(e)}')
        raise

if __name__ == "__main__':
    main()
