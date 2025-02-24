from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse

# Create a simple view for the root URL
def welcome(request):
    return HttpResponse("Welcome to the API! Visit /api/hello/ for a response.")

urlpatterns = [
    path('', welcome, name='welcome'),
    path('admin/', admin.site.urls),
    path('api/', include('ai_lead_generation.api.urls')),  # Updated path
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
