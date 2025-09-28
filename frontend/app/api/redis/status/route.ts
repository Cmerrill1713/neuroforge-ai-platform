import { NextResponse } from 'next/server'

// Redis functionality disabled to prevent connection errors
export async function GET() {
  return NextResponse.json({ 
    status: 'disabled', 
    message: 'Redis functionality disabled',
    stats: {
      keys: 0,
      memory: '0MB',
      ops: 0,
      hitRate: 0,
      connected: false,
      uptime: '0h'
    },
    timestamp: new Date().toISOString(),
    source: 'disabled'
  })
}