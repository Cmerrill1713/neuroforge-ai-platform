# 🚀 Server Startup Guide

## **Frontend and Backend Server Instructions**

### **🌐 Quick Start**

#### **Option 1: Manual Startup (Recommended)**

1. **Start Backend Server:**
   ```bash
   cd "/Users/christianmerrill/Prompt Engineering"
   python3 api_server.py
   ```

2. **Start Frontend Server (in new terminal):**
   ```bash
   cd "/Users/christianmerrill/Prompt Engineering/frontend"
   npm run dev
   ```

#### **Option 2: Automated Startup**
```bash
cd "/Users/christianmerrill/Prompt Engineering"
python3 start_servers.py
```

### **🔧 Prerequisites**

#### **Backend Requirements:**
- Python 3.8+
- FastAPI and Uvicorn installed
- Required Python packages

#### **Frontend Requirements:**
- Node.js 16+
- npm installed
- Frontend dependencies installed

### **📋 Server URLs**

Once started, the servers will be available at:

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

### **🎯 Available Features**

#### **Frontend Features:**
- ✅ **AI Chat** - Chat with 8 specialized AI models
- ✅ **Advanced Chat** - Bookmarks, likes, regeneration, editing
- ✅ **Voice Integration** - Speech-to-text and text-to-speech
- ✅ **Real-Time Collaboration** - Multi-user sessions, screen sharing
- ✅ **Code Editor** - AI-assisted coding with Monaco editor
- ✅ **Multimodal** - Image and document analysis
- ✅ **Learning Dashboard** - Progress tracking and analytics
- ✅ **Performance Monitor** - Real-time performance metrics

#### **Backend API Endpoints:**
- `GET /status` - Server status and health
- `GET /models` - Available AI models
- `POST /chat` - Chat with AI models
- `GET /health` - Health check
- `WebSocket /ws` - Real-time communication

### **🧪 Testing the Servers**

#### **1. Backend Testing:**
```bash
# Test backend status
curl http://localhost:8000/status

# Test available models
curl http://localhost:8000/models

# Test chat endpoint
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello, how are you?", "task_type": "text_generation"}'
```

#### **2. Frontend Testing:**
1. Open http://localhost:3000 in your browser
2. Navigate through the 7 panels using the sidebar
3. Test chat functionality
4. Try voice features
5. Test collaboration features
6. Use the code editor
7. Upload images for analysis
8. Check the learning dashboard
9. Monitor performance metrics

### **🔍 Troubleshooting**

#### **Backend Issues:**
- **Port 8000 in use**: Change port in `api_server.py`
- **Missing dependencies**: Install with `pip install fastapi uvicorn`
- **Python errors**: Check Python version and imports

#### **Frontend Issues:**
- **Port 3000 in use**: Next.js will automatically use next available port
- **Missing dependencies**: Run `npm install` in frontend directory
- **Build errors**: Check Node.js version and package.json

#### **Common Solutions:**
```bash
# Install backend dependencies
pip install fastapi uvicorn websockets pydantic

# Install frontend dependencies
cd frontend
npm install

# Check Python version
python3 --version

# Check Node.js version
node --version
npm --version
```

### **📊 Server Status Monitoring**

#### **Backend Health Check:**
```bash
curl http://localhost:8000/health
```

#### **Frontend Health Check:**
```bash
curl http://localhost:3000
```

#### **Process Monitoring:**
```bash
# Check running processes
ps aux | grep -E "(python|node)" | grep -v grep

# Check port usage
netstat -an | grep -E "(8000|3000)"
```

### **🛑 Stopping Servers**

#### **Manual Stop:**
- Press `Ctrl+C` in each terminal running the servers

#### **Automated Stop:**
- The `start_servers.py` script handles graceful shutdown

### **🎉 Expected Results**

#### **Successful Startup:**
- ✅ Backend server running on port 8000
- ✅ Frontend server running on port 3000
- ✅ No error messages in console
- ✅ Both servers respond to health checks
- ✅ Frontend loads in browser
- ✅ API endpoints accessible

#### **Frontend Interface:**
- Modern Material-UI design
- 7 functional panels in sidebar
- Real-time performance monitoring
- Responsive design
- Smooth animations
- Full accessibility support

#### **Backend API:**
- FastAPI with automatic documentation
- WebSocket support for real-time features
- CORS enabled for frontend integration
- Comprehensive error handling
- Health monitoring endpoints

### **🚀 Production Deployment**

#### **Backend Production:**
```bash
# Use production ASGI server
pip install gunicorn
gunicorn api_server:app -w 4 -k uvicorn.workers.UvicornWorker
```

#### **Frontend Production:**
```bash
cd frontend
npm run build
npm start
```

### **📈 Performance Expectations**

#### **Backend Performance:**
- Response time: < 200ms for most endpoints
- Chat response: < 2 seconds
- WebSocket latency: < 100ms
- Memory usage: < 500MB

#### **Frontend Performance:**
- Initial load: < 2 seconds
- Panel switching: < 300ms
- Chat message: < 500ms
- Animation smoothness: 60fps

### **🔐 Security Considerations**

#### **Development:**
- CORS enabled for localhost
- No authentication required
- Debug mode enabled

#### **Production:**
- Implement authentication
- Configure CORS properly
- Use HTTPS
- Enable rate limiting
- Add input validation

### **📝 Logs and Debugging**

#### **Backend Logs:**
- Console output shows request/response details
- Error messages include stack traces
- Performance metrics logged

#### **Frontend Logs:**
- Browser console shows client-side logs
- Network tab shows API requests
- Performance tab shows metrics

### **🎯 Next Steps**

1. **Start the servers** using the instructions above
2. **Test all features** in the frontend
3. **Verify API endpoints** work correctly
4. **Check performance** and responsiveness
5. **Test on different devices** and browsers
6. **Monitor logs** for any issues
7. **Enjoy the AI-powered experience!**

---

**🚀 Server Startup**: ✅ **READY TO LAUNCH**

The frontend and backend are ready to run with comprehensive features and excellent user experience!
