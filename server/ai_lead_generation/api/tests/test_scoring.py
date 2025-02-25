from django.test import TestCase
from django.contrib.auth import get_user_model
from ..models import Lead
from ..scoring import LeadScorer

User = get_user_model()

class LeadScorerTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
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
        
        self.scorer = LeadScorer()
    
    def test_calculate_company_size_score(self):
        """Test company size scoring"""
        # Test different company sizes
        sizes = [(50, 0.3), (200, 0.6), (1000, 1.0)]
        for size, expected_score in sizes:
            self.lead.company_size = size
            score = self.scorer.calculate_company_size_score(self.lead)
            self.assertAlmostEqual(score, expected_score, places=1)
    
    def test_calculate_funding_score(self):
        """Test funding amount scoring"""
        # Test different funding amounts
        amounts = [(100000, 0.2), (1000000, 0.5), (10000000, 1.0)]
        for amount, expected_score in amounts:
            self.lead.funding_amount = amount
            score = self.scorer.calculate_funding_score(self.lead)
            self.assertAlmostEqual(score, expected_score, places=1)
    
    def test_calculate_industry_score(self):
        """Test industry scoring"""
        # Test different industries
        industries = [
            ('Technology', 1.0),
            ('Healthcare', 0.8),
            ('Other', 0.5)
        ]
        for industry, expected_score in industries:
            self.lead.industry = industry
            score = self.scorer.calculate_industry_score(self.lead)
            self.assertAlmostEqual(score, expected_score, places=1)
    
    def test_calculate_total_score(self):
        """Test total score calculation"""
        self.lead.company_size = 500
        self.lead.funding_amount = 5000000
        self.lead.industry = 'Technology'
        
        total_score = self.scorer.calculate_total_score(self.lead)
        self.assertGreater(total_score, 0)
        self.assertLessEqual(total_score, 1.0)
        
        # Test with minimum values
        self.lead.company_size = 10
        self.lead.funding_amount = 0
        self.lead.industry = 'Other'
        min_score = self.scorer.calculate_total_score(self.lead)
        self.assertLess(min_score, total_score)
