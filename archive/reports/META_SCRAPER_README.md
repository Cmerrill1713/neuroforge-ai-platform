# Meta AI Document Scraper

A focused scraper specifically designed to extract Meta's AI documentation, research papers, and resources.

## Features

- **Targeted Scraping**: Specifically targets Meta AI sources
- **Multiple Source Types**: Handles GitHub, arXiv, Hugging Face, and PyTorch docs
- **Structured Output**: Saves content in organized JSON format
- **Error Handling**: Robust error handling with detailed logging
- **Respectful Scraping**: Includes delays and proper headers

## Quick Start

```bash
# Run the scraper
python3 run_meta_scraper.py

# Or run directly
python3 meta_document_scraper.py
```

## Sources Scraped

### Research Papers
- arXiv Meta AI papers
- Papers with Code Meta AI research
- Google Scholar Meta AI publications

### Llama Documentation
- GitHub Llama repository
- Hugging Face Llama models
- Llama README and docs

### GitHub Repositories
- Facebook Research organization
- Meta Llama repositories
- PyTorch repository

### Official Documentation
- PyTorch documentation
- Meta AI official site
- Facebook Research site

## Output Structure

```
meta_documents/
├── research_papers.json
├── llama_docs.json
├── github_repos.json
├── official_docs.json
├── all_meta_documents.json
└── meta_scraping_summary.txt
```

## Integration

This scraper is designed to work with your existing AI crawling system. The output JSON files can be easily integrated into your knowledge base or processing pipeline.

## Requirements

- Python 3.7+
- requests
- beautifulsoup4

## Usage Example

```python
from meta_document_scraper import MetaDocumentScraper

# Create scraper instance
scraper = MetaDocumentScraper("my_meta_docs")

# Scrape all Meta documents
results = scraper.scrape_all_meta_docs()

# Access results
for category, docs in results.items():
    for doc in docs:
        if doc['metadata']['status'] == 'success':
            print(f"Title: {doc['metadata']['title']}")
            print(f"Content: {doc['content'][:200]}...")
```

## Notes

- The scraper includes respectful delays between requests
- Failed requests are logged with error details
- Content is extracted based on source type (GitHub, arXiv, etc.)
- All metadata is preserved for integration with your AI system
