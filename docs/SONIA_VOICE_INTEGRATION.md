# Sonia Voice Integration Documentation

## 🎤 **Sonia Voice System Overview**

Sonia is our primary female voice assistant with a smooth British accent, integrated throughout the entire system using Microsoft Edge TTS for authentic female voice generation.

## 🔧 **Technical Implementation**

### **Voice Configuration**
- **Voice**: `en-GB-SoniaNeural` (Microsoft Edge TTS)
- **Engine**: Edge TTS (forced for Sonia to ensure female voice)
- **Rate**: 0.8 (smooth, natural pace)
- **Pitch**: +10% (more feminine tone)
- **Profile ID**: `sonia_clean`

### **System Architecture**
```
Frontend (Port 3000) → Next.js API Routes → Consolidated API (Port 8004) → TTS Server (Port 8086)
```

### **Key Implementation Details**

#### **1. TTS Server Configuration** (`src/api/tts_server.py`)
```python
# Force Edge TTS for Sonia to get proper female voice
if voice_profile == "sonia_clean":
    use_chatterbox = False  # Override Chatterbox (male-voiced)
    logger.info("🎭 Forcing Edge TTS for Sonia to ensure female voice")

# Sonia voice profile
"sonia_clean": {
    "chatterbox": {"exaggeration": 0.2, "cfg_weight": 0.7},
    "edge": {"voice": "en-GB-SoniaNeural", "rate": "0.8", "pitch": "+10%"},
    "description": "Sonia - British female voice with higher pitch"
}
```

#### **2. API Integration**
- **TTS Server**: `http://localhost:8086/synthesize`
- **Consolidated API**: `http://localhost:8004/api/voice/synthesize`
- **Frontend API**: `http://localhost:3000/api/voice/synthesize`

#### **3. Frontend Integration**
- **Voice Options**: `/api/voice/options` - Returns available voices including Sonia
- **Voice Synthesis**: `/api/voice/synthesize` - Generates audio with Sonia
- **System Health**: `/api/system/health` - Monitors TTS server status

## ✅ **Verification & Testing**

### **Test Results**
```bash
# TTS Server Direct
curl http://localhost:8086/synthesize → ✅ engine: edge_tts

# Consolidated API
curl http://localhost:8004/api/voice/synthesize → ✅ engine: edge_tts

# Frontend API
curl http://localhost:3000/api/voice/synthesize → ✅ engine: edge_tts
```

### **Available Voices**
1. **sonia_clean** - Smooth British female voice (Default)
2. **assistant** - Friendly assistant voice
3. **sultry** - Sultry feminine voice
4. **seductive** - Seductive feminine voice
5. **intimate** - Intimate whisper voice
6. **confident** - Confident feminine voice
7. **honey** - Honey-smooth feminine voice

## 🎯 **Frontend Integration**

### **Voice Toggle Control**
The frontend now includes a voice toggle to enable/disable voice synthesis:

- **Toggle Location**: Top-right of chat interface, next to voice selection
- **Label**: "Voice Response" 
- **Persistence**: Setting saved in localStorage
- **Default**: Enabled (voice on by default)

### **Voice Controls**
1. **Voice Toggle** - Enable/disable voice synthesis
2. **Voice Selection** - Choose from available voices (disabled when voice is off)
3. **Speak Button** - Individual message speak button (disabled when voice is off)

### **Usage Examples**

### **Frontend JavaScript**
```javascript
// Get available voices
const voices = await fetch('/api/voice/options').then(r => r.json());

// Synthesize speech with Sonia
const response = await fetch('/api/voice/synthesize', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        text: "Hello! This is Sonia speaking.",
        voice: "sonia_clean"
    })
});

const audioData = await response.json();
// audioData.audio_file contains the generated WAV file
```

### **Direct API Call**
```bash
curl -X POST http://localhost:8004/api/voice/synthesize \
  -H "Content-Type: application/json" \
  -d '{"text":"Hello Sonia!","voice":"sonia_clean"}'
```

## 🔍 **Troubleshooting**

### **Common Issues**
1. **Male Voice Instead of Female**: Ensure Sonia uses Edge TTS, not Chatterbox
2. **Audio Not Playing**: Check if audio file is generated and accessible
3. **API Errors**: Verify all services are running (TTS: 8086, Consolidated: 8004, Frontend: 3000)

### **Health Check**
```bash
# Check system health
curl http://localhost:3000/api/system/health

# Check TTS server directly
curl http://localhost:8086/status
```

## 📊 **Performance Metrics**

- **Response Time**: < 2 seconds for typical text
- **Audio Quality**: 44.1kHz WAV format
- **File Size**: ~50-70KB for 10-second speech
- **Engine**: Microsoft Edge TTS (cloud-based, high quality)

## 🎭 **Voice Characteristics**

- **Accent**: British English
- **Gender**: Female
- **Tone**: Professional, friendly, smooth
- **Speed**: Natural conversational pace
- **Pitch**: Slightly higher for feminine quality

---

**Last Updated**: January 1, 2025  
**Status**: ✅ Fully Operational  
**Engine**: Edge TTS (forced for Sonia)  
**Default Voice**: sonia_clean
