from django.test import TestCase
from django.contrib.auth import get_user_model
from ai_lead_generation.api.models import Lead
from ai_lead_generation.api.services import LeadAutomationService
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
        # Create CSV data
        csv_data = [
            {
                'name': 'Jane Doe',
                'email': 'jane@example.com',
                'company': 'Tech Corp',
                'position': 'CTO',
                'industry': 'tech'
            },
            {
                'name': 'Bob Smith',
                'email': 'bob@example.com',
                'company': 'Finance Inc',
                'position': 'CFO',
                'industry': 'finance'
            }
        ]
        
        # Import leads from the CSV data
        result = self.service.import_leads_from_csv(csv_data, self.user)
        
        # Check if leads were imported
        self.assertEqual(Lead.objects.count(), 3)  # Including the one from setUp
        self.assertIn('imported_count', result)
        self.assertEqual(result['imported_count'], 2)
        self.assertIn('error_count', result)
        self.assertEqual(result['error_count'], 0)
        
        # Check if the imported leads have correct data
        self.assertTrue(Lead.objects.filter(name='Jane Doe').exists())
        self.assertTrue(Lead.objects.filter(name='Bob Smith').exists())

    def test_import_leads_with_duplicate_data(self):
        """Test handling of duplicate leads during import"""
        # Create CSV data with a duplicate lead
        csv_data = [
            {
                'name': 'Jane Doe',
                'email': 'jane@example.com',
                'company': 'Tech Corp',
                'position': 'CTO',
                'industry': 'tech'
            },
            {
                'name': 'Jane Doe',  # Duplicate name
                'email': 'jane@example.com',  # Duplicate email
                'company': 'Tech Corp',
                'position': 'CTO',
                'industry': 'tech'
            }
        ]
        
        # Import leads
        result = self.service.import_leads_from_csv(csv_data, self.user)
        
        # Both leads should be imported (no uniqueness constraint)
        self.assertEqual(result['imported_count'], 2)
        self.assertEqual(result['error_count'], 0)
        self.assertEqual(
            Lead.objects.filter(name='Jane Doe', email='jane@example.com').count(),
            2
        )

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

    def test_process_lead_with_missing_data(self):
        """Test processing a lead with missing required data"""
        # Create a lead with minimal data
        minimal_lead = Lead.objects.create(
            name='Minimal Lead',
            created_by=self.user
        )
        
        result = self.service.process_all_leads()
        self.assertIn('total_processed', result)

    def test_generate_messages_with_special_characters(self):
        """Test message generation with special characters in lead data"""
        special_lead = Lead.objects.create(
            name="John O'Brien and Sons",
            email='john@example.com',
            company='Tech & More, Inc.',
            position='CEO & Founder',
            industry='tech',
            created_by=self.user
        )
        
        # Test LinkedIn message
        linkedin_msg = self.service.generate_linkedin_message(special_lead)
        self.assertIsInstance(linkedin_msg, str)
        self.assertIn('Tech & More', linkedin_msg)
        
        # Test email
        email = self.service.generate_email_content(special_lead)
        self.assertIsInstance(email, str)
        self.assertIn("O'Brien", email)

    def test_process_lead_with_large_numbers(self):
        """Test lead processing with very large numbers"""
        large_numbers_lead = Lead.objects.create(
            name='Big Corp',
            email='contact@bigcorp.com',
            company='Big Corporation',
            position='CEO',
            industry='tech',
            company_size=1000000,  # 1 million employees
            funding_amount=1000000000.00,  # $1 billion
            created_by=self.user
        )
        
        result = self.service.process_all_leads()
        self.assertIn('total_processed', result)
        self.assertGreater(large_numbers_lead.lead_score, 0)

    def test_message_generation_rate_limiting(self):
        """Test rate limiting in message generation"""
        messages = set()
        for _ in range(5):
            message = self.service.generate_linkedin_message(self.lead)
            messages.add(message)
        
        # We expect at least 2 different messages from the templates
        self.assertGreater(len(messages), 1, "Expected more than one unique message template to be used")

    def test_lead_scoring_edge_cases(self):
        """Test lead scoring with edge cases"""
        # Test with zero values
        zero_lead = Lead.objects.create(
            name='Zero Corp',
            email='zero@example.com',
            company='Zero Inc',
            position='CEO',
            industry='other',
            company_size=0,
            funding_amount=0.00,
            created_by=self.user
        )
        
        result = self.service.process_all_leads()
        self.assertIn('total_processed', result)
        self.assertIsNotNone(zero_lead.lead_score)
        
        # Test with maximum possible values
        max_lead = Lead.objects.create(
            name='Max Corp',
            email='max@example.com',
            company='Maximum Inc',
            position='CEO',
            industry='tech',
            company_size=999999,
            funding_amount=999999999.99,
            created_by=self.user
        )
        
        result = self.service.process_all_leads()
        self.assertIn('total_processed', result)
        self.assertIsNotNone(max_lead.lead_score)
        self.assertGreater(max_lead.lead_score, 0)

    def test_error_handling_in_bulk_processing(self):
        """Test error handling during bulk lead processing"""
        # Create a mix of valid and invalid leads
        leads = [
            Lead.objects.create(
                name='Valid Lead',
                email='valid@example.com',
                company='Valid Corp',
                created_by=self.user
            ),
            Lead.objects.create(
                name='Invalid Lead',
                email='invalid-email',  # Invalid email format
                company='Invalid Corp',
                created_by=self.user
            )
        ]
        
        result = self.service.process_all_leads()
        self.assertIn('total_processed', result)
        self.assertIn('successful', result)
