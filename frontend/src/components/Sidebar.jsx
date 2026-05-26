import React from 'react';

const Sidebar = ({ onNewChat }) => {
  return (
    <div className="w-64 bg-[#111118] border-r border-gray-800 flex flex-col h-full flex-shrink-0 transition-all duration-300">
      <div className="p-4">
        <button 
          onClick={onNewChat}
          className="w-full flex items-center justify-center gap-2 py-3 px-4 bg-blue-600 hover:bg-blue-700 rounded-lg text-white text-sm font-semibold transition-all duration-200 shadow-md hover:shadow-blue-900/20 focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 4v16m8-8H4"></path>
          </svg>
          New Chat
        </button>
      </div>
      
      <div className="flex-1 overflow-y-auto p-4 pt-2">
        <div className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-3">Today</div>
        {/* Placeholder for future chat history. We only have current session for now. */}
        <div className="px-3 py-2 text-sm text-gray-300 bg-gray-800/50 rounded-md truncate cursor-pointer hover:bg-gray-800 transition-colors">
          Current Session
        </div>
      </div>

      <div className="p-4 border-t border-gray-800/60 bg-[#111118]">
        <div className="flex items-center gap-3 px-2 py-2 rounded-md hover:bg-gray-800/50 transition-colors cursor-pointer">
          <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-blue-600 to-emerald-500 flex items-center justify-center text-white font-bold text-sm shadow-md">
            P
          </div>
          <div className="flex flex-col">
            <span className="text-sm font-medium text-gray-200">PYQ Agent</span>
            <span className="text-xs text-gray-500">Gemini Pro 2.5</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Sidebar;
