from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from api.models import Lead
import json
import os

User = get_user_model()

class AuthenticationViewsTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.register_url = reverse('register')
        self.token_url = reverse('token_obtain_pair')
        self.user_data = {
            'username': 'testuser',
            'password': 'testpass123',
            'email': 'test@example.com'
        }

    def test_user_registration(self):
        """Test user registration endpoint"""
        response = self.client.post(self.register_url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.get().username, 'testuser')

    def test_user_token_obtain(self):
        """Test token obtain endpoint"""
        # Create a user first
        User.objects.create_user(username='testuser', password='testpass123')
        
        # Try to get token
        response = self.client.post(self.token_url, {
            'username': 'testuser',
            'password': 'testpass123'
        }, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

class LeadManagementViewsTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)
        
        self.lead = Lead.objects.create(
            name='John Doe',
            email='john@example.com',
            company='Test Company',
            position='CEO',
            industry='tech',
            created_by=self.user
        )
        
        self.import_url = reverse('import_leads')
        self.process_url = reverse('process_leads')
        self.test_message_url = reverse('test_message_generation')

    def test_import_leads_without_file(self):
        """Test import leads endpoint without file"""
        response = self.client.post(self.import_url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_process_leads(self):
        """Test process leads endpoint"""
        response = self.client.post(self.process_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
        self.assertIn('stats', response.data)

    def test_test_message_generation(self):
        """Test message generation endpoint"""
        response = self.client.post(self.test_message_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('linkedin_message', response.data)
        self.assertIn('email', response.data)
        self.assertIn('lead', response.data)

    def test_unauthorized_access(self):
        """Test unauthorized access to protected endpoints"""
        # Create a new client without authentication
        client = APIClient()
        
        response = client.post(self.process_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
