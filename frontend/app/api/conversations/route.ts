import { NextRequest, NextResponse } from 'next/server'

// Reuse the same interfaces and manager from chat route
interface Conversation {
  id: string
  title: string
  created_at: string
  updated_at: string
  metadata?: any
}

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
class ConversationManager {
  async getConversations(limit = 50): Promise<Conversation[]> {
    // In real implementation: call MCP Supabase select tool
    console.log('MCP Supabase: Retrieved conversations list')
    return [
      {
        id: 'conv_sample_1',
        title: 'Welcome Conversation',
        created_at: new Date(Date.now() - 86400000).toISOString(), // 1 day ago
        updated_at: new Date(Date.now() - 3600000).toISOString(), // 1 hour ago
        metadata: { task_type: 'general', message_count: 5 }
      },
      {
        id: 'conv_sample_2', 
        title: 'Coding Session',
        created_at: new Date(Date.now() - 172800000).toISOString(), // 2 days ago
        updated_at: new Date(Date.now() - 7200000).toISOString(), // 2 hours ago
        metadata: { task_type: 'coding', message_count: 12 }
      }
    ]
  }

  async getConversation(id: string): Promise<Conversation | null> {
    // In real implementation: call MCP Supabase select tool
    console.log('MCP Supabase: Retrieved conversation', id)
    return {
      id,
      title: 'Sample Conversation',
      created_at: new Date(Date.now() - 86400000).toISOString(),
      updated_at: new Date().toISOString(),
      metadata: { task_type: 'general', message_count: 5 }
    }
  }

  async getMessages(conversationId: string, limit = 100): Promise<Message[]> {
    // In real implementation: call MCP Supabase select tool
    console.log('MCP Supabase: Retrieved messages for conversation', conversationId)
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
      }
    ]
  }
}

const conversationManager = new ConversationManager()

// GET /api/conversations - List all conversations
export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url)
    const limit = parseInt(searchParams.get('limit') || '50')
    
    const conversations = await conversationManager.getConversations(limit)
    
    return NextResponse.json({
      status: 'success',
      data: conversations,
      count: conversations.length
    })
  } catch (error) {
    console.error('Conversations API error:', error)
    return NextResponse.json({
      error: 'Failed to retrieve conversations',
      status: 'error',
      details: error instanceof Error ? error.message : 'Unknown error'
    }, { status: 500 })
  }
}

// POST /api/conversations - Create new conversation
export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const { title, metadata } = body
    
    if (!title) {
      return NextResponse.json({
        error: 'Title is required',
        status: 'error'
      }, { status: 400 })
    }

    // In real implementation: call MCP Supabase insert tool
    const conversation: Conversation = {
      id: `conv_${Date.now()}`,
      title,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      metadata: metadata || {}
    }
    
    console.log('MCP Supabase: Created conversation', conversation.id)
    
    return NextResponse.json({
      status: 'success',
      data: conversation
    })
  } catch (error) {
    console.error('Create conversation API error:', error)
    return NextResponse.json({
      error: 'Failed to create conversation',
      status: 'error',
      details: error instanceof Error ? error.message : 'Unknown error'
    }, { status: 500 })
  }
}
