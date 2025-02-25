import logging
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)

class LeadScorer:
    def __init__(self, target_industry: str = "SaaS"):
        self.target_industry = target_industry

    def calculate_company_size_score(self, lead):
        """Calculate score based on company size"""
        try:
            company_size = int(lead.company_size) if lead.company_size else 0
        except (ValueError, TypeError):
            return 0.1
        
        if company_size >= 1000:
            return 1.0
        elif company_size >= 500:
            return 0.8
        elif company_size >= 100:
            return 0.6
        elif company_size >= 50:
            return 0.3
        else:
            return 0.1

    def calculate_funding_score(self, lead):
        """Calculate score based on funding amount"""
        try:
            funding_amount = float(lead.funding_amount) if lead.funding_amount else 0
        except (ValueError, TypeError):
            return 0.1
        
        if funding_amount >= 10000000:  # 10M+
            return 1.0
        elif funding_amount >= 5000000:  # 5M+
            return 0.8
        elif funding_amount >= 1000000:  # 1M+
            return 0.5
        elif funding_amount >= 100000:   # 100K+
            return 0.2
        else:
            return 0.1

    def calculate_industry_score(self, lead):
        """Calculate score based on industry"""
        industry = str(lead.industry).lower() if lead.industry else ""
        
        high_value_industries = ['technology', 'tech', 'saas', 'fintech', 'ai', 'machine learning']
        medium_value_industries = ['healthcare', 'finance', 'retail', 'manufacturing']
        
        if any(ind in industry for ind in high_value_industries):
            return 1.0
        elif any(ind in industry for ind in medium_value_industries):
            return 0.8
        else:
            return 0.5

    def calculate_total_score(self, lead):
        """Calculate total lead score"""
        try:
            # Calculate individual scores
            company_size_score = self.calculate_company_size_score(lead)
            funding_score = self.calculate_funding_score(lead)
            industry_score = self.calculate_industry_score(lead)
            
            # Weights for each factor
            weights = {
                'company_size': 0.3,
                'funding': 0.3,
                'industry': 0.4
            }
            
            # Calculate weighted average
            total_score = (
                company_size_score * weights['company_size'] +
                funding_score * weights['funding'] +
                industry_score * weights['industry']
            )
            
            return round(total_score, 2)
        except Exception as e:
            logger.error(f"Error calculating lead score: {str(e)}")
            return 0.0
