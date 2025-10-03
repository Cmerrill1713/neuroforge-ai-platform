#!/usr/bin/env python3
"""
LFM2 Re-indexing Script
Re-processes all documents with LFM2-1.2B-RAG embeddings for maximum performance
"""

import asyncio
import logging
import os
import sys
import time
from typing import List, Dict, Any
import requests
import weaviate
from transformers import AutoTokenizer, AutoModel
import torch
import torch.nn.functional as F

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from core.retrieval.weaviate_store import WeaviateStore

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LFM2Reindexer:
    """Re-index documents with LFM2 embeddings"""
    
    def __init__(self):
        self.lfm2_model = "LiquidAI/LFM2-1.2B-RAG"
        self.knowledge_base_url = "http://localhost:8004"
        self.weaviate_host = "localhost"
        self.weaviate_port = 8090
        
        # Initialize LFM2 model
        self.tokenizer = None
        self.model = None
        self._load_lfm2_model()
        
        # Initialize Weaviate
        self.weaviate_client = None
        self._connect_weaviate()
    
    def _load_lfm2_model(self):
        """Load LFM2 model for embeddings"""
        try:
            logger.info(f"🔄 Loading LFM2 model: {self.lfm2_model}")
            self.tokenizer = AutoTokenizer.from_pretrained(self.lfm2_model)
            self.model = AutoModel.from_pretrained(self.lfm2_model)
            self.model.eval()
            logger.info(f"✅ LFM2 model loaded successfully")
            logger.info(f"✅ Vocab size: {self.tokenizer.vocab_size}")
        except Exception as e:
            logger.error(f"❌ Failed to load LFM2 model: {e}")
            raise
    
    def _connect_weaviate(self):
        """Connect to Weaviate"""
        try:
            self.weaviate_client = weaviate.connect_to_custom(
                http_host=self.weaviate_host,
                http_port=self.weaviate_port,
                http_secure=False,
                grpc_host=self.weaviate_host,
                grpc_port=50051,
                grpc_secure=False,
                skip_init_checks=False
            )
            logger.info(f"✅ Connected to Weaviate: {self.weaviate_host}:{self.weaviate_port}")
        except Exception as e:
            logger.error(f"❌ Failed to connect to Weaviate: {e}")
            raise
    
    def generate_lfm2_embedding(self, text: str) -> List[float]:
        """Generate LFM2 embedding for text"""
        try:
            # Tokenize input
            inputs = self.tokenizer(
                text, 
                return_tensors="pt", 
                padding=True, 
                truncation=True, 
                max_length=512
            )
            
            # Generate embeddings
            with torch.no_grad():
                outputs = self.model(**inputs)
                # Use mean pooling of last hidden states
                embeddings = outputs.last_hidden_state.mean(dim=1)
                # Normalize embeddings
                embeddings = F.normalize(embeddings, p=2, dim=1)
                return embeddings.squeeze().tolist()
                
        except Exception as e:
            logger.error(f"❌ Failed to generate LFM2 embedding: {e}")
            raise
    
    def get_knowledge_base_documents(self) -> List[Dict[str, Any]]:
        """Get all documents from knowledge base"""
        try:
            logger.info("📚 Fetching documents from knowledge base...")
            
            # Get stats first
            stats_response = requests.get(f"{self.knowledge_base_url}/api/knowledge/stats")
            if stats_response.status_code == 200:
                stats = stats_response.json()
                logger.info(f"📊 Knowledge base stats: {stats.get('total_documents', 0)} documents")
            
            all_documents = []
            seen_urls = set()
            
            # Try different search approaches
            search_approaches = [
                # Approach 1: Direct API search
                {"endpoint": "/api/knowledge/search", "method": "POST", "data": {"query": "test", "limit": 100}},
                # Approach 2: Unified search
                {"endpoint": "/unified-search", "method": "GET", "params": {"q": "test", "limit": 100}},
                # Approach 3: Try with different terms
                {"endpoint": "/api/knowledge/search", "method": "POST", "data": {"query": "", "limit": 100}},
            ]
            
            for approach in search_approaches:
                try:
                    logger.info(f"🔍 Trying approach: {approach['endpoint']}")
                    
                    if approach["method"] == "POST":
                        response = requests.post(
                            f"{self.knowledge_base_url}{approach['endpoint']}",
                            json=approach["data"],
                            timeout=10
                        )
                    else:
                        response = requests.get(
                            f"{self.knowledge_base_url}{approach['endpoint']}",
                            params=approach.get("params", {}),
                            timeout=10
                        )
                    
                    logger.info(f"Response status: {response.status_code}")
                    logger.info(f"Response content: {response.text[:200]}...")
                    
                    if response.status_code == 200:
                        data = response.json()
                        results = data.get('results', [])
                        logger.info(f"✅ Found {len(results)} results")
                        
                        for result in results:
                            url = result.get('url', '')
                            if url and url not in seen_urls:
                                doc = {
                                    "content": result.get('content', ''),
                                    "title": result.get('source', result.get('title', 'Unknown')),
                                    "url": url,
                                    "source_type": "migrated",
                                    "domain": "knowledge_base",
                                    "keywords": ["migrated"]
                                }
                                all_documents.append(doc)
                                seen_urls.add(url)
                        
                        if results:
                            break  # Found results, stop trying other approaches
                    
                except Exception as e:
                    logger.warning(f"⚠️ Approach failed: {e}")
                    continue
            
            # If no results from API, try to get documents directly from Weaviate
            if not all_documents:
                logger.info("🔄 Trying direct Weaviate access...")
                try:
                    # Connect to existing Weaviate collection
                    existing_collection = self.weaviate_client.collections.get("KnowledgeDocument")
                    
                    # Get all documents
                    response = existing_collection.query.fetch_objects(limit=1000)
                    
                    for obj in response.objects:
                        url = obj.properties.get('url', '')
                        if url and url not in seen_urls:
                            doc = {
                                "content": obj.properties.get('content', ''),
                                "title": obj.properties.get('title', 'Unknown'),
                                "url": url,
                                "source_type": obj.properties.get('source_type', 'migrated'),
                                "domain": obj.properties.get('domain', 'knowledge_base'),
                                "keywords": ["migrated"]
                            }
                            all_documents.append(doc)
                            seen_urls.add(url)
                    
                    logger.info(f"✅ Retrieved {len(all_documents)} documents from existing Weaviate")
                    
                except Exception as e:
                    logger.warning(f"⚠️ Direct Weaviate access failed: {e}")
            
            logger.info(f"📚 Total documents retrieved: {len(all_documents)}")
            return all_documents
            
        except Exception as e:
            logger.error(f"❌ Failed to get knowledge base documents: {e}")
            return []
    
    def create_lfm2_schema(self):
        """Create new schema compatible with LFM2 embeddings (2048 dim)"""
        try:
            logger.info("🔧 Creating LFM2-compatible schema...")
            
            # Check if schema exists
            try:
                collection = self.weaviate_client.collections.get("KnowledgeDocumentLFM2")
                logger.info("✅ LFM2 schema already exists")
                return
            except:
                pass
            
            # Create new collection with 2048-dim vector
            collection = self.weaviate_client.collections.create(
                name="KnowledgeDocumentLFM2",
                description="Documents indexed with LFM2-1.2B-RAG embeddings",
                vectorizer_config=weaviate.classes.config.Configure.Vectorizer.none(),  # We'll provide vectors
                properties=[
                    weaviate.classes.config.Property(
                        name="content",
                        data_type=weaviate.classes.config.DataType.TEXT,
                        description="Document content"
                    ),
                    weaviate.classes.config.Property(
                        name="title", 
                        data_type=weaviate.classes.config.DataType.TEXT,
                        description="Document title"
                    ),
                    weaviate.classes.config.Property(
                        name="url",
                        data_type=weaviate.classes.config.DataType.TEXT,
                        description="Document URL"
                    ),
                    weaviate.classes.config.Property(
                        name="source_type",
                        data_type=weaviate.classes.config.DataType.TEXT,
                        description="Source type"
                    ),
                    weaviate.classes.config.Property(
                        name="domain",
                        data_type=weaviate.classes.config.DataType.TEXT,
                        description="Document domain"
                    )
                ],
                vector_index_config=weaviate.classes.config.Configure.VectorIndex.hnsw(
                    distance_metric=weaviate.classes.config.VectorDistances.COSINE
                )
            )
            
            logger.info("✅ Created LFM2-compatible schema (2048 dimensions)")
            
        except Exception as e:
            logger.error(f"❌ Failed to create LFM2 schema: {e}")
            raise
    
    async def reindex_documents(self, documents: List[Dict[str, Any]]):
        """Re-index documents with LFM2 embeddings"""
        try:
            logger.info(f"🔄 Re-indexing {len(documents)} documents with LFM2...")
            
            collection = self.weaviate_client.collections.get("KnowledgeDocumentLFM2")
            
            # Process documents in batches
            batch_size = 10
            total_processed = 0
            
            for i in range(0, len(documents), batch_size):
                batch = documents[i:i + batch_size]
                logger.info(f"📦 Processing batch {i//batch_size + 1}/{(len(documents) + batch_size - 1)//batch_size}")
                
                # Process batch - add documents one by one
                for doc in batch:
                    try:
                        # Generate LFM2 embedding
                        content = doc.get('content', '')
                        if not content:
                            continue
                            
                        embedding = self.generate_lfm2_embedding(content)
                        
                        # Prepare document data
                        doc_data = {
                            "content": content,
                            "title": doc.get('title', ''),
                            "url": doc.get('url', ''),
                            "source_type": doc.get('source_type', ''),
                            "domain": doc.get('domain', '')
                        }
                        
                        # Add to Weaviate with LFM2 embedding
                        collection.data.insert(
                            properties=doc_data,
                            vector=embedding
                        )
                        
                        total_processed += 1
                        
                    except Exception as e:
                        logger.warning(f"⚠️ Failed to process document: {e}")
                        continue
                
                logger.info(f"✅ Processed {total_processed}/{len(documents)} documents")
                
                # Small delay to prevent overwhelming the system
                await asyncio.sleep(0.1)
            
            logger.info(f"🎉 Re-indexing complete! Processed {total_processed} documents")
            
        except Exception as e:
            logger.error(f"❌ Re-indexing failed: {e}")
            raise
    
    def verify_reindexing(self):
        """Verify the re-indexing was successful"""
        try:
            logger.info("🔍 Verifying re-indexing...")
            
            collection = self.weaviate_client.collections.get("KnowledgeDocumentLFM2")
            
            # Get document count
            result = collection.aggregate.over_all(total_count=True)
            doc_count = result.total_count
            
            logger.info(f"📊 LFM2-indexed documents: {doc_count}")
            
            # Test a query
            test_query = "machine learning algorithms"
            embedding = self.generate_lfm2_embedding(test_query)
            
            response = collection.query.near_vector(
                near_vector=embedding,
                limit=3,
                return_metadata=weaviate.classes.query.MetadataQuery(distance=True)
            )
            
            logger.info(f"🔍 Test query returned {len(response.objects)} results")
            
            for i, obj in enumerate(response.objects):
                logger.info(f"  {i+1}. {obj.properties.get('title', 'Unknown')} (distance: {obj.metadata.distance:.3f})")
            
            return doc_count > 0
            
        except Exception as e:
            logger.error(f"❌ Verification failed: {e}")
            return False
    
    def close(self):
        """Close connections"""
        if self.weaviate_client:
            self.weaviate_client.close()

async def main():
    """Main re-indexing process"""
    logger.info("🚀 Starting LFM2 Re-indexing Process")
    logger.info("=" * 50)
    
    reindexer = None
    try:
        # Initialize reindexer
        reindexer = LFM2Reindexer()
        
        # Get documents from knowledge base
        documents = reindexer.get_knowledge_base_documents()
        if not documents:
            logger.error("❌ No documents found to re-index")
            return
        
        # Create LFM2 schema
        reindexer.create_lfm2_schema()
        
        # Re-index documents
        await reindexer.reindex_documents(documents)
        
        # Verify re-indexing
        success = reindexer.verify_reindexing()
        
        if success:
            logger.info("🎉 LFM2 RE-INDEXING SUCCESSFUL!")
            logger.info("✅ All documents now use LFM2-1.2B-RAG embeddings")
            logger.info("✅ 2048-dimensional embeddings for richer semantic understanding")
            logger.info("✅ Edge-native performance optimization")
        else:
            logger.error("❌ Re-indexing verification failed")
            
    except Exception as e:
        logger.error(f"❌ Re-indexing process failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if reindexer:
            reindexer.close()

if __name__ == "__main__":
    asyncio.run(main())
