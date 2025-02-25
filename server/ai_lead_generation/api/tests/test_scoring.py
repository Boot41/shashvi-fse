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


class LeadScorerTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.scorer = LeadScorer()
        
        # Create test leads with various characteristics
        self.enterprise_lead = Lead.objects.create(
            name='Enterprise Corp',
            email='enterprise@example.com',
            company='Enterprise Inc',
            position='CEO',
            industry='Technology',
            company_size=5000,
            funding_amount=50000000,
            created_by=self.user
        )
        
        self.startup_lead = Lead.objects.create(
            name='Startup Corp',
            email='startup@example.com',
            company='Startup Inc',
            position='Founder',
            industry='SaaS',
            company_size=10,
            funding_amount=500000,
            created_by=self.user
        )
        
        self.minimal_lead = Lead.objects.create(
            name='Minimal Corp',
            email='minimal@example.com',
            created_by=self.user
        )

    def test_company_size_scoring(self):
        """Test scoring based on company size"""
        # Test enterprise company
        score = self.scorer.calculate_company_size_score(self.enterprise_lead)
        self.assertEqual(score, 1.0)
        
        # Test startup
        score = self.scorer.calculate_company_size_score(self.startup_lead)
        self.assertEqual(score, 0.1)
        
        # Test missing company size
        score = self.scorer.calculate_company_size_score(self.minimal_lead)
        self.assertEqual(score, 0.1)
        
        # Test string value handling
        lead = Lead.objects.create(
            name='String Size Corp',
            company_size='1000',
            created_by=self.user
        )
        score = self.scorer.calculate_company_size_score(lead)
        self.assertEqual(score, 1.0)
        
        # Test invalid value handling
        lead.company_size = 'invalid'
        score = self.scorer.calculate_company_size_score(lead)
        self.assertEqual(score, 0.1)

    def test_funding_scoring(self):
        """Test scoring based on funding amount"""
        # Test well-funded company
        score = self.scorer.calculate_funding_score(self.enterprise_lead)
        self.assertEqual(score, 1.0)
        
        # Test startup funding
        score = self.scorer.calculate_funding_score(self.startup_lead)
        self.assertEqual(score, 0.2)
        
        # Test no funding
        score = self.scorer.calculate_funding_score(self.minimal_lead)
        self.assertEqual(score, 0.1)
        
        # Test string value handling
        lead = Lead.objects.create(
            name='String Funding Corp',
            funding_amount='10000000',
            created_by=self.user
        )
        score = self.scorer.calculate_funding_score(lead)
        self.assertEqual(score, 1.0)
        
        # Test invalid value handling
        lead.funding_amount = 'invalid'
        score = self.scorer.calculate_funding_score(lead)
        self.assertEqual(score, 0.1)

    def test_industry_scoring(self):
        """Test scoring based on industry"""
        # Test high-value industry
        score = self.scorer.calculate_industry_score(self.enterprise_lead)
        self.assertEqual(score, 1.0)
        
        # Test another high-value industry
        score = self.scorer.calculate_industry_score(self.startup_lead)
        self.assertEqual(score, 1.0)
        
        # Test missing industry
        score = self.scorer.calculate_industry_score(self.minimal_lead)
        self.assertEqual(score, 0.5)
        
        # Test medium-value industry
        lead = Lead.objects.create(
            name='Healthcare Corp',
            industry='Healthcare',
            created_by=self.user
        )
        score = self.scorer.calculate_industry_score(lead)
        self.assertEqual(score, 0.8)
        
        # Test case insensitivity
        lead.industry = 'TECHNOLOGY'
        score = self.scorer.calculate_industry_score(lead)
        self.assertEqual(score, 1.0)

    def test_total_score_calculation(self):
        """Test calculation of total lead score"""
        # Test high-value lead
        score = self.scorer.calculate_total_score(self.enterprise_lead)
        self.assertGreaterEqual(score, 0.9)
        self.assertLessEqual(score, 1.0)
        
        # Test startup lead
        score = self.scorer.calculate_total_score(self.startup_lead)
        self.assertGreater(score, 0.3)
        self.assertLess(score, 0.8)
        
        # Test minimal lead
        score = self.scorer.calculate_total_score(self.minimal_lead)
        self.assertGreater(score, 0)
        self.assertLess(score, 0.5)
        
        # Test error handling
        lead = Lead.objects.create(
            name='Error Corp',
            company_size='invalid',
            funding_amount='invalid',
            created_by=self.user
        )
        score = self.scorer.calculate_total_score(lead)
        self.assertGreaterEqual(score, 0)
        self.assertLessEqual(score, 1)

    def test_edge_cases(self):
        """Test edge cases and boundary conditions"""
        # Test extremely large values
        large_lead = Lead.objects.create(
            name='Huge Corp',
            company_size=1000000000,
            funding_amount=1000000000000,
            industry='Technology',
            created_by=self.user
        )
        score = self.scorer.calculate_total_score(large_lead)
        self.assertGreaterEqual(score, 0)
        self.assertLessEqual(score, 1)
        
        # Test zero values
        zero_lead = Lead.objects.create(
            name='Zero Corp',
            company_size=0,
            funding_amount=0,
            industry='Other',
            created_by=self.user
        )
        score = self.scorer.calculate_total_score(zero_lead)
        self.assertGreaterEqual(score, 0)
        self.assertLessEqual(score, 1)
        
        # Test negative values
        negative_lead = Lead.objects.create(
            name='Negative Corp',
            company_size=-100,
            funding_amount=-1000000,
            created_by=self.user
        )
        score = self.scorer.calculate_total_score(negative_lead)
        self.assertGreaterEqual(score, 0)
        self.assertLessEqual(score, 1)
