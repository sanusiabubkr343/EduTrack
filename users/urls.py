from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import UserViewSet, ProfileViewSet

app_name = "users"


router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'profiles', ProfileViewSet, basename='profile')

urlpatterns = [
    path('', include(router.urls)),
]
