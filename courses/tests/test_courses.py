import pytest
from django.urls import reverse
from rest_framework import status
from courses.models import Course, Enrollment
from users.models import User

pytestmark = pytest.mark.django_db


class TestCourseViewSet:
    def test_list_courses(self, api_client, mocked_authentication):
        mocked_authentication(role="student")
        url = reverse('courses:course-list')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK

    def test_create_course_as_teacher(self, api_client, mocked_authentication):
        teacher = mocked_authentication(role='teacher')
        api_client.force_authenticate(user=teacher)
        url = reverse('courses:course-list')
        data = {'title': 'Test Course', 'description': 'Test Description'}
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_201_CREATED
        assert Course.objects.count() == 1
        assert Course.objects.first().teacher == teacher

    def test_create_course_as_student_fails(self, api_client, mocked_authentication):
        student = mocked_authentication(role='student')
        api_client.force_authenticate(user=student)
        url = reverse('courses:course-list')
        data = {'title': 'Test Course', 'description': 'Test Description'}
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_retrieve_course_as_teacher(self, api_client, mocked_authentication):
        teacher = mocked_authentication(role='teacher')
        course = Course.objects.create(
            title="Test Course", description="Test Description", teacher=teacher
        )
        api_client.force_authenticate(user=teacher)
        url = reverse('courses:course-detail', kwargs={'pk': course.id})
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['title'] == course.title

    def test_retrieve_course_as_enrolled_student(self, api_client, mocked_authentication):
        teacher = mocked_authentication(role='teacher')
        course = Course.objects.create(
            title="Test Course", description="Test Description", teacher=teacher
        )
        student = mocked_authentication(role='student')
        course.students.add(student)
        api_client.force_authenticate(user=student)
        url = reverse('courses:course-detail', kwargs={'pk': course.id})
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK

    def test_delete_course_as_teacher(self, api_client, mocked_authentication):
        teacher = mocked_authentication(role='teacher')
        course = Course.objects.create(
            title="Test Course", description="Test Description", teacher=teacher
        )
        api_client.force_authenticate(user=teacher)
        url = reverse('courses:course-detail', kwargs={'pk': course.id})
        response = api_client.delete(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert Course.objects.count() == 0

    def test_enroll_as_student(self, api_client, mocked_authentication):
        teacher = mocked_authentication(role='teacher')
        course = Course.objects.create(
            title="Test Course", description="Test Description", teacher=teacher
        )
        student = mocked_authentication(role='student')
        api_client.force_authenticate(user=student)
        url = reverse('courses:course-enroll', kwargs={'pk': course.id})
        response = api_client.post(url)
        assert response.status_code == status.HTTP_201_CREATED
        assert course.students.filter(id=student.id).exists()
        assert Enrollment.objects.filter(student=student, course=course).exists()

    def test_enroll_as_teacher_fails(self, api_client, mocked_authentication):
        teacher = mocked_authentication(role='teacher')
        course = Course.objects.create(
            title="Test Course", description="Test Description", teacher=teacher
        )
        api_client.force_authenticate(user=teacher)
        url = reverse('courses:course-enroll', kwargs={'pk': course.id})
        response = api_client.post(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_enroll_twice_fails(self, api_client, mocked_authentication):
        teacher = mocked_authentication(role='teacher')
        course = Course.objects.create(
            title="Test Course", description="Test Description", teacher=teacher
        )
        student = mocked_authentication(role='student')
        course.students.add(student)
        Enrollment.objects.create(student=student, course=course)
        api_client.force_authenticate(user=student)
        url = reverse('courses:course-enroll', kwargs={'pk': course.id})
        response = api_client.post(url)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_unenroll_as_student(self, api_client, mocked_authentication):
        teacher = mocked_authentication(role='teacher')
        course = Course.objects.create(
            title="Test Course", description="Test Description", teacher=teacher
        )
        student = mocked_authentication(role='student')
        course.students.add(student)
        Enrollment.objects.create(student=student, course=course)
        api_client.force_authenticate(user=student)
        url = reverse('courses:course-unenroll', kwargs={'pk': course.id})
        response = api_client.post(url)
        assert response.status_code == status.HTTP_200_OK
        assert not course.students.filter(id=student.id).exists()
        assert not Enrollment.objects.filter(student=student, course=course).exists()

    def test_unenroll_when_not_enrolled_fails(self, api_client, mocked_authentication):
        teacher = mocked_authentication(role='teacher')
        course = Course.objects.create(
            title="Test Course", description="Test Description", teacher=teacher
        )
        student = mocked_authentication(role='student')
        api_client.force_authenticate(user=student)
        url = reverse('courses:course-unenroll', kwargs={'pk': course.id})
        response = api_client.post(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestEnrollmentViewSet:
    def test_list_enrollments_as_teacher(self, api_client, mocked_authentication):
        teacher = mocked_authentication(role='teacher')
        course = Course.objects.create(
            title="Test Course", description="Test Description", teacher=teacher
        )
        student = mocked_authentication(role='student')

        enrollment = Enrollment.objects.create(student=student, course=course)
        api_client.force_authenticate(user=teacher)
        url = reverse('courses:enrollment-list')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["count"] == 1

    def test_list_enrollments_as_student(self, api_client, mocked_authentication):
        teacher = mocked_authentication(role='teacher')
        course = Course.objects.create(
            title="Test Course", description="Test Description", teacher=teacher
        )
        student = mocked_authentication(role='student')

        enrollment = Enrollment.objects.create(student=student, course=course)
        api_client.force_authenticate(user=student)
        url = reverse('courses:enrollment-list')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK

    def test_retrieve_enrollment_as_teacher(self, api_client, mocked_authentication):
        teacher = mocked_authentication(role='teacher')
        course = Course.objects.create(
            title="Test Course", description="Test Description", teacher=teacher
        )
        student = mocked_authentication(role='student')

        enrollment = Enrollment.objects.create(student=student, course=course)
        api_client.force_authenticate(user=teacher)
        url = reverse('courses:enrollment-detail', kwargs={'pk': enrollment.id})
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == enrollment.id

    def test_retrieve_enrollment_as_student(self, api_client, mocked_authentication):
        teacher = mocked_authentication(role='teacher')
        course = Course.objects.create(
            title="Test Course", description="Test Description", teacher=teacher
        )
        student = mocked_authentication(role='student')

        enrollment = Enrollment.objects.create(student=student, course=course)
        api_client.force_authenticate(user=student)
        url = reverse('courses:enrollment-detail', kwargs={'pk': enrollment.id})
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == enrollment.id
