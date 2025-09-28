#!/usr/bin/env python3
"""
Input Schemas for Agentic LLM Core

This module implements the Pydantic schemas for all input types as specified in
milestone_1_core_pipeline.md Task 1.1.1: Design Pydantic Input Schemas

Complies with:
- System Specification: Agentic LLM Core v0.1 (specs/system.md)
- Milestone 1: Core Pipeline Foundation (tasks/milestone_1_core_pipeline.md)
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any, Union, List
from datetime import datetime
import re

class TextInput(BaseModel):
    """Text input schema with validation rules"""
    content: str = Field(..., max_length=10000, description="Text content to process")
    language: Optional[str] = Field(default="en", description="Language of the text")
    encoding: str = Field(default="utf-8", description="Text encoding")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional metadata")
    
    @validator('content')
    def validate_content(cls, v):
        if not v or not v.strip():
            raise ValueError("Content cannot be empty")
        return v.strip()
    
    @validator('language')
    def validate_language(cls, v):
        if v and not re.match(r'^[a-z]{2}(-[A-Z]{2})?$', v):
            raise ValueError("Language must be in ISO 639-1 format (e.g., 'en', 'en-US')")
        return v

class ImageInput(BaseModel):
    """Image input schema with size/format constraints"""
    data: bytes = Field(..., description="Image data as bytes")
    format: str = Field(..., pattern="^(jpg|jpeg|png|gif|webp)$", description="Image format")
    max_size: tuple[int, int] = Field(default=(2048, 2048), description="Maximum image dimensions")
    quality: int = Field(default=85, ge=1, le=100, description="Image quality (1-100)")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional metadata")
    
    @validator('data')
    def validate_data_size(cls, v):
        if len(v) > 10 * 1024 * 1024:  # 10MB limit
            raise ValueError("Image data too large (max 10MB)")
        return v
    
    @validator('format')
    def validate_format(cls, v):
        allowed_formats = ['jpg', 'jpeg', 'png', 'gif', 'webp']
        if v.lower() not in allowed_formats:
            raise ValueError(f"Format must be one of: {allowed_formats}")
        return v.lower()

class DocumentInput(BaseModel):
    """Document input schema with file type validation"""
    file_path: str = Field(..., description="Path to the document file")
    file_type: str = Field(..., pattern="^(pdf|docx|txt|md)$", description="Document type")
    max_size: int = Field(default=50 * 1024 * 1024, description="Maximum file size in bytes")
    encoding: str = Field(default="utf-8", description="Text encoding for text files")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional metadata")
    
    @validator('file_path')
    def validate_file_path(cls, v):
        if not v or not v.strip():
            raise ValueError("File path cannot be empty")
        return v.strip()
    
    @validator('file_type')
    def validate_file_type(cls, v):
        allowed_types = ['pdf', 'docx', 'txt', 'md']
        if v.lower() not in allowed_types:
            raise ValueError(f"File type must be one of: {allowed_types}")
        return v.lower()

class ProcessedInput(BaseModel):
    """Unified schema for processed inputs in the pipeline"""
    input_type: str = Field(..., pattern="^(text|image|document)$", description="Type of input")
    content: Union[str, bytes, dict] = Field(..., description="Processed content")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Processing metadata")
    timestamp: float = Field(default_factory=lambda: datetime.now().timestamp(), description="Processing timestamp")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0, description="Processing confidence score")
    
    @validator('input_type')
    def validate_input_type(cls, v):
        allowed_types = ['text', 'image', 'document']
        if v not in allowed_types:
            raise ValueError(f"Input type must be one of: {allowed_types}")
        return v
    
    @validator('content')
    def validate_content_not_empty(cls, v):
        if isinstance(v, str) and not v.strip():
            raise ValueError("Content cannot be empty")
        elif isinstance(v, bytes) and len(v) == 0:
            raise ValueError("Content cannot be empty")
        elif isinstance(v, dict) and not v:
            raise ValueError("Content cannot be empty")
        return v

class ValidationResult(BaseModel):
    """Result of input validation"""
    valid: bool = Field(..., description="Whether validation passed")
    errors: List[str] = Field(default_factory=list, description="Validation errors")
    warnings: List[str] = Field(default_factory=list, description="Validation warnings")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Validation metadata")

# Example usage and testing
if __name__ == "__main__":
    # Test text input
    try:
        text_input = TextInput(
            content="Hello, how are you?",
            language="en",
            metadata={"source": "test"}
        )
        print("✅ Text input validation passed")
        print(f"Content: {text_input.content}")
        print(f"Language: {text_input.language}")
    except Exception as e:
        print(f"❌ Text input validation failed: {e}")
    
    # Test image input
    try:
        image_data = b"fake_image_data"
        image_input = ImageInput(
            data=image_data,
            format="png",
            metadata={"source": "test"}
        )
        print("✅ Image input validation passed")
        print(f"Format: {image_input.format}")
        print(f"Data size: {len(image_input.data)} bytes")
    except Exception as e:
        print(f"❌ Image input validation failed: {e}")
    
    # Test document input
    try:
        doc_input = DocumentInput(
            file_path="/path/to/document.pdf",
            file_type="pdf",
            metadata={"source": "test"}
        )
        print("✅ Document input validation passed")
        print(f"File path: {doc_input.file_path}")
        print(f"File type: {doc_input.file_type}")
    except Exception as e:
        print(f"❌ Document input validation failed: {e}")
    
    # Test processed input
    try:
        processed = ProcessedInput(
            input_type="text",
            content="Processed text content",
            metadata={"original_type": "text", "processing_time": 0.1}
        )
        print("✅ Processed input validation passed")
        print(f"Input type: {processed.input_type}")
        print(f"Timestamp: {processed.timestamp}")
    except Exception as e:
        print(f"❌ Processed input validation failed: {e}")
    
    print("\n🎉 All input schema tests completed!")
