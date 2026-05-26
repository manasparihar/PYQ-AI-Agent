import React, { useState } from 'react';

const ChatInput = ({ onSend, isLoading }) => {
  const [input, setInput] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;
    onSend(input);
    setInput('');
  };

  return (
    <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-[#1E1E2E] via-[#1E1E2E]/90 to-transparent pt-12 pb-6 px-4 md:px-8 pointer-events-none">
      <form onSubmit={handleSubmit} className="max-w-3xl mx-auto relative flex items-end bg-[#2A2A3C] rounded-2xl shadow-xl border border-gray-700/50 focus-within:border-gray-500 transition-colors pointer-events-auto">
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
              e.preventDefault();
              handleSubmit(e);
            }
          }}
          placeholder="Message PYQ Agent..."
          className="w-full bg-transparent text-gray-100 rounded-2xl pl-4 pr-12 py-4 focus:outline-none resize-none max-h-48 overflow-y-auto placeholder-gray-400"
          rows={1}
          style={{ minHeight: '56px' }}
        />
        <button
          type="submit"
          disabled={!input.trim() || isLoading}
          className="absolute right-2 bottom-2 p-2 rounded-xl text-white bg-blue-600 hover:bg-blue-500 disabled:opacity-30 disabled:bg-gray-600 disabled:text-gray-400 transition-all flex items-center justify-center"
        >
          <svg stroke="currentColor" fill="none" strokeWidth="2" viewBox="0 0 24 24" className="w-5 h-5" xmlns="http://www.w3.org/2000/svg">
            <path strokeLinecap="round" strokeLinejoin="round" d="M4.5 12h15m0 0l-6.75-6.75M19.5 12l-6.75 6.75" />
          </svg>
        </button>
      </form>
      <div className="text-center text-xs text-gray-500 mt-3 font-medium pointer-events-auto">
        AI PYQ Agent can make mistakes. Verify important information.
      </div>
    </div>
  );
};

export default ChatInput;
