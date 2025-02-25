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
        
        self.assertIn('total_processed', result)
        self.assertIn('processed', result)
        self.assertGreater(result['total_processed'], 0)
        self.assertGreater(len(result['processed']), 0)
        
        lead_data = result['processed'][0]
        self.assertIn('id', lead_data)
        self.assertIn('name', lead_data)
        self.assertIn('company', lead_data)
        self.assertIn('industry', lead_data)
        self.assertIn('status', lead_data)
        self.assertIn('score', lead_data)

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
        # Create an invalid lead
        Lead.objects.create(
            name='Invalid Lead',
            email='invalid@example.com',
            company='Invalid Corp',
            created_by=self.user
        )
        
        # Create a valid lead
        Lead.objects.create(
            name='Valid Lead',
            email='valid@example.com',
            company='Valid Corp',
            created_by=self.user
        )
        
        result = self.service.process_all_leads()
        self.assertIn('total_processed', result)
        self.assertIn('processed', result)
        self.assertEqual(result['total_processed'], 3)  # Including the one from setUp

    def test_process_leads_error_handling(self):
        """Test error handling during lead processing"""
        with self.assertRaises(ValueError):
            self.service.process_all_leads({'invalid_filter': 'value'})
            
        # Test with invalid status
        with self.assertRaises(ValueError):
            self.service.process_all_leads({'status': 'invalid_status'})

    def test_process_leads_with_filters(self):
        """Test processing leads with different filters"""
        # Create additional leads
        leads = [
            Lead.objects.create(
                name=f'Test Lead {i}',
                email=f'lead{i}@example.com',
                company=f'Company {i}',
                industry='Technology' if i % 2 == 0 else 'Finance',
                status='new',
                created_by=self.user
            ) for i in range(5)
        ]
        
        # Test filtering by industry
        result = self.service.process_all_leads({'industry': 'Technology'})
        self.assertGreater(len(result['processed']), 0)
        for lead in result['processed']:
            self.assertEqual(lead['industry'], 'Technology')
        
        # Test filtering by status
        result = self.service.process_all_leads({'status': 'new'})
        self.assertGreater(len(result['processed']), 0)
        for lead in result['processed']:
            self.assertEqual(lead['status'], 'new')

    def test_lead_scoring(self):
        """Test lead scoring functionality"""
        # Create leads with different characteristics
        high_value_lead = Lead.objects.create(
            name='High Value Lead',
            email='high@example.com',
            company='Big Corp',
            industry='Technology',
            company_size=1000,
            funding_amount=10000000,
            created_by=self.user
        )
        
        low_value_lead = Lead.objects.create(
            name='Low Value Lead',
            email='low@example.com',
            company='Small Corp',
            industry='Other',
            company_size=10,
            funding_amount=0,
            created_by=self.user
        )
        
        # Score the leads
        high_score = self.service.score_lead(high_value_lead)
        low_score = self.service.score_lead(low_value_lead)
        
        # High value lead should have higher score
        self.assertGreater(high_score, low_score)

    def test_message_customization(self):
        """Test message customization based on lead attributes"""
        # Test with different lead attributes
        enterprise_lead = Lead.objects.create(
            name='Enterprise Lead',
            email='enterprise@example.com',
            company='Enterprise Corp',
            industry='Technology',
            company_size=5000,
            created_by=self.user
        )
        
        startup_lead = Lead.objects.create(
            name='Startup Lead',
            email='startup@example.com',
            company='Cool Startup',
            industry='Technology',
            company_size=10,
            created_by=self.user
        )
        
        # Messages should be different for different types of leads
        enterprise_message = self.service.generate_email_content(enterprise_lead)
        startup_message = self.service.generate_email_content(startup_lead)
        
        self.assertNotEqual(enterprise_message, startup_message)
        self.assertIn('Enterprise Corp', enterprise_message)
        self.assertIn('Cool Startup', startup_message)
