import { useState } from 'react';
import { StatsOverview } from '@/components/dashboard/stats-overview';
import { LeadsTable } from '@/components/leads/leads-table';

// Temporary mock data
const mockStats = {
  totalLeads: 1234,
  emailsSent: 856,
  responsesReceived: 342,
  positiveReplies: 156,
  conversionRate: 18.2,
};

const mockLeads = [
  {
    id: '1',
    companyName: 'TechCorp Inc.',
    industry: 'Software',
    fundingAmount: 5000000,
    leadScore: 85,
    outreachStatus: 'pending',
    decisionMaker: {
      name: 'John Smith',
      email: 'john@techcorp.com',
      jobTitle: 'CTO',
    },
    createdAt: '2024-03-15T10:00:00Z',
  },
  {
    id: '2',
    companyName: 'HealthTech Solutions',
    industry: 'Healthcare',
    fundingAmount: 10000000,
    leadScore: 92,
    outreachStatus: 'sent',
    decisionMaker: {
      name: 'Sarah Johnson',
      email: 'sarah@healthtech.com',
      jobTitle: 'CEO',
    },
    createdAt: '2024-03-14T15:30:00Z',
  },
  {
    id: '3',
    companyName: 'EcoEnergy',
    industry: 'Renewable Energy',
    fundingAmount: 3000000,
    leadScore: 75,
    outreachStatus: 'replied',
    decisionMaker: {
      name: 'Mike Brown',
      email: 'mike@ecoenergy.com',
      jobTitle: 'COO',
    },
    createdAt: '2024-03-13T09:15:00Z',
  },
  {
    id: '4',
    companyName: 'FinServe',
    industry: 'Fintech',
    fundingAmount: 8000000,
    leadScore: 88,
    outreachStatus: 'opened',
    decisionMaker: {
      name: 'Lisa Chen',
      email: 'lisa@finserve.com',
      jobTitle: 'CFO',
    },
    createdAt: '2024-03-12T14:45:00Z',
  },
  {
    id: '5',
    companyName: 'RetailTech',
    industry: 'Retail',
    fundingAmount: 2000000,
    leadScore: 65,
    outreachStatus: 'no_response',
    decisionMaker: {
      name: 'David Wilson',
      email: 'david@retailtech.com',
      jobTitle: 'CTO',
    },
    createdAt: '2024-03-11T11:20:00Z',
  },
];

export function DashboardPage() {
  const [stats] = useState(mockStats);
  const [leads] = useState(mockLeads);

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold tracking-tight text-gray-900 dark:text-white">
          Welcome back, John!
        </h1>
        <p className="mt-2 text-lg text-gray-600 dark:text-gray-400">
          Here's what's happening with your leads today.
        </p>
      </div>

      <StatsOverview stats={stats} />
      
      <div>
        <h2 className="text-2xl font-semibold tracking-tight text-gray-900 dark:text-white">
          Recent Leads
        </h2>
        <div className="mt-4">
          <LeadsTable leads={leads} />
        </div>
      </div>
    </div>
  );
}