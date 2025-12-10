import { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Bot, Plus, Play, Clock, CheckCircle, XCircle, Loader2, MessageSquare, Code, Search } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { agentsApi } from '@/services/api';
import type { Agent, AgentCreateUpdate, ModelProvider } from '@/types';

// Template definitions for quick start
const AGENT_TEMPLATES: Array<{
  id: string;
  name: string;
  description: string;
  icon: typeof MessageSquare;
  config: AgentCreateUpdate;
}> = [
  {
    id: 'qa-assistant',
    name: 'Q&A Assistant',
    description: 'Simple question-answering agent',
    icon: MessageSquare,
    config: {
      name: 'Q&A Assistant',
      description: 'A helpful assistant that answers questions clearly and concisely.',
      system_prompt: 'You are a helpful Q&A assistant. Answer questions accurately and concisely. If you don\'t know something, say so rather than making up information.',
      model_provider: 'bedrock' as ModelProvider,
      model_id: 'anthropic.claude-3-sonnet-20240229-v1:0',
      temperature: 0.7,
      max_tokens: 2048,
      streaming_enabled: true,
      mcp_enabled: false,
      tools: [],
    },
  },
  {
    id: 'code-helper',
    name: 'Code Helper',
    description: 'Programming assistance with code tools',
    icon: Code,
    config: {
      name: 'Code Helper',
      description: 'An AI assistant specialized in helping with programming tasks.',
      system_prompt: 'You are an expert programmer. Help users with coding questions, debug issues, explain concepts, and write clean, efficient code. Always explain your reasoning and suggest best practices.',
      model_provider: 'bedrock' as ModelProvider,
      model_id: 'anthropic.claude-3-sonnet-20240229-v1:0',
      temperature: 0.3,
      max_tokens: 4096,
      streaming_enabled: true,
      mcp_enabled: false,
      tools: [],
    },
  },
  {
    id: 'research-agent',
    name: 'Research Agent',
    description: 'Web search and analysis capabilities',
    icon: Search,
    config: {
      name: 'Research Agent',
      description: 'An agent that can search the web and analyze information.',
      system_prompt: 'You are a research assistant. Help users find information, analyze data, and synthesize findings from multiple sources. Be thorough and cite your sources when possible.',
      model_provider: 'bedrock' as ModelProvider,
      model_id: 'anthropic.claude-3-sonnet-20240229-v1:0',
      temperature: 0.5,
      max_tokens: 4096,
      streaming_enabled: true,
      mcp_enabled: false,
      tools: [],
    },
  },
];

export function Dashboard() {
  const navigate = useNavigate();
  const [agents, setAgents] = useState<Agent[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isCreatingTemplate, setIsCreatingTemplate] = useState<string | null>(null);
  const [stats, setStats] = useState({
    total: 0,
    active: 0,
    draft: 0,
  });

  useEffect(() => {
    loadAgents();
  }, []);

  const loadAgents = async () => {
    try {
      const response = await agentsApi.list(1, 6);
      setAgents(response.agents);
      setStats({
        total: response.total,
        active: response.agents.filter(a => a.status === 'active').length,
        draft: response.agents.filter(a => a.status === 'draft').length,
      });
    } catch (error) {
      console.error('Failed to load agents:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const createFromTemplate = async (template: typeof AGENT_TEMPLATES[0]) => {
    setIsCreatingTemplate(template.id);
    try {
      const agent = await agentsApi.create(template.config);
      navigate(`/app/agents/${agent.id}`);
    } catch (error) {
      console.error('Failed to create agent from template:', error);
      alert('Failed to create agent. Please try again.');
    } finally {
      setIsCreatingTemplate(null);
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'active':
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'draft':
        return <Clock className="h-4 w-4 text-yellow-500" />;
      case 'paused':
        return <XCircle className="h-4 w-4 text-orange-500" />;
      default:
        return <Clock className="h-4 w-4 text-muted-foreground" />;
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Dashboard</h1>
          <p className="text-muted-foreground">
            Manage your AI agents and workflows
          </p>
        </div>
        <Button asChild>
          <Link to="/app/agents/new">
            <Plus className="mr-2 h-4 w-4" />
            New Agent
          </Link>
        </Button>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Total Agents</CardTitle>
            <Bot className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.total}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Active</CardTitle>
            <CheckCircle className="h-4 w-4 text-green-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.active}</div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium">Draft</CardTitle>
            <Clock className="h-4 w-4 text-yellow-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.draft}</div>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Recent Agents</CardTitle>
          <CardDescription>
            Your most recently created and updated agents
          </CardDescription>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="flex items-center justify-center py-8">
              <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
            </div>
          ) : agents.length === 0 ? (
            <div className="text-center py-8">
              <Bot className="mx-auto h-12 w-12 text-muted-foreground" />
              <h3 className="mt-4 text-lg font-semibold">No agents yet</h3>
              <p className="text-muted-foreground">
                Create your first AI agent to get started
              </p>
              <Button asChild className="mt-4">
                <Link to="/app/agents/new">
                  <Plus className="mr-2 h-4 w-4" />
                  Create Agent
                </Link>
              </Button>
            </div>
          ) : (
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              {agents.map((agent) => (
                <Card key={agent.id} className="hover:border-primary/50 transition-colors">
                  <CardHeader className="pb-2">
                    <div className="flex items-center justify-between">
                      <CardTitle className="text-base font-medium truncate">
                        {agent.name}
                      </CardTitle>
                      {getStatusIcon(agent.status)}
                    </div>
                    <CardDescription className="line-clamp-2">
                      {agent.description || 'No description'}
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="flex items-center justify-between text-sm text-muted-foreground">
                      <span className="capitalize">{agent.model_provider}</span>
                      <span>{agent.tools.length} tools</span>
                    </div>
                    <div className="flex gap-2 mt-4">
                      <Button variant="outline" size="sm" asChild className="flex-1">
                        <Link to={`/app/agents/${agent.id}`}>Edit</Link>
                      </Button>
                      <Button size="sm" asChild className="flex-1">
                        <Link to={`/app/agents/${agent.id}/chat`}>
                          <Play className="mr-1 h-3 w-3" />
                          Run
                        </Link>
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Quick Start Templates</CardTitle>
          <CardDescription>
            Pre-configured agents for common use cases - click to create
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-3">
            {AGENT_TEMPLATES.map((template) => {
              const Icon = template.icon;
              const isCreating = isCreatingTemplate === template.id;
              return (
                <Card
                  key={template.id}
                  className={`cursor-pointer hover:border-primary/50 transition-colors ${isCreating ? 'opacity-70' : ''}`}
                  onClick={() => !isCreatingTemplate && createFromTemplate(template)}
                >
                  <CardHeader>
                    <div className="flex items-center gap-2">
                      {isCreating ? (
                        <Loader2 className="h-5 w-5 animate-spin text-primary" />
                      ) : (
                        <Icon className="h-5 w-5 text-primary" />
                      )}
                      <CardTitle className="text-base">{template.name}</CardTitle>
                    </div>
                    <CardDescription>
                      {template.description}
                    </CardDescription>
                  </CardHeader>
                </Card>
              );
            })}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
