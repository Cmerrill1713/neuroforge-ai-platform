import { NextRequest, NextResponse } from 'next/server'
import { exec } from 'child_process'
import { promisify } from 'util'

const execAsync = promisify(exec)

export async function POST(request: NextRequest) {
  let body: any = null
  try {
    body = await request.json()
    const { question, context, step_by_step } = body

    if (!question) {
      return NextResponse.json({
        success: false,
        error: 'Question is required'
      }, { status: 400 })
    }

    // Create a Python script to run HRM reasoning
    const pythonScript = `
import sys
sys.path.append('/Users/christianmerrill/hrm-mlx')
from hrm_integration import HRMReasoningEngine
import json

# Create reasoning engine
engine = HRMReasoningEngine()

# Process reasoning
result = engine.reason_about_decision("${question.replace(/"/g, '\\"')}", "${context.replace(/"/g, '\\"')}")

# Output result as JSON
print(json.dumps(result))
`

    // Execute the Python script
    const { stdout, stderr } = await execAsync(`python3 -c "${pythonScript}"`)
    
    if (stderr) {
      console.error('Python script error:', stderr)
    }

    // Parse the result
    const result = JSON.parse(stdout.trim())
    
    return NextResponse.json(result)
  } catch (error) {
    console.error('HRM reasoning failed:', error)
    return NextResponse.json({
      success: false,
      error: error instanceof Error ? error.message : 'Unknown error',
      question: body?.question || '',
      context: body?.context || '',
      reasoning_steps: [],
      final_decision: '',
      confidence: 0,
      model: 'HRM-MLX'
    }, { status: 500 })
  }
}
