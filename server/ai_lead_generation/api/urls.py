from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import (
    UserRegistrationView,
    LeadListCreateView,
    ImportLeadsView,
    ProcessLeadsView,
    GenerateMessagesView,
    TestMessageGenerationView
)

urlpatterns = [
    # Authentication endpoints
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('register/', UserRegistrationView.as_view(), name='register'),
    
    # Lead management endpoints
    path('leads/', LeadListCreateView.as_view(), name='lead-list-create'),
    path('leads/import/', ImportLeadsView.as_view(), name='import-leads'),
    path('leads/process/', ProcessLeadsView.as_view(), name='process-leads'),
    path('leads/generate-messages/', GenerateMessagesView.as_view(), name='generate-messages'),
    path('leads/test-message/', TestMessageGenerationView.as_view(), name='test_message_generation'),
]
