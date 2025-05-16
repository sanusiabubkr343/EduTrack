from rest_framework import serializers

from users.serializers import UserSerializer
from .models import Course, Enrollment


class CourseSerializer(serializers.ModelSerializer):
    teacher = UserSerializer(read_only=True)
    students = UserSerializer(many=True, read_only=True)
    is_teacher = serializers.SerializerMethodField()
    is_enrolled = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = [
            'id',
            'title',
            'description',
            'teacher',
            'students',
            'created_at',
            'updated_at',
            'is_teacher',
            'is_enrolled',
        ]
        read_only_fields = ['teacher', 'students', 'created_at', 'updated_at']

    def get_is_teacher(self, obj)->bool:
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            return obj.teacher == request.user
        return False

    def get_is_enrolled(self, obj)->bool:
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            return obj.students.filter(id=request.user.id).exists()
        return False


class EnrollmentSerializer(serializers.ModelSerializer):
    student = UserSerializer(read_only=True)
    course = CourseSerializer(read_only=True)

    class Meta:
        model = Enrollment
        fields = ['id', 'student', 'course', 'enrolled_at']
        read_only_fields = ['enrolled_at']


class CourseCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ['title', 'description']

    def create(self, validated_data):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            return Course.objects.create(teacher=request.user, **validated_data)
        raise serializers.ValidationError("User not found in request context")
