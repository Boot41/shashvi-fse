from django.test import TestCase
from django.contrib.auth import get_user_model
from api.models import Lead
from api.services import LeadAutomationService
import tempfile
import csv
import os

User = get_user_model()

class LeadAutomationServiceTest(TestCase):
    def setUp(self):
        self.service = LeadAutomationService()
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
            company_size=100,
            funding_amount=1000000.00,
            hiring_status=True,
            created_by=self.user
        )

    def test_generate_linkedin_message(self):
        """Test LinkedIn message generation"""
        message = self.service.generate_linkedin_message(self.lead)
        self.assertIsInstance(message, str)
        self.assertGreater(len(message), 0)
        self.assertLess(len(message), 300)  # LinkedIn character limit
        
        # Check if message contains lead information
        self.assertIn(self.lead.name, message)
        self.assertIn(self.lead.company, message)

    def test_generate_email_content(self):
        """Test email content generation"""
        email = self.service.generate_email_content(self.lead)
        self.assertIsInstance(email, str)
        self.assertGreater(len(email), 0)
        
        # Check if email contains lead information
        self.assertIn(self.lead.name, email)
        self.assertIn(self.lead.company, email)

    def test_import_leads_from_csv(self):
        """Test importing leads from CSV file"""
        # Create a temporary CSV file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.csv') as f:
            writer = csv.writer(f)
            writer.writerow(['name', 'email', 'company', 'position', 'industry'])
            writer.writerow(['Jane Doe', 'jane@example.com', 'Tech Corp', 'CTO', 'tech'])
            writer.writerow(['Bob Smith', 'bob@example.com', 'Finance Inc', 'CFO', 'finance'])
            csv_path = f.name

        try:
            # Import leads from the CSV
            result = self.service.import_leads_from_csv(csv_path, self.user)
            
            # Check if leads were imported
            self.assertEqual(Lead.objects.count(), 3)  # Including the one from setUp
            self.assertIn('total_imported', result)
            self.assertEqual(result['total_imported'], 2)
            
            # Check if the imported leads have correct data
            self.assertTrue(Lead.objects.filter(name='Jane Doe').exists())
            self.assertTrue(Lead.objects.filter(name='Bob Smith').exists())
            
        finally:
            # Clean up
            os.unlink(csv_path)

    def test_process_all_leads(self):
        """Test processing all leads"""
        result = self.service.process_all_leads()
        
        # Check if processing was successful
        self.assertIn('total_processed', result)
        self.assertIn('successful', result)
        self.assertIn('failed', result)
        
        # Check if lead was processed
        processed_lead = Lead.objects.get(id=self.lead.id)
        self.assertNotEqual(processed_lead.lead_score, 0)  # Score should be calculated
        self.assertIsNotNone(processed_lead.last_contact_date)
