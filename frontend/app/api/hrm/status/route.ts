import { NextRequest, NextResponse } from 'next/server'
import { exec } from 'child_process'
import { promisify } from 'util'

const execAsync = promisify(exec)

export async function GET(request: NextRequest) {
  try {
    // Check if HRM-MLX is available
    const { stdout } = await execAsync('python3 -c "import sys; sys.path.append(\'/Users/christianmerrill/hrm-mlx\'); from models.hrm.hrm_act_v1 import HierarchicalReasoningModel; print(\'HRM-MLX available\')"')
    
    return NextResponse.json({
      status: 'ready',
      model: 'HRM-MLX',
      message: 'Hierarchical Reasoning Model is available',
      capabilities: [
        'Chain-of-thought reasoning',
        'Hierarchical decision trees',
        'Multi-step planning',
        'Alternative exploration',
        'Adaptive computation'
      ]
    })
  } catch (error) {
    console.error('HRM status check failed:', error)
    return NextResponse.json({
      status: 'error',
      model: 'HRM-MLX',
      message: 'HRM-MLX is not available',
      error: error instanceof Error ? error.message : 'Unknown error'
    }, { status: 500 })
  }
}
