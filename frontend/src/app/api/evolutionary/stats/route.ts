/**
 * Evolutionary Optimizer Stats API Route
 * Proxies requests to Python backend
 */

import { NextResponse } from 'next/server'

const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8005'

export async function GET() {
  try {
    const response = await fetch(`${BACKEND_URL}/api/evolutionary/stats`, {
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
    console.error('Error fetching evolution stats:', error)
    // Fallback to mock data if backend unavailable
    return NextResponse.json({
      current_generation: 0,
      best_score: 0,
      mean_score: 0,
      population_size: 12,
      status: 'offline',
      error: 'Backend unavailable'
    }, { status: 503 })
  }
}

