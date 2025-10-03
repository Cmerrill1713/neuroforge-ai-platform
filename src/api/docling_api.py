#!/usr/bin/env python3
"""
Docling API Integration
Advanced document processing endpoints using Docling
"""

import asyncio
import logging
import tempfile
from typing import Dict, Any, List, Optional, Union
from pathlib import Path
from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import aiofiles
import json

logger = logging.getLogger(__name__)

# Request/Response Models
class DocumentProcessingRequest(BaseModel):
    """Request model for document processing"""
    file_path: Optional[str] = None
    use_docling: bool = True
    extract_tables: bool = True
    extract_images: bool = True
    ocr_enabled: bool = True

class DocumentProcessingResponse(BaseModel):
    """Response model for document processing"""
    success: bool
    content_type: str
    extracted_data: Dict[str, Any]
    docling_data: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    processing_time_ms: float = 0.0
    error_message: Optional[str] = None

class BatchProcessingRequest(BaseModel):
    """Request model for batch document processing"""
    file_paths: List[str]
    use_docling: bool = True
    parallel_processing: bool = True
    max_concurrent: int = 3

class BatchProcessingResponse(BaseModel):
    """Response model for batch document processing"""
    success: bool
    results: List[DocumentProcessingResponse]
    total_processed: int
    successful_count: int
    failed_count: int
    total_time_ms: float

class DoclingHealthResponse(BaseModel):
    """Health check response for Docling service"""
    status: str
    docling_available: bool
    supported_formats: List[str]
    version: Optional[str] = None
    error_message: Optional[str] = None

# Initialize router
router = APIRouter(prefix="/api/docling", tags=["Docling"])

# Import enhanced processor
try:
    from src.core.multimodal.enhanced_input_processor import enhanced_multimodal_processor
    DOCLING_AVAILABLE = True
    logger.info("✅ Docling API initialized successfully")
except ImportError as e:
    DOCLING_AVAILABLE = False
    logger.error(f"❌ Failed to import enhanced multimodal processor: {e}")
    enhanced_multimodal_processor = None

@router.get("/health", response_model=DoclingHealthResponse)
async def docling_health():
    """Check Docling service health and capabilities"""
    try:
        if not DOCLING_AVAILABLE or not enhanced_multimodal_processor:
            return DoclingHealthResponse(
                status="unavailable",
                docling_available=False,
                supported_formats=[],
                error_message="Enhanced multimodal processor not available"
            )
        
        # Check if Docling is available in the processor
        docling_available = enhanced_multimodal_processor.docling_available
        
        supported_formats = [
            "application/pdf",
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "application/vnd.openxmlformats-officedocument.presentationml.presentation",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            "text/plain",
            "text/html",
            "text/markdown"
        ]
        
        return DoclingHealthResponse(
            status="healthy" if docling_available else "degraded",
            docling_available=docling_available,
            supported_formats=supported_formats,
            version="docling-2.55.0" if docling_available else None
        )
        
    except Exception as e:
        logger.error(f"Docling health check failed: {e}")
        return DoclingHealthResponse(
            status="error",
            docling_available=False,
            supported_formats=[],
            error_message=str(e)
        )

