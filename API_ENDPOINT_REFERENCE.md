# 🔌 COMPLETE API ENDPOINT REFERENCE
**Last Updated**: October 2, 2025 (Docling Integration Complete - Advanced Document Processing)  
**Purpose**: Comprehensive reference for all API endpoints in the system

---

## 🎯 **SYSTEM OVERVIEW**

The consolidated API server runs on **Port 8004** and provides access to all system functionality through RESTful endpoints.

**Base URL**: `http://localhost:8004`

---

## 📋 **CORE API ENDPOINTS**

### **System Management**
| Endpoint | Method | Purpose | Parameters |
|----------|--------|---------|------------|
| `/` | GET | System status | None |
| `/api/system/health` | GET | System health check | None |
| `/api/system/metrics` | GET | Performance metrics | None |
| `/docs` | GET | API documentation | None |

### **Chat & Agents**
| Endpoint | Method | Purpose | Parameters |
|----------|--------|---------|------------|
| `/api/chat/` | POST | Chat interactions | `{"message": "string"}` |
| `/api/agents/` | GET | Agent management | None |

### **Knowledge Base**
| Endpoint | Method | Purpose | Parameters |
|----------|--------|---------|------------|
| `/api/knowledge/` | GET | Knowledge base search | Query parameters |

### **Admin Operations**
| Endpoint | Method | Purpose | Parameters |
|----------|--------|---------|------------|
| `/api/admin/` | GET | Admin operations | None |
| `/api/admin/cache/clear` | POST | Clear system cache | None |

---

## 🚀 **ENHANCED API ENDPOINTS**

### **Voice Services**
| Endpoint | Method | Purpose | Parameters |
|----------|--------|---------|------------|
| `/api/voice/options` | GET | Get available voices | None |
| `/api/voice/health` | GET | Voice services health | None |
| `/api/voice/synthesize` | POST | Text-to-speech | `{"text": "string", "voice_profile": "string"}` |

### **Enhanced RAG System**
| Endpoint | Method | Purpose | Parameters |
|----------|--------|---------|------------|
| `/api/rag/enhanced/search` | POST | Enhanced semantic search | `{"query_text": "string", "top_k": int}` |
| `/api/rag/enhanced/health` | GET | RAG system health | None |
| `/api/rag/enhanced/stats` | GET | RAG system statistics | None |

### **Enhanced MCP Tools**
| Endpoint | Method | Purpose | Parameters |
|----------|--------|---------|------------|
| `/api/mcp/tools` | GET | Available MCP tools | None |
| `/api/mcp/execute` | POST | Execute MCP tool | `{"tool": "string", "args": []}` |
| `/api/mcp/health` | GET | MCP system health | None |

### **Self-Healing System**
| Endpoint | Method | Purpose | Parameters |
|----------|--------|---------|------------|
| `/api/healing/health` | GET | Self-healing system health | None |
| `/api/healing/analyze-and-heal` | POST | Analyze and fix errors | `{"error_message": "string"}` |
| `/api/healing/research-unknown-error` | POST | Research unknown errors | `{"error_message": "string"}` |
| `/api/healing/stats` | GET | Healing statistics | None |
| `/api/healing/emergency-heal` | POST | Emergency healing | `{"error_message": "string"}` |

### **Vision Processing (LLaVA)**
| Endpoint | Method | Purpose | Parameters |
|----------|--------|---------|------------|
| `/api/vision/analyze` | POST | Analyze images | `{"image_url": "string"}` |
| `/api/vision/health` | GET | Vision system health | None |
| `/api/vision/models` | GET | Available vision models | None |

### **Optimized Large Models**
| Endpoint | Method | Purpose | Parameters |
|----------|--------|---------|------------|
| `/api/model/status` | GET | Model optimization status | None |
| `/api/model/optimize` | POST | Optimize model | `{"model_name": "string"}` |
| `/api/model/health` | GET | Model system health | None |

### **MLX Processing**
| Endpoint | Method | Purpose | Parameters |
|----------|--------|---------|------------|
| `/api/mlx/status` | GET | MLX processing status | None |
| `/api/mlx/process` | POST | Process with MLX | `{"text": "string"}` |
| `/api/mlx/health` | GET | MLX system health | None |

---

