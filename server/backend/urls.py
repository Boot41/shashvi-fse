from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse

# Create a simple view for the root URL
def welcome(request):
    return HttpResponse("Welcome to the API! Visit /api/hello/ for a response.")

urlpatterns = [
    path('', welcome, name='welcome'),
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),  # Ensure 'api.urls' does NOT redefine 'api/'
]
