#!/usr/bin/env python3
"""
Conversation Persistence API Routes
Automatically saves all chat conversations to PostgreSQL
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from uuid import uuid4

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

# Router
router = APIRouter(prefix="/api/conversations", tags=["conversations"])

# Global database connection (will be initialized)
db_connection = None


class MessageCreate(BaseModel):
    """Create message request"""
    conversation_id: Optional[str] = None
    content: str = Field(..., min_length=1)
    sender: str = Field(..., pattern="^(user|assistant)$")
    model: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ConversationResponse(BaseModel):
    """Conversation response"""
    id: str
    title: str
    created_at: str
    updated_at: str
    message_count: int


class MessageResponse(BaseModel):
    """Message response"""
    id: str
    conversation_id: str
    content: str
    sender: str
    model: Optional[str]
    created_at: str
    metadata: Dict[str, Any]


def set_db_connection(conn):
    """Set global database connection"""
    global db_connection
    db_connection = conn


@router.post("/messages", response_model=MessageResponse)
async def save_message(message: MessageCreate) -> MessageResponse:
    """
    Save a message to the conversation
    
    Auto-creates conversation if conversation_id not provided
    Returns the saved message with IDs
    """
    if not db_connection:
        # Store in memory if no DB (fallback)
        logger.warning("No database configured - message not persisted")
        return MessageResponse(
            id=str(uuid4()),
            conversation_id=message.conversation_id or str(uuid4()),
            content=message.content,
            sender=message.sender,
            model=message.model,
            created_at=datetime.now().isoformat(),
            metadata=message.metadata
        )
    
    try:
        import psycopg2
        from psycopg2.extras import RealDictCursor
        import json
        
        conn = db_connection
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        # Create conversation if needed
        conversation_id = message.conversation_id
        if not conversation_id:
            # Generate title from first user message
            title = message.content[:50] + ("..." if len(message.content) > 50 else "")
            
            cur.execute("""
                INSERT INTO conversations (id, title, created_at, updated_at)
                VALUES (%s, %s, NOW(), NOW())
                RETURNING id
            """, (str(uuid4()), title))
            
            conversation_id = cur.fetchone()['id']
        
        # Save message
        message_id = str(uuid4())
        cur.execute("""
            INSERT INTO messages (id, conversation_id, content, sender, model, created_at, metadata)
            VALUES (%s, %s, %s, %s, %s, NOW(), %s)
            RETURNING id, created_at
        """, (
            message_id,
            conversation_id,
            message.content,
            message.sender,
            message.model,
            json.dumps(message.metadata)
        ))
        
        result = cur.fetchone()
        
        # Update conversation timestamp
        cur.execute("""
            UPDATE conversations SET updated_at = NOW() WHERE id = %s
        """, (conversation_id,))
        
        conn.commit()
        cur.close()
        
        logger.info(f"💾 Message saved: {message_id} in conversation {conversation_id}")
        
        return MessageResponse(
            id=result['id'],
            conversation_id=conversation_id,
            content=message.content,
            sender=message.sender,
            model=message.model,
            created_at=result['created_at'].isoformat(),
            metadata=message.metadata
        )
        
    except Exception as e:
        logger.error(f"Failed to save message: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to save message: {str(e)}")


@router.get("/conversations", response_model=List[ConversationResponse])
async def get_conversations(limit: int = 50) -> List[ConversationResponse]:
    """Get all conversations"""
    if not db_connection:
        return []
    
    try:
        import psycopg2
        from psycopg2.extras import RealDictCursor
        
        conn = db_connection
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        cur.execute("""
            SELECT 
                c.id, 
                c.title, 
                c.created_at, 
                c.updated_at,
                COUNT(m.id) as message_count
            FROM conversations c
            LEFT JOIN messages m ON c.id = m.conversation_id
            GROUP BY c.id, c.title, c.created_at, c.updated_at
            ORDER BY c.updated_at DESC
            LIMIT %s
        """, (limit,))
        
        conversations = cur.fetchall()
        cur.close()
        
        return [
            ConversationResponse(
                id=conv['id'],
                title=conv['title'],
                created_at=conv['created_at'].isoformat(),
                updated_at=conv['updated_at'].isoformat(),
                message_count=conv['message_count']
            )
            for conv in conversations
        ]
        
    except Exception as e:
        logger.error(f"Failed to get conversations: {e}")
        return []


@router.get("/conversations/{conversation_id}/messages", response_model=List[MessageResponse])
async def get_conversation_messages(conversation_id: str) -> List[MessageResponse]:
    """Get all messages in a conversation"""
    if not db_connection:
        return []
    
    try:
        import psycopg2
        from psycopg2.extras import RealDictCursor
        
        conn = db_connection
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        cur.execute("""
            SELECT id, conversation_id, content, sender, model, created_at, metadata
            FROM messages
            WHERE conversation_id = %s
            ORDER BY created_at ASC
        """, (conversation_id,))
        
        messages = cur.fetchall()
        cur.close()
        
        return [
            MessageResponse(
                id=msg['id'],
                conversation_id=msg['conversation_id'],
                content=msg['content'],
                sender=msg['sender'],
                model=msg['model'],
                created_at=msg['created_at'].isoformat(),
                metadata=msg['metadata'] or {}
            )
            for msg in messages
        ]
        
    except Exception as e:
        logger.error(f"Failed to get messages: {e}")
        return []


@router.delete("/conversations/{conversation_id}")
async def delete_conversation(conversation_id: str) -> Dict[str, Any]:
    """Delete a conversation and all its messages"""
    if not db_connection:
        raise HTTPException(status_code=503, detail="Database not configured")
    
    try:
        import psycopg2
        
        conn = db_connection
        cur = conn.cursor()
        
        # Delete conversation (messages cascade)
        cur.execute("DELETE FROM conversations WHERE id = %s", (conversation_id,))
        conn.commit()
        cur.close()
        
        logger.info(f"🗑️ Deleted conversation: {conversation_id}")
        
        return {"success": True, "conversation_id": conversation_id}
        
    except Exception as e:
        logger.error(f"Failed to delete conversation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

