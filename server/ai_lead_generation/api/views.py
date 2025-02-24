from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status, generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import get_user_model
from .models import Lead, Outreach
from .serializers import LeadSerializer, UserSerializer, OutreachSerializer
from .services import LeadAutomationService
import csv
import io
import logging

logger = logging.getLogger(__name__)
User = get_user_model()

class UserRegistrationView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = []  # Allow anyone to register

class LeadViewSet(viewsets.ModelViewSet):
    queryset = Lead.objects.all()
    serializer_class = LeadSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

class LeadDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Lead.objects.all()
    serializer_class = LeadSerializer
    permission_classes = [IsAuthenticated]

class ImportLeadsView(APIView):
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        if 'file' not in request.FILES:
            return Response({'error': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)

        csv_file = request.FILES['file']
        if not csv_file.name.endswith('.csv'):
            return Response({'error': 'File must be CSV format'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            decoded_file = csv_file.read().decode('utf-8')
            csv_data = csv.DictReader(io.StringIO(decoded_file))
            service = LeadAutomationService()
            result = service.import_leads_from_csv(csv_data, request.user)
            return Response(result, status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.error(f"Error importing leads: {str(e)}")
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class ProcessLeadsView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        try:
            service = LeadAutomationService()
            status_filter = request.query_params.get('status')
            industry_filter = request.query_params.get('industry')

            # Build filter dictionary
            filters = {}
            if status_filter:
                filters['status'] = status_filter
            if industry_filter:
                filters['industry'] = industry_filter

            result = service.process_all_leads(filters=filters)
            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error processing leads: {str(e)}")
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class GenerateMessagesView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, lead_id, *args, **kwargs):
        try:
            try:
                lead = get_object_or_404(Lead, id=lead_id)
            except:
                return Response({'error': f'Lead with id {lead_id} not found'}, status=status.HTTP_404_NOT_FOUND)
            
            service = LeadAutomationService()
            
            email_content = service.generate_email_content(lead)
            linkedin_content = service.generate_linkedin_message(lead)
            
            outreach = Outreach.objects.create(
                lead=lead,
                email_content=email_content,
                linkedin_content=linkedin_content
            )
            
            serializer = OutreachSerializer(outreach)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.error(f"Error generating messages for lead {lead_id}: {str(e)}")
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class TestMessageGenerationView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        try:
            lead_data = request.data
            lead = Lead(**lead_data)
            service = LeadAutomationService()
            
            email_content = service.generate_email_content(lead)
            linkedin_content = service.generate_linkedin_message(lead)
            
            return Response({
                'email_content': email_content,
                'linkedin_content': linkedin_content
            }, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error testing message generation: {str(e)}")
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
