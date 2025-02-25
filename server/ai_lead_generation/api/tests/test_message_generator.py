from django.test import TestCase
from ..models import Lead
from ..message_generator import MessageGenerator
from django.contrib.auth import get_user_model

User = get_user_model()

class MessageGeneratorTest(TestCase):
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
        content = self.generator.generate_email_content(self.lead)
        
        # Check required elements
        self.assertIsInstance(content, str)
        self.assertIn(self.lead.name, content)
        self.assertIn(self.lead.company, content)
        self.assertGreater(len(content), 50)
        
        # Test with missing data
        lead_no_company = Lead.objects.create(
            name='Jane Doe',
            email='jane@example.com',
            created_by=self.user
        )
        content = self.generator.generate_email_content(lead_no_company)
        self.assertIsInstance(content, str)
        self.assertIn(lead_no_company.name, content)

    def test_generate_linkedin_message(self):
        """Test LinkedIn message generation"""
        message = self.generator.generate_linkedin_message(self.lead)
        
        # Check message properties
        self.assertIsInstance(message, str)
        self.assertIn(self.lead.name, message)
        self.assertLess(len(message), 300)  # LinkedIn character limit
        
        # Test with minimal lead data
        minimal_lead = Lead.objects.create(
            name='Minimal Lead',
            email='minimal@example.com',
            created_by=self.user
        )
        message = self.generator.generate_linkedin_message(minimal_lead)
        self.assertIsInstance(message, str)
        self.assertIn(minimal_lead.name, message)

    def test_generate_custom_message(self):
        """Test custom message generation"""
        template = "Hi {name}, I noticed you work at {company}."
        message = self.generator.generate_custom_message(self.lead, template)
        
        # Check template substitution
        self.assertIn(self.lead.name, message)
        self.assertIn(self.lead.company, message)
        
        # Test with missing template variables
        template = "Hi {name}, how about {nonexistent}?"
        message = self.generator.generate_custom_message(self.lead, template)
        self.assertIn(self.lead.name, message)
        self.assertIn("{nonexistent}", message)

    def test_message_length_limits(self):
        """Test message length limits"""
        # Create lead with very long values
        long_lead = Lead.objects.create(
            name='A' * 100,
            email='long@example.com',
            company='B' * 100,
            position='C' * 100,
            industry='D' * 100,
            created_by=self.user
        )
        
        # Test email content length
        email = self.generator.generate_email_content(long_lead)
        self.assertLess(len(email), 2000)
        
        # Test LinkedIn message length
        linkedin = self.generator.generate_linkedin_message(long_lead)
        self.assertLess(len(linkedin), 300)

    def test_message_sanitization(self):
        """Test message content sanitization"""
        # Create lead with potentially problematic values
        special_lead = Lead.objects.create(
            name='Test<script>alert("xss")</script>',
            email='test@example.com',
            company='Company & Co.',
            position='CEO & Founder',
            created_by=self.user
        )
        
        email = self.generator.generate_email_content(special_lead)
        linkedin = self.generator.generate_linkedin_message(special_lead)
        
        # Check that HTML is escaped
        self.assertNotIn('<script>', email)
        self.assertNotIn('<script>', linkedin)
        
        # Check that legitimate characters are preserved
        self.assertIn('&', email)
        self.assertIn('&', linkedin)
