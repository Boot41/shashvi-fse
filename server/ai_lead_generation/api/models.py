from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.contrib.auth.models import AbstractUser, Group, Permission, User
from django.core.validators import MinValueValidator, MaxValueValidator
import json

# Create your models here.

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('user', 'User'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')

    groups = models.ManyToManyField(
        Group,
        related_name='customuser_set',  
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups'
    )
    
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='customuser_permissions',  
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions'
    )

class Company(models.Model):
    """Model representing a company."""
    name = models.CharField(max_length=255)
    industry = models.CharField(max_length=255)
    funding_amount = models.DecimalField(max_digits=15, decimal_places=2)
    location = models.CharField(max_length=255)
    linkedin_profile = models.URLField(blank=True)
    website = models.URLField(blank=True, null=True, help_text="Company website URL")
    about = models.TextField(blank=True, help_text="Description of the company")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def clean(self):
        if not self.name:
            raise ValidationError('Name cannot be empty.')
        if not self.industry:
            raise ValidationError('Industry cannot be empty.')
        if self.funding_amount is None:
            raise ValidationError('Funding amount cannot be empty.')
        if not self.location:
            raise ValidationError('Location cannot be empty.')

class Lead(models.Model):
    # Basic Information
    name = models.CharField(max_length=255, default='Unknown')
    email = models.EmailField(default='unknown@example.com')
    company = models.CharField(max_length=255, default='Unknown Company')
    position = models.CharField(max_length=255, default='Unknown Position')
    
    # Company Details
    industry = models.CharField(max_length=255, blank=True)
    company_size = models.CharField(max_length=50, blank=True)
    funding_amount = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        null=True, 
        blank=True,
        help_text="Company's funding amount in USD"
    )
    
    # Scoring
    lead_score = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        null=True,
        blank=True,
        help_text="Lead score from 0-100"
    )
    
    # Hiring Information
    open_positions = models.IntegerField(
        default=0,
        help_text="Number of open positions"
    )
    
    # Metadata and Tracking
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,  
        related_name='leads',
        null=True,  
        blank=True  
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_contacted = models.DateTimeField(null=True, blank=True)
    last_contact_date = models.DateTimeField(null=True, blank=True, help_text="Date when the lead was last contacted")
    
    # Status
    STATUS_CHOICES = [
        ('new', 'New'),
        ('contacted', 'Contacted'),
        ('qualified', 'Qualified'),
        ('unqualified', 'Unqualified'),
        ('converted', 'Converted'),
    ]
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='new'
    )
    
    # Notes and Additional Data
    notes = models.TextField(blank=True)
    metadata = models.JSONField(
        null=True,
        blank=True,
        help_text="Additional metadata about the lead"
    )

    def __str__(self):
        return f"{self.name} - {self.company}"

    class Meta:
        ordering = ['-lead_score', '-created_at']
        
    def get_metadata_display(self):
        """Returns formatted metadata for admin display"""
        if not self.metadata:
            return "No metadata"
        try:
            return json.dumps(self.metadata, indent=2)
        except:
            return str(self.metadata)

    def calculate_lead_score(self):
        """Calculate lead score based on various factors"""
        score = 0
        
        # Company size score (max 30 points)
        try:
            size = int(self.company_size)
            if size > 1000:
                score += 30
            elif size > 500:
                score += 20
            elif size > 100:
                score += 10
        except (ValueError, TypeError):
            pass
        
        # Funding amount score (max 40 points)
        if self.funding_amount:
            funding = float(self.funding_amount)
            if funding > 10000000:  # > 10M
                score += 40
            elif funding > 5000000:  # > 5M
                score += 30
            elif funding > 1000000:  # > 1M
                score += 20
            elif funding > 500000:  # > 500K
                score += 10
        
        # Industry score (max 30 points)
        tech_industries = ['tech', 'technology', 'software', 'it', 'saas']
        if self.industry and self.industry.lower() in tech_industries:
            score += 30
        
        # Ensure score is between 0 and 100
        return max(0, min(100, score))

    def save(self, *args, **kwargs):
        if self.lead_score is None:
            self.lead_score = self.calculate_lead_score()
        super().save(*args, **kwargs)

class LeadMessage(models.Model):
    lead = models.ForeignKey(
        Lead,
        on_delete=models.CASCADE,
        related_name='messages'
    )
    linkedin_message = models.TextField()
    email_content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Messages for {self.lead.name}"

class Outreach(models.Model):
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name='outreach_emails', null=True)
    email_content = models.TextField()
    linkedin_content = models.TextField(blank=True, help_text="LinkedIn message content")
    generated_at = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=False)
    is_linkedin_approved = models.BooleanField(default=False)

    def __str__(self):
        return f"Outreach for {self.lead.company if self.lead else 'Unknown'} - {self.generated_at.strftime('%Y-%m-%d %H:%M')}"

    class Meta:
        ordering = ['-generated_at']
