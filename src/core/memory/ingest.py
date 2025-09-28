"""
Document Ingestion Pipeline for Agentic LLM Core v0.1

This module provides a comprehensive document ingestion pipeline with support for:
- Multiple document formats (text, PDF, images, audio, video)
- Chunking and preprocessing
- Vector embedding generation
- Batch processing and parallel ingestion
- Progress tracking and error handling

Created: 2024-09-24
Status: Draft
"""

from __future__ import annotations

import hashlib
import io
import logging
import uuid
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

import aiofiles
import aiohttp
from pydantic import BaseModel, Field, field_validator

from .vector_pg import Document, DocumentType, DocumentStatus, VectorStore
from ..providers.llm_qwen3 import Qwen3Provider, Qwen3EmbedRequest


# ============================================================================
# Ingestion Models
# ============================================================================

class IngestionStatus(str, Enum):
    """Ingestion process status."""
    PENDING = "pending"
    PROCESSING = "processing"
    CHUNKING = "chunking"
    EMBEDDING = "embedding"
    INDEXING = "indexing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class IngestionSource(BaseModel):
    """Source information for ingestion."""
    source_type: str = Field(..., description="Type of source (file, url, text)")
    source_path: Optional[str] = Field(None, description="Path or URL to source")
    source_content: Optional[str] = Field(None, description="Direct content for text sources")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Source metadata")
    
    @field_validator('source_type')
    @classmethod
    def validate_source_type(cls, v):
        allowed_types = ['file', 'url', 'text', 'stream']
        if v not in allowed_types:
            raise ValueError(f"Source type must be one of: {allowed_types}")
        return v


class ChunkingConfig(BaseModel):
    """Configuration for document chunking."""
    chunk_size: int = Field(default=1000, ge=100, le=10000, description="Maximum chunk size in characters")
    chunk_overlap: int = Field(default=200, ge=0, le=1000, description="Overlap between chunks")
    preserve_sentences: bool = Field(default=True, description="Preserve sentence boundaries")
    preserve_paragraphs: bool = Field(default=True, description="Preserve paragraph boundaries")
    min_chunk_size: int = Field(default=100, ge=10, description="Minimum chunk size")
    
    @field_validator('chunk_overlap')
    @classmethod
    def validate_chunk_overlap(cls, v, values):
        if 'chunk_size' in values and v >= values['chunk_size']:
            raise ValueError("Chunk overlap must be less than chunk size")
        return v


class EmbeddingConfig(BaseModel):
    """Configuration for embedding generation."""
    model_name: str = Field(default="qwen3-omni", description="Embedding model name")
    batch_size: int = Field(default=32, ge=1, le=128, description="Batch size for embedding generation")
    normalize_embeddings: bool = Field(default=True, description="Normalize embeddings")
    cache_embeddings: bool = Field(default=True, description="Cache embeddings for reuse")


class IngestionJob(BaseModel):
    """Ingestion job model."""
    job_id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique job ID")
    sources: List[IngestionSource] = Field(..., description="Sources to ingest")
    chunking_config: ChunkingConfig = Field(default_factory=ChunkingConfig, description="Chunking configuration")
    embedding_config: EmbeddingConfig = Field(default_factory=EmbeddingConfig, description="Embedding configuration")
    status: IngestionStatus = Field(default=IngestionStatus.PENDING, description="Job status")
    progress: float = Field(default=0.0, ge=0.0, le=1.0, description="Progress percentage")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), description="Creation timestamp")
    started_at: Optional[datetime] = Field(None, description="Start timestamp")
    completed_at: Optional[datetime] = Field(None, description="Completion timestamp")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Job metadata")
    
    # Results
    total_documents: int = Field(default=0, description="Total documents processed")
    total_chunks: int = Field(default=0, description="Total chunks created")
    successful_documents: int = Field(default=0, description="Successfully processed documents")
    failed_documents: int = Field(default=0, description="Failed documents")


# ============================================================================
# Document Processors
# ============================================================================

