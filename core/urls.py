from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

urlpatterns = [
    # Admin Panel
    path('admin/', admin.site.urls),
    # API Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    # API Endpoints
    path('api/auth/', include('users.urls')),
    path('api/courses/', include('courses.urls')),
    path('api/assignments/', include('assignments.urls')),
    # Health Check
    path('health/', include('health_check.urls')),
]
