from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from core.permissions import IsCourseTeacher, IsEnrolledStudent
from courses.models import Course
from .models import Assignment, Submission
from .serializers import (
    AssignmentSerializer,
    AssignmentCreateSerializer,
    SubmissionSerializer,
    SubmissionCreateSerializer,
    SubmissionGradeSerializer,
)
from drf_spectacular.utils import extend_schema
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend


@extend_schema(tags=["Assignment"])
class AssignmentViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows assignments to be viewed or edited.
    """

    queryset = Assignment.objects.all()
    permission_classes = [IsAuthenticated]
    # filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    # filterset_fields = ['course', 'submissions__reiewed']
    # search_fields = [
    #     'title',
    #     'description',
    # ]

    def get_serializer_class(self):
        if self.action == 'create':
            return AssignmentCreateSerializer
        return AssignmentSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAuthenticated, IsCourseTeacher]
        elif self.action in ['retrieve', 'list']:
            permission_classes = [IsAuthenticated, IsEnrolledStudent | IsCourseTeacher]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        user = self.request.user
        if user.is_teacher():
            return Assignment.objects.filter(course__teacher=user)
        return Assignment.objects.filter(course__students=user)

    def perform_create(self, serializer):
        course = get_object_or_404(Course, pk=self.request.data.get('course'))
        serializer.save(course=course)

    @action(detail=True, methods=['get'])
    def submissions(self, request, pk=None):
        """List all submissions for this assignment"""
        assignment = self.get_object()
        if not (
            assignment.course.teacher == request.user
            or request.user in assignment.course.students.all()
        ):
            return Response(status=status.HTTP_403_FORBIDDEN)

        submissions = assignment.submissions.all()
        serializer = SubmissionSerializer(submissions, many=True)
        return Response(serializer.data)


@extend_schema(tags=["Assignment"])

class SubmissionViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows assignment submissions to be viewed or edited.
    """

    queryset = Submission.objects.all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create':
            return SubmissionCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return SubmissionGradeSerializer
        return SubmissionSerializer

    def get_permissions(self):
        if self.action in ['create']:
            permission_classes = [IsAuthenticated, IsEnrolledStudent]
        elif self.action in ['update', 'partial_update']:
            permission_classes = [IsAuthenticated, IsCourseTeacher]
        elif self.action in ['retrieve', 'list']:
            permission_classes = [IsAuthenticated, IsEnrolledStudent | IsCourseTeacher]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        user = self.request.user
        if user.is_teacher():
            return Submission.objects.filter(assignment__course__teacher=user)
        return Submission.objects.filter(student=user)

    def create(self, request, *args, **kwargs):
        assignment_id = request.data.get('assignment')
        assignment = get_object_or_404(Assignment, pk=assignment_id)

        if not assignment.course.students.filter(id=request.user.id).exists():
            return Response(
                {'detail': 'You are not enrolled in this course.'}, status=status.HTTP_403_FORBIDDEN
            )

        if Submission.objects.filter(assignment=assignment, student=request.user).exists():
            return Response(
                {'detail': 'You have already submitted this assignment.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(assignment=assignment, student=request.user)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @action(detail=True, methods=['patch'])
    def review(self, request, pk=None):
        """Mark submission as reviewed and optionally add a grade"""
        submission = self.get_object()
        serializer = SubmissionGradeSerializer(submission, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
