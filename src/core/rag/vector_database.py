"""
Advanced Vector Database System for Agentic LLM Core v2.0

This module provides ChromaDB-based vector database capabilities for advanced RAG,
including semantic search, document chunking, and retrieval optimization.

Created: 2024-09-28
Status: Production Ready
"""

import asyncio
import logging
import uuid
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

import chromadb
from chromadb.config import Settings
from pydantic import BaseModel, Field
from sentence_transformers import SentenceTransformer

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


# ============================================================================
# Data Models
# ============================================================================

class DocumentType(str, Enum):
    """Types of documents that can be stored."""
    TEXT = "text"
    CODE = "code"
    MARKDOWN = "markdown"
    PDF = "pdf"
    IMAGE_DESCRIPTION = "image_description"
    CONVERSATION = "conversation"
    KNOWLEDGE_BASE = "knowledge_base"


class ChunkingStrategy(str, Enum):
    """Document chunking strategies."""
    FIXED_SIZE = "fixed_size"
    SEMANTIC = "semantic"
    SENTENCE = "sentence"
    PARAGRAPH = "paragraph"
    CODE_BLOCK = "code_block"


class DocumentChunk(BaseModel):
    """A chunk of a document."""
    chunk_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    document_id: str = Field(..., description="ID of the parent document")
    content: str = Field(..., description="Chunk content")
    chunk_index: int = Field(..., description="Index of chunk in document")
    metadata: Dict[str, Any] = Field(default_factory=dict)
    embedding: Optional[List[float]] = Field(None, description="Vector embedding")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class Document(BaseModel):
    """A document in the vector database."""
    document_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str = Field(..., description="Document title")
    content: str = Field(..., description="Full document content")
    document_type: DocumentType = Field(DocumentType.TEXT)
    source: Optional[str] = Field(None, description="Source file path or URL")
    metadata: Dict[str, Any] = Field(default_factory=dict)
    chunks: List[DocumentChunk] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class SearchResult(BaseModel):
    """Search result from vector database."""
    chunk_id: str = Field(..., description="ID of the matching chunk")
    document_id: str = Field(..., description="ID of the parent document")
    content: str = Field(..., description="Chunk content")
    similarity_score: float = Field(..., description="Similarity score (0-1)")
    metadata: Dict[str, Any] = Field(default_factory=dict)
    document_title: Optional[str] = Field(None, description="Parent document title")


class SearchRequest(BaseModel):
    """Search request for vector database."""
    query: str = Field(..., description="Search query")
    limit: int = Field(10, ge=1, le=100, description="Maximum results to return")
    similarity_threshold: float = Field(0.7, ge=0.0, le=1.0, description="Minimum similarity score")
    document_types: Optional[List[DocumentType]] = Field(None, description="Filter by document types")
    metadata_filters: Optional[Dict[str, Any]] = Field(None, description="Metadata filters")
    include_metadata: bool = Field(True, description="Include metadata in results")


# ============================================================================
# Document Chunking
# ============================================================================

