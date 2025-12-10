import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  RefreshCw,
  Package,
  GitBranch,
  AlertCircle,
  CheckCircle,
  Loader2,
  ExternalLink,
  Play,
  FileText,
  Bot,
  Copy,
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Switch } from '@/components/ui/switch';
import { agentsApi, sdkUpdateApi } from '@/services/api';
import { useToast } from '@/hooks/use-toast';
import type { Agent } from '@/types';

type WorkflowStep = 'idle' | 'checking' | 'analyzing' | 'updating' | 'complete' | 'error';

interface UpdateResult {
  success: boolean;
  response: string;
  currentVersion?: string;
  latestVersion?: string;
  targetVersion?: string;
}

export function SDKUpdate() {
  const navigate = useNavigate();
  const { toast } = useToast();

  const [workflowStep, setWorkflowStep] = useState<WorkflowStep>('idle');
  const [checkResult, setCheckResult] = useState<UpdateResult | null>(null);
  const [analyzeResult, setAnalyzeResult] = useState<UpdateResult | null>(null);
  const [updateResult, setUpdateResult] = useState<UpdateResult | null>(null);

  const [targetVersion, setTargetVersion] = useState('');
  const [repoName, setRepoName] = useState('');
  const [dryRun, setDryRun] = useState(true);

  const [templates, setTemplates] = useState<Agent[]>([]);
  const [isLoadingTemplates, setIsLoadingTemplates] = useState(true);

  useEffect(() => {
    loadTemplates();
  }, []);

  const loadTemplates = async () => {
    try {
      const response = await agentsApi.listTemplates();
      setTemplates(response.templates);
    } catch (error) {
      console.error('Failed to load templates:', error);
    } finally {
      setIsLoadingTemplates(false);
    }
  };

  const handleCheckUpdates = async () => {
    setWorkflowStep('checking');
    setCheckResult(null);
    setAnalyzeResult(null);
    setUpdateResult(null);

    try {
      const response = await sdkUpdateApi.checkForUpdates();
      setCheckResult({
        success: response.success,
        response: response.result.response,
      });
      setWorkflowStep('idle');
      toast({
        title: 'Check Complete',
        description: 'SDK version check completed successfully',
      });
    } catch (error) {
      setWorkflowStep('error');
      toast({
        title: 'Error',
        description: error instanceof Error ? error.message : 'Failed to check for updates',
        variant: 'destructive',
      });
    }
  };

  const handleAnalyzeVersion = async () => {
    if (!targetVersion) {
      toast({
        title: 'Error',
        description: 'Please enter a target version to analyze',
        variant: 'destructive',
      });
      return;
    }

    setWorkflowStep('analyzing');
    setAnalyzeResult(null);

    try {
      const response = await sdkUpdateApi.analyzeVersion(targetVersion);
      setAnalyzeResult({
        success: response.success,
        response: response.result.response,
        targetVersion: response.result.target_version,
      });
      setWorkflowStep('idle');
      toast({
        title: 'Analysis Complete',
        description: `Analysis for version ${targetVersion} completed`,
      });
    } catch (error) {
      setWorkflowStep('error');
      toast({
        title: 'Error',
        description: error instanceof Error ? error.message : 'Failed to analyze version',
        variant: 'destructive',
      });
    }
  };

  const handlePerformUpdate = async () => {
    if (!targetVersion || !repoName) {
      toast({
        title: 'Error',
        description: 'Please enter target version and repository name',
        variant: 'destructive',
      });
      return;
    }

    setWorkflowStep('updating');
    setUpdateResult(null);

    try {
      const response = await sdkUpdateApi.performUpdate(targetVersion, repoName, dryRun);
      setUpdateResult({
        success: response.success,
        response: response.result.response,
        targetVersion: response.result.target_version,
      });
      setWorkflowStep('complete');
      toast({
        title: dryRun ? 'Dry Run Complete' : 'Update Complete',
        description: dryRun
          ? 'Dry run completed - no changes made'
          : 'SDK update completed successfully',
      });
    } catch (error) {
      setWorkflowStep('error');
      toast({
        title: 'Error',
        description: error instanceof Error ? error.message : 'Failed to perform update',
        variant: 'destructive',
      });
    }
  };

  const handleCreateFromTemplate = async (template: Agent) => {
    try {
      const newAgent = await agentsApi.createFromTemplate(template.id);
      toast({
        title: 'Agent Created',
        description: `Created "${newAgent.name}" from template`,
      });
      navigate(`/app/agents/${newAgent.id}`);
    } catch (error) {
      toast({
        title: 'Error',
        description: error instanceof Error ? error.message : 'Failed to create agent from template',
        variant: 'destructive',
      });
    }
  };

  const getStepIcon = (step: WorkflowStep) => {
    switch (step) {
      case 'checking':
      case 'analyzing':
      case 'updating':
        return <Loader2 className="h-5 w-5 animate-spin" />;
      case 'complete':
        return <CheckCircle className="h-5 w-5 text-green-500" />;
      case 'error':
        return <AlertCircle className="h-5 w-5 text-destructive" />;
      default:
        return null;
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">SDK Auto-Update</h1>
        <p className="text-muted-foreground">
          Monitor and update the Strands SDK using AI-powered automation
        </p>
      </div>

      <Tabs defaultValue="workflow" className="space-y-4">
        <TabsList>
          <TabsTrigger value="workflow">
            <RefreshCw className="mr-2 h-4 w-4" />
            Update Workflow
          </TabsTrigger>
          <TabsTrigger value="templates">
            <Bot className="mr-2 h-4 w-4" />
            Agent Templates
          </TabsTrigger>
        </TabsList>

        <TabsContent value="workflow" className="space-y-4">
          {/* Step 1: Check for Updates */}
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Package className="h-5 w-5" />
                  <CardTitle>Step 1: Check for Updates</CardTitle>
                </div>
                {workflowStep === 'checking' && getStepIcon('checking')}
              </div>
              <CardDescription>
                Check if a new version of the Strands SDK is available
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <Button
                onClick={handleCheckUpdates}
                disabled={workflowStep !== 'idle' && workflowStep !== 'complete' && workflowStep !== 'error'}
              >
                {workflowStep === 'checking' ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Checking...
                  </>
                ) : (
                  <>
                    <RefreshCw className="mr-2 h-4 w-4" />
                    Check for Updates
                  </>
                )}
              </Button>

              {checkResult && (
                <Card className="bg-muted/50">
                  <CardHeader className="py-3">
                    <CardTitle className="text-sm flex items-center gap-2">
                      {checkResult.success ? (
                        <CheckCircle className="h-4 w-4 text-green-500" />
                      ) : (
                        <AlertCircle className="h-4 w-4 text-destructive" />
                      )}
                      Check Result
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="py-2">
                    <ScrollArea className="h-[200px]">
                      <pre className="text-sm whitespace-pre-wrap font-mono">
                        {checkResult.response}
                      </pre>
                    </ScrollArea>
                  </CardContent>
                </Card>
              )}
            </CardContent>
          </Card>

          {/* Step 2: Analyze Version */}
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <FileText className="h-5 w-5" />
                  <CardTitle>Step 2: Analyze Version</CardTitle>
                </div>
                {workflowStep === 'analyzing' && getStepIcon('analyzing')}
              </div>
              <CardDescription>
                Analyze release notes and breaking changes for a specific version
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex gap-4">
                <div className="flex-1 space-y-2">
                  <Label htmlFor="targetVersion">Target Version</Label>
                  <Input
                    id="targetVersion"
                    placeholder="e.g., 0.1.5"
                    value={targetVersion}
                    onChange={(e) => setTargetVersion(e.target.value)}
                  />
                </div>
                <div className="flex items-end">
                  <Button
                    onClick={handleAnalyzeVersion}
                    disabled={!targetVersion || (workflowStep !== 'idle' && workflowStep !== 'complete' && workflowStep !== 'error')}
                  >
                    {workflowStep === 'analyzing' ? (
                      <>
                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                        Analyzing...
                      </>
                    ) : (
                      <>
                        <FileText className="mr-2 h-4 w-4" />
                        Analyze
                      </>
                    )}
                  </Button>
                </div>
              </div>

              {analyzeResult && (
                <Card className="bg-muted/50">
                  <CardHeader className="py-3">
                    <CardTitle className="text-sm flex items-center gap-2">
                      {analyzeResult.success ? (
                        <CheckCircle className="h-4 w-4 text-green-500" />
                      ) : (
                        <AlertCircle className="h-4 w-4 text-destructive" />
                      )}
                      Analysis Result for v{analyzeResult.targetVersion}
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="py-2">
                    <ScrollArea className="h-[300px]">
                      <pre className="text-sm whitespace-pre-wrap font-mono">
                        {analyzeResult.response}
                      </pre>
                    </ScrollArea>
                  </CardContent>
                </Card>
              )}
            </CardContent>
          </Card>

          {/* Step 3: Perform Update */}
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <GitBranch className="h-5 w-5" />
                  <CardTitle>Step 3: Perform Update</CardTitle>
                </div>
                {workflowStep === 'updating' && getStepIcon('updating')}
                {workflowStep === 'complete' && getStepIcon('complete')}
              </div>
              <CardDescription>
                Create a branch, update requirements.txt, and create a pull request
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid gap-4 md:grid-cols-2">
                <div className="space-y-2">
                  <Label htmlFor="repoName">Repository (owner/repo)</Label>
                  <Input
                    id="repoName"
                    placeholder="e.g., your-org/strands-gui"
                    value={repoName}
                    onChange={(e) => setRepoName(e.target.value)}
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="updateVersion">Version to Update To</Label>
                  <Input
                    id="updateVersion"
                    placeholder="e.g., 0.1.5"
                    value={targetVersion}
                    onChange={(e) => setTargetVersion(e.target.value)}
                  />
                </div>
              </div>

              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <Switch
                    id="dryRun"
                    checked={dryRun}
                    onCheckedChange={setDryRun}
                  />
                  <Label htmlFor="dryRun" className="cursor-pointer">
                    Dry Run (preview changes without creating PR)
                  </Label>
                </div>

                <Button
                  onClick={handlePerformUpdate}
                  disabled={!targetVersion || !repoName || (workflowStep !== 'idle' && workflowStep !== 'complete' && workflowStep !== 'error')}
                  variant={dryRun ? 'outline' : 'default'}
                >
                  {workflowStep === 'updating' ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      {dryRun ? 'Running Preview...' : 'Updating...'}
                    </>
                  ) : (
                    <>
                      <Play className="mr-2 h-4 w-4" />
                      {dryRun ? 'Preview Update' : 'Perform Update'}
                    </>
                  )}
                </Button>
              </div>

              {updateResult && (
                <Card className={`${updateResult.success ? 'bg-green-500/10 border-green-500/20' : 'bg-destructive/10 border-destructive/20'}`}>
                  <CardHeader className="py-3">
                    <CardTitle className="text-sm flex items-center gap-2">
                      {updateResult.success ? (
                        <CheckCircle className="h-4 w-4 text-green-500" />
                      ) : (
                        <AlertCircle className="h-4 w-4 text-destructive" />
                      )}
                      {dryRun ? 'Dry Run Result' : 'Update Result'}
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="py-2">
                    <ScrollArea className="h-[300px]">
                      <pre className="text-sm whitespace-pre-wrap font-mono">
                        {updateResult.response}
                      </pre>
                    </ScrollArea>
                  </CardContent>
                </Card>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="templates" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Agent Templates</CardTitle>
              <CardDescription>
                Pre-configured agent templates that you can use as starting points
              </CardDescription>
            </CardHeader>
            <CardContent>
              {isLoadingTemplates ? (
                <div className="flex items-center justify-center py-8">
                  <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
                </div>
              ) : templates.length === 0 ? (
                <div className="text-center py-8 text-muted-foreground">
                  <Bot className="h-12 w-12 mx-auto mb-4 opacity-50" />
                  <p>No templates available yet</p>
                  <p className="text-sm">Templates will appear here once the system is initialized</p>
                </div>
              ) : (
                <div className="grid gap-4 md:grid-cols-2">
                  {templates.map((template) => (
                    <Card key={template.id} className="relative">
                      <CardHeader className="pb-2">
                        <div className="flex items-start justify-between">
                          <div>
                            <CardTitle className="text-base">{template.name}</CardTitle>
                            <CardDescription className="line-clamp-2 mt-1">
                              {template.description}
                            </CardDescription>
                          </div>
                        </div>
                      </CardHeader>
                      <CardContent className="space-y-3">
                        <div className="flex items-center gap-4 text-sm text-muted-foreground">
                          <span className="capitalize">{template.model_provider}</span>
                          <span>{template.tools.length} tools</span>
                        </div>
                        <div className="flex gap-2">
                          <Button
                            size="sm"
                            onClick={() => handleCreateFromTemplate(template)}
                          >
                            <Copy className="mr-2 h-3 w-3" />
                            Use Template
                          </Button>
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => {
                              // Show system prompt in a dialog or expand
                              toast({
                                title: template.name,
                                description: template.system_prompt?.slice(0, 200) + '...',
                              });
                            }}
                          >
                            <ExternalLink className="mr-2 h-3 w-3" />
                            View Details
                          </Button>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
