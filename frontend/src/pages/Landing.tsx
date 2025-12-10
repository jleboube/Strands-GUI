import { useState } from 'react';
import { Link } from 'react-router-dom';
import {
  Bot,
  Zap,
  Shield,
  Code,
  MessageSquare,
  Workflow,
  CheckCircle,
  ArrowRight,
  ChevronDown,
  Github,
  Twitter,
  Linkedin,
  Star,
  Users,
  Globe,
  Cpu
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';

// FAQ Accordion Item
function FAQItem({ question, answer }: { question: string; answer: string }) {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div className="border-b border-border">
      <button
        className="w-full py-4 flex items-center justify-between text-left hover:text-primary transition-colors"
        onClick={() => setIsOpen(!isOpen)}
      >
        <span className="font-medium">{question}</span>
        <ChevronDown className={`h-5 w-5 transition-transform ${isOpen ? 'rotate-180' : ''}`} />
      </button>
      {isOpen && (
        <div className="pb-4 text-muted-foreground">
          {answer}
        </div>
      )}
    </div>
  );
}

export function Landing() {
  return (
    <div className="min-h-screen bg-background">
      {/* Navbar - Sticky */}
      <nav className="sticky top-0 z-50 bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 border-b border-border">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="h-8 w-8 rounded-lg bg-primary flex items-center justify-center">
              <Bot className="h-5 w-5 text-primary-foreground" />
            </div>
            <span className="text-xl font-bold">Strands GUI</span>
          </div>

          <div className="hidden md:flex items-center gap-8">
            <a href="#features" className="text-muted-foreground hover:text-foreground transition-colors">Features</a>
            <a href="#how-it-works" className="text-muted-foreground hover:text-foreground transition-colors">How it Works</a>
            <a href="#testimonials" className="text-muted-foreground hover:text-foreground transition-colors">Testimonials</a>
            <a href="#faq" className="text-muted-foreground hover:text-foreground transition-colors">FAQ</a>
          </div>

          <div className="flex items-center gap-3">
            <Button variant="ghost" asChild>
              <Link to="/login">Sign In</Link>
            </Button>
            <Button asChild>
              <Link to="/register">Get Started</Link>
            </Button>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-primary/5 via-transparent to-primary/10" />
        <div className="container mx-auto px-4 py-20 md:py-32 relative">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            <div className="space-y-8">
              {/* Social Proof Badge */}
              <div className="inline-flex items-center gap-2 bg-primary/10 text-primary px-4 py-2 rounded-full text-sm font-medium">
                <Users className="h-4 w-4" />
                <span>Trusted by 1,000+ developers</span>
              </div>

              {/* Main Heading */}
              <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold leading-tight">
                Build AI Agents
                <span className="text-primary"> Without the Complexity</span>
              </h1>

              <p className="text-xl text-muted-foreground max-w-lg">
                The visual interface for AWS Strands SDK. Create, configure, and deploy intelligent AI agents in minutes, not days.
              </p>

              {/* CTAs */}
              <div className="flex flex-col sm:flex-row gap-4">
                <Button size="lg" asChild className="text-lg px-8">
                  <Link to="/register">
                    Start Building Free
                    <ArrowRight className="ml-2 h-5 w-5" />
                  </Link>
                </Button>
                <Button size="lg" variant="outline" asChild className="text-lg px-8">
                  <a href="https://github.com/strands-agents" target="_blank" rel="noopener noreferrer">
                    <Github className="mr-2 h-5 w-5" />
                    View on GitHub
                  </a>
                </Button>
              </div>

              {/* Quick Stats */}
              <div className="flex gap-8 pt-4">
                <div>
                  <div className="text-2xl font-bold">5min</div>
                  <div className="text-sm text-muted-foreground">Setup Time</div>
                </div>
                <div>
                  <div className="text-2xl font-bold">10+</div>
                  <div className="text-sm text-muted-foreground">Model Providers</div>
                </div>
                <div>
                  <div className="text-2xl font-bold">100%</div>
                  <div className="text-sm text-muted-foreground">Open Source</div>
                </div>
              </div>
            </div>

            {/* Hero Visual - Product Screenshot/Demo */}
            <div className="relative">
              <div className="bg-gradient-to-br from-primary/20 to-primary/5 rounded-2xl p-1">
                <div className="bg-card rounded-xl overflow-hidden shadow-2xl border border-border">
                  <div className="bg-muted px-4 py-3 flex items-center gap-2 border-b border-border">
                    <div className="flex gap-1.5">
                      <div className="w-3 h-3 rounded-full bg-red-500" />
                      <div className="w-3 h-3 rounded-full bg-yellow-500" />
                      <div className="w-3 h-3 rounded-full bg-green-500" />
                    </div>
                    <div className="flex-1 text-center text-sm text-muted-foreground">Strands GUI - Agent Builder</div>
                  </div>
                  <div className="p-6 space-y-4">
                    <div className="flex items-center gap-3 p-4 bg-muted rounded-lg">
                      <Bot className="h-10 w-10 text-primary" />
                      <div>
                        <div className="font-semibold">Research Agent</div>
                        <div className="text-sm text-muted-foreground">Claude 3 Sonnet • 3 Tools</div>
                      </div>
                    </div>
                    <div className="grid grid-cols-2 gap-3">
                      <div className="p-3 bg-muted/50 rounded-lg">
                        <Cpu className="h-5 w-5 text-primary mb-2" />
                        <div className="text-sm font-medium">Model Config</div>
                      </div>
                      <div className="p-3 bg-muted/50 rounded-lg">
                        <Code className="h-5 w-5 text-primary mb-2" />
                        <div className="text-sm font-medium">Tool Setup</div>
                      </div>
                    </div>
                    <div className="p-4 bg-primary/10 rounded-lg border border-primary/20">
                      <div className="text-sm font-medium text-primary mb-2">System Prompt</div>
                      <div className="text-sm text-muted-foreground">You are a research assistant. Help users find and analyze information...</div>
                    </div>
                  </div>
                </div>
              </div>
              {/* Floating badges */}
              <div className="absolute -top-4 -right-4 bg-card border border-border rounded-lg px-3 py-2 shadow-lg">
                <div className="flex items-center gap-2 text-sm">
                  <CheckCircle className="h-4 w-4 text-green-500" />
                  <span>Agent Active</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Partners/Trust Section */}
      <section className="border-y border-border bg-muted/30">
        <div className="container mx-auto px-4 py-12">
          <p className="text-center text-muted-foreground mb-8">Powered by industry-leading AI providers</p>
          <div className="flex flex-wrap justify-center items-center gap-8 md:gap-16">
            {['Amazon Bedrock', 'Anthropic', 'OpenAI', 'Google Gemini', 'Ollama'].map((provider) => (
              <div key={provider} className="text-lg font-semibold text-muted-foreground/60 hover:text-muted-foreground transition-colors">
                {provider}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Benefits Section - Bento Grid */}
      <section id="features" className="py-20 md:py-32">
        <div className="container mx-auto px-4">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold mb-4">Everything You Need to Build AI Agents</h2>
            <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
              Focus on what your agents do, not how they're built
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {/* Large Feature Card */}
            <Card className="lg:col-span-2 bg-gradient-to-br from-primary/10 to-transparent border-primary/20">
              <CardHeader>
                <div className="h-12 w-12 rounded-lg bg-primary/20 flex items-center justify-center mb-4">
                  <Bot className="h-6 w-6 text-primary" />
                </div>
                <CardTitle className="text-2xl">Visual Agent Builder</CardTitle>
                <CardDescription className="text-base">
                  Design sophisticated AI agents through an intuitive drag-and-drop interface. No coding required for basic agents, full code access for advanced customization.
                </CardDescription>
              </CardHeader>
            </Card>

            <Card>
              <CardHeader>
                <div className="h-12 w-12 rounded-lg bg-primary/10 flex items-center justify-center mb-4">
                  <Zap className="h-6 w-6 text-primary" />
                </div>
                <CardTitle>Multi-Model Support</CardTitle>
                <CardDescription>
                  Switch between Claude, GPT-4, Gemini, and local models with a single click. Test and compare results.
                </CardDescription>
              </CardHeader>
            </Card>

            <Card>
              <CardHeader>
                <div className="h-12 w-12 rounded-lg bg-primary/10 flex items-center justify-center mb-4">
                  <Code className="h-6 w-6 text-primary" />
                </div>
                <CardTitle>Custom Tools</CardTitle>
                <CardDescription>
                  Extend your agents with custom Python tools or connect to external APIs. Built-in tools for common tasks.
                </CardDescription>
              </CardHeader>
            </Card>

            <Card>
              <CardHeader>
                <div className="h-12 w-12 rounded-lg bg-primary/10 flex items-center justify-center mb-4">
                  <MessageSquare className="h-6 w-6 text-primary" />
                </div>
                <CardTitle>Real-time Chat</CardTitle>
                <CardDescription>
                  Stream responses in real-time with WebSocket connections. Test agents instantly in the built-in chat interface.
                </CardDescription>
              </CardHeader>
            </Card>

            <Card>
              <CardHeader>
                <div className="h-12 w-12 rounded-lg bg-primary/10 flex items-center justify-center mb-4">
                  <Shield className="h-6 w-6 text-primary" />
                </div>
                <CardTitle>Secure by Default</CardTitle>
                <CardDescription>
                  API keys encrypted at rest. Role-based access control. Audit logs for compliance.
                </CardDescription>
              </CardHeader>
            </Card>

            <Card>
              <CardHeader>
                <div className="h-12 w-12 rounded-lg bg-primary/10 flex items-center justify-center mb-4">
                  <Workflow className="h-6 w-6 text-primary" />
                </div>
                <CardTitle>MCP Integration</CardTitle>
                <CardDescription>
                  Connect to Model Context Protocol servers for enhanced capabilities and external service integration.
                </CardDescription>
              </CardHeader>
            </Card>
          </div>
        </div>
      </section>

      {/* How it Works */}
      <section id="how-it-works" className="py-20 md:py-32 bg-muted/30">
        <div className="container mx-auto px-4">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold mb-4">Get Started in 3 Simple Steps</h2>
            <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
              From zero to deployed agent in under 5 minutes
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto">
            <div className="text-center">
              <div className="h-16 w-16 rounded-full bg-primary text-primary-foreground flex items-center justify-center text-2xl font-bold mx-auto mb-6">
                1
              </div>
              <h3 className="text-xl font-semibold mb-3">Configure Your Model</h3>
              <p className="text-muted-foreground">
                Choose from 10+ AI models including Claude, GPT-4, Gemini, or local models via Ollama. Add your API keys securely.
              </p>
            </div>

            <div className="text-center">
              <div className="h-16 w-16 rounded-full bg-primary text-primary-foreground flex items-center justify-center text-2xl font-bold mx-auto mb-6">
                2
              </div>
              <h3 className="text-xl font-semibold mb-3">Design Your Agent</h3>
              <p className="text-muted-foreground">
                Write a system prompt, select tools, and configure parameters. Use templates to get started faster.
              </p>
            </div>

            <div className="text-center">
              <div className="h-16 w-16 rounded-full bg-primary text-primary-foreground flex items-center justify-center text-2xl font-bold mx-auto mb-6">
                3
              </div>
              <h3 className="text-xl font-semibold mb-3">Test & Deploy</h3>
              <p className="text-muted-foreground">
                Chat with your agent in real-time. Iterate quickly based on results. Export or deploy when ready.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Testimonials */}
      <section id="testimonials" className="py-20 md:py-32">
        <div className="container mx-auto px-4">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold mb-4">Loved by Developers Worldwide</h2>
            <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
              See what developers are building with Strands GUI
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-6 max-w-6xl mx-auto">
            {[
              {
                name: 'Sarah Chen',
                role: 'ML Engineer at TechCorp',
                content: 'Strands GUI cut our agent development time by 80%. The visual builder is intuitive and the multi-model support is a game-changer.',
                stars: 5,
              },
              {
                name: 'Marcus Johnson',
                role: 'Founder, AI Solutions',
                content: 'Finally a tool that makes AI agents accessible to my entire team. We went from idea to production in a single afternoon.',
                stars: 5,
              },
              {
                name: 'Emily Rodriguez',
                role: 'Senior Developer',
                content: 'The ability to test different models side by side helped us find the perfect balance of cost and performance for our use case.',
                stars: 5,
              },
            ].map((testimonial, index) => (
              <Card key={index}>
                <CardContent className="pt-6">
                  <div className="flex gap-1 mb-4">
                    {Array.from({ length: testimonial.stars }).map((_, i) => (
                      <Star key={i} className="h-5 w-5 fill-primary text-primary" />
                    ))}
                  </div>
                  <p className="text-muted-foreground mb-4">{testimonial.content}</p>
                  <div className="flex items-center gap-3">
                    <div className="h-10 w-10 rounded-full bg-primary/20 flex items-center justify-center">
                      <span className="text-sm font-semibold text-primary">
                        {testimonial.name.split(' ').map(n => n[0]).join('')}
                      </span>
                    </div>
                    <div>
                      <div className="font-semibold">{testimonial.name}</div>
                      <div className="text-sm text-muted-foreground">{testimonial.role}</div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* FAQ Section */}
      <section id="faq" className="py-20 md:py-32 bg-muted/30">
        <div className="container mx-auto px-4">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold mb-4">Frequently Asked Questions</h2>
            <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
              Everything you need to know about Strands GUI
            </p>
          </div>

          <div className="max-w-3xl mx-auto">
            <FAQItem
              question="What is Strands GUI?"
              answer="Strands GUI is a web-based interface for the AWS Strands Agents SDK. It allows you to create, configure, and manage AI agents through a visual interface without writing complex code."
            />
            <FAQItem
              question="Which AI models are supported?"
              answer="We support all major AI providers including Amazon Bedrock (Claude, Titan, Llama, Mistral), OpenAI (GPT-4, GPT-3.5), Google (Gemini Pro, Gemini Flash), Anthropic (direct API), and local models via Ollama."
            />
            <FAQItem
              question="Is it free to use?"
              answer="Strands GUI is open source and free to self-host. You only pay for the AI model usage from your chosen providers. We also offer a managed cloud version for teams who don't want to manage infrastructure."
            />
            <FAQItem
              question="Can I use my own custom tools?"
              answer="Yes! You can create custom Python tools, connect to external APIs, or use our built-in tools for common tasks like web search, file operations, and shell commands."
            />
            <FAQItem
              question="How secure is my data?"
              answer="Security is our priority. API keys are encrypted at rest using industry-standard encryption. All communications use TLS. We support role-based access control and provide audit logs for compliance."
            />
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 md:py-32">
        <div className="container mx-auto px-4">
          <div className="bg-gradient-to-br from-primary to-orange-600 rounded-3xl p-8 md:p-16 text-center">
            <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
              Ready to Build Your First AI Agent?
            </h2>
            <p className="text-xl text-white/80 max-w-2xl mx-auto mb-8">
              Join thousands of developers who are building the future with intelligent AI agents.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Button size="lg" variant="secondary" asChild className="text-lg px-8">
                <Link to="/register">
                  Get Started Free
                  <ArrowRight className="ml-2 h-5 w-5" />
                </Link>
              </Button>
              <Button size="lg" variant="outline" asChild className="text-lg px-8 bg-transparent border-white text-white hover:bg-white/10">
                <a href="https://github.com/strands-agents" target="_blank" rel="noopener noreferrer">
                  Star on GitHub
                </a>
              </Button>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-border py-12">
        <div className="container mx-auto px-4">
          <div className="grid md:grid-cols-4 gap-8">
            {/* Logo & Description */}
            <div className="md:col-span-1">
              <div className="flex items-center gap-2 mb-4">
                <div className="h-8 w-8 rounded-lg bg-primary flex items-center justify-center">
                  <Bot className="h-5 w-5 text-primary-foreground" />
                </div>
                <span className="text-xl font-bold">Strands GUI</span>
              </div>
              <p className="text-muted-foreground text-sm">
                The visual interface for building AI agents with AWS Strands SDK.
              </p>
            </div>

            {/* Links */}
            <div>
              <h4 className="font-semibold mb-4">Product</h4>
              <ul className="space-y-2 text-sm text-muted-foreground">
                <li><a href="#features" className="hover:text-foreground">Features</a></li>
                <li><a href="#how-it-works" className="hover:text-foreground">How it Works</a></li>
                <li><Link to="/documentation" className="hover:text-foreground">Documentation</Link></li>
                <li><Link to="/api-reference" className="hover:text-foreground">API Reference</Link></li>
              </ul>
            </div>

            <div>
              <h4 className="font-semibold mb-4">Legal</h4>
              <ul className="space-y-2 text-sm text-muted-foreground">
                <li><Link to="/privacy" className="hover:text-foreground">Privacy Policy</Link></li>
                <li><Link to="/terms" className="hover:text-foreground">Terms of Service</Link></li>
                <li><Link to="/license" className="hover:text-foreground">License</Link></li>
              </ul>
            </div>

            {/* Newsletter */}
            <div>
              <h4 className="font-semibold mb-4">Stay Updated</h4>
              <p className="text-sm text-muted-foreground mb-4">
                Get the latest updates on new features and releases.
              </p>
              <div className="flex gap-4">
                <a href="#" className="text-muted-foreground hover:text-foreground">
                  <Github className="h-5 w-5" />
                </a>
                <a href="#" className="text-muted-foreground hover:text-foreground">
                  <Twitter className="h-5 w-5" />
                </a>
                <a href="#" className="text-muted-foreground hover:text-foreground">
                  <Linkedin className="h-5 w-5" />
                </a>
              </div>
            </div>
          </div>

          <div className="border-t border-border mt-12 pt-8 flex flex-col md:flex-row justify-between items-center gap-4">
            <p className="text-sm text-muted-foreground">
              © 2025 Strands GUI. Built by Joe LeBoube with AWS Strands Agents SDK.
            </p>
            <div className="flex items-center gap-2">
              <Globe className="h-4 w-4 text-muted-foreground" />
              <span className="text-sm text-muted-foreground">Open Source</span>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
