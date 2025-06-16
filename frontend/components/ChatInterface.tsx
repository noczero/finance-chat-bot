import React, { useState, useRef, useEffect } from 'react';
import { FiSend, FiUpload } from 'react-icons/fi';
import ReactMarkdown from 'react-markdown';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  created_at: string;
  sources?: Array<{
    content: string;
    page: number;
    score: number;
  }>;
}

interface ChatInterfaceProps {
  messages: Message[];
  setMessages: React.Dispatch<React.SetStateAction<Message[]>>;
  onError?: (error: string) => void;
  onFileUpload?: () => void;
  onRefreshConversations?: (result: boolean) => void;
}

export default function ChatInterface({ messages, setMessages, onError, onFileUpload, onRefreshConversations }: ChatInterfaceProps) {
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);
  const [expandedSources, setExpandedSources] = useState<{ [key: string]: boolean }>({});


  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async () => {
    if (!input.trim()) return;

    try {
      setIsLoading(true);

      const userMessage: Message = {
        id: Date.now().toString(),
        role: 'user',
        content: input.trim(),
        created_at: getFormattedDateNow()
      };
      setMessages((prev: Message[]) => [...prev, userMessage]);
      setInput('');

      const response = await fetch('http://localhost:8000/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          question: userMessage.content,
          conversation_token: window.location.pathname.slice(1)
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to get response from server');
      }

      const data = await response.json();

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: data.answer,
        created_at: getFormattedDateNow(),
        sources: data.sources
      };
      setMessages((prev: Message[]) => [...prev, assistantMessage]);

      window.history.pushState(null, '', `/${data.conversation_token}`);

      onRefreshConversations?.(true);

    } catch (error) {
      console.error('Error sending message:', error);
      onError?.(error instanceof Error ? error.message : 'Failed to send message');
    } finally {
      setIsLoading(false);
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setInput(e.target.value);
    // Auto-resize textarea
    if (inputRef.current) {
      inputRef.current.style.height = 'auto';
      inputRef.current.style.height = `${Math.min(inputRef.current.scrollHeight, 200)}px`;
    }2
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const getFormattedDateNow = () => {
    const now = new Date();

    const options: Intl.DateTimeFormatOptions = {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
      timeZoneName: 'short'
    };

    return now.toLocaleDateString([], options)
  }

  const toggleSources = (messageId: string) => {
    setExpandedSources(prev => ({ ...prev, [messageId]: !prev[messageId] }));
  };

  const questions = [
    "What is the total revenue for 2025?",
    "What is the year-over-year operating profit growth rate?",
    "What are the main cost items?",
    "How is the cash flow situation?",
    "What is the debt ratio?",
    "How does the balance sheet look for this quarter?",
    "What are the key financial ratios?",
    "Can you explain the cash flow statement?"
  ];



  return (
    <div className="flex flex-col h-full">
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 ? (
          <div className="flex items-center justify-center">
            <div className="text-center text-gray-500">
              <p className="text-lg font-medium mb-2">Welcome to Financial Assistant</p>
              <p className="text-md font-medium mb-2">What would you like to do?</p>
              <p className="text-sm">Start a conversation by asking a question about financial statements or upload a document for a complete review!</p>

              <div className="grid grid-cols-2 gap-4 mt-4">
                {questions.map((question, index) => (
                  <div
                    key={index}
                    className="bg-white shadow-md rounded-lg p-4 cursor-pointer"
                    onClick={() => setInput(question)}
                  >
                    <p className="text-sm text-gray-700 font-semibold">{question}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        ) : (
          messages.map((message) => (
            <div
              key={message.id}
              className={`flex ${
                message.role === 'user' ? 'justify-end' : 'justify-start'
              }`}
            >
              <div className="flex flex-col max-w-[80%]">
                <div
                  className={`rounded-2xl px-4 py-2 ${
                    message.role === 'user'
                      ? 'bg-blue-500 text-white rounded-br-none'
                      : 'bg-white text-gray-800 rounded-bl-none shadow-sm'
                  }`}
                >
                  <ReactMarkdown>{message.content}</ReactMarkdown>

                  {message.role === 'assistant' && message.sources && (
                    <div className="mt-2 text-sm">
                      <p
                        className="font-semibold text-gray-700 cursor-pointer"
                        onClick={() => toggleSources(message.id)}
                      >
                        Sources ({message.sources.length}):
                      </p>
                      {expandedSources[message.id] && message.sources.map((source, index) => (
                        <div key={index} className="mt-1 bg-gray-50 p-2 rounded">
                          <p className="text-xs text-gray-500">Page {source.page} (Score: {source.score.toFixed(2)})</p>
                          <p className="text-xs text-gray-600">{source.content}</p>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
                <span className="text-xs text-gray-400 mt-1">
                  {message.created_at}
                </span>
              </div>
            </div>
          ))
        )}
        {isLoading && (
          <div className="flex justify-start">
            <div className="bg-white rounded-2xl px-4 py-2 shadow-sm">
              <div className="flex space-x-2">
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" />
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-100" />
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-200" />
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <div className="border-t border-gray-200 bg-white p-4">
        <div className="max-w-4xl mx-auto">
          <div className="flex items-center gap-2">
            <button
              onClick={onFileUpload}
              className="p-2 text-gray-400 hover:text-gray-600 rounded-lg hover:bg-gray-100"
              title="Upload document"
            >
              <FiUpload className="w-5 h-5" />
            </button>
            <div className="flex-1 relative">
              <textarea
                ref={inputRef}
                value={input}
                onChange={handleInputChange}
                onKeyDown={handleKeyPress}
                placeholder="Ask a question about the financial statement..."
                className="w-full p-3 pr-12 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none min-h-[44px] max-h-[200px]"
                disabled={isLoading}
                rows={1}
              />
              <button
                onClick={handleSendMessage}
                disabled={isLoading || !input.trim()}
                className={`absolute right-2 top-1/2 -translate-y-1/2 p-2 text-gray-400 hover:text-gray-600 disabled:opacity-50 disabled:cursor-not-allowed ${
                  isLoading || !input.trim()
                    ? 'bg-gray-300'
                    : 'bg-blue-500 hover:bg-blue-600 text-white'
                }`}
              >
                <FiSend className="w-5 h-5" />
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
} 