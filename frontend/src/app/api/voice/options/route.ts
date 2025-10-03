import { NextRequest, NextResponse } from 'next/server'

const BACKEND_URL = process.env.NEXT_PUBLIC_CONSOLIDATED_API_URL || 'http://localhost:8004'

export async function GET() {
  try {
    const response = await fetch(`${BACKEND_URL}/api/voice/options`, {
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
    console.error('Error fetching voice options:', error)
    return NextResponse.json(
      { 
        voices: [
          { id: "sonia_clean", name: "Sonia Clean", description: "Smooth British female voice" },
          { id: "assistant", name: "Assistant", description: "Friendly assistant voice" }
        ],
        default: "sonia_clean",
        engines: ["chatterbox", "edge_tts"],
        status: "fallback"
      },
      { status: 200 }
    )
  }
}
