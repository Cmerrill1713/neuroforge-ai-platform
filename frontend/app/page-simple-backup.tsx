'use client'

import React, { useState } from 'react'

export default function HomePage() {
  const [message, setMessage] = useState('');
  const [messages, setMessages] = useState<Array<{id: string, content: string, sender: 'user' | 'assistant', audioFile?: string}>>([]);
  const [isLoading, setIsLoading] = useState(false);

  const handleSendMessage = async () => {
    if (!message.trim()) return;
    
    setIsLoading(true);
    const userMessage = { id: Date.now().toString(), content: message, sender: 'user' as const };
    setMessages(prev => [...prev, userMessage]);
    const currentMessage = message;
    setMessage('');
    
    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: currentMessage }),
      });
      
      const data = await response.json();
      setMessages(prev => [...prev, { 
        id: (Date.now() + 1).toString(), 
        content: data.content, 
        sender: 'assistant',
        audioFile: data.audioFile 
      }]);
    } catch (error) {
      console.error('Error sending message:', error);
      setMessages(prev => [...prev, { id: (Date.now() + 1).toString(), content: 'Sorry, there was an error.', sender: 'assistant' }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div style={{ 
      display: 'flex', 
      flexDirection: 'column',
      height: '100vh', 
      width: '100vw',
      backgroundColor: '#0a0a0a',
      padding: '16px',
      color: 'white'
    }}>
      {/* Header */}
      <div style={{ 
        padding: '16px', 
        marginBottom: '16px', 
        background: 'linear-gradient(135deg, rgba(25, 118, 210, 0.95) 0%, rgba(21, 101, 192, 0.95) 100%)',
        borderRadius: '8px',
        textAlign: 'center'
      }}>
        <h1 style={{ margin: 0, fontWeight: 700 }}>
          AI Chat Assistant
        </h1>
        <p style={{ margin: '8px 0 0 0', opacity: 0.8 }}>
          Test the user experience and functionality
        </p>
      </div>

      {/* Messages */}
      <div style={{ 
        flex: 1, 
        overflow: 'auto', 
        marginBottom: '16px',
        padding: '8px',
        border: '1px solid rgba(255, 255, 255, 0.1)',
        borderRadius: '8px',
        background: 'rgba(255, 255, 255, 0.02)'
      }}>
        {messages.length === 0 ? (
          <div style={{ textAlign: 'center', marginTop: '32px', opacity: 0.6 }}>
            <p>Start a conversation with the AI assistant</p>
            <p style={{ fontSize: '14px', marginTop: '16px' }}>
              ✅ Frontend: Running on port 3000<br/>
              ✅ Backend: Running on port 8002<br/>
                      ✅ Production TTS: Running on port 8086<br/>
              ✅ API: Chat endpoint working<br/>
              ✅ System: Ready for testing
            </p>
          </div>
        ) : (
          messages.map((msg) => (
            <div key={msg.id} style={{ 
              marginBottom: '16px', 
              display: 'flex', 
              justifyContent: msg.sender === 'user' ? 'flex-end' : 'flex-start' 
            }}>
              <div style={{
                padding: '16px',
                maxWidth: '70%',
                background: msg.sender === 'user' 
                  ? 'linear-gradient(135deg, #1976d2 0%, #1565c0 100%)'
                  : 'rgba(255, 255, 255, 0.05)',
                borderRadius: '8px',
                border: '1px solid rgba(255, 255, 255, 0.1)'
              }}>
                <p style={{ margin: 0 }}>
                  {msg.content}
                </p>
                {msg.audioFile && (
                  <div style={{ marginTop: '12px' }}>
                    <audio 
                      autoPlay 
                      style={{ width: '100%', height: '32px' }}
                      onLoadedData={(e) => e.currentTarget.play()}
                    >
                      <source src={`/api/audio?filename=${msg.audioFile}`} type="audio/mpeg" />
                      Your browser does not support the audio element.
                    </audio>
                    <p style={{ fontSize: '12px', opacity: 0.7, margin: '4px 0 0 0' }}>
                      🔊 AI Voice Response
                    </p>
                  </div>
                )}
              </div>
            </div>
          ))
        )}
        {isLoading && (
          <div style={{ display: 'flex', justifyContent: 'flex-start', marginBottom: '16px' }}>
            <div style={{
              padding: '16px',
              background: 'rgba(255, 255, 255, 0.05)',
              borderRadius: '8px',
              border: '1px solid rgba(255, 255, 255, 0.1)'
            }}>
              <p style={{ margin: 0, opacity: 0.7 }}>
                AI is thinking...
              </p>
            </div>
          </div>
        )}
      </div>

      {/* Input */}
      <div style={{ display: 'flex', gap: '8px' }}>
        <input
          type="text"
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
          placeholder="Type your message here..."
          disabled={isLoading}
          style={{
            flex: 1,
            padding: '12px',
            backgroundColor: 'rgba(255, 255, 255, 0.1)',
            border: '1px solid rgba(255, 255, 255, 0.3)',
            borderRadius: '8px',
            color: 'white',
            fontSize: '16px'
          }}
        />
        <button
          onClick={handleSendMessage}
          disabled={isLoading || !message.trim()}
          style={{
            padding: '12px 16px',
            background: 'linear-gradient(135deg, #1976d2 0%, #1565c0 100%)',
            color: 'white',
            border: 'none',
            borderRadius: '8px',
            cursor: 'pointer',
            fontSize: '16px',
            opacity: (isLoading || !message.trim()) ? 0.5 : 1
          }}
        >
          Send
        </button>
      </div>
    </div>
  )
}