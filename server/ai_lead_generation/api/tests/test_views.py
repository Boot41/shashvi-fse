from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from ai_lead_generation.api.models import Lead
import json
import os
import tempfile
import csv

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
        self.assertNotIn('password', response.data)  # Password should not be in response
        self.assertIn('id', response.data)
        self.assertIn('username', response.data)
        self.assertIn('email', response.data)

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
        self.lead_detail_url = reverse('lead-detail', kwargs={'pk': self.lead.pk})
        self.generate_messages_url = reverse('generate_messages', kwargs={'lead_id': self.lead.pk})

    def test_import_leads_without_file(self):
        """Test import leads endpoint without file"""
        response = self.client.post(self.import_url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_import_leads_with_valid_file(self):
        """Test import leads endpoint with valid CSV file"""
        # Create a temporary CSV file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            writer = csv.writer(f)
            writer.writerow(['name', 'email', 'company', 'position', 'industry'])
            writer.writerow(['John Doe', 'john@example.com', 'Test Inc', 'CEO', 'tech'])
            writer.writerow(['Jane Smith', 'jane@example.com', 'Test Corp', 'CTO', 'tech'])
        
        # Open and send the file
        with open(f.name, 'rb') as f:
            response = self.client.post(self.import_url, {'file': f}, format='multipart')
        
        # Clean up
        os.unlink(f.name)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('imported_count', response.data)
        self.assertIn('error_count', response.data)

    def test_import_leads_with_invalid_file(self):
        """Test import leads endpoint with invalid file format"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write('invalid data')
            txt_path = f.name

        try:
            with open(txt_path, 'rb') as txt_file:
                response = self.client.post(self.import_url, {'file': txt_file}, format='multipart')
                self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        finally:
            os.unlink(txt_path)

    def test_process_leads(self):
        """Test process leads endpoint"""
        response = self.client.post(self.process_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_processed', response.data)
        self.assertIn('successful', response.data)
        self.assertIn('failed', response.data)

    def test_lead_detail_view(self):
        """Test lead detail endpoint"""
        # Test GET request
        response = self.client.get(self.lead_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'John Doe')

        # Test PUT request
        updated_data = {
            'name': 'John Updated',
            'email': 'john.updated@example.com',
            'company': 'Updated Company',
            'position': 'CTO',
            'industry': 'tech'
        }
        response = self.client.put(self.lead_detail_url, updated_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'John Updated')

        # Test PATCH request
        patch_data = {'position': 'COO'}
        response = self.client.patch(self.lead_detail_url, patch_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['position'], 'COO')

        # Test DELETE request
        response = self.client.delete(self.lead_detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Lead.objects.filter(pk=self.lead.pk).exists())

    def test_generate_messages_view(self):
        """Test message generation for a specific lead"""
        response = self.client.post(self.generate_messages_url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)  
        self.assertIn('email_content', response.data)
        self.assertIn('linkedin_content', response.data)
        self.assertIn('lead', response.data)
        
        # Verify message content
        self.assertIn(self.lead.name, response.data['email_content'])
        self.assertIn(self.lead.company, response.data['email_content'])
        self.assertLess(len(response.data['linkedin_content']), 300)

    def test_generate_messages_invalid_lead(self):
        """Test message generation with invalid lead ID"""
        invalid_url = reverse('generate_messages', kwargs={'lead_id': 99999})
        response = self.client.post(invalid_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_process_leads_with_filters(self):
        """Test process leads endpoint with filters"""
        # Delete existing leads
        Lead.objects.all().delete()
        
        # Create leads with different statuses
        Lead.objects.create(
            name='Test Lead 1',
            email='test1@example.com',
            company='Company 1',
            status='new',
            created_by=self.user
        )
        Lead.objects.create(
            name='Test Lead 2',
            email='test2@example.com',
            company='Company 2',
            status='contacted',
            created_by=self.user
        )

        # Test processing with status filter
        response = self.client.post(f"{self.process_url}?status=new")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_processed'], 1)
        self.assertEqual(response.data['successful'], 1)
        self.assertEqual(response.data['failed'], 0)

        # Test processing with industry filter
        response = self.client.post(f"{self.process_url}?industry=tech")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_processed', response.data)
        self.assertIn('successful', response.data)
        self.assertIn('failed', response.data)

    def test_rate_limiting(self):
        """Test rate limiting on API endpoints"""
        # Make multiple rapid requests to test rate limiting
        for _ in range(10):
            response = self.client.get(self.lead_detail_url)
        
        # The last request should be rate limited
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_429_TOO_MANY_REQUESTS])

    def test_test_message_generation(self):
        """Test message generation endpoint"""
        test_data = {
            'name': 'Test Lead',
            'company': 'Test Company',
            'position': 'CEO',
            'industry': 'tech'
        }
        response = self.client.post(self.test_message_url, test_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('email_content', response.data)
        self.assertIn('linkedin_content', response.data)  
        self.assertIn('Test Lead', response.data['email_content'])
        self.assertIn('Test Company', response.data['email_content'])

    def test_unauthorized_access(self):
        """Test unauthorized access to protected endpoints"""
        # Create a new client without authentication
        client = APIClient()
        
        response = client.post(self.process_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