class DocumentProcessor(ABC):
    """Abstract base class for document processors."""
    
    @abstractmethod
    async def can_process(self, source: IngestionSource) -> bool:
        """Check if this processor can handle the source."""
        pass
    
    @abstractmethod
    async def process(self, source: IngestionSource) -> List[Document]:
        """Process the source and return documents."""
        pass


class TextProcessor(DocumentProcessor):
    """Processor for plain text documents."""
    
    async def can_process(self, source: IngestionSource) -> bool:
        """Check if this is a text source."""
        if source.source_type == "text":
            return True
        
        if source.source_type == "file":
            path = Path(source.source_path)
            return path.suffix.lower() in ['.txt', '.md', '.rst']
        
        return False
    
    async def process(self, source: IngestionSource) -> List[Document]:
        """Process text source."""
        if source.source_type == "text":
            content = source.source_content
        else:
            async with aiofiles.open(source.source_path, 'r', encoding='utf-8') as f:
                content = await f.read()
        
        # Create document
        doc = Document(
            content=content,
            title=source.metadata.get('title', 'Untitled Text Document'),
            doc_type=DocumentType.TEXT,
            metadata=source.metadata,
            source=source.source_path or "direct_text",
            status=DocumentStatus.PENDING
        )
        
        return [doc]


class PDFProcessor(DocumentProcessor):
    """Processor for PDF documents."""
    
    async def can_process(self, source: IngestionSource) -> bool:
        """Check if this is a PDF source."""
        if source.source_type == "file":
            path = Path(source.source_path)
            return path.suffix.lower() == '.pdf'
        return False
    
    async def process(self, source: IngestionSource) -> List[Document]:
        """Process PDF source."""
        try:
            import PyPDF2
        except ImportError:
            raise ImportError("PyPDF2 is required for PDF processing. Install with: pip install PyPDF2")
        
        documents = []
        
        async with aiofiles.open(source.source_path, 'rb') as f:
            pdf_content = await f.read()
            
            # Create PDF reader
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_content))
            
            # Extract text from each page
            for page_num, page in enumerate(pdf_reader.pages):
                try:
                    text = page.extract_text()
                    if text.strip():
                        doc = Document(
                            content=text,
                            title=f"{source.metadata.get('title', 'PDF Document')} - Page {page_num + 1}",
                            doc_type=DocumentType.PDF,
                            metadata={
                                **source.metadata,
                                'page_number': page_num + 1,
                                'total_pages': len(pdf_reader.pages)
                            },
                            source=source.source_path,
                            status=DocumentStatus.PENDING
                        )
                        documents.append(doc)
                except Exception as e:
                    logging.warning(f"Failed to extract text from page {page_num + 1}: {e}")
                    continue
        
        return documents


class ImageProcessor(DocumentProcessor):
    """Processor for image documents."""
    
    async def can_process(self, source: IngestionSource) -> bool:
        """Check if this is an image source."""
        if source.source_type == "file":
            path = Path(source.source_path)
            return path.suffix.lower() in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff']
        return False
    
    async def process(self, source: IngestionSource) -> List[Document]:
        """Process image source."""
        try:
            from PIL import Image
            import pytesseract
        except ImportError:
            raise ImportError("PIL and pytesseract are required for image processing. Install with: pip install Pillow pytesseract")
        
        # Load image
        image = Image.open(source.source_path)
        
        # Extract text using OCR
        try:
            text = pytesseract.image_to_string(image)
        except Exception as e:
            logging.warning(f"OCR failed for {source.source_path}: {e}")
            text = f"[Image: {source.source_path}] - OCR extraction failed"
        
        # Create document
        doc = Document(
            content=text,
            title=source.metadata.get('title', f"Image Document: {Path(source.source_path).name}"),
            doc_type=DocumentType.IMAGE,
            metadata={
                **source.metadata,
                'image_size': image.size,
                'image_mode': image.mode,
                'ocr_extracted': True
            },
            source=source.source_path,
            status=DocumentStatus.PENDING
        )
        
        return [doc]


