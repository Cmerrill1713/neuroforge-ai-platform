/**
 * RAG Query API Route
 * Proxies hybrid retrieval search to Python backend
 */

import { NextResponse } from 'next/server'

const BACKEND_URL = process.env.BACKEND_URL || 'http://localhost:8005'

export async function POST(request: Request) {
  try {
    const body = await request.json()
    
    const response = await fetch(`${BACKEND_URL}/api/rag/query`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
      cache: 'no-store', // Disable caching to get fresh data
    })
    
    if (!response.ok) {
      throw new Error(`Backend returned ${response.status}`)
    }
    
    const data = await response.json()
    return NextResponse.json(data)
  } catch (error) {
    console.error('Error querying RAG:', error)
    
    // Fallback to empty results
    return NextResponse.json({
      query: "",
      results: [],
      latency_ms: 0,
      num_results: 0,
      retrieval_method: "hybrid",
      cache_hit: false,
      error: 'Backend unavailable'
    }, { status: 503 })
  }
}
