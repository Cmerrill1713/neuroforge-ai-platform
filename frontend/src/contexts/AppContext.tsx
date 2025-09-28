import React, { createContext, useContext, useReducer, useEffect, ReactNode } from 'react';
import { apiService } from '../services/api';
import { wsService } from '../services/websocket';
import { ChatMessage, ModelInfo, AgentInfo } from '../services/api';

interface AppState {
  // Chat state
  messages: ChatMessage[];
  isLoading: boolean;
  
  // Models state
  models: ModelInfo[];
  activeModel: string | null;
  
  // Agents state
  agents: AgentInfo[];
  activeAgents: string[];
  
  // System state
  systemStatus: 'online' | 'offline' | 'error';
  lastUpdate: Date | null;
  
  // UI state
  sidebarOpen: boolean;
  notifications: Notification[];
}

type AppAction =
  | { type: 'SET_LOADING'; payload: boolean }
  | { type: 'ADD_MESSAGE'; payload: ChatMessage }
  | { type: 'SET_MESSAGES'; payload: ChatMessage[] }
  | { type: 'SET_MODELS'; payload: ModelInfo[] }
  | { type: 'SET_ACTIVE_MODEL'; payload: string }
  | { type: 'SET_AGENTS'; payload: AgentInfo[] }
  | { type: 'SET_ACTIVE_AGENTS'; payload: string[] }
  | { type: 'SET_SYSTEM_STATUS'; payload: 'online' | 'offline' | 'error' }
  | { type: 'SET_SIDEBAR_OPEN'; payload: boolean }
  | { type: 'ADD_NOTIFICATION'; payload: Notification }
  | { type: 'REMOVE_NOTIFICATION'; payload: string }
  | { type: 'UPDATE_LAST_UPDATE' };

interface Notification {
  id: string;
  type: 'success' | 'error' | 'warning' | 'info';
  message: string;
  timestamp: Date;
}

const initialState: AppState = {
  messages: [],
  isLoading: false,
  models: [],
  activeModel: null,
  agents: [],
  activeAgents: [],
  systemStatus: 'offline',
  lastUpdate: null,
  sidebarOpen: true,
  notifications: [],
};

function appReducer(state: AppState, action: AppAction): AppState {
  switch (action.type) {
    case 'SET_LOADING':
      return { ...state, isLoading: action.payload };
    
    case 'ADD_MESSAGE':
      return { ...state, messages: [...state.messages, action.payload] };
    
    case 'SET_MESSAGES':
      return { ...state, messages: action.payload };
    
    case 'SET_MODELS':
      return { ...state, models: action.payload };
    
    case 'SET_ACTIVE_MODEL':
      return { ...state, activeModel: action.payload };
    
    case 'SET_AGENTS':
      return { ...state, agents: action.payload };
    
    case 'SET_ACTIVE_AGENTS':
      return { ...state, activeAgents: action.payload };
    
    case 'SET_SYSTEM_STATUS':
      return { ...state, systemStatus: action.payload };
    
    case 'SET_SIDEBAR_OPEN':
      return { ...state, sidebarOpen: action.payload };
    
    case 'ADD_NOTIFICATION':
      return { ...state, notifications: [...state.notifications, action.payload] };
    
    case 'REMOVE_NOTIFICATION':
      return { ...state, notifications: state.notifications.filter(n => n.id !== action.payload) };
    
    case 'UPDATE_LAST_UPDATE':
      return { ...state, lastUpdate: new Date() };
    
    default:
      return state;
  }
}

interface AppContextType {
  state: AppState;
  dispatch: React.Dispatch<AppAction>;
  
  // Actions
  sendMessage: (content: string, model?: string) => Promise<void>;
  loadModels: () => Promise<void>;
  loadAgents: () => Promise<void>;
  checkSystemStatus: () => Promise<void>;
  addNotification: (type: Notification['type'], message: string) => void;
}

const AppContext = createContext<AppContextType | undefined>(undefined);

export const useAppContext = () => {
  const context = useContext(AppContext);
  if (!context) {
    throw new Error('useAppContext must be used within an AppProvider');
  }
  return context;
};

interface AppProviderProps {
  children: ReactNode;
}

