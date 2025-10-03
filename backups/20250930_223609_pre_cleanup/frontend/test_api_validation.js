#!/usr/bin/env node

/**
 * Complete API Validation Script
 * Tests all endpoints and features of the AI Chat System
 */

const https = require('https');
const http = require('http');

const BASE_URL = 'http://localhost:3000';
const OLLAMA_URL = 'http://localhost:11434';

// Test configuration
const TESTS = {
  ollama: [
    { name: 'Ollama Health Check', endpoint: '/api/tags', method: 'GET' },
    { name: 'Ollama Model Test', endpoint: '/api/generate', method: 'POST', body: { model: 'qwen2.5:7b', prompt: 'Hello test', stream: false } }
  ],
  chat: [
    { name: 'General Chat Test', body: { message: 'Hello, test message', conversationId: 'test-general', customModelName: 'TestAI' } },
    { name: 'Coding Task Test', body: { message: 'Write a Python function to calculate fibonacci', conversationId: 'test-coding', customModelName: 'CodeAI' } },
    { name: 'Analysis Task Test', body: { message: 'Analyze this complex problem and provide reasoning', conversationId: 'test-analysis', customModelName: 'AnalystAI' } },
    { name: 'System Task Test', body: { message: 'Help me deploy this Docker container to production', conversationId: 'test-system', customModelName: 'DevOpsAI' } },
    { name: 'Multimodal Task Test', body: { message: 'Describe this image and analyze its contents', conversationId: 'test-multimodal', customModelName: 'VisionAI' } }
  ],
  feedback: [
    { name: 'Positive Feedback Test', body: { messageId: 'test-123', feedback: 'thumbs_up', message: 'Hello, test the chat API', model: 'qwen2.5:7b', detectedTask: 'coding', timestamp: '2025-09-27T06:15:26.035Z' } },
    { name: 'Negative Feedback Test', body: { messageId: 'test-456', feedback: 'thumbs_down', message: 'Write some code for me', model: 'llama3.2:3b', detectedTask: 'system', timestamp: '2025-09-27T06:15:26.035Z' } }
  ],
  frontend: [
    { name: 'Frontend Health Check', endpoint: '/', method: 'GET' },
    { name: 'Static Assets Check', endpoint: '/_next/static/css/app/layout.css', method: 'GET' }
  ]
};

// Utility function to make HTTP requests
function makeRequest(url, options = {}) {
  return new Promise((resolve, reject) => {
    const client = url.startsWith('https:') ? https : http;
    
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
          const parsedData = res.headers['content-type']?.includes('application/json') ? JSON.parse(data) : data;
          resolve({
            status: res.statusCode,
            headers: res.headers,
            data: parsedData,
            raw: data
          });
        } catch (e) {
          resolve({
            status: res.statusCode,
            headers: res.headers,
            data: data,
            raw: data
          });
        }
      });
    });

    req.on('error', reject);

    if (options.body) {
      req.write(typeof options.body === 'string' ? options.body : JSON.stringify(options.body));
    }

    req.end();
  });
}

