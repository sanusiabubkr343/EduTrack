from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import get_user_model

from core.permissions import IsAdminOrSelf
from .models import Profile
from .serializers import UserSerializer, UserRegistrationSerializer, ProfileSerializer

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """

    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrSelf]

    def get_serializer_class(self):
        if self.action == 'create':
            return UserRegistrationSerializer
        return UserSerializer

    def get_permissions(self):
        if self.action == 'create':
            return [permissions.AllowAny()]  # Allow anyone to register
        return super().get_permissions()

    @action(detail=False, methods=['get'])
    def me(self, request):
        """
        Retrieve the current authenticated user's data
        """
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(detail=False, methods=['put', 'patch'])
    def update_me(self, request):
        """
        Update the current authenticated user's data
        """
        user = request.user
        serializer = self.get_serializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def set_password(self, request, pk=None):
        """
        Change a user's password
        """
        user = self.get_object()
        if not request.user.is_staff and user != request.user:
            return Response(
                {'detail': 'You can only change your own password.'},
                status=status.HTTP_403_FORBIDDEN,
            )

        password = request.data.get('password')
        if not password:
            return Response(
                {'password': ['This field is required.']}, status=status.HTTP_400_BAD_REQUEST
            )

        user.set_password(password)
        user.save()
        return Response({'status': 'password set'})


class ProfileViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows profiles to be viewed or edited.
    """

    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrSelf]

    def get_queryset(self):
        if self.request.user.is_staff:
            return Profile.objects.all()
        return Profile.objects.filter(user=self.request.user)

    @action(detail=False, methods=['get', 'put', 'patch'])
    def me(self, request):
        """
        Retrieve or update the current authenticated user's profile
        """
        profile = request.user.profile
        if request.method in ['PUT', 'PATCH']:
            serializer = self.get_serializer(profile, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
        else:
            serializer = self.get_serializer(profile)
            return Response(serializer.data)