class URLProcessor(DocumentProcessor):
    """Processor for URL sources."""
    
    async def can_process(self, source: IngestionSource) -> bool:
        """Check if this is a URL source."""
        return source.source_type == "url"
    
    async def process(self, source: IngestionSource) -> List[Document]:
        """Process URL source."""
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(source.source_path) as response:
                    if response.status == 200:
                        content = await response.text()
                        
                        # Extract title from HTML if possible
                        title = source.metadata.get('title')
                        if not title:
                            import re
                            title_match = re.search(r'<title>(.*?)</title>', content, re.IGNORECASE)
                            if title_match:
                                title = title_match.group(1).strip()
                            else:
                                title = f"Web Page: {urlparse(source.source_path).netloc}"
                        
                        # Clean HTML content (basic)
                        import re
                        clean_content = re.sub(r'<[^>]+>', '', content)
                        clean_content = re.sub(r'\s+', ' ', clean_content).strip()
                        
                        doc = Document(
                            content=clean_content,
                            title=title,
                            doc_type=DocumentType.TEXT,
                            metadata={
                                **source.metadata,
                                'url': source.source_path,
                                'response_status': response.status,
                                'content_type': response.headers.get('content-type', '')
                            },
                            source=source.source_path,
                            status=DocumentStatus.PENDING
                        )
                        
                        return [doc]
                    else:
                        raise Exception(f"HTTP {response.status}: {response.reason}")
                        
            except Exception as e:
                raise Exception(f"Failed to fetch URL {source.source_path}: {e}")


# ============================================================================
# Chunking Engine
# ============================================================================

class ChunkingEngine:
    """Engine for chunking documents."""
    
    def __init__(self, config: ChunkingConfig):
        self.config = config
    
    def chunk_document(self, document: Document) -> List[Document]:
        """Chunk a document into smaller pieces."""
        content = document.content
        
        if len(content) <= self.config.chunk_size:
            return [document]
        
        chunks = []
        
        if self.config.preserve_paragraphs:
            chunks = self._chunk_by_paragraphs(content)
        elif self.config.preserve_sentences:
            chunks = self._chunk_by_sentences(content)
        else:
            chunks = self._chunk_by_characters(content)
        
        # Create chunk documents
        chunk_docs = []
        for i, chunk_content in enumerate(chunks):
            if len(chunk_content.strip()) >= self.config.min_chunk_size:
                chunk_doc = Document(
                    content=chunk_content,
                    title=f"{document.title} - Chunk {i + 1}",
                    doc_type=document.doc_type,
                    metadata={
                        **document.metadata,
                        'chunk_index': i,
                        'total_chunks': len(chunks),
                        'original_document_id': document.id
                    },
                    source=document.source,
                    chunk_index=i,
                    parent_id=document.id,
                    status=DocumentStatus.PENDING
                )
                chunk_docs.append(chunk_doc)
        
        return chunk_docs
    
    def _chunk_by_paragraphs(self, content: str) -> List[str]:
        """Chunk content by paragraphs."""
        paragraphs = content.split('\n\n')
        chunks = []
        current_chunk = ""
        
        for paragraph in paragraphs:
            if len(current_chunk) + len(paragraph) <= self.config.chunk_size:
                current_chunk += paragraph + "\n\n"
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = paragraph + "\n\n"
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def _chunk_by_sentences(self, content: str) -> List[str]:
        """Chunk content by sentences."""
        import re
        
        # Simple sentence splitting
        sentences = re.split(r'[.!?]+', content)
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
                
            if len(current_chunk) + len(sentence) <= self.config.chunk_size:
                current_chunk += sentence + ". "
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = sentence + ". "
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def _chunk_by_characters(self, content: str) -> List[str]:
        """Chunk content by character count."""
        chunks = []
        start = 0
        
        while start < len(content):
            end = start + self.config.chunk_size
            
            # Add overlap if not at the beginning
            if start > 0:
                start = max(0, start - self.config.chunk_overlap)
            
            chunk = content[start:end]
            chunks.append(chunk)
            start = end
        
        return chunks


