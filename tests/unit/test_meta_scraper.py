#!/usr/bin/env python3
""'
Test script for Meta AI Document Scraper
Tests with a small subset of URLs to validate functionality
""'

import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from enhanced_meta_ai_scraper import AdvancedMetaAIScraper

def test_scraper():
    """TODO: Add docstring."""
    """Test the scraper with a small subset""'
    print("Testing Meta AI Document Scraper...')
    print("=' * 50)

    # Create test scraper with limited sources
    scraper = AdvancedMetaAIScraper(output_dir="test_meta_ai_docs')

    # Test with just a few URLs
    test_sources = {
        "test_research': [
            "https://ai.meta.com/research/',
        ],
        "test_llama': [
            "https://ai.meta.com/llama/',
        ]
    }

    # Temporarily replace sources for testing
    original_sources = scraper.sources
    scraper.sources = test_sources

    try:
        results = scraper.scrape_all()

        print("\nTest Results:')
        print("-' * 30)

        for category, category_results in results.items():
            success_count = len([doc for doc in category_results if doc["metadata"]["status"] == "success'])
            print(f"{category}: {success_count}/{len(category_results)} successful')

            for doc in category_results:
                if doc["metadata"]["status"] == "success':
                    print(f"  ✓ {doc["metadata"]["title"][:50]}...')
                    print(f"    Word count: {doc["metadata"]["word_count"]}')
                    print(f"    Insights: {len(doc["insights"])}')
                else:
                    print(f"  ✗ Failed: {doc["metadata"]["error"]}')

        print(f"\nTest completed! Results saved to: {scraper.output_dir}')
        return True

    except Exception as e:
        print(f"Test failed: {e}')
        return False
    finally:
        # Restore original sources
        scraper.sources = original_sources

if __name__ == "__main__':
    success = test_scraper()
    sys.exit(0 if success else 1)
