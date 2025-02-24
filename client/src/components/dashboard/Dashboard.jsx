import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { leads, auth } from '../../services/api';

const Dashboard = () => {
  const [leadsData, setLeads] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [selectedFile, setSelectedFile] = useState(null);
  const [uploadStatus, setUploadStatus] = useState('');
  const [selectedLead, setSelectedLead] = useState(null);
  const [messages, setMessages] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    fetchLeads();
  }, []);

  const fetchLeads = async () => {
    try {
      const response = await leads.getAll();
      setLeads(response.data);
      setLoading(false);
    } catch (err) {
      handleError(err);
    }
  };

  const handleError = (err) => {
    if (err.response?.status === 401) {
      auth.logout();
      navigate('/login');
    } else {
      setError(err.response?.data?.error || 'An error occurred');
      setLoading(false);
    }
  };

  const handleLogout = () => {
    auth.logout();
    navigate('/login');
  };

  const handleFileChange = (e) => {
    setSelectedFile(e.target.files[0]);
    setUploadStatus('');
  };

  const handleFileUpload = async () => {
    if (!selectedFile) {
      setUploadStatus('Please select a file first');
      return;
    }

    try {
      setUploadStatus('Uploading...');
      await leads.import(selectedFile);
      setUploadStatus('Upload successful!');
      fetchLeads();
    } catch (err) {
      handleError(err);
      setUploadStatus('Upload failed: ' + (err.response?.data?.error || 'Unknown error'));
    }
  };

  const handleProcessLeads = async () => {
    try {
      await leads.process();
      await fetchLeads(); // Refresh leads list with updated scores
    } catch (err) {
      handleError(err);
    }
  };

  const handleGenerateMessages = async (lead) => {
    try {
      const response = await leads.generateMessages(lead.id);
      setSelectedLead(lead);
      setMessages(response.data);
    } catch (err) {
      handleError(err);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-100 py-6 flex flex-col justify-center sm:py-12">
        <div className="relative py-3 sm:max-w-xl sm:mx-auto">
          <div className="text-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600 mx-auto"></div>
            <p className="mt-2 text-gray-600">Loading your leads...</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-100 py-6">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Lead Dashboard</h1>
          <div className="flex items-center space-x-4">
            <button
              onClick={handleLogout}
              className="px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-red-600 hover:bg-red-700"
            >
              Logout
            </button>
          </div>
        </div>

        <div className="flex justify-between items-center mb-8">
          <div className="flex space-x-4">
            <div>
              <input
                type="file"
                onChange={handleFileChange}
                className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100"
              />
              {uploadStatus && (
                <p className={`mt-2 text-sm ${uploadStatus.includes('failed') ? 'text-red-600' : 'text-green-600'}`}>
                  {uploadStatus}
                </p>
              )}
            </div>
            <button
              onClick={handleFileUpload}
              className="px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700"
            >
              Upload Leads
            </button>
            <button
              onClick={handleProcessLeads}
              className="px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-green-600 hover:bg-green-700"
            >
              Process All Leads
            </button>
          </div>
        </div>

        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
            {error}
          </div>
        )}

        <div className="flex space-x-8">
          <div className="flex-1">
            <div className="bg-white shadow overflow-hidden sm:rounded-md">
              <ul className="divide-y divide-gray-200">
                {leadsData.length === 0 ? (
                  <li className="px-4 py-4 sm:px-6">
                    <p className="text-gray-500 text-center">No leads found. Upload some leads to get started!</p>
                  </li>
                ) : (
                  leadsData.map((lead) => (
                    <li key={lead.id}>
                      <div className="px-4 py-4 sm:px-6">
                        <div className="flex items-center justify-between">
                          <div className="flex-1">
                            <h3 className="text-lg font-medium text-gray-900">{lead.name}</h3>
                            <p className="mt-1 text-sm text-gray-500">{lead.company}</p>
                            <p className="mt-1 text-sm text-gray-500">{lead.email}</p>
                          </div>
                          <div className="flex items-center space-x-4">
                            <span className="px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                              Score: {lead.lead_score || 'N/A'}
                            </span>
                            <button
                              onClick={() => handleGenerateMessages(lead)}
                              className="px-3 py-1 border border-transparent text-sm font-medium rounded-md text-indigo-700 bg-indigo-100 hover:bg-indigo-200"
                            >
                              Generate Messages
                            </button>
                          </div>
                        </div>
                      </div>
                    </li>
                  ))
                )}
              </ul>
            </div>
          </div>

          {selectedLead && messages && (
            <div className="w-96">
              <div className="bg-white shadow sm:rounded-lg">
                <div className="px-4 py-5 sm:p-6">
                  <h3 className="text-lg font-medium text-gray-900">Generated Messages</h3>
                  <div className="mt-4 space-y-4">
                    <div>
                      <h4 className="text-sm font-medium text-gray-500">LinkedIn Message</h4>
                      <p className="mt-1 text-sm text-gray-900">{messages.linkedin_message}</p>
                    </div>
                    <div>
                      <h4 className="text-sm font-medium text-gray-500">Email Content</h4>
                      <p className="mt-1 text-sm text-gray-900 whitespace-pre-wrap">{messages.email}</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
