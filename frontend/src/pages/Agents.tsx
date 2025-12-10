import { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import {
  Bot, Plus, Play, Trash2, Copy, Download, MoreVertical, Search, Loader2
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { agentsApi } from '@/services/api';
import { useToast } from '@/hooks/use-toast';
import type { Agent } from '@/types';

export function Agents() {
  const [agents, setAgents] = useState<Agent[]>([]);
  const [filteredAgents, setFilteredAgents] = useState<Agent[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [deleteAgent, setDeleteAgent] = useState<Agent | null>(null);
  const navigate = useNavigate();
  const { toast } = useToast();

  useEffect(() => {
    loadAgents();
  }, []);

  useEffect(() => {
    if (searchQuery) {
      setFilteredAgents(
        agents.filter(
          (a) =>
            a.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
            a.description?.toLowerCase().includes(searchQuery.toLowerCase())
        )
      );
    } else {
      setFilteredAgents(agents);
    }
  }, [searchQuery, agents]);

  const loadAgents = async () => {
    try {
      const response = await agentsApi.list(1, 100);
      setAgents(response.agents);
      setFilteredAgents(response.agents);
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to load agents',
        variant: 'destructive',
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleDuplicate = async (agent: Agent) => {
    try {
      const newAgent = await agentsApi.duplicate(agent.id);
      toast({
        title: 'Agent duplicated',
        description: `Created ${newAgent.name}`,
      });
      loadAgents();
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to duplicate agent',
        variant: 'destructive',
      });
    }
  };

  const handleExport = async (agent: Agent) => {
    try {
      const config = await agentsApi.export(agent.id);
      const blob = new Blob([JSON.stringify(config, null, 2)], {
        type: 'application/json',
      });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${agent.name.toLowerCase().replace(/\s+/g, '-')}.json`;
      a.click();
      URL.revokeObjectURL(url);
      toast({
        title: 'Exported',
        description: `Agent configuration downloaded`,
      });
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to export agent',
        variant: 'destructive',
      });
    }
  };

  const handleDelete = async () => {
    if (!deleteAgent) return;
    try {
      await agentsApi.delete(deleteAgent.id);
      toast({
        title: 'Deleted',
        description: `Agent "${deleteAgent.name}" deleted`,
      });
      setDeleteAgent(null);
      loadAgents();
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to delete agent',
        variant: 'destructive',
      });
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return 'bg-green-500';
      case 'draft':
        return 'bg-yellow-500';
      case 'paused':
        return 'bg-orange-500';
      case 'archived':
        return 'bg-gray-500';
      default:
        return 'bg-gray-500';
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Agents</h1>
          <p className="text-muted-foreground">
            Create and manage your AI agents
          </p>
        </div>
        <Button asChild>
          <Link to="/app/agents/new">
            <Plus className="mr-2 h-4 w-4" />
            New Agent
          </Link>
        </Button>
      </div>

      <div className="flex items-center gap-4">
        <div className="relative flex-1 max-w-sm">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <Input
            placeholder="Search agents..."
            className="pl-9"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>
      </div>

      {isLoading ? (
        <div className="flex items-center justify-center py-12">
          <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
        </div>
      ) : filteredAgents.length === 0 ? (
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-12">
            <Bot className="h-12 w-12 text-muted-foreground" />
            <h3 className="mt-4 text-lg font-semibold">
              {searchQuery ? 'No agents found' : 'No agents yet'}
            </h3>
            <p className="text-muted-foreground text-center max-w-sm">
              {searchQuery
                ? 'Try adjusting your search query'
                : 'Create your first AI agent to start building intelligent workflows'}
            </p>
            {!searchQuery && (
              <Button asChild className="mt-4">
                <Link to="/app/agents/new">
                  <Plus className="mr-2 h-4 w-4" />
                  Create Agent
                </Link>
              </Button>
            )}
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {filteredAgents.map((agent) => (
            <Card
              key={agent.id}
              className="hover:border-primary/50 transition-colors cursor-pointer"
              onClick={() => navigate(`/app/agents/${agent.id}`)}
            >
              <CardHeader className="pb-2">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <div className={`w-2 h-2 rounded-full ${getStatusColor(agent.status)}`} />
                    <CardTitle className="text-base font-medium truncate">
                      {agent.name}
                    </CardTitle>
                  </div>
                  <DropdownMenu>
                    <DropdownMenuTrigger asChild onClick={(e) => e.stopPropagation()}>
                      <Button variant="ghost" size="icon" className="h-8 w-8">
                        <MoreVertical className="h-4 w-4" />
                      </Button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent align="end">
                      <DropdownMenuItem
                        onClick={(e) => {
                          e.stopPropagation();
                          navigate(`/app/agents/${agent.id}/chat`);
                        }}
                      >
                        <Play className="mr-2 h-4 w-4" />
                        Run Agent
                      </DropdownMenuItem>
                      <DropdownMenuItem
                        onClick={(e) => {
                          e.stopPropagation();
                          handleDuplicate(agent);
                        }}
                      >
                        <Copy className="mr-2 h-4 w-4" />
                        Duplicate
                      </DropdownMenuItem>
                      <DropdownMenuItem
                        onClick={(e) => {
                          e.stopPropagation();
                          handleExport(agent);
                        }}
                      >
                        <Download className="mr-2 h-4 w-4" />
                        Export
                      </DropdownMenuItem>
                      <DropdownMenuSeparator />
                      <DropdownMenuItem
                        className="text-destructive"
                        onClick={(e) => {
                          e.stopPropagation();
                          setDeleteAgent(agent);
                        }}
                      >
                        <Trash2 className="mr-2 h-4 w-4" />
                        Delete
                      </DropdownMenuItem>
                    </DropdownMenuContent>
                  </DropdownMenu>
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
                <div className="text-xs text-muted-foreground mt-2">
                  Updated {new Date(agent.updated_at).toLocaleDateString()}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      <Dialog open={!!deleteAgent} onOpenChange={() => setDeleteAgent(null)}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Delete Agent</DialogTitle>
            <DialogDescription>
              Are you sure you want to delete "{deleteAgent?.name}"? This action
              cannot be undone.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button variant="outline" onClick={() => setDeleteAgent(null)}>
              Cancel
            </Button>
            <Button variant="destructive" onClick={handleDelete}>
              Delete
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
