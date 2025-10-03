/**
 * Evolutionary Optimizer Stats API Route
 * Returns mock data for testing the frontend
 */

import { NextResponse } from 'next/server'

export async function GET() {
  // Mock data for frontend testing
  const stats = {
    current_generation: 3,
    best_score: 0.8456,
    mean_score: 0.7823,
    population_size: 12,
    status: 'idle'
  }
  
  return NextResponse.json(stats)
}

