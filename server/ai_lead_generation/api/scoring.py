from typing import Dict, Optional
import pandas as pd
import numpy as np

class LeadScorer:
    def __init__(self, target_industry: str = "SaaS"):
        self.target_industry = target_industry
        # Weights for different factors (total = 100)
        self.weights = {
            'funding_score': 40,  # 40% weight for funding
            'industry_score': 30,  # 30% weight for industry fit
            'hiring_score': 30,   # 30% weight for hiring activity
        }

    def calculate_funding_score(self, funding_amount: Optional[float]) -> float:
        """
        Calculate score based on funding amount
        Score ranges: 
        - $0-1M: 20 points
        - $1M-5M: 40 points
        - $5M-20M: 60 points
        - $20M-50M: 80 points
        - $50M+: 100 points
        """
        if not funding_amount or pd.isna(funding_amount):
            return 0
        
        funding_ranges = [
            (0, 1_000_000, 20),
            (1_000_000, 5_000_000, 40),
            (5_000_000, 20_000_000, 60),
            (20_000_000, 50_000_000, 80),
            (50_000_000, float('inf'), 100)
        ]
        
        for min_amount, max_amount, score in funding_ranges:
            if min_amount <= funding_amount < max_amount:
                return score
        return 0

    def calculate_industry_score(self, industry: Optional[str]) -> float:
        """
        Calculate score based on industry fit
        - Exact match with target: 100 points
        - Related industry: 60 points
        - Other tech: 40 points
        - Others: 20 points
        """
        if not industry or pd.isna(industry):
            return 0
        
        industry = industry.lower()
        target = self.target_industry.lower()
        
        # Exact match
        if target in industry or industry in target:
            return 100
            
        # Related industries (customize based on your target)
        related_industries = ['software', 'tech', 'cloud', 'platform']
        if any(rel in industry for rel in related_industries):
            return 60
            
        # Other tech
        tech_industries = ['it', 'digital', 'internet', 'web']
        if any(tech in industry for tech in tech_industries):
            return 40
            
        return 20

    def calculate_hiring_score(self, hiring_data: Dict) -> float:
        """
        Calculate score based on hiring trends
        - Actively hiring (multiple positions): 100 points
        - Some hiring activity: 60 points
        - No current hiring: 20 points
        """
        if not hiring_data or pd.isna(hiring_data):
            return 20
            
        try:
            num_positions = hiring_data.get('open_positions', 0)
            if num_positions > 5:
                return 100
            elif num_positions > 0:
                return 60
            return 20
        except:
            return 20

    def calculate_total_score(self, company_data: Dict) -> int:
        """
        Calculate total lead score based on all factors
        Returns a score from 1-100
        """
        # Calculate individual scores
        funding_score = self.calculate_funding_score(company_data.get('funding_amount'))
        industry_score = self.calculate_industry_score(company_data.get('industry'))
        hiring_score = self.calculate_hiring_score(company_data.get('hiring_data'))
        
        # Apply weights
        weighted_score = (
            funding_score * self.weights['funding_score'] / 100 +
            industry_score * self.weights['industry_score'] / 100 +
            hiring_score * self.weights['hiring_score'] / 100
        )
        
        # Round to nearest integer and ensure range is 1-100
        return max(1, min(100, round(weighted_score)))
