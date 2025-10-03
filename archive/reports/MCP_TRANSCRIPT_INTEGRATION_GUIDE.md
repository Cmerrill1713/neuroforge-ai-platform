# MCP Transcript Service Integration Guide

## Overview
Your system now has a complete MCP-integrated transcript service that can crawl GitHub repositories and YouTube channels, then process the content through your existing MCP infrastructure.

## What We've Built

### 1. **MCP Transcript Service** (`mcp_transcript_service.py`)
- Integrates with your existing MCP infrastructure
- Provides 5 main tools for content crawling and processing
- Works with your Docker setup

### 2. **IndyDevDan Content Crawler** (`indydevdan_content_crawler.py`)
- Crawls GitHub repositories and YouTube channels
- Downloads transcripts and processes content
- Saves everything to your knowledge base

### 3. **Docker Integration**
- Added `transcript-mcp` service to your `docker-compose.yml`
- Created `Dockerfile.transcript-mcp` for containerized deployment
- Updated `mcp.json` to include the transcript service

## Available MCP Tools

### 1. **crawl_github_repos**
```json
{
  "name": "crawl_github_repos",
  "description": "Crawl GitHub repositories for any user",
  "parameters": {
    "username": "string (default: indydevdan)"
  }
}
```

### 2. **crawl_youtube_channel**
```json
{
  "name": "crawl_youtube_channel",
  "description": "Crawl YouTube channel for videos and transcripts",
  "parameters": {
    "channel_url": "string (required)"
  }
}
```

### 3. **process_transcript**
```json
{
  "name": "process_transcript",
  "description": "Process and analyze a transcript",
  "parameters": {
    "transcript_id": "string (required)",
    "analysis_type": "summary|keywords|topics|sentiment"
  }
}
```

### 4. **search_transcripts**
```json
{
  "name": "search_transcripts",
  "description": "Search through crawled transcripts",
  "parameters": {
    "query": "string (required)",
    "source_type": "youtube_video|github_repository|all"
  }
}
```

### 5. **get_transcript_stats**
```json
{
  "name": "get_transcript_stats",
  "description": "Get statistics about crawled content"
}
```

## How to Use

### Option 1: Direct Python Usage
```bash
# Run the crawler directly
python3 indydevdan_content_crawler.py

# Test the MCP service
python3 test_mcp_transcript.py
```

### Option 2: Docker Deployment
```bash
# Start with MCP profile
docker-compose --profile mcp up -d

# Check logs
docker-compose logs transcript-mcp
```

### Option 3: MCP Client Integration
The service integrates with your existing MCP tools shown in the interface:
- **GitHub Official** (96 tools) - for repository access
- **YouTube transcripts** (2 tools) - for video transcript processing

## Example Usage Scenarios

### Scenario 1: Crawl a Different GitHub User
```python
# If indydevdan isn't the right username, try:
await service.handle_tool_call("crawl_github_repos", {
    "username": "actual_username_here"
})
```

### Scenario 2: Crawl YouTube Channel
```python
await service.handle_tool_call("crawl_youtube_channel", {
    "channel_url": "https://www.youtube.com/@actual_channel_name"
})
```

### Scenario 3: Process Transcripts
```python
# After crawling, process transcripts
await service.handle_tool_call("process_transcript", {
    "transcript_id": "youtube_abc123",
    "analysis_type": "summary"
})
```

### Scenario 4: Search Content
```python
# Search through all crawled content
await service.handle_tool_call("search_transcripts", {
    "query": "python programming",
    "source_type": "all"
})
```

## Integration with Your Existing MCP Tools

Your system already shows these MCP tools:
- **ArXiv MCP Server** (4 tools) - Research papers
- **Context7** (2 tools) - Context management  
- **DeepWiki** (3 tools) - Knowledge base
- **DuckDuckGo** (2 tools) - Web search
- **Fetch (Reference)** (1 tool) - Reference fetching
- **GitHub Official** (96 tools) - GitHub integration
- **YouTube transcripts** (2 tools) - Video transcripts

Our new **transcript-mcp** service adds 5 additional tools specifically for:
1. Crawling GitHub repositories
2. Crawling YouTube channels  
3. Processing transcripts
4. Searching content
5. Getting statistics

## Next Steps

1. **Find the correct GitHub username** for indydevdan
2. **Get the YouTube channel URL** for indydevdan
3. **Run the crawler** to populate your knowledge base
4. **Use the MCP tools** to search and process the content

## Configuration

### Environment Variables
```bash
# Optional: GitHub token for higher rate limits
GITHUB_TOKEN=your_github_token_here
```

### Docker Environment
The transcript service runs on port `8087` and integrates with your existing `ai-network`.

## Benefits

✅ **Integrated with your existing MCP infrastructure**  
✅ **Works with your Docker setup**  
✅ **Processes both GitHub and YouTube content**  
✅ **Saves everything to your knowledge base**  
✅ **Provides search and analysis capabilities**  
✅ **Compatible with your existing MCP tools**

The system is now ready to crawl indydevdan's content (once we have the correct usernames/URLs) and integrate it seamlessly with your existing MCP-powered AI system!
