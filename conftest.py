import copy
import pytest
from pytest_factoryboy import register
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from users.tests.factories import UserFactory, ProfileFactory
from rest_framework_simplejwt.authentication import JWTAuthentication

register(UserFactory)
register(ProfileFactory)

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def active_user():
    return UserFactory()


@pytest.fixture
def mocked_authentication(active_user, mocker):

    def _user(role):
        user_copy = active_user
        user_copy.role=role
        user_copy.save()

        mocker.patch.object(
            JWTAuthentication, "authenticate", return_value=(active_user, None)
        )
        return user_copy

    return _user
