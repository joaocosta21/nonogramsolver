from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('solver.urls')),  # API endpoint
    path('', include('solver.urls')),  # Add this line
]
