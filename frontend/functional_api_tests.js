#!/usr/bin/env node

/**
 * Functional API Test Script for NeuroForge Dual-Backend Architecture
 * Tests both Consolidated API (Port 8003) and Agentic Platform (Port 8000)
 */

const http = require('http');
const fs = require('fs');
const path = require('path');

// Dual-backend configuration
const BACKENDS = {
  consolidated: {
    name: 'Consolidated API',
    baseUrl: 'http://localhost:8003',
    endpoints: [
      { name: 'Health Check', endpoint: '/api/system/health', method: 'GET' },
      { name: 'Send Chat Message', endpoint: '/api/chat/', method: 'POST', body: { message: 'Hello from Consolidated API!' } },
      { name: 'Get Voice Options', endpoint: '/api/voice/options', method: 'GET' },
      { name: 'Synthesize Speech', endpoint: '/api/voice/synthesize', method: 'POST', body: { text: 'Hello from Consolidated API.', voice: 'chatterbox' } },
      { name: 'Get Vision Models', endpoint: '/api/vision/models', method: 'GET' },
      { name: 'Get Agents', endpoint: '/api/agents/', method: 'GET' },
      { name: 'Get Knowledge Stats', endpoint: '/api/knowledge/stats', method: 'GET' },
      { name: 'Search Knowledge', endpoint: '/api/knowledge/search', method: 'POST', body: { query: 'test' } }
    ]
  },
  agentic: {
    name: 'Agentic Platform',
    baseUrl: 'http://localhost:8000',
    endpoints: [
      { name: 'Health Check', endpoint: '/health', method: 'GET' },
      { name: 'Code Assistant', endpoint: '/code-assistant/assist', method: 'POST', body: { task_description: 'Create a simple console.log function', mode: 'code_generation', language: 'javascript' } },
      { name: 'Workflow Execute', endpoint: '/workflow/execute', method: 'POST', body: { workflow: 'test', data: {} } },
      { name: 'Knowledge Graph Stats', endpoint: '/knowledge-graph/stats', method: 'GET' },
      // { name: 'Embedding Search', endpoint: '/embedding/search', method: 'POST', body: { query: { query: 'test search' } } },
      { name: 'Vibe Coding Generate', endpoint: '/vibe-coding/generate', method: 'POST', body: { description: 'Create a simple function', style: 'clean_code' } },
      { name: 'Crawler Stats', endpoint: '/crawler/stats', method: 'GET' }
    ]
  }
};

// Utility function to make HTTP requests
function makeRequest(url, options = {}) {
  return new Promise((resolve, reject) => {
    const client = http;
    
    const req = client.request(url, {
      method: options.method || 'GET',
      headers: {
        'Content-Type': 'application/json',
        ...options.headers
      }
    }, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        try {
          const jsonData = data ? JSON.parse(data) : {};
          resolve({
            status: res.statusCode,
            headers: res.headers,
            data: jsonData,
            rawData: data
          });
        } catch (e) {
          resolve({
            status: res.statusCode,
            headers: res.headers,
            data: data,
            rawData: data
          });
        }
      });
    });

    req.on('error', reject);
    
    if (options.body) {
      req.write(JSON.stringify(options.body));
    }
    
    req.end();
  });
}

// Test individual endpoint
async function runTest(test, baseUrl) {
  const startTime = Date.now();
  
  try {
    const url = `${baseUrl}${test.endpoint}`;
    const response = await makeRequest(url, {
      method: test.method,
      body: test.body
    });
    
    const responseTime = Date.now() - startTime;
    
    return {
      success: response.status >= 200 && response.status < 300,
      status: response.status,
      responseTime,
      data: response.data
    };
  } catch (error) {
    return {
      success: false,
      error: error.message,
      responseTime: Date.now() - startTime
    };
  }
}

// Test file uploads (Consolidated API only)
async function testFileUploads() {
  console.log('📁 Testing file upload endpoints (Consolidated API):');
  
  let total = 0;
  let passed = 0;
  let failed = 0;
  
  // Test audio transcription
  total++;
  try {
    const audioPath = '/Users/christianmerrill/Prompt Engineering/frontend/test.wav';
    if (fs.existsSync(audioPath)) {
      const audioData = fs.readFileSync(audioPath);
      const response = await makeMultipartRequest(
        'http://localhost:8003/api/voice/transcribe',
        {},
        { file: { data: audioData, filename: 'test.wav', contentType: 'audio/wav' } }
      );
      
      if (response.status >= 200 && response.status < 300) {
        passed++;
        console.log(`  ✅ Transcribe Audio: ${response.status} - ${response.data?.transcription ? 'Success' : 'No transcription'}`);
      } else {
        failed++;
        console.log(`  ❌ Transcribe Audio: ${response.status} - ${response.data?.detail || 'Failed'}`);
      }
    } else {
      failed++;
      console.log(`  ❌ Transcribe Audio: Test file not found`);
    }
  } catch (error) {
    failed++;
    console.log(`  ❌ Transcribe Audio: ${error.message}`);
  }
  
  // Test image upload
  total++;
  try {
    const imagePath = '/Users/christianmerrill/Prompt Engineering/frontend/test.png';
    if (fs.existsSync(imagePath)) {
      const imageData = fs.readFileSync(imagePath);
      const response = await makeMultipartRequest(
        'http://localhost:8003/api/chat/upload',
        { message: 'Test message with image' },
        { file: { data: imageData, filename: 'test.png', contentType: 'image/png' } }
      );
      
      if (response.status >= 200 && response.status < 300) {
        passed++;
        console.log(`  ✅ Chat with Image: ${response.status} - ${response.data?.response ? 'Success' : 'No response'}`);
      } else {
        failed++;
        console.log(`  ❌ Chat with Image: ${response.status} - ${response.data?.detail || 'Failed'}`);
      }
    } else {
      failed++;
      console.log(`  ❌ Chat with Image: Test file not found`);
    }
  } catch (error) {
    failed++;
    console.log(`  ❌ Chat with Image: ${error.message}`);
  }
  
  return { total, passed, failed };
}

