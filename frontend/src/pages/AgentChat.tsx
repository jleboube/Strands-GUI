import { useEffect, useRef, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import ReactMarkdown from 'react-markdown';
import {
  ArrowLeft, Send, Trash2, Bot, User, Loader2
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Card } from '@/components/ui/card';
import { agentsApi } from '@/services/api';
import { useToast } from '@/hooks/use-toast';
import type { Agent, ChatMessage, WebSocketMessage } from '@/types';
import { cn } from '@/lib/utils';

export function AgentChat() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { toast } = useToast();
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const wsRef = useRef<WebSocket | null>(null);

  const [agent, setAgent] = useState<Agent | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputText, setInputText] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const [isConnected, setIsConnected] = useState(false);
  const [isStreaming, setIsStreaming] = useState(false);

  useEffect(() => {
    loadAgent();
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [id]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const loadAgent = async () => {
    try {
      const agentData = await agentsApi.get(parseInt(id!));
      setAgent(agentData);
      connectWebSocket();
    } catch (error) {
      toast({
        title: 'Error',
        description: 'Failed to load agent',
        variant: 'destructive',
      });
      navigate('/app/agents');
    } finally {
      setIsLoading(false);
    }
  };

  const connectWebSocket = () => {
    const token = localStorage.getItem('token');
    const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${wsProtocol}//${window.location.host}/api/ws/chat/${id}?token=${token}`;

    wsRef.current = new WebSocket(wsUrl);

    wsRef.current.onopen = () => {
      setIsConnected(true);
    };

    wsRef.current.onmessage = (event) => {
      const data: WebSocketMessage = JSON.parse(event.data);
      handleWebSocketMessage(data);
    };

    wsRef.current.onclose = () => {
      setIsConnected(false);
    };

    wsRef.current.onerror = () => {
      setIsConnected(false);
      toast({
        title: 'Connection Error',
        description: 'Failed to connect to agent. Using REST API fallback.',
        variant: 'destructive',
      });
    };
  };

  const handleWebSocketMessage = (data: WebSocketMessage) => {
    switch (data.type) {
      case 'ready':
        break;
      case 'status':
        if (data.status === 'thinking') {
          setIsStreaming(true);
        }
        break;
      case 'chunk':
        setMessages((prev) => {
          const lastMessage = prev[prev.length - 1];
          if (lastMessage && lastMessage.role === 'assistant' && lastMessage.status === 'streaming') {
            return [
              ...prev.slice(0, -1),
              {
                ...lastMessage,
                content: lastMessage.content + data.content,
              },
            ];
          }
          return [
            ...prev,
            {
              id: crypto.randomUUID(),
              role: 'assistant',
              content: data.content || '',
              timestamp: new Date(),
              status: 'streaming',
            },
          ];
        });
        break;
      case 'complete':
        setMessages((prev) => {
          const lastMessage = prev[prev.length - 1];
          if (lastMessage && lastMessage.role === 'assistant') {
            return [
              ...prev.slice(0, -1),
              {
                ...lastMessage,
                status: 'complete',
              },
            ];
          }
          return prev;
        });
        setIsStreaming(false);
        break;
      case 'error':
        setMessages((prev) => [
          ...prev,
          {
            id: crypto.randomUUID(),
            role: 'assistant',
            content: `Error: ${data.message}`,
            timestamp: new Date(),
            status: 'error',
          },
        ]);
        setIsStreaming(false);
        break;
      case 'history_cleared':
        setMessages([]);
        break;
    }
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleSend = async () => {
    if (!inputText.trim() || isStreaming) return;

    const userMessage: ChatMessage = {
      id: crypto.randomUUID(),
      role: 'user',
      content: inputText,
      timestamp: new Date(),
      status: 'complete',
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputText('');

    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(
        JSON.stringify({
          type: 'message',
          content: inputText,
        })
      );
    } else {
      // Fallback to REST API
      setIsStreaming(true);
      try {
        const conversationHistory = messages.map((m) => ({
          role: m.role,
          content: m.content,
        }));

        const run = await agentsApi.run(parseInt(id!), inputText, conversationHistory);

        setMessages((prev) => [
          ...prev,
          {
            id: crypto.randomUUID(),
            role: 'assistant',
            content: run.output_text || run.error_message || 'No response',
            timestamp: new Date(),
            status: run.status === 'completed' ? 'complete' : 'error',
          },
        ]);
      } catch (error: any) {
        setMessages((prev) => [
          ...prev,
          {
            id: crypto.randomUUID(),
            role: 'assistant',
            content: `Error: ${error.message}`,
            timestamp: new Date(),
            status: 'error',
          },
        ]);
      } finally {
        setIsStreaming(false);
      }
    }
  };

  const handleClearHistory = () => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ type: 'clear_history' }));
    } else {
      setMessages([]);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
      </div>
    );
  }

  return (
    <div className="flex flex-col h-[calc(100vh-6rem)]">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-4">
          <Button variant="ghost" size="icon" onClick={() => navigate(`/app/agents/${id}`)}>
            <ArrowLeft className="h-5 w-5" />
          </Button>
          <div>
            <h1 className="text-xl font-bold flex items-center gap-2">
              <Bot className="h-5 w-5" />
              {agent?.name}
            </h1>
            <p className="text-sm text-muted-foreground flex items-center gap-2">
              <span
                className={cn(
                  'w-2 h-2 rounded-full',
                  isConnected ? 'bg-green-500' : 'bg-yellow-500'
                )}
              />
              {isConnected ? 'Connected (WebSocket)' : 'Using REST API'}
            </p>
          </div>
        </div>
        <Button variant="outline" size="sm" onClick={handleClearHistory}>
          <Trash2 className="mr-2 h-4 w-4" />
          Clear History
        </Button>
      </div>

      <Card className="flex-1 flex flex-col overflow-hidden">
        <ScrollArea className="flex-1 p-4">
          {messages.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full text-center">
              <Bot className="h-12 w-12 text-muted-foreground mb-4" />
              <h3 className="text-lg font-medium">Start a conversation</h3>
              <p className="text-muted-foreground max-w-sm">
                Send a message to start chatting with {agent?.name}
              </p>
            </div>
          ) : (
            <div className="space-y-4">
              {messages.map((message) => (
                <div
                  key={message.id}
                  className={cn(
                    'flex gap-3',
                    message.role === 'user' ? 'justify-end' : 'justify-start'
                  )}
                >
                  {message.role === 'assistant' && (
                    <div className="w-8 h-8 rounded-full bg-primary flex items-center justify-center shrink-0">
                      <Bot className="h-4 w-4 text-primary-foreground" />
                    </div>
                  )}
                  <div
                    className={cn(
                      'max-w-[80%] rounded-lg px-4 py-2',
                      message.role === 'user'
                        ? 'bg-primary text-primary-foreground'
                        : 'bg-muted',
                      message.status === 'error' && 'bg-destructive/10 text-destructive'
                    )}
                  >
                    {message.role === 'assistant' ? (
                      <div className="prose dark:prose-invert prose-sm max-w-none">
                        <ReactMarkdown>{message.content}</ReactMarkdown>
                      </div>
                    ) : (
                      <p className="whitespace-pre-wrap">{message.content}</p>
                    )}
                    {message.status === 'streaming' && (
                      <span className="inline-block w-2 h-4 bg-current animate-pulse ml-1" />
                    )}
                  </div>
                  {message.role === 'user' && (
                    <div className="w-8 h-8 rounded-full bg-secondary flex items-center justify-center shrink-0">
                      <User className="h-4 w-4" />
                    </div>
                  )}
                </div>
              ))}
              <div ref={messagesEndRef} />
            </div>
          )}
        </ScrollArea>

        <div className="p-4 border-t">
          <div className="flex gap-2">
            <Textarea
              placeholder="Type your message..."
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              onKeyDown={handleKeyDown}
              className="min-h-[60px] resize-none"
              disabled={isStreaming}
            />
            <Button
              onClick={handleSend}
              disabled={!inputText.trim() || isStreaming}
              className="shrink-0"
            >
              {isStreaming ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Send className="h-4 w-4" />
              )}
            </Button>
          </div>
          <p className="text-xs text-muted-foreground mt-2">
            Press Enter to send, Shift+Enter for new line
          </p>
        </div>
      </Card>
    </div>
  );
}
