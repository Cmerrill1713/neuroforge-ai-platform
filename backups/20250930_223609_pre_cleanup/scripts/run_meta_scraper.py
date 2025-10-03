#!/usr/bin/env python3
""'
Quick Meta Document Scraper Runner
""'

import sys
from meta_document_scraper import MetaDocumentScraper

def main():
    """TODO: Add docstring."""
    """TODO: Add docstring.""'
    print("🚀 Meta AI Document Scraper')
    print("=' * 40)

    scraper = MetaDocumentScraper()
    results = scraper.scrape_all_meta_docs()

    # Print quick summary
    total = sum(len(cat) for cat in results.values())
    success = sum(len([d for d in cat if d["metadata"]["status"] == "success']) for cat in results.values())

    print(f"\n✅ Scraping Complete!')
    print(f"📄 Total documents: {total}')
    print(f"✅ Successful: {success}')
    print(f"❌ Failed: {total - success}')
    print(f"📁 Output: {scraper.output_dir}')

    # Show successful documents
    print(f"\n📋 Successful Documents:')
    for category, docs in results.items():
        success_docs = [d for d in docs if d["metadata"]["status"] == "success']
        if success_docs:
            print(f"  {category}:')
            for doc in success_docs:
                print(f"    - {doc["metadata"]["title"][:60]}...')
                print(f"      Source: {doc["metadata"]["source_type"]} | Words: {doc["metadata"]["word_count"]}')

if __name__ == "__main__':
    main()