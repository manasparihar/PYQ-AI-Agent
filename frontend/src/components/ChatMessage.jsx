import React from 'react';
import ReactMarkdown from 'react-markdown';
import PDFButton from './PDFButton';

const ChatMessage = ({ message }) => {
  const isUser = message.role === 'user';
  
  return (
    <div className={`py-6 px-4 flex w-full transition-all duration-300 ${isUser ? 'bg-transparent' : 'bg-[#252538]'}`}>
      <div className="max-w-3xl mx-auto flex gap-4 md:gap-6 w-full group">
        <div className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 text-sm font-bold shadow-sm mt-0.5 ${isUser ? 'bg-gray-600 text-white' : 'bg-gradient-to-tr from-blue-600 to-emerald-500 text-white'}`}>
          {isUser ? 'U' : 'AI'}
        </div>
        <div className="flex-1 overflow-x-auto min-w-0">
          <div className="prose prose-invert prose-blue max-w-none text-gray-200 leading-relaxed prose-pre:bg-[#1A1A27] prose-pre:border prose-pre:border-gray-700/50">
            {isUser ? (
              <div className="whitespace-pre-wrap text-[15px]">{message.content}</div>
            ) : (
              <ReactMarkdown>{message.content}</ReactMarkdown>
            )}
          </div>
          
          {/* Inject PDF Export Button for individual AI responses */}
          {!isUser && (
            <div className="mt-3 opacity-0 group-hover:opacity-100 transition-opacity duration-200">
               <PDFButton content={message.content} title="AI PYQ Response Export" />
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ChatMessage;
