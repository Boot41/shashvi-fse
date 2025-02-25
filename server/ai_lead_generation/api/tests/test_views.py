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
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.files.uploadedfile import SimpleUploadedFile

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
        """Set up test data and authentication"""
        self.client = APIClient()
        
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Get JWT token
        refresh = RefreshToken.for_user(self.user)
        self.access_token = str(refresh.access_token)
        
        # Set up authentication headers
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        
        # Create test lead
        self.lead = Lead.objects.create(
            name='John Doe',
            email='john@example.com',
            company='Test Company',
            position='CEO',
            industry='Technology',
            created_by=self.user
        )
        
        # Set up API endpoints
        self.leads_url = reverse('lead-list-create')
        self.import_url = reverse('import-leads')
        self.process_url = reverse('process-leads')
        self.generate_messages_url = reverse('generate-messages')

    def test_unauthorized_access(self):
        """Test accessing protected endpoints without authentication"""
        # Remove authentication
        self.client.credentials()
        
        # Test leads endpoint
        response = self.client.get(self.leads_url)
        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED,
            "Endpoint /api/leads/ should require authentication"
        )
        
        # Test import endpoint
        response = self.client.post(self.import_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # Test process endpoint
        response = self.client.post(self.process_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_process_leads(self):
        """Test process leads endpoint"""
        response = self.client.post(self.process_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        data = response.json()
        self.assertIn('total_processed', data)
        self.assertIn('processed', data)
        self.assertGreater(data['total_processed'], 0)

    def test_process_leads_with_filters(self):
        """Test process leads endpoint with filters"""
        # Test with status filter
        response = self.client.post(f"{self.process_url}?status=new")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        data = response.json()
        self.assertIn('total_processed', data)
        self.assertIn('processed', data)
        
        # Test with industry filter
        response = self.client.post(f"{self.process_url}?industry=Technology")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        data = response.json()
        self.assertIn('total_processed', data)
        self.assertIn('processed', data)

    def test_process_leads_invalid_filter(self):
        """Test process leads endpoint with invalid filter"""
        response = self.client.post(f"{self.process_url}?invalid_filter=value")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_generate_messages_view(self):
        """Test message generation for a specific lead"""
        response = self.client.post(self.generate_messages_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        data = response.json()
        self.assertIn('linkedin_message', data)
        self.assertIn('email_content', data)

    def test_generate_messages_invalid_lead(self):
        """Test message generation with invalid lead ID"""
        invalid_url = reverse('generate-messages')
        response = self.client.post(invalid_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_import_leads(self):
        """Test importing leads from CSV"""
        csv_content = "name,email,company,position,industry\nJane Doe,jane@example.com,Test Corp,CTO,Technology"
        csv_file = SimpleUploadedFile("leads.csv", csv_content.encode('utf-8'), content_type='text/csv')
        
        response = self.client.post(self.import_url, {'file': csv_file}, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        data = response.json()
        self.assertIn('imported_count', data)
        self.assertIn('error_count', data)
        self.assertEqual(data['imported_count'], 1)
        self.assertEqual(data['error_count'], 0)

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

    def test_lead_detail_view(self):
        """Test lead detail endpoint"""
        # Test GET request
        response = self.client.get(reverse('lead-detail', kwargs={'pk': self.lead.pk}))
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
        response = self.client.put(reverse('lead-detail', kwargs={'pk': self.lead.pk}), updated_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'John Updated')

        # Test PATCH request
        patch_data = {'position': 'COO'}
        response = self.client.patch(reverse('lead-detail', kwargs={'pk': self.lead.pk}), patch_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['position'], 'COO')

        # Test DELETE request
        response = self.client.delete(reverse('lead-detail', kwargs={'pk': self.lead.pk}))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Lead.objects.filter(pk=self.lead.pk).exists())

    def test_rate_limiting(self):
        """Test rate limiting on API endpoints"""
        # Make multiple rapid requests to test rate limiting
        for _ in range(10):
            response = self.client.get(reverse('lead-detail', kwargs={'pk': self.lead.pk}))
        
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
        response = self.client.post(reverse('test-message-generation'), test_data, format='json')
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

    def test_process_leads_invalid_filter(self):
        """Test processing leads with invalid filter parameters"""
        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            reverse('process-leads') + '?status=invalid_status',
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
    def test_generate_messages_lead_not_found(self):
        """Test generating messages for non-existent lead"""
        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            reverse('generate-messages', kwargs={'lead_id': 99999}),
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        
    def test_import_leads_empty_csv(self):
        """Test importing an empty CSV file"""
        self.client.force_authenticate(user=self.user)
        
        # Create empty CSV file
        with tempfile.NamedTemporaryFile(suffix='.csv', mode='w', delete=False) as f:
            writer = csv.writer(f)
            writer.writerow(['name', 'email', 'company', 'industry'])  # Only headers
            
        with open(f.name, 'rb') as csv_file:
            response = self.client.post(
                reverse('import-leads'),
                {'file': csv_file},
                format='multipart'
            )
            
        os.unlink(f.name)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        
    def test_unauthorized_access(self):
        """Test accessing protected endpoints without authentication"""
        # Test various endpoints without authentication
        endpoints = [
            reverse('leads'),
            reverse('process-leads'),
            reverse('generate-messages', kwargs={'lead_id': 1}),
            reverse('import-leads')
        ]
        
        for endpoint in endpoints:
            response = self.client.get(endpoint)
            self.assertEqual(
                response.status_code,
                status.HTTP_401_UNAUTHORIZED,
                f"Endpoint {endpoint} should require authentication"
            )
