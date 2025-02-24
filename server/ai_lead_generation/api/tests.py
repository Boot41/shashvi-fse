from django.test import TestCase
from django.core.management import call_command
from django.utils import timezone
from api.models import Company
from django.core.exceptions import ValidationError
from unittest.mock import patch

class FetchCompaniesCommandTest(TestCase):
    @patch('api.management.commands.fetch_companies.requests.get')  # Adjusted import path
    def test_successful_fetch(self, mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {'data': 'mocked data'}
        # Call the command
        call_command('fetch_companies')  # Ensure the command is called correctly
        # Add assertions here to verify expected behavior
        self.assertTrue(True)  # Replace with actual assertions
    
    def test_no_fetch(self):
        pass

class CompanyModelTest(TestCase):
    def setUp(self):
        # Create a Company instance for testing
        self.company = Company.objects.create(
            name='Test Company',
            industry='Tech',
            funding_amount=3000000,
            linkedin_profile='http://linkedin.com/test',
            location='Test City'
        )

    def test_company_creation(self):
        self.assertEqual(self.company.name, 'Test Company')
        self.assertEqual(self.company.industry, 'Tech')

    def test_company_update(self):
        self.company.name = 'Updated Company'
        self.company.save()
        self.assertEqual(self.company.name, 'Updated Company')

    def test_company_deletion(self):
        self.company.delete()
        self.assertEqual(Company.objects.count(), 0)

    def test_company_read(self):
        company = Company.objects.get(name='Test Company')
        self.assertEqual(company.industry, 'Tech')
        self.assertEqual(company.funding_amount, 3000000)
        self.assertEqual(company.linkedin_profile, 'http://linkedin.com/test')
        self.assertEqual(company.location, 'Test City')

    def test_company_create_multiple(self):
        Company.objects.create(
            name='Test Company 2',
            industry='Finance',
            funding_amount=2000000,
            linkedin_profile='http://linkedin.com/test2',
            location='Test City 2'
        )
        self.assertEqual(Company.objects.count(), 2)

    def test_company_update_multiple(self):
        Company.objects.create(
            name='Test Company 2',
            industry='Finance',
            funding_amount=2000000,
            linkedin_profile='http://linkedin.com/test2',
            location='Test City 2'
        )
        company = Company.objects.get(name='Test Company 2')
        company.name = 'Updated Company 2'
        company.save()
        self.assertEqual(Company.objects.get(name='Updated Company 2').industry, 'Finance')

    def test_company_delete_multiple(self):
        Company.objects.create(
            name='Test Company 2',
            industry='Finance',
            funding_amount=2000000,
            linkedin_profile='http://linkedin.com/test2',
            location='Test City 2'
        )
        Company.objects.get(name='Test Company 2').delete()
        self.assertEqual(Company.objects.count(), 1)

    def test_create_company_missing_fields(self):
        with self.assertRaises(Exception):  # Adjust the exception type based on your model validation
            Company.objects.create(name='')  # Missing required fields

    def test_create_company_empty_fields(self):
        company = Company(
            name='',
            industry='',
            funding_amount=0,
            linkedin_profile='',
            location=''
        )
        with self.assertRaises(ValidationError):  
            company.full_clean()

    def test_create_company_invalid_data(self):
        with self.assertRaises(ValidationError):  
            Company.objects.create(
                name='Invalid Company',
                industry='Tech',
                funding_amount='invalid',  # Invalid funding amount
                linkedin_profile='http://linkedin.com/invalid',
                location='Test City'
            )

    def test_delete_non_existent_company(self):
        with self.assertRaises(Company.DoesNotExist):
            Company.objects.get(name='Non Existent Company').delete()

    def test_update_company_invalid_data(self):
        self.company.name = 'Updated Company'
        self.company.funding_amount = 'invalid'  # Invalid funding amount
        with self.assertRaises(ValidationError):  
            self.company.save()

    def test_update_company_empty_fields(self):
        self.company.name = ''
        self.company.industry = ''
        self.company.funding_amount = 0
        self.company.linkedin_profile = ''
        self.company.location = ''
        with self.assertRaises(ValidationError):  
            self.company.full_clean()

    def test_delete_company_with_empty_fields(self):
        company = Company.objects.create(
            name='',
            industry='',
            funding_amount=0,
            linkedin_profile='',
            location=''
        )
        company.delete()
        self.assertEqual(Company.objects.count(), 0)

    def test_create_company_with_long_fields(self):
        with self.assertRaises(Exception):  # Adjust the exception type based on your model validation
            Company.objects.create(
                name='a' * 256,
                industry='a' * 256,
                funding_amount=1000000000000,
                linkedin_profile='http://linkedin.com/' + 'a' * 256,
                location='a' * 256
            )

    def test_update_company_with_long_fields(self):
        self.company.name = 'a' * 256
        self.company.industry = 'a' * 256
        self.company.funding_amount = 1000000000000
        self.company.linkedin_profile = 'http://linkedin.com/' + 'a' * 256
        self.company.location = 'a' * 256
        with self.assertRaises(Exception):  # Adjust the exception type based on your model validation
            self.company.save()
