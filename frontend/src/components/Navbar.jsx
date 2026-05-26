import React from 'react';

const Navbar = ({ onNewChat }) => {
  return (
    <nav className="bg-gray-800 border-b border-gray-700 px-6 py-4 flex items-center justify-between shadow-sm relative z-20">
      <div className="flex items-center gap-3">
        <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center font-bold text-white shadow-md">
          P
        </div>
        <h1 className="text-xl font-bold text-gray-100 tracking-tight">AI PYQ Agent</h1>
      </div>
      <div className="flex items-center gap-4">
        {onNewChat && (
          <button 
            onClick={onNewChat}
            className="px-4 py-2 bg-gray-700 hover:bg-gray-600 text-gray-200 text-sm font-medium rounded-lg transition-colors border border-gray-600 shadow-sm"
          >
            + New Chat
          </button>
        )}
        <div className="text-sm text-gray-400 font-medium hidden sm:block">
          Powered by Gemini ⚡
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
