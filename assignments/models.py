from django.db import models
from django.core.exceptions import ValidationError
from apps.courses.models import Course
from apps.users.models import User


class Assignment(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='assignments')
    due_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} - {self.course.title}"

    def clean(self):
        if not self.course.teacher.is_teacher():
            raise ValidationError("Only course teachers can create assignments.")


class Submission(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='submissions')
    student = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)
    reviewed = models.BooleanField(default=False)
    grade = models.PositiveIntegerField(null=True, blank=True)

    class Meta:
        unique_together = ('assignment', 'student')

    def clean(self):
        if not self.student.is_student():
            raise ValidationError("Only students can submit assignments.")
        if not self.assignment.course.students.filter(id=self.student.id).exists():
            raise ValidationError("Student must be enrolled in the course to submit.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.student.username}'s submission for {self.assignment.title}"
