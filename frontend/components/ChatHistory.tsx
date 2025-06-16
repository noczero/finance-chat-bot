import React, { useState, useEffect } from 'react';
import { useRouter } from "next/router";
import { MdEditDocument } from "react-icons/md";

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  created_at: string;
}

interface ChatHistoryProps {
  onMessagesUpdate: (message: any) => void;
  refreshConversations: boolean;
}

const ChatHistory = ({ onMessagesUpdate, refreshConversations }: ChatHistoryProps) => {
  const [conversations, setConversations] = useState<any[]>([]);
  const [selectedToken, setSelectedToken] = useState<string | null>(null);
  const router = useRouter();

  const fetchConversations = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/conversations');
      if (response.status !== 200) {
        throw new Error('Conversations not found');
      }
      const data = await response.json();
      setConversations(data);
    } catch (error: any) {
      setConversations([]);
    }
  };

  useEffect(() => {
    const pathname = window.location.pathname;
    setSelectedToken(pathname.substring(1))
    fetchConversations();
  }, [refreshConversations]);

  const handleConversationClick = async (token: string) => {
    try {
      const response = await fetch(`http://localhost:8000/api/conversations/${token}/messages`);
      const data = await response.json();

      const formattedMessages = data.messages.map((message: Message) => ({
        ...message,
        created_at: formattedCreatedAtToLocalTimezone(message.created_at),
      }));

      onMessagesUpdate(formattedMessages);
    } catch (error) {
      console.error('Error fetching messages:', error);
    }

    window.history.pushState(null, '', `/${token}`);

    setSelectedToken(token);

    fetchConversations();
  };

  const handleRedirectHome = () => {
    router.push('/').then(() => {
      router.reload();
    });
  };

  const formattedCreatedAtToLocalTimezone = (created_at: string) => {
    const date = new Date(created_at);

    const offsetMinutes = date.getTimezoneOffset();

    date.setMinutes(date.getMinutes() - offsetMinutes);

    const options: Intl.DateTimeFormatOptions = {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
      timeZoneName: 'short'
    };

    return date.toLocaleString([], options);
  }

  return (
    <div className="w-80 border-r border-gray-200 bg-gray-50">
      <div className="p-4 border-b border-gray-200 flex justify-between items-center">
        <h2 className="text-lg font-semibold text-gray-800">Recents</h2>
        <button
          className="text-gray-800 hover:text-gray-500"
          onClick={handleRedirectHome}
        >
          <MdEditDocument size={24} />
        </button>
      </div>
      <div className="overflow-y-auto h-[calc(100%-4rem)]">
        {(
          conversations.map((conversation: any) => (
            <div
              key={conversation.token}
              className={`p-4 cursor-pointer border-b border-gray-200 ${
                selectedToken === conversation.token ? 'bg-gray-300' : 'hover:bg-gray-100'
              }`}
              onClick={() => handleConversationClick(conversation.token)}
            >
              <div className="flex items-center space-x-3">
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-gray-900 truncate">
                    {conversation.name}
                  </p>
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

export default ChatHistory;
