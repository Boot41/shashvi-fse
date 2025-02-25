from django.test import TestCase
from django.contrib.auth import get_user_model
from ..models import Lead, Outreach
from django.utils import timezone

User = get_user_model()

class BasicModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_lead_creation(self):
        """Test basic lead creation"""
        lead = Lead.objects.create(
            name='Test Lead',
            email='lead@example.com',
            company='Test Company',
            created_by=self.user
        )
        self.assertEqual(lead.name, 'Test Lead')
        self.assertEqual(lead.status, 'new')
        self.assertEqual(lead.lead_score, 0.0)

    def test_lead_string_representation(self):
        """Test lead string representation"""
        lead = Lead.objects.create(
            name='Test Lead',
            email='lead@example.com',
            company='Test Company',
            created_by=self.user
        )
        self.assertEqual(str(lead), 'Test Lead - Test Company')

    def test_outreach_creation(self):
        """Test basic outreach creation"""
        lead = Lead.objects.create(
            name='Test Lead',
            email='lead@example.com',
            company='Test Company',
            created_by=self.user
        )
        outreach = Outreach.objects.create(
            lead=lead,
            email_content='Test email',
            linkedin_content='Test LinkedIn message'
        )
        self.assertEqual(outreach.status, 'pending')
        self.assertIsNone(outreach.sent_at)

    def test_outreach_status_updates(self):
        """Test outreach status update methods"""
        lead = Lead.objects.create(
            name='Test Lead',
            email='lead@example.com',
            company='Test Company',
            created_by=self.user
        )
        outreach = Outreach.objects.create(
            lead=lead,
            email_content='Test email',
            linkedin_content='Test LinkedIn message'
        )
        
        # Test send
        outreach.send()
        self.assertEqual(outreach.status, 'sent')
        self.assertIsNotNone(outreach.sent_at)
        
        # Test mark_responded
        outreach.mark_responded()
        self.assertEqual(outreach.status, 'responded')
        self.assertIsNotNone(outreach.response_received_at)
        
        # Test mark_failed
        outreach.mark_failed('Test failure')
        self.assertEqual(outreach.status, 'failed')
        self.assertEqual(outreach.notes, 'Test failure')

    def test_lead_status_choices(self):
        """Test lead status choices"""
        lead = Lead.objects.create(
            name='Test Lead',
            email='lead@example.com',
            company='Test Company',
            created_by=self.user
        )
        
        # Test all valid statuses
        valid_statuses = ['new', 'contacted', 'qualified', 'converted', 'lost']
        for status in valid_statuses:
            lead.status = status
            lead.save()
            self.assertEqual(lead.status, status)

    def test_lead_ordering(self):
        """Test lead ordering by created_at"""
        lead1 = Lead.objects.create(
            name='Lead 1',
            email='lead1@example.com',
            company='Company 1',
            created_by=self.user
        )
        lead2 = Lead.objects.create(
            name='Lead 2',
            email='lead2@example.com',
            company='Company 2',
            created_by=self.user
        )
        
        leads = Lead.objects.all()
        self.assertEqual(leads[0], lead2)  # Most recent first
        self.assertEqual(leads[1], lead1)

    def test_outreach_string_representation(self):
        """Test outreach string representation"""
        lead = Lead.objects.create(
            name='Test Lead',
            email='lead@example.com',
            company='Test Company',
            created_by=self.user
        )
        outreach = Outreach.objects.create(
            lead=lead,
            email_content='Test email',
            linkedin_content='Test LinkedIn message'
        )
        expected_str = f"Outreach to Test Lead (pending)"
        self.assertEqual(str(outreach), expected_str)
