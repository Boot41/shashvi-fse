from django.test import TestCase
from django.contrib.auth import get_user_model
from ai_lead_generation.api.models import Lead

User = get_user_model()

class LeadModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
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

    def test_lead_creation(self):
        """Test lead creation and default values"""
        self.assertEqual(self.lead.name, 'John Doe')
        self.assertEqual(self.lead.email, 'john@example.com')
        self.assertEqual(self.lead.company, 'Test Company')
        self.assertEqual(self.lead.position, 'CEO')
        self.assertEqual(self.lead.industry, 'tech')
        self.assertEqual(self.lead.company_size, 100)
        self.assertEqual(float(self.lead.funding_amount), 1000000.00)
        self.assertEqual(self.lead.created_by, self.user)
        self.assertEqual(self.lead.status, 'new')
        self.assertIsNotNone(self.lead.lead_score)  # Score should be calculated on save

    def test_lead_str_representation(self):
        """Test the string representation of Lead model"""
        expected_str = f"{self.lead.name} - {self.lead.company}"
        self.assertEqual(str(self.lead), expected_str)

    def test_lead_score_calculation(self):
        """Test lead score calculation based on various factors"""
        # Update lead with high-value attributes
        self.lead.company_size = 1500  # > 1000 for max points
        self.lead.funding_amount = 10000000.00
        self.lead.industry = 'tech'
        self.lead.save()
        
        # Verify the lead score is calculated
        self.assertIsNotNone(self.lead.lead_score)
        self.assertGreater(self.lead.lead_score, 0)