## 🌐 **FRONTEND API PROXY ENDPOINTS**

The frontend runs on **Port 3000** and provides API proxy endpoints that forward requests to the backend.

**Base URL**: `http://localhost:3000`

### **Frontend Proxy Endpoints**
| Endpoint | Method | Purpose | Backend Target |
|----------|--------|---------|----------------|
| `/api/system/health` | GET | System health via frontend | `http://localhost:8004/api/system/health` |
| `/api/chat` | POST | Chat via frontend | `http://localhost:8004/api/chat/` |
| `/api/voice/options` | GET | Voice options via frontend | `http://localhost:8004/api/voice/options` |
| `/api/voice/health` | GET | Voice health via frontend | `http://localhost:8004/api/voice/health` |
| `/api/rag/query` | POST | RAG queries via frontend | `http://localhost:8004/api/rag/enhanced/search` |

### **Frontend Environment Variables**
```bash
# Required in frontend/.env.local
NEXT_PUBLIC_CONSOLIDATED_API_URL=http://localhost:8004
NEXT_PUBLIC_AGENTIC_PLATFORM_URL=http://localhost:8000
NEXT_PUBLIC_API_URL=http://localhost:8004
```

---

## 🔧 **USAGE EXAMPLES**

### **Basic Health Check**
```bash
curl http://localhost:8004/api/system/health
```

### **Chat Interaction**
```bash
curl -X POST http://localhost:8004/api/chat/ \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello, how are you?"}'
```

### **Voice Synthesis**
```bash
curl -X POST http://localhost:8004/api/voice/synthesize \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello world", "voice_profile": "assistant"}'
```

### **Enhanced RAG Search**
```bash
curl -X POST http://localhost:8004/api/rag/enhanced/search \
  -H "Content-Type: application/json" \
  -d '{"query_text": "machine learning", "top_k": 5}'
```

### **Self-Healing Error Analysis**
```bash
curl -X POST http://localhost:8004/api/healing/analyze-and-heal \
  -H "Content-Type: application/json" \
  -d '{"error_message": "ModuleNotFoundError: No module named test"}'
```

### **MCP Tool Execution**
```bash
curl -X POST http://localhost:8004/api/mcp/execute \
  -H "Content-Type: application/json" \
  -d '{"tool": "calculator", "args": ["2+2"]}'
```

### **Vision Analysis**
```bash
curl -X POST http://localhost:8004/api/vision/analyze \
  -H "Content-Type: application/json" \
  -d '{"image_url": "https://example.com/image.jpg"}'
```

### **Frontend API Proxy Testing**
```bash
# Test frontend system health proxy
curl http://localhost:3000/api/system/health

# Test frontend chat proxy
curl -X POST http://localhost:3000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello from frontend"}'

# Test frontend voice options proxy
curl http://localhost:3000/api/voice/options

# Test frontend RAG query proxy
curl -X POST http://localhost:3000/api/rag/query \
  -H "Content-Type: application/json" \
  -d '{"query_text": "artificial intelligence"}'
```

### **Middleware Testing (All Working - 93.8% Success Rate)**
```bash
# Test GZip compression and performance timing
curl -H "Accept-Encoding: gzip" http://localhost:8004/api/system/health -I
# Expected: content-encoding: gzip, x-process-time header

# Test request validation (should return 422)
curl -X POST -H "Content-Type: application/json" \
  -d '{"message": ""}' http://localhost:8004/api/chat/
# Expected: HTTP 422 with validation error

# Test CORS headers
curl -H "Origin: http://localhost:3000" http://localhost:8004/api/system/health -I
# Expected: Access-Control-Allow-Origin header
```

---

## 📄 **DOCLING DOCUMENT PROCESSING ENDPOINTS**

**Base URL**: `http://localhost:8004`

### **Health & Status**
| Endpoint | Method | Purpose | Parameters |
|----------|--------|---------|------------|
| `/api/docling/health` | GET | Check Docling service health | None |
| `/api/docling/status` | GET | Get processing status and capabilities | None |
| `/api/docling/formats` | GET | Get supported document formats | None |

