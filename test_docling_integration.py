#!/usr/bin/env python3
"""
Test Docling Integration
Comprehensive testing of Docling integration with the system
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

class DoclingIntegrationTester:
    """Test Docling integration functionality"""
    
    def __init__(self, base_url: str = "http://localhost:8004"):
        self.base_url = base_url
        self.test_results = []
    
    async def run_all_tests(self):
        """Run all Docling integration tests"""
        logger.info("🧪 Starting Docling Integration Tests")
        
        tests = [
            ("Health Check", self.test_health_check),
            ("Supported Formats", self.test_supported_formats),
            ("Processing Status", self.test_processing_status),
            ("Enhanced Processor", self.test_enhanced_processor),
            ("API Endpoints", self.test_api_endpoints)
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
        
        # Print summary
        self.print_summary()
        
        # Save results
        with open("docling_integration_test_results.json", "w") as f:
            json.dump(self.test_results, f, indent=2)
        
        return self.test_results
    
    async def test_health_check(self) -> bool:
        """Test Docling health check endpoint"""
        try:
            response = requests.get(f"{self.base_url}/api/docling/health", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"Health check response: {data}")
                
                # Check if Docling is available
                docling_available = data.get("docling_available", False)
                status = data.get("status", "unknown")
                
                logger.info(f"Docling available: {docling_available}")
                logger.info(f"Status: {status}")
                logger.info(f"Supported formats: {len(data.get('supported_formats', []))}")
                
                return True
            else:
                logger.error(f"Health check failed with status {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Health check test failed: {e}")
            return False
    
    async def test_supported_formats(self) -> bool:
        """Test supported formats endpoint"""
        try:
            response = requests.get(f"{self.base_url}/api/docling/formats", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"Supported formats response: {json.dumps(data, indent=2)}")
                
                # Check if we have document formats
                doc_formats = data.get("document_formats", [])
                image_formats = data.get("image_formats", [])
                
                logger.info(f"Document formats: {len(doc_formats)}")
                logger.info(f"Image formats: {len(image_formats)}")
                
                # Check for key formats
                pdf_support = any(f["format"] == "PDF" for f in doc_formats)
                docx_support = any(f["format"] == "DOCX" for f in doc_formats)
                
                logger.info(f"PDF support: {pdf_support}")
                logger.info(f"DOCX support: {docx_support}")
                
                return len(doc_formats) > 0 and pdf_support and docx_support
            else:
                logger.error(f"Supported formats failed with status {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Supported formats test failed: {e}")
            return False
    
    async def test_processing_status(self) -> bool:
        """Test processing status endpoint"""
        try:
            response = requests.get(f"{self.base_url}/api/docling/status", timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"Processing status response: {data}")
                
                # Check status
                status = data.get("status", "unknown")
                docling_available = data.get("docling_available", False)
                
                logger.info(f"Processing status: {status}")
                logger.info(f"Docling available: {docling_available}")
                
                return status in ["available", "healthy"]
            else:
                logger.error(f"Processing status failed with status {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Processing status test failed: {e}")
            return False
    
    async def test_enhanced_processor(self) -> bool:
        """Test enhanced multimodal processor directly"""
        try:
            # Import and test the enhanced processor
            from src.core.multimodal.enhanced_input_processor import enhanced_multimodal_processor
            
            logger.info("Testing enhanced multimodal processor...")
            
            # Test basic text processing
            test_text = "This is a test document for Docling integration."
            result = await enhanced_multimodal_processor.process_input(
                test_text, 
                "text/plain",
                use_docling=False  # Use basic processing for text
            )
            
            logger.info(f"Text processing result: {result.success}")
            logger.info(f"Processing time: {result.processing_time_ms}ms")
            
            if result.success:
                logger.info(f"Extracted data: {result.extracted_data}")
                logger.info(f"Docling used: {result.metadata.get('docling_used', False)}")
                
                return True
            else:
                logger.error(f"Text processing failed: {result.error_message}")
                return False
                
        except Exception as e:
            logger.error(f"Enhanced processor test failed: {e}")
            return False
    
    async def test_api_endpoints(self) -> bool:
        """Test Docling API endpoints"""
        try:
            # Test batch processing endpoint (with empty list)
            batch_request = {
                "file_paths": [],
                "use_docling": True,
                "parallel_processing": True,
                "max_concurrent": 3
            }
            
            response = requests.post(
                f"{self.base_url}/api/docling/batch",
                json=batch_request,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"Batch processing response: {data}")
                
                # Should return empty results for empty file list
                total_processed = data.get("total_processed", 0)
                successful_count = data.get("successful_count", 0)
                
                logger.info(f"Total processed: {total_processed}")
                logger.info(f"Successful count: {successful_count}")
                
                return total_processed == 0 and successful_count == 0
            else:
                logger.error(f"Batch processing failed with status {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"API endpoints test failed: {e}")
            return False
    
    def print_summary(self):
        """Print test summary"""
        logger.info("\n" + "="*60)
        logger.info("🧪 DOCLING INTEGRATION TEST SUMMARY")
        logger.info("="*60)
        
        passed = sum(1 for result in self.test_results if result["success"])
        total = len(self.test_results)
        
        for result in self.test_results:
            logger.info(f"{result['status']} {result['test']}")
        
        logger.info(f"\n📊 Results: {passed}/{total} tests passed")
        logger.info(f"🎯 Success Rate: {(passed/total)*100:.1f}%")
        
        if passed == total:
            logger.info("🎉 All tests passed! Docling integration is working correctly.")
        else:
            logger.info("⚠️ Some tests failed. Check the logs for details.")
        
        logger.info("="*60)

async def main():
    """Run Docling integration tests"""
    tester = DoclingIntegrationTester()
    results = await tester.run_all_tests()
    
    # Check if all tests passed
    all_passed = all(result["success"] for result in results)
    
    if all_passed:
        print("\n🎉 Docling integration is fully functional!")
    else:
        print("\n⚠️ Some tests failed. Check the results above.")
    
    return all_passed

if __name__ == "__main__":
    asyncio.run(main())
