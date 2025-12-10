import { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import {
  Bot, Save, ArrowLeft, Play, Loader2, Wrench, Settings2, MessageSquare
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Slider } from '@/components/ui/slider';
import { Switch } from '@/components/ui/switch';
import { Checkbox } from '@/components/ui/checkbox';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { agentsApi, toolsApi, modelsApi } from '@/services/api';
import { useToast } from '@/hooks/use-toast';
import type { Tool, ProviderInfo, ModelProvider, AgentCreateUpdate } from '@/types';

export function AgentBuilder() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { toast } = useToast();
  const isEditing = !!id;

  const [isLoading, setIsLoading] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [providers, setProviders] = useState<ProviderInfo[]>([]);
  const [tools, setTools] = useState<Tool[]>([]);

  const [formData, setFormData] = useState({
    name: '',
    description: '',
    system_prompt: '',
    model_provider: 'bedrock' as ModelProvider,
    model_id: 'anthropic.claude-3-sonnet-20240229-v1:0',
    temperature: 0.7,
    max_tokens: 4096,
    streaming_enabled: true,
    mcp_enabled: false,
    selectedTools: [] as number[],
  });

  useEffect(() => {
    loadData();
  }, [id]);

  const loadData = async () => {
    setIsLoading(true);
    try {
      const [modelsRes, toolsRes] = await Promise.all([
        modelsApi.list(),
        toolsApi.list(),
      ]);
      setProviders(modelsRes.providers);
      setTools(toolsRes);

      if (isEditing) {
        const agent = await agentsApi.get(parseInt(id));
        setFormData({
          name: agent.name,
          description: agent.description || '',
          system_prompt: agent.system_prompt || '',
          model_provider: agent.model_provider,
          model_id: agent.model_id,
          temperature: agent.temperature,
          max_tokens: agent.max_tokens,
          streaming_enabled: agent.streaming_enabled,
          mcp_enabled: agent.mcp_enabled,
          selectedTools: agent.tools.filter(t => t.enabled).map(t => t.tool_id),
        });
      }
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to load data',
        variant: 'destructive',
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleSave = async () => {
    if (!formData.name.trim()) {
      toast({
        title: 'Validation Error',
        description: 'Agent name is required',
        variant: 'destructive',
      });
      return;
    }

    setIsSaving(true);
    try {
      const agentData: AgentCreateUpdate = {
        name: formData.name,
        description: formData.description || undefined,
        system_prompt: formData.system_prompt || undefined,
        model_provider: formData.model_provider,
        model_id: formData.model_id,
        temperature: formData.temperature,
        max_tokens: formData.max_tokens,
        streaming_enabled: formData.streaming_enabled,
        mcp_enabled: formData.mcp_enabled,
        tools: formData.selectedTools.map(toolId => ({
          tool_id: toolId,
          enabled: true,
        })),
      };

      if (isEditing) {
        await agentsApi.update(parseInt(id!), agentData);
        toast({
          title: 'Saved',
          description: 'Agent updated successfully',
        });
      } else {
        const newAgent = await agentsApi.create(agentData);
        toast({
          title: 'Created',
          description: 'Agent created successfully',
        });
        navigate(`/app/agents/${newAgent.id}`);
      }
    } catch (error: any) {
      toast({
        title: 'Error',
        description: error.message || 'Failed to save agent',
        variant: 'destructive',
      });
    } finally {
      setIsSaving(false);
    }
  };

  const selectedProvider = providers.find(p => p.id === formData.model_provider);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Button variant="ghost" size="icon" onClick={() => navigate('/app/agents')}>
            <ArrowLeft className="h-5 w-5" />
          </Button>
          <div>
            <h1 className="text-3xl font-bold">
              {isEditing ? 'Edit Agent' : 'New Agent'}
            </h1>
            <p className="text-muted-foreground">
              {isEditing ? 'Modify your agent configuration' : 'Create a new AI agent'}
            </p>
          </div>
        </div>
        <div className="flex gap-2">
          {isEditing && (
            <Button variant="outline" onClick={() => navigate(`/app/agents/${id}/chat`)}>
              <Play className="mr-2 h-4 w-4" />
              Run
            </Button>
          )}
          <Button onClick={handleSave} disabled={isSaving}>
            {isSaving ? (
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
            ) : (
              <Save className="mr-2 h-4 w-4" />
            )}
            Save
          </Button>
        </div>
      </div>

      <Tabs defaultValue="basic" className="space-y-4">
        <TabsList>
          <TabsTrigger value="basic">
            <Bot className="mr-2 h-4 w-4" />
            Basic Info
          </TabsTrigger>
          <TabsTrigger value="model">
            <Settings2 className="mr-2 h-4 w-4" />
            Model
          </TabsTrigger>
          <TabsTrigger value="tools">
            <Wrench className="mr-2 h-4 w-4" />
            Tools
          </TabsTrigger>
          <TabsTrigger value="prompt">
            <MessageSquare className="mr-2 h-4 w-4" />
            System Prompt
          </TabsTrigger>
        </TabsList>

        <TabsContent value="basic">
          <Card>
            <CardHeader>
              <CardTitle>Basic Information</CardTitle>
              <CardDescription>
                Set the name and description for your agent
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="name">Name *</Label>
                <Input
                  id="name"
                  placeholder="My Agent"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="description">Description</Label>
                <Textarea
                  id="description"
                  placeholder="Describe what this agent does..."
                  value={formData.description}
                  onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                />
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="model">
          <Card>
            <CardHeader>
              <CardTitle>Model Configuration</CardTitle>
              <CardDescription>
                Select the AI model and configure its parameters
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="grid gap-4 md:grid-cols-2">
                <div className="space-y-2">
                  <Label>Provider</Label>
                  <Select
                    value={formData.model_provider}
                    onValueChange={(value: ModelProvider) => {
                      const provider = providers.find(p => p.id === value);
                      setFormData({
                        ...formData,
                        model_provider: value,
                        model_id: provider?.models[0]?.id || '',
                      });
                    }}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Select provider" />
                    </SelectTrigger>
                    <SelectContent>
                      {providers.map((provider) => (
                        <SelectItem key={provider.id} value={provider.id}>
                          {provider.name}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label>Model</Label>
                  <Select
                    value={formData.model_id}
                    onValueChange={(value) => setFormData({ ...formData, model_id: value })}
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Select model" />
                    </SelectTrigger>
                    <SelectContent>
                      {selectedProvider?.models.map((model) => (
                        <SelectItem key={model.id} value={model.id}>
                          {model.name}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              </div>

              <div className="space-y-4">
                <div className="space-y-2">
                  <div className="flex justify-between">
                    <Label>Temperature</Label>
                    <span className="text-sm text-muted-foreground">
                      {formData.temperature}
                    </span>
                  </div>
                  <Slider
                    value={[formData.temperature]}
                    onValueChange={([value]) => setFormData({ ...formData, temperature: value })}
                    min={0}
                    max={2}
                    step={0.1}
                  />
                  <p className="text-xs text-muted-foreground">
                    Higher values make output more random, lower values more focused
                  </p>
                </div>

                <div className="space-y-2">
                  <div className="flex justify-between">
                    <Label>Max Tokens</Label>
                    <span className="text-sm text-muted-foreground">
                      {formData.max_tokens}
                    </span>
                  </div>
                  <Slider
                    value={[formData.max_tokens]}
                    onValueChange={([value]) => setFormData({ ...formData, max_tokens: value })}
                    min={256}
                    max={16384}
                    step={256}
                  />
                </div>
              </div>

              <div className="flex items-center justify-between">
                <div className="space-y-0.5">
                  <Label>Streaming</Label>
                  <p className="text-sm text-muted-foreground">
                    Enable real-time response streaming
                  </p>
                </div>
                <Switch
                  checked={formData.streaming_enabled}
                  onCheckedChange={(checked) =>
                    setFormData({ ...formData, streaming_enabled: checked })
                  }
                />
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="tools">
          <Card>
            <CardHeader>
              <CardTitle>Tools</CardTitle>
              <CardDescription>
                Select the tools your agent can use
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid gap-4 md:grid-cols-2">
                {tools.map((tool) => (
                  <div
                    key={tool.id}
                    className="flex items-start space-x-3 p-3 rounded-lg border"
                  >
                    <Checkbox
                      id={`tool-${tool.id}`}
                      checked={formData.selectedTools.includes(tool.id)}
                      onCheckedChange={(checked) => {
                        if (checked) {
                          setFormData({
                            ...formData,
                            selectedTools: [...formData.selectedTools, tool.id],
                          });
                        } else {
                          setFormData({
                            ...formData,
                            selectedTools: formData.selectedTools.filter(
                              (id) => id !== tool.id
                            ),
                          });
                        }
                      }}
                    />
                    <div className="space-y-1">
                      <Label
                        htmlFor={`tool-${tool.id}`}
                        className="font-medium cursor-pointer"
                      >
                        {tool.display_name}
                      </Label>
                      <p className="text-sm text-muted-foreground">
                        {tool.description || 'No description'}
                      </p>
                      <span className="text-xs text-muted-foreground capitalize">
                        {tool.tool_type}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
              {tools.length === 0 && (
                <p className="text-center text-muted-foreground py-8">
                  No tools available. Create custom tools in the Tools section.
                </p>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="prompt">
          <Card>
            <CardHeader>
              <CardTitle>System Prompt</CardTitle>
              <CardDescription>
                Define the personality and instructions for your agent
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Textarea
                placeholder="You are a helpful AI assistant..."
                className="min-h-[300px] font-mono text-sm"
                value={formData.system_prompt}
                onChange={(e) =>
                  setFormData({ ...formData, system_prompt: e.target.value })
                }
              />
              <p className="text-sm text-muted-foreground mt-2">
                The system prompt defines how your agent should behave and respond.
              </p>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
