from django.urls import path
from . import views
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    # Add your API endpoints here
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('leads/', views.LeadsView.as_view(), name='leads'),
    path('import-crunchbase-leads/', views.ImportCrunchbaseLeadsView.as_view(), name='import-crunchbase-leads'),
]
