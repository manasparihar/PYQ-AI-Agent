import React, { useState, useEffect } from 'react';
import Sidebar from '../components/Sidebar';
import ChatWindow from '../components/ChatWindow';
import ChatInput from '../components/ChatInput';
import { createSession, streamChatWithAI } from '../services/api';

const Home = () => {
  const [sessionId, setSessionId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isInitializing, setIsInitializing] = useState(true); // Prevent messaging before session loads
  const [error, setError] = useState(null);
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);

  // Initialize session on mount
  useEffect(() => {
    const initSession = async (retries = 1) => {
      setIsInitializing(true);
      setError(null);
      
      // 1. Try to load from localStorage first
      const storedSessionId = localStorage.getItem('chat_session_id');
      const storedMessages = localStorage.getItem('chat_messages');
      
      if (storedSessionId) {
        console.log("Restoring existing session:", storedSessionId);
        setSessionId(storedSessionId);
        try {
          if (storedMessages) {
            setMessages(JSON.parse(storedMessages));
          }
        } catch(e) {
          setMessages([]);
        }
        setIsInitializing(false);
        return; // Restored successfully
      }

      // 2. Otherwise create a new session
      console.log("Creating new session...");
      try {
        const result = await createSession();
        console.log("Session creation response:", result);
        
        // Backend returns { "session_id": "..." }
        if (result && result.session_id) {
          setSessionId(result.session_id);
          localStorage.setItem('chat_session_id', result.session_id);
          console.log("New session created and stored:", result.session_id);
        } else {
          throw new Error("Invalid response format: missing session_id");
        }
      } catch (err) {
        console.error("Failed to create session:", err);
        if (retries > 0) {
          console.log(`Retrying session creation... (${retries} attempts left)`);
          return initSession(retries - 1);
        }
        setError("Could not connect to backend. Please verify your internet connection and backend status.");
      } finally {
        setIsInitializing(false);
      }
    };
    
    initSession();
  }, []);

  // Save messages to localStorage whenever they change
  useEffect(() => {
    if (messages.length > 0) {
      localStorage.setItem('chat_messages', JSON.stringify(messages));
    }
  }, [messages]);

  const handleNewChat = async () => {
    localStorage.removeItem('chat_session_id');
    localStorage.removeItem('chat_messages');
    setMessages([]);
    setError(null);
    setIsInitializing(true); // Block input while creating
    
    console.log("Starting new chat...");
    try {
      const result = await createSession();
      console.log("New chat session response:", result);
      
      if (result && result.session_id) {
        setSessionId(result.session_id);
        localStorage.setItem('chat_session_id', result.session_id);
        console.log("New chat session created:", result.session_id);
      } else {
        throw new Error("Invalid response format: missing session_id");
      }
    } catch (err) {
      console.error("Failed to start new chat:", err);
      setError("Failed to start new chat. Please try again.");
    } finally {
      setIsInitializing(false);
    }
  };

  const handleSendMessage = async (prompt) => {
    if (!sessionId) {
      setError("No active session. Please refresh the page to start a new session.");
      return;
    }
    
    console.log(`Sending message in session [${sessionId}]:`, prompt);
    
    // Add user message to UI immediately
    const userMsg = { role: 'user', content: prompt };
    setMessages(prev => [...prev, userMsg]);
    
    setIsLoading(true);
    setError(null);
    
    // Insert an empty assistant message that will be populated via the stream
    setMessages(prev => [...prev, { role: 'assistant', content: '' }]);
    
    try {
      await streamChatWithAI(sessionId, prompt, (chunk) => {
        setIsLoading(false); // Stop showing bouncing dots once we receive the first chunk
        setMessages(prev => {
          const newMessages = [...prev];
          const lastMsgIndex = newMessages.length - 1;
          
          // Append the new chunk to the last assistant message
          newMessages[lastMsgIndex] = {
            ...newMessages[lastMsgIndex],
            content: newMessages[lastMsgIndex].content + chunk
          };
          return newMessages;
        });
      });
      console.log("Message stream completed successfully.");
    } catch (err) {
      console.error("Chat API error:", err);
      setError(err.message || "Failed to communicate with AI.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex h-screen bg-[#1E1E2E] text-gray-100 overflow-hidden font-sans selection:bg-blue-500/30">
      {/* Mobile Sidebar Overlay */}
      {isSidebarOpen && (
        <div 
          className="fixed inset-0 bg-black/60 backdrop-blur-sm z-40 md:hidden transition-opacity"
          onClick={() => setIsSidebarOpen(false)}
        />
      )}

      {/* Sidebar Area */}
      <div className={`fixed inset-y-0 left-0 z-50 transform ${isSidebarOpen ? 'translate-x-0' : '-translate-x-full'} md:relative md:translate-x-0 transition duration-300 ease-in-out flex-shrink-0`}>
        <Sidebar onNewChat={() => { handleNewChat(); setIsSidebarOpen(false); }} />
      </div>

      {/* Main Chat Area */}
      <div className="flex flex-col flex-1 min-w-0 h-full relative">
        {/* Mobile Header */}
        <div className="md:hidden flex items-center justify-between p-4 border-b border-gray-800 bg-[#1E1E2E] z-10">
          <button onClick={() => setIsSidebarOpen(true)} className="text-gray-300 hover:text-white p-1 rounded-md hover:bg-gray-800 transition-colors">
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
               <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 6h16M4 12h16M4 18h16"></path>
            </svg>
          </button>
          <div className="font-semibold text-gray-200">AI PYQ Agent</div>
          <button onClick={handleNewChat} className="text-gray-300 hover:text-white p-1 rounded-md hover:bg-gray-800 transition-colors">
             <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 4v16m8-8H4"></path>
             </svg>
          </button>
        </div>

        {error && (
          <div className="bg-red-500/10 text-red-400 px-4 py-3 text-center text-sm border-b border-red-500/20 font-medium z-10 shrink-0">
            ⚠️ {error}
          </div>
        )}
        
        {isInitializing && !sessionId && (
          <div className="bg-blue-500/10 text-blue-400 px-4 py-3 text-center text-sm border-b border-blue-500/20 font-medium z-10 shrink-0 flex items-center justify-center gap-2">
            <div className="w-4 h-4 border-2 border-blue-400 border-t-transparent rounded-full animate-spin"></div>
            Connecting to AI backend...
          </div>
        )}
        
        <div className="flex-1 overflow-y-auto w-full scroll-smooth">
          <ChatWindow 
            messages={messages} 
            isLoading={isLoading} 
            sessionId={sessionId} 
          />
        </div>
        
        <div className="w-full shrink-0">
          <ChatInput onSend={handleSendMessage} isLoading={isLoading || isInitializing} />
        </div>
      </div>
    </div>
  );
};

export default Home;