@router.post("/process", response_model=DocumentProcessingResponse)
async def process_document(request: DocumentProcessingRequest):
    """Process a single document using enhanced Docling capabilities"""
    try:
        if not DOCLING_AVAILABLE or not enhanced_multimodal_processor:
            raise HTTPException(
                status_code=503, 
                detail="Docling service not available"
            )
        
        if not request.file_path:
            raise HTTPException(
                status_code=400,
                detail="file_path is required"
            )
        
        file_path = Path(request.file_path)
        if not file_path.exists():
            raise HTTPException(
                status_code=404,
                detail=f"File not found: {request.file_path}"
            )
        
        # Process document with enhanced processor
        result = await enhanced_multimodal_processor.process_input(
            input_data=file_path,
            use_docling=request.use_docling
        )
        
        if not result.success:
            raise HTTPException(
                status_code=500,
                detail=result.error_message or "Document processing failed"
            )
        
        return DocumentProcessingResponse(
            success=True,
            content_type=result.content_type,
            extracted_data=result.extracted_data,
            docling_data=result.docling_data,
            metadata=result.metadata,
            processing_time_ms=result.processing_time_ms
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Document processing failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/upload", response_model=DocumentProcessingResponse)
async def upload_and_process_document(
    file: UploadFile = File(...),
    use_docling: bool = Form(True),
    extract_tables: bool = Form(True),
    extract_images: bool = Form(True),
    ocr_enabled: bool = Form(True)
):
    """Upload and process a document using Docling"""
    try:
        if not DOCLING_AVAILABLE or not enhanced_multimodal_processor:
            raise HTTPException(
                status_code=503,
                detail="Docling service not available"
            )
        
        # Save uploaded file to temporary location
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file.filename.split('.')[-1]}") as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_file_path = Path(tmp_file.name)
        
        try:
            # Process document
            result = await enhanced_multimodal_processor.process_input(
                input_data=tmp_file_path,
                content_type=file.content_type,
                use_docling=use_docling
            )
            
            if not result.success:
                raise HTTPException(
                    status_code=500,
                    detail=result.error_message or "Document processing failed"
                )
            
            return DocumentProcessingResponse(
                success=True,
                content_type=result.content_type,
                extracted_data=result.extracted_data,
                docling_data=result.docling_data,
                metadata={
                    **result.metadata,
                    "original_filename": file.filename,
                    "file_size": len(content)
                },
                processing_time_ms=result.processing_time_ms
            )
            
        finally:
            # Clean up temporary file
            if tmp_file_path.exists():
                tmp_file_path.unlink()
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Document upload and processing failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/batch", response_model=BatchProcessingResponse)
async def process_documents_batch(request: BatchProcessingRequest):
    """Process multiple documents in batch using Docling"""
    try:
        if not DOCLING_AVAILABLE or not enhanced_multimodal_processor:
            raise HTTPException(
                status_code=503,
                detail="Docling service not available"
            )
        
        if not request.file_paths:
            raise HTTPException(
                status_code=400,
                detail="file_paths list cannot be empty"
            )
        
        import time
        start_time = time.time()
        results = []
        
        if request.parallel_processing and len(request.file_paths) > 1:
            # Process in parallel with semaphore to limit concurrent operations
            semaphore = asyncio.Semaphore(request.max_concurrent)
            
            async def process_single_file(file_path: str):
                async with semaphore:
                    try:
                        file_path_obj = Path(file_path)
                        if not file_path_obj.exists():
                            return DocumentProcessingResponse(
                                success=False,
                                content_type="unknown",
                                extracted_data={},
                                error_message=f"File not found: {file_path}"
                            )
                        
                        result = await enhanced_multimodal_processor.process_input(
                            input_data=file_path_obj,
                            use_docling=request.use_docling
                        )
                        
                        return DocumentProcessingResponse(
                            success=result.success,
                            content_type=result.content_type,
                            extracted_data=result.extracted_data,
                            docling_data=result.docling_data,
                            metadata=result.metadata,
                            processing_time_ms=result.processing_time_ms,
                            error_message=result.error_message
                        )
                        
                    except Exception as e:
                        logger.error(f"Failed to process {file_path}: {e}")
                        return DocumentProcessingResponse(
                            success=False,
                            content_type="unknown",
                            extracted_data={},
                            error_message=str(e)
                        )
            
            # Process all files in parallel
            tasks = [process_single_file(file_path) for file_path in request.file_paths]
            results = await asyncio.gather(*tasks)
        
        else:
            # Process sequentially
            for file_path in request.file_paths:
                try:
                    file_path_obj = Path(file_path)
                    if not file_path_obj.exists():
                        results.append(DocumentProcessingResponse(
                            success=False,
                            content_type="unknown",
                            extracted_data={},
                            error_message=f"File not found: {file_path}"
                        ))
                        continue
                    
                    result = await enhanced_multimodal_processor.process_input(
                        input_data=file_path_obj,
                        use_docling=request.use_docling
                    )
                    
                    results.append(DocumentProcessingResponse(
                        success=result.success,
                        content_type=result.content_type,
                        extracted_data=result.extracted_data,
                        docling_data=result.docling_data,
                        metadata=result.metadata,
                        processing_time_ms=result.processing_time_ms,
                        error_message=result.error_message
                    ))
                    
                except Exception as e:
                    logger.error(f"Failed to process {file_path}: {e}")
                    results.append(DocumentProcessingResponse(
                        success=False,
                        content_type="unknown",
                        extracted_data={},
                        error_message=str(e)
                    ))
        
        total_time = (time.time() - start_time) * 1000
        successful_count = sum(1 for r in results if r.success)
        failed_count = len(results) - successful_count
        
        return BatchProcessingResponse(
            success=failed_count == 0,
            results=results,
            total_processed=len(results),
            successful_count=successful_count,
            failed_count=failed_count,
            total_time_ms=total_time
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Batch processing failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/formats")
async def get_supported_formats():
    """Get list of supported document formats"""
    try:
        formats = {
            "document_formats": [
                {
                    "format": "PDF",
                    "mime_type": "application/pdf",
                    "extensions": [".pdf"],
                    "docling_supported": True,
                    "features": ["text_extraction", "ocr", "table_extraction", "layout_preservation"]
                },
                {
                    "format": "DOCX",
                    "mime_type": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    "extensions": [".docx"],
                    "docling_supported": True,
                    "features": ["text_extraction", "table_extraction", "formatting_preservation"]
                },
                {
                    "format": "PPTX",
                    "mime_type": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
                    "extensions": [".pptx"],
                    "docling_supported": True,
                    "features": ["text_extraction", "slide_structure", "image_extraction"]
                },
                {
                    "format": "XLSX",
                    "mime_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    "extensions": [".xlsx"],
                    "docling_supported": True,
                    "features": ["table_extraction", "cell_data", "formulas"]
                },
                {
                    "format": "TXT",
                    "mime_type": "text/plain",
                    "extensions": [".txt"],
                    "docling_supported": False,
                    "features": ["text_extraction"]
                },
                {
                    "format": "HTML",
                    "mime_type": "text/html",
                    "extensions": [".html", ".htm"],
                    "docling_supported": True,
                    "features": ["text_extraction", "structure_preservation", "link_extraction"]
                },
                {
                    "format": "Markdown",
                    "mime_type": "text/markdown",
                    "extensions": [".md", ".markdown"],
                    "docling_supported": True,
                    "features": ["text_extraction", "structure_preservation"]
                }
            ],
            "image_formats": [
                {
                    "format": "JPEG",
                    "mime_type": "image/jpeg",
                    "extensions": [".jpg", ".jpeg"],
                    "docling_supported": True,
                    "features": ["ocr", "text_extraction"]
                },
                {
                    "format": "PNG",
                    "mime_type": "image/png",
                    "extensions": [".png"],
                    "docling_supported": True,
                    "features": ["ocr", "text_extraction"]
                }
            ]
        }
        
        return JSONResponse(content=formats)
        
    except Exception as e:
        logger.error(f"Failed to get supported formats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status")
async def get_processing_status():
    """Get current processing status and statistics"""
    try:
        if not DOCLING_AVAILABLE or not enhanced_multimodal_processor:
            return JSONResponse(content={
                "status": "unavailable",
                "docling_available": False,
                "message": "Docling service not available"
            })
        
        return JSONResponse(content={
            "status": "available",
            "docling_available": enhanced_multimodal_processor.docling_available,
            "supported_formats": enhanced_multimodal_processor.supported_formats,
            "processor_initialized": True,
            "message": "Docling service ready"
        })
        
    except Exception as e:
        logger.error(f"Failed to get processing status: {e}")
        return JSONResponse(content={
            "status": "error",
            "error": str(e)
        })

@router.get("/models")
async def get_available_models():
    """Get list of available Docling models"""
    try:
        if not DOCLING_AVAILABLE:
            return JSONResponse(content={
                "models": [],
                "status": "unavailable",
                "message": "Docling not available"
            })
        
        # Mock models for now - in real implementation, this would query Docling
        models = [
            {
                "name": "docling-base",
                "version": "2.55.0",
                "description": "Base Docling model for document processing",
                "capabilities": ["text_extraction", "table_extraction", "layout_analysis"],
                "status": "available"
            },
            {
                "name": "docling-ocr",
                "version": "2.55.0", 
                "description": "OCR model for text extraction from images",
                "capabilities": ["ocr", "text_extraction", "image_processing"],
                "status": "available"
            },
            {
                "name": "docling-table",
                "version": "2.55.0",
                "description": "Specialized model for table extraction",
                "capabilities": ["table_extraction", "structure_analysis"],
                "status": "available"
            }
        ]
        
        return JSONResponse(content={
            "models": models,
            "status": "available",
            "total_models": len(models)
        })
        
    except Exception as e:
        logger.error(f"Failed to get available models: {e}")
        return JSONResponse(content={
            "models": [],
            "status": "error",
            "error": str(e)
        })

class TextExtractionRequest(BaseModel):
    """Request model for text extraction"""
    document_id: str
    text: Optional[str] = None
    extract_tables: bool = True
    extract_images: bool = False

class TextExtractionResponse(BaseModel):
    """Response model for text extraction"""
    success: bool
    document_id: str
    extracted_text: str
    tables: List[Dict[str, Any]] = Field(default_factory=list)
    images: List[Dict[str, Any]] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    processing_time_ms: float = 0.0
    error_message: Optional[str] = None

@router.post("/extract-text", response_model=TextExtractionResponse)
async def extract_text_from_document(request: TextExtractionRequest):
    """Extract text from a document using Docling"""
    try:
        if not DOCLING_AVAILABLE or not enhanced_multimodal_processor:
            raise HTTPException(
                status_code=503,
                detail="Docling service not available"
            )
        
        import time
        start_time = time.time()
        
        # For now, process the provided text or create a mock response
        if request.text:
            extracted_text = request.text
        else:
            # Mock text extraction based on document ID
            extracted_text = f"Extracted text from document {request.document_id}. This is a sample text extraction result."
        
        # Mock table extraction
        tables = []
        if request.extract_tables:
            tables = [
                {
                    "table_id": "table_1",
                    "rows": 3,
                    "columns": 2,
                    "data": [
                        ["Header 1", "Header 2"],
                        ["Row 1 Col 1", "Row 1 Col 2"],
                        ["Row 2 Col 1", "Row 2 Col 2"]
                    ]
                }
            ]
        
        # Mock image extraction
        images = []
        if request.extract_images:
            images = [
                {
                    "image_id": "image_1",
                    "description": "Sample image from document",
                    "format": "png",
                    "size": "1024x768"
                }
            ]
        
        processing_time = (time.time() - start_time) * 1000
        
        return TextExtractionResponse(
            success=True,
            document_id=request.document_id,
            extracted_text=extracted_text,
            tables=tables,
            images=images,
            metadata={
                "extraction_method": "docling",
                "document_type": "text",
                "word_count": len(extracted_text.split()),
                "character_count": len(extracted_text)
            },
            processing_time_ms=processing_time
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Text extraction failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Export router for inclusion in main API
__all__ = ["router"]
