# 🚀 MCP Automated Content Processing Guide

## Overview

This guide explains how to use the MCP-powered automated content processing pipeline to efficiently crawl, process, and store content from multiple sources in parallel.

## 🎯 What We Built

### ✅ **MCP Content Processor** (`mcp_automated_content_processor.py`)
- **Parallel Processing**: Process multiple content sources simultaneously
- **Quality Assessment**: AI-powered content quality scoring
- **Vector Embeddings**: Automatic embedding generation for semantic search
- **Knowledge Base Integration**: Automatic updates to your existing vector store
- **Content Filtering**: Quality and relevance-based filtering
- **Tag Extraction**: Automatic tag generation for content categorization

### ✅ **Configuration System** (`configs/content_sources.yaml`)
- **Multiple Sources**: arXiv, GitHub, YouTube, Stack Overflow, Reddit, etc.
- **Flexible Filtering**: Category-based, language-based, and quality-based filters
- **Rate Limiting**: Respectful crawling with configurable delays
- **Quality Thresholds**: Configurable minimum quality and relevance scores

### ✅ **Demo System** (`demo_mcp_content_processing.py`)
- **Complete Examples**: End-to-end processing demonstrations
- **Search Capabilities**: Semantic search through processed content
- **Quality Analysis**: Comprehensive quality metrics and reporting
- **Continuous Processing**: Automated periodic content updates

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the Demo

```bash
python demo_mcp_content_processing.py
```

### 3. Basic Usage

```python
from mcp_automated_content_processor import MCPContentProcessor, ContentSource

# Initialize processor
processor = MCPContentProcessor()
await processor.initialize()

# Create sources
sources = [
    ContentSource(
        name="arxiv_ml",
        url="https://arxiv.org/search/?query=machine+learning",
        type="arxiv",
        priority=9,
        filters={"categories": ["cs.LG", "cs.AI"], "max_results": 20}
    )
]

# Create and run processing job
job = await processor.create_processing_job(sources)
results = await processor.process_content_sources(job.job_id)
```

## 📊 Key Features

### **Parallel Processing**
- Process up to 5 sources simultaneously
- Configurable parallel processing limits
- Efficient resource utilization

### **Quality Assessment**
- **Readability Score**: Content clarity and structure
- **Technical Depth**: Sophistication level
- **Completeness**: Thoroughness of content
- **Accuracy Indicators**: Reliability signals
- **Domain Relevance**: Relevance to AI/ML/tech

### **Content Sources**
- **arXiv**: Academic research papers
- **GitHub**: Trending repositories and code
- **YouTube**: Educational tutorials
- **Stack Overflow**: Technical discussions
- **Reddit**: Community discussions
- **News Sites**: TechCrunch, VentureBeat
- **Blogs**: Medium articles

### **Search & Retrieval**
- **Semantic Search**: Vector-based similarity search
- **Quality Filtering**: Filter by minimum quality scores
- **Category Filtering**: Search within specific categories
- **Tag-based Search**: Find content by tags

## 🔧 Configuration

### **Source Configuration**

```yaml
sources:
  arxiv_ml:
    name: "arXiv Machine Learning"
    url: "https://arxiv.org/search/?query=machine+learning"
    type: "arxiv"
    priority: 9
    enabled: true
    crawl_interval: 3600
    filters:
      categories: ["cs.LG", "cs.AI"]
      max_results: 100
```

### **Processing Configuration**

```yaml
processing:
  max_parallel_sources: 5
  quality_threshold: 0.6
  relevance_threshold: 0.5
  auto_update_knowledge_base: true
```

### **Model Configuration**

```yaml
models:
  quality_assessment: "llama3.1:8b"
  tag_extraction: "llama3.2:3b"
  embeddings: "nomic-embed-text:latest"
```

## 📈 Usage Examples

### **1. Process arXiv Papers**

```python
# Create arXiv sources
arxiv_sources = [
    ContentSource(
        name="arxiv_transformer",
        url="https://arxiv.org/search/?query=transformer",
        type="arxiv",
        priority=9,
        filters={"categories": ["cs.LG", "cs.CL"]}
    )
]

# Process with high quality threshold
job = await processor.create_processing_job(
    sources=arxiv_sources,
    quality_threshold=0.8,
    relevance_threshold=0.7
)
```

