import { useEffect, useState } from 'react';
import { Plus, Key, Trash2, Loader2, Eye, EyeOff } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { apiKeysApi } from '@/services/api';
import { useToast } from '@/hooks/use-toast';
import type { APIKey, ModelProvider } from '@/types';

const PROVIDERS = [
  { id: 'bedrock', name: 'Amazon Bedrock', requiresAwsCreds: true },
  { id: 'gemini', name: 'Google Gemini', requiresApiKey: true },
  { id: 'openai', name: 'OpenAI', requiresApiKey: true },
  { id: 'anthropic', name: 'Anthropic', requiresApiKey: true },
  { id: 'ollama', name: 'Ollama (Local)', requiresHost: true },
];

export function APIKeys() {
  const [apiKeys, setApiKeys] = useState<APIKey[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const { toast } = useToast();

  const [formData, setFormData] = useState({
    provider: '' as ModelProvider | '',
    name: '',
    api_key: '',
    aws_access_key_id: '',
    aws_secret_access_key: '',
    aws_region: 'us-east-1',
    ollama_host: 'http://localhost:11434',
  });

  const [showSecrets, setShowSecrets] = useState<Record<string, boolean>>({});

  useEffect(() => {
    loadApiKeys();
  }, []);

  const loadApiKeys = async () => {
    try {
      const keys = await apiKeysApi.list();
      setApiKeys(keys);
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to load API keys',
        variant: 'destructive',
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleOpenDialog = () => {
    setFormData({
      provider: '',
      name: '',
      api_key: '',
      aws_access_key_id: '',
      aws_secret_access_key: '',
      aws_region: 'us-east-1',
      ollama_host: 'http://localhost:11434',
    });
    setIsDialogOpen(true);
  };

  const handleSave = async () => {
    if (!formData.provider || !formData.name.trim()) {
      toast({
        title: 'Validation Error',
        description: 'Provider and name are required',
        variant: 'destructive',
      });
      return;
    }

    setIsSaving(true);
    try {
      await apiKeysApi.create({
        provider: formData.provider,
        name: formData.name,
        api_key: formData.api_key || undefined,
        aws_access_key_id: formData.aws_access_key_id || undefined,
        aws_secret_access_key: formData.aws_secret_access_key || undefined,
        aws_region: formData.aws_region || undefined,
        ollama_host: formData.ollama_host || undefined,
      });
      toast({
        title: 'Saved',
        description: 'API key saved successfully',
      });
      setIsDialogOpen(false);
      loadApiKeys();
    } catch (error: any) {
      toast({
        title: 'Error',
        description: error.message || 'Failed to save API key',
        variant: 'destructive',
      });
    } finally {
      setIsSaving(false);
    }
  };

  const handleDelete = async (key: APIKey) => {
    if (!confirm(`Delete API key "${key.name}"?`)) return;

    try {
      await apiKeysApi.delete(key.id);
      toast({
        title: 'Deleted',
        description: 'API key deleted successfully',
      });
      loadApiKeys();
    } catch (error: any) {
      toast({
        title: 'Error',
        description: error.message || 'Failed to delete API key',
        variant: 'destructive',
      });
    }
  };

  const selectedProvider = PROVIDERS.find((p) => p.id === formData.provider);

  const getProviderIcon = (_provider: string) => {
    return <Key className="h-4 w-4" />;
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">API Keys</h1>
          <p className="text-muted-foreground">
            Manage credentials for AI model providers
          </p>
        </div>
        <Button onClick={handleOpenDialog}>
          <Plus className="mr-2 h-4 w-4" />
          Add API Key
        </Button>
      </div>

      {isLoading ? (
        <div className="flex items-center justify-center py-12">
          <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
        </div>
      ) : apiKeys.length === 0 ? (
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-12">
            <Key className="h-12 w-12 text-muted-foreground" />
            <h3 className="mt-4 text-lg font-semibold">No API keys configured</h3>
            <p className="text-muted-foreground text-center max-w-sm">
              Add API keys for your AI model providers to start using agents
            </p>
            <Button className="mt-4" onClick={handleOpenDialog}>
              <Plus className="mr-2 h-4 w-4" />
              Add API Key
            </Button>
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {apiKeys.map((key) => (
            <Card key={key.id}>
              <CardHeader className="pb-2">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    {getProviderIcon(key.provider)}
                    <CardTitle className="text-base">{key.name}</CardTitle>
                  </div>
                  <Button
                    variant="ghost"
                    size="icon"
                    className="h-8 w-8 text-destructive"
                    onClick={() => handleDelete(key)}
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </div>
                <CardDescription className="capitalize">
                  {PROVIDERS.find((p) => p.id === key.provider)?.name || key.provider}
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="text-sm text-muted-foreground space-y-1">
                  {key.aws_region && <p>Region: {key.aws_region}</p>}
                  {key.ollama_host && <p>Host: {key.ollama_host}</p>}
                  <p className="text-xs">
                    Added {new Date(key.created_at).toLocaleDateString()}
                  </p>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Add API Key</DialogTitle>
            <DialogDescription>
              Configure credentials for an AI model provider
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-4">
            <div className="space-y-2">
              <Label>Provider</Label>
              <Select
                value={formData.provider}
                onValueChange={(value: ModelProvider) =>
                  setFormData({ ...formData, provider: value })
                }
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select provider" />
                </SelectTrigger>
                <SelectContent>
                  {PROVIDERS.map((provider) => (
                    <SelectItem key={provider.id} value={provider.id}>
                      {provider.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="name">Name</Label>
              <Input
                id="name"
                placeholder="My API Key"
                value={formData.name}
                onChange={(e) =>
                  setFormData({ ...formData, name: e.target.value })
                }
              />
            </div>

            {selectedProvider?.requiresApiKey && (
              <div className="space-y-2">
                <Label htmlFor="api_key">API Key</Label>
                <div className="relative">
                  <Input
                    id="api_key"
                    type={showSecrets.api_key ? 'text' : 'password'}
                    placeholder="sk-..."
                    value={formData.api_key}
                    onChange={(e) =>
                      setFormData({ ...formData, api_key: e.target.value })
                    }
                  />
                  <Button
                    type="button"
                    variant="ghost"
                    size="icon"
                    className="absolute right-0 top-0 h-full"
                    onClick={() =>
                      setShowSecrets({ ...showSecrets, api_key: !showSecrets.api_key })
                    }
                  >
                    {showSecrets.api_key ? (
                      <EyeOff className="h-4 w-4" />
                    ) : (
                      <Eye className="h-4 w-4" />
                    )}
                  </Button>
                </div>
              </div>
            )}

            {selectedProvider?.requiresAwsCreds && (
              <>
                <div className="space-y-2">
                  <Label htmlFor="aws_access_key_id">AWS Access Key ID</Label>
                  <Input
                    id="aws_access_key_id"
                    placeholder="AKIA..."
                    value={formData.aws_access_key_id}
                    onChange={(e) =>
                      setFormData({ ...formData, aws_access_key_id: e.target.value })
                    }
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="aws_secret_access_key">AWS Secret Access Key</Label>
                  <div className="relative">
                    <Input
                      id="aws_secret_access_key"
                      type={showSecrets.aws_secret ? 'text' : 'password'}
                      placeholder="..."
                      value={formData.aws_secret_access_key}
                      onChange={(e) =>
                        setFormData({
                          ...formData,
                          aws_secret_access_key: e.target.value,
                        })
                      }
                    />
                    <Button
                      type="button"
                      variant="ghost"
                      size="icon"
                      className="absolute right-0 top-0 h-full"
                      onClick={() =>
                        setShowSecrets({
                          ...showSecrets,
                          aws_secret: !showSecrets.aws_secret,
                        })
                      }
                    >
                      {showSecrets.aws_secret ? (
                        <EyeOff className="h-4 w-4" />
                      ) : (
                        <Eye className="h-4 w-4" />
                      )}
                    </Button>
                  </div>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="aws_region">AWS Region</Label>
                  <Select
                    value={formData.aws_region}
                    onValueChange={(value) =>
                      setFormData({ ...formData, aws_region: value })
                    }
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="us-east-1">US East (N. Virginia)</SelectItem>
                      <SelectItem value="us-west-2">US West (Oregon)</SelectItem>
                      <SelectItem value="eu-west-1">EU (Ireland)</SelectItem>
                      <SelectItem value="ap-northeast-1">Asia Pacific (Tokyo)</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </>
            )}

            {selectedProvider?.requiresHost && (
              <div className="space-y-2">
                <Label htmlFor="ollama_host">Ollama Host</Label>
                <Input
                  id="ollama_host"
                  placeholder="http://localhost:11434"
                  value={formData.ollama_host}
                  onChange={(e) =>
                    setFormData({ ...formData, ollama_host: e.target.value })
                  }
                />
              </div>
            )}
          </div>

          <DialogFooter>
            <Button variant="outline" onClick={() => setIsDialogOpen(false)}>
              Cancel
            </Button>
            <Button onClick={handleSave} disabled={isSaving}>
              {isSaving && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              Save
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
