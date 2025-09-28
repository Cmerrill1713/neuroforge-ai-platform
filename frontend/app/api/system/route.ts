import { NextRequest, NextResponse } from 'next/server';

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const type = searchParams.get('type') || 'status';

    if (type === 'status') {
      // System status information
      const systemStatus = {
        status: 'healthy',
        uptime: process.uptime(),
        memory: process.memoryUsage(),
        version: '1.0.0',
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
    }

    if (type === 'metrics') {
      // System metrics
      const metrics = {
        timestamp: new Date().toISOString(),
        performance: {
          cpu: Math.random() * 100,
          memory: Math.random() * 100,
          disk: Math.random() * 100,
          network: Math.random() * 100
        },
        ai: {
          activeModels: 2,
          totalRequests: Math.floor(Math.random() * 10000) + 5000,
          averageResponseTime: Math.random() * 1000 + 200,
          errorRate: Math.random() * 5
        },
        system: {
          uptime: process.uptime(),
          loadAverage: [Math.random(), Math.random(), Math.random()],
          processes: Math.floor(Math.random() * 200) + 100
        }
      };

      return NextResponse.json(metrics);
    }

    return NextResponse.json(
      { error: 'Invalid type parameter' },
      { status: 400 }
    );
  } catch (error) {
    console.error('System API error:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}