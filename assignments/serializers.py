from rest_framework import serializers

from courses.serializers import CourseSerializer
from users.serializers import UserSerializer
from .models import Assignment, Submission



class AssignmentSerializer(serializers.ModelSerializer):
    course = CourseSerializer(read_only=True)
    has_submitted = serializers.SerializerMethodField()

    class Meta:
        model = Assignment
        fields = [
            'id',
            'title',
            'description',
            'course',
            'due_date',
            'created_at',
            'updated_at',
            'has_submitted',
        ]
        read_only_fields = ['created_at', 'updated_at']

    def get_has_submitted(self, obj)->bool:
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            return obj.submissions.filter(student=request.user).exists()
        return False


class AssignmentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assignment
        fields = ['title', 'description', 'course', 'due_date']

    def validate_course(self, value):
        request = self.context.get('request')
        if value.teacher != request.user:
            raise serializers.ValidationError(
                "You can only create assignments for your own courses"
            )
        return value


class SubmissionSerializer(serializers.ModelSerializer):
    student = UserSerializer(read_only=True)
    assignment = AssignmentSerializer(read_only=True)

    class Meta:
        model = Submission
        fields = ['id', 'assignment', 'student', 'content', 'submitted_at', 'reviewed', 'grade']
        read_only_fields = ['student', 'assignment', 'submitted_at']

    def validate(self, data):
        request = self.context.get('request')
        assignment = self.context.get('assignment')

        if Submission.objects.filter(assignment=assignment, student=request.user).exists():
            raise serializers.ValidationError("You have already submitted this assignment")

        return data


class SubmissionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Submission
        fields = ['content']

    def create(self, validated_data):
        request = self.context.get('request')
        assignment = self.context.get('assignment')

        if not assignment.course.students.filter(id=request.user.id).exists():
            raise serializers.ValidationError("You are not enrolled in this course")

        return Submission.objects.create(
            assignment=assignment, student=request.user, **validated_data
        )


class SubmissionGradeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Submission
        fields = ['reviewed', 'grade']
