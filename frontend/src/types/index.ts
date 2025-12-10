export interface User {
  id: number;
  email: string;
  full_name: string | null;
  is_active: boolean;
  role: 'user' | 'admin';
  created_at: string;
  updated_at: string;
}

export interface Token {
  access_token: string;
  token_type: string;
  user: User;
}

export type ModelProvider = 'bedrock' | 'gemini' | 'ollama' | 'openai' | 'anthropic' | 'custom';
export type AgentStatus = 'draft' | 'active' | 'paused' | 'archived';
export type RunStatus = 'pending' | 'running' | 'completed' | 'failed' | 'cancelled';
export type ToolType = 'builtin' | 'custom' | 'mcp';

export interface AgentTool {
  id: number;
  tool_id: number;
  tool_name: string;
  tool_display_name: string;
  enabled: boolean;
  config: Record<string, unknown> | null;
}

export interface Agent {
  id: number;
  name: string;
  description: string | null;
  system_prompt: string | null;
  status: AgentStatus;
  model_provider: ModelProvider;
  model_id: string;
  model_config_json: Record<string, unknown> | null;
  temperature: number;
  max_tokens: number;
  streaming_enabled: boolean;
  mcp_enabled: boolean;
  mcp_config: Record<string, unknown> | null;
  is_template: boolean;
  owner_id: number | null;
  created_at: string;
  updated_at: string;
  tools: AgentTool[];
}

export interface AgentListResponse {
  agents: Agent[];
  total: number;
  page: number;
  per_page: number;
}

export interface AgentRun {
  id: number;
  agent_id: number;
  status: RunStatus;
  input_text: string;
  output_text: string | null;
  error_message: string | null;
  start_time: string | null;
  end_time: string | null;
  tokens_used: number | null;
  response_time_ms: number | null;
  conversation_history: Array<{ role: string; content: string }> | null;
  created_at: string;
}

export interface Tool {
  id: number;
  name: string;
  display_name: string;
  description: string | null;
  tool_type: ToolType;
  source_code: string | null;
  file_path: string | null;
  mcp_server_config: Record<string, unknown> | null;
  parameters_schema: Record<string, unknown> | null;
  is_global: boolean;
  owner_id: number | null;
  enabled: boolean;
  created_at: string;
  updated_at: string;
}

export interface APIKey {
  id: number;
  user_id: number;
  provider: ModelProvider;
  name: string;
  aws_region: string | null;
  ollama_host: string | null;
  created_at: string;
  updated_at: string;
}

export interface ModelInfo {
  id: string;
  name: string;
}

export interface ProviderInfo {
  id: ModelProvider;
  name: string;
  models: ModelInfo[];
}

export interface ModelsResponse {
  providers: ProviderInfo[];
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  status?: 'sending' | 'streaming' | 'complete' | 'error';
}

export interface WebSocketMessage {
  type: 'ready' | 'status' | 'chunk' | 'complete' | 'error' | 'history_cleared' | 'pong';
  agent_id?: number;
  agent_name?: string;
  status?: string;
  content?: string;
  message?: string;
  run_id?: number;
}

export interface AgentToolInput {
  tool_id: number;
  enabled: boolean;
  config?: Record<string, unknown>;
}

export interface AgentCreateUpdate {
  name: string;
  description?: string;
  system_prompt?: string;
  model_provider: ModelProvider;
  model_id: string;
  temperature: number;
  max_tokens: number;
  streaming_enabled: boolean;
  mcp_enabled: boolean;
  tools: AgentToolInput[];
}
