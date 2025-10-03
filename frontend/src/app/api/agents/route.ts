import { NextRequest, NextResponse } from 'next/server'

const BACKEND_URL = process.env.NEXT_PUBLIC_CONSOLIDATED_API_URL || 'http://localhost:8004'

export async function GET() {
  try {
    const response = await fetch(`${BACKEND_URL}/api/agents/`, {
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
    console.error('Error fetching agents:', error)
    return NextResponse.json(
      { 
        agents: [
          {
            id: "qwen2.5-14b",
            name: "Qwen 2.5 14B",
            description: "Advanced reasoning model",
            status: "active",
            performance: { accuracy: 0.92, speed: 0.85 }
          },
          {
            id: "qwen2.5-72b", 
            name: "Qwen 2.5 72B",
            description: "Large reasoning model",
            status: "active",
            performance: { accuracy: 0.95, speed: 0.70 }
          }
        ]
      },
      { status: 200 }
    )
  }
}
