import logging
from django.utils import timezone
from .models import Lead
from .scoring import LeadScorer
from .message_generator import MessageGenerator, generate_messages
import csv
import io
import random

logger = logging.getLogger(__name__)

class LeadAutomationService:
    def __init__(self):
        self.email_templates = [
            "Hi {name},\n\nI came across {company}'s impressive work in the {industry} sector. Your role as {position} particularly caught my attention.\n\nI'd love to schedule a quick call to discuss how we might collaborate. Would you have 15 minutes this week?\n\nBest regards,\n[Your name]",
            "Dear {name},\n\nI noticed {company}'s recent achievements in {industry}. As {position}, I believe you might be interested in exploring potential synergies between our organizations.\n\nWould you be open to a brief discussion?\n\nBest,\n[Your name]"
        ]
        self.linkedin_templates = [
            "Hi {name}, I noticed your great work at {company} and would love to connect!",
            "Hello {name}! I'm impressed by your role as {position} at {company}. Let's connect!",
            "Hi {name}, I saw that you're in the {industry} industry at {company}. Would love to chat!",
            "Hey {name}! Your experience at {company} caught my attention. Let's connect!",
            "Hi {name}, I'm reaching out because your work in {industry} at {company} is impressive!"
        ]

    def generate_email_content(self, lead):
        """Generate personalized email content for a lead"""
        try:
            template = self.email_templates[0]  # Use first template for now
            return template.format(
                name=lead.name or "Unknown",
                company=lead.company or "Unknown Company",
                position=lead.position or "Unknown Position",
                industry=lead.industry or "your industry"
            )
        except Exception as e:
            logger.error(f"Error generating email content for lead {lead.id}: {str(e)}")
            return ""

    def generate_linkedin_message(self, lead):
        """Generate a LinkedIn message for a lead"""
        templates = [
            "Hi {name}, I noticed your great work at {company} and would love to connect!",
            "Hello {name}! I'm impressed by your role as {position} at {company}. Let's connect!",
            "Hi {name}, I saw that you're in the {industry} industry at {company}. Would love to chat!",
            "Hey {name}! Your experience at {company} caught my attention. Let's connect!",
            "Hi {name}, I'm reaching out because your work in {industry} at {company} is impressive!"
        ]
        
        # Randomly select a template
        template = random.choice(templates)
        
        # Format the template with lead data
        try:
            message = template.format(
                name=lead.name,
                company=lead.company,
                position=lead.position or 'professional',
                industry=lead.industry or 'your industry'
            )
            return message
        except Exception as e:
            logger.error(f"Error generating LinkedIn message for lead {lead.id}: {str(e)}")
            raise

    def import_leads_from_csv(self, csv_data, user):
        """Import leads from CSV data"""
        imported_count = 0
        error_count = 0

        try:
            for row in csv_data:
                try:
                    lead = Lead.objects.create(
                        name=row.get('name', ''),
                        email=row.get('email', ''),
                        company=row.get('company', ''),
                        position=row.get('position', ''),
                        industry=row.get('industry', ''),
                        company_size=row.get('company_size', 0),
                        funding_amount=row.get('funding_amount', 0.0),
                        created_by=user
                    )
                    imported_count += 1
                except Exception as e:
                    logger.error(f"Error importing lead: {str(e)}")
                    error_count += 1

            return {
                'imported_count': imported_count,
                'error_count': error_count
            }
        except Exception as e:
            logger.error(f"Error reading CSV file: {str(e)}")
            raise

    def score_lead(self, lead):
        """Calculate lead score using LeadScorer"""
        scorer = LeadScorer()
        return scorer.calculate_total_score(lead)

    def process_all_leads(self, filters=None):
        """Process all leads with optional filters"""
        try:
            leads = Lead.objects.all()
            
            if filters:
                # Validate filters
                valid_filters = {'status', 'industry', 'company_size', 'funding_amount'}
                invalid_filters = set(filters.keys()) - valid_filters
                if invalid_filters:
                    raise ValueError(f"Invalid filters: {', '.join(invalid_filters)}")
                
                leads = leads.filter(**filters)
            
            results = []
            for lead in leads:
                lead_data = {
                    'id': lead.id,
                    'name': lead.name,
                    'company': lead.company,
                    'industry': lead.industry,
                    'status': lead.status,
                    'score': self.score_lead(lead)
                }
                results.append(lead_data)
            
            return {
                'total_processed': len(results),
                'processed': results
            }
            
        except Exception as e:
            logger.error(f"Error in process_all_leads: {str(e)}")
            raise
