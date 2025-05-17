import factory
from factory.django import DjangoModelFactory
from django.contrib.auth import get_user_model
from courses.models import Course, Enrollment
from users.tests.factories import UserFactory

User = get_user_model()


class CourseFactory(DjangoModelFactory):
    class Meta:
        model = Course

    title = factory.Faker('sentence', nb_words=4)
    description = factory.Faker('paragraph')
    teacher = factory.SubFactory(UserFactory)


class EnrollmentFactory(DjangoModelFactory):
    class Meta:
        model = Enrollment

    student = factory.SubFactory(UserFactory)
    course = factory.SubFactory(CourseFactory)
