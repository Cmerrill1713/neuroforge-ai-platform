import { NextRequest, NextResponse } from 'next/server'
import { selfOptimizationSystem } from '@/lib/self-optimization-system'

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url)
    const type = searchParams.get('type') || 'all'
    
    console.log(`🔧 Self-Optimization API: Getting data - ${type}`)
    
    switch (type) {
      case 'tasks':
        const allTasks = selfOptimizationSystem.getAllTasks()
        return NextResponse.json({
          status: 'success',
          data: { tasks: allTasks }
        })

      case 'active':
        const activeTasks = selfOptimizationSystem.getActiveTasks()
        return NextResponse.json({
          status: 'success',
          data: { tasks: activeTasks }
        })

      case 'completed':
        const completedTasks = selfOptimizationSystem.getAllTasks().filter(task => task.status === 'completed')
        return NextResponse.json({
          status: 'success',
          data: { tasks: completedTasks }
        })

      case 'status':
        const allTasksStatus = selfOptimizationSystem.getAllTasks()
        const activeTasksStatus = selfOptimizationSystem.getActiveTasks()
        
        return NextResponse.json({
          status: 'success',
          data: {
            totalTasks: allTasksStatus.length,
            activeTasks: activeTasksStatus.length,
            completedTasks: allTasksStatus.filter(t => t.status === 'completed').length,
            failedTasks: allTasksStatus.filter(t => t.status === 'failed').length,
            systemStatus: 'operational'
          }
        })

      case 'all':
      default:
        // Return all data
        const allTasksDefault = selfOptimizationSystem.getAllTasks()
        const activeTasksDefault = selfOptimizationSystem.getActiveTasks()
        
        return NextResponse.json({
          status: 'success',
          data: {
            tasks: allTasksDefault,
            activeTasks: activeTasksDefault,
            summary: {
              total: allTasksDefault.length,
              active: activeTasksDefault.length,
              completed: allTasksDefault.filter(t => t.status === 'completed').length,
              failed: allTasksDefault.filter(t => t.status === 'failed').length
            }
          }
        })
    }

  } catch (error: unknown) {
    const errorMessage = error instanceof Error ? error.message : 'Unknown error'
    console.error('❌ Self-Optimization API Error:', errorMessage)
    
    return NextResponse.json({
      error: errorMessage,
      status: 'error'
    }, { status: 500 })
  }
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const { action, ...params } = body

    if (!action) {
      return NextResponse.json({
        error: 'Action is required',
        status: 'error'
      }, { status: 400 })
    }

    console.log(`🔧 Self-Optimization API: Processing action - ${action}`)

    switch (action) {
      case 'create_task':
        const { description, requirements, constraints, successCriteria, maxIterations } = params
        
        if (!description || !requirements || !Array.isArray(requirements)) {
          return NextResponse.json({
            error: 'Description and requirements are required',
            status: 'error'
          }, { status: 400 })
        }

        const task = await selfOptimizationSystem.createOptimizationTask(
          description,
          requirements,
          constraints || [],
          successCriteria || [],
          maxIterations || 10
        )

        return NextResponse.json({
          status: 'success',
          data: { task },
          message: 'Optimization task created successfully'
        })

      case 'execute_task':
        const { taskId } = params
        
        if (!taskId) {
          return NextResponse.json({
            error: 'Task ID is required',
            status: 'error'
          }, { status: 400 })
        }

        const executedTask = await selfOptimizationSystem.executeOptimizationTask(taskId)

        return NextResponse.json({
          status: 'success',
          data: { task: executedTask },
          message: 'Optimization task executed successfully'
        })

      case 'get_task':
        const { taskId: getTaskId } = params
        
        if (!getTaskId) {
          return NextResponse.json({
            error: 'Task ID is required',
            status: 'error'
          }, { status: 400 })
        }

        const retrievedTask = selfOptimizationSystem.getTask(getTaskId)
        
        if (!retrievedTask) {
          return NextResponse.json({
            error: 'Task not found',
            status: 'error'
          }, { status: 404 })
        }

        return NextResponse.json({
          status: 'success',
          data: { task: retrievedTask }
        })

      case 'cleanup':
        await selfOptimizationSystem.cleanupSandbox()
        
        return NextResponse.json({
          status: 'success',
          message: 'Sandbox cleaned up successfully'
        })

      default:
        return NextResponse.json({
          error: `Unknown action: ${action}`,
          status: 'error'
        }, { status: 400 })
    }

  } catch (error) {
    console.error('Self-Optimization API error:', error)
    return NextResponse.json({
      error: 'Internal server error',
      status: 'error',
      details: error instanceof Error ? error.message : 'Unknown error'
    }, { status: 500 })
  }
}

