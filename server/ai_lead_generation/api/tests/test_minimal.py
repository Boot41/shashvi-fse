from django.test import TestCase
from django.contrib.auth import get_user_model
from ..models import Lead

User = get_user_model()

class MinimalTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_lead_creation_and_score(self):
        """Test creating a lead and checking its score"""
        lead = Lead.objects.create(
            name='Test Lead',
            email='lead@example.com',
            company='Test Company',
            industry='Technology',
            company_size=1000,
            funding_amount=1000000,
            created_by=self.user
        )
        
        # Basic field checks
        self.assertEqual(lead.name, 'Test Lead')
        self.assertEqual(lead.email, 'lead@example.com')
        self.assertEqual(lead.company, 'Test Company')
        
        # Score should be greater than 0 for a high-value lead
        self.assertGreater(lead.lead_score, 0)
        self.assertLessEqual(lead.lead_score, 1.0)

    def test_lead_minimal_data(self):
        """Test lead creation with minimal data"""
        lead = Lead.objects.create(
            name='Minimal Lead',
            email='minimal@example.com',
            company='Minimal Company',
            created_by=self.user
        )
        
        # Check default values
        self.assertEqual(lead.status, 'new')
        self.assertEqual(lead.lead_score, 0.0)
        self.assertEqual(lead.notes, '')
        
        # String representation
        self.assertEqual(str(lead), 'Minimal Lead - Minimal Company')
