import { NextRequest, NextResponse } from 'next/server'
import { unifiedSystem } from '@/lib/unified-system'

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const { type, operation, parameters } = body
    
    if (!type || !operation) {
      return NextResponse.json({
        error: 'Type and operation are required',
        status: 'error'
      }, { status: 400 })
    }

    // Initialize unified system if not already done
    if (!unifiedSystem.isSystemInitialized()) {
      await unifiedSystem.initialize()
    }

    console.log(`🔧 Unified API: Processing ${type} operation - ${operation}`)
    
    // Create unified operation
    const unifiedOperation = {
      id: `unified_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`,
      type: type as 'chat' | 'system' | 'knowledge' | 'agent',
      operation,
      parameters,
      status: 'pending' as const,
      timestamp: new Date()
    }

    // Process the operation
    const result = await unifiedSystem.processOperation(unifiedOperation)

    return NextResponse.json({
      status: 'success',
      data: {
        operation: result,
        systemHealth: unifiedSystem.getSystemHealth(),
        timestamp: new Date().toISOString()
      }
    })

  } catch (error) {
    console.error('Unified API error:', error)
    return NextResponse.json({
      error: 'Internal server error',
      status: 'error',
      details: error instanceof Error ? error.message : 'Unknown error'
    }, { status: 500 })
  }
}

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url)
    const infoType = searchParams.get('type')
    
    // Initialize unified system if not already done
    if (!unifiedSystem.isSystemInitialized()) {
      await unifiedSystem.initialize()
    }

    if (infoType === 'health') {
      return NextResponse.json({
        status: 'success',
        data: {
          health: unifiedSystem.getSystemHealth(),
          timestamp: new Date().toISOString()
        }
      })
    } else if (infoType === 'operations') {
      return NextResponse.json({
        status: 'success',
        data: {
          operations: [],
          timestamp: new Date().toISOString()
        }
      })
    } else {
      return NextResponse.json({
        status: 'success',
        data: {
          systemHealth: unifiedSystem.getSystemHealth(),
          activeOperations: [],
          initialized: unifiedSystem.isSystemInitialized(),
          timestamp: new Date().toISOString()
        }
      })
    }

  } catch (error) {
    console.error('Unified status API error:', error)
    return NextResponse.json({
      error: 'Internal server error',
      status: 'error',
      details: error instanceof Error ? error.message : 'Unknown error'
    }, { status: 500 })
  }
}
