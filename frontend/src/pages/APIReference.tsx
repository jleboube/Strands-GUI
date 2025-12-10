import { Link } from 'react-router-dom';
import {
  Code,
  ChevronLeft,
  ArrowRight,
  Lock,
  User,
  Bot,
  Wrench,
  Key,
  MessageSquare,
  Play,
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';

interface Endpoint {
  method: 'GET' | 'POST' | 'PUT' | 'DELETE';
  path: string;
  description: string;
  auth: boolean;
}

interface APISection {
  title: string;
  icon: React.ElementType;
  description: string;
  endpoints: Endpoint[];
}

const apiSections: APISection[] = [
  {
    title: 'Authentication',
    icon: Lock,
    description: 'User authentication and session management.',
    endpoints: [
      { method: 'POST', path: '/api/auth/register', description: 'Register a new user', auth: false },
      { method: 'POST', path: '/api/auth/login', description: 'Login and receive JWT token', auth: false },
      { method: 'GET', path: '/api/auth/me', description: 'Get current user information', auth: true },
      { method: 'POST', path: '/api/auth/logout', description: 'Logout current user', auth: true },
    ],
  },
  {
    title: 'Users',
    icon: User,
    description: 'User profile and settings management.',
    endpoints: [
      { method: 'GET', path: '/api/users/me', description: 'Get current user profile', auth: true },
      { method: 'PUT', path: '/api/users/me', description: 'Update current user profile', auth: true },
      { method: 'PUT', path: '/api/users/me/password', description: 'Change password', auth: true },
    ],
  },
  {
    title: 'Agents',
    icon: Bot,
    description: 'AI agent CRUD operations and management.',
    endpoints: [
      { method: 'GET', path: '/api/agents', description: 'List all agents', auth: true },
      { method: 'POST', path: '/api/agents', description: 'Create a new agent', auth: true },
      { method: 'GET', path: '/api/agents/{id}', description: 'Get agent by ID', auth: true },
      { method: 'PUT', path: '/api/agents/{id}', description: 'Update an agent', auth: true },
      { method: 'DELETE', path: '/api/agents/{id}', description: 'Delete an agent', auth: true },
      { method: 'GET', path: '/api/agents/templates/list', description: 'List available templates', auth: true },
      { method: 'POST', path: '/api/agents/templates/create-from', description: 'Create agent from template', auth: true },
    ],
  },
  {
    title: 'Agent Runs',
    icon: Play,
    description: 'Execute agents and manage run history.',
    endpoints: [
      { method: 'POST', path: '/api/agents/{id}/run', description: 'Run an agent', auth: true },
      { method: 'GET', path: '/api/agents/{id}/runs', description: 'Get agent run history', auth: true },
      { method: 'GET', path: '/api/agents/{id}/runs/{run_id}', description: 'Get specific run details', auth: true },
    ],
  },
  {
    title: 'Tools',
    icon: Wrench,
    description: 'Tool management and discovery.',
    endpoints: [
      { method: 'GET', path: '/api/tools', description: 'List all available tools', auth: true },
      { method: 'POST', path: '/api/tools', description: 'Create a custom tool', auth: true },
      { method: 'GET', path: '/api/tools/{id}', description: 'Get tool by ID', auth: true },
      { method: 'PUT', path: '/api/tools/{id}', description: 'Update a tool', auth: true },
      { method: 'DELETE', path: '/api/tools/{id}', description: 'Delete a tool', auth: true },
    ],
  },
  {
    title: 'API Keys',
    icon: Key,
    description: 'Model provider API key management.',
    endpoints: [
      { method: 'GET', path: '/api/api-keys', description: 'List all API keys', auth: true },
      { method: 'POST', path: '/api/api-keys', description: 'Create a new API key', auth: true },
      { method: 'DELETE', path: '/api/api-keys/{id}', description: 'Delete an API key', auth: true },
      { method: 'GET', path: '/api/api-keys/providers', description: 'List configured providers', auth: true },
      { method: 'GET', path: '/api/api-keys/models', description: 'List available models', auth: true },
    ],
  },
  {
    title: 'Chat',
    icon: MessageSquare,
    description: 'Real-time chat with agents via WebSocket.',
    endpoints: [
      { method: 'GET', path: '/api/ws/{agent_id}', description: 'WebSocket connection for chat', auth: true },
      { method: 'POST', path: '/api/agents/{id}/chat/clear', description: 'Clear conversation history', auth: true },
    ],
  },
];

const methodColors: Record<string, string> = {
  GET: 'bg-blue-500/10 text-blue-500 border-blue-500/20',
  POST: 'bg-green-500/10 text-green-500 border-green-500/20',
  PUT: 'bg-yellow-500/10 text-yellow-500 border-yellow-500/20',
  DELETE: 'bg-red-500/10 text-red-500 border-red-500/20',
};

export function APIReference() {
  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b border-border bg-card/50 backdrop-blur-sm sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Link to="/landing">
              <Button variant="ghost" size="sm">
                <ChevronLeft className="h-4 w-4 mr-1" />
                Back to Home
              </Button>
            </Link>
            <div className="h-6 w-px bg-border" />
            <h1 className="text-xl font-bold flex items-center gap-2">
              <Code className="h-5 w-5 text-primary" />
              API Reference
            </h1>
          </div>
          <div className="flex items-center gap-2">
            <Link to="/app">
              <Button>
                Open App
                <ArrowRight className="ml-2 h-4 w-4" />
              </Button>
            </Link>
          </div>
        </div>
      </header>

      {/* Hero */}
      <section className="py-16 px-4 border-b border-border">
        <div className="container mx-auto max-w-4xl text-center">
          <h1 className="text-4xl font-bold mb-4">API Reference</h1>
          <p className="text-xl text-muted-foreground mb-8">
            Complete REST API documentation for Strands GUI.
          </p>
          <div className="flex justify-center gap-4">
            <Link to="/documentation">
              <Button variant="outline">View Documentation</Button>
            </Link>
          </div>
        </div>
      </section>

      {/* Base URL */}
      <section className="py-8 px-4 border-b border-border bg-muted/30">
        <div className="container mx-auto max-w-4xl">
          <h2 className="text-lg font-semibold mb-3">Base URL</h2>
          <pre className="bg-card border border-border p-4 rounded-lg text-sm overflow-x-auto">
            <code>http://localhost:8847/api</code>
          </pre>
          <p className="text-sm text-muted-foreground mt-2">
            All API endpoints are prefixed with <code>/api</code>. Replace <code>localhost:8847</code> with your deployment URL.
          </p>
        </div>
      </section>

      {/* Authentication */}
      <section className="py-8 px-4 border-b border-border">
        <div className="container mx-auto max-w-4xl">
          <h2 className="text-lg font-semibold mb-3">Authentication</h2>
          <div className="bg-card border border-border p-4 rounded-lg space-y-3">
            <p className="text-sm text-muted-foreground">
              Most endpoints require authentication via JWT token. Include the token in the Authorization header:
            </p>
            <pre className="bg-muted p-3 rounded-md text-sm overflow-x-auto">
              <code>Authorization: Bearer &lt;your_jwt_token&gt;</code>
            </pre>
            <p className="text-sm text-muted-foreground">
              Obtain a token by calling the <code>/api/auth/login</code> endpoint.
            </p>
          </div>
        </div>
      </section>

      {/* API Sections */}
      <section className="py-12 px-4">
        <div className="container mx-auto max-w-4xl space-y-8">
          {apiSections.map((section) => (
            <Card key={section.title}>
              <CardHeader>
                <div className="flex items-center gap-2">
                  <section.icon className="h-5 w-5 text-primary" />
                  <CardTitle>{section.title}</CardTitle>
                </div>
                <CardDescription>{section.description}</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {section.endpoints.map((endpoint, idx) => (
                    <div
                      key={idx}
                      className="flex items-center justify-between p-3 bg-muted/50 rounded-lg hover:bg-muted transition-colors"
                    >
                      <div className="flex items-center gap-3">
                        <Badge variant="outline" className={methodColors[endpoint.method]}>
                          {endpoint.method}
                        </Badge>
                        <code className="text-sm font-mono">{endpoint.path}</code>
                      </div>
                      <div className="flex items-center gap-3">
                        <span className="text-sm text-muted-foreground hidden md:block">
                          {endpoint.description}
                        </span>
                        {endpoint.auth && (
                          <span title="Requires authentication">
                            <Lock className="h-4 w-4 text-muted-foreground" />
                          </span>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </section>

      {/* Response Format */}
      <section className="py-12 px-4 border-t border-border bg-muted/30">
        <div className="container mx-auto max-w-4xl">
          <h2 className="text-2xl font-bold mb-6">Response Format</h2>
          <div className="grid md:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle className="text-lg text-green-500">Success Response</CardTitle>
              </CardHeader>
              <CardContent>
                <pre className="bg-muted p-3 rounded-md text-sm overflow-x-auto">
{`{
  "id": 1,
  "name": "My Agent",
  "status": "active",
  ...
}`}
                </pre>
              </CardContent>
            </Card>
            <Card>
              <CardHeader>
                <CardTitle className="text-lg text-red-500">Error Response</CardTitle>
              </CardHeader>
              <CardContent>
                <pre className="bg-muted p-3 rounded-md text-sm overflow-x-auto">
{`{
  "detail": "Error message here"
}`}
                </pre>
              </CardContent>
            </Card>
          </div>
        </div>
      </section>

      {/* HTTP Status Codes */}
      <section className="py-12 px-4 border-t border-border">
        <div className="container mx-auto max-w-4xl">
          <h2 className="text-2xl font-bold mb-6">HTTP Status Codes</h2>
          <div className="bg-card border border-border rounded-lg overflow-hidden">
            <table className="w-full text-sm">
              <thead className="bg-muted">
                <tr>
                  <th className="px-4 py-3 text-left font-medium">Code</th>
                  <th className="px-4 py-3 text-left font-medium">Description</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                <tr>
                  <td className="px-4 py-3 font-mono text-green-500">200</td>
                  <td className="px-4 py-3 text-muted-foreground">Success</td>
                </tr>
                <tr>
                  <td className="px-4 py-3 font-mono text-green-500">201</td>
                  <td className="px-4 py-3 text-muted-foreground">Created successfully</td>
                </tr>
                <tr>
                  <td className="px-4 py-3 font-mono text-yellow-500">400</td>
                  <td className="px-4 py-3 text-muted-foreground">Bad request - invalid input</td>
                </tr>
                <tr>
                  <td className="px-4 py-3 font-mono text-yellow-500">401</td>
                  <td className="px-4 py-3 text-muted-foreground">Unauthorized - invalid or missing token</td>
                </tr>
                <tr>
                  <td className="px-4 py-3 font-mono text-yellow-500">403</td>
                  <td className="px-4 py-3 text-muted-foreground">Forbidden - insufficient permissions</td>
                </tr>
                <tr>
                  <td className="px-4 py-3 font-mono text-yellow-500">404</td>
                  <td className="px-4 py-3 text-muted-foreground">Not found</td>
                </tr>
                <tr>
                  <td className="px-4 py-3 font-mono text-red-500">500</td>
                  <td className="px-4 py-3 text-muted-foreground">Internal server error</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-8 px-4 border-t border-border">
        <div className="container mx-auto max-w-4xl text-center text-sm text-muted-foreground">
          <p>
            For interactive API testing, you can use the Swagger UI at{' '}
            <code className="bg-muted px-2 py-1 rounded">/docs</code>
          </p>
        </div>
      </footer>
    </div>
  );
}