class DocumentChunker:
    """Handles document chunking strategies."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def chunk_document(
        self, 
        document: Document, 
        strategy: ChunkingStrategy = ChunkingStrategy.SEMANTIC,
        chunk_size: int = 512,
        overlap: int = 50
    ) -> List[DocumentChunk]:
        """Chunk a document based on the specified strategy."""
        
        if strategy == ChunkingStrategy.FIXED_SIZE:
            return self._chunk_fixed_size(document, chunk_size, overlap)
        elif strategy == ChunkingStrategy.SENTENCE:
            return self._chunk_by_sentences(document, chunk_size)
        elif strategy == ChunkingStrategy.PARAGRAPH:
            return self._chunk_by_paragraphs(document)
        elif strategy == ChunkingStrategy.CODE_BLOCK:
            return self._chunk_code_blocks(document)
        else:  # SEMANTIC
            return self._chunk_semantic(document, chunk_size)
    
    def _chunk_fixed_size(
        self, 
        document: Document, 
        chunk_size: int, 
        overlap: int
    ) -> List[DocumentChunk]:
        """Chunk document into fixed-size pieces."""
        chunks = []
        content = document.content
        start = 0
        
        while start < len(content):
            end = min(start + chunk_size, len(content))
            chunk_content = content[start:end]
            
            # Try to break at word boundary
            if end < len(content):
                last_space = chunk_content.rfind(' ')
                if last_space > chunk_size * 0.8:  # If we can break at 80% of chunk size
                    chunk_content = chunk_content[:last_space]
                    end = start + last_space
            
            chunk = DocumentChunk(
                document_id=document.document_id,
                content=chunk_content.strip(),
                chunk_index=len(chunks),
                metadata={
                    "chunking_strategy": "fixed_size",
                    "chunk_size": len(chunk_content),
                    "start_pos": start,
                    "end_pos": end
                }
            )
            chunks.append(chunk)
            
            start = end - overlap
        
        return chunks
    
    def _chunk_by_sentences(self, document: Document, max_chunk_size: int) -> List[DocumentChunk]:
        """Chunk document by sentences."""
        import re
        
        # Split by sentences (simple regex)
        sentences = re.split(r'[.!?]+', document.content)
        chunks = []
        current_chunk = ""
        chunk_index = 0
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
                
            if len(current_chunk) + len(sentence) > max_chunk_size and current_chunk:
                # Create chunk
                chunk = DocumentChunk(
                    document_id=document.document_id,
                    content=current_chunk.strip(),
                    chunk_index=chunk_index,
                    metadata={
                        "chunking_strategy": "sentence",
                        "sentence_count": current_chunk.count('.') + current_chunk.count('!') + current_chunk.count('?')
                    }
                )
                chunks.append(chunk)
                current_chunk = sentence
                chunk_index += 1
            else:
                current_chunk += " " + sentence if current_chunk else sentence
        
        # Add final chunk
        if current_chunk:
            chunk = DocumentChunk(
                document_id=document.document_id,
                content=current_chunk.strip(),
                chunk_index=chunk_index,
                metadata={
                    "chunking_strategy": "sentence",
                    "sentence_count": current_chunk.count('.') + current_chunk.count('!') + current_chunk.count('?')
                }
            )
            chunks.append(chunk)
        
        return chunks
    
    def _chunk_by_paragraphs(self, document: Document) -> List[DocumentChunk]:
        """Chunk document by paragraphs."""
        paragraphs = document.content.split('\n\n')
        chunks = []
        
        for i, paragraph in enumerate(paragraphs):
            if paragraph.strip():
                chunk = DocumentChunk(
                    document_id=document.document_id,
                    content=paragraph.strip(),
                    chunk_index=i,
                    metadata={
                        "chunking_strategy": "paragraph",
                        "paragraph_length": len(paragraph)
                    }
                )
                chunks.append(chunk)
        
        return chunks
    
    def _chunk_code_blocks(self, document: Document) -> List[DocumentChunk]:
        """Chunk document by code blocks."""
        import re
        
        # Find code blocks (between ``` or indented)
        code_pattern = r'```[\s\S]*?```|^    .*$'
        code_blocks = re.findall(code_pattern, document.content, re.MULTILINE)
        
        chunks = []
        for i, code_block in enumerate(code_blocks):
            chunk = DocumentChunk(
                document_id=document.document_id,
                content=code_block.strip(),
                chunk_index=i,
                metadata={
                    "chunking_strategy": "code_block",
                    "is_code": True,
                    "language": self._detect_code_language(code_block)
                }
            )
            chunks.append(chunk)
        
        return chunks
    
    def _chunk_semantic(self, document: Document, chunk_size: int) -> List[DocumentChunk]:
        """Chunk document semantically (simplified version)."""
        # For now, use sentence-based chunking as semantic chunking
        # In a full implementation, you'd use semantic similarity
        return self._chunk_by_sentences(document, chunk_size)
    
    def _detect_code_language(self, code_block: str) -> str:
        """Detect programming language from code block."""
        if 'def ' in code_block or 'import ' in code_block:
            return 'python'
        elif 'function ' in code_block or 'const ' in code_block:
            return 'javascript'
        elif 'class ' in code_block and '{' in code_block:
            return 'java'
        elif '#include' in code_block:
            return 'cpp'
        else:
            return 'unknown'


# ============================================================================
# Vector Database System
# ============================================================================

class VectorDatabase:
    """Advanced vector database system using ChromaDB."""
    
    def __init__(self, persist_directory: str = "./vector_db"):
        self.logger = logging.getLogger(__name__)
        self.persist_directory = Path(persist_directory)
        self.persist_directory.mkdir(exist_ok=True)
        
        # Initialize ChromaDB
        self.client = chromadb.PersistentClient(
            path=str(self.persist_directory),
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        # Initialize embedding model
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Initialize chunker
        self.chunker = DocumentChunker()
        
        # Collection for documents
        self.collection = self.client.get_or_create_collection(
            name="agentic_llm_documents",
            metadata={"description": "Agentic LLM Core document collection"}
        )
        
        self.logger.info(f"Vector database initialized at {self.persist_directory}")
    
    async def add_document(
        self, 
        document: Document, 
        chunking_strategy: ChunkingStrategy = ChunkingStrategy.SEMANTIC
    ) -> str:
        """Add a document to the vector database."""
        try:
            # Chunk the document
            chunks = self.chunker.chunk_document(document, chunking_strategy)
            document.chunks = chunks
            
            # Generate embeddings for chunks
            chunk_contents = [chunk.content for chunk in chunks]
            embeddings = self.embedding_model.encode(chunk_contents).tolist()
            
            # Prepare data for ChromaDB
            chunk_ids = [chunk.chunk_id for chunk in chunks]
            metadatas = []
            
            for i, chunk in enumerate(chunks):
                metadata = {
                    "document_id": document.document_id,
                    "document_title": document.title,
                    "document_type": document.document_type.value,
                    "chunk_index": chunk.chunk_index,
                    "source": document.source or "",
                    "created_at": document.created_at.isoformat(),
                    **chunk.metadata,
                    **document.metadata
                }
                metadatas.append(metadata)
            
            # Add to ChromaDB
            self.collection.add(
                ids=chunk_ids,
                embeddings=embeddings,
                documents=chunk_contents,
                metadatas=metadatas
            )
            
            self.logger.info(f"Added document '{document.title}' with {len(chunks)} chunks")
            return document.document_id
            
        except Exception as e:
            self.logger.error(f"Failed to add document: {e}")
            raise
    
    async def search(
        self, 
        request: SearchRequest
    ) -> List[SearchResult]:
        """Search the vector database."""
        try:
            # Generate query embedding
            query_embedding = self.embedding_model.encode([request.query]).tolist()[0]
            
            # Prepare where clause for filtering
            where_clause = {}
            if request.document_types:
                where_clause["document_type"] = {"$in": [dt.value for dt in request.document_types]}
            
            if request.metadata_filters:
                where_clause.update(request.metadata_filters)
            
            # Search ChromaDB
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=request.limit,
                where=where_clause if where_clause else None,
                include=["documents", "metadatas", "distances"]
            )
            
            # Convert to SearchResult objects
            search_results = []
            if results['ids'] and results['ids'][0]:
                for i, chunk_id in enumerate(results['ids'][0]):
                    distance = results['distances'][0][i]
                    similarity_score = 1 - distance  # Convert distance to similarity
                    
                    if similarity_score >= request.similarity_threshold:
                        result = SearchResult(
                            chunk_id=chunk_id,
                            document_id=results['metadatas'][0][i]['document_id'],
                            content=results['documents'][0][i],
                            similarity_score=similarity_score,
                            metadata=results['metadatas'][0][i] if request.include_metadata else {},
                            document_title=results['metadatas'][0][i].get('document_title')
                        )
                        search_results.append(result)
            
            self.logger.info(f"Search returned {len(search_results)} results for query: {request.query[:50]}...")
            return search_results
            
        except Exception as e:
            self.logger.error(f"Search failed: {e}")
            raise
    
    async def get_document(self, document_id: str) -> Optional[Document]:
        """Get a document by ID."""
        try:
            # Search for chunks belonging to this document
            results = self.collection.get(
                where={"document_id": document_id},
                include=["documents", "metadatas"]
            )
            
            if not results['ids']:
                return None
            
            # Reconstruct document
            chunks = []
            document_title = None
            
            for i, chunk_id in enumerate(results['ids']):
                metadata = results['metadatas'][i]
                if document_title is None:
                    document_title = metadata.get('document_title', 'Unknown')
                
                chunk = DocumentChunk(
                    chunk_id=chunk_id,
                    document_id=document_id,
                    content=results['documents'][i],
                    chunk_index=metadata.get('chunk_index', i),
                    metadata=metadata
                )
                chunks.append(chunk)
            
            # Sort chunks by index
            chunks.sort(key=lambda x: x.chunk_index)
            
            # Reconstruct document content
            content = '\n'.join([chunk.content for chunk in chunks])
            
            document = Document(
                document_id=document_id,
                title=document_title,
                content=content,
                document_type=DocumentType(results['metadatas'][0].get('document_type', 'text')),
                source=results['metadatas'][0].get('source'),
                metadata=results['metadatas'][0],
                chunks=chunks
            )
            
            return document
            
        except Exception as e:
            self.logger.error(f"Failed to get document {document_id}: {e}")
            return None
    
    async def delete_document(self, document_id: str) -> bool:
        """Delete a document and all its chunks."""
        try:
            # Get all chunk IDs for this document
            results = self.collection.get(
                where={"document_id": document_id},
                include=[]
            )
            
            if results['ids']:
                self.collection.delete(ids=results['ids'])
                self.logger.info(f"Deleted document {document_id} with {len(results['ids'])} chunks")
                return True
            else:
                self.logger.warning(f"Document {document_id} not found")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to delete document {document_id}: {e}")
            return False
    
    async def get_collection_stats(self) -> Dict[str, Any]:
        """Get collection statistics."""
        try:
            count = self.collection.count()
            return {
                "total_chunks": count,
                "collection_name": self.collection.name,
                "persist_directory": str(self.persist_directory)
            }
        except Exception as e:
            self.logger.error(f"Failed to get collection stats: {e}")
            return {"error": str(e)}
    
    async def reset_collection(self) -> bool:
        """Reset the entire collection."""
        try:
            self.client.delete_collection("agentic_llm_documents")
            self.collection = self.client.create_collection(
                name="agentic_llm_documents",
                metadata={"description": "Agentic LLM Core document collection"}
            )
            self.logger.info("Collection reset successfully")
            return True
        except Exception as e:
            self.logger.error(f"Failed to reset collection: {e}")
            return False


# ============================================================================
# RAG System Integration
# ============================================================================

class AdvancedRAGSystem:
    """Advanced RAG system using vector database."""
    
    def __init__(self, vector_db: Optional[VectorDatabase] = None):
        self.logger = logging.getLogger(__name__)
        self.vector_db = vector_db or VectorDatabase()
    
    async def add_knowledge(
        self, 
        title: str, 
        content: str, 
        document_type: DocumentType = DocumentType.KNOWLEDGE_BASE,
        source: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Add knowledge to the RAG system."""
        document = Document(
            title=title,
            content=content,
            document_type=document_type,
            source=source,
            metadata=metadata or {}
        )
        
        return await self.vector_db.add_document(document)
    
    async def retrieve_relevant_context(
        self, 
        query: str, 
        limit: int = 5,
        similarity_threshold: float = 0.7
    ) -> List[SearchResult]:
        """Retrieve relevant context for a query."""
        search_request = SearchRequest(
            query=query,
            limit=limit,
            similarity_threshold=similarity_threshold,
            include_metadata=True
        )
        
        return await self.vector_db.search(search_request)
    
    async def generate_contextual_response(
        self, 
        query: str, 
        context_limit: int = 5
    ) -> Dict[str, Any]:
        """Generate a response with relevant context."""
        # Retrieve relevant context
        context_results = await self.retrieve_relevant_context(query, context_limit)
        
        # Format context for LLM
        context_text = ""
        if context_results:
            context_text = "Relevant Context:\n"
            for i, result in enumerate(context_results, 1):
                context_text += f"{i}. {result.content}\n"
                if result.document_title:
                    context_text += f"   (Source: {result.document_title})\n"
            context_text += "\n"
        
        return {
            "query": query,
            "context": context_text,
            "context_sources": [result.document_title for result in context_results if result.document_title],
            "similarity_scores": [result.similarity_score for result in context_results],
            "context_count": len(context_results)
        }


