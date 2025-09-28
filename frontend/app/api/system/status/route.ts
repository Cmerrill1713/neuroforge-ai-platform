import { NextResponse } from 'next/server'

export async function GET() {
  try {
    // Simulate Docker system status check
    const systemStatus = {
      docker: {
        connected: true,
        containers: [
          { name: 'agentic-platform', status: 'running', image: 'agentic-engineering-platform:latest' },
          { name: 'ollama', status: 'running', image: 'ollama/ollama:latest' },
          { name: 'postgres', status: 'running', image: 'postgres:15-alpine' },
          { name: 'redis', status: 'running', image: 'redis:7-alpine' },
          { name: 'nginx', status: 'running', image: 'nginx:alpine' }
        ],
        images: 15,
        volumes: 8,
        networks: 3
      },
      platform: {
        status: 'operational',
        components: {
          mcp_servers: { active: 10, total: 10, health: 'healthy' },
          knowledge_base: { documents: 20, indexed: true, searchable: true },
          ai_models: { local_models: 8, cloud_models: 0, ollama_connected: true },
          monitoring: { active: true, metrics_collected: true }
        }
      },
      services: {
        ollama: { status: 'running', port: 11434, models_loaded: 8 },
        database: { status: 'connected', type: 'postgresql', port: 5432 },
        cache: { status: 'connected', type: 'redis', port: 6379 },
        proxy: { status: 'running', type: 'nginx', port: 80 }
      },
      timestamp: new Date().toISOString(),
      uptime: '2h 15m 30s'
    }

    return NextResponse.json({
      success: true,
      data: systemStatus,
      message: 'System status retrieved successfully'
    })
  } catch (error) {
    return NextResponse.json({
      success: false,
      error: 'Failed to retrieve system status',
      details: error instanceof Error ? error.message : 'Unknown error'
    }, { status: 500 })
  }
}
