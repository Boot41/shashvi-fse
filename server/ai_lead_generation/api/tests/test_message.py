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
            created_by=self.user
        )
        
        self.generator = MessageGenerator()

    def test_email_content_generation(self):
        """Test email content generation"""
        content = self.generator.generate_email_content(self.lead)
        self.assertIsInstance(content, str)
        self.assertIn(self.lead.name, content)
        self.assertIn(self.lead.company, content)
        self.assertIn(self.lead.position, content)

    def test_linkedin_message_generation(self):
        """Test LinkedIn message generation"""
        message = self.generator.generate_linkedin_message(self.lead)
        self.assertIsInstance(message, str)
        self.assertIn(self.lead.name, message)
        self.assertIn(self.lead.company, message)
        self.assertLessEqual(len(message), 280)  # LinkedIn character limit

    def test_custom_message_generation(self):
        """Test custom message generation"""
        template = "Hi {name}, I noticed you work at {company} as {position}."
        message = self.generator.generate_custom_message(self.lead, template)
        self.assertIn(self.lead.name, message)
        self.assertIn(self.lead.company, message)
        self.assertIn(self.lead.position, message)

    def test_missing_data_handling(self):
        """Test handling of missing lead data"""
        lead = Lead.objects.create(
            name='Minimal Lead',
            email='minimal@example.com',
            company='',  # Empty company
            created_by=self.user
        )
        
        # Test email content
        content = self.generator.generate_email_content(lead)
        self.assertIsInstance(content, str)
        self.assertIn(lead.name, content)
        
        # Test LinkedIn message
        message = self.generator.generate_linkedin_message(lead)
        self.assertIsInstance(message, str)
        self.assertIn(lead.name, message)
        
        # Test custom message
        template = "Hi {name}, how's {company}?"
        message = self.generator.generate_custom_message(lead, template)
        self.assertIn(lead.name, message)

    def test_html_escaping(self):
        """Test HTML escaping in messages"""
        lead = Lead.objects.create(
            name='<script>alert("XSS")</script>',
            email='test@example.com',
            company='<b>Company</b>',
            position='<i>CEO</i>',
            created_by=self.user
        )
        
        # Test email content
        content = self.generator.generate_email_content(lead)
        self.assertNotIn('<script>', content)
        self.assertNotIn('<b>', content)
        
        # Test LinkedIn message
        message = self.generator.generate_linkedin_message(lead)
        self.assertNotIn('<script>', message)
        self.assertNotIn('<b>', message)
        
        # Test custom message
        template = "Hi {name}, welcome to {company}!"
        message = self.generator.generate_custom_message(lead, template)
        self.assertNotIn('<script>', message)
        self.assertNotIn('<b>', message)
