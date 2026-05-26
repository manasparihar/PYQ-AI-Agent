import React, { useEffect, useRef } from 'react';
import ChatMessage from './ChatMessage';

const ChatWindow = ({ messages, isLoading }) => {
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  return (
    <div className="flex-1 flex flex-col relative h-full">
      {messages.length === 0 ? (
        <div className="flex-1 flex flex-col items-center justify-center p-8 text-center h-full max-w-2xl mx-auto mt-[-10vh]">
          <div className="w-16 h-16 bg-gradient-to-tr from-blue-600 to-emerald-500 rounded-2xl flex items-center justify-center font-bold text-white text-2xl shadow-xl shadow-blue-500/20 mb-6 ring-1 ring-white/10">
            P
          </div>
          <h2 className="text-2xl md:text-3xl font-bold text-white mb-3 tracking-tight">How can I help you today?</h2>
          <p className="text-gray-400 max-w-md text-sm md:text-base leading-relaxed">
            I am your AI agent for Previous Year Questions. Ask me to search past papers for RPSC, REET, SSC, or test me on any topic!
          </p>
        </div>
      ) : (
        <div className="flex-1 pb-36"> {/* Padding bottom to clear sticky input */}
          {messages.map((msg, idx) => (
            <ChatMessage key={idx} message={msg} />
          ))}
          
          {isLoading && (
            <div className="py-6 px-4 flex w-full bg-[#252538]">
              <div className="max-w-3xl mx-auto flex gap-4 md:gap-6 w-full">
                <div className="w-8 h-8 rounded-full flex items-center justify-center shrink-0 bg-gradient-to-tr from-blue-600 to-emerald-500 text-white text-sm font-bold shadow-sm">
                  AI
                </div>
                <div className="flex items-center gap-1.5 h-8">
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.4s' }}></div>
                </div>
              </div>
            </div>
          )}
          <div ref={bottomRef} className="h-4" />
        </div>
      )}
    </div>
  );
};

export default ChatWindow;
