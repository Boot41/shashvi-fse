import React, { useState } from 'react';
import { mockLeads, generateMockMessages } from '../../data/mockData';

const OutreachPage = () => {
  const [selectedLead, setSelectedLead] = useState(null);
  const [messages, setMessages] = useState(null);
  const [loading, setLoading] = useState(false);
  const [copyStatus, setCopyStatus] = useState({ email: false, linkedin: false });

  const handleGenerateMessages = async (lead) => {
    setSelectedLead(lead);
    setLoading(true);
    
    // Simulate API call
    setTimeout(() => {
      const generatedMessages = generateMockMessages(lead);
      setMessages(generatedMessages);
      setLoading(false);
    }, 1000);
  };

  const handleCopy = async (text, type) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopyStatus(prev => ({ ...prev, [type]: true }));
      setTimeout(() => {
        setCopyStatus(prev => ({ ...prev, [type]: false }));
      }, 2000);
    } catch (err) {
      console.error('Failed to copy text:', err);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="sm:flex sm:items-center">
        <div className="sm:flex-auto">
          <h1 className="text-2xl font-semibold text-gray-900">Outreach Messages</h1>
          <p className="mt-2 text-sm text-gray-700">
            Generate personalized email and LinkedIn messages for your leads.
          </p>
        </div>
      </div>

      <div className="mt-8 grid grid-cols-1 gap-6 lg:grid-cols-2">
        {/* Leads List */}
        <div className="bg-white shadow rounded-lg overflow-hidden">
          <div className="px-4 py-5 sm:px-6">
            <h3 className="text-lg leading-6 font-medium text-gray-900">Select a Lead</h3>
          </div>
          <ul className="divide-y divide-gray-200 max-h-[600px] overflow-y-auto">
            {mockLeads.map((lead) => (
              <li
                key={lead.id}
                className={`px-4 py-4 hover:bg-gray-50 cursor-pointer ${
                  selectedLead?.id === lead.id ? 'bg-indigo-50' : ''
                }`}
                onClick={() => handleGenerateMessages(lead)}
              >
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-900">{lead.companyName}</p>
                    <p className="text-sm text-gray-500">{lead.contactName} - {lead.position}</p>
                  </div>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      handleGenerateMessages(lead);
                    }}
                    className="inline-flex items-center px-3 py-1.5 border border-transparent text-xs font-medium rounded-md text-indigo-700 bg-indigo-100 hover:bg-indigo-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                  >
                    Generate Messages
                  </button>
                </div>
              </li>
            ))}
          </ul>
        </div>

        {/* Message Preview */}
        <div className="bg-white shadow rounded-lg">
          <div className="px-4 py-5 sm:px-6">
            <h3 className="text-lg leading-6 font-medium text-gray-900">Message Preview</h3>
          </div>
          <div className="px-4 py-5 sm:p-6">
            {loading ? (
              <div className="flex justify-center items-center h-64">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
              </div>
            ) : selectedLead && messages ? (
              <div className="space-y-6">
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <h4 className="text-sm font-medium text-gray-900">Email Message</h4>
                    <button
                      onClick={() => handleCopy(messages.email, 'email')}
                      className="text-sm text-indigo-600 hover:text-indigo-900"
                    >
                      {copyStatus.email ? 'Copied!' : 'Copy'}
                    </button>
                  </div>
                  <div className="bg-gray-50 rounded-md p-4">
                    <pre className="text-sm text-gray-700 whitespace-pre-wrap font-sans">
                      {messages.email}
                    </pre>
                  </div>
                </div>

                <div>
                  <div className="flex items-center justify-between mb-2">
                    <h4 className="text-sm font-medium text-gray-900">LinkedIn Message</h4>
                    <button
                      onClick={() => handleCopy(messages.linkedin, 'linkedin')}
                      className="text-sm text-indigo-600 hover:text-indigo-900"
                    >
                      {copyStatus.linkedin ? 'Copied!' : 'Copy'}
                    </button>
                  </div>
                  <div className="bg-gray-50 rounded-md p-4">
                    <pre className="text-sm text-gray-700 whitespace-pre-wrap font-sans">
                      {messages.linkedin}
                    </pre>
                  </div>
                </div>

                <button
                  onClick={() => handleGenerateMessages(selectedLead)}
                  className="w-full inline-flex justify-center items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                >
                  Regenerate Messages
                </button>
              </div>
            ) : (
              <div className="text-center text-gray-500 py-12">
                Select a lead to generate personalized messages
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default OutreachPage;
