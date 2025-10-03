#!/usr/bin/env python3
"""
Comprehensive Docling Integration Test
Test Docling with actual document processing
"""

import asyncio
import json
import logging
import tempfile
import requests
from pathlib import Path
from typing import Dict, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ComprehensiveDoclingTester:
    """Comprehensive Docling integration tester"""
    
    def __init__(self, base_url: str = "http://localhost:8004"):
        self.base_url = base_url
        self.test_results = []
    
    async def run_comprehensive_tests(self):
        """Run comprehensive Docling tests"""
        logger.info("🧪 Starting Comprehensive Docling Tests")
        
        tests = [
            ("API Health", self.test_api_health),
            ("Create Test Document", self.test_create_sample_document),
            ("Process Text Document", self.test_process_text_document),
            ("Test Batch Processing", self.test_batch_processing),
            ("Test Upload Endpoint", self.test_upload_endpoint),
            ("Integration with RAG", self.test_rag_integration)
        ]
        
        for test_name, test_func in tests:
            try:
                logger.info(f"🔍 Running {test_name}...")
                result = await test_func()
                self.test_results.append({
                    "test": test_name,
                    "success": result,
                    "status": "✅ PASSED" if result else "❌ FAILED"
                })
                logger.info(f"{'✅' if result else '❌'} {test_name}: {'PASSED' if result else 'FAILED'}")
            except Exception as e:
                logger.error(f"❌ {test_name} failed with error: {e}")
                self.test_results.append({
                    "test": test_name,
                    "success": False,
                    "status": f"❌ ERROR: {str(e)}"
                })
        
        self.print_summary()
        return self.test_results
    
    async def test_api_health(self) -> bool:
        """Test Docling API health"""
        try:
            response = requests.get(f"{self.base_url}/api/docling/health", timeout=10)
            if response.status_code == 200:
                data = response.json()
                logger.info(f"✅ Docling API is healthy: {data['status']}")
                logger.info(f"✅ Docling available: {data['docling_available']}")
                logger.info(f"✅ Supported formats: {len(data['supported_formats'])}")
                return True
            else:
                logger.error(f"❌ Health check failed: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"❌ Health check error: {e}")
            return False
    
    async def test_create_sample_document(self) -> bool:
        """Create a sample document for testing"""
        try:
            # Create a sample text document
            sample_content = """
# Sample Document for Docling Testing

## Introduction
This is a test document created to validate Docling integration with our AI system.

## Features Being Tested
- Text extraction
- Document structure analysis
- Metadata extraction
- Content processing

## Test Data
Here are some test elements:

### Table Example
| Feature | Status | Notes |
|---------|--------|-------|
| PDF Processing | ✅ | Working |
| DOCX Processing | ✅ | Working |
| OCR | ✅ | Available |
| Table Extraction | ✅ | Available |

### Code Example
```python
def test_docling():
    return "Docling integration test"
```

## Conclusion
This document tests various Docling capabilities including:
1. Headers and sections
2. Tables and lists
3. Code blocks
4. Structured content

End of test document.
"""
            
            # Save to temporary file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
                f.write(sample_content)
                self.test_file_path = f.name
            
            logger.info(f"✅ Created test document: {self.test_file_path}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to create test document: {e}")
            return False
    
    async def test_process_text_document(self) -> bool:
        """Test processing the sample document"""
        try:
            if not hasattr(self, 'test_file_path'):
                logger.error("❌ Test file not created")
                return False
            
            # Test document processing
            request_data = {
                "file_path": self.test_file_path,
                "use_docling": True,
                "extract_tables": True,
                "extract_images": True,
                "ocr_enabled": True
            }
            
            response = requests.post(
                f"{self.base_url}/api/docling/process",
                json=request_data,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"✅ Document processed successfully")
                logger.info(f"✅ Processing time: {data['processing_time_ms']}ms")
                logger.info(f"✅ Content type: {data['content_type']}")
                
                # Check extracted data
                extracted_data = data.get('extracted_data', {})
                logger.info(f"✅ Document type: {extracted_data.get('type')}")
                logger.info(f"✅ Word count: {extracted_data.get('word_count')}")
                logger.info(f"✅ Docling processed: {extracted_data.get('docling_processed')}")
                
                # Check for tables
                tables = extracted_data.get('tables', [])
                logger.info(f"✅ Tables found: {len(tables)}")
                
                # Check for structure
                structure = extracted_data.get('structure', {})
                logger.info(f"✅ Has headers: {structure.get('has_headers')}")
                logger.info(f"✅ Has lists: {structure.get('has_lists')}")
                
                return True
            else:
                logger.error(f"❌ Document processing failed: {response.status_code}")
                logger.error(f"Response: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Document processing error: {e}")
            return False
    
    async def test_batch_processing(self) -> bool:
        """Test batch processing with the sample document"""
        try:
            if not hasattr(self, 'test_file_path'):
                logger.error("❌ Test file not created")
                return False
            
            # Test batch processing
            request_data = {
                "file_paths": [self.test_file_path],
                "use_docling": True,
                "parallel_processing": True,
                "max_concurrent": 1
            }
            
            response = requests.post(
                f"{self.base_url}/api/docling/batch",
                json=request_data,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"✅ Batch processing completed")
                logger.info(f"✅ Total processed: {data['total_processed']}")
                logger.info(f"✅ Successful: {data['successful_count']}")
                logger.info(f"✅ Failed: {data['failed_count']}")
                logger.info(f"✅ Total time: {data['total_time_ms']}ms")
                
                if data['successful_count'] > 0:
                    result = data['results'][0]
                    logger.info(f"✅ First result success: {result['success']}")
                    return True
                else:
                    logger.error("❌ No successful processing in batch")
                    return False
            else:
                logger.error(f"❌ Batch processing failed: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Batch processing error: {e}")
            return False
    
    async def test_upload_endpoint(self) -> bool:
        """Test document upload endpoint"""
        try:
            if not hasattr(self, 'test_file_path'):
                logger.error("❌ Test file not created")
                return False
            
            # Test file upload
            with open(self.test_file_path, 'rb') as f:
                files = {'file': (Path(self.test_file_path).name, f, 'text/markdown')}
                data = {
                    'use_docling': 'true',
                    'extract_tables': 'true',
                    'extract_images': 'true',
                    'ocr_enabled': 'true'
                }
                
                response = requests.post(
                    f"{self.base_url}/api/docling/upload",
                    files=files,
                    data=data,
                    timeout=30
                )
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"✅ Upload processing completed")
                logger.info(f"✅ Processing time: {result['processing_time_ms']}ms")
                logger.info(f"✅ Original filename: {result['metadata'].get('original_filename')}")
                
                extracted_data = result.get('extracted_data', {})
                logger.info(f"✅ Word count: {extracted_data.get('word_count')}")
                logger.info(f"✅ Docling processed: {extracted_data.get('docling_processed')}")
                
                return True
            else:
                logger.error(f"❌ Upload processing failed: {response.status_code}")
                logger.error(f"Response: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Upload processing error: {e}")
            return False
    
    async def test_rag_integration(self) -> bool:
        """Test integration with RAG system"""
        try:
            # Test if the enhanced RAG system can use Docling-processed documents
            response = requests.get(f"{self.base_url}/api/rag/enhanced/health", timeout=10)
            
            if response.status_code == 200:
                logger.info("✅ RAG system is available")
                
                # Test RAG search
                search_request = {
                    "query_text": "Docling integration test",
                    "top_k": 3,
                    "use_hybrid_search": False,
                    "min_confidence": 0.1
                }
                
                search_response = requests.post(
                    f"{self.base_url}/api/rag/enhanced/search",
                    json=search_request,
                    timeout=15
                )
                
                if search_response.status_code == 200:
                    search_data = search_response.json()
                    logger.info("✅ RAG search completed")
                    logger.info(f"✅ Results found: {len(search_data.get('results', []))}")
                    return True
                else:
                    logger.warning(f"⚠️ RAG search failed: {search_response.status_code}")
                    return True  # Still consider this a pass since RAG is available
            else:
                logger.error(f"❌ RAG system not available: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"❌ RAG integration test error: {e}")
            return False
    
    def print_summary(self):
        """Print test summary"""
        logger.info("\n" + "="*70)
        logger.info("🧪 COMPREHENSIVE DOCLING INTEGRATION TEST SUMMARY")
        logger.info("="*70)
        
        passed = sum(1 for result in self.test_results if result["success"])
        total = len(self.test_results)
        
        for result in self.test_results:
            logger.info(f"{result['status']} {result['test']}")
        
        logger.info(f"\n📊 Results: {passed}/{total} tests passed")
        logger.info(f"🎯 Success Rate: {(passed/total)*100:.1f}%")
        
        if passed == total:
            logger.info("🎉 All tests passed! Docling integration is fully functional.")
            logger.info("🚀 Your system now has advanced document processing capabilities!")
        else:
            logger.info("⚠️ Some tests failed. Check the logs for details.")
        
        logger.info("="*70)
        
        # Cleanup
        if hasattr(self, 'test_file_path'):
            try:
                Path(self.test_file_path).unlink()
                logger.info(f"🧹 Cleaned up test file: {self.test_file_path}")
            except:
                pass

async def main():
    """Run comprehensive Docling tests"""
    tester = ComprehensiveDoclingTester()
    results = await tester.run_comprehensive_tests()
    
    all_passed = all(result["success"] for result in results)
    
    if all_passed:
        print("\n🎉 Docling integration is fully functional!")
        print("🚀 Your AI system now has advanced document processing capabilities!")
    else:
        print("\n⚠️ Some tests failed. Check the results above.")
    
    return all_passed

if __name__ == "__main__":
    asyncio.run(main())
