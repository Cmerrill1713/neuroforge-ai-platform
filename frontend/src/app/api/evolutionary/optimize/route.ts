/**
 * Evolutionary Optimization API Route
 * Proxies optimization requests to Python backend
 */

import { NextResponse } from 'next/server'

const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8005'

export async function POST(request: Request) {
  try {
    const body = await request.json()
    
    const response = await fetch(`${BACKEND_URL}/api/evolutionary/optimize`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
    })
    
    if (!response.ok) {
      throw new Error(`Backend returned ${response.status}`)
    }
    
    const data = await response.json()
    return NextResponse.json(data)
  } catch (error) {
    console.error('Error running optimization:', error)
    return NextResponse.json({
      success: false,
      error: 'Backend unavailable or optimization failed'
    }, { status: 503 })
  }
}

