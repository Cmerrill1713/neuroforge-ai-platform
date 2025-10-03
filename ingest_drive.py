#!/usr/bin/env python3
"""
External Drive Ingestion Wrapper
Easy-to-use script for ingesting external drives with Docling
"""

import asyncio
import sys
from pathlib import Path

# Add scripts directory to path
sys.path.append(str(Path(__file__).parent / "scripts"))

from ingest_external_drive import ExternalDriveIngester

async def main():
    """Interactive external drive ingestion"""
    print("🚀 External Drive Ingestion with Docling")
    print("=" * 50)
    
    # Get drive path from user
    if len(sys.argv) > 1:
        drive_path = sys.argv[1]
    else:
        drive_path = input("Enter path to external drive: ").strip()
    
    if not drive_path:
        print("❌ No drive path provided")
        return 1
    
    drive_path = Path(drive_path)
    if not drive_path.exists():
        print(f"❌ Drive path does not exist: {drive_path}")
        return 1
    
    # Get optional parameters
    max_files_input = input("Max files to process (Enter for no limit): ").strip()
    max_files = int(max_files_input) if max_files_input.isdigit() else None
    
    print(f"\n📁 Drive: {drive_path}")
    print(f"📊 Max files: {max_files or 'No limit'}")
    print(f"🔧 Processing with Docling (advanced document processing)")
    print(f"📚 Results will be added to knowledge base")
    
    confirm = input("\nProceed with ingestion? (y/N): ").strip().lower()
    if confirm != 'y':
        print("❌ Ingestion cancelled")
        return 0
    
    # Start ingestion
    ingester = ExternalDriveIngester()
    
    try:
        print("\n🚀 Starting ingestion...")
        results = await ingester.ingest_drive(drive_path, max_files)
        
        print(f"\n🎉 Ingestion completed!")
        print(f"✅ Processed: {results['files_processed']} files")
        print(f"📚 Added to KB: {results['documents_added']} documents")
        print(f"⏱️ Time: {results['processing_time']:.1f} seconds")
        
        if results['files_processed'] > 0:
            print("\n🚀 Your external drive content is now searchable!")
            print("💡 Try searching your knowledge base for content from the drive")
        
        return 0
    
    except KeyboardInterrupt:
        print("\n⚠️ Ingestion interrupted by user")
        return 1
    except Exception as e:
        print(f"\n❌ Ingestion failed: {e}")
        return 1

if __name__ == "__main__":
    exit(asyncio.run(main()))
