#!/usr/bin/env python3
""'
Comprehensive Knowledge Base Integration Script
Integrates all documents from the knowledge base into the vector database
""'

import asyncio
import json
import logging
import os
import requests
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ComprehensiveKnowledgeIntegrator:
    """TODO: Add docstring."""
    """Integrates all knowledge base documents into Weaviate vector database""'

    def __init__(self, weaviate_url: str = "http://host.docker.internal:8090", knowledge_base_path: str = "/app/knowledge_base'):
        """TODO: Add docstring."""
        self.weaviate_url = weaviate_url
        self.knowledge_base_path = Path(knowledge_base_path)
        self.session = requests.Session()

    def test_weaviate_connection(self) -> bool:
        """TODO: Add docstring."""
        """Test connection to Weaviate""'
        try:
            response = self.session.get(f"{self.weaviate_url}/v1/meta', timeout=5)
            if response.status_code == 200:
                logger.info("✅ Weaviate connection successful')
                return True
            else:
                logger.error(f"❌ Weaviate connection failed: {response.status_code}')
                return False
        except Exception as e:
            logger.error(f"❌ Weaviate connection error: {e}')
            return False

    def create_document_schema(self) -> bool:
        """TODO: Add docstring."""
        """Create comprehensive Document schema in Weaviate""'
        schema = {
            "class": "KnowledgeDocument',
            "description": "Comprehensive knowledge base documents including Wikipedia, YouTube, GitHub, and training resources',
            "vectorizer": "none',
            "properties': [
                {
                    "name": "title',
                    "dataType": ["text'],
                    "description": "Document title'
                },
                {
                    "name": "content',
                    "dataType": ["text'],
                    "description": "Document content'
                },
                {
                    "name": "source',
                    "dataType": ["text'],
                    "description": "Document source URL'
                },
                {
                    "name": "category',
                    "dataType": ["text'],
                    "description": "Document category (wikipedia, youtube, github, training, etc.)'
                },
                {
                    "name": "subcategory',
                    "dataType": ["text'],
                    "description": "Document subcategory'
                },
                {
                    "name": "keywords',
                    "dataType": ["text'],
                    "description": "Comma-separated keywords'
                },
                {
                    "name": "crawled_at',
                    "dataType": ["text'],
                    "description": "Crawl timestamp'
                },
                {
                    "name": "document_type',
                    "dataType": ["text'],
                    "description": "Type of document (article, transcript, readme, etc.)'
                }
            ]
        }

        try:
            response = self.session.post(f"{self.weaviate_url}/v1/schema', json=schema)
            if response.status_code in [200, 422]:  # 422 means schema already exists
                logger.info("✅ KnowledgeDocument schema created or already exists')
                return True
            else:
                logger.error(f"❌ Schema creation failed: {response.status_code} - {response.text}')
                return False
        except Exception as e:
            logger.error(f"❌ Schema creation error: {e}')
            return False

    def add_document(self, title: str, content: str, source: str, category: str,
        """TODO: Add docstring."""
                    subcategory: str = "', keywords: List[str] = None,
                    document_type: str = "document') -> Optional[str]:
        """Add a document to Weaviate""'
        document = {
            "class": "KnowledgeDocument',
            "properties': {
                "title': title,
                "content': content,
                "source': source,
                "category': category,
                "subcategory': subcategory,
                "keywords": ", '.join(keywords or []),
                "crawled_at': datetime.now().isoformat(),
                "document_type': document_type
            }
        }

        try:
            response = self.session.post(f"{self.weaviate_url}/v1/objects', json=document)
            if response.status_code == 200:
                doc_id = response.json()["id']
                logger.info(f"✅ Document added: {title[:50]}... (ID: {doc_id})')
                return doc_id
            else:
                logger.error(f"❌ Failed to add document: {response.status_code} - {response.text}')
                return None
        except Exception as e:
            logger.error(f"❌ Document addition error: {e}')
            return None

    def process_wikipedia_document(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """TODO: Add docstring."""
        """Process a Wikipedia document""'
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            title = data.get('title', 'Untitled Wikipedia Article')
            content = data.get('content', '')
            url = data.get('url', '')

            # Extract keywords from categories
            categories = data.get('categories', [])
            keywords = []
            for cat in categories:
                if isinstance(cat, dict):
                    keywords.extend(cat.get('title', '').split())

            return {
                'title': title,
                'content': content,
                'source': url,
                'category': 'wikipedia',
                'subcategory': 'article',
                'keywords': keywords,
                'document_type': 'wikipedia_article'
            }
        except Exception as e:
            logger.error(f"❌ Failed to process Wikipedia document {file_path}: {e}')
            return None

    def process_youtube_document(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """TODO: Add docstring."""
        """Process a YouTube transcript document""'
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            title = data.get('title', 'Untitled YouTube Video')
            content = data.get('transcript', '')
            url = data.get('url', '')

            # Extract keywords from description
            description = data.get('description', '')
            keywords = [word for word in description.split() if len(word) > 4][:10]  # Top 10 longer words

            return {
                'title': title,
                'content': content,
                'source': url,
                'category': 'youtube',
                'subcategory': 'transcript',
                'keywords': keywords,
                'document_type': 'video_transcript'
            }
        except Exception as e:
            logger.error(f"❌ Failed to process YouTube document {file_path}: {e}')
            return None

    def process_github_document(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """TODO: Add docstring."""
        """Process a GitHub repository document""'
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            title = data.get('title', 'Untitled GitHub Repository')
            content = data.get('content', '') or data.get('readme_content', '')
            url = data.get('url', '')

            # Extract keywords from topics and description
            topics = data.get('topics', [])
            description = data.get('description', '')
            keywords = topics + [word for word in description.split() if len(word) > 4][:10]

            return {
                'title': title,
                'content': content,
                'source': url,
                'category': 'github',
                'subcategory': 'repository',
                'keywords': keywords,
                'document_type': 'repository_content'
            }
        except Exception as e:
            logger.error(f"❌ Failed to process GitHub document {file_path}: {e}')
            return None

    def process_llm_training_document(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """TODO: Add docstring."""
        """Process an LLM training document""'
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            title = data.get('title', 'Untitled Training Document')
            content = data.get('content', '')
            url = data.get('url', '')

            # Extract keywords from content
            content_words = content.split()[:50]  # First 50 words
            keywords = [word for word in content_words if len(word) > 5][:10]  # Top 10 longer words

            return {
                'title': title,
                'content': content,
                'source': url,
                'category': 'training',
                'subcategory': 'llm_training',
                'keywords': keywords,
                'document_type': 'training_document'
            }
        except Exception as e:
            logger.error(f"❌ Failed to process training document {file_path}: {e}')
            return None

    def process_meta_document(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """TODO: Add docstring."""
        """Process a Meta AI document""'
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            title = data.get('title', 'Untitled Meta Document')
            content = data.get('content', '')
            url = data.get('url', '')

            # Extract keywords from content
            content_words = content.split()[:50]
            keywords = [word for word in content_words if len(word) > 5][:10]

            return {
                'title': title,
                'content': content,
                'source': url,
                'category': 'meta',
                'subcategory': 'research',
                'keywords': keywords,
                'document_type': 'research_document'
            }
        except Exception as e:
            logger.error(f"❌ Failed to process Meta document {file_path}: {e}')
            return None

    def process_document_file(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """TODO: Add docstring."""
        """Process any document file based on its name""'
        filename = file_path.name

        if filename.startswith('wiki_') or filename.startswith('wikipedia_'):
            return self.process_wikipedia_document(file_path)
        elif filename.startswith('youtube_'):
            return self.process_youtube_document(file_path)
        elif filename.startswith('github_'):
            return self.process_github_document(file_path)
        elif 'llm_training' in filename:
            return self.process_llm_training_document(file_path)
        elif 'meta' in filename.lower():
            return self.process_meta_document(file_path)
        else:
            # Generic processing for other documents
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                title = data.get('title', filename)
                content = data.get('content', '')
                url = data.get('url', '')

                return {
                    'title': title,
                    'content': content,
                    'source': url,
                    'category': 'general',
                    'subcategory': 'document',
                    'keywords': [],
                    'document_type': 'document'
                }
            except Exception as e:
                logger.error(f"❌ Failed to process document {file_path}: {e}')
                return None

    def integrate_all_documents(self, max_documents: int = None) -> int:
        """TODO: Add docstring."""
        """Integrate all documents from knowledge base""'
        added_count = 0
        processed_count = 0

        # Get all JSON files
        json_files = list(self.knowledge_base_path.glob('*.json'))

        logger.info(f"📂 Found {len(json_files)} JSON files to process')

        for file_path in json_files:
            if max_documents and processed_count >= max_documents:
                break

            processed_count += 1

            # Process the document
            doc_data = self.process_document_file(file_path)
            if not doc_data:
                continue

            # Add to vector database
            title = doc_data['title']
            content = doc_data['content']
            source = doc_data['source']
            category = doc_data['category']
            subcategory = doc_data['subcategory']
            keywords = doc_data['keywords']
            document_type = doc_data['document_type']

            if content and len(content) > 50:  # Only add documents with substantial content
                doc_id = self.add_document(title, content, source, category, subcategory, keywords, document_type)
                if doc_id:
                    added_count += 1

                # Add a small delay to avoid overwhelming Weaviate
                import time
                time.sleep(0.1)

        logger.info(f"✅ Successfully integrated {added_count}/{processed_count} documents')
        return added_count

    def test_search_functionality(self) -> bool:
        """TODO: Add docstring."""
        """Test the search functionality""'
        queries = [
            "machine learning',
            "artificial intelligence',
            "neural networks',
            "deep learning',
            "natural language processing'
        ]

        success_count = 0

        for query in queries:
            graphql_query = {
                'query': f'''
                    {{
                        Get {{
                            KnowledgeDocument(
                                limit: 3
                                where: {{
                                    path: ["content']
                                    operator: Like
                                    valueText: "*{query}*'
                                }}
                            ) {{
                                title
                                category
                                source
                            }}
                        }}
                    }}
                '''
            }

            try:
                response = self.session.post(f"{self.weaviate_url}/v1/graphql', json=graphql_query)
                if response.status_code == 200:
                    data = response.json()
                    documents = data.get('data', {}).get('Get', {}).get('KnowledgeDocument', [])
                    if documents:
                        success_count += 1
                        logger.info(f"✅ Search '{query}' found {len(documents)} results')
                    else:
                        logger.warning(f"⚠️ Search '{query}' found no results')
                else:
                    logger.error(f"❌ Search '{query}' failed: {response.status_code}')
            except Exception as e:
                logger.error(f"❌ Search '{query}' error: {e}')

        return success_count >= 3  # At least 3 out of 5 searches should work

def main():
    """TODO: Add docstring."""
    """Main integration function""'
    logger.info("🚀 Starting Comprehensive Knowledge Base Integration')

    # Initialize integrator
    integrator = ComprehensiveKnowledgeIntegrator()

    # Test Weaviate connection
    if not integrator.test_weaviate_connection():
        logger.error("❌ Cannot connect to Weaviate. Exiting.')
        return

    # Create schema
    if not integrator.create_document_schema():
        logger.error("❌ Failed to create schema. Exiting.')
        return

    # Integrate all documents
    added_count = integrator.integrate_all_documents()

    # Test search functionality
    logger.info("🔍 Testing search functionality...')
    if integrator.test_search_functionality():
        logger.info("✅ Search functionality working correctly')
    else:
        logger.warning("⚠️ Search functionality has issues')

    logger.info(f"🎉 Integration complete! Added {added_count} documents to knowledge base')

if __name__ == "__main__':
    main()
