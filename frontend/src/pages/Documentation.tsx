import { Link } from 'react-router-dom';
import {
  Book,
  Code,
  Cpu,
  Key,
  Wrench,
  Bot,
  MessageSquare,
  Settings,
  ArrowRight,
  ExternalLink,
  ChevronLeft,
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';

const sections = [
  {
    title: 'Getting Started',
    icon: Book,
    description: 'Learn the basics of Strands GUI and set up your first agent.',
    items: [
      { title: 'Quick Start Guide', description: 'Get up and running in minutes' },
      { title: 'Installation', description: 'Docker-based deployment instructions' },
      { title: 'Configuration', description: 'Environment variables and settings' },
    ],
  },
  {
    title: 'Agents',
    icon: Bot,
    description: 'Create, configure, and manage AI agents.',
    items: [
      { title: 'Creating Agents', description: 'Build your first AI agent' },
      { title: 'Agent Configuration', description: 'System prompts, models, and parameters' },
      { title: 'Agent Templates', description: 'Use pre-built agent templates' },
    ],
  },
  {
    title: 'Tools',
    icon: Wrench,
    description: 'Extend agent capabilities with tools.',
    items: [
      { title: 'Built-in Tools', description: 'File operations, HTTP requests, and more' },
      { title: 'Custom Tools', description: 'Create your own tools with Python' },
      { title: 'MCP Tools', description: 'Model Context Protocol integration' },
    ],
  },
  {
    title: 'Model Providers',
    icon: Cpu,
    description: 'Connect to various AI model providers.',
    items: [
      { title: 'AWS Bedrock', description: 'Claude, Titan, and other models' },
      { title: 'OpenAI', description: 'GPT-4 and other OpenAI models' },
      { title: 'Ollama', description: 'Local model deployment' },
    ],
  },
  {
    title: 'API Keys',
    icon: Key,
    description: 'Manage authentication for model providers.',
    items: [
      { title: 'Adding API Keys', description: 'Securely store your credentials' },
      { title: 'Provider Setup', description: 'Configure each provider' },
      { title: 'Security Best Practices', description: 'Keep your keys safe' },
    ],
  },
  {
    title: 'Chat Interface',
    icon: MessageSquare,
    description: 'Interact with your agents in real-time.',
    items: [
      { title: 'Starting a Conversation', description: 'Chat with your agents' },
      { title: 'Streaming Responses', description: 'Real-time response streaming' },
      { title: 'Conversation History', description: 'View and manage chat history' },
    ],
  },
];

export function Documentation() {
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
              <Book className="h-5 w-5 text-primary" />
              Documentation
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
          <h1 className="text-4xl font-bold mb-4">Strands GUI Documentation</h1>
          <p className="text-xl text-muted-foreground mb-8">
            Everything you need to know about building and managing AI agents with Strands GUI.
          </p>
          <div className="flex justify-center gap-4">
            <Link to="/api-reference">
              <Button variant="outline">
                <Code className="mr-2 h-4 w-4" />
                API Reference
              </Button>
            </Link>
            <a
              href="https://github.com/strands-agents/strands-agents"
              target="_blank"
              rel="noopener noreferrer"
            >
              <Button variant="outline">
                <ExternalLink className="mr-2 h-4 w-4" />
                Strands SDK Docs
              </Button>
            </a>
          </div>
        </div>
      </section>

      {/* Quick Start */}
      <section className="py-12 px-4 border-b border-border bg-muted/30">
        <div className="container mx-auto max-w-4xl">
          <h2 className="text-2xl font-bold mb-6 flex items-center gap-2">
            <Settings className="h-6 w-6 text-primary" />
            Quick Start
          </h2>
          <div className="bg-card border border-border rounded-lg p-6 space-y-4">
            <div className="space-y-2">
              <h3 className="font-semibold">1. Clone the Repository</h3>
              <pre className="bg-muted p-3 rounded-md text-sm overflow-x-auto">
                <code>git clone https://github.com/your-org/strands-gui.git</code>
              </pre>
            </div>
            <div className="space-y-2">
              <h3 className="font-semibold">2. Configure Environment</h3>
              <pre className="bg-muted p-3 rounded-md text-sm overflow-x-auto">
                <code>cp .env.example .env{'\n'}# Edit .env with your configuration</code>
              </pre>
            </div>
            <div className="space-y-2">
              <h3 className="font-semibold">3. Start with Docker Compose</h3>
              <pre className="bg-muted p-3 rounded-md text-sm overflow-x-auto">
                <code>docker compose up -d</code>
              </pre>
            </div>
            <div className="space-y-2">
              <h3 className="font-semibold">4. Access the Application</h3>
              <p className="text-muted-foreground">
                Open your browser and navigate to <code className="bg-muted px-2 py-1 rounded">http://localhost:3847</code>
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Documentation Sections */}
      <section className="py-12 px-4">
        <div className="container mx-auto max-w-6xl">
          <h2 className="text-2xl font-bold mb-8">Documentation Sections</h2>
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            {sections.map((section) => (
              <Card key={section.title} className="hover:border-primary/50 transition-colors">
                <CardHeader>
                  <div className="flex items-center gap-2 mb-2">
                    <section.icon className="h-5 w-5 text-primary" />
                    <CardTitle>{section.title}</CardTitle>
                  </div>
                  <CardDescription>{section.description}</CardDescription>
                </CardHeader>
                <CardContent>
                  <ul className="space-y-2">
                    {section.items.map((item) => (
                      <li key={item.title} className="text-sm">
                        <span className="font-medium">{item.title}</span>
                        <span className="text-muted-foreground"> - {item.description}</span>
                      </li>
                    ))}
                  </ul>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Architecture Overview */}
      <section className="py-12 px-4 border-t border-border bg-muted/30">
        <div className="container mx-auto max-w-4xl">
          <h2 className="text-2xl font-bold mb-6">Architecture Overview</h2>
          <div className="bg-card border border-border rounded-lg p-6">
            <div className="grid md:grid-cols-2 gap-8">
              <div>
                <h3 className="font-semibold mb-3">Frontend</h3>
                <ul className="space-y-2 text-sm text-muted-foreground">
                  <li>React 18 with TypeScript</li>
                  <li>Vite for fast development</li>
                  <li>Tailwind CSS for styling</li>
                  <li>shadcn/ui component library</li>
                  <li>React Router for navigation</li>
                  <li>WebSocket for real-time chat</li>
                </ul>
              </div>
              <div>
                <h3 className="font-semibold mb-3">Backend</h3>
                <ul className="space-y-2 text-sm text-muted-foreground">
                  <li>FastAPI (Python 3.11+)</li>
                  <li>SQLAlchemy with async support</li>
                  <li>PostgreSQL database</li>
                  <li>Strands Agents SDK</li>
                  <li>JWT authentication</li>
                  <li>WebSocket support</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-8 px-4 border-t border-border">
        <div className="container mx-auto max-w-4xl text-center text-sm text-muted-foreground">
          <p>
            Strands GUI is built on top of the{' '}
            <a
              href="https://github.com/strands-agents/strands-agents"
              target="_blank"
              rel="noopener noreferrer"
              className="text-primary hover:underline"
            >
              Strands Agents SDK
            </a>
            .
          </p>
          <p className="mt-2">
            For SDK-specific documentation, please refer to the official Strands SDK documentation.
          </p>
        </div>
      </footer>
    </div>
  );
}