### **2. Search Processed Content**

```python
# Semantic search
results = await processor.search_processed_content(
    query="transformer attention mechanism",
    limit=10,
    min_quality=0.7
)

for content in results:
    print(f"Title: {content.title}")
    print(f"Quality: {content.quality_score:.2f}")
    print(f"Source: {content.source}")
```

### **3. Get Processing Statistics**

```python
stats = await processor.get_processing_stats()
print(f"Total content: {stats['total_content_items']}")
print(f"Average quality: {stats['average_quality_score']:.3f}")
print(f"Categories: {stats['category_distribution']}")
```

## 🔄 Continuous Processing

### **Set Up Automated Updates**

```python
# Create continuous processing sources
continuous_sources = [
    ContentSource(
        name="arxiv_daily",
        url="https://arxiv.org/list/cs.AI/recent",
        type="arxiv",
        crawl_interval=3600,  # 1 hour
        filters={"max_results": 10}
    )
]

# Process periodically
while True:
    job = await processor.create_processing_job(continuous_sources)
    results = await processor.process_content_sources(job.job_id)
    await asyncio.sleep(3600)  # Wait 1 hour
```

## 📊 Quality Metrics

### **Content Quality Scores**
- **0.9-1.0**: Excellent quality, highly relevant
- **0.8-0.9**: Very good quality, relevant
- **0.7-0.8**: Good quality, mostly relevant
- **0.6-0.7**: Acceptable quality, somewhat relevant
- **<0.6**: Low quality, filtered out by default

### **Quality Assessment Factors**
1. **Readability (20%)**: Clear writing, good structure
2. **Technical Depth (25%)**: Sophisticated technical content
3. **Completeness (20%)**: Thorough coverage of topic
4. **Accuracy Indicators (20%)**: Reliable sources, citations
5. **Domain Relevance (15%)**: Relevant to AI/ML/tech domains

## 🛠️ Integration with Existing System

### **MCP Integration**
- Uses your existing MCP adapter
- Integrates with Pydantic AI validation
- Leverages your Ollama models
- Connects to your vector store

### **Knowledge Base Updates**
- Automatic vector embeddings
- Metadata storage
- Category and tag assignment
- Quality score tracking

### **Performance Monitoring**
- Processing time tracking
- Quality score monitoring
- Source performance metrics
- Error logging and alerting

## 🚨 Error Handling

### **Common Issues**
1. **Source Unavailable**: Automatic retry with backoff
2. **Quality Assessment Failure**: Default quality scores
3. **Embedding Generation Error**: Skip embedding, continue processing
4. **Knowledge Base Update Failure**: Log error, continue processing

### **Monitoring**
- Comprehensive logging
- Error tracking
- Performance metrics
- Quality score trends

## 📚 Advanced Usage

### **Custom Content Sources**

```python
custom_source = ContentSource(
    name="custom_api",
    url="https://api.example.com/content",
    type="api",
    priority=8,
    filters={"category": "ai", "limit": 50}
)
```

### **Custom Quality Assessment**

```python
# Override quality assessment with custom logic
async def custom_quality_assessment(content):
    # Your custom quality assessment logic
    return ContentQualityMetrics(...)
```

### **Custom Content Processing**

```python
# Add custom processing steps
async def custom_content_processor(content_item):
    # Your custom processing logic
    processed_item = await your_custom_processing(content_item)
    return processed_item
```

## 🎯 Next Steps

1. **Run the Demo**: Start with `demo_mcp_content_processing.py`
2. **Configure Sources**: Customize `configs/content_sources.yaml`
3. **Set Up Continuous Processing**: Implement automated periodic updates
4. **Monitor Quality**: Track quality scores and adjust thresholds
5. **Scale Up**: Add more sources and increase parallel processing

## 🔗 Integration Points

- **Existing MCP Tools**: Leverages your current MCP infrastructure
- **Vector Store**: Integrates with your PostgreSQL vector database
- **Ollama Models**: Uses your existing model setup
- **Knowledge Base**: Updates your existing knowledge base
- **Monitoring**: Integrates with your existing logging and monitoring

This automated content processing pipeline will significantly enhance your knowledge base with high-quality, relevant content from multiple sources, all processed in parallel for maximum efficiency!