# ============================================================================
# Main Function
# ============================================================================

async def main():
    """Main function for testing the vector database system."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Vector Database System")
    parser.add_argument("--action", choices=["add", "search", "stats", "reset"], required=True)
    parser.add_argument("--title", help="Document title")
    parser.add_argument("--content", help="Document content")
    parser.add_argument("--query", help="Search query")
    parser.add_argument("--limit", type=int, default=5, help="Search result limit")
    
    args = parser.parse_args()
    
    try:
        # Initialize vector database
        vector_db = VectorDatabase()
        rag_system = AdvancedRAGSystem(vector_db)
        
        if args.action == "add":
            if not args.title or not args.content:
                print("Error: --title and --content are required for add action")
                return 1
            
            doc_id = await rag_system.add_knowledge(args.title, args.content)
            print(f"✅ Added document: {doc_id}")
            
        elif args.action == "search":
            if not args.query:
                print("Error: --query is required for search action")
                return 1
            
            results = await rag_system.retrieve_relevant_context(args.query, args.limit)
            print(f"\n🔍 Search Results for: {args.query}")
            print("=" * 50)
            
            for i, result in enumerate(results, 1):
                print(f"\n{i}. Similarity: {result.similarity_score:.3f}")
                print(f"   Content: {result.content[:200]}...")
                if result.document_title:
                    print(f"   Source: {result.document_title}")
            
        elif args.action == "stats":
            stats = await vector_db.get_collection_stats()
            print("📊 Collection Statistics:")
            print(f"   Total chunks: {stats.get('total_chunks', 0)}")
            print(f"   Collection: {stats.get('collection_name', 'Unknown')}")
            
        elif args.action == "reset":
            success = await vector_db.reset_collection()
            if success:
                print("✅ Collection reset successfully")
            else:
                print("❌ Failed to reset collection")
                return 1
        
        return 0
        
    except Exception as e:
        logger.error(f"Vector database operation failed: {e}")
        return 1


if __name__ == "__main__":
    exit(asyncio.run(main()))
