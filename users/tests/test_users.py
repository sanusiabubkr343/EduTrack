import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from users.models import Profile
from users.serializers import (
    UserSerializer,
    UserRegistrationSerializer,
    ProfileSerializer,
    LoginUserSerializer,
)

User = get_user_model()


@pytest.mark.django_db
class TestUserViewSet:
    def test_user_registration(self, api_client):
        url = reverse('users:user-list')
        print(url)
        data = {
            'username': 'registeruser',
            'email': 'register@example.com',
            'password': 'registerpass123',
            'first_name': 'Register',
            'last_name': 'User',
            'role': User.STUDENT,
        }
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_201_CREATED
        assert User.objects.filter(email='register@example.com').exists()

    def test_user_login(self, api_client, user_factory):
        url = reverse('users:user-login')
        user = user_factory(password='testpass123')
        data = {'email': user.email, 'password': 'testpass123'}
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_200_OK
        assert 'tokens' in response.data['data']

    def test_user_list(self, mocked_authentication,api_client, user_factory):
        user_factory.create_batch(3)
        url = reverse('users:user-list')
        mocked_authentication(role="teacher")
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 4  # 3 created + admin user

    def test_user_detail(self, mocked_authentication,api_client, user_factory):
        user = user_factory()
        mocked_authentication(role="student")
        url = reverse('users:user-detail', kwargs={'pk': user.pk})
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['email'] == user.email

    def test_user_update(self, mocked_authentication,api_client, user_factory):

        auth_user = mocked_authentication(role="stuednt")
        url = reverse('users:user-detail', kwargs={'pk': auth_user.pk})
        data = {'username': 'Updated'}
        response = api_client.patch(url, data)
        assert response.status_code == status.HTTP_200_OK
        auth_user.refresh_from_db()
        assert auth_user.username == 'Updated'
