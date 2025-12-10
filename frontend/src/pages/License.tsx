import { Link } from 'react-router-dom';
import { Scale, ChevronLeft, ArrowRight, ExternalLink } from 'lucide-react';
import { Button } from '@/components/ui/button';

export function License() {
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
              <Scale className="h-5 w-5 text-primary" />
              License
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
        <div className="container mx-auto max-w-3xl">
          <div className="prose prose-neutral dark:prose-invert">
            <h1>MIT License</h1>
            <p className="lead">
              Strands GUI is open source software licensed under the MIT License.
            </p>
          </div>

          {/* License Text */}
          <div className="mt-8 bg-card border border-border rounded-lg p-6 font-mono text-sm">
            <pre className="whitespace-pre-wrap">
{`MIT License

Copyright (c) ${new Date().getFullYear()} Strands GUI Contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.`}
            </pre>
          </div>

          {/* What this means */}
          <div className="mt-12 prose prose-neutral dark:prose-invert">
            <h2>What This License Means</h2>
            <p>The MIT License is a permissive open source license that allows you to:</p>

            <div className="grid md:grid-cols-2 gap-6 not-prose mt-6">
              <div className="bg-green-500/10 border border-green-500/20 rounded-lg p-4">
                <h3 className="font-semibold text-green-500 mb-3">You CAN:</h3>
                <ul className="space-y-2 text-sm">
                  <li className="flex items-start gap-2">
                    <span className="text-green-500">✓</span>
                    Use the software for commercial purposes
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-green-500">✓</span>
                    Modify the source code
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-green-500">✓</span>
                    Distribute the software
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-green-500">✓</span>
                    Sublicense to others
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-green-500">✓</span>
                    Use privately
                  </li>
                </ul>
              </div>

              <div className="bg-yellow-500/10 border border-yellow-500/20 rounded-lg p-4">
                <h3 className="font-semibold text-yellow-500 mb-3">You MUST:</h3>
                <ul className="space-y-2 text-sm">
                  <li className="flex items-start gap-2">
                    <span className="text-yellow-500">!</span>
                    Include the original copyright notice
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-yellow-500">!</span>
                    Include the license text in distributions
                  </li>
                </ul>
              </div>
            </div>

            <div className="mt-6 bg-red-500/10 border border-red-500/20 rounded-lg p-4 not-prose">
              <h3 className="font-semibold text-red-500 mb-3">Limitations:</h3>
              <ul className="space-y-2 text-sm">
                <li className="flex items-start gap-2">
                  <span className="text-red-500">✗</span>
                  No warranty is provided
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-red-500">✗</span>
                  Authors are not liable for damages
                </li>
              </ul>
            </div>

            <h2 className="mt-8">Third-Party Licenses</h2>
            <p>
              Strands GUI depends on various open source projects, each with their own licenses.
              Key dependencies include:
            </p>
            <ul>
              <li>
                <strong>Strands Agents SDK</strong> - Apache 2.0 License
              </li>
              <li>
                <strong>React</strong> - MIT License
              </li>
              <li>
                <strong>FastAPI</strong> - MIT License
              </li>
              <li>
                <strong>Tailwind CSS</strong> - MIT License
              </li>
              <li>
                <strong>shadcn/ui</strong> - MIT License
              </li>
            </ul>

            <h2>Contributing</h2>
            <p>
              By contributing to Strands GUI, you agree that your contributions will be licensed
              under the same MIT License. See our contribution guidelines for more information.
            </p>

            <div className="mt-8 flex gap-4">
              <a
                href="https://opensource.org/licenses/MIT"
                target="_blank"
                rel="noopener noreferrer"
              >
                <Button variant="outline">
                  <ExternalLink className="mr-2 h-4 w-4" />
                  Full MIT License Text
                </Button>
              </a>
              <a
                href="https://github.com/strands-agents/strands-agents"
                target="_blank"
                rel="noopener noreferrer"
              >
                <Button variant="outline">
                  <ExternalLink className="mr-2 h-4 w-4" />
                  View on GitHub
                </Button>
              </a>
            </div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="py-8 px-4 border-t border-border">
        <div className="container mx-auto max-w-3xl flex justify-between items-center text-sm text-muted-foreground">
          <p>Strands GUI</p>
          <div className="flex gap-4">
            <Link to="/privacy" className="hover:text-foreground">Privacy Policy</Link>
            <Link to="/terms" className="hover:text-foreground">Terms of Service</Link>
          </div>
        </div>
      </footer>
    </div>
  );
}