// Helper function for multipart requests
function makeMultipartRequest(url, fields = {}, files = {}) {
  return new Promise((resolve, reject) => {
    const boundary = '----formdata-' + Math.random().toString(36);
    const urlObj = new URL(url);
    
    const postData = [];
    
    // Add regular fields
    for (const [key, value] of Object.entries(fields)) {
      postData.push(`--${boundary}\r\n`);
      postData.push(`Content-Disposition: form-data; name="${key}"\r\n`);
      postData.push(`\r\n`);
      postData.push(`${value}\r\n`);
    }
    
    // Add file fields
    for (const [key, file] of Object.entries(files)) {
      postData.push(`--${boundary}\r\n`);
      postData.push(`Content-Disposition: form-data; name="${key}"; filename="${file.filename}"\r\n`);
      postData.push(`Content-Type: ${file.contentType}\r\n`);
      postData.push(`\r\n`);
      postData.push(file.data);
      postData.push(`\r\n`);
    }
    
    postData.push(`--${boundary}--\r\n`);
    
    const body = Buffer.concat(postData.map(item => 
      Buffer.isBuffer(item) ? item : Buffer.from(item, 'utf8')
    ));
    
    const options = {
      hostname: urlObj.hostname,
      port: urlObj.port,
      path: urlObj.pathname + urlObj.search,
      method: 'POST',
      headers: {
        'Content-Type': `multipart/form-data; boundary=${boundary}`,
        'Content-Length': body.length
      }
    };
    
    const req = http.request(options, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        try {
          const jsonData = data ? JSON.parse(data) : {};
          resolve({
            status: res.statusCode,
            headers: res.headers,
            data: jsonData,
            rawData: data
          });
        } catch (e) {
          resolve({
            status: res.statusCode,
            headers: res.headers,
            data: data,
            rawData: data
          });
        }
      });
    });
    
    req.on('error', reject);
    req.write(body);
    req.end();
  });
}

// Main test execution
async function runTests() {
  console.log('🚀 Starting NeuroForge Dual-Backend Functional Tests...\n');
  
  let totalTests = 0;
  let passedTests = 0;
  let failedTests = 0;
  
  // Test each backend
  for (const [backendKey, backend] of Object.entries(BACKENDS)) {
    console.log(`🔧 Testing ${backend.name} (${backend.baseUrl}):`);
    
    for (const test of backend.endpoints) {
      totalTests++;
      const result = await runTest(test, backend.baseUrl);
      
      if (result.success) {
        passedTests++;
        console.log(`  ✅ ${test.name}: ${result.status} - ${result.responseTime}ms`);
      } else {
        failedTests++;
        console.log(`  ❌ ${test.name}: ${result.error}`);
      }
    }
    console.log('');
  }
  
  // Test file uploads on Consolidated API
  console.log('📁 Testing file upload endpoints (Consolidated API):');
  const uploadTests = await testFileUploads();
  totalTests += uploadTests.total;
  passedTests += uploadTests.passed;
  failedTests += uploadTests.failed;
  
  // Summary
  console.log('📊 Dual-Backend Test Summary:');
  console.log(`  Total Tests: ${totalTests}`);
  console.log(`  Passed: ${passedTests}`);
  console.log(`  Failed: ${failedTests}`);
  console.log(`  Success Rate: ${((passedTests / totalTests) * 100).toFixed(1)}%`);
  
  if (failedTests === 0) {
    console.log('\n🎉 All tests passed! NeuroForge dual-backend integration is working correctly.');
    console.log('   ✅ Consolidated API (Port 8003) - Chat, Voice, Vision, Agents');
    console.log('   ✅ Agentic Platform (Port 8000) - Code Assistant, Workflows, Knowledge Graph');
  } else {
    console.log(`\n⚠️  ${failedTests} test(s) failed. Check the backend implementations.`);
  }
}

// Run tests if called directly
if (require.main === module) {
  runTests().catch(console.error);
}