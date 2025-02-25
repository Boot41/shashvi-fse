from django.test import TestCase
from django.contrib.auth import get_user_model
from ..models import Lead
from ..services import LeadAutomationService

User = get_user_model()

class SimpleLeadAutomationServiceTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.service = LeadAutomationService()

    def test_process_all_leads(self):
        """Test processing all leads"""
        # Create test leads
        Lead.objects.create(
            name='Lead 1',
            email='lead1@example.com',
            company='Company 1',
            created_by=self.user
        )
        Lead.objects.create(
            name='Lead 2',
            email='lead2@example.com',
            company='Company 2',
            created_by=self.user
        )
        
        # Process leads
        result = self.service.process_all_leads()
        self.assertIn('total_processed', result)
        self.assertIn('processed', result)
        self.assertEqual(result['total_processed'], 2)

    def test_process_leads_with_filters(self):
        """Test processing leads with filters"""
        # Create test leads
        Lead.objects.create(
            name='Tech Lead',
            email='tech@example.com',
            company='Tech Corp',
            industry='Technology',
            created_by=self.user
        )
        Lead.objects.create(
            name='Other Lead',
            email='other@example.com',
            company='Other Corp',
            industry='Other',
            created_by=self.user
        )
        
        # Process leads with industry filter
        filters = {'industry': 'Technology'}
        result = self.service.process_all_leads(filters=filters)
        self.assertEqual(result['total_processed'], 1)

    def test_process_leads_empty_result(self):
        """Test processing leads with no matches"""
        # Create test lead
        Lead.objects.create(
            name='Test Lead',
            email='test@example.com',
            company='Test Corp',
            created_by=self.user
        )
        
        # Process leads with non-matching filter
        filters = {'industry': 'NonExistent'}
        result = self.service.process_all_leads(filters=filters)
        self.assertEqual(result['total_processed'], 0)
        self.assertEqual(len(result['processed']), 0)

    def test_process_leads_with_scoring(self):
        """Test processing leads with scoring"""
        # Create high-value lead
        Lead.objects.create(
            name='High Value Lead',
            email='high@example.com',
            company='Big Corp',
            industry='Technology',
            company_size=1000,
            funding_amount=1000000,
            created_by=self.user
        )
        
        # Process leads
        result = self.service.process_all_leads()
        processed_lead = result['processed'][0]
        self.assertGreater(processed_lead.lead_score, 0)
