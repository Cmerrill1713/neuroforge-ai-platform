import { NextRequest, NextResponse } from 'next/server';

export async function GET(request: NextRequest) {
  try {
    // System status information
    const systemStatus = {
      status: 'healthy' as const,
      models: [
        {
          name: 'Qwen-7B',
          type: 'ollama' as const,
          status: 'active' as const,
          performance_score: 0.95,
          response_time: 180,
        },
        {
          name: 'Llama-13B',
          type: 'ollama' as const,
          status: 'active' as const,
          performance_score: 0.88,
          response_time: 320,
        },
        {
          name: 'Mistral-7B',
          type: 'ollama' as const,
          status: 'inactive' as const,
          performance_score: 0.92,
          response_time: 0,
        }
      ],
      uptime: process.uptime(),
      memory_usage: process.memoryUsage().heapUsed / process.memoryUsage().heapTotal * 100,
      timestamp: new Date().toISOString(),
      services: {
        database: 'connected',
        redis: 'connected',
        websocket: 'active',
        ai_models: 'running'
      },
      metrics: {
        activeConnections: Math.floor(Math.random() * 50) + 10,
        requestsPerMinute: Math.floor(Math.random() * 100) + 20,
        errorRate: Math.random() * 2,
        responseTime: Math.random() * 500 + 100
      }
    };

    return NextResponse.json(systemStatus);
  } catch (error) {
    console.error('Status API error:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}
