from rest_framework.permissions import BasePermission


class IsTeacher(BasePermission):
    message = "You must be a logged-in teacher to access this resource."

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_teacher()


class IsCourseTeacher(BasePermission):
    message = "You must be the teacher of this course to access this resource."

    def has_object_permission(self, request, view, obj):
        return obj.teacher == request.user


class IsEnrolledStudent(BasePermission):
    message = "You must be an enrolled student in this course to access this resource."

    def has_object_permission(self, request, view, obj):
        return request.user.is_student() and obj.students.filter(id=request.user.id).exists()
