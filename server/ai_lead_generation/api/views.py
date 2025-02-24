from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth import get_user_model, authenticate
from rest_framework import generics, permissions
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework import status
from rest_framework import serializers
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
import pandas as pd
import os
from django.conf import settings
from .models import Lead

User = get_user_model()

# Create your views here.

def hello_api(request):
    """A simple API view that returns a greeting message."""
    return JsonResponse({"message": "Hello, World!"})

class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration."""
    class Meta:
        model = User
        fields = ['username', 'email', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User(**validated_data)
        user.set_password(validated_data['password'])  # Secure password hashing
        user.save()
        return user

class UserRegistrationView(generics.CreateAPIView):
    """API view for user registration."""
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]

class UserLoginSerializer(serializers.Serializer):
    """Serializer for user login."""
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True)

class UserLoginView(TokenObtainPairView):
    """API view for user login."""
    serializer_class = UserLoginSerializer
    permission_classes = [permissions.AllowAny]

class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'user': serializer.data,
                'tokens': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username', '')
        password = request.data.get('password', '')
        
        user = authenticate(username=username, password=password)
        
        if user is not None:
            serializer = TokenObtainPairSerializer(data=request.data)
            if serializer.is_valid():
                return Response(serializer.validated_data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({
            'error': 'Invalid username or password'
        }, status=status.HTTP_401_UNAUTHORIZED)

class RefreshTokenView(APIView):
    def post(self, request):
        refresh_token = request.data.get('refresh_token')
        
        try:
            refresh = RefreshToken(refresh_token)
            return Response({
                'access': str(refresh.access_token)
            })
        except Exception:
            return Response({
                'error': 'Invalid refresh token'
            }, status=status.HTTP_401_UNAUTHORIZED)

class LeadsView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        try:
            # Get the path to the CSV file
            csv_path = os.path.join(settings.BASE_DIR.parent, 'data', 'Crunchbase companies information.csv')
            
            # Read the CSV file
            df = pd.read_csv(csv_path)
            
            # Convert DataFrame to list of dictionaries
            leads = df.fillna('').to_dict('records')
            
            return Response({
                'status': 'success',
                'count': len(leads),
                'leads': leads
            })
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class ImportCrunchbaseLeadsView(APIView):
    """API view for importing Crunchbase company data as leads."""
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        try:
            # Clear existing leads before import
            Lead.objects.all().delete()
            
            # Read the CSV file
            csv_file_path = os.path.join(settings.BASE_DIR, 'data', 'Crunchbase companies information.csv')
            df = pd.read_csv(csv_file_path)
            
            imported_count = 0
            error_count = 0
            
            for _, row in df.iterrows():
                try:
                    company_name = str(row['name']).strip() if pd.notna(row['name']) else 'Unknown Company'
                    
                    # Extract industry from the industries JSON field
                    try:
                        industries = eval(row['industries']) if pd.notna(row['industries']) else []
                        industry = industries[0]['value'] if industries else 'Unknown'
                    except:
                        industry = 'Unknown'
                    
                    # Extract highest funding amount from featured_list JSON
                    highest_funding = 0
                    try:
                        featured_list = eval(row['featured_list']) if pd.notna(row['featured_list']) else []
                        for feature in featured_list:
                            if isinstance(feature, dict) and 'org_funding_total' in feature:
                                funding = feature['org_funding_total'].get('value_usd', 0)
                                highest_funding = max(highest_funding, funding)
                    except:
                        pass
                    
                    # Extract LinkedIn URL from social_media_links JSON
                    linkedin_url = None
                    try:
                        social_media_links = eval(row['social_media_links']) if pd.notna(row['social_media_links']) else []
                        linkedin_url = next((url for url in social_media_links if 'linkedin.com' in url.lower()), None)
                    except:
                        pass
                    
                    # Create lead object with better error handling for required fields
                    lead = Lead(
                        name=company_name,
                        company=company_name,
                        email=str(row['contact_email']).strip() if pd.notna(row['contact_email']) else 'unknown@example.com',
                        industry=industry,
                        company_size=str(row['num_employees']) if pd.notna(row['num_employees']) else '',
                        funding_amount=highest_funding,
                        position='Unknown Position',
                        created_by=request.user,
                        status='new',
                        metadata={
                            'website': str(row['website']).strip() if pd.notna(row['website']) else None,
                            'location': str(row['location']).strip() if pd.notna(row['location']) else None,
                            'founded_date': str(row['founded_date']).strip() if pd.notna(row['founded_date']) else None,
                            'company_type': str(row['company_type']).strip() if pd.notna(row['company_type']) else None,
                            'operating_status': str(row['operating_status']).strip() if pd.notna(row['operating_status']) else None,
                            'monthly_visits': str(row['monthly_visits']).strip() if pd.notna(row['monthly_visits']) else None,
                            'about': str(row['full_description']).strip() if pd.notna(row['full_description']) else None,
                            'linkedin_url': linkedin_url
                        }
                    )
                    lead.save()
                    imported_count += 1
                except Exception as e:
                    print(f"Error processing row for company {row.get('name', 'Unknown')}: {str(e)}")
                    error_count += 1
                    continue
            
            return Response({
                'status': 'success',
                'message': f'Successfully imported {imported_count} leads from Crunchbase data',
                'details': f'Errors: {error_count}, Total rows: {len(df)}'
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
