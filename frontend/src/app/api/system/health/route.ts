import { NextRequest, NextResponse } from 'next/server'

const BACKEND_URL = process.env.NEXT_PUBLIC_CONSOLIDATED_API_URL || 'http://localhost:8004'

export async function GET() {
  try {
    const response = await fetch(`${BACKEND_URL}/api/system/health`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    })

    if (!response.ok) {
      throw new Error(`Backend responded with ${response.status}`)
    }

    const data = await response.json()
    return NextResponse.json(data)
  } catch (error) {
    console.error('Error fetching system health:', error)
    return NextResponse.json(
      { 
        status: 'unknown',
        version: 'unknown',
        error: error instanceof Error ? error.message : 'Unknown error',
        services: {
          consolidated_api: { status: 'down', port: 8004 },
          tts_server: { status: 'down', port: 8086 },
          whisper_server: { status: 'down', port: 8087 },
          ollama: { status: 'down', port: 11434 },
          mcp_server: { status: 'down', port: 8000 }
        }
      },
      { status: 200 }
    )
  }
}
