import { Users, Send, MessageSquare, ThumbsUp } from 'lucide-react';
import { StatsCard } from '@/components/stats-card';
import type { Stats } from '@/types';

interface StatsOverviewProps {
  stats: Stats;
}

export function StatsOverview({ stats }: StatsOverviewProps) {
  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
      <StatsCard
        title="Total Leads"
        value={stats.totalLeads}
        icon={<Users className="h-4 w-4" />}
        trend={{ value: 12, isPositive: true }}
        description="Total leads in your pipeline"
      />
      <StatsCard
        title="Emails Sent"
        value={stats.emailsSent}
        icon={<Send className="h-4 w-4" />}
        trend={{ value: 8, isPositive: true }}
        description="Outreach emails sent this month"
      />
      <StatsCard
        title="Responses Received"
        value={stats.responsesReceived}
        icon={<MessageSquare className="h-4 w-4" />}
        trend={{ value: 5, isPositive: true }}
        description="Responses from leads this month"
      />
      <StatsCard
        title="Positive Replies"
        value={stats.positiveReplies}
        icon={<ThumbsUp className="h-4 w-4" />}
        trend={{ value: 15, isPositive: true }}
        description="Positive responses this month"
      />
    </div>
  );
}