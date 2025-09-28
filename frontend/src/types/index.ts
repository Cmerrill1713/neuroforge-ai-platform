import React from 'react';

// Type definitions for the application
export interface Panel {
  id: string;
  name: string;
  icon: React.ReactNode;
  color: string;
}

export interface ChatMessage {
  id: string;
  content: string;
  sender: 'user' | 'assistant';
  timestamp: Date | string;
  model?: string;
  metadata?: Record<string, any>;
}

export interface AppState {
  activePanel: string;
  sidebarOpen: boolean;
  isMobile: boolean;
}

export interface ChatInterfaceProps {
  activePanel: string;
  onSendMessage: (message: string) => void;
}

export interface NavigationProps {
  panels: Panel[];
  activePanel: string;
  onPanelChange: (panelId: string) => void;
  sidebarOpen: boolean;
}
