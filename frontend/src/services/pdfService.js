import { api, API_URL } from './api';

/**
 * Calls the FastAPI backend to generate a PDF for specific content.
 * @param {string} title - The title of the PDF
 * @param {string} content - The actual text content to convert
 * @returns {Promise<Object>} The API response containing the relative pdf_url
 */
export const exportContentToPDF = async (title, content) => {
  try {
    const response = await api.post('/generate-pdf', {
      title,
      content
    });
    return response.data;
  } catch (error) {
    throw new Error(error.response?.data?.detail || 'Failed to generate PDF. Please try again.');
  }
};

/**
 * Constructs the full absolute URL for the PDF so the browser can download it.
 * Uses the environment-based API_URL to support production deployments.
 */
export const getFullPdfUrl = (pdfUrl) => {
  const cleanUrl = pdfUrl.startsWith('/') ? pdfUrl : `/${pdfUrl}`;
  return `${API_URL}${cleanUrl}`;
};
