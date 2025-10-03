# Model Capabilities Definition

## Current Model Architecture

### 🧠 **TEXT MODELS** (Ollama)
| Model | Size | Primary Use | Capabilities |
|-------|------|-------------|--------------|
| `qwen2.5:72b` | 72B | **Complex reasoning, analysis, planning** | Text generation, reasoning, analysis, planning, research |
| `qwen2.5:14b` | 14B | **Balanced performance** | Text generation, coding, reasoning, analysis |
| `qwen2.5:7b` | 7B | **Fast responses, general chat** | Text generation, coding, instruction following |
| `mistral:7b` | 7B | **Code generation** | Text generation, coding, instruction following |
| `llama3.2:3b` | 3B | **Fast responses, simple tasks** | Text generation, simple reasoning |

### 👁️ **VISION MODELS**
| Model | Type | Primary Use | Capabilities |
|-------|------|-------------|--------------|
| `apple-FastVLM-7B` | HuggingFace | **Image/video analysis only** | Image analysis, video analysis, visual understanding |
| `llava:7b` | Ollama | **Multimodal text+vision** | Text generation, image analysis, multimodal reasoning |

### 🎤 **AUDIO MODELS**
| Model | Type | Primary Use | Capabilities |
|-------|------|-------------|--------------|
| `chatterbox-tts` | HuggingFace | **Text-to-Speech** | Speech synthesis, voice generation |
| `whisper` | HuggingFace | **Speech-to-Text** | Speech recognition, transcription |

## 🎯 **ROUTING RULES**

### Text Tasks → Ollama Models
- **Simple chat**: `llama3.2:3b` (fastest)
- **General tasks**: `qwen2.5:7b` (balanced)
- **Complex reasoning**: `qwen2.5:72b` (most capable)
- **Code generation**: `mistral:7b` or `qwen2.5:7b`

### Vision Tasks → Vision Models
- **Image analysis**: `apple-FastVLM-7B` (vision-only)
- **Multimodal tasks**: `llava:7b` (text+vision)

### Audio Tasks → Audio Models
- **Text-to-Speech**: `chatterbox-tts`
- **Speech-to-Text**: `whisper`

## 🚫 **CRITICAL ROUTING ISSUES**

### Current Problems:
1. **FastVLM being used for text chat** ❌
   - FastVLM is VISION-ONLY
   - Should NEVER handle text-only tasks
   - Causes tensor errors and poor responses

2. **Chat endpoint routing incorrectly** ❌
   - Intelligent router selects FastVLM for text tasks
   - Should route to Ollama models instead

3. **Vision endpoint has attribute errors** ❌
   - `VisionAnalysisRequest` doesn't have `prompt` field
   - Should use `analysis_type` field

## 🔧 **REQUIRED FIXES**

### 1. Fix Intelligent Model Router
- Prevent FastVLM from being selected for text tasks
- Ensure proper model capability matching
- Add audio model routing

### 2. Fix Vision Endpoint
- Use correct field names (`analysis_type` not `prompt`)
- Ensure FastVLM is properly loaded and accessible

### 3. Add Audio Model Routing
- Route TTS requests to `chatterbox-tts`
- Route STT requests to `whisper`
- Ensure proper audio model initialization

## 📊 **PERFORMANCE CHARACTERISTICS**

### Response Times (Apple Silicon MPS):
- `llama3.2:3b`: ~1-2 seconds
- `qwen2.5:7b`: ~3-5 seconds  
- `qwen2.5:72b`: ~25-60 seconds
- `apple-FastVLM-7B`: ~8-15 seconds (vision only)
- `chatterbox-tts`: ~10-20 seconds
- `whisper`: ~2-5 seconds

### Memory Usage:
- `llama3.2:3b`: ~2GB
- `qwen2.5:7b`: ~4.7GB
- `qwen2.5:72b`: ~45GB
- `apple-FastVLM-7B`: ~15GB
- `chatterbox-tts`: ~3GB
- `whisper`: ~1GB

## 🎯 **OPTIMAL MODEL SELECTION**

### For Different Use Cases:
- **Quick chat**: `llama3.2:3b`
- **Research/analysis**: `qwen2.5:72b`
- **Code generation**: `mistral:7b`
- **Image analysis**: `apple-FastVLM-7B`
- **Multimodal tasks**: `llava:7b`
- **Voice synthesis**: `chatterbox-tts`
- **Speech recognition**: `whisper`

This architecture ensures each model is used for its intended purpose, maximizing performance and avoiding errors.
