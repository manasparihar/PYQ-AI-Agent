import React, { useState } from 'react';
import { exportContentToPDF, getFullPdfUrl } from '../services/pdfService';

const PDFButton = ({ content, title = "AI PYQ Response" }) => {
  const [isGenerating, setIsGenerating] = useState(false);
  const [statusMessage, setStatusMessage] = useState(null);

  const handleGenerateAndDownload = async () => {
    if (!content) return;
    
    setIsGenerating(true);
    setStatusMessage(null);
    
    try {
      // 1. Call backend API with specific message content
      const result = await exportContentToPDF(title, content);
      
      if (result.success && result.pdf_url) {
        // 2. Automatically open/download PDF in browser
        const fullUrl = getFullPdfUrl(result.pdf_url);
        window.open(fullUrl, '_blank');
        
        // 3. Show success toast message
        setStatusMessage({ type: 'success', text: 'PDF exported successfully!' });
        setTimeout(() => setStatusMessage(null), 3000);
      } else {
        setStatusMessage({ type: 'error', text: 'Backend failed to return PDF url.' });
        setTimeout(() => setStatusMessage(null), 3000);
      }
    } catch (err) {
      // 4. Handle API errors properly
      setStatusMessage({ type: 'error', text: err.message });
      setTimeout(() => setStatusMessage(null), 5000);
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <div className="flex flex-col items-start relative mt-4">
      <button
        onClick={handleGenerateAndDownload}
        disabled={isGenerating || !content}
        className="flex items-center gap-1.5 px-3 py-1.5 bg-[#2A2A3C] hover:bg-[#323246] text-gray-300 rounded-lg transition-all shadow-sm disabled:opacity-50 disabled:cursor-not-allowed text-[13px] font-medium border border-gray-700/50 focus:outline-none focus:ring-2 focus:ring-blue-500/50 hover:shadow-md hover:text-white"
      >
        {isGenerating ? (
          <span className="animate-spin h-3.5 w-3.5 border-2 border-gray-500 border-t-gray-200 rounded-full"></span>
        ) : (
          <svg xmlns="http://www.w3.org/2000/svg" className="h-3.5 w-3.5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
        )}
        {isGenerating ? 'Exporting...' : 'Export PDF'}
      </button>
      
      {/* Dynamic Toast Messages */}
      {statusMessage && (
        <div className={`absolute top-full mt-1.5 px-2.5 py-1 rounded-md text-[11px] font-medium whitespace-nowrap z-50 shadow-md ${
          statusMessage.type === 'success' 
            ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' 
            : 'bg-red-500/10 text-red-400 border border-red-500/20'
        }`}>
          {statusMessage.text}
        </div>
      )}
    </div>
  );
};

export default PDFButton;
