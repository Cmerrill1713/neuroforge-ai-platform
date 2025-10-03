# 🚀 NeuroForge Quick Start Guide

## Simple 2-Step Setup

### Step 1: Start the Backend
```bash
cd "/Users/christianmerrill/Prompt Engineering"
python3 main.py
```

Leave this running in one terminal.

### Step 2: Start the Frontend
```bash
cd "/Users/christianmerrill/Prompt Engineering/frontend"
npm run dev
```

Leave this running in another terminal.

---

## Access Your AI

**Open your browser:** http://localhost:3000

That's it! Just start chatting. All the NeuroForge intelligence (model selection, optimization, learning) happens automatically in the background.

---

## What's Running

- **Backend (Port 8004)**: All AI intelligence, routing, optimization
- **Frontend (Port 3000)**: Clean chat interface

---

## Features Working Automatically

✨ **Intelligent Model Routing** - Selects best model for each task  
🧠 **Thompson Bandit Selection** - Optimizes prompt/model choices  
🔄 **Continuous Learning** - Gets smarter with each interaction  
⚡ **Performance Optimization** - Caches responses, balances load  
📊 **Enhanced Monitoring** - Tracks health and performance  

All transparent to you - just chat naturally!

---

## Troubleshooting

### Backend won't start?
```bash
# Check if port is in use
lsof -i :8004

# Install dependencies if needed
pip3 install -r requirements.txt
```

### Frontend won't start?
```bash
cd frontend
npm install
npm run dev
```

### Check what's running
```bash
# Check backend
curl http://localhost:8004/

# Check frontend
curl http://localhost:3000/
```

---

**Enjoy your AI assistant!** 🎉
