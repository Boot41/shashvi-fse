import pandas as pd
from datetime import datetime
from django.conf import settings
from .models import Lead
from typing import List, Dict
import logging
import random

logger = logging.getLogger(__name__)

class LeadAutomationService:
    def __init__(self):
        # LinkedIn message templates
        self.linkedin_templates = [
            "Hi {name}, I noticed your work at {company} in the {industry} space. Would love to connect and explore potential synergies!",
            "Hello {name}! Your role as {position} at {company} caught my attention. Let's connect and share industry insights.",
            "Hi {name}, impressed by {company}'s impact in {industry}. Would be great to connect and learn from your experience!",
            "Hello {name}, your work at {company} is inspiring! Would love to connect and discuss {industry} innovations.",
        ]
        
        # Email templates
        self.email_templates = [
            """Hi {name},

I came across {company}'s impressive work in the {industry} sector. Your role as {position} particularly caught my attention.

I'd love to schedule a quick call to discuss how we might collaborate. Would you have 15 minutes this week?

Best regards,
[Your name]""",
            """Hello {name},

I've been following {company}'s innovations in {industry}, and I'm impressed by your approach.

I'd love to learn more about your experience as {position} and share some ideas that might be valuable.

Would you be open to a brief conversation?

Best regards,
[Your name]""",
            """Dear {name},

Your work as {position} at {company} aligns perfectly with some {industry} initiatives we're working on.

I'd love to share some specific ideas that could benefit both our organizations.

Would you be interested in a brief discussion?

Best regards,
[Your name]"""
        ]

    def generate_linkedin_message(self, lead: Lead) -> str:
        """
        Generate personalized LinkedIn connection request using templates
        """
        try:
            template = random.choice(self.linkedin_templates)
            message = template.format(
                name=lead.name,
                company=lead.company,
                position=lead.position or "your role",
                industry=lead.industry or "your industry"
            )
            return message[:300]  # LinkedIn's character limit
            
        except Exception as e:
            logger.error(f"Error generating LinkedIn message: {str(e)}")
            return ""

    def generate_email_content(self, lead: Lead) -> str:
        """
        Generate personalized email content
        Returns the email body as a string
        """
        try:
            template = random.choice(self.email_templates)
            email_content = template.format(
                name=lead.name,
                company=lead.company,
                position=lead.position or "your role",
                industry=lead.industry or "your industry"
            )
            return email_content
            
        except Exception as e:
            logger.error(f"Error generating email content: {str(e)}")
            return ""

    def import_leads_from_csv(self, file_path: str, user) -> Dict:
        """
        Import leads from a CSV file
        Returns stats about the import process
        """
        try:
            df = pd.read_csv(file_path)
            total_imported = 0
            errors = 0
            
            for _, row in df.iterrows():
                try:
                    Lead.objects.create(
                        name=row['name'],
                        email=row['email'],
                        company=row['company'],
                        position=row['position'],
                        industry=row.get('industry', 'other'),
                        created_by=user
                    )
                    total_imported += 1
                except Exception as e:
                    logger.error(f"Error importing lead: {str(e)}")
                    errors += 1
            
            return {
                'total_imported': total_imported,
                'errors': errors
            }
            
        except Exception as e:
            logger.error(f"Error reading CSV file: {str(e)}")
            return {
                'total_imported': 0,
                'errors': 1
            }

    def process_all_leads(self) -> Dict:
        """
        Process all leads that haven't been contacted
        Returns stats about the processing
        """
        try:
            leads = Lead.objects.filter(
                linkedin_connection_sent=False,
                email_sent=False
            )
            
            total_processed = 0
            successful = 0
            failed = 0
            
            for lead in leads:
                try:
                    # Calculate lead score
                    lead.calculate_lead_score()
                    
                    # Update contact date
                    lead.last_contact_date = datetime.now()
                    lead.save()
                    
                    successful += 1
                except Exception as e:
                    logger.error(f"Error processing lead {lead.id}: {str(e)}")
                    failed += 1
                
                total_processed += 1
            
            return {
                'total_processed': total_processed,
                'successful': successful,
                'failed': failed
            }
            
        except Exception as e:
            logger.error(f"Error in process_all_leads: {str(e)}")
            return {
                'total_processed': 0,
                'successful': 0,
                'failed': 1
            }
