from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import get_user_model

from core.permissions import IsAdminOrSelf
from users.utils import create_jwt_pair_for_user
from .models import Profile
from .serializers import (
    LoginUserSerializer,
    UserSerializer,
    UserRegistrationSerializer,
    ProfileSerializer,
)
from drf_spectacular.utils import extend_schema
from django.contrib.auth import authenticate
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.parsers import MultiPartParser
from rest_framework import mixins


User = get_user_model()


@extend_schema(tags=["Users"])
class UserViewSet(viewsets.ModelViewSet):

    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsAdminOrSelf]

    def get_serializer_class(self):
        if self.action == 'create':
            self.parser_classes = [MultiPartParser]
            return UserRegistrationSerializer
        return self.serializer_class

    def get_permissions(self):
        if self.action == 'create':
            return [AllowAny()]  # Allow anyone to register
        return super().get_permissions()

    @action(
        methods=['POST'],
        detail=False,
        permission_classes=[AllowAny],
        serializer_class=LoginUserSerializer,
        url_path='login',
    )
    def login(self, request):
        "login a user"
        serializer = LoginUserSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data["email"]
            password = serializer.validated_data["password"]
            user = authenticate(email=email, password=password)
            if user is not None:
                tokens = create_jwt_pair_for_user(user)
                serializer.validated_data["tokens"] = tokens
                serializer.validated_data["user_data"] = UserSerializer(instance=user).data

                response = {"message": "Login Successful", "data": serializer.data}
                return Response(data=response, status=status.HTTP_200_OK)
            return Response(
                data={"message": "Invalid email or password"},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProfileViewSet(viewsets.ModelViewSet):

    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrSelf]

    def get_queryset(self):
        user_role = self.request.user.role
        if user_role == "teacher":
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
