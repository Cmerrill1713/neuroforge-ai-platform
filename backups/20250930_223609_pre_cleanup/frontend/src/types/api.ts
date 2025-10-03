// Minimal API types
export interface AgentInfo {
  id: string
  name: string
  type: string
  status: 'active' | 'inactive' | 'error'
  lastActivity: string
  capabilities: string[]
}

export interface SystemHealthResponse {
  status: 'healthy' | 'degraded' | 'unhealthy'
  version: string
  uptime: number
  database_connected: boolean
  components: Record<string, boolean>
}

export interface AgentPerformanceStats {
  total_agents: number
  active_agents: number
  total_requests: number
  average_response_time: number
  success_rate: number
  agent_stats: Record<string, any>
}

export interface ChatMessage {
  id: string
  content: string
  sender: 'user' | 'assistant'
  timestamp: string
  model?: string
  agent_used?: string;
  confidence?: number;
  reasoning?: string;
  performance_metrics?: Record<string, any>;
  cache_hit?: boolean;
  response_time?: number;
  attachment?: {
    name: string;
    type: string;
    size: number;
  }
}

export interface ChatRequest {
  message: string
  model?: string
  context?: string
}

export interface ChatResponse {
  response: string;
  agent_used: string;
  confidence: number;
  reasoning: string;
  performance_metrics: Record<string, any>;
  cache_hit: boolean;
  response_time: number;
  timestamp: string;
}

export interface ChatHistoryResponse {
  messages: ChatMessage[]
  total_count: number
}

export interface KnowledgeSearchRequest {
  query: string
  limit?: number
}

export interface KnowledgeSearchResponse {
  results: any[]
  total_found: number
  search_time: number
}

export interface KnowledgeStatsResponse {
  total_documents: number
  total_chunks: number
  last_updated: string
  index_size: number
}

export interface ApiError {
  error: string
  message?: string
  status?: number
}

// Vision Model Types
export interface VisionAnalysisRequest {
  image_url?: string
  image_data?: string
}

export interface VisionAnalysisResponse {
  analysis: any
  recommendations: any[]
  timestamp: string
}

export interface VisionModelsResponse {
  models: string[]
  capabilities: string[]
}

// HRM Model Types
export interface HRMReasoningRequest {
  content: string
  user_id?: string
  use_chaos?: boolean
  use_quantum?: boolean
}

export interface HRMReasoningResponse {
  reasoning: any
  confidence: number
  approach: string
}

export interface HRMModelsResponse {
  models: string[]
}

// Voice Model Types
export interface VoiceSynthesisRequest {
  text: string
  voice?: string
}

export interface VoiceSynthesisResponse {
  audio_url: string
  text: string
  voice: string
  duration: number
  format: string
}

export interface VoiceTranscriptionRequest {
  audio_data: string
  language?: string
}

export interface VoiceTranscriptionResponse {
  text: string
  confidence: number
  language: string
  duration: number
}

export interface VoiceOptionsResponse {
  voices: string[]
}

// MLX Model Types
export interface MLXGenerationRequest {
  prompt: string
  model?: string
  max_tokens?: number
}

export interface MLXGenerationResponse {
  text: string
  model: string
  tokens_generated: number
  performance: string
}

export interface MLXModelsResponse {
  models: string[]
  capabilities: string[]
  optimization: string
}

// Ollama Model Types
export interface OllamaGenerationRequest {
  prompt: string
  model?: string
}

export interface OllamaGenerationResponse {
  text: string
  model: string
  tokens_used: number
  finish_reason: string
}

export interface OllamaModelsResponse {
  models: any
  status: string
  error?: string
}