# ============================================================================
# Embedding Generator
# ============================================================================

class EmbeddingGenerator:
    """Generator for document embeddings."""
    
    def __init__(self, provider: Qwen3Provider, config: EmbeddingConfig):
        self.provider = provider
        self.config = config
        self.cache: Dict[str, List[float]] = {}
    
    async def generate_embeddings(self, documents: List[Document]) -> List[List[float]]:
        """Generate embeddings for documents."""
        embeddings = []
        
        # Process in batches
        for i in range(0, len(documents), self.config.batch_size):
            batch = documents[i:i + self.config.batch_size]
            batch_embeddings = await self._generate_batch_embeddings(batch)
            embeddings.extend(batch_embeddings)
        
        return embeddings
    
    async def _generate_batch_embeddings(self, documents: List[Document]) -> List[List[float]]:
        """Generate embeddings for a batch of documents."""
        # Check cache first
        cached_embeddings = []
        uncached_docs = []
        
        for doc in documents:
            content_hash = hashlib.md5(doc.content.encode()).hexdigest()
            if self.config.cache_embeddings and content_hash in self.cache:
                cached_embeddings.append(self.cache[content_hash])
            else:
                uncached_docs.append((doc, content_hash))
        
        # Generate embeddings for uncached documents
        if uncached_docs:
            texts = [doc.content for doc, _ in uncached_docs]
            
            request = Qwen3EmbedRequest(
                texts=texts,
                normalize=self.config.normalize_embeddings
            )
            
            response = await self.provider.embed(request)
            
            if response.success and response.embeddings:
                # Cache embeddings
                for (doc, content_hash), embedding in zip(uncached_docs, response.embeddings):
                    if self.config.cache_embeddings:
                        self.cache[content_hash] = embedding
                    cached_embeddings.append(embedding)
            else:
                raise Exception(f"Failed to generate embeddings: {response.error_message}")
        
        return cached_embeddings


# ============================================================================
# Main Ingestion Pipeline
# ============================================================================

