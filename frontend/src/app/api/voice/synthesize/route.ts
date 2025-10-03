import { NextRequest, NextResponse } from 'next/server'

const BACKEND_URL = process.env.NEXT_PUBLIC_CONSOLIDATED_API_URL || 'http://localhost:8004'

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    
    const response = await fetch(`${BACKEND_URL}/api/voice/synthesize`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
    })

    if (!response.ok) {
      throw new Error(`Backend responded with ${response.status}`)
    }

    // Return the audio blob directly
    const audioBlob = await response.blob()
    return new NextResponse(audioBlob, {
      headers: {
        'Content-Type': 'audio/wav',
      },
    })
  } catch (error) {
    console.error('Error synthesizing speech:', error)
    // Return empty WAV file on error
    const emptyWav = new Uint8Array([
      0x52, 0x49, 0x46, 0x46, 0x24, 0x00, 0x00, 0x00, 0x57, 0x41, 0x56, 0x45,
      0x66, 0x6D, 0x74, 0x20, 0x10, 0x00, 0x00, 0x00, 0x01, 0x00, 0x01, 0x00,
      0x44, 0xAC, 0x00, 0x00, 0x88, 0x58, 0x01, 0x00, 0x02, 0x00, 0x10, 0x00,
      0x64, 0x61, 0x74, 0x61, 0x00, 0x00, 0x00, 0x00
    ])
    return new NextResponse(emptyWav, {
      headers: {
        'Content-Type': 'audio/wav',
      },
    })
  }
}
