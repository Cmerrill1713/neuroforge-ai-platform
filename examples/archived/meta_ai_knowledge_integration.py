#!/usr/bin/env python3
""'
Meta AI Knowledge Base Integration Script
Integrates Meta AI documents into the agentic engineering platform's knowledge base
""'

import asyncio
import json
import logging
import requests
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MetaAIKnowledgeIntegrator:
    """TODO: Add docstring."""
    """Integrates Meta AI documents into Weaviate vector database""'

    def __init__(self, weaviate_url: str = "http://host.docker.internal:8090'):
        """TODO: Add docstring."""
        self.weaviate_url = weaviate_url
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
        """Create Document schema in Weaviate""'
        schema = {
            "class": "MetaAIDocument',
            "description": "Meta AI research papers, documentation, and resources',
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
                    "description": "Document category (research, docs, etc.)'
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
                }
            ]
        }

        try:
            response = self.session.post(f"{self.weaviate_url}/v1/schema', json=schema)
            if response.status_code in [200, 422]:  # 422 means schema already exists
                logger.info("✅ Document schema created or already exists')
                return True
            else:
                logger.error(f"❌ Schema creation failed: {response.status_code} - {response.text}')
                return False
        except Exception as e:
            logger.error(f"❌ Schema creation error: {e}')
            return False

    def add_document(self, title: str, content: str, source: str, category: str, keywords: List[str]) -> Optional[str]:
        """TODO: Add docstring."""
        """Add a document to Weaviate""'
        document = {
            "class": "MetaAIDocument',
            "properties': {
                "title': title,
                "content': content,
                "source': source,
                "category': category,
                "keywords": ", '.join(keywords),
                "crawled_at': datetime.now().isoformat()
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

    def search_documents(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """TODO: Add docstring."""
        """Search documents in Weaviate""'
        graphql_query = {
            "query": f""'
                {{
                    Get {{
                        MetaAIDocument(
                            limit: {limit}
                            where: {{
                                path: ["content']
                                operator: Like
                                valueText: "*{query}*'
                            }}
                        ) {{
                            title
                            content
                            source
                            category
                            keywords
                            crawled_at
                        }}
                    }}
                }}
            ""'
        }

        try:
            response = self.session.post(f"{self.weaviate_url}/v1/graphql', json=graphql_query)
            if response.status_code == 200:
                data = response.json()
                documents = data.get("data", {}).get("Get", {}).get("MetaAIDocument', [])
                logger.info(f"✅ Found {len(documents)} documents for query: {query}')
                return documents
            else:
                logger.error(f"❌ Search failed: {response.status_code} - {response.text}')
                return []
        except Exception as e:
            logger.error(f"❌ Search error: {e}')
            return []

    def load_meta_documents(self, file_path: str) -> List[Dict[str, Any]]:
        """TODO: Add docstring."""
        """Load Meta AI documents from JSON file""'
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Flatten the nested structure
            documents = []
            for category, items in data.items():
                for item in items:
                    if isinstance(item, dict):
                        # Extract metadata and content
                        metadata = item.get('metadata', {})
                        content = item.get('content', '')

                        # Create document structure
                        doc = {
                            'title': metadata.get('title', f'{category} Document'),
                            'content': content,
                            'source': metadata.get('url', ''),
                            'category': category,
                            'keywords': metadata.get('keywords', [])
                        }
                        documents.append(doc)

            logger.info(f"✅ Loaded {len(documents)} documents from {file_path}')
            return documents
        except Exception as e:
            logger.error(f"❌ Failed to load documents: {e}')
            return []

    def integrate_meta_documents(self, documents: List[Dict[str, Any]]) -> int:
        """TODO: Add docstring."""
        """Integrate Meta AI documents into Weaviate""'
        added_count = 0

        for doc in documents:
            # Handle both dict and string formats
            if isinstance(doc, str):
                # Skip string entries that are just content
                continue
            elif isinstance(doc, dict):
                title = doc.get('title', 'Untitled')
                content = doc.get('content', '') or doc.get('readme_content', '')
                source = doc.get('url', '')
                category = doc.get('category', 'unknown')
                keywords = doc.get('keywords', [])

                if content and len(content) > 50:  # Only add documents with substantial content
                    doc_id = self.add_document(title, content, source, category, keywords)
                    if doc_id:
                        added_count += 1

                    # Add a small delay to avoid overwhelming Weaviate
                    import time
                    time.sleep(0.1)

        logger.info(f"✅ Successfully integrated {added_count} documents')
        return added_count

def main():
    """TODO: Add docstring."""
    """Main integration function""'
    logger.info("🚀 Starting Meta AI Knowledge Base Integration')

    # Initialize integrator
    integrator = MetaAIKnowledgeIntegrator()

    # Test Weaviate connection
    if not integrator.test_weaviate_connection():
        logger.error("❌ Cannot connect to Weaviate. Exiting.')
        return

    # Create schema
    if not integrator.create_document_schema():
        logger.error("❌ Failed to create schema. Exiting.')
        return

    # Load Meta AI documents
    meta_docs_file = "/app/knowledge/meta_documents/all_meta_documents.json'
    documents = integrator.load_meta_documents(meta_docs_file)

    if not documents:
        logger.error("❌ No documents to integrate. Exiting.')
        return

    # Integrate documents
    added_count = integrator.integrate_meta_documents(documents)

    # Test search
    logger.info("🔍 Testing search functionality...')
    results = integrator.search_documents("LLM training', limit=3)

    if results:
        logger.info("✅ Search test successful')
        for i, result in enumerate(results, 1):
            logger.info(f"   {i}. {result.get('title', 'No title')[:50]}...')
    else:
        logger.warning("⚠️ Search test returned no results')

    logger.info(f"🎉 Integration complete! Added {added_count} documents to knowledge base')

if __name__ == "__main__':
    main()
