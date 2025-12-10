import { Link } from 'react-router-dom';
import { Shield, ChevronLeft, ArrowRight } from 'lucide-react';
import { Button } from '@/components/ui/button';

export function PrivacyPolicy() {
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
              <Shield className="h-5 w-5 text-primary" />
              Privacy Policy
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

      {/* Content */}
      <main className="py-12 px-4">
        <div className="container mx-auto max-w-3xl prose prose-neutral dark:prose-invert">
          <h1>Privacy Policy</h1>
          <p className="lead">Last updated: {new Date().toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' })}</p>

          <h2>1. Introduction</h2>
          <p>
            Welcome to Strands GUI ("we," "our," or "us"). We are committed to protecting your privacy and ensuring
            the security of your personal information. This Privacy Policy explains how we collect, use, disclose,
            and safeguard your information when you use our application.
          </p>

          <h2>2. Information We Collect</h2>
          <h3>2.1 Information You Provide</h3>
          <ul>
            <li><strong>Account Information:</strong> Email address, name, and password when you create an account.</li>
            <li><strong>API Keys:</strong> Third-party API keys you configure for model providers (stored securely).</li>
            <li><strong>Agent Configurations:</strong> Settings, prompts, and configurations for AI agents you create.</li>
            <li><strong>Chat History:</strong> Conversations with AI agents (stored locally and in your database).</li>
          </ul>

          <h3>2.2 Automatically Collected Information</h3>
          <ul>
            <li><strong>Usage Data:</strong> How you interact with the application, including features used and actions taken.</li>
            <li><strong>Log Data:</strong> Server logs including IP addresses, browser type, and access times.</li>
            <li><strong>Device Information:</strong> Device type, operating system, and browser information.</li>
          </ul>

          <h2>3. How We Use Your Information</h2>
          <p>We use the information we collect to:</p>
          <ul>
            <li>Provide, maintain, and improve our services</li>
            <li>Process and complete transactions</li>
            <li>Send you technical notices and support messages</li>
            <li>Respond to your comments and questions</li>
            <li>Monitor and analyze usage patterns</li>
            <li>Detect, prevent, and address technical issues</li>
          </ul>

          <h2>4. Data Storage and Security</h2>
          <p>
            Strands GUI is designed to be self-hosted, meaning your data remains on your own infrastructure.
            We implement industry-standard security measures to protect your information:
          </p>
          <ul>
            <li>API keys are encrypted at rest</li>
            <li>Passwords are hashed using secure algorithms</li>
            <li>All communications use HTTPS encryption</li>
            <li>Regular security audits and updates</li>
          </ul>

          <h2>5. Third-Party Services</h2>
          <p>
            When you configure AI model providers (AWS Bedrock, OpenAI, Anthropic, etc.), your prompts and
            conversations are sent to these third-party services. Please review their respective privacy
            policies to understand how they handle your data:
          </p>
          <ul>
            <li>AWS Bedrock: <a href="https://aws.amazon.com/privacy/" target="_blank" rel="noopener noreferrer">AWS Privacy Notice</a></li>
            <li>OpenAI: <a href="https://openai.com/privacy" target="_blank" rel="noopener noreferrer">OpenAI Privacy Policy</a></li>
            <li>Anthropic: <a href="https://www.anthropic.com/privacy" target="_blank" rel="noopener noreferrer">Anthropic Privacy Policy</a></li>
          </ul>

          <h2>6. Data Sharing</h2>
          <p>
            We do not sell, trade, or rent your personal information to third parties. We may share information only:
          </p>
          <ul>
            <li>With your consent</li>
            <li>To comply with legal obligations</li>
            <li>To protect our rights and safety</li>
            <li>With service providers who assist in our operations (under confidentiality agreements)</li>
          </ul>

          <h2>7. Your Rights</h2>
          <p>You have the right to:</p>
          <ul>
            <li>Access your personal information</li>
            <li>Correct inaccurate data</li>
            <li>Delete your account and associated data</li>
            <li>Export your data in a portable format</li>
            <li>Opt out of non-essential data collection</li>
          </ul>

          <h2>8. Data Retention</h2>
          <p>
            We retain your information for as long as your account is active or as needed to provide services.
            You can request deletion of your data at any time through the application settings or by contacting us.
          </p>

          <h2>9. Children's Privacy</h2>
          <p>
            Our services are not intended for individuals under the age of 13. We do not knowingly collect
            personal information from children under 13.
          </p>

          <h2>10. Changes to This Policy</h2>
          <p>
            We may update this Privacy Policy from time to time. We will notify you of any changes by posting
            the new Privacy Policy on this page and updating the "Last updated" date.
          </p>

          <h2>11. Contact Us</h2>
          <p>
            If you have questions about this Privacy Policy or our privacy practices, please contact us through
            the application or by creating an issue on our GitHub repository.
          </p>

          <div className="mt-12 p-6 bg-muted rounded-lg">
            <h3 className="mt-0">Self-Hosted Deployment</h3>
            <p className="mb-0">
              Since Strands GUI is self-hosted, you maintain full control over your data. This privacy policy
              serves as a template and should be customized to reflect your organization's specific data
              handling practices when deploying the application.
            </p>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="py-8 px-4 border-t border-border">
        <div className="container mx-auto max-w-3xl flex justify-between items-center text-sm text-muted-foreground">
          <p>Strands GUI</p>
          <div className="flex gap-4">
            <Link to="/terms" className="hover:text-foreground">Terms of Service</Link>
            <Link to="/license" className="hover:text-foreground">License</Link>
          </div>
        </div>
      </footer>
    </div>
  );
}
