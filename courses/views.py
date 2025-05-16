from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response

from core.permissions import IsCourseTeacher, IsEnrolledStudent, IsTeacher
from .models import Course, Enrollment
from .serializers import CourseSerializer, EnrollmentSerializer


class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer

    def get_permissions(self):
        if self.action in ['create']:
            permission_classes = [IsTeacher]
        elif self.action in ['update', 'partial_update', 'destroy']:
            permission_classes = [IsCourseTeacher]
        elif self.action in ['retrieve']:
            permission_classes = [IsEnrolledStudent | IsCourseTeacher]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        serializer.save(teacher=self.request.user)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def enroll(self, request, pk=None):
        course = self.get_object()
        if not request.user.is_student():
            return Response(
                {'detail': 'Only students can enroll in courses.'}, status=status.HTTP_403_FORBIDDEN
            )

        enrollment, created = Enrollment.objects.get_or_create(student=request.user, course=course)

        if created:
            serializer = EnrollmentSerializer(enrollment)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(
            {'detail': 'Already enrolled in this course.'}, status=status.HTTP_400_BAD_REQUEST
        )


class EnrollmentViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = EnrollmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Enrollment.objects.all()

    def get_queryset(self):
        if self.request.user.is_teacher():
            return self.queryset.filter(course__teacher=self.request.user)
        return self.queryset.filter(student=self.request.user)
