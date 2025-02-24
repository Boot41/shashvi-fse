import logging
import tempfile
from django.test import TestCase, override_settings
from django.contrib.auth import get_user_model
from ai_lead_generation.api.models import Lead, Outreach
from ai_lead_generation.api.services import LeadAutomationService
import os

User = get_user_model()

class LoggingTest(TestCase):
    def setUp(self):
        # Create a temporary log file
        self.log_file = tempfile.NamedTemporaryFile(delete=False)
        self.addCleanup(self.cleanup_log_file)
        
        # Configure logging to use the temporary file
        self.logger = logging.getLogger('ai_lead_generation')
        self.handler = logging.FileHandler(self.log_file.name)
        self.logger.addHandler(self.handler)
        self.logger.setLevel(logging.DEBUG)
        
        # Create test user and lead
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        self.lead = Lead.objects.create(
            name='John Doe',
            email='john@example.com',
            company='Test Company',
            position='CEO',
            industry='tech',
            created_by=self.user
        )
        
        self.service = LeadAutomationService()

    def cleanup_log_file(self):
        """Clean up the temporary log file"""
        self.handler.close()
        self.logger.removeHandler(self.handler)
        os.unlink(self.log_file.name)

    def get_log_contents(self):
        """Read and return the contents of the log file"""
        with open(self.log_file.name, 'r') as f:
            return f.read()

    def test_lead_processing_logging(self):
        """Test that lead processing events are properly logged"""
        self.logger.info(f"Processing lead: {self.lead.id}")
        self.service.process_all_leads()
        log_contents = self.get_log_contents()
        
        # Check for expected log messages
        self.assertIn(f"Processing lead: {self.lead.id}", log_contents)
        self.assertIn("process_all_leads", log_contents)

    def test_error_logging(self):
        """Test that errors are properly logged"""
        # Create a lead with invalid data to trigger an error
        invalid_lead = Lead.objects.create(
            name='Invalid Lead',
            email='invalid',  # Invalid email format
            company='Test Company',
            created_by=self.user
        )
        
        self.logger.error(f"Error processing lead {invalid_lead.id}: Invalid email format")
        log_contents = self.get_log_contents()
        
        # Check for error log messages
        self.assertIn(f"Error processing lead {invalid_lead.id}", log_contents)
        self.assertIn("Invalid email format", log_contents)

    def test_outreach_generation_logging(self):
        """Test logging of outreach message generation"""
        # Generate messages for a lead
        self.logger.info(f"Generating messages for lead: {self.lead.id}")
        Outreach.objects.create(
            lead=self.lead,
            email_content="Test email",
            linkedin_content="Test LinkedIn message"
        )
        
        log_contents = self.get_log_contents()
        
        # Check for message generation logs
        self.assertIn(f"Generating messages for lead: {self.lead.id}", log_contents)

    def test_authentication_logging(self):
        """Test logging of authentication events"""
        # Test login
        self.logger.info("User logged in successfully: testuser")
        self.client.login(username='testuser', password='testpass123')
        log_contents = self.get_log_contents()
        
        # Check for authentication logs
        self.assertIn("User logged in successfully", log_contents)
        self.assertIn("testuser", log_contents)

    def test_critical_error_logging(self):
        """Test logging of critical errors"""
        try:
            # Simulate a critical error
            raise Exception("Critical test error")
        except Exception as e:
            self.logger.critical(f"Critical error occurred: {str(e)}")
        
        log_contents = self.get_log_contents()
        
        # Check for critical error logs
        self.assertIn("Critical error occurred", log_contents)
        self.assertIn("Critical test error", log_contents)
