export interface Lead {
  id: string;
  companyName: string;
  industry: string;
  fundingAmount: number;
  leadScore: number;
  outreachStatus: 'pending' | 'sent' | 'opened' | 'replied' | 'no_response';
  decisionMaker: {
    name: string;
    email: string;
    jobTitle: string;
  };
  linkedInProfile?: string;
  createdAt: string;
  lastInteraction?: string;
}

export interface EmailTemplate {
  id: string;
  subject: string;
  body: string;
  type: 'initial' | 'follow_up' | 'closing';
  createdAt: string;
}

export interface User {
  id: string;
  name: string;
  email: string;
  role: 'admin' | 'user';
  avatar?: string;
  preferences: {
    emailNotifications: boolean;
    emailDigestFrequency: 'daily' | 'weekly' | 'never';
    darkMode: boolean;
  };
}

export interface Interaction {
  id: string;
  leadId: string;
  type: 'email_sent' | 'email_opened' | 'email_replied' | 'note_added';
  content: string;
  createdAt: string;
}

export interface LeadScore {
  total: number;
  factors: {
    fundingAmount: number;
    companySize: number;
    industryFit: number;
    engagement: number;
  };
}

export interface Stats {
  totalLeads: number;
  emailsSent: number;
  responsesReceived: number;
  positiveReplies: number;
  conversionRate: number;
}