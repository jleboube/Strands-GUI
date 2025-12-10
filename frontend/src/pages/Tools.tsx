import { useEffect, useState } from 'react';
import {
  Plus, Wrench, Trash2, Code, Settings, Loader2
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { toolsApi } from '@/services/api';
import { useToast } from '@/hooks/use-toast';
import type { Tool } from '@/types';

export function Tools() {
  const [tools, setTools] = useState<Tool[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [editingTool, setEditingTool] = useState<Tool | null>(null);
  const [isSaving, setIsSaving] = useState(false);
  const { toast } = useToast();

  const [formData, setFormData] = useState({
    name: '',
    display_name: '',
    description: '',
    source_code: '',
  });

  useEffect(() => {
    loadTools();
  }, []);

  const loadTools = async () => {
    try {
      const toolsList = await toolsApi.list();
      setTools(toolsList);
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to load tools',
        variant: 'destructive',
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleOpenDialog = (tool?: Tool) => {
    if (tool) {
      setEditingTool(tool);
      setFormData({
        name: tool.name,
        display_name: tool.display_name,
        description: tool.description || '',
        source_code: tool.source_code || '',
      });
    } else {
      setEditingTool(null);
      setFormData({
        name: '',
        display_name: '',
        description: '',
        source_code: `from strands import tool

@tool
def my_tool(param: str) -> str:
    """Description of what this tool does.

    Args:
        param: Description of the parameter

    Returns:
        Description of the return value
    """
    return f"Result: {param}"
`,
      });
    }
    setIsDialogOpen(true);
  };

  const handleSave = async () => {
    if (!formData.name.trim() || !formData.display_name.trim()) {
      toast({
        title: 'Validation Error',
        description: 'Name and display name are required',
        variant: 'destructive',
      });
      return;
    }

    setIsSaving(true);
    try {
      // Validate source code first
      const validation = await toolsApi.validate({
        name: formData.name,
        display_name: formData.display_name,
        source_code: formData.source_code,
      });

      if (!validation.valid) {
        toast({
          title: 'Invalid Source Code',
          description: validation.message,
          variant: 'destructive',
        });
        setIsSaving(false);
        return;
      }

      if (editingTool) {
        await toolsApi.update(editingTool.id, {
          name: formData.name,
          display_name: formData.display_name,
          description: formData.description,
          source_code: formData.source_code,
        });
        toast({
          title: 'Updated',
          description: 'Tool updated successfully',
        });
      } else {
        await toolsApi.create({
          name: formData.name,
          display_name: formData.display_name,
          description: formData.description,
          tool_type: 'custom',
          source_code: formData.source_code,
        });
        toast({
          title: 'Created',
          description: 'Tool created successfully',
        });
      }

      setIsDialogOpen(false);
      loadTools();
    } catch (error: any) {
      toast({
        title: 'Error',
        description: error.message || 'Failed to save tool',
        variant: 'destructive',
      });
    } finally {
      setIsSaving(false);
    }
  };

  const handleDelete = async (tool: Tool) => {
    if (!confirm(`Delete tool "${tool.display_name}"?`)) return;

    try {
      await toolsApi.delete(tool.id);
      toast({
        title: 'Deleted',
        description: 'Tool deleted successfully',
      });
      loadTools();
    } catch (error: any) {
      toast({
        title: 'Error',
        description: error.message || 'Failed to delete tool',
        variant: 'destructive',
      });
    }
  };

  const builtinTools = tools.filter((t) => t.tool_type === 'builtin');
  const customTools = tools.filter((t) => t.tool_type === 'custom');

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Tools</h1>
          <p className="text-muted-foreground">
            Manage tools that agents can use
          </p>
        </div>
        <Button onClick={() => handleOpenDialog()}>
          <Plus className="mr-2 h-4 w-4" />
          New Tool
        </Button>
      </div>

      {isLoading ? (
        <div className="flex items-center justify-center py-12">
          <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
        </div>
      ) : (
        <Tabs defaultValue="builtin">
          <TabsList>
            <TabsTrigger value="builtin">
              Built-in ({builtinTools.length})
            </TabsTrigger>
            <TabsTrigger value="custom">
              Custom ({customTools.length})
            </TabsTrigger>
          </TabsList>

          <TabsContent value="builtin" className="mt-4">
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              {builtinTools.map((tool) => (
                <Card key={tool.id}>
                  <CardHeader className="pb-2">
                    <div className="flex items-center gap-2">
                      <Wrench className="h-4 w-4 text-primary" />
                      <CardTitle className="text-base">{tool.display_name}</CardTitle>
                    </div>
                    <CardDescription>{tool.description}</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <span className="text-xs bg-muted px-2 py-1 rounded">
                      Built-in
                    </span>
                  </CardContent>
                </Card>
              ))}
            </div>
          </TabsContent>

          <TabsContent value="custom" className="mt-4">
            {customTools.length === 0 ? (
              <Card>
                <CardContent className="flex flex-col items-center justify-center py-12">
                  <Code className="h-12 w-12 text-muted-foreground" />
                  <h3 className="mt-4 text-lg font-semibold">No custom tools</h3>
                  <p className="text-muted-foreground text-center max-w-sm">
                    Create custom Python tools to extend your agents' capabilities
                  </p>
                  <Button className="mt-4" onClick={() => handleOpenDialog()}>
                    <Plus className="mr-2 h-4 w-4" />
                    Create Tool
                  </Button>
                </CardContent>
              </Card>
            ) : (
              <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                {customTools.map((tool) => (
                  <Card key={tool.id}>
                    <CardHeader className="pb-2">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <Code className="h-4 w-4 text-primary" />
                          <CardTitle className="text-base">{tool.display_name}</CardTitle>
                        </div>
                        <div className="flex gap-1">
                          <Button
                            variant="ghost"
                            size="icon"
                            className="h-8 w-8"
                            onClick={() => handleOpenDialog(tool)}
                          >
                            <Settings className="h-4 w-4" />
                          </Button>
                          <Button
                            variant="ghost"
                            size="icon"
                            className="h-8 w-8 text-destructive"
                            onClick={() => handleDelete(tool)}
                          >
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        </div>
                      </div>
                      <CardDescription>{tool.description || 'No description'}</CardDescription>
                    </CardHeader>
                    <CardContent>
                      <span className="text-xs bg-secondary px-2 py-1 rounded">
                        Custom
                      </span>
                    </CardContent>
                  </Card>
                ))}
              </div>
            )}
          </TabsContent>
        </Tabs>
      )}

      <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
        <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>
              {editingTool ? 'Edit Tool' : 'Create Tool'}
            </DialogTitle>
            <DialogDescription>
              Create a custom Python tool for your agents
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-4">
            <div className="grid gap-4 md:grid-cols-2">
              <div className="space-y-2">
                <Label htmlFor="name">Name (identifier)</Label>
                <Input
                  id="name"
                  placeholder="my_tool"
                  value={formData.name}
                  onChange={(e) =>
                    setFormData({
                      ...formData,
                      name: e.target.value.toLowerCase().replace(/\s+/g, '_'),
                    })
                  }
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="display_name">Display Name</Label>
                <Input
                  id="display_name"
                  placeholder="My Tool"
                  value={formData.display_name}
                  onChange={(e) =>
                    setFormData({ ...formData, display_name: e.target.value })
                  }
                />
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="description">Description</Label>
              <Input
                id="description"
                placeholder="Describe what this tool does..."
                value={formData.description}
                onChange={(e) =>
                  setFormData({ ...formData, description: e.target.value })
                }
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="source_code">Source Code (Python)</Label>
              <Textarea
                id="source_code"
                className="min-h-[300px] font-mono text-sm"
                placeholder="Write your Python tool code..."
                value={formData.source_code}
                onChange={(e) =>
                  setFormData({ ...formData, source_code: e.target.value })
                }
              />
              <p className="text-xs text-muted-foreground">
                Use the @tool decorator from strands to define your tool function
              </p>
            </div>
          </div>

          <DialogFooter>
            <Button variant="outline" onClick={() => setIsDialogOpen(false)}>
              Cancel
            </Button>
            <Button onClick={handleSave} disabled={isSaving}>
              {isSaving && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              {editingTool ? 'Update' : 'Create'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
