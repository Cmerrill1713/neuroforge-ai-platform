#!/usr/bin/env python3
"""
Demo External Drive Ingestion
Demonstrate Docling integration with external drive processing
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

class ExternalDriveDemo:
    """Demonstrate external drive ingestion capabilities"""
    
    def __init__(self, api_url: str = "http://localhost:8004"):
        self.api_url = api_url
        self.docling_url = f"{api_url}/api/docling"
        self.rag_url = f"{api_url}/api/rag/enhanced"
    
    async def run_demo(self):
        """Run complete demonstration"""
        print("🚀 External Drive Ingestion Demo with Docling")
        print("=" * 60)
        
        # Step 1: Check system health
        await self.check_system_health()
        
        # Step 2: Create sample documents
        sample_files = await self.create_sample_documents()
        
        # Step 3: Process documents with Docling
        processed_results = await self.process_documents(sample_files)
        
        # Step 4: Add to knowledge base
        await self.add_to_knowledge_base(processed_results)
        
        # Step 5: Demonstrate search capabilities
        await self.demonstrate_search()
        
        # Step 6: Show batch processing
        await self.demonstrate_batch_processing(sample_files)
        
        # Cleanup
        await self.cleanup(sample_files)
        
        print("\n🎉 Demo completed successfully!")
        print("🚀 Your system is ready for external drive ingestion!")
    
    async def check_system_health(self):
        """Check system health and capabilities"""
        print("\n📊 Step 1: Checking System Health")
        print("-" * 40)
        
        try:
            # Check Docling health
            response = requests.get(f"{self.docling_url}/health", timeout=10)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Docling Status: {data['status']}")
                print(f"✅ Docling Available: {data['docling_available']}")
                print(f"✅ Supported Formats: {len(data['supported_formats'])}")
                print(f"✅ Version: {data['version']}")
            
            # Check RAG system
            response = requests.get(f"{self.rag_url}/health", timeout=10)
            if response.status_code == 200:
                print("✅ RAG System: Healthy")
            
            # Check main API
            response = requests.get(f"{self.api_url}/api/system/health", timeout=10)
            if response.status_code == 200:
                print("✅ Main API: Healthy")
            
        except Exception as e:
            print(f"❌ Health check failed: {e}")
            raise
    
    async def create_sample_documents(self) -> list:
        """Create sample documents for demonstration"""
        print("\n📄 Step 2: Creating Sample Documents")
        print("-" * 40)
        
        sample_files = []
        
        # Create sample PDF content (as text file for demo)
        pdf_content = """
# Sample PDF Document

## Executive Summary
This is a demonstration document showing Docling's advanced processing capabilities.

## Key Features
- Advanced text extraction
- Table processing
- Image analysis with OCR
- Structure preservation

## Financial Data
| Quarter | Revenue | Profit | Growth |
|---------|---------|--------|--------|
| Q1 2024 | $1.2M   | $300K  | +15%   |
| Q2 2024 | $1.4M   | $350K  | +17%   |
| Q3 2024 | $1.6M   | $400K  | +14%   |

## Conclusion
Docling provides enterprise-grade document processing capabilities.
"""
        
        # Create sample DOCX content
        docx_content = """
# Technical Specification Document

## Overview
This document outlines the technical specifications for the new AI system.

## System Requirements
- CPU: 8 cores minimum
- RAM: 32GB recommended
- Storage: 1TB SSD
- GPU: Apple Metal or NVIDIA RTX

## Performance Metrics
- Processing Speed: < 100ms per document
- Accuracy: 99.5% text extraction
- OCR Accuracy: 98.2%
- Table Extraction: 99.1%

## Implementation Details
The system uses Docling for advanced document processing with the following features:
1. Multi-format support
2. OCR capabilities
3. Table extraction
4. Layout preservation
"""
        
        # Create sample CSV content
        csv_content = """Name,Department,Salary,Start Date
