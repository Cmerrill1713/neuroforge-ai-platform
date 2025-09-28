#!/usr/bin/env python3
"""
Input Ingestion Service for Agentic LLM Core

This module implements the InputIngestionService as specified in
milestone_1_core_pipeline.md Task 1.1.2: Implement InputIngestionService Class

Complies with:
- System Specification: Agentic LLM Core v0.1 (specs/system.md)
- Milestone 1: Core Pipeline Foundation (tasks/milestone_1_core_pipeline.md)
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List
from pathlib import Path
from datetime import datetime
import time

from ..schemas.input_schemas import (
    TextInput,
    ImageInput,
    DocumentInput,
    ProcessedInput,
    ValidationResult
)

logger = logging.getLogger(__name__)

class InputValidator:
    """Input validation service"""
    
    async def validate_text_input(self, content: str, metadata: Dict[str, Any]) -> ValidationResult:
        """Validate text input"""
        try:
            text_input = TextInput(
                content=content,
                language=metadata.get("language", "en"),
                encoding=metadata.get("encoding", "utf-8"),
                metadata=metadata
            )
            return ValidationResult(valid=True, metadata={"validated_input": text_input})
        except Exception as e:
            return ValidationResult(valid=False, errors=[str(e)])
    
    async def validate_image_input(self, data: bytes, metadata: Dict[str, Any]) -> ValidationResult:
        """Validate image input"""
        try:
            image_input = ImageInput(
                data=data,
                format=metadata.get("format", "png"),
                max_size=metadata.get("max_size", (2048, 2048)),
                quality=metadata.get("quality", 85),
                metadata=metadata
            )
            return ValidationResult(valid=True, metadata={"validated_input": image_input})
        except Exception as e:
            return ValidationResult(valid=False, errors=[str(e)])
    
    async def validate_document_input(self, path: str, metadata: Dict[str, Any]) -> ValidationResult:
        """Validate document input"""
        try:
            # Check if file exists
            file_path = Path(path)
            if not file_path.exists():
                return ValidationResult(valid=False, errors=[f"File not found: {path}"])
            
            # Get file extension
            file_ext = file_path.suffix.lower().lstrip('.')
            
            document_input = DocumentInput(
                file_path=str(file_path),
                file_type=file_ext,
                max_size=metadata.get("max_size", 50 * 1024 * 1024),
                encoding=metadata.get("encoding", "utf-8"),
                metadata=metadata
            )
            return ValidationResult(valid=True, metadata={"validated_input": document_input})
        except Exception as e:
            return ValidationResult(valid=False, errors=[str(e)])

class InputIngestionService:
    """
    Core input ingestion service with async processing and validation
    
    Implements Task 1.1.2: Implement InputIngestionService Class
    
    Acceptance Criteria:
    - [ ] All input types processed asynchronously
    - [ ] Validation errors handled gracefully
    - [ ] Queue backpressure prevents memory issues
    - [ ] Performance < 1 second per input
    """
    
    def __init__(self, validator: InputValidator):
        self.validator = validator
        self.input_queue = asyncio.Queue(maxsize=100)
        self.processing_stats = {
            "total_processed": 0,
            "successful_processing": 0,
            "failed_processing": 0,
            "average_processing_time": 0.0
        }
        
    async def ingest_text(self, content: str, metadata: Optional[Dict[str, Any]] = None) -> ProcessedInput:
        """
        Ingest and process text input
        
        Args:
            content: Text content to process
            metadata: Optional metadata for the input
            
        Returns:
            ProcessedInput: Processed text input
        """
        if metadata is None:
            metadata = {}
        
        start_time = time.time()
        
        try:
            # Validate input
            validation_result = await self.validator.validate_text_input(content, metadata)
            
            if not validation_result.valid:
                raise ValueError(f"Text validation failed: {validation_result.errors}")
            
            validated_input = validation_result.metadata["validated_input"]
            
            # Process text input
            processed_input = await self._process_text(validated_input)
            
            # Update stats
            processing_time = time.time() - start_time
            self._update_stats(True, processing_time)
            
            logger.info(f"Text input processed in {processing_time:.3f}s")
            return processed_input
            
        except Exception as e:
            processing_time = time.time() - start_time
            self._update_stats(False, processing_time)
            logger.error(f"Text ingestion failed: {e}")
            raise
    
    async def ingest_image(self, data: bytes, metadata: Optional[Dict[str, Any]] = None) -> ProcessedInput:
        """
        Ingest and process image input
        
        Args:
            data: Image data as bytes
            metadata: Optional metadata for the input
            
        Returns:
            ProcessedInput: Processed image input
        """
        if metadata is None:
            metadata = {}
        
        start_time = time.time()
        
        try:
            # Validate input
            validation_result = await self.validator.validate_image_input(data, metadata)
            
            if not validation_result.valid:
                raise ValueError(f"Image validation failed: {validation_result.errors}")
            
            validated_input = validation_result.metadata["validated_input"]
            
            # Process image input
            processed_input = await self._process_image(validated_input)
            
            # Update stats
            processing_time = time.time() - start_time
            self._update_stats(True, processing_time)
            
            logger.info(f"Image input processed in {processing_time:.3f}s")
            return processed_input
            
        except Exception as e:
            processing_time = time.time() - start_time
            self._update_stats(False, processing_time)
            logger.error(f"Image ingestion failed: {e}")
            raise
    
    async def ingest_document(self, path: str, metadata: Optional[Dict[str, Any]] = None) -> ProcessedInput:
        """
        Ingest and process document input
        
        Args:
            path: Path to the document file
            metadata: Optional metadata for the input
            
        Returns:
            ProcessedInput: Processed document input
        """
        if metadata is None:
            metadata = {}
        
        start_time = time.time()
        
        try:
            # Validate input
            validation_result = await self.validator.validate_document_input(path, metadata)
            
            if not validation_result.valid:
                raise ValueError(f"Document validation failed: {validation_result.errors}")
            
            validated_input = validation_result.metadata["validated_input"]
            
            # Process document input
            processed_input = await self._process_document(validated_input)
            
            # Update stats
            processing_time = time.time() - start_time
            self._update_stats(True, processing_time)
            
            logger.info(f"Document input processed in {processing_time:.3f}s")
            return processed_input
            
        except Exception as e:
            processing_time = time.time() - start_time
            self._update_stats(False, processing_time)
            logger.error(f"Document ingestion failed: {e}")
            raise
    
    async def _process_text(self, text_input: TextInput) -> ProcessedInput:
        """Process text input"""
        # Basic text processing (to be enhanced with actual processing)
        processed_content = text_input.content
        
        # Add processing metadata
        processing_metadata = {
            "original_length": len(text_input.content),
            "language": text_input.language,
            "encoding": text_input.encoding,
            "processing_steps": ["validation", "normalization"],
            "timestamp": datetime.now().isoformat()
        }
        
        return ProcessedInput(
            input_type="text",
            content=processed_content,
            metadata=processing_metadata,
            timestamp=time.time(),
            confidence=1.0
        )
    
    async def _process_image(self, image_input: ImageInput) -> ProcessedInput:
        """Process image input"""
        # Basic image processing (to be enhanced with actual processing)
        # For now, we'll store the image data as-is
        
        # Add processing metadata
        processing_metadata = {
            "original_size": len(image_input.data),
            "format": image_input.format,
            "max_size": image_input.max_size,
            "quality": image_input.quality,
            "processing_steps": ["validation", "format_check"],
            "timestamp": datetime.now().isoformat()
        }
        
        return ProcessedInput(
            input_type="image",
            content=image_input.data,
            metadata=processing_metadata,
            timestamp=time.time(),
            confidence=1.0
        )
    
    async def _process_document(self, document_input: DocumentInput) -> ProcessedInput:
        """Process document input"""
        # Basic document processing (to be enhanced with actual processing)
        # For now, we'll read the file path and type
        
        # Add processing metadata
        processing_metadata = {
            "file_path": document_input.file_path,
            "file_type": document_input.file_type,
            "file_size": Path(document_input.file_path).stat().st_size,
            "encoding": document_input.encoding,
            "processing_steps": ["validation", "path_check"],
            "timestamp": datetime.now().isoformat()
        }
        
        return ProcessedInput(
            input_type="document",
            content={"file_path": document_input.file_path, "file_type": document_input.file_type},
            metadata=processing_metadata,
            timestamp=time.time(),
            confidence=1.0
        )
    
    def _update_stats(self, success: bool, processing_time: float):
        """Update processing statistics"""
        self.processing_stats["total_processed"] += 1
        
        if success:
            self.processing_stats["successful_processing"] += 1
        else:
            self.processing_stats["failed_processing"] += 1
        
        # Update average processing time
        total = self.processing_stats["total_processed"]
        current_avg = self.processing_stats["average_processing_time"]
        self.processing_stats["average_processing_time"] = (
            (current_avg * (total - 1) + processing_time) / total
        )
    
    def get_stats(self) -> Dict[str, Any]:
        """Get processing statistics"""
        return self.processing_stats.copy()
    
    def get_queue_status(self) -> Dict[str, Any]:
        """Get input queue status"""
        return {
            "queue_size": self.input_queue.qsize(),
            "max_size": self.input_queue.maxsize,
            "is_full": self.input_queue.full(),
            "is_empty": self.input_queue.empty()
        }

# Example usage and testing
async def main():
    """Example usage of InputIngestionService"""
    logger.info("🚀 Testing Input Ingestion Service")
    logger.info("=" * 50)
    
    validator = InputValidator()
    service = InputIngestionService(validator)
    
    try:
        # Test text ingestion
        logger.info("Testing text ingestion...")
        text_input = await service.ingest_text(
            "Hello, how are you today?",
            {"source": "test", "language": "en"}
        )
        logger.info(f"✅ Text processed: {text_input.input_type}")
        logger.info(f"Content: {text_input.content[:50]}...")
        
        # Test image ingestion
        logger.info("Testing image ingestion...")
        image_data = b"fake_image_data_for_testing"
        image_input = await service.ingest_image(
            image_data,
            {"source": "test", "format": "png"}
        )
        logger.info(f"✅ Image processed: {image_input.input_type}")
        logger.info(f"Data size: {len(image_input.content)} bytes")
        
        # Test document ingestion
        logger.info("Testing document ingestion...")
        # Create a temporary file for testing
        test_file = Path("test_document.txt")
        test_file.write_text("This is a test document.")
        
        try:
            doc_input = await service.ingest_document(
                str(test_file),
                {"source": "test"}
            )
            logger.info(f"✅ Document processed: {doc_input.input_type}")
            logger.info(f"File path: {doc_input.metadata['file_path']}")
        finally:
            # Clean up test file
            if test_file.exists():
                test_file.unlink()
        
        # Get statistics
        stats = service.get_stats()
        logger.info(f"Processing stats: {stats}")
        
        queue_status = service.get_queue_status()
        logger.info(f"Queue status: {queue_status}")
        
        logger.info("🎉 Input ingestion service test completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Input ingestion service test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    asyncio.run(main())
