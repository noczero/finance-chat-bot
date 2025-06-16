import React, {useEffect, useState} from 'react';
import Head from 'next/head';
import FileUpload from '../components/FileUpload';
import ChatInterface from '../components/ChatInterface';
import { FiX } from 'react-icons/fi';
import ChatHistory from "@/components/ChatHistory";
import Header from "@/components/Header";

export default function DynamicHome() {
  const [error, setError] = useState<string | null>(null);
  const [isUploadOpen, setIsUploadOpen] = useState(false);
  const [messages, setMessages] = useState<any[]>([]); // Add messages state
  const [refreshConversations, setRefreshConversations] = useState(false); // Add boolean state


  const handleUploadComplete = (result: any) => {
    setError(null);
    setIsUploadOpen(false);
  };

  const handleUploadError = (error: string) => {
    setError(error);
  };

  const handleChatError = (error: string) => {
    setError(error);
  };

  const handleMessagesUpdate = (newMessages: any[]) => {
    setMessages(newMessages);
  };

  const fetchMessages = async (token_conversation: string) => {
        try {
          const response = await fetch(`http://localhost:8000/api/conversations/${token_conversation}/messages`);
          if (response.status !== 200) {
            throw new Error('Messages not found');
          }
          const data = await response.json();

           const formattedMessages = data.messages.map((message: any) => ({
            ...message,
            created_at: formattedCreatedAtToLocalTimezone(message.created_at),
          }));

          setMessages(formattedMessages);
        } catch (error: any) {
          setError(error.message);
        }
  };

  useEffect(() => {
    const pathname = window.location.pathname;
    fetchMessages(pathname.substring(1))
  }, []);

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
    <div className="min-h-screen bg-gray-50">
      <Head>
        <title>Financial Assistant</title>
        <meta name="description" content="AI-powered Q&A system for financial documents" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <Header/>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {error && (
          <div className="mb-4">
            <div className="rounded-md bg-red-50 p-4">
              <div className="flex">
                <div className="flex-shrink-0">
                  <FiX className="h-5 w-5 text-red-400" />
                </div>
                <div className="ml-3">
                  <p className="text-sm font-medium text-red-800">{error}</p>
                </div>
              </div>
            </div>
          </div>
        )}

        <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
          <div className="flex h-[calc(100vh-12rem)]">
            <ChatHistory
                onMessagesUpdate={handleMessagesUpdate}
                refreshConversations={refreshConversations} // Pass boolean state
            />

            <div className="flex-1 flex flex-col">
              <div className="flex-1 overflow-hidden">
                <ChatInterface
                  messages={messages}
                  setMessages={setMessages}
                  onError={handleChatError}
                  onFileUpload={() => setIsUploadOpen(true)}
                  onRefreshConversations={() => setRefreshConversations(true)}
                />
              </div>

              {isUploadOpen && (
                <div className="absolute inset-0 bg-black bg-opacity-50 flex items-center justify-center">
                  <div className="bg-white rounded-lg shadow-xl p-6 w-full max-w-md">
                    <div className="flex justify-between items-center mb-4">
                      <h3 className="text-lg font-medium text-gray-900">Upload Financial Document</h3>
                      <button
                        onClick={() => setIsUploadOpen(false)}
                        className="text-gray-400 hover:text-gray-600"
                      >
                        <FiX className="w-5 h-5" />
                      </button>
                    </div>
                    <FileUpload
                      onUploadComplete={handleUploadComplete}
                      onUploadError={handleUploadError}
                    />
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
