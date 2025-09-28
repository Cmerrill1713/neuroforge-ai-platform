import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { message, model, context, stream, conversationId } = body;

    if (!message) {
      return NextResponse.json(
        { error: 'Message is required' },
        { status: 400 }
      );
    }

    // Simulate AI response with enhanced features
    const selectedModel = model || 'qwen-7b';
    const responseTime = Math.random() * 1000 + 200; // 200-1200ms
    
    // Simulate task detection
    const detectedTask = message.toLowerCase().includes('code') ? 'coding' : 
                       message.toLowerCase().includes('debug') ? 'debugging' :
                       message.toLowerCase().includes('explain') ? 'explanation' : 'general';

    // Simulate context awareness
    const contextAware = Math.random() > 0.3; // 70% chance
    const semanticSearch = Math.random() > 0.5; // 50% chance
    
    const aiResponse = {
      response: `AI Response (${selectedModel}): I received your message "${message}". This is a simulated response with enhanced features including task detection, context awareness, and semantic search capabilities.`,
      selectedModel,
      timestamp: new Date().toISOString(),
      response_time: responseTime,
      tokens_used: Math.floor(Math.random() * 100) + 50,
      conversationId: conversationId || `conv_${Date.now()}`,
      messageId: `msg_${Date.now()}`,
      detectedTask,
      conversationPersisted: true,
      contextInfo: {
        systemAware: contextAware,
        knowledgeResults: semanticSearch ? Math.floor(Math.random() * 5) + 1 : 0,
        autoSwitchToCodeEditor: detectedTask === 'coding'
      },
      suggestedActions: [
        'Continue conversation',
        'Switch to code editor',
        'Search knowledge base',
        'Get system status'
      ],
      metadata: {
        model: selectedModel,
        responseTime,
        context,
        stream: stream || false
      }
    };

    return NextResponse.json(aiResponse);
  } catch (error) {
    console.error('AI Chat API error:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}