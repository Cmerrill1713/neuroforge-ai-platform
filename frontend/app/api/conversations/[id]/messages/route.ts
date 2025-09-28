import { NextRequest, NextResponse } from 'next/server'

// Reuse interfaces
interface Message {
  id: string
  conversation_id: string
  content: string
  sender: 'user' | 'ai'
  model?: string
  detected_task?: string
  feedback?: 'thumbs_up' | 'thumbs_down' | null
  created_at: string
  metadata?: any
}

// Simulated MCP Supabase operations
class MessageManager {
  async getMessages(conversationId: string, limit = 100): Promise<Message[]> {
    // In real implementation: call MCP Supabase select tool
    console.log('MCP Supabase: Retrieved messages for conversation', conversationId)
    
    // Return sample messages for demonstration
    return [
      {
        id: 'msg_1',
        conversation_id: conversationId,
        content: 'Hello! How can I help you today?',
        sender: 'user',
        created_at: new Date(Date.now() - 86400000).toISOString(),
        metadata: {}
      },
      {
        id: 'msg_2',
        conversation_id: conversationId,
        content: 'Hello! I\'m your AI assistant. I can help you with various tasks including coding, analysis, creative writing, and more. What would you like to work on?',
        sender: 'ai',
        model: 'qwen2.5:7b',
        detected_task: 'general',
        created_at: new Date(Date.now() - 86350000).toISOString(),
        metadata: { tokens: 45 }
      },
      {
        id: 'msg_3',
        conversation_id: conversationId,
        content: 'Can you help me write a React component?',
        sender: 'user',
        created_at: new Date(Date.now() - 86300000).toISOString(),
        metadata: {}
      },
      {
        id: 'msg_4',
        conversation_id: conversationId,
        content: 'Absolutely! I\'d be happy to help you create a React component. What kind of component do you need? For example:\n\n1. A simple functional component\n2. A component with state management\n3. A component with props\n4. A component with hooks\n\nLet me know what you\'re looking to build and I\'ll provide you with a complete example.',
        sender: 'ai',
        model: 'qwen2.5:7b',
        detected_task: 'coding',
        created_at: new Date(Date.now() - 86250000).toISOString(),
        metadata: { tokens: 78, intelligentSelection: true }
      }
    ]
  }

  async updateMessageFeedback(messageId: string, feedback: 'thumbs_up' | 'thumbs_down'): Promise<void> {
    // In real implementation: call MCP Supabase update tool
    console.log('MCP Supabase: Updated message feedback', messageId, feedback)
  }
}

const messageManager = new MessageManager()

// GET /api/conversations/[id]/messages - Get messages for a conversation
export async function GET(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const { searchParams } = new URL(request.url)
    const limit = parseInt(searchParams.get('limit') || '100')
    
    const messages = await messageManager.getMessages(params.id, limit)
    
    return NextResponse.json({
      status: 'success',
      data: messages,
      conversationId: params.id,
      count: messages.length
    })
  } catch (error) {
    console.error('Messages API error:', error)
    return NextResponse.json({
      error: 'Failed to retrieve messages',
      status: 'error',
      details: error instanceof Error ? error.message : 'Unknown error'
    }, { status: 500 })
  }
}

// PUT /api/conversations/[id]/messages - Update message feedback
export async function PUT(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const body = await request.json()
    const { messageId, feedback } = body
    
    if (!messageId || !feedback) {
      return NextResponse.json({
        error: 'Message ID and feedback are required',
        status: 'error'
      }, { status: 400 })
    }

    if (!['thumbs_up', 'thumbs_down'].includes(feedback)) {
      return NextResponse.json({
        error: 'Feedback must be either thumbs_up or thumbs_down',
        status: 'error'
      }, { status: 400 })
    }

    await messageManager.updateMessageFeedback(messageId, feedback)
    
    return NextResponse.json({
      status: 'success',
      message: 'Feedback updated successfully',
      data: { messageId, feedback }
    })
  } catch (error) {
    console.error('Update feedback API error:', error)
    return NextResponse.json({
      error: 'Failed to update feedback',
      status: 'error',
      details: error instanceof Error ? error.message : 'Unknown error'
    }, { status: 500 })
  }
}
