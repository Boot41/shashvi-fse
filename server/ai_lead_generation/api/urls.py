from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import (
    UserRegistrationView,
    LeadViewSet,
    LeadDetailView,
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
    path('leads/', LeadViewSet.as_view({'get': 'list', 'post': 'create'}), name='leads'),
    path('leads/<int:pk>/', LeadDetailView.as_view(), name='lead-detail'),
    path('leads/import/', ImportLeadsView.as_view(), name='import_leads'),
    path('leads/process/', ProcessLeadsView.as_view(), name='process_leads'),
    path('leads/<int:lead_id>/generate-messages/', GenerateMessagesView.as_view(), name='generate_messages'),
    path('leads/test-message/', TestMessageGenerationView.as_view(), name='test_message_generation'),
]
