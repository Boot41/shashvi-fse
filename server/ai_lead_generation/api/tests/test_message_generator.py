from django.test import TestCase
from django.contrib.auth import get_user_model
from ..models import Lead
from ..message_generator import MessageGenerator

User = get_user_model()

class MessageGeneratorTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.lead = Lead.objects.create(
            name='John Doe',
            email='john@example.com',
            company='Test Company',
            position='CEO',
            industry='Technology',
            company_size=100,
            funding_amount=1000000,
            created_by=self.user
        )
        
        self.generator = MessageGenerator()
    
    def test_generate_email_content(self):
        """Test email content generation"""
        email_content = self.generator.generate_email_content(self.lead)
        self.assertIsInstance(email_content, str)
        self.assertGreater(len(email_content), 0)
        self.assertIn(self.lead.name, email_content)
        self.assertIn(self.lead.company, email_content)
    
    def test_generate_linkedin_message(self):
        """Test LinkedIn message generation"""
        linkedin_message = self.generator.generate_linkedin_message(self.lead)
        self.assertIsInstance(linkedin_message, str)
        self.assertGreater(len(linkedin_message), 0)
        self.assertLess(len(linkedin_message), 300)  # LinkedIn character limit
        self.assertIn(self.lead.name, linkedin_message)
        
    def test_generate_custom_message(self):
        """Test custom message generation with template"""
        template = "Hi {name}, I noticed {company} is growing fast!"
        message = self.generator.generate_custom_message(self.lead, template)
        self.assertIn(self.lead.name, message)
        self.assertIn(self.lead.company, message)
