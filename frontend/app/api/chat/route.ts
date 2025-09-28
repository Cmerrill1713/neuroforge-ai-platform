import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { message, model } = body;

    if (!message) {
      return NextResponse.json(
        { error: 'Message is required' },
        { status: 400 }
      );
    }

    // Connect to real backend AI
    const backendResponse = await fetch('http://localhost:8002/api/chat', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        message: message,
        task_type: body.task_type || 'text_generation',
        latency_requirement: body.latency_requirement || 1000,
        input_type: body.input_type || 'text',
        max_tokens: body.max_tokens || 1024,
        temperature: body.temperature || 0.7
      }),
    });

    if (!backendResponse.ok) {
      throw new Error(`Backend API error: ${backendResponse.status}`);
    }

    const backendData = await backendResponse.json();
    
    // Generate speech using production TTS server
    let audioFile = null;
    try {
              const ttsResponse = await fetch('http://localhost:8086/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          text: backendData.message,
          voice_profile: 'assistant',
          emotion: 'neutral',
          speed: 'normal',
          output_file: `chat_audio_${Date.now()}.mp3`
        }),
      });

      if (ttsResponse.ok) {
        const ttsData = await ttsResponse.json();
        audioFile = ttsData.output_file;
        console.log(`✅ TTS generated: ${audioFile}`);
      } else {
        console.warn(`⚠️ TTS failed: ${ttsResponse.status}`);
      }
    } catch (ttsError) {
      console.warn('⚠️ TTS error:', ttsError);
    }
    
    const aiResponse = {
      id: Date.now().toString(),
      content: backendData.message,
      sender: 'assistant' as const,
      timestamp: new Date().toISOString(),
      model: backendData.agent || 'default',
      audioFile: audioFile, // Include audio file path
      metadata: {
        responseTime: backendData.timestamp || Date.now(),
        tokens: 0,
        agent: backendData.agent,
        confidence: 1.0,
        complexity: 'medium',
        ttsGenerated: !!audioFile
      }
    };

    return NextResponse.json(aiResponse);
  } catch (error) {
    console.error('Chat API error:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const limit = parseInt(searchParams.get('limit') || '50');

    // Simulate chat history (replace with actual database query)
    const chatHistory = [
      {
        id: '1',
        content: 'Hello! How can I help you today?',
        sender: 'assistant' as const,
        timestamp: new Date(Date.now() - 60000).toISOString(),
        model: 'default',
      },
      {
        id: '2',
        content: 'Welcome to the AI Assistant system!',
        sender: 'assistant' as const,
        timestamp: new Date(Date.now() - 30000).toISOString(),
        model: 'default',
      }
    ];

    return NextResponse.json(chatHistory.slice(0, limit));
  } catch (error) {
    console.error('Chat history API error:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}
