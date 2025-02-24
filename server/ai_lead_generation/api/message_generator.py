def generate_messages(lead):
    """
    Generate personalized LinkedIn and email messages for a lead
    """
    # LinkedIn message template
    linkedin_template = f"""Hi {lead.name},

I noticed your work at {lead.company} in the {lead.industry} industry. Given your role as {lead.position}, I thought you might be interested in our AI-powered lead generation solution that's helping companies like yours streamline their sales process.

Would you be open to a quick chat about how we could help {lead.company} achieve better sales results?

Best regards"""

    # Email template
    email_template = f"""Dear {lead.name},

I hope this email finds you well. I recently came across {lead.company}'s impressive work in the {lead.industry} space, and I wanted to reach out.

As {lead.position} at {lead.company}, I'm sure you're always looking for ways to optimize your sales process and generate high-quality leads. Our AI-powered lead generation platform has been helping companies:

1. Identify and score potential leads automatically
2. Generate personalized outreach messages
3. Track and analyze lead engagement

Given {lead.company}'s growth and position in the market, I believe we could help you achieve even better results.

Would you be interested in a 15-minute call to discuss how we could specifically help {lead.company}?

Looking forward to your response.

Best regards"""

    return {
        'linkedin_message': linkedin_template,
        'email': email_template
    }
