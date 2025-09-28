import { NextRequest, NextResponse } from 'next/server'
import { 
  treeWatcherAgent, 
  securityAgent, 
  codeQualityAgent, 
  masterAgent,
  type AgentResponse 
} from '@/lib/prompt-based-agents'
import { hrmReasoningService } from '@/lib/hrm-reasoning-service'
import { backgroundDevilsAdvocate } from '@/lib/background-devils-advocate'

// Available agents
const AGENTS = {
  'tree-watcher': treeWatcherAgent,
  'security': securityAgent,
  'quality': codeQualityAgent,
  'master': masterAgent
} as const

type AgentName = keyof typeof AGENTS

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const { agent, prompt, context } = body
    
    if (!agent || !prompt) {
      return NextResponse.json({
        error: 'Agent name and prompt are required',
        status: 'error'
      }, { status: 400 })
    }

    const agentName = agent as AgentName
    const selectedAgent = AGENTS[agentName]
    
    if (!selectedAgent) {
      return NextResponse.json({
        error: `Unknown agent: ${agent}. Available agents: ${Object.keys(AGENTS).join(', ')}`,
        status: 'error'
      }, { status: 400 })
    }

    console.log(`🤖 Processing agent request: ${agentName} - "${prompt}"`)
    
    // Check if this agent request requires hierarchical reasoning
    let reasoningResult = null
    if (hrmReasoningService.requiresHierarchicalReasoning(prompt)) {
      console.log('🧠 HRM Reasoning: Agent request requires hierarchical analysis')
      try {
        reasoningResult = await hrmReasoningService.reasonAboutDecision({
          question: prompt,
          context: context || '',
          step_by_step: true,
          max_steps: 5
        })
        console.log(`✅ HRM Reasoning completed in ${reasoningResult.processing_time}ms`)
      } catch (error) {
        console.warn('HRM Reasoning failed:', error)
      }
    }
    
    // Process the prompt with the selected agent
    const response: AgentResponse = await selectedAgent.processPrompt(prompt, context)
    
    // Background Devil's Advocate Analysis for Agent Response
    let devilsAdvocateResult = null
    try {
      console.log(`🎭 Background Devil's Advocate: Analyzing ${agentName} agent response...`)
      devilsAdvocateResult = await backgroundDevilsAdvocate.challengeAgentResponse(JSON.stringify(response.result), agentName)
      
      if (devilsAdvocateResult.challenges.length > 0) {
        console.log(`🎭 Devil's Advocate: Found ${devilsAdvocateResult.challenges.length} challenges for ${agentName} (${devilsAdvocateResult.overall_assessment.risk_level} risk)`)
        
        // Enhance the response with challenges if risk is medium or high
        if (devilsAdvocateResult.overall_assessment.risk_level !== 'LOW') {
          const enhancedResult = backgroundDevilsAdvocate.enhanceWithChallenges(JSON.stringify(response.result), devilsAdvocateResult.challenges)
          
          // Update the response with enhanced result
          response.result = JSON.parse(enhancedResult)
          
          // Store Devil's Advocate info in the response for the client
          const enhancedResponse = {
            ...response,
            devilsAdvocate: {
              originalResponse: response.result,
              challenges: devilsAdvocateResult.challenges,
              assessment: devilsAdvocateResult.overall_assessment
            }
          }
          
          return NextResponse.json({
            status: 'success',
            data: {
              agent: agentName,
              prompt,
              response: enhancedResponse,
              reasoning: reasoningResult,
              timestamp: new Date().toISOString()
            }
          })
        }
      } else {
        console.log(`🎭 Devil's Advocate: No significant challenges found for ${agentName}`)
      }
    } catch (error) {
      console.warn(`Devil's Advocate analysis failed for ${agentName}:`, error)
    }
    
    // Add Devil's Advocate info to the response
    const finalResponse = {
      ...response,
      devilsAdvocate: devilsAdvocateResult ? {
        originalResponse: response.result,
        challenges: devilsAdvocateResult.challenges,
        assessment: devilsAdvocateResult.overall_assessment
      } : null
    }

    return NextResponse.json({
      status: 'success',
      data: {
        agent: agentName,
        prompt,
        response: finalResponse,
        reasoning: reasoningResult,
        timestamp: new Date().toISOString()
      }
    })

  } catch (error) {
    console.error('Agent API error:', error)
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
    const agentName = searchParams.get('agent') as AgentName
    
    if (agentName && AGENTS[agentName]) {
      // Get status of specific agent
      const agent = AGENTS[agentName]
      return NextResponse.json({
        status: 'success',
        data: {
          agent: agentName,
          status: agent.getStatus()
        }
      })
    } else {
      // Get status of all agents
      const allStatuses = Object.entries(AGENTS).map(([name, agent]) => ({
        name,
        status: agent.getStatus()
      }))
      
      return NextResponse.json({
        status: 'success',
        data: {
          agents: allStatuses,
          totalAgents: allStatuses.length,
          activeAgents: allStatuses.filter(a => a.status.isActive).length
        }
      })
    }

  } catch (error) {
    console.error('Agent status API error:', error)
    return NextResponse.json({
      error: 'Internal server error',
      status: 'error',
      details: error instanceof Error ? error.message : 'Unknown error'
    }, { status: 500 })
  }
}

export async function PUT(request: NextRequest) {
  try {
    const body = await request.json()
    const { agent, action } = body
    
    if (!agent || !action) {
      return NextResponse.json({
        error: 'Agent name and action are required',
        status: 'error'
      }, { status: 400 })
    }

    const agentName = agent as AgentName
    const selectedAgent = AGENTS[agentName]
    
    if (!selectedAgent) {
      return NextResponse.json({
        error: `Unknown agent: ${agent}`,
        status: 'error'
      }, { status: 400 })
    }

    let result: any = {}

    switch (action) {
      case 'activate':
        selectedAgent.activate()
        result = { message: `${agentName} activated`, status: 'active' }
        break
      
      case 'deactivate':
        selectedAgent.deactivate()
        result = { message: `${agentName} deactivated`, status: 'inactive' }
        break
      
      case 'activate-all':
        masterAgent.activateAll()
        result = { message: 'All agents activated', status: 'all_active' }
        break
      
      case 'deactivate-all':
        masterAgent.deactivateAll()
        result = { message: 'All agents deactivated', status: 'all_inactive' }
        break
      
      default:
        return NextResponse.json({
          error: `Unknown action: ${action}. Available actions: activate, deactivate, activate-all, deactivate-all`,
          status: 'error'
        }, { status: 400 })
    }

    return NextResponse.json({
      status: 'success',
      data: {
        agent: agentName,
        action,
        result,
        timestamp: new Date().toISOString()
      }
    })

  } catch (error) {
    console.error('Agent control API error:', error)
    return NextResponse.json({
      error: 'Internal server error',
      status: 'error',
      details: error instanceof Error ? error.message : 'Unknown error'
    }, { status: 500 })
  }
}
