/**
 * Bandit Stats API Route
 * Proxies requests to Python backend
 */

import { NextResponse } from 'next/server'

const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8005'

export async function GET() {
  try {
    const response = await fetch(`${BACKEND_URL}/api/evolutionary/bandit/stats`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    })
    
    if (!response.ok) {
      throw new Error(`Backend returned ${response.status}`)
    }
    
    const data = await response.json()
    return NextResponse.json(data)
  } catch (error) {
    console.error('Error fetching bandit stats:', error)
    // Fallback to empty data if backend unavailable
    return NextResponse.json({
      genomes: {},
      current_backend: "unknown",
      execution_history_count: 0,
      error: 'Backend unavailable'
    }, { status: 503 })
  }
}

