import React, { memo } from 'react';
import { Box, Typography, Paper, IconButton, Tooltip } from '@mui/material';
import { ContentCopy as CopyIcon } from '@mui/icons-material';
import { ChatMessage as ChatMessageType } from '../../types';
import { useCopy } from '../../hooks/useCopy';

interface ChatMessageProps {
  message: ChatMessageType;
}

export const ChatMessage = memo<ChatMessageProps>(({ message }) => {
  const isUser = message.sender === 'user';
  const { copyMessage } = useCopy();

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
