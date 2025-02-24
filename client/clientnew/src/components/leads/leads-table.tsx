import { useState } from 'react';
import { ArrowUpDown, Eye, Mail, Linkedin } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { formatCurrency } from '@/lib/utils';
import type { Lead } from '@/types';

interface LeadsTableProps {
  leads: Lead[];
}

type SortField = 'companyName' | 'industry' | 'fundingAmount' | 'leadScore';
type SortOrder = 'asc' | 'desc';

const getLeadScoreBadge = (score: number) => {
  if (score >= 80) return <Badge variant="success">High</Badge>;
  if (score >= 50) return <Badge variant="warning">Medium</Badge>;
  return <Badge variant="danger">Low</Badge>;
};

const getStatusBadge = (status: Lead['outreachStatus']) => {
  const variants: Record<Lead['outreachStatus'], BadgeProps['variant']> = {
    pending: 'default',
    sent: 'warning',
    opened: 'warning',
    replied: 'success',
    no_response: 'danger',
  };

  const labels: Record<Lead['outreachStatus'], string> = {
    pending: 'Pending',
    sent: 'Sent',
    opened: 'Opened',
    replied: 'Replied',
    no_response: 'No Response',
  };

  return <Badge variant={variants[status]}>{labels[status]}</Badge>;
};

export function LeadsTable({ leads }: LeadsTableProps) {
  const [sortField, setSortField] = useState<SortField>('companyName');
  const [sortOrder, setSortOrder] = useState<SortOrder>('asc');
  const [searchTerm, setSearchTerm] = useState('');
  const [industryFilter, setIndustryFilter] = useState<string>('all');

  const handleSort = (field: SortField) => {
    if (field === sortField) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortOrder('asc');
    }
  };

  const sortedAndFilteredLeads = leads
    .filter((lead) => {
      const matchesSearch = lead.companyName
        .toLowerCase()
        .includes(searchTerm.toLowerCase());
      const matchesIndustry =
        industryFilter === 'all' || lead.industry === industryFilter;
      return matchesSearch && matchesIndustry;
    })
    .sort((a, b) => {
      const order = sortOrder === 'asc' ? 1 : -1;
      if (sortField === 'fundingAmount') {
        return (a[sortField] - b[sortField]) * order;
      }
      if (sortField === 'leadScore') {
        return (a[sortField] - b[sortField]) * order;
      }
      return a[sortField].localeCompare(b[sortField]) * order;
    });

  const industries = Array.from(new Set(leads.map((lead) => lead.industry)));

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <input
            type="text"
            placeholder="Search companies..."
            className="rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
          <select
            className="rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
            value={industryFilter}
            onChange={(e) => setIndustryFilter(e.target.value)}
          >
            <option value="all">All Industries</option>
            {industries.map((industry) => (
              <option key={industry} value={industry}>
                {industry}
              </option>
            ))}
          </select>
        </div>
      </div>

      <div className="rounded-md border">
        <table className="w-full text-sm">
          <thead className="border-b bg-muted/50">
            <tr>
              <th
                className="cursor-pointer px-4 py-3 text-left"
                onClick={() => handleSort('companyName')}
              >
                <div className="flex items-center space-x-1">
                  <span>Company</span>
                  <ArrowUpDown className="h-4 w-4" />
                </div>
              </th>
              <th className="px-4 py-3 text-left">Industry</th>
              <th
                className="cursor-pointer px-4 py-3 text-left"
                onClick={() => handleSort('fundingAmount')}
              >
                <div className="flex items-center space-x-1">
                  <span>Funding</span>
                  <ArrowUpDown className="h-4 w-4" />
                </div>
              </th>
              <th
                className="cursor-pointer px-4 py-3 text-left"
                onClick={() => handleSort('leadScore')}
              >
                <div className="flex items-center space-x-1">
                  <span>Lead Score</span>
                  <ArrowUpDown className="h-4 w-4" />
                </div>
              </th>
              <th className="px-4 py-3 text-left">Status</th>
              <th className="px-4 py-3 text-left">Actions</th>
            </tr>
          </thead>
          <tbody>
            {sortedAndFilteredLeads.map((lead) => (
              <tr
                key={lead.id}
                className="border-b transition-colors hover:bg-muted/50"
              >
                <td className="px-4 py-3">{lead.companyName}</td>
                <td className="px-4 py-3">{lead.industry}</td>
                <td className="px-4 py-3">
                  {formatCurrency(lead.fundingAmount)}
                </td>
                <td className="px-4 py-3">
                  {getLeadScoreBadge(lead.leadScore)}
                </td>
                <td className="px-4 py-3">
                  {getStatusBadge(lead.outreachStatus)}
                </td>
                <td className="px-4 py-3">
                  <div className="flex items-center space-x-2">
                    <Button variant="ghost" size="sm">
                      <Eye className="h-4 w-4" />
                    </Button>
                    <Button variant="ghost" size="sm">
                      <Mail className="h-4 w-4" />
                    </Button>
                    <Button variant="ghost" size="sm">
                      <Linkedin className="h-4 w-4" />
                    </Button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}