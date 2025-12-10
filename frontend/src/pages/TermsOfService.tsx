import { Link } from 'react-router-dom';
import { FileText, ChevronLeft, ArrowRight } from 'lucide-react';
import { Button } from '@/components/ui/button';

export function TermsOfService() {
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
              <FileText className="h-5 w-5 text-primary" />
              Terms of Service
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
          <h1>Terms of Service</h1>
          <p className="lead">Last updated: {new Date().toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' })}</p>

          <h2>1. Acceptance of Terms</h2>
          <p>
            By accessing or using Strands GUI ("the Service"), you agree to be bound by these Terms of Service
            ("Terms"). If you do not agree to these Terms, please do not use the Service.
          </p>

          <h2>2. Description of Service</h2>
          <p>
            Strands GUI is a web-based graphical user interface for managing AI agents built with the
            Strands Agents SDK. The Service allows you to:
          </p>
          <ul>
            <li>Create and configure AI agents</li>
            <li>Manage tools and integrations</li>
            <li>Configure model provider connections</li>
            <li>Interact with agents through a chat interface</li>
            <li>Monitor agent activity and performance</li>
          </ul>

          <h2>3. User Accounts</h2>
          <h3>3.1 Registration</h3>
          <p>
            To use certain features of the Service, you must create an account. You agree to provide accurate,
            current, and complete information during registration and to update such information to keep it
            accurate, current, and complete.
          </p>

          <h3>3.2 Account Security</h3>
          <p>
            You are responsible for safeguarding your password and any activities or actions under your account.
            You agree to notify us immediately of any unauthorized access to or use of your account.
          </p>

          <h2>4. Acceptable Use</h2>
          <p>You agree not to use the Service to:</p>
          <ul>
            <li>Violate any applicable laws or regulations</li>
            <li>Infringe on the rights of others</li>
            <li>Generate harmful, abusive, or misleading content</li>
            <li>Attempt to gain unauthorized access to systems or data</li>
            <li>Distribute malware or engage in harmful activities</li>
            <li>Circumvent security measures or access controls</li>
            <li>Overload or disrupt the Service's infrastructure</li>
          </ul>

          <h2>5. API Keys and Third-Party Services</h2>
          <h3>5.1 Your API Keys</h3>
          <p>
            You are responsible for maintaining the security of any API keys you configure in the Service.
            We are not responsible for charges or usage incurred through your third-party provider accounts.
          </p>

          <h3>5.2 Third-Party Terms</h3>
          <p>
            Your use of third-party AI model providers (AWS Bedrock, OpenAI, Anthropic, etc.) is subject to
            their respective terms of service and usage policies. You agree to comply with all applicable
            third-party terms.
          </p>

          <h2>6. Intellectual Property</h2>
          <h3>6.1 Our Rights</h3>
          <p>
            The Service, including its original content, features, and functionality, is owned by the Strands
            GUI developers and is protected by copyright, trademark, and other intellectual property laws.
          </p>

          <h3>6.2 Your Content</h3>
          <p>
            You retain all rights to the content you create, including agent configurations, custom tools,
            and conversation history. By using the Service, you grant us a limited license to store and
            process your content solely to provide the Service.
          </p>

          <h2>7. Open Source License</h2>
          <p>
            Strands GUI is released under an open source license. Your use of the source code is governed
            by the applicable open source license terms. See the <Link to="/license">License page</Link> for details.
          </p>

          <h2>8. Disclaimer of Warranties</h2>
          <p>
            THE SERVICE IS PROVIDED "AS IS" AND "AS AVAILABLE" WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS
            OR IMPLIED, INCLUDING BUT NOT LIMITED TO IMPLIED WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
            PARTICULAR PURPOSE, AND NON-INFRINGEMENT.
          </p>
          <p>We do not warrant that:</p>
          <ul>
            <li>The Service will be uninterrupted or error-free</li>
            <li>Defects will be corrected</li>
            <li>The Service is free of viruses or harmful components</li>
            <li>AI-generated content will be accurate or appropriate</li>
          </ul>

          <h2>9. Limitation of Liability</h2>
          <p>
            TO THE MAXIMUM EXTENT PERMITTED BY LAW, IN NO EVENT SHALL THE DEVELOPERS, CONTRIBUTORS, OR
            AFFILIATES BE LIABLE FOR ANY INDIRECT, INCIDENTAL, SPECIAL, CONSEQUENTIAL, OR PUNITIVE DAMAGES,
            INCLUDING WITHOUT LIMITATION, LOSS OF PROFITS, DATA, USE, GOODWILL, OR OTHER INTANGIBLE LOSSES,
            RESULTING FROM YOUR USE OF THE SERVICE.
          </p>

          <h2>10. Indemnification</h2>
          <p>
            You agree to indemnify and hold harmless the developers and contributors from any claims, damages,
            losses, liabilities, and expenses arising out of or related to your use of the Service or violation
            of these Terms.
          </p>

          <h2>11. Modifications to Terms</h2>
          <p>
            We reserve the right to modify these Terms at any time. We will provide notice of any material
            changes by updating the "Last updated" date. Your continued use of the Service after such
            modifications constitutes acceptance of the updated Terms.
          </p>

          <h2>12. Termination</h2>
          <p>
            We may terminate or suspend your access to the Service immediately, without prior notice, for
            any reason, including breach of these Terms. Upon termination, your right to use the Service
            will cease immediately.
          </p>

          <h2>13. Governing Law</h2>
          <p>
            These Terms shall be governed by and construed in accordance with the laws of the jurisdiction
            in which the Service is operated, without regard to its conflict of law provisions.
          </p>

          <h2>14. Severability</h2>
          <p>
            If any provision of these Terms is found to be unenforceable or invalid, that provision shall
            be limited or eliminated to the minimum extent necessary, and the remaining provisions shall
            remain in full force and effect.
          </p>

          <h2>15. Contact</h2>
          <p>
            If you have any questions about these Terms, please contact us through the application or by
            creating an issue on our GitHub repository.
          </p>

          <div className="mt-12 p-6 bg-muted rounded-lg">
            <h3 className="mt-0">Self-Hosted Deployment Notice</h3>
            <p className="mb-0">
              These Terms of Service serve as a template for self-hosted deployments of Strands GUI.
              Organizations deploying this software should customize these terms to reflect their specific
              requirements, jurisdiction, and policies.
            </p>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="py-8 px-4 border-t border-border">
        <div className="container mx-auto max-w-3xl flex justify-between items-center text-sm text-muted-foreground">
          <p>Strands GUI</p>
          <div className="flex gap-4">
            <Link to="/privacy" className="hover:text-foreground">Privacy Policy</Link>
            <Link to="/license" className="hover:text-foreground">License</Link>
          </div>
        </div>
      </footer>
    </div>
  );
}
