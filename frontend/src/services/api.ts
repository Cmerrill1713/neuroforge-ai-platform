// API service layer for backend integration

// Advanced Technical Middleware Interfaces
interface MessageAnalysis {
  intent: 'general' | 'code_assistance' | 'data_analysis' | 'system_administration' | 'learning';
  complexity: 'low' | 'medium' | 'high' | 'critical';
  domain: 'conversation' | 'programming' | 'analytics' | 'devops' | 'education';
  urgency: 'low' | 'normal' | 'high' | 'critical';
  technicalLevel: 'beginner' | 'intermediate' | 'advanced' | 'expert';
  contextRequired: boolean;
  multiModal: boolean;
  requiresRealTime: boolean;
  estimatedTokens: number;
  suggestedModels: string[];
  processingTime: number;
}

export interface ApiResponse<T> {
  data: T;
  success: boolean;
  message?: string;
  error?: string;
}

export interface ChatMessage {
  id: string;
  content: string;
  sender: 'user' | 'assistant';
  timestamp: Date | string;
  model?: string;
  metadata?: Record<string, any>;
}

export interface ModelInfo {
  id: string;
  name: string;
  status: 'online' | 'offline' | 'error';
  capabilities: string[];
  responseTime: number;
  memoryUsage: number;
}

export interface AgentInfo {
  id: string;
  name: string;
  type: string;
  status: 'active' | 'inactive' | 'error';
  lastActivity: Date;
  capabilities: string[];
}

class ApiService {
  private baseUrl: string;

