from django.test import TestCase
from django.contrib.auth import get_user_model
from ..models import Lead

User = get_user_model()

class BasicLeadTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_lead_basic_fields(self):
        """Test basic lead fields"""
        lead = Lead.objects.create(
            name='Test Lead',
            email='lead@example.com',
            company='Test Company',
            created_by=self.user
        )
        
        # Check field values
        self.assertEqual(lead.name, 'Test Lead')
        self.assertEqual(lead.email, 'lead@example.com')
        self.assertEqual(lead.company, 'Test Company')
        self.assertEqual(lead.status, 'new')
        self.assertEqual(lead.notes, '')
        
        # Check string representation
        self.assertEqual(str(lead), 'Test Lead - Test Company')
