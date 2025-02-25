from django.test import TestCase
from django.contrib.auth import get_user_model
from ..models import Lead

User = get_user_model()

class SimpleModelTests(TestCase):
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
        self.assertEqual(lead.email, 'lead@example.com')
        self.assertEqual(lead.company, 'Test Company')
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

    def test_lead_status_update(self):
        """Test updating lead status"""
        lead = Lead.objects.create(
            name='Test Lead',
            email='lead@example.com',
            company='Test Company',
            created_by=self.user
        )
        lead.status = 'contacted'
        lead.save()
        self.assertEqual(lead.status, 'contacted')

    def test_lead_notes(self):
        """Test lead notes field"""
        notes = "This is a test note"
        lead = Lead.objects.create(
            name='Test Lead',
            email='lead@example.com',
            company='Test Company',
            created_by=self.user,
            notes=notes
        )
        self.assertEqual(lead.notes, notes)