// Test runner
async function runTest(category, test) {
  try {
    console.log(`\n🧪 Testing: ${test.name}`);
    console.log(`   Category: ${category}`);
    
    let url, options = {};
    
    if (category === 'ollama') {
      url = `${OLLAMA_URL}${test.endpoint}`;
      options.method = test.method;
      if (test.body) options.body = test.body;
    } else if (category === 'chat') {
      url = `${BASE_URL}/api/ai/chat`;
      options.method = 'POST';
      options.body = test.body;
    } else if (category === 'feedback') {
      url = `${BASE_URL}/api/feedback/analyze`;
      options.method = 'POST';
      options.body = test.body;
    } else if (category === 'frontend') {
      url = `${BASE_URL}${test.endpoint}`;
      options.method = test.method;
    }

    const startTime = Date.now();
    const response = await makeRequest(url, options);
    const duration = Date.now() - startTime;

    // Analyze response
    const isSuccess = response.status >= 200 && response.status < 300;
    const status = isSuccess ? '✅ PASS' : '❌ FAIL';
    
    console.log(`   Status: ${status} (${response.status})`);
    console.log(`   Duration: ${duration}ms`);
    
    if (category === 'chat' && isSuccess) {
      console.log(`   Model: ${response.data?.data?.model || 'Unknown'}`);
      console.log(`   Task: ${response.data?.data?.detectedTask || 'Unknown'}`);
      console.log(`   Response Length: ${response.data?.data?.message?.length || 0} chars`);
    }
    
    if (category === 'feedback' && isSuccess) {
      console.log(`   Quality Score: ${response.data?.data?.analysis?.quality || 'Unknown'}`);
      console.log(`   Issues Found: ${response.data?.data?.analysis?.issues?.length || 0}`);
      console.log(`   Improvements: ${response.data?.data?.analysis?.improvements?.length || 0}`);
    }

    if (!isSuccess) {
      console.log(`   Error: ${response.data?.error || response.data || 'Unknown error'}`);
    }

    return { success: isSuccess, duration, response };

  } catch (error) {
    console.log(`   Status: ❌ ERROR`);
    console.log(`   Error: ${error.message}`);
    return { success: false, error: error.message };
  }
}

// Main validation function
async function runValidation() {
  console.log('🔍 COMPLETE API VALIDATION STARTING');
  console.log('====================================');
  console.log(`Base URL: ${BASE_URL}`);
  console.log(`Ollama URL: ${OLLAMA_URL}`);
  console.log(`Timestamp: ${new Date().toISOString()}`);

  const results = {
    total: 0,
    passed: 0,
    failed: 0,
    errors: 0,
    categories: {}
  };

  // Run all tests
  for (const [category, tests] of Object.entries(TESTS)) {
    console.log(`\n📂 Testing Category: ${category.toUpperCase()}`);
    console.log('=' + '='.repeat(30));
    
    results.categories[category] = { total: tests.length, passed: 0, failed: 0, errors: 0 };
    
    for (const test of tests) {
      results.total++;
      results.categories[category].total++;
      
      const result = await runTest(category, test);
      
      if (result.success) {
        results.passed++;
        results.categories[category].passed++;
      } else if (result.error) {
        results.errors++;
        results.categories[category].errors++;
      } else {
        results.failed++;
        results.categories[category].failed++;
      }
      
      // Small delay between tests
      await new Promise(resolve => setTimeout(resolve, 100));
    }
  }

  // Print summary
  console.log('\n📊 VALIDATION SUMMARY');
  console.log('====================');
  console.log(`Total Tests: ${results.total}`);
  console.log(`✅ Passed: ${results.passed}`);
  console.log(`❌ Failed: ${results.failed}`);
  console.log(`⚠️  Errors: ${results.errors}`);
  console.log(`Success Rate: ${((results.passed / results.total) * 100).toFixed(1)}%`);

  console.log('\n📋 Category Breakdown:');
  for (const [category, stats] of Object.entries(results.categories)) {
    const rate = ((stats.passed / stats.total) * 100).toFixed(1);
    console.log(`   ${category}: ${stats.passed}/${stats.total} (${rate}%)`);
  }

  // Overall status
  const overallSuccess = results.failed === 0 && results.errors === 0;
  console.log(`\n🎯 Overall Status: ${overallSuccess ? '✅ ALL SYSTEMS OPERATIONAL' : '❌ ISSUES DETECTED'}`);
  
  if (overallSuccess) {
    console.log('\n🚀 SYSTEM READY FOR PRODUCTION!');
    console.log('   - All APIs responding correctly');
    console.log('   - Ollama integration working');
    console.log('   - Chat system functional');
    console.log('   - Feedback system operational');
    console.log('   - Frontend serving correctly');
  } else {
    console.log('\n🔧 ISSUES TO ADDRESS:');
    if (results.failed > 0) {
      console.log(`   - ${results.failed} tests failed (check API responses)`);
    }
    if (results.errors > 0) {
      console.log(`   - ${results.errors} tests errored (check connectivity)`);
    }
  }

  return results;
}

// Run validation if called directly
if (require.main === module) {
  runValidation().catch(console.error);
}

module.exports = { runValidation, TESTS };
