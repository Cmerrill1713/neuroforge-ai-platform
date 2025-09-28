import React, { memo } from 'react';
import { Box, Typography, Paper, IconButton, Tooltip, Chip } from '@mui/material';
import { ContentCopy as CopyIcon } from '@mui/icons-material';
import { ChatMessage as ChatMessageType } from '../../types';
import { useCopy } from '../../hooks/useCopy';

interface ChatMessageProps {
  message: ChatMessageType;
}

export const ChatMessage = memo<ChatMessageProps>(({ message }) => {
  const isUser = message.sender === 'user';
  const { copyMessage } = useCopy();

  const metadata = message.metadata || {};
  const agentLabel = metadata.agent || metadata.agent_name || message.model;
  const rawConfidence = metadata.confidence ?? metadata.confidence_score;
  const confidence = typeof rawConfidence === 'number'
    ? rawConfidence
    : rawConfidence !== undefined
      ? Number(rawConfidence)
      : undefined;
  const rawResponseTime = metadata.responseTimeMs ?? metadata.processing_time;
  const responseTime = typeof rawResponseTime === 'number'
    ? rawResponseTime
    : rawResponseTime !== undefined
      ? Number(rawResponseTime)
      : undefined;
  const fallbackUsed = Boolean(metadata.fallbackUsed ?? metadata.fallback);
  const reviewRequired = Boolean(metadata.reviewRequired ?? metadata.requires_review);
  const securityFlags = Number(metadata.securityFlags ?? 0);

  const handleCopyMessage = async () => {
    await copyMessage(message.content);
  };
  
  return (
    <Box sx={{ 
      mb: 2, 
      display: 'flex', 
      justifyContent: isUser ? 'flex-end' : 'flex-start',
      position: 'relative',
      '&:hover .copy-button': {
        opacity: 1,
      },
    }}>
      <Paper
        sx={{
          p: 2,
          maxWidth: '70%',
          background: isUser 
            ? 'linear-gradient(135deg, #1976d2 0%, #1565c0 100%)'
            : 'rgba(255, 255, 255, 0.05)',
          backdropFilter: 'blur(10px)',
          border: '1px solid rgba(255, 255, 255, 0.1)',
          borderRadius: 2,
          ml: isUser ? 2 : 0,
          mr: isUser ? 0 : 2,
          position: 'relative',
        }}
      >
        <Typography
          variant="body1"
          sx={{
            color: 'white',
            fontWeight: isUser ? 500 : 400,
            wordBreak: 'break-word',
          }}
        >
          {message.content}
        </Typography>
        {!isUser && (agentLabel || confidence !== undefined || fallbackUsed || responseTime !== undefined) && (
          <Box sx={{ mt: 1, display: 'flex', flexWrap: 'wrap', gap: 1 }}>
            {agentLabel && (
              <Chip
                label={`Agent: ${agentLabel}`}
                size="small"
                sx={{ backgroundColor: 'rgba(25, 118, 210, 0.2)', color: '#90caf9' }}
              />
            )}
            {Number.isFinite(confidence) && (
              <Chip
                label={`Confidence: ${(confidence * 100).toFixed(1)}%`}
                size="small"
                sx={{ backgroundColor: 'rgba(76, 175, 80, 0.2)', color: '#a5d6a7' }}
              />
            )}
            {Number.isFinite(responseTime) && (
              <Chip
                label={`Latency: ${responseTime.toFixed(0)}ms`}
                size="small"
                sx={{ backgroundColor: 'rgba(255, 193, 7, 0.2)', color: '#ffe082' }}
              />
            )}
            {fallbackUsed && (
              <Chip
                label="Fallback response"
                size="small"
                sx={{ backgroundColor: 'rgba(244, 67, 54, 0.2)', color: '#ef9a9a' }}
              />
            )}
            {reviewRequired && (
              <Chip
                label="Review suggested"
                size="small"
                sx={{ backgroundColor: 'rgba(255, 152, 0, 0.2)', color: '#ffcc80' }}
              />
            )}
            {securityFlags > 0 && (
              <Chip
                label={`Security flags: ${securityFlags}`}
                size="small"
                sx={{ backgroundColor: 'rgba(229, 57, 53, 0.25)', color: '#ef9a9a' }}
              />
            )}
          </Box>
        )}
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mt: 1 }}>
          <Typography
            variant="caption"
            sx={{
              color: 'rgba(255, 255, 255, 0.6)',
              fontSize: '0.7rem',
            }}
          >
            {typeof window !== 'undefined' ? new Date(message.timestamp).toLocaleTimeString() : 'Loading...'}
          </Typography>
          <Tooltip title="Copy message">
            <IconButton
              size="small"
              onClick={handleCopyMessage}
              className="copy-button"
              sx={{
                opacity: 0,
                transition: 'opacity 0.2s ease',
                color: 'rgba(255, 255, 255, 0.7)',
                '&:hover': {
                  backgroundColor: 'rgba(255, 255, 255, 0.1)',
                  color: 'white',
                },
              }}
            >
              <CopyIcon fontSize="small" />
            </IconButton>
          </Tooltip>
        </Box>
      </Paper>
    </Box>
  );
});

ChatMessage.displayName = 'ChatMessage';
