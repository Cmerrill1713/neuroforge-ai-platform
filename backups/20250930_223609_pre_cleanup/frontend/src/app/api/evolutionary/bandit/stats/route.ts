/**
 * Bandit Stats API Route
 * Returns Thompson sampling statistics
 */

import { NextResponse } from 'next/server'

export async function GET() {
  // Mock bandit stats for testing
  const stats = {
    "genome_1727795422_4567": {
      pulls: 847,
      mean_reward: 0.856,
      expected_value: 0.862
    },
    "genome_1727795423_8912": {
      pulls: 623,
      mean_reward: 0.834,
      expected_value: 0.841
    },
    "genome_1727795424_3456": {
      pulls: 412,
      mean_reward: 0.823,
      expected_value: 0.829
    },
    current_backend: "primary",
    execution_history_count: 1882
  }
  
  return NextResponse.json(stats)
}

