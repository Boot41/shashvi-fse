import React, { useState, useEffect } from 'react';
import { leadService } from '../../services';

const LeadMessages = ({ lead, onClose }) => {
  const [messages, setMessages] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [copySuccess, setCopySuccess] = useState({ email: false, linkedin: false });

  useEffect(() => {
    fetchMessages();
  }, [lead.id]);

  const fetchMessages = async () => {
    try {
      const data = await leadService.generateMessages(lead.id);
      setMessages(data);
      setError(null);
    } catch (err) {
      setError('Failed to generate messages. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleCopy = async (text, type) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopySuccess({ ...copySuccess, [type]: true });
      setTimeout(() => {
        setCopySuccess({ ...copySuccess, [type]: false });
      }, 2000);
    } catch (err) {
      console.error('Failed to copy text: ', err);
    }
  };

  return (
    <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full">
      <div className="relative top-20 mx-auto p-5 border w-11/12 md:w-3/4 lg:w-1/2 shadow-lg rounded-md bg-white">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-medium text-gray-900">
            Messages for {lead.name}
          </h3>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-500"
          >
            <span className="sr-only">Close</span>
            <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {loading ? (
          <div className="flex justify-center items-center h-32">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
          </div>
        ) : error ? (
          <div className="bg-red-50 p-4 rounded-md">
            <div className="text-red-700">{error}</div>
          </div>
        ) : (
          <div className="space-y-4">
            <div className="bg-gray-50 p-4 rounded-md">
              <div className="flex justify-between items-start mb-2">
                <h4 className="text-sm font-medium text-gray-900">Email Message</h4>
                <button
                  onClick={() => handleCopy(messages.email_content, 'email')}
                  className="text-indigo-600 hover:text-indigo-900 text-sm"
                >
                  {copySuccess.email ? 'Copied!' : 'Copy'}
                </button>
              </div>
              <pre className="text-sm text-gray-700 whitespace-pre-wrap font-sans">
                {messages.email_content}
              </pre>
            </div>

            <div className="bg-gray-50 p-4 rounded-md">
              <div className="flex justify-between items-start mb-2">
                <h4 className="text-sm font-medium text-gray-900">LinkedIn Message</h4>
                <button
                  onClick={() => handleCopy(messages.linkedin_content, 'linkedin')}
                  className="text-indigo-600 hover:text-indigo-900 text-sm"
                >
                  {copySuccess.linkedin ? 'Copied!' : 'Copy'}
                </button>
              </div>
              <pre className="text-sm text-gray-700 whitespace-pre-wrap font-sans">
                {messages.linkedin_content}
              </pre>
            </div>

            <div className="mt-4 flex justify-end space-x-3">
              <button
                onClick={fetchMessages}
                className="px-4 py-2 text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 rounded-md"
              >
                Regenerate Messages
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default LeadMessages;
