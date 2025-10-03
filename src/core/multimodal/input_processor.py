#!/usr/bin/env python3
"""
Multimodal Input Processing System
Handle images, documents, audio, and other media types for AI processing
"""

import asyncio
import base64
import json
import logging
import mimetypes
import tempfile
from typing import Dict, Any, List, Optional, Union, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
import io
import hashlib

logger = logging.getLogger(__name__)

@dataclass
class ProcessingResult:
    """Result of multimodal input processing"""
    success: bool
    content_type: str
    extracted_data: Dict[str, Any]
    metadata: Dict[str, Any] = field(default_factory=dict)
    processing_time_ms: float = 0.0
    error_message: Optional[str] = None
    file_hash: Optional[str] = None

@dataclass
class ImageData:
    """Processed image data"""
    width: int
    height: int
    format: str
    size_bytes: int
    base64_data: str
    extracted_text: Optional[str] = None
    objects: List[Dict[str, Any]] = field(default_factory=list)
    faces: List[Dict[str, Any]] = field(default_factory=list)
    colors: List[Dict[str, Any]] = field(default_factory=list)

@dataclass
class DocumentData:
    """Processed document data"""
    title: Optional[str] = None
    content: str = ""
    pages: int = 0
    word_count: int = 0
    language: Optional[str] = None
    keywords: List[str] = field(default_factory=list)
    summary: Optional[str] = None
    structure: Dict[str, Any] = field(default_factory=dict)

@dataclass
class AudioData:
    """Processed audio data"""
    duration_seconds: float = 0.0
    sample_rate: int = 0
    channels: int = 0
    format: str = ""
    transcription: Optional[str] = None
    language: Optional[str] = None
    speakers: List[Dict[str, Any]] = field(default_factory=list)

