import { NextRequest, NextResponse } from 'next/server'
import { learningSystem } from '@/lib/learning-system'

interface FeedbackData {
  messageId: string
  feedback: 'thumbs_up' | 'thumbs_down'
  message: string
  model: string
  detectedTask: string
  timestamp: string
}

interface ConversationAnalysis {
  quality: number
  issues: string[]
  improvements: string[]
  modelSuggestion?: string
  taskAccuracy: number
}

// Analyze conversation quality and identify issues
function analyzeConversation(feedbackData: FeedbackData): ConversationAnalysis {
  const { messageId, feedback, message, model, detectedTask } = feedbackData
  
  let analysis: ConversationAnalysis = {
    quality: 0.5,
    issues: [],
    improvements: [],
    taskAccuracy: 0.5
  }

  if (feedback === 'thumbs_up') {
    // Positive feedback - analyze what went well
    analysis.quality = 0.9
    
    // Analyze successful patterns
    const successFactors = []
    
    if (message.toLowerCase().includes('code') && model.includes('codellama')) {
      successFactors.push('Correct model selection for coding task')
    }
    
    if (message.toLowerCase().includes('analyze') && model.includes('llama3.1')) {
      successFactors.push('Correct model selection for analysis task')
    }
    
    if (message.toLowerCase().includes('docker') && model.includes('phi3')) {
      successFactors.push('Correct model selection for system task')
    }
    
    analysis.improvements = successFactors
    analysis.taskAccuracy = 0.95
    
  } else if (feedback === 'thumbs_down') {
    // Negative feedback - identify issues and suggest fixes
    analysis.quality = 0.2
    
    // Identify potential issues
    const issues = []
    
    // Check for model-task mismatch (using available models)
    if (message.toLowerCase().includes('code') && !model.includes('qwen2.5:7b')) {
      issues.push('Model-task mismatch: Coding task not assigned to Qwen 2.5 7B')
      analysis.modelSuggestion = 'qwen2.5:7b'
    }
    
    if (message.toLowerCase().includes('analyze') && !model.includes('qwen2.5:14b')) {
      issues.push('Model-task mismatch: Analysis task not assigned to Qwen 2.5 14B')
      analysis.modelSuggestion = 'qwen2.5:14b'
    }
    
    if (message.toLowerCase().includes('docker') && !model.includes('llama3.2:3b')) {
      issues.push('Model-task mismatch: System task not assigned to Llama 3.2 3B')
      analysis.modelSuggestion = 'llama3.2:3b'
    }
    
    // Check for response quality issues
    if (message.length < 50) {
      issues.push('Response too brief - may need more detailed explanation')
    }
    
    if (!message.includes('.')) {
      issues.push('Response lacks proper sentence structure')
    }
    
    // Check for task detection accuracy
    const taskKeywords = {
      'coding': ['code', 'programming', 'function', 'api', 'bug', 'debug', 'git'],
      'analysis': ['analyze', 'explain', 'compare', 'evaluate', 'reasoning'],
      'system': ['docker', 'deploy', 'server', 'infrastructure', 'monitoring'],
      'multimodal': ['image', 'picture', 'visual', 'photo'],
      'creative': ['write', 'story', 'creative', 'poem']
    }
    
    const detectedKeywords = taskKeywords[detectedTask as keyof typeof taskKeywords] || []
    const messageLower = message.toLowerCase()
    const keywordMatches = detectedKeywords.filter(keyword => messageLower.includes(keyword))
    
    if (keywordMatches.length === 0 && detectedTask !== 'general') {
      issues.push('Task detection may be inaccurate - no relevant keywords found')
      analysis.taskAccuracy = 0.3
    } else {
      analysis.taskAccuracy = keywordMatches.length / detectedKeywords.length
    }
    
    analysis.issues = issues
    
    // Generate improvement suggestions
    const improvements = []
    
    if (analysis.modelSuggestion) {
      improvements.push(`Switch to ${analysis.modelSuggestion} for better performance`)
    }
    
    if (analysis.taskAccuracy < 0.5) {
      improvements.push('Improve task detection algorithm')
    }
    
    if (issues.some(issue => issue.includes('brief'))) {
      improvements.push('Generate more comprehensive responses')
    }
    
    analysis.improvements = improvements
  }
  
  return analysis
}

export async function POST(request: NextRequest) {
  try {
    const feedbackData: FeedbackData = await request.json()
    
    // Validate input
    if (!feedbackData.messageId || !feedbackData.feedback || !feedbackData.message) {
      return NextResponse.json({
        error: 'Missing required fields',
        status: 'error'
      }, { status: 400 })
    }
    
    // Analyze the feedback
    const analysis = analyzeConversation(feedbackData)
    
    // Store feedback for learning (in a real system, this would go to a database)
    const feedbackRecord = {
      ...feedbackData,
      analysis,
      timestamp: new Date().toISOString()
    }
    
    // In a production system, you would:
    // 1. Store this in a database
    // 2. Update model selection algorithms
    // 3. Train on feedback patterns
    // 4. Adjust task detection rules
    
    console.log('Feedback Analysis:', JSON.stringify(feedbackRecord, null, 2))
    
    // Process feedback through learning system
    await learningSystem.processFeedback({
      messageId: feedbackData.messageId,
      conversationId: 'unknown',
      feedback: feedbackData.feedback,
      model: feedbackData.model || 'unknown',
      detectedTask: feedbackData.detectedTask || 'unknown',
      userMessage: feedbackData.message || 'User message',
      aiResponse: 'AI response' // Would be retrieved from conversation
    })
    
    return NextResponse.json({
      status: 'success',
      data: {
        analysis,
        improvements: analysis.improvements,
        nextActions: feedbackData.feedback === 'thumbs_down' ? analysis.improvements : ['Continue current approach'],
        learningApplied: true
      }
    })
    
  } catch (error) {
    console.error('Feedback analysis error:', error)
    return NextResponse.json({
      error: 'Failed to analyze feedback',
      status: 'error'
    }, { status: 500 })
  }
}
