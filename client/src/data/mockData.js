export const mockLeads = [
  {
    id: 1,
    companyName: "TechCorp Solutions",
    contactName: "John Smith",
    position: "CEO",
    industry: "Technology",
    fundingAmount: "$5M",
    leadScore: 85,
    email: "john@techcorp.com",
    status: "New"
  },
  {
    id: 2,
    companyName: "HealthPlus Inc",
    contactName: "Sarah Johnson",
    position: "CTO",
    industry: "Healthcare",
    fundingAmount: "$10M",
    leadScore: 92,
    email: "sarah@healthplus.com",
    status: "Contacted"
  },
  {
    id: 3,
    companyName: "FinTech Innovations",
    contactName: "Michael Brown",
    position: "COO",
    industry: "Finance",
    fundingAmount: "$3M",
    leadScore: 78,
    email: "michael@fintech.com",
    status: "New"
  },
  {
    id: 4,
    companyName: "Green Energy Co",
    contactName: "Emma Wilson",
    position: "Director",
    industry: "Energy",
    fundingAmount: "$7M",
    leadScore: 88,
    email: "emma@greenenergy.com",
    status: "New"
  },
  {
    id: 5,
    companyName: "Retail Solutions",
    contactName: "David Lee",
    position: "VP Sales",
    industry: "Retail",
    fundingAmount: "$2M",
    leadScore: 72,
    email: "david@retail.com",
    status: "Contacted"
  }
];

export const generateMockMessages = (lead) => ({
  email: `Hi ${lead.contactName},

I noticed that ${lead.companyName} recently raised ${lead.fundingAmount} in funding. Congratulations! 

I work with companies in the ${lead.industry} space to help them scale their operations efficiently. Given your role as ${lead.position}, I thought you might be interested in learning how we've helped similar companies achieve 30% growth in their first year.

Would you be open to a 15-minute call this week to discuss how we could help ${lead.companyName}?

Best regards,
[Your name]`,
  linkedin: `Hi ${lead.contactName}! Congratulations on the recent ${lead.fundingAmount} funding round at ${lead.companyName}. I help ${lead.industry} companies scale efficiently - would love to connect and share some insights!`
});