class MultimodalInputProcessor:
    """Process multimodal inputs including images, documents, and audio"""
    
    def __init__(self):
        self.supported_formats = {
            "image": ["jpg", "jpeg", "png", "gif", "bmp", "webp", "tiff"],
            "document": ["pdf", "docx", "txt", "md", "rtf", "odt"],
            "audio": ["mp3", "wav", "flac", "aac", "ogg", "m4a"],
            "video": ["mp4", "avi", "mov", "mkv", "webm"],
            "data": ["json", "csv", "xml", "yaml", "yml"]
        }
        
        self.processors = {
            "image": self._process_image,
            "document": self._process_document,
            "audio": self._process_audio,
            "video": self._process_video,
            "data": self._process_data
        }
        
        logger.info("🎭 Multimodal Input Processor initialized")
    
    async def process_input(
        self,
        input_data: Union[str, bytes, Path],
        content_type: Optional[str] = None
    ) -> ProcessingResult:
        """Process multimodal input and extract information"""
        start_time = datetime.now()
        
        try:
            # Determine content type
            if content_type is None:
                content_type = self._detect_content_type(input_data)
            
            # Get file hash for caching
            file_hash = self._calculate_hash(input_data)
            
            # Determine processor type
            processor_type = self._get_processor_type(content_type)
            
            if processor_type not in self.processors:
                raise ValueError(f"Unsupported content type: {content_type}")
            
            # Process the input
            extracted_data = await self.processors[processor_type](input_data, content_type)
            
            # Create metadata
            metadata = {
                "content_type": content_type,
                "processor_type": processor_type,
                "file_size": len(input_data) if isinstance(input_data, bytes) else 0,
                "timestamp": datetime.now().isoformat()
            }
            
            processing_time = (datetime.now() - start_time).total_seconds() * 1000
            
            return ProcessingResult(
                success=True,
                content_type=content_type,
                extracted_data=extracted_data,
                metadata=metadata,
                processing_time_ms=processing_time,
                file_hash=file_hash
            )
            
        except Exception as e:
            processing_time = (datetime.now() - start_time).total_seconds() * 1000
            logger.error(f"❌ Input processing failed: {e}")
            
            return ProcessingResult(
                success=False,
                content_type=content_type or "unknown",
                extracted_data={},
                metadata={},
                processing_time_ms=processing_time,
                error_message=str(e)
            )
    
    def _detect_content_type(self, input_data: Union[str, bytes, Path]) -> str:
        """Detect content type from input data"""
        if isinstance(input_data, Path):
            mime_type, _ = mimetypes.guess_type(str(input_data))
            return mime_type or "application/octet-stream"
        
        elif isinstance(input_data, str):
            # Check if it's a file path
            if Path(input_data).exists():
                mime_type, _ = mimetypes.guess_type(input_data)
                return mime_type or "text/plain"
            else:
                return "text/plain"
        
        elif isinstance(input_data, bytes):
            # Try to detect from magic bytes
            return self._detect_from_bytes(input_data)
        
        return "application/octet-stream"
    
    def _detect_from_bytes(self, data: bytes) -> str:
        """Detect content type from byte signature"""
        if len(data) < 4:
            return "application/octet-stream"
        
        # Common file signatures
        signatures = {
            b'\xFF\xD8\xFF': 'image/jpeg',
            b'\x89PNG': 'image/png',
            b'GIF8': 'image/gif',
            b'BM': 'image/bmp',
            b'%PDF': 'application/pdf',
            b'PK\x03\x04': 'application/zip',  # Could be docx, etc.
            b'ID3': 'audio/mpeg',
            b'OggS': 'audio/ogg',
            b'RIFF': 'audio/wav',
            b'fLaC': 'audio/flac'
        }
        
        for signature, mime_type in signatures.items():
            if data.startswith(signature):
                return mime_type
        
        # Check if it's text
        try:
            data.decode('utf-8')
            return 'text/plain'
        except UnicodeDecodeError:
            pass
        
        return "application/octet-stream"
    
    def _get_processor_type(self, content_type: str) -> str:
        """Get processor type from content type"""
        if content_type.startswith('image/'):
            return "image"
        elif content_type.startswith('audio/'):
            return "audio"
        elif content_type.startswith('video/'):
            return "video"
        elif content_type in ['application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document']:
            return "document"
        elif content_type.startswith('text/'):
            return "document"
        elif content_type in ['application/json', 'text/csv', 'application/xml']:
            return "data"
        else:
            return "document"  # Default fallback
    
    def _calculate_hash(self, input_data: Union[str, bytes, Path]) -> str:
        """Calculate hash of input data"""
        if isinstance(input_data, Path):
            with open(input_data, 'rb') as f:
                data = f.read()
        elif isinstance(input_data, str):
            data = input_data.encode('utf-8')
        else:
            data = input_data
        
        return hashlib.md5(data).hexdigest()
    
    async def _process_image(self, input_data: Union[str, bytes, Path], content_type: str) -> Dict[str, Any]:
        """Process image input"""
        try:
            # Convert to bytes if needed
            if isinstance(input_data, (str, Path)):
                if Path(input_data).exists():
                    with open(input_data, 'rb') as f:
                        image_data = f.read()
                else:
                    # Assume it's base64 encoded
                    image_data = base64.b64decode(input_data)
            else:
                image_data = input_data
            
            # Create base64 representation
            base64_data = base64.b64encode(image_data).decode('utf-8')
            
            # Extract image metadata
            image_info = await self._extract_image_metadata(image_data)
            
            # Extract text from image (OCR)
            extracted_text = await self._extract_text_from_image(image_data)
            
            # Detect objects in image
            objects = await self._detect_objects_in_image(image_data)
            
            # Detect faces in image
            faces = await self._detect_faces_in_image(image_data)
            
            # Extract dominant colors
            colors = await self._extract_colors_from_image(image_data)
            
            return {
                "type": "image",
                "width": image_info.get("width", 0),
                "height": image_info.get("height", 0),
                "format": image_info.get("format", "unknown"),
                "size_bytes": len(image_data),
                "base64_data": base64_data,
                "extracted_text": extracted_text,
                "objects": objects,
                "faces": faces,
                "colors": colors
            }
            
        except Exception as e:
            logger.error(f"Image processing failed: {e}")
            return {"type": "image", "error": str(e)}
    
    async def _process_document(self, input_data: Union[str, bytes, Path], content_type: str) -> Dict[str, Any]:
        """Process document input"""
        try:
            # Convert to text content
            if isinstance(input_data, Path) and input_data.exists():
                if content_type == 'application/pdf':
                    content = await self._extract_pdf_content(input_data)
                elif content_type in ['application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document']:
                    content = await self._extract_docx_content(input_data)
                else:
                    with open(input_data, 'r', encoding='utf-8') as f:
                        content = f.read()
            elif isinstance(input_data, str):
                content = input_data
            else:
                content = input_data.decode('utf-8')
            
            # Analyze document
            analysis = await self._analyze_document_content(content)
            
            return {
                "type": "document",
                "title": analysis.get("title"),
                "content": content,
                "pages": analysis.get("pages", 1),
                "word_count": analysis.get("word_count", 0),
                "language": analysis.get("language"),
                "keywords": analysis.get("keywords", []),
                "summary": analysis.get("summary"),
                "structure": analysis.get("structure", {})
            }
            
        except Exception as e:
            logger.error(f"Document processing failed: {e}")
            return {"type": "document", "error": str(e)}
    
    async def _process_audio(self, input_data: Union[str, bytes, Path], content_type: str) -> Dict[str, Any]:
        """Process audio input"""
        try:
            # Convert to bytes if needed
            if isinstance(input_data, Path):
                with open(input_data, 'rb') as f:
                    audio_data = f.read()
            elif isinstance(input_data, str):
                audio_data = base64.b64decode(input_data)
            else:
                audio_data = input_data
            
            # Extract audio metadata
            audio_info = await self._extract_audio_metadata(audio_data)
            
            # Transcribe audio
            transcription = await self._transcribe_audio(audio_data)
            
            # Detect speakers
            speakers = await self._detect_speakers(audio_data)
            
            return {
                "type": "audio",
                "duration_seconds": audio_info.get("duration", 0.0),
                "sample_rate": audio_info.get("sample_rate", 0),
                "channels": audio_info.get("channels", 0),
                "format": audio_info.get("format", "unknown"),
                "transcription": transcription,
                "language": audio_info.get("language"),
                "speakers": speakers
            }
            
        except Exception as e:
            logger.error(f"Audio processing failed: {e}")
            return {"type": "audio", "error": str(e)}
    
    async def _process_video(self, input_data: Union[str, bytes, Path], content_type: str) -> Dict[str, Any]:
        """Process video input"""
        try:
            # For now, extract basic metadata
            if isinstance(input_data, Path):
                file_size = input_data.stat().st_size
            elif isinstance(input_data, bytes):
                file_size = len(input_data)
            else:
                file_size = 0
            
            return {
                "type": "video",
                "content_type": content_type,
                "file_size": file_size,
                "note": "Video processing not fully implemented"
            }
            
        except Exception as e:
            logger.error(f"Video processing failed: {e}")
            return {"type": "video", "error": str(e)}
    
    async def _process_data(self, input_data: Union[str, bytes, Path], content_type: str) -> Dict[str, Any]:
        """Process structured data input"""
        try:
            # Convert to string
            if isinstance(input_data, Path):
                with open(input_data, 'r', encoding='utf-8') as f:
                    data_str = f.read()
            elif isinstance(input_data, bytes):
                data_str = input_data.decode('utf-8')
            else:
                data_str = input_data
            
            # Parse based on content type
            if content_type == 'application/json':
                parsed_data = json.loads(data_str)
            elif content_type == 'text/csv':
                parsed_data = await self._parse_csv(data_str)
            elif content_type in ['application/xml', 'text/xml']:
                parsed_data = await self._parse_xml(data_str)
            elif content_type in ['application/yaml', 'text/yaml']:
                parsed_data = await self._parse_yaml(data_str)
            else:
                parsed_data = {"raw": data_str}
            
            return {
                "type": "data",
                "content_type": content_type,
                "parsed_data": parsed_data,
                "size": len(data_str)
            }
            
        except Exception as e:
            logger.error(f"Data processing failed: {e}")
            return {"type": "data", "error": str(e)}
    
    # Helper methods for specific processing tasks
    async def _extract_image_metadata(self, image_data: bytes) -> Dict[str, Any]:
        """Extract metadata from image"""
        try:
            from PIL import Image
            import io
            
            image = Image.open(io.BytesIO(image_data))
            
            return {
                "width": image.width,
                "height": image.height,
                "format": image.format,
                "mode": image.mode
            }
        except ImportError:
            logger.warning("PIL not available for image processing")
            return {"width": 0, "height": 0, "format": "unknown"}
        except Exception as e:
            logger.warning(f"Image metadata extraction failed: {e}")
            return {"width": 0, "height": 0, "format": "unknown"}
    
    async def _extract_text_from_image(self, image_data: bytes) -> Optional[str]:
        """Extract text from image using OCR"""
        try:
            import pytesseract
            from PIL import Image
            import io
            
            image = Image.open(io.BytesIO(image_data))
            text = pytesseract.image_to_string(image)
            
            return text.strip() if text.strip() else None
            
        except ImportError:
            logger.warning("pytesseract not available for OCR")
            return None
        except Exception as e:
            logger.warning(f"OCR failed: {e}")
            return None
    
    async def _detect_objects_in_image(self, image_data: bytes) -> List[Dict[str, Any]]:
        """Detect objects in image"""
        # Mock implementation - replace with actual object detection
        return [
            {"class": "person", "confidence": 0.95, "bbox": [100, 100, 200, 300]},
            {"class": "car", "confidence": 0.87, "bbox": [300, 150, 500, 250]}
        ]
    
    async def _detect_faces_in_image(self, image_data: bytes) -> List[Dict[str, Any]]:
        """Detect faces in image"""
        # Mock implementation - replace with actual face detection
        return [
            {"confidence": 0.92, "bbox": [120, 110, 180, 170], "age": 25, "gender": "female"}
        ]
    
    async def _extract_colors_from_image(self, image_data: bytes) -> List[Dict[str, Any]]:
        """Extract dominant colors from image"""
        try:
            from PIL import Image
            import io
            
            image = Image.open(io.BytesIO(image_data))
            image = image.convert('RGB')
            
            # Get color histogram
            colors = image.getcolors(maxcolors=256*256*256)
            if colors:
                # Sort by frequency and get top colors
                colors.sort(key=lambda x: x[0], reverse=True)
                dominant_colors = []
                
                for count, color in colors[:5]:  # Top 5 colors
                    dominant_colors.append({
                        "rgb": color,
                        "frequency": count,
                        "percentage": (count / sum(c[0] for c in colors)) * 100
                    })
                
                return dominant_colors
            
            return []
            
        except ImportError:
            logger.warning("PIL not available for color extraction")
            return []
        except Exception as e:
            logger.warning(f"Color extraction failed: {e}")
            return []
    
    async def _extract_pdf_content(self, pdf_path: Path) -> str:
        """Extract content from PDF"""
        try:
            import PyPDF2
            
            with open(pdf_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                content = ""
                
                for page in reader.pages:
                    content += page.extract_text() + "\n"
                
                return content.strip()
                
        except ImportError:
            logger.warning("PyPDF2 not available for PDF processing")
            return "PDF processing not available"
        except Exception as e:
            logger.warning(f"PDF extraction failed: {e}")
            return f"PDF extraction failed: {e}"
    
    async def _extract_docx_content(self, docx_path: Path) -> str:
        """Extract content from DOCX"""
        try:
            from docx import Document
            
            doc = Document(docx_path)
            content = ""
            
            for paragraph in doc.paragraphs:
                content += paragraph.text + "\n"
            
            return content.strip()
            
        except ImportError:
            logger.warning("python-docx not available for DOCX processing")
            return "DOCX processing not available"
        except Exception as e:
            logger.warning(f"DOCX extraction failed: {e}")
            return f"DOCX extraction failed: {e}"
    
    async def _analyze_document_content(self, content: str) -> Dict[str, Any]:
        """Analyze document content"""
        # Basic analysis
        words = content.split()
        sentences = content.split('.')
        
        # Extract title (first line or first sentence)
        title = None
        lines = content.split('\n')
        for line in lines:
            if line.strip():
                title = line.strip()
                break
        
        # Basic keyword extraction (simple approach)
        keywords = []
        word_freq = {}
        for word in words:
            word = word.lower().strip('.,!?;:"()[]{}')
            if len(word) > 3:  # Only consider words longer than 3 characters
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # Get top keywords
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        keywords = [word for word, freq in sorted_words[:10]]
        
        # Generate summary (first few sentences)
        summary = '. '.join(sentences[:3]) + '.' if len(sentences) > 3 else content
        
        return {
            "title": title,
            "word_count": len(words),
            "sentence_count": len(sentences),
            "keywords": keywords,
            "summary": summary,
            "structure": {
                "paragraphs": len(content.split('\n\n')),
                "lines": len(lines)
            }
        }
    
    async def _extract_audio_metadata(self, audio_data: bytes) -> Dict[str, Any]:
        """Extract audio metadata"""
        # Mock implementation - replace with actual audio processing
        return {
            "duration": 120.5,
            "sample_rate": 44100,
            "channels": 2,
            "format": "mp3"
        }
    
    async def _transcribe_audio(self, audio_data: bytes) -> Optional[str]:
        """Transcribe audio to text"""
        # Mock implementation - replace with actual speech recognition
        return "This is a mock transcription of the audio content."
    
    async def _detect_speakers(self, audio_data: bytes) -> List[Dict[str, Any]]:
        """Detect speakers in audio"""
        # Mock implementation - replace with actual speaker detection
        return [
            {"speaker_id": "speaker_1", "start_time": 0.0, "end_time": 60.0},
            {"speaker_id": "speaker_2", "start_time": 60.0, "end_time": 120.5}
        ]
    
    async def _parse_csv(self, csv_data: str) -> Dict[str, Any]:
        """Parse CSV data"""
        try:
            import csv
            import io
            
            reader = csv.DictReader(io.StringIO(csv_data))
            rows = list(reader)
            
            return {
                "headers": reader.fieldnames,
                "rows": rows,
                "row_count": len(rows)
            }
            
        except Exception as e:
            logger.warning(f"CSV parsing failed: {e}")
            return {"error": str(e)}
    
    async def _parse_xml(self, xml_data: str) -> Dict[str, Any]:
        """Parse XML data"""
        try:
            import xml.etree.ElementTree as ET
            
            root = ET.fromstring(xml_data)
            
            def element_to_dict(element):
                result = {}
                if element.text and element.text.strip():
                    result['text'] = element.text.strip()
                
                if element.attrib:
                    result['attributes'] = element.attrib
                
                children = {}
                for child in element:
                    child_dict = element_to_dict(child)
                    if child.tag in children:
                        if not isinstance(children[child.tag], list):
                            children[child.tag] = [children[child.tag]]
                        children[child.tag].append(child_dict)
                    else:
                        children[child.tag] = child_dict
                
                if children:
                    result.update(children)
                
                return result
            
            return element_to_dict(root)
            
        except Exception as e:
            logger.warning(f"XML parsing failed: {e}")
            return {"error": str(e)}
    
    async def _parse_yaml(self, yaml_data: str) -> Dict[str, Any]:
        """Parse YAML data"""
        try:
            import yaml
            
            return yaml.safe_load(yaml_data)
            
        except ImportError:
            logger.warning("PyYAML not available for YAML parsing")
            return {"error": "YAML parsing not available"}
        except Exception as e:
            logger.warning(f"YAML parsing failed: {e}")
            return {"error": str(e)}

# Global multimodal processor instance
multimodal_processor = MultimodalInputProcessor()

async def main():
    """Test multimodal input processor"""
    print("🎭 Multimodal Input Processor Test")
    
    # Test text processing
    text_result = await multimodal_processor.process_input("Hello, this is a test document.", "text/plain")
    print(f"Text processing: {text_result.success}")
    print(f"Content: {text_result.extracted_data.get('content', '')[:50]}...")
    
    # Test JSON processing
    json_data = '{"name": "John", "age": 30, "city": "New York"}'
    json_result = await multimodal_processor.process_input(json_data, "application/json")
    print(f"JSON processing: {json_result.success}")
    print(f"Parsed data: {json_result.extracted_data.get('parsed_data', {})}")
    
    # Test CSV processing
    csv_data = "name,age,city\nJohn,30,New York\nJane,25,Los Angeles"
    csv_result = await multimodal_processor.process_input(csv_data, "text/csv")
    print(f"CSV processing: {csv_result.success}")
    print(f"Headers: {csv_result.extracted_data.get('parsed_data', {}).get('headers', [])}")

if __name__ == "__main__":
    asyncio.run(main())