### **Document Processing**
| Endpoint | Method | Purpose | Parameters |
|----------|--------|---------|------------|
| `/api/docling/process` | POST | Process single document | `file_path`, `use_docling`, `extract_tables`, `extract_images`, `ocr_enabled` |
| `/api/docling/upload` | POST | Upload and process file | `file` (multipart), `use_docling`, `extract_tables`, `extract_images`, `ocr_enabled` |
| `/api/docling/batch` | POST | Batch process multiple files | `file_paths[]`, `use_docling`, `parallel_processing`, `max_concurrent` |

### **Docling Testing Examples**
```bash
# Check Docling health
curl http://localhost:8004/api/docling/health

# Get supported formats
curl http://localhost:8004/api/docling/formats

# Process a document
curl -X POST http://localhost:8004/api/docling/process \
  -H "Content-Type: application/json" \
  -d '{"file_path": "/path/to/document.pdf", "use_docling": true}'

# Upload and process file
curl -X POST http://localhost:8004/api/docling/upload \
  -F "file=@document.pdf" \
  -F "use_docling=true" \
  -F "extract_tables=true" \
  -F "ocr_enabled=true"

# Batch process multiple files
curl -X POST http://localhost:8004/api/docling/batch \
  -H "Content-Type: application/json" \
  -d '{"file_paths": ["/path/to/doc1.pdf", "/path/to/doc2.docx"], "use_docling": true}'
```

### **Supported Formats**
- **PDF**: OCR, table extraction, layout preservation
- **DOCX/PPTX/XLSX**: Office document processing
- **Images**: JPG, PNG, TIFF (OCR enabled)
- **Text**: TXT, MD, HTML, RTF
- **Data**: CSV, JSON, YAML, XML

---

## 📊 **RESPONSE FORMATS**

### **Standard Success Response**
```json
{
  "success": true,
  "data": { ... },
  "timestamp": "2025-10-02T18:00:00.000Z"
}
```

### **Standard Error Response**
```json
{
  "success": false,
  "error": "Error message",
  "details": { ... },
  "timestamp": "2025-10-02T18:00:00.000Z"
}
```

### **Health Check Response**
```json
{
  "status": "healthy",
  "version": "2.0.0",
  "uptime": 3600.0,
  "components": { ... }
}
```

---

## 🚨 **ERROR HANDLING**

### **HTTP Status Codes**
- **200**: Success
- **400**: Bad Request (invalid parameters)
- **404**: Not Found (endpoint not found)
- **500**: Internal Server Error
- **503**: Service Unavailable

### **Common Error Scenarios**
1. **Service Down**: Check if `main.py` is running
2. **Port Conflict**: Verify port 8004 is available
3. **Missing Dependencies**: Check requirements.txt
4. **Invalid Parameters**: Verify request format

---

## 🔍 **TESTING COMMANDS**

### **Comprehensive Health Check**
```bash
# System health
curl http://localhost:8004/api/system/health

# Enhanced features health
curl http://localhost:8004/api/healing/health
curl http://localhost:8004/api/voice/health
curl http://localhost:8004/api/rag/enhanced/health
curl http://localhost:8004/api/vision/health
curl http://localhost:8004/api/model/status
curl http://localhost:8004/api/mlx/status
```

### **Feature Testing**
```bash
# Test self-healing
curl -X POST http://localhost:8004/api/healing/research-unknown-error \
  -H "Content-Type: application/json" \
  -d '{"error_message": "ImportError: cannot import name TestClass"}'

# Test RAG search
curl -X POST http://localhost:8004/api/rag/enhanced/search \
  -H "Content-Type: application/json" \
  -d '{"query_text": "artificial intelligence"}'

# Test MCP tools
curl http://localhost:8004/api/mcp/tools
```

---

## 📈 **PERFORMANCE TARGETS**

| Endpoint Type | Target Response Time |
|---------------|---------------------|
| Health Checks | < 500ms |
| Chat Interactions | < 3s |
| RAG Search | < 2s |
| Voice Synthesis | < 5s |
| Vision Analysis | < 10s |
| Self-Healing | < 1s |

---

## 🔒 **SECURITY NOTES**

- All endpoints require proper JSON formatting
- Input validation is performed on all parameters
- Error messages are sanitized for security
- No authentication required for development (production setup needed)

---

**⚠️ IMPORTANT**: This reference should be updated whenever new endpoints are added or existing ones are modified. Always test endpoints after making changes to ensure they work correctly.
