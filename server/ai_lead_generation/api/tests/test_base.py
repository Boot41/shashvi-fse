"""Base test case for API tests"""

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from ..models import Lead, Outreach

User = get_user_model()

class BaseTestCase(TestCase):
    def setUp(self):
        """Set up test data and authentication"""
        self.client = APIClient()
        
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Get JWT token
        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)
        
        # Set up authentication headers
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        
        # Create test lead
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
        
        # Create test outreach
        self.test_outreach = Outreach.objects.create(
            lead=self.lead,
            email_content='Test email content',
            linkedin_content='Test LinkedIn content'
        )
        
        # Set up API endpoints
        self.leads_url = reverse('lead-list-create')
        self.import_url = reverse('import-leads')
        self.process_url = reverse('process-leads')
        self.generate_messages_url = reverse('generate-messages', kwargs={'lead_id': self.lead.id})
        
    def tearDown(self):
        """Clean up after each test"""
        User.objects.all().delete()
        Lead.objects.all().delete()
        Outreach.objects.all().delete()
        
    def test_setup(self):
        """Test that setup works correctly"""
        self.assertTrue(self.user.is_authenticated)
        self.assertEqual(Lead.objects.count(), 1)
        self.assertEqual(Outreach.objects.count(), 1)
