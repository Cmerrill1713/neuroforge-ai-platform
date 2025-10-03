import { NextRequest, NextResponse } from 'next/server'

const BACKEND_URL = process.env.NEXT_PUBLIC_CONSOLIDATED_API_URL || 'http://localhost:8004'

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    
    // Add validation for empty or invalid messages
    if (!body.message || typeof body.message !== 'string' || body.message.trim() === '') {
      return NextResponse.json(
        { 
          error: "Message is required and cannot be empty",
          response: "Please provide a valid message.",
          agent_used: "fallback",
          confidence: 0.0
        },
        { status: 400 }
      )
    }
    
    const response = await fetch(`${BACKEND_URL}/api/chat/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
    })

    if (!response.ok) {
      throw new Error(`Backend responded with ${response.status}`)
    }

    const data = await response.json()
    return NextResponse.json(data)
  } catch (error) {
    console.error('Error sending chat:', error)
    return NextResponse.json(
      { 
        response: "I'm sorry, I'm having trouble connecting to the AI service right now. Please try again later.",
        agent_used: "fallback",
        confidence: 0.0,
        error: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 500 }
    )
  }
}
