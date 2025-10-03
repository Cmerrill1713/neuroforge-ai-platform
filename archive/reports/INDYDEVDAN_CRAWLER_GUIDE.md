# IndyDevDan Content Crawler Usage Guide

## Overview
This crawler will scrape indydevdan's GitHub repositories and YouTube channel content, then add it to your knowledge base for use with your AI system.

## Quick Start

### 1. Setup
```bash
# Install dependencies
python setup_crawler.py

# Or manually install
pip install -r requirements.crawler.txt
```

### 2. Configure (Optional)
Add your GitHub token to `.env` file for higher rate limits:
```bash
GITHUB_TOKEN=your_github_token_here
```

### 3. Run Crawler
```bash
python indydevdan_content_crawler.py
```

## What It Does

### GitHub Crawling
- Fetches all repositories from indydevdan's GitHub profile
- Extracts repository metadata (stars, forks, language, etc.)
- Downloads README content
- Extracts keywords and tags

### YouTube Crawling
- Scrapes video metadata (title, description, views, duration)
- Downloads automatic captions/transcripts
- Processes video content for knowledge base

### Knowledge Base Integration
- Creates individual JSON files for each item
- Updates the main knowledge base index
- Adds proper metadata and retrieval tags
- Generates content hashes for deduplication

## Output Structure

```
knowledge_base/
├── index.json                          # Main index file
├── indydevdan_crawl_summary.json      # Crawl summary
├── github_123456.json                  # Individual GitHub repo
├── github_789012.json
├── youtube_abc123.json                 # Individual YouTube video
├── youtube_def456.json
└── ...
```

## Configuration Options

### GitHub Token (Optional)
- **Without token**: Uses public API (rate limited to 60 requests/hour)
- **With token**: Uses authenticated API (5000 requests/hour)

### YouTube Channel
- Provide full YouTube channel URL when prompted
- Example: `https://www.youtube.com/@indydevdan`

## Rate Limiting
- GitHub: Respects API rate limits automatically
- YouTube: 1 second delay between videos
- Both: Graceful error handling and retry logic

## Content Processing

### GitHub Repositories
Each repository entry includes:
- Basic metadata (name, description, stars, forks)
- README content
- Programming language
- Topics and keywords
- Creation and update dates

### YouTube Videos
Each video entry includes:
- Video metadata (title, description, views, duration)
- Full transcript/captions
- Upload date
- Keywords extracted from title/description

## Integration with Your AI System

The crawled content will be automatically integrated into your existing knowledge base system:

1. **Searchable**: Content is indexed and searchable
2. **Tagged**: Proper retrieval tags for easy filtering
3. **Structured**: Consistent format with your existing knowledge base
4. **Deduplicated**: Content hashes prevent duplicates

## Troubleshooting

### Common Issues

1. **GitHub Rate Limit**: Add a GitHub token to `.env` file
2. **YouTube Access**: Some videos may not have captions
3. **Network Issues**: Crawler includes retry logic
4. **Large Channels**: May take time for channels with many videos

### Error Handling
- All errors are logged with details
- Crawler continues processing other items
- Partial results are saved if crawl is interrupted

## Example Usage

```bash
# Basic crawl (GitHub only)
python indydevdan_content_crawler.py
# Press Enter when asked for YouTube URL

# Full crawl (GitHub + YouTube)
python indydevdan_content_crawler.py
# Enter: https://www.youtube.com/@indydevdan
```

## Results

After crawling, you'll have:
- ✅ All indydevdan's GitHub repositories in your knowledge base
- ✅ All YouTube videos with transcripts
- ✅ Searchable content for your AI system
- ✅ Proper metadata and tagging
- ✅ Integration with existing knowledge base structure

The content will be immediately available for your AI system to reference and use in responses!