John Smith,Engineering,95000,2023-01-15
Jane Doe,Marketing,87000,2023-02-20
Bob Johnson,Sales,78000,2023-03-10
Alice Brown,HR,82000,2023-04-05
Charlie Wilson,Engineering,105000,2023-05-12"""
        
        # Save sample files
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(pdf_content)
            sample_files.append(Path(f.name))
            print(f"✅ Created: {f.name}")
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(docx_content)
            sample_files.append(Path(f.name))
            print(f"✅ Created: {f.name}")
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(csv_content)
            sample_files.append(Path(f.name))
            print(f"✅ Created: {f.name}")
        
        print(f"📊 Total sample files created: {len(sample_files)}")
        return sample_files
    
    async def process_documents(self, files: list) -> list:
        """Process documents with Docling"""
        print("\n🔧 Step 3: Processing Documents with Docling")
        print("-" * 40)
        
        results = []
        
        for file_path in files:
            try:
                print(f"🔄 Processing: {file_path.name}")
                
                request_data = {
                    "file_path": str(file_path),
                    "use_docling": True,
                    "extract_tables": True,
                    "extract_images": True,
                    "ocr_enabled": True
                }
                
                response = requests.post(
                    f"{self.docling_url}/process",
                    json=request_data,
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    results.append({
                        'file': file_path.name,
                        'success': result['success'],
                        'data': result['extracted_data'],
                        'processing_time': result['processing_time_ms']
                    })
                    
                    if result['success']:
                        extracted = result['extracted_data']
                        print(f"  ✅ Success: {extracted.get('word_count', 0)} words")
                        print(f"  ✅ Tables: {len(extracted.get('tables', []))}")
                        print(f"  ✅ Time: {result['processing_time_ms']:.1f}ms")
                    else:
                        print(f"  ❌ Failed: {result.get('error_message')}")
                else:
                    print(f"  ❌ HTTP Error: {response.status_code}")
                
            except Exception as e:
                print(f"  ❌ Error: {e}")
        
        print(f"📊 Processed: {len([r for r in results if r['success']])}/{len(files)} files")
        return results
    
    async def add_to_knowledge_base(self, results: list):
        """Add processed documents to knowledge base"""
        print("\n📚 Step 4: Adding to Knowledge Base")
        print("-" * 40)
        
        documents_added = 0
        
        for result in results:
            if not result['success']:
                continue
            
            try:
                extracted_data = result['data']
                content = extracted_data.get('content', '')
                
                if not content:
                    continue
                
                metadata = {
                    'source': result['file'],
                    'processing_method': 'docling_demo',
                    'word_count': extracted_data.get('word_count', 0),
                    'tables_count': len(extracted_data.get('tables', [])),
                    'processing_time_ms': result['processing_time']
                }
                
                kb_request = {
                    "documents": [content],
                    "metadata": [metadata]
                }
                
                response = requests.post(
                    f"{self.rag_url}/add-documents",
                    json=kb_request,
                    timeout=30
                )
                
                if response.status_code == 200:
                    documents_added += 1
                    print(f"  ✅ Added to KB: {result['file']}")
                else:
                    print(f"  ⚠️ Failed to add: {result['file']}")
                
            except Exception as e:
                print(f"  ❌ Error adding {result['file']}: {e}")
        
        print(f"📊 Documents added to knowledge base: {documents_added}")
    
    async def demonstrate_search(self):
        """Demonstrate search capabilities"""
        print("\n🔍 Step 5: Demonstrating Search Capabilities")
        print("-" * 40)
        
        search_queries = [
            "financial data revenue profit",
            "technical specifications system requirements",
            "employee salary department",
            "Docling document processing"
        ]
        
        for query in search_queries:
            try:
                print(f"🔍 Searching: '{query}'")
                
                search_request = {
                    "query_text": query,
                    "top_k": 3,
                    "use_hybrid_search": False,
                    "min_confidence": 0.1
                }
                
                response = requests.post(
                    f"{self.rag_url}/search",
                    json=search_request,
                    timeout=15
                )
                
                if response.status_code == 200:
                    search_data = response.json()
                    results = search_data.get('results', [])
                    print(f"  ✅ Found: {len(results)} results")
                    
                    for i, result in enumerate(results[:2], 1):
                        content = result.get('content', '')[:100]
                        score = result.get('score', 0)
                        print(f"    {i}. Score: {score:.3f} - {content}...")
                else:
                    print(f"  ❌ Search failed: {response.status_code}")
                
            except Exception as e:
                print(f"  ❌ Search error: {e}")
    
    async def demonstrate_batch_processing(self, files: list):
        """Demonstrate batch processing capabilities"""
        print("\n📦 Step 6: Demonstrating Batch Processing")
        print("-" * 40)
        
        try:
            file_paths = [str(f) for f in files]
            
            batch_request = {
                "file_paths": file_paths,
                "use_docling": True,
                "parallel_processing": True,
                "max_concurrent": 3
            }
            
            print(f"🔄 Batch processing {len(file_paths)} files...")
            
            response = requests.post(
                f"{self.docling_url}/batch",
                json=batch_request,
                timeout=60
            )
            
            if response.status_code == 200:
                batch_data = response.json()
                print(f"  ✅ Batch completed")
                print(f"  📊 Total processed: {batch_data['total_processed']}")
                print(f"  ✅ Successful: {batch_data['successful_count']}")
                print(f"  ❌ Failed: {batch_data['failed_count']}")
                print(f"  ⏱️ Total time: {batch_data['total_time_ms']:.1f}ms")
            else:
                print(f"  ❌ Batch processing failed: {response.status_code}")
        
        except Exception as e:
            print(f"  ❌ Batch processing error: {e}")
    
    async def cleanup(self, files: list):
        """Clean up temporary files"""
        print("\n🧹 Cleaning up temporary files")
        print("-" * 40)
        
        for file_path in files:
            try:
                file_path.unlink()
                print(f"  🗑️ Deleted: {file_path.name}")
            except Exception as e:
                print(f"  ⚠️ Could not delete {file_path.name}: {e}")

async def main():
    """Run the demonstration"""
    demo = ExternalDriveDemo()
    
    try:
        await demo.run_demo()
        
        print("\n" + "=" * 60)
        print("🎉 DEMONSTRATION COMPLETE!")
        print("=" * 60)
        print("🚀 Your system is ready for external drive ingestion!")
        print("📄 Use: python3 ingest_drive.py /path/to/your/drive")
        print("🔍 Search your processed documents through the RAG system")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(asyncio.run(main()))
