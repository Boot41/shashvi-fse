from django.test import TestCase
from django.contrib.auth import get_user_model
from ..models import Lead
from ..scoring import LeadScorer

User = get_user_model()

class SimpleLeadScorerTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.scorer = LeadScorer()

    def test_company_size_scoring(self):
        """Test scoring based on company size"""
        lead = Lead.objects.create(
            name='Test Lead',
            email='test@example.com',
            company='Test Company',
            company_size=1000,  # Large company
            created_by=self.user
        )
        score = self.scorer.calculate_company_size_score(lead)
        self.assertGreater(score, 0)

    def test_funding_scoring(self):
        """Test scoring based on funding amount"""
        lead = Lead.objects.create(
            name='Test Lead',
            email='test@example.com',
            company='Test Company',
            funding_amount=1000000,  # Well-funded
            created_by=self.user
        )
        score = self.scorer.calculate_funding_score(lead)
        self.assertGreater(score, 0)

    def test_industry_scoring(self):
        """Test scoring based on industry"""
        lead = Lead.objects.create(
            name='Test Lead',
            email='test@example.com',
            company='Test Company',
            industry='Technology',  # High-value industry
            created_by=self.user
        )
        score = self.scorer.calculate_industry_score(lead)
        self.assertGreater(score, 0)

    def test_total_score_calculation(self):
        """Test total score calculation"""
        lead = Lead.objects.create(
            name='Test Lead',
            email='test@example.com',
            company='Test Company',
            company_size=1000,
            funding_amount=1000000,
            industry='Technology',
            created_by=self.user
        )
        score = self.scorer.calculate_total_score(lead)
        self.assertGreater(score, 0)
        self.assertLessEqual(score, 1.0)  # Score should be normalized