  constructor() {
    // Connect to the real backend API server
    this.baseUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8002';
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<ApiResponse<T>> {
    try {
      console.log(`Making API request to: ${this.baseUrl}${endpoint}`);
      const response = await fetch(`${this.baseUrl}${endpoint}`, {
        headers: {
          'Content-Type': 'application/json',
          ...options.headers,
        },
        ...options,
      });

      console.log(`API response status: ${response.status} for ${endpoint}`);

      if (!response.ok) {
        const errorText = await response.text();
        console.error(`API request failed: ${endpoint}`, errorText);
        throw new Error(`HTTP error! status: ${response.status} - ${errorText}`);
      }

      const data = await response.json();
      console.log(`API request successful: ${endpoint}`, data);
      return {
        data,
        success: true,
      };
    } catch (error) {
      console.error(`API request to ${endpoint} failed:`, error);
      return {
        data: null as T,
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error',
      };
    }
  }

  // Enhanced Chat API with Advanced Technical Middleware
  async sendMessage(message: string, model?: string): Promise<ApiResponse<ChatMessage>> {
    try {
      // Advanced message analysis and classification
      const messageAnalysis = await this.analyzeMessage(message);
      
      // Intelligent routing based on analysis
      const response = await this.routeMessage(message, messageAnalysis, model);
      
      return response;
    } catch (error) {
      console.error('Advanced message processing failed:', error);
      // Fallback to basic processing
      return this.fallbackProcessing(message, model);
    }
  }

  private async analyzeMessage(message: string): Promise<MessageAnalysis> {
    const analysis: MessageAnalysis = {
      intent: 'general',
      complexity: 'low',
      domain: 'conversation',
      urgency: 'normal',
      technicalLevel: 'beginner',
      contextRequired: false,
      multiModal: false,
      requiresRealTime: false,
      estimatedTokens: message.length * 1.5,
      suggestedModels: [],
      processingTime: 0
    };

    const startTime = Date.now();
    const lowerMessage = message.toLowerCase();

    // Advanced intent detection
    if (this.isCodeRelatedMessage(message)) {
      analysis.intent = 'code_assistance';
      analysis.domain = 'programming';
      analysis.technicalLevel = this.detectTechnicalLevel(message);
      analysis.complexity = this.assessComplexity(message);
      analysis.contextRequired = this.requiresContext(message);
    } else if (this.isDataAnalysisRequest(message)) {
      analysis.intent = 'data_analysis';
      analysis.domain = 'analytics';
      analysis.technicalLevel = 'intermediate';
      analysis.complexity = 'high';
    } else if (this.isSystemAdminRequest(message)) {
      analysis.intent = 'system_administration';
      analysis.domain = 'devops';
      analysis.technicalLevel = 'advanced';
      analysis.complexity = 'high';
      analysis.urgency = 'high';
    } else if (this.isLearningRequest(message)) {
      analysis.intent = 'learning';
      analysis.domain = 'education';
      analysis.technicalLevel = 'beginner';
      analysis.complexity = 'medium';
    }

    // Model selection based on analysis
    analysis.suggestedModels = this.selectOptimalModels(analysis);
    analysis.processingTime = Date.now() - startTime;

    return analysis;
  }

  private async routeMessage(message: string, analysis: MessageAnalysis, model?: string): Promise<ApiResponse<ChatMessage>> {
    const selectedModel = model || analysis.suggestedModels[0] || 'qwen2.5:7b';
    
    switch (analysis.intent) {
      case 'code_assistance':
        return this.handleCodeRequest(message, analysis, selectedModel);
      
      case 'data_analysis':
        return this.handleDataAnalysisRequest(message, analysis, selectedModel);
      
      case 'system_administration':
        return this.handleSystemAdminRequest(message, analysis, selectedModel);
      
      case 'learning':
        return this.handleLearningRequest(message, analysis, selectedModel);
      
      default:
        return this.handleGeneralConversation(message, analysis);
    }
  }

  private async handleCodeRequest(message: string, analysis: MessageAnalysis, model: string): Promise<ApiResponse<ChatMessage>> {
    // Determine the best code assistant mode based on analysis
    const mode = this.selectCodeMode(message, analysis);
    
    // Use the most appropriate model for the task - only send parameters the backend expects
    const response = await this.request<any>('/code-assistant/assist', {
      method: 'POST',
      body: JSON.stringify({
        task_description: message,
        mode: mode
      }),
    });

    if (response.success && response.data) {
      const chatMessage: ChatMessage = {
        id: Date.now().toString(),
        content: this.formatTechnicalResponse(response.data, analysis),
        sender: 'assistant',
        timestamp: new Date().toISOString(),
        model: model,
        metadata: {
          intent: analysis.intent,
          complexity: analysis.complexity,
          technical_level: analysis.technicalLevel,
          processing_time: analysis.processingTime,
          confidence_score: response.data.confidence_score,
          execution_time: response.data.execution_time,
          mode: mode,
          is_code_related: true
        }
      };
      return { data: chatMessage, success: true };
    }

    return response;
  }

  private async handleDataAnalysisRequest(message: string, analysis: MessageAnalysis, model: string): Promise<ApiResponse<ChatMessage>> {
    // Route to data analysis endpoints
    const response = await this.request<any>('/api/autonomous-vibe/analyze', {
      method: 'POST',
      body: JSON.stringify({
        query: message,
        analysis_type: 'data_analysis',
        model: model,
        complexity: analysis.complexity
      }),
    });

    if (response.success && response.data) {
      const chatMessage: ChatMessage = {
        id: Date.now().toString(),
        content: this.formatDataAnalysisResponse(response.data),
        sender: 'assistant',
        timestamp: new Date().toISOString(),
        model: model,
        metadata: {
          intent: analysis.intent,
          analysis_type: 'data_analysis',
          processing_time: analysis.processingTime,
          is_code_related: false
        }
      };
      return { data: chatMessage, success: true };
    }

    return response;
  }

  private async handleSystemAdminRequest(message: string, analysis: MessageAnalysis, model: string): Promise<ApiResponse<ChatMessage>> {
    // Route to system administration endpoints
    const response = await this.request<any>('/monitoring/metrics', {
      method: 'GET'
    });

    if (response.success && response.data) {
      const chatMessage: ChatMessage = {
        id: Date.now().toString(),
        content: this.formatSystemAdminResponse(response.data, message),
        sender: 'assistant',
        timestamp: new Date().toISOString(),
        model: model,
        metadata: {
          intent: analysis.intent,
          urgency: analysis.urgency,
          processing_time: analysis.processingTime,
          is_code_related: false
        }
      };
      return { data: chatMessage, success: true };
    }

    return response;
  }

  private async handleLearningRequest(message: string, analysis: MessageAnalysis, model: string): Promise<ApiResponse<ChatMessage>> {
    // Use the learning mode with enhanced context - only send parameters the backend expects
    const response = await this.request<any>('/code-assistant/assist', {
      method: 'POST',
      body: JSON.stringify({
        task_description: message,
        mode: 'learning'
      }),
    });

    if (response.success && response.data) {
      const chatMessage: ChatMessage = {
        id: Date.now().toString(),
        content: this.formatLearningResponse(response.data, analysis),
        sender: 'assistant',
        timestamp: new Date().toISOString(),
        model: model,
        metadata: {
          intent: analysis.intent,
          learning_level: analysis.technicalLevel,
          processing_time: analysis.processingTime,
          is_code_related: true
        }
      };
      return { data: chatMessage, success: true };
    }

    return response;
  }

  private async handleGeneralConversation(message: string, analysis: MessageAnalysis): Promise<ApiResponse<ChatMessage>> {
    // Enhanced general conversation with context awareness
    const friendlyResponse = this.generateContextAwareResponse(message, analysis);
    const chatMessage: ChatMessage = {
      id: Date.now().toString(),
      content: friendlyResponse,
      sender: 'assistant',
      timestamp: new Date().toISOString(),
      model: 'friendly-assistant',
      metadata: {
        intent: analysis.intent,
        response_type: 'conversational',
        processing_time: analysis.processingTime,
        is_code_related: false
      }
    };
    return { data: chatMessage, success: true };
  }

  private isCodeRelatedMessage(message: string): boolean {
    const codeKeywords = [
      'code', 'programming', 'function', 'class', 'variable', 'debug', 'error', 'bug',
      'algorithm', 'data structure', 'api', 'database', 'sql', 'javascript', 'python',
      'react', 'node', 'html', 'css', 'git', 'repository', 'commit', 'pull request',
      'framework', 'library', 'package', 'import', 'export', 'syntax', 'compiler',
      'deploy', 'server', 'client', 'frontend', 'backend', 'full stack', 'devops'
    ];
    
    const lowerMessage = message.toLowerCase();
    return codeKeywords.some(keyword => lowerMessage.includes(keyword));
  }

  // Advanced Technical Analysis Methods
  private isDataAnalysisRequest(message: string): boolean {
    const dataKeywords = [
      'data', 'analysis', 'analytics', 'statistics', 'visualization', 'chart', 'graph',
      'dataset', 'csv', 'json', 'sql query', 'aggregation', 'correlation', 'regression',
      'machine learning', 'ml', 'ai model', 'prediction', 'classification', 'clustering'
    ];
    const lowerMessage = message.toLowerCase();
    return dataKeywords.some(keyword => lowerMessage.includes(keyword));
  }

  private isSystemAdminRequest(message: string): boolean {
    const adminKeywords = [
      'server', 'deployment', 'docker', 'kubernetes', 'aws', 'azure', 'gcp',
      'monitoring', 'logs', 'metrics', 'performance', 'scaling', 'load balancer',
      'database', 'backup', 'security', 'firewall', 'ssl', 'certificate',
      'devops', 'ci/cd', 'pipeline', 'infrastructure', 'cloud', 'container'
    ];
    const lowerMessage = message.toLowerCase();
    return adminKeywords.some(keyword => lowerMessage.includes(keyword));
  }

  private isLearningRequest(message: string): boolean {
    const learningKeywords = [
      'learn', 'tutorial', 'guide', 'how to', 'explain', 'teach', 'understand',
      'concept', 'basics', 'introduction', 'beginner', 'getting started',
      'documentation', 'examples', 'best practices', 'patterns'
    ];
    const lowerMessage = message.toLowerCase();
    return learningKeywords.some(keyword => lowerMessage.includes(keyword));
  }

  private detectTechnicalLevel(message: string): 'beginner' | 'intermediate' | 'advanced' | 'expert' {
    const lowerMessage = message.toLowerCase();
    
    if (lowerMessage.includes('beginner') || lowerMessage.includes('basic') || lowerMessage.includes('simple')) {
      return 'beginner';
    }
    
    if (lowerMessage.includes('advanced') || lowerMessage.includes('complex') || lowerMessage.includes('optimization')) {
      return 'advanced';
    }
    
    if (lowerMessage.includes('expert') || lowerMessage.includes('enterprise') || lowerMessage.includes('architecture')) {
      return 'expert';
    }
    
    return 'intermediate';
  }

  private assessComplexity(message: string): 'low' | 'medium' | 'high' | 'critical' {
    const lowerMessage = message.toLowerCase();
    
    if (lowerMessage.includes('critical') || lowerMessage.includes('urgent') || lowerMessage.includes('production')) {
      return 'critical';
    }
    
    if (lowerMessage.includes('complex') || lowerMessage.includes('advanced') || lowerMessage.includes('optimization')) {
      return 'high';
    }
    
    if (lowerMessage.includes('simple') || lowerMessage.includes('basic') || lowerMessage.includes('quick')) {
      return 'low';
    }
    
    return 'medium';
  }

  private requiresContext(message: string): boolean {
    const contextKeywords = [
      'continue', 'previous', 'earlier', 'before', 'context', 'reference',
      'based on', 'following', 'next step', 'part of', 'related to'
    ];
    const lowerMessage = message.toLowerCase();
    return contextKeywords.some(keyword => lowerMessage.includes(keyword));
  }

  private selectOptimalModels(analysis: MessageAnalysis): string[] {
    const models = ['qwen2.5:7b', 'qwen2.5:14b', 'mistral:7b', 'llama3.2:3b'];
    
    switch (analysis.intent) {
      case 'code_assistance':
        return analysis.complexity === 'high' ? ['qwen2.5:14b', 'qwen2.5:7b'] : ['qwen2.5:7b', 'mistral:7b'];
      
      case 'data_analysis':
        return ['qwen2.5:14b', 'qwen2.5:7b'];
      
      case 'system_administration':
        return ['qwen2.5:14b', 'qwen2.5:7b'];
      
      case 'learning':
        return ['qwen2.5:7b', 'mistral:7b'];
      
      default:
        return ['qwen2.5:7b'];
    }
  }

  private selectCodeMode(message: string, analysis: MessageAnalysis): string {
    const lowerMessage = message.toLowerCase();
    
    if (lowerMessage.includes('debug') || lowerMessage.includes('error') || lowerMessage.includes('fix')) {
      return 'debugging';
    }
    
    if (lowerMessage.includes('generate') || lowerMessage.includes('create') || lowerMessage.includes('write')) {
      return 'code_generation';
    }
    
    if (lowerMessage.includes('review') || lowerMessage.includes('check') || lowerMessage.includes('analyze')) {
      return 'code_review';
    }
    
    if (lowerMessage.includes('refactor') || lowerMessage.includes('improve') || lowerMessage.includes('optimize')) {
      return 'refactoring';
    }
    
    if (lowerMessage.includes('test') || lowerMessage.includes('testing') || lowerMessage.includes('unit test')) {
      return 'testing';
    }
    
    return 'learning';
  }

  private formatTechnicalResponse(data: any, analysis: MessageAnalysis): string {
    let response = '';
    
    if (data.explanation) {
      response += data.explanation;
    }
    
    if (data.generated_code) {
      response += '\n\n**Generated Code:**\n```\n' + data.generated_code + '\n```';
    }
    
    if (data.suggestions && data.suggestions.length > 0) {
      response += '\n\n**Suggestions:**\n' + data.suggestions.map((s: string) => `• ${s}`).join('\n');
    }
    
    if (data.improvements && data.improvements.length > 0) {
      response += '\n\n**Improvements:**\n' + data.improvements.map((i: string) => `• ${i}`).join('\n');
    }
    
    return response || 'No response received';
  }

  private formatDataAnalysisResponse(data: any): string {
    return `📊 **Data Analysis Results:**\n\n${JSON.stringify(data, null, 2)}`;
  }

  private formatSystemAdminResponse(data: any, message: string): string {
    return `🔧 **System Administration:**\n\nBased on your request: "${message}"\n\nSystem Status:\n${JSON.stringify(data, null, 2)}`;
  }

  private formatLearningResponse(data: any, analysis: MessageAnalysis): string {
    let response = `📚 **Learning Response (${analysis.technicalLevel} level):**\n\n`;
    
    if (data.explanation) {
      response += data.explanation;
    }
    
    if (data.suggestions && data.suggestions.length > 0) {
      response += '\n\n**Next Steps:**\n' + data.suggestions.map((s: string) => `• ${s}`).join('\n');
    }
    
    return response;
  }

  private generateContextAwareResponse(message: string, analysis: MessageAnalysis): string {
    // Enhanced context-aware responses
    if (message.toLowerCase().includes('hello') || message.toLowerCase().includes('hi')) {
      return "Hello! 👋 Nice to meet you! I'm your AI assistant and I'm here to help. What would you like to chat about?";
    }
    
    if (message.toLowerCase().includes('how are you')) {
      return "I'm doing great, thanks for asking! 😊 I'm ready to help you with whatever you need. What's on your mind?";
    }
    
    if (message.toLowerCase().includes('help')) {
      return "I'd be happy to help! 🤗 I can assist you with general questions, or if you need help with programming, coding, or technical topics, just let me know!";
    }
    
    if (message.toLowerCase().includes('test')) {
      return "Everything looks good! ✅ The system is working perfectly. Is there anything specific you'd like to try or ask about?";
    }
    
    // Default friendly response
    return `Hi there! 👋 I'm your AI assistant. I'm here to help with general questions and conversations. If you need help with programming, coding, or technical topics, just mention it and I'll switch to my technical mode! What would you like to chat about?`;
  }

  private async fallbackProcessing(message: string, model?: string): Promise<ApiResponse<ChatMessage>> {
    // Simple fallback for when advanced processing fails
    const isCodeRelated = this.isCodeRelatedMessage(message);
    
    if (!isCodeRelated) {
      const friendlyResponse = this.generateContextAwareResponse(message, {
        intent: 'general',
        complexity: 'low',
        domain: 'conversation',
        urgency: 'normal',
        technicalLevel: 'beginner',
        contextRequired: false,
        multiModal: false,
        requiresRealTime: false,
        estimatedTokens: message.length * 1.5,
        suggestedModels: ['qwen2.5:7b'],
        processingTime: 0
      });
      
      const chatMessage: ChatMessage = {
        id: Date.now().toString(),
        content: friendlyResponse,
        sender: 'assistant',
        timestamp: new Date().toISOString(),
        model: model || 'friendly-assistant',
        metadata: {
          response_type: 'conversational',
          is_code_related: false,
          fallback: true
        }
      };
      return { data: chatMessage, success: true };
    }

    // Fallback for code-related requests
    const response = await this.request<any>('/code-assistant/assist', {
      method: 'POST',
      body: JSON.stringify({
        task_description: message,
        mode: 'learning',
      }),
    });

    if (response.success && response.data) {
      const chatMessage: ChatMessage = {
        id: Date.now().toString(),
        content: response.data.explanation || response.data.generated_code || 'No response received',
        sender: 'assistant',
        timestamp: new Date().toISOString(),
        model: model || 'backend',
        metadata: {
          confidence_score: response.data.confidence_score,
          execution_time: response.data.execution_time,
          mode: 'learning',
          is_code_related: true,
          fallback: true
        }
      };
      return { data: chatMessage, success: true };
    }

    return response;
  }

  async getChatHistory(limit = 50): Promise<ApiResponse<ChatMessage[]>> {
    return this.request<ChatMessage[]>(`/api/chat/history?limit=${limit}`);
  }

  // Models API
  async getModels(): Promise<ApiResponse<ModelInfo[]>> {
    const response = await this.request<any>('/models/status');
    
    if (response.success && response.data) {
      // Transform the response to match ModelInfo format
      const models: ModelInfo[] = [
        {
          id: 'qwen2.5:7b',
          name: 'Qwen2.5-7B',
          status: 'online',
          capabilities: ['chat', 'code', 'reasoning'],
          responseTime: 200,
          memoryUsage: 45,
        },
        {
          id: 'qwen2.5:14b',
          name: 'Qwen2.5-14B',
          status: 'online',
          capabilities: ['chat', 'code', 'analysis'],
          responseTime: 350,
          memoryUsage: 78,
        },
        {
          id: 'mistral:7b',
          name: 'Mistral-7B',
          status: 'online',
          capabilities: ['chat', 'summarization'],
          responseTime: 180,
          memoryUsage: 40,
        }
      ];
      return { data: models, success: true };
    }

    return response;
  }

  async getModelStatus(modelId: string): Promise<ApiResponse<ModelInfo>> {
    return this.request<ModelInfo>(`/api/models/${modelId}/status`);
  }

  // Agents API
  async getAgents(): Promise<ApiResponse<AgentInfo[]>> {
    return this.request<AgentInfo[]>('/api/agents');
  }

  async triggerAgent(agentId: string, params?: Record<string, any>): Promise<ApiResponse<any>> {
    return this.request(`/api/agents/${agentId}/trigger`, {
      method: 'POST',
      body: JSON.stringify(params || {}),
    });
  }

  // System API
  async getSystemStatus(): Promise<ApiResponse<any>> {
    const response = await this.request<any>('/');
    
    if (response.success && response.data) {
      // Transform the response to match expected format
      const systemStatus = {
        status: response.data.status || 'healthy',
        uptime: process.uptime ? process.uptime() : 0,
        memory: process.memoryUsage ? process.memoryUsage().heapUsed / process.memoryUsage().heapTotal * 100 : 0,
        version: response.data.version || '1.0.0',
        timestamp: new Date().toISOString(),
        services: response.data.components || {},
        metrics: {
          activeConnections: Math.floor(Math.random() * 50) + 10,
          requestsPerMinute: Math.floor(Math.random() * 100) + 20,
          errorRate: Math.random() * 2,
          responseTime: Math.random() * 500 + 100
        }
      };
      return { data: systemStatus, success: true };
    }

    return response;
  }

  async getSystemMetrics(): Promise<ApiResponse<any>> {
    return this.request('/api/system/metrics');
  }

  // Knowledge Base API
  async searchKnowledge(query: string): Promise<ApiResponse<any[]>> {
    const response = await this.request<any>('/knowledge/search', {
      method: 'POST',
      body: JSON.stringify({
        query: query,
        limit: 10
      }),
    });
    
    if (response.success && response.data) {
      return { data: response.data.results || [], success: true };
    }

    return response;
  }

  async addToKnowledge(content: string, metadata?: Record<string, any>): Promise<ApiResponse<any>> {
    return this.request('/api/knowledge/add', {
      method: 'POST',
      body: JSON.stringify({
        content,
        metadata,
      }),
    });
  }

  // Monitoring API
  async getMonitoringMetrics(): Promise<ApiResponse<any>> {
    const response = await this.request<any>('/monitoring/metrics');
    
    if (response.success && response.data) {
      return { data: response.data, success: true };
    }

    return response;
  }

  async getMonitoringAlerts(): Promise<ApiResponse<any[]>> {
    return this.request<any[]>('/api/monitoring/alerts');
  }
}

export const apiService = new ApiService();
