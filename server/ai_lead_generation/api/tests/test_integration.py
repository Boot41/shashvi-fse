from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient
from ..models import Lead
import json

User = get_user_model()

class AuthenticationIntegrationTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpass123'
        }
        self.login_url = reverse('token_obtain_pair')
        self.register_url = reverse('register')
        self.leads_url = reverse('get_leads')

    def test_complete_auth_flow(self):
        """Test complete authentication flow: register -> login -> access protected route"""
        # 1. Register new user
        register_response = self.client.post(self.register_url, self.user_data)
        self.assertEqual(register_response.status_code, status.HTTP_201_CREATED)

        # 2. Login with new user
        login_response = self.client.post(self.login_url, {
            'username': self.user_data['username'],
            'password': self.user_data['password']
        })
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)
        self.assertIn('access', login_response.data)
        self.assertIn('refresh', login_response.data)

        # 3. Access protected route with token
        access_token = login_response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        protected_response = self.client.get(self.leads_url)
        self.assertEqual(protected_response.status_code, status.HTTP_200_OK)

    def test_invalid_token_access(self):
        """Test accessing protected route with invalid token"""
        self.client.credentials(HTTP_AUTHORIZATION='Bearer invalid_token')
        response = self.client.get(self.leads_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

class LeadManagementIntegrationTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        # Get auth token
        response = self.client.post(reverse('token_obtain_pair'), {
            'username': 'testuser',
            'password': 'testpass123'
        })
        self.access_token = response.data['access']
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')

        # Create test lead
        self.lead = Lead.objects.create(
            name='Test Lead',
            email='lead@example.com',
            company='Test Company',
            position='CEO',
            created_by=self.user
        )

    def test_lead_operations_flow(self):
        """Test complete lead management flow"""
        # 1. Get leads (should include our test lead)
        get_response = self.client.get(reverse('get_leads'))
        self.assertEqual(get_response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(get_response.data), 1)
        self.assertEqual(get_response.data[0]['name'], 'Test Lead')

        # 2. Process leads
        process_response = self.client.post(reverse('process_leads'))
        self.assertEqual(process_response.status_code, status.HTTP_200_OK)

        # 3. Generate messages for lead
        message_response = self.client.post(
            reverse('test_message_generation'),
            {'lead_id': self.lead.id}
        )
        self.assertEqual(message_response.status_code, status.HTTP_200_OK)
        self.assertIn('linkedin_message', message_response.data)
        self.assertIn('email', message_response.data)

    def test_lead_isolation(self):
        """Test that users can only access their own leads"""
        # Create another user and their lead
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='otherpass123'
        )
        other_lead = Lead.objects.create(
            name='Other Lead',
            email='other.lead@example.com',
            company='Other Company',
            position='CTO',
            created_by=other_user
        )

        # Get leads - should only see own leads
        response = self.client.get(reverse('get_leads'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], 'Test Lead')

        # Try to generate messages for other user's lead
        response = self.client.post(
            reverse('test_message_generation'),
            {'lead_id': other_lead.id}
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

class TokenRefreshIntegrationTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.login_response = self.client.post(reverse('token_obtain_pair'), {
            'username': 'testuser',
            'password': 'testpass123'
        })

    def test_token_refresh_flow(self):
        """Test token refresh flow"""
        # Get initial tokens
        self.assertEqual(self.login_response.status_code, status.HTTP_200_OK)
        initial_access = self.login_response.data['access']
        refresh_token = self.login_response.data['refresh']

        # Use refresh token to get new access token
        refresh_response = self.client.post(reverse('token_refresh'), {
            'refresh': refresh_token
        })
        self.assertEqual(refresh_response.status_code, status.HTTP_200_OK)
        self.assertIn('access', refresh_response.data)
        new_access = refresh_response.data['access']
        self.assertNotEqual(initial_access, new_access)

        # Verify new access token works
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {new_access}')
        response = self.client.get(reverse('get_leads'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_invalid_refresh_token(self):
        """Test using invalid refresh token"""
        response = self.client.post(reverse('token_refresh'), {
            'refresh': 'invalid_refresh_token'
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
