import logging

logger = logging.getLogger(__name__)

class MessageGenerator:
    def generate_email_content(self, lead):
        """Generate personalized email content for a lead"""
        try:
            template = f"""
Dear {lead.name},

I noticed that {lead.company} has been making waves in the {lead.industry} industry. 
Your role as {lead.position} must keep you busy with all the exciting developments.

I would love to connect and discuss how we can help {lead.company} achieve even greater success.

Best regards,
AI Lead Generation Team
            """
            return template.strip()
        except Exception as e:
            logger.error(f"Error generating email content: {str(e)}")
            return ""

    def generate_linkedin_message(self, lead):
        """Generate a LinkedIn message for a lead (max 300 chars)"""
        try:
            template = f"""Hi {lead.name}, I noticed your great work at {lead.company}! Would love to connect and discuss how we can help with your {lead.industry} initiatives."""
            return template[:300]  # LinkedIn message limit
        except Exception as e:
            logger.error(f"Error generating LinkedIn message: {str(e)}")
            return ""

    def generate_custom_message(self, lead, template):
        """Generate a message using a custom template"""
        try:
            return template.format(
                name=lead.name,
                company=lead.company,
                position=lead.position,
                industry=lead.industry
            )
        except Exception as e:
            logger.error(f"Error generating custom message: {str(e)}")
            return ""

def generate_messages(lead):
    """
    Generate personalized LinkedIn and email messages for a lead
    """
    message_generator = MessageGenerator()

    # LinkedIn message template
    linkedin_template = message_generator.generate_linkedin_message(lead)

    # Email template
    email_template = message_generator.generate_email_content(lead)

    return {
        'linkedin_message': linkedin_template,
        'email': email_template
    }
