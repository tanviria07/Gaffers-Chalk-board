import { useState, useRef, useEffect } from 'react';
import { Send, Bot, User } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { ScrollArea } from '@/components/ui/scroll-area';
import { sendChatMessage } from '@/lib/chatAgent';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: number;
}

interface ChatBotProps {
  videoId: string | null;
  currentTime: number;
  context?: {
    commentary?: string;
    nflAnalogy?: string;
  };
  videoMetadata?: {
    title?: string;
    description?: string;
    uploader?: string;
  };
}

const ChatBot = ({ videoId, currentTime, context, videoMetadata }: ChatBotProps) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const isDisabled = !videoId;

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || isDisabled || isLoading || !videoId) return;

    const frozenTimestamp = currentTime;
    const messageToSend = input.trim();

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: messageToSend,
      timestamp: frozenTimestamp,
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const response = await sendChatMessage({
        videoId,
        timestamp: frozenTimestamp,
        userMessage: messageToSend,
        context: context,
        videoMetadata: videoMetadata,
      });

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: response.response,
        timestamp: response.timestamp,
      };
      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Chat error:', error);
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.',
        timestamp: currentTime,
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="flex flex-col h-[300px] bg-card/50 rounded-lg chalk-border overflow-hidden">
      <div className="flex items-center gap-2 px-3 py-2 border-b border-chalk-white/20 flex-shrink-0">
        <Bot className="w-4 h-4 text-chalk-yellow" />
        <h3 className="font-chalk text-sm text-chalk-yellow">Ask About This Play</h3>
      </div>

      <ScrollArea className="flex-1 min-h-0">
        <div className="px-3 py-2 space-y-3">
          {messages.length === 0 ? (
            <div className="text-center py-4">
              <p className="text-xs text-chalk-white/50 font-body">
                {isDisabled
                  ? 'Load a video to start chatting'
                  : 'Ask questions about the current play'}
              </p>
            </div>
          ) : (
            messages.map((message) => (
              <div
                key={message.id}
                className={`flex gap-2 ${
                  message.role === 'user' ? 'justify-end' : 'justify-start'
                }`}
              >
                {message.role === 'assistant' && (
                  <div className="w-6 h-6 rounded-full bg-chalk-yellow/20 border border-chalk-yellow/40 flex items-center justify-center flex-shrink-0 mt-0.5">
                    <Bot className="w-3 h-3 text-chalk-yellow" />
                  </div>
                )}
                <div
                  className={`max-w-[80%] rounded-lg px-3 py-2 ${
                    message.role === 'user'
                      ? 'bg-chalk-yellow/20 border border-chalk-yellow/30 text-chalk-white'
                      : 'bg-chalk-green-light/40 border border-chalk-white/20 text-chalk-white/90'
                  }`}
                >
                  <p className="text-xs font-body leading-relaxed">{message.content}</p>
                </div>
                {message.role === 'user' && (
                  <div className="w-6 h-6 rounded-full bg-chalk-white/10 border border-chalk-white/30 flex items-center justify-center flex-shrink-0 mt-0.5">
                    <User className="w-3 h-3 text-chalk-white/70" />
                  </div>
                )}
              </div>
            ))
          )}
          {isLoading && (
            <div className="flex gap-2 justify-start">
              <div className="w-6 h-6 rounded-full bg-chalk-yellow/20 border border-chalk-yellow/40 flex items-center justify-center flex-shrink-0 mt-0.5">
                <Bot className="w-3 h-3 text-chalk-yellow" />
              </div>
              <div className="bg-chalk-green-light/40 border border-chalk-white/20 rounded-lg px-3 py-2">
                <div className="flex gap-1">
                  <div className="w-2 h-2 rounded-full bg-chalk-yellow animate-pulse" style={{ animationDelay: '0ms' }} />
                  <div className="w-2 h-2 rounded-full bg-chalk-yellow animate-pulse" style={{ animationDelay: '150ms' }} />
                  <div className="w-2 h-2 rounded-full bg-chalk-yellow animate-pulse" style={{ animationDelay: '300ms' }} />
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>
      </ScrollArea>

      <div className="border-t border-chalk-white/20 p-2 flex-shrink-0">
        <div className="flex gap-2">
          <Input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder={isDisabled ? 'Load a video first...' : 'Ask about this play...'}
            disabled={isDisabled || isLoading}
            className="flex-1 bg-background/50 border-chalk-white/20 text-chalk-white placeholder:text-chalk-white/40 focus-visible:ring-chalk-yellow/50"
          />
          <Button
            onClick={handleSend}
            disabled={isDisabled || isLoading || !input.trim()}
            size="icon"
            className="bg-chalk-yellow/20 hover:bg-chalk-yellow/30 border border-chalk-yellow/40 text-chalk-yellow disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Send className="w-4 h-4" />
          </Button>
        </div>
      </div>
    </div>
  );
};

export default ChatBot;
