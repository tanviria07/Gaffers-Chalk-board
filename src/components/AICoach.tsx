import { useState, useRef, useEffect } from 'react';
import { Send, Bot, User } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { generateExplanation, ExplanationStyle, AgentOutput } from '@/lib/explanationAgent';
import { VideoContext } from '@/lib/videoContext';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';

interface AICoachProps {
  videoContext: VideoContext | null;
}

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp?: number;
  tags?: string[];
}

const AICoach = ({ videoContext }: AICoachProps) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [style, setStyle] = useState<ExplanationStyle>('NFL analogies');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async () => {
    if (!inputValue.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: inputValue.trim(),
      timestamp: videoContext?.currentTime,
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    try {
      const response: AgentOutput = await generateExplanation({
        userMessage: userMessage.content,
        videoContext,
        style,
      });

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: response.responseText,
        timestamp: response.timestampUsed,
        tags: response.tags,
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Error generating explanation:', error);
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.',
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <div className="flex flex-col h-full bg-card/50 rounded-lg chalk-border overflow-hidden min-h-0">
      <div className="p-4 border-b border-chalk-white/10">
        <div className="flex items-center gap-2 mb-3">
          <Bot className="w-5 h-5 text-chalk-green" />
          <h2 className="font-chalk text-xl text-chalk">AI Coach</h2>
        </div>
        <Select value={style} onValueChange={(value) => setStyle(value as ExplanationStyle)}>
          <SelectTrigger className="bg-black/40 border-chalk-white/20 text-foreground">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="NFL analogies">NFL Analogies</SelectItem>
            <SelectItem value="Beginner friendly">Beginner Friendly</SelectItem>
            <SelectItem value="Tactical">Tactical</SelectItem>
          </SelectContent>
        </Select>
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 && (
          <div className="text-center text-muted-foreground text-sm py-8">
            <p className="mb-2">Ask me anything about the video!</p>
            <p className="text-xs">Try: "Explain what's happening right now"</p>
            <p className="text-xs">or "Who's pressing and why?"</p>
          </div>
        )}
        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex gap-3 ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            {message.role === 'assistant' && (
              <div className="w-8 h-8 rounded-full bg-chalk-green/20 flex items-center justify-center flex-shrink-0">
                <Bot className="w-4 h-4 text-chalk-green" />
              </div>
            )}
            <div
              className={`max-w-[80%] rounded-lg p-3 ${
                message.role === 'user'
                  ? 'bg-chalk-green/20 text-foreground'
                  : 'bg-black/40 text-foreground/90'
              }`}
            >
              <p className="text-sm leading-relaxed whitespace-pre-wrap">{message.content}</p>
              {message.timestamp !== undefined && (
                <p className="text-xs text-muted-foreground mt-2">
                  {formatTime(message.timestamp)}s
                </p>
              )}
              {message.tags && message.tags.length > 0 && (
                <div className="flex flex-wrap gap-1 mt-2">
                  {message.tags.map((tag, idx) => (
                    <span
                      key={idx}
                      className="text-xs px-2 py-0.5 bg-chalk-green/20 text-chalk-green rounded"
                    >
                      {tag}
                    </span>
                  ))}
                </div>
              )}
            </div>
            {message.role === 'user' && (
              <div className="w-8 h-8 rounded-full bg-muted flex items-center justify-center flex-shrink-0">
                <User className="w-4 h-4 text-muted-foreground" />
              </div>
            )}
          </div>
        ))}
        {isLoading && (
          <div className="flex gap-3 justify-start">
            <div className="w-8 h-8 rounded-full bg-chalk-green/20 flex items-center justify-center flex-shrink-0">
              <Bot className="w-4 h-4 text-chalk-green" />
            </div>
            <div className="bg-black/40 rounded-lg p-3">
              <div className="flex gap-1">
                <div className="w-2 h-2 bg-foreground/60 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                <div className="w-2 h-2 bg-foreground/60 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                <div className="w-2 h-2 bg-foreground/60 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <div className="p-4 border-t border-chalk-white/10">
        <div className="flex gap-2">
          <Textarea
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask about the video..."
            className="bg-black/40 border-chalk-white/20 text-foreground placeholder:text-muted-foreground resize-none min-h-[60px]"
            disabled={isLoading}
          />
          <Button
            onClick={handleSend}
            disabled={!inputValue.trim() || isLoading}
            className="bg-chalk-green hover:bg-chalk-green/80 text-chalkboard flex-shrink-0"
          >
            <Send className="w-4 h-4" />
          </Button>
        </div>
      </div>
    </div>
  );
};

export default AICoach;
