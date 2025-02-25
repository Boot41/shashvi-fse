from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from ..models import Lead

User = get_user_model()

class SimpleViewTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        self.lead = Lead.objects.create(
            name='Test Lead',
            email='lead@example.com',
            company='Test Company',
            created_by=self.user
        )

    def test_lead_list(self):
        """Test getting list of leads"""
        url = reverse('lead-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_lead_detail(self):
        """Test getting lead detail"""
        url = reverse('lead-detail', args=[self.lead.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Test Lead')

    def test_create_lead(self):
        """Test creating a new lead"""
        url = reverse('lead-list')
        data = {
            'name': 'New Lead',
            'email': 'new@example.com',
            'company': 'New Company'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Lead.objects.count(), 2)

    def test_update_lead(self):
        """Test updating a lead"""
        url = reverse('lead-detail', args=[self.lead.id])
        data = {
            'name': 'Updated Lead',
            'email': 'updated@example.com',
            'company': 'Updated Company'
        }
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.lead.refresh_from_db()
        self.assertEqual(self.lead.name, 'Updated Lead')
