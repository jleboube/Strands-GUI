import type {
  Token,
  Agent,
  AgentListResponse,
  AgentRun,
  Tool,
  APIKey,
  ModelsResponse,
  AgentCreateUpdate
} from '@/types';

const API_BASE = '/api';

class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
    this.name = 'ApiError';
  }
}

async function fetchWithAuth<T>(
  url: string,
  options: RequestInit = {}
): Promise<T> {
  const token = localStorage.getItem('token');

  const headers: HeadersInit = {
    'Content-Type': 'application/json',
    ...options.headers,
  };

  if (token) {
    (headers as Record<string, string>)['Authorization'] = `Bearer ${token}`;
  }

  const response = await fetch(`${API_BASE}${url}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw new ApiError(response.status, error.detail || 'Request failed');
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return response.json();
}

// Auth API
export const authApi = {
  register: (email: string, password: string, fullName?: string) =>
    fetchWithAuth<Token>('/auth/register', {
      method: 'POST',
      body: JSON.stringify({ email, password, full_name: fullName }),
    }),

  login: (email: string, password: string) =>
    fetchWithAuth<Token>('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    }),

  me: () => fetchWithAuth<Token['user']>('/auth/me'),

  updateProfile: (data: { email?: string; full_name?: string; password?: string }) =>
    fetchWithAuth<Token['user']>('/auth/me', {
      method: 'PUT',
      body: JSON.stringify(data),
    }),
};

// Agents API
export const agentsApi = {
  list: (page = 1, perPage = 20) =>
    fetchWithAuth<AgentListResponse>(`/agents?page=${page}&per_page=${perPage}`),

  get: (id: number) => fetchWithAuth<Agent>(`/agents/${id}`),

  create: (data: AgentCreateUpdate) =>
    fetchWithAuth<Agent>('/agents', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  update: (id: number, data: AgentCreateUpdate) =>
    fetchWithAuth<Agent>(`/agents/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    }),

  delete: (id: number) =>
    fetchWithAuth<void>(`/agents/${id}`, { method: 'DELETE' }),

  run: (id: number, inputText: string, conversationHistory?: Array<{ role: string; content: string }>) =>
    fetchWithAuth<AgentRun>(`/agents/${id}/run`, {
      method: 'POST',
      body: JSON.stringify({ input_text: inputText, conversation_history: conversationHistory }),
    }),

  listRuns: (id: number, limit = 50) =>
    fetchWithAuth<AgentRun[]>(`/agents/${id}/runs?limit=${limit}`),

  duplicate: (id: number) =>
    fetchWithAuth<Agent>(`/agents/${id}/duplicate`, { method: 'POST' }),

  export: (id: number) => fetchWithAuth<Record<string, unknown>>(`/agents/${id}/export`),

  // Template methods
  listTemplates: () => fetchWithAuth<{ templates: Agent[] }>('/agents/templates/list'),

  createFromTemplate: (templateId: number, name?: string) =>
    fetchWithAuth<Agent>('/agents/templates/create-from', {
      method: 'POST',
      body: JSON.stringify({ template_id: templateId, name }),
    }),
};

// SDK Update API
export const sdkUpdateApi = {
  checkForUpdates: () =>
    fetchWithAuth<{ success: boolean; result: { response: string } }>('/agents/sdk-update/check', {
      method: 'POST',
    }),

  analyzeVersion: (version: string) =>
    fetchWithAuth<{ success: boolean; result: { response: string; target_version: string } }>(
      `/agents/sdk-update/analyze/${version}`,
      { method: 'POST' }
    ),

  performUpdate: (version: string, repo: string, dryRun = true) =>
    fetchWithAuth<{ success: boolean; result: { response: string; target_version: string; repo: string; dry_run: boolean } }>(
      `/agents/sdk-update/perform?version=${encodeURIComponent(version)}&repo=${encodeURIComponent(repo)}&dry_run=${dryRun}`,
      { method: 'POST' }
    ),
};

// Tools API
export const toolsApi = {
  list: () => fetchWithAuth<Tool[]>('/tools'),

  listBuiltin: () => fetchWithAuth<Tool[]>('/tools/builtin'),

  get: (id: number) => fetchWithAuth<Tool>(`/tools/${id}`),

  create: (data: Partial<Tool>) =>
    fetchWithAuth<Tool>('/tools', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  update: (id: number, data: Partial<Tool>) =>
    fetchWithAuth<Tool>(`/tools/${id}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    }),

  delete: (id: number) =>
    fetchWithAuth<void>(`/tools/${id}`, { method: 'DELETE' }),

  validate: (data: Partial<Tool>) =>
    fetchWithAuth<{ valid: boolean; message: string }>('/tools/validate', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
};

// API Keys API
export const apiKeysApi = {
  list: () => fetchWithAuth<APIKey[]>('/api-keys'),

  create: (data: {
    provider: string;
    name: string;
    api_key?: string;
    aws_access_key_id?: string;
    aws_secret_access_key?: string;
    aws_region?: string;
    ollama_host?: string;
  }) =>
    fetchWithAuth<APIKey>('/api-keys', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  delete: (id: number) =>
    fetchWithAuth<void>(`/api-keys/${id}`, { method: 'DELETE' }),
};

// Models API
export const modelsApi = {
  list: () => fetchWithAuth<ModelsResponse>('/models'),
};

// Health API
export const healthApi = {
  check: () => fetch(`${API_BASE.replace('/api', '')}/health`).then(r => r.json()),
};

export { ApiError };