export const AppProvider: React.FC<AppProviderProps> = ({ children }) => {
  const [state, dispatch] = useReducer(appReducer, initialState);

  // Initialize WebSocket connection
  useEffect(() => {
    // wsService.connect(); // Disabled - using HTTP POST instead
    
    // Set up WebSocket message handlers
    const handleMessage = (message: any) => {
      switch (message.type) {
        case 'chat_message':
          dispatch({ type: 'ADD_MESSAGE', payload: message.data });
          break;
        case 'model_update':
          dispatch({ type: 'SET_MODELS', payload: message.data });
          break;
        case 'agent_update':
          dispatch({ type: 'SET_AGENTS', payload: message.data });
          break;
        case 'system_status':
          dispatch({ type: 'SET_SYSTEM_STATUS', payload: message.data.status });
          break;
        case 'notification':
          addNotification(message.data.type, message.data.message);
          break;
      }
    };

    wsService.config.onMessage = handleMessage;

    return () => {
      // wsService.disconnect(); // Disabled - using HTTP POST instead
    };
  }, []);

  // Load initial data
  useEffect(() => {
    loadModels();
    loadAgents();
    checkSystemStatus();
  }, [loadModels]);

  // Actions
  const sendMessage = async (content: string, model?: string) => {
    dispatch({ type: 'SET_LOADING', payload: true });
    
    try {
      const userMessage: ChatMessage = {
        id: Date.now().toString(),
        content,
        sender: 'user',
        timestamp: new Date(),
      };
      
      dispatch({ type: 'ADD_MESSAGE', payload: userMessage });
      let assistantMessage: ChatMessage | null = null;

      try {
        const res = await fetch('/api/chat', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ message: content, model: model || state.activeModel || undefined }),
        });

        if (res.ok) {
          const data = await res.json();
          assistantMessage = {
            id: data.id ?? Date.now().toString(),
            content: data.content ?? '',
            sender: 'assistant',
            timestamp: data.timestamp ?? new Date().toISOString(),
            model: data.model ?? data.metadata?.modelName,
            metadata: {
              ...data.metadata,
              agent: data.metadata?.agent ?? data.model,
              confidence: data.metadata?.confidence,
              fallbackUsed: data.metadata?.fallbackUsed ?? false,
              responseTimeMs: data.metadata?.responseTimeMs,
            },
          };
        } else {
          console.warn('Chat API request failed, falling back to apiService:', await res.text());
        }
      } catch (error) {
        console.warn('Chat API request error, falling back to apiService:', error);
      }

      if (!assistantMessage) {
        const response = await apiService.sendMessage(content, model || state.activeModel || undefined);
        if (response.success && response.data) {
          assistantMessage = response.data;
        } else {
          throw new Error(response.error || 'Failed to send message');
        }
      }

      if (assistantMessage) {
        assistantMessage.metadata = {
          ...assistantMessage.metadata,
          agent: assistantMessage.metadata?.agent || assistantMessage.model,
        };
        dispatch({ type: 'ADD_MESSAGE', payload: assistantMessage });
      }
    } catch (error) {
      addNotification('error', `Failed to send message: ${error instanceof Error ? error.message : 'Unknown error'}`);
    } finally {
      dispatch({ type: 'SET_LOADING', payload: false });
    }
  };

  const loadModels = useCallback(async () => {
    try {
      const response = await apiService.getModels();
      if (response.success && response.data) {
        dispatch({ type: 'SET_MODELS', payload: response.data });
        if (response.data.length > 0 && !state.activeModel) {
          dispatch({ type: 'SET_ACTIVE_MODEL', payload: response.data[0].id });
        }
      }
    } catch (error) {
      console.error('Failed to load models:', error);
    }
  }, [state.activeModel]);

  const loadAgents = async () => {
    try {
      const response = await apiService.getAgents();
      if (response.success && response.data) {
        dispatch({ type: 'SET_AGENTS', payload: response.data });
      }
    } catch (error) {
      console.error('Failed to load agents:', error);
    }
  };

  const checkSystemStatus = async () => {
    try {
      const response = await apiService.getSystemStatus();
      if (response.success) {
        dispatch({ type: 'SET_SYSTEM_STATUS', payload: 'online' });
      } else {
        dispatch({ type: 'SET_SYSTEM_STATUS', payload: 'error' });
      }
    } catch (error) {
      dispatch({ type: 'SET_SYSTEM_STATUS', payload: 'offline' });
    }
    dispatch({ type: 'UPDATE_LAST_UPDATE' });
  };

  const addNotification = (type: Notification['type'], message: string) => {
    const notification: Notification = {
      id: Date.now().toString(),
      type,
      message,
      timestamp: new Date(),
    };
    dispatch({ type: 'ADD_NOTIFICATION', payload: notification });
    
    // Auto-remove notification after 5 seconds
    setTimeout(() => {
      dispatch({ type: 'REMOVE_NOTIFICATION', payload: notification.id });
    }, 5000);
  };

  const contextValue: AppContextType = {
    state,
    dispatch,
    sendMessage,
    loadModels,
    loadAgents,
    checkSystemStatus,
    addNotification,
  };

  return (
    <AppContext.Provider value={contextValue}>
      {children}
    </AppContext.Provider>
  );
};
