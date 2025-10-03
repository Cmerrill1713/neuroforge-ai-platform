#!/usr/bin/env python3
"""
External Drive Ingestion with Docling
Process entire external drives and populate knowledge base with advanced document processing
"""

import asyncio
import json
import logging
import os
import time
from pathlib import Path
from typing import Dict, Any, List, Optional, Set
import aiofiles
import aiohttp
from concurrent.futures import ThreadPoolExecutor
import mimetypes

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ExternalDriveIngester:
    """Ingest external drives using Docling for advanced document processing"""
    
    def __init__(self, api_url: str = "http://localhost:8004"):
        self.api_url = api_url
        self.docling_url = f"{api_url}/api/docling"
        self.rag_url = f"{api_url}/api/rag/enhanced"
        
        # Supported file extensions for Docling processing
        self.supported_extensions = {
            # Documents
            '.pdf', '.docx', '.doc', '.pptx', '.ppt', '.xlsx', '.xls',
            # Text files
            '.txt', '.md', '.markdown', '.rtf', '.odt',
            # Web files
            '.html', '.htm', '.xml',
            # Images (OCR)
            '.jpg', '.jpeg', '.png', '.tiff', '.tif', '.bmp',
            # Data files
            '.csv', '.json', '.yaml', '.yml'
        }
        
        # Directories to skip
        self.skip_directories = {
            'System Volume Information', '$RECYCLE.BIN', '.Trashes', '.fseventsd',
            '.Spotlight-V100', '.TemporaryItems', '.VolumeIcon.icns',
            'node_modules', '.git', '__pycache__', '.DS_Store', '.cache',
            'venv', 'env', '.env', 'tmp', 'temp'
        }
        
        # File size limits (in MB)
        self.max_file_size_mb = 50  # Skip files larger than 50MB
        
        # Processing statistics
        self.stats = {
            'total_files_found': 0,
            'files_processed': 0,
            'files_skipped': 0,
            'files_failed': 0,
            'processing_time': 0,
            'documents_added': 0,
            'errors': []
        }
    
    async def ingest_drive(self, drive_path: str, max_files: Optional[int] = None) -> Dict[str, Any]:
        """
        Ingest entire external drive
        
        Args:
            drive_path: Path to external drive
            max_files: Maximum number of files to process (None for all)
        """
        start_time = time.time()
        drive_path = Path(drive_path)
        
        logger.info(f"🚀 Starting external drive ingestion: {drive_path}")
        logger.info(f"📁 Drive exists: {drive_path.exists()}")
        logger.info(f"📊 Max files limit: {max_files or 'No limit'}")
        
        if not drive_path.exists():
            raise ValueError(f"Drive path does not exist: {drive_path}")
        
        # Check Docling API health
        if not await self._check_docling_health():
            raise RuntimeError("Docling API is not healthy")
        
        # Discover all files
        logger.info("🔍 Discovering files on external drive...")
        files_to_process = await self._discover_files(drive_path, max_files)
        
        self.stats['total_files_found'] = len(files_to_process)
        logger.info(f"📄 Found {len(files_to_process)} files to process")
        
        if not files_to_process:
            logger.warning("⚠️ No files found to process")
            return self.stats
        
        # Process files in batches
        await self._process_files_batch(files_to_process)
        
        # Calculate final statistics
        self.stats['processing_time'] = time.time() - start_time
        
        # Save results
        await self._save_ingestion_results(drive_path)
        
        logger.info("🎉 External drive ingestion completed!")
        self._print_summary()
        
        return self.stats
    
    async def _check_docling_health(self) -> bool:
        """Check if Docling API is healthy"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.docling_url}/health", timeout=10) as response:
                    if response.status == 200:
                        data = await response.json()
                        healthy = data.get('status') == 'healthy' and data.get('docling_available', False)
                        logger.info(f"✅ Docling API health: {data.get('status')}")
                        return healthy
                    else:
                        logger.error(f"❌ Docling API health check failed: {response.status}")
                        return False
        except Exception as e:
            logger.error(f"❌ Docling API health check error: {e}")
            return False
    
    async def _discover_files(self, drive_path: Path, max_files: Optional[int]) -> List[Path]:
        """Discover all processable files on the drive"""
        files_to_process = []
        
        def scan_directory(path: Path) -> List[Path]:
            files = []
            try:
                for item in path.iterdir():
                    if item.name.startswith('.'):
                        continue
                    
                    if item.is_dir():
                        if item.name in self.skip_directories:
                            continue
                        files.extend(scan_directory(item))
                    elif item.is_file():
                        if item.suffix.lower() in self.supported_extensions:
                            # Check file size
                            try:
                                size_mb = item.stat().st_size / (1024 * 1024)
                                if size_mb <= self.max_file_size_mb:
                                    files.append(item)
                                else:
                                    logger.debug(f"⏭️ Skipping large file: {item} ({size_mb:.1f}MB)")
                                    self.stats['files_skipped'] += 1
                            except OSError:
                                logger.debug(f"⏭️ Skipping inaccessible file: {item}")
                                self.stats['files_skipped'] += 1
                        else:
                            self.stats['files_skipped'] += 1
                    
                    # Limit files if specified
                    if max_files and len(files) >= max_files:
                        logger.info(f"🛑 Reached file limit: {max_files}")
                        break
            
            except PermissionError:
                logger.warning(f"⚠️ Permission denied accessing: {path}")
            except Exception as e:
                logger.error(f"❌ Error scanning {path}: {e}")
            
            return files
        
        # Use thread pool for file system operations
        with ThreadPoolExecutor(max_workers=4) as executor:
            loop = asyncio.get_event_loop()
            files_to_process = await loop.run_in_executor(executor, scan_directory, drive_path)
        
        return files_to_process
    
    async def _process_files_batch(self, files: List[Path]):
        """Process files in batches using Docling"""
        batch_size = 5  # Process 5 files concurrently
        semaphore = asyncio.Semaphore(batch_size)
        
        async def process_single_file(file_path: Path):
            async with semaphore:
                try:
                    await self._process_file_with_docling(file_path)
                    self.stats['files_processed'] += 1
                except Exception as e:
                    logger.error(f"❌ Failed to process {file_path}: {e}")
                    self.stats['files_failed'] += 1
                    self.stats['errors'].append({
                        'file': str(file_path),
                        'error': str(e)
                    })
        
        # Process files in batches
        tasks = []
        for file_path in files:
            task = asyncio.create_task(process_single_file(file_path))
            tasks.append(task)
            
            # Process in batches to avoid overwhelming the system
            if len(tasks) >= batch_size:
                await asyncio.gather(*tasks)
                tasks = []
                
                # Log progress
                progress = (self.stats['files_processed'] + self.stats['files_failed']) / len(files) * 100
                logger.info(f"📊 Progress: {progress:.1f}% ({self.stats['files_processed'] + self.stats['files_failed']}/{len(files)})")
        
        # Process remaining tasks
        if tasks:
            await asyncio.gather(*tasks)
    
    async def _process_file_with_docling(self, file_path: Path):
        """Process a single file using Docling"""
        try:
            # Prepare request
            request_data = {
                "file_path": str(file_path),
                "use_docling": True,
                "extract_tables": True,
                "extract_images": True,
                "ocr_enabled": True
            }
            
            # Process with Docling
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.docling_url}/process",
                    json=request_data,
                    timeout=60  # 60 second timeout for large files
                ) as response:
                    
                    if response.status == 200:
                        result = await response.json()
                        
                        if result['success']:
                            await self._add_to_knowledge_base(file_path, result)
                            logger.info(f"✅ Processed: {file_path.name}")
                        else:
                            logger.warning(f"⚠️ Processing failed: {file_path.name}")
                            raise Exception(result.get('error_message', 'Processing failed'))
                    else:
                        error_text = await response.text()
                        raise Exception(f"HTTP {response.status}: {error_text}")
        
        except asyncio.TimeoutError:
            logger.warning(f"⏱️ Timeout processing: {file_path.name}")
            raise Exception("Processing timeout")
        except Exception as e:
            logger.error(f"❌ Error processing {file_path.name}: {e}")
            raise
    
    async def _add_to_knowledge_base(self, file_path: Path, docling_result: Dict[str, Any]):
        """Add processed document to knowledge base"""
        try:
            extracted_data = docling_result.get('extracted_data', {})
            
            # Prepare document for knowledge base
            document_content = extracted_data.get('content', '')
            if not document_content:
                logger.warning(f"⚠️ No content extracted from: {file_path.name}")
                return
            
            # Create metadata
            metadata = {
                'source': str(file_path),
                'filename': file_path.name,
                'file_type': file_path.suffix.lower(),
                'processing_method': 'docling',
                'docling_processed': extracted_data.get('docling_processed', False),
                'word_count': extracted_data.get('word_count', 0),
                'pages': extracted_data.get('pages', 1),
                'tables_count': len(extracted_data.get('tables', [])),
                'images_count': len(extracted_data.get('images', [])),
                'processing_time_ms': docling_result.get('processing_time_ms', 0)
            }
            
            # Add to knowledge base via RAG API
            kb_request = {
                "documents": [document_content],
                "metadata": [metadata]
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.rag_url}/add-documents",
                    json=kb_request,
                    timeout=30
                ) as response:
                    
                    if response.status == 200:
                        self.stats['documents_added'] += 1
                        logger.debug(f"📚 Added to knowledge base: {file_path.name}")
                    else:
                        error_text = await response.text()
                        logger.warning(f"⚠️ Failed to add to KB: {file_path.name} - {error_text}")
        
        except Exception as e:
            logger.error(f"❌ Failed to add to knowledge base: {file_path.name} - {e}")
    
    async def _save_ingestion_results(self, drive_path: Path):
        """Save ingestion results to file"""
        try:
            results = {
                'drive_path': str(drive_path),
                'ingestion_timestamp': time.time(),
                'statistics': self.stats,
                'docling_capabilities': {
                    'supported_formats': list(self.supported_extensions),
                    'max_file_size_mb': self.max_file_size_mb,
                    'api_url': self.api_url
                }
            }
            
            results_file = f"external_drive_ingestion_results_{int(time.time())}.json"
            
            async with aiofiles.open(results_file, 'w') as f:
                await f.write(json.dumps(results, indent=2))
            
            logger.info(f"💾 Results saved to: {results_file}")
        
        except Exception as e:
            logger.error(f"❌ Failed to save results: {e}")
    
    def _print_summary(self):
        """Print ingestion summary"""
        logger.info("\n" + "="*70)
        logger.info("📊 EXTERNAL DRIVE INGESTION SUMMARY")
        logger.info("="*70)
        logger.info(f"📁 Total files found: {self.stats['total_files_found']}")
        logger.info(f"✅ Files processed: {self.stats['files_processed']}")
        logger.info(f"⏭️ Files skipped: {self.stats['files_skipped']}")
        logger.info(f"❌ Files failed: {self.stats['files_failed']}")
        logger.info(f"📚 Documents added to KB: {self.stats['documents_added']}")
        logger.info(f"⏱️ Total time: {self.stats['processing_time']:.1f} seconds")
        
        if self.stats['errors']:
            logger.info(f"⚠️ Errors encountered: {len(self.stats['errors'])}")
            for error in self.stats['errors'][:5]:  # Show first 5 errors
                logger.info(f"   - {error['file']}: {error['error']}")
        
        success_rate = (self.stats['files_processed'] / self.stats['total_files_found'] * 100) if self.stats['total_files_found'] > 0 else 0
        logger.info(f"🎯 Success rate: {success_rate:.1f}%")
        logger.info("="*70)

async def main():
    """Main function for external drive ingestion"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Ingest external drive with Docling')
    parser.add_argument('drive_path', help='Path to external drive')
    parser.add_argument('--max-files', type=int, help='Maximum number of files to process')
    parser.add_argument('--api-url', default='http://localhost:8004', help='API URL')
    
    args = parser.parse_args()
    
    ingester = ExternalDriveIngester(args.api_url)
    
    try:
        results = await ingester.ingest_drive(args.drive_path, args.max_files)
        
        if results['files_processed'] > 0:
            print(f"\n🎉 Successfully processed {results['files_processed']} files!")
            print(f"📚 Added {results['documents_added']} documents to knowledge base!")
            print("🚀 Your external drive content is now searchable!")
        else:
            print("\n⚠️ No files were processed. Check the logs for details.")
    
    except Exception as e:
        logger.error(f"❌ Ingestion failed: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(asyncio.run(main()))