class IngestionPipeline:
    """Main ingestion pipeline."""
    
    def __init__(
        self,
        vector_store: VectorStore,
        embedding_provider: Qwen3Provider,
        chunking_config: Optional[ChunkingConfig] = None,
        embedding_config: Optional[EmbeddingConfig] = None
    ):
        self.vector_store = vector_store
        self.embedding_provider = embedding_provider
        self.chunking_config = chunking_config or ChunkingConfig()
        self.embedding_config = embedding_config or EmbeddingConfig()
        
        # Initialize components
        self.chunking_engine = ChunkingEngine(self.chunking_config)
        self.embedding_generator = EmbeddingGenerator(self.embedding_provider, self.embedding_config)
        
        # Document processors
        self.processors = [
            TextProcessor(),
            PDFProcessor(),
            ImageProcessor(),
            URLProcessor()
        ]
        
        self.logger = logging.getLogger(__name__)
    
    async def ingest_job(self, job: IngestionJob) -> IngestionJob:
        """Process an ingestion job."""
        job.status = IngestionStatus.PROCESSING
        job.started_at = datetime.now(timezone.utc)
        
        try:
            # Process sources
            all_documents = []
            for source in job.sources:
                documents = await self._process_source(source)
                all_documents.extend(documents)
            
            job.total_documents = len(all_documents)
            job.progress = 0.1
            
            # Chunk documents
            job.status = IngestionStatus.CHUNKING
            chunked_documents = []
            for doc in all_documents:
                chunks = self.chunking_engine.chunk_document(doc)
                chunked_documents.extend(chunks)
            
            job.total_chunks = len(chunked_documents)
            job.progress = 0.3
            
            # Generate embeddings
            job.status = IngestionStatus.EMBEDDING
            embeddings = await self.embedding_generator.generate_embeddings(chunked_documents)
            
            job.progress = 0.7
            
            # Index documents
            job.status = IngestionStatus.INDEXING
            indexed_ids = await self.vector_store.index(chunked_documents, embeddings)
            
            job.successful_documents = len(indexed_ids)
            job.progress = 1.0
            job.status = IngestionStatus.COMPLETED
            job.completed_at = datetime.now(timezone.utc)
            
            self.logger.info(f"Ingestion job {job.job_id} completed successfully")
            
        except Exception as e:
            job.status = IngestionStatus.FAILED
            job.error_message = str(e)
            job.completed_at = datetime.now(timezone.utc)
            self.logger.error(f"Ingestion job {job.job_id} failed: {e}")
        
        return job
    
    async def _process_source(self, source: IngestionSource) -> List[Document]:
        """Process a single source."""
        # Find appropriate processor
        processor = None
        for p in self.processors:
            if await p.can_process(source):
                processor = p
                break
        
        if not processor:
            raise ValueError(f"No processor found for source type: {source.source_type}")
        
        # Process source
        documents = await processor.process(source)
        
        # Update document metadata
        for doc in documents:
            doc.metadata.update(source.metadata)
            doc.status = DocumentStatus.PENDING
        
        return documents
    
    async def ingest_sources(
        self,
        sources: List[IngestionSource],
        chunking_config: Optional[ChunkingConfig] = None,
        embedding_config: Optional[EmbeddingConfig] = None
    ) -> IngestionJob:
        """Ingest multiple sources."""
        # Create job
        job = IngestionJob(
            sources=sources,
            chunking_config=chunking_config or self.chunking_config,
            embedding_config=embedding_config or self.embedding_config
        )
        
        # Process job
        return await self.ingest_job(job)
    
    async def ingest_file(
        self,
        file_path: str,
        title: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> IngestionJob:
        """Ingest a single file."""
        source = IngestionSource(
            source_type="file",
            source_path=file_path,
            metadata={
                **(metadata or {}),
                'title': title or Path(file_path).name
            }
        )
        
        return await self.ingest_sources([source])
    
    async def ingest_text(
        self,
        content: str,
        title: str = "Text Document",
        metadata: Optional[Dict[str, Any]] = None
    ) -> IngestionJob:
        """Ingest text content."""
        source = IngestionSource(
            source_type="text",
            source_content=content,
            metadata={
                **(metadata or {}),
                'title': title
            }
        )
        
        return await self.ingest_sources([source])
    
    async def ingest_url(
        self,
        url: str,
        title: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> IngestionJob:
        """Ingest content from URL."""
        source = IngestionSource(
            source_type="url",
            source_path=url,
            metadata={
                **(metadata or {}),
                'title': title or f"URL: {urlparse(url).netloc}"
            }
        )
        
        return await self.ingest_sources([source])


# ============================================================================
# Factory Functions
# ============================================================================

def create_ingestion_pipeline(
    vector_store: VectorStore,
    embedding_provider: Qwen3Provider,
    chunk_size: int = 1000,
    chunk_overlap: int = 200,
    batch_size: int = 32
) -> IngestionPipeline:
    """Create an ingestion pipeline with default configuration."""
    chunking_config = ChunkingConfig(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )
    
    embedding_config = EmbeddingConfig(
        batch_size=batch_size
    )
    
    return IngestionPipeline(
        vector_store=vector_store,
        embedding_provider=embedding_provider,
        chunking_config=chunking_config,
        embedding_config=embedding_config
    )


# ============================================================================
# Export all classes and functions
# ============================================================================

__all__ = [
    # Enums
    "IngestionStatus",
    
    # Models
    "IngestionSource",
    "ChunkingConfig",
    "EmbeddingConfig",
    "IngestionJob",
    
    # Processors
    "DocumentProcessor",
    "TextProcessor",
    "PDFProcessor",
    "ImageProcessor",
    "URLProcessor",
    
    # Engines
    "ChunkingEngine",
    "EmbeddingGenerator",
    
    # Main pipeline
    "IngestionPipeline",
    
    # Factory functions
    "create_ingestion_pipeline",
]
