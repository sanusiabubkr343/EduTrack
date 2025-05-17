import factory
from django.contrib.auth import get_user_model
from users.models import Profile
from faker import Faker

fake = Faker()
User = get_user_model()


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.LazyAttribute(lambda _: fake.user_name())
    email = factory.LazyAttribute(lambda _: fake.email())
    first_name = factory.LazyAttribute(lambda _: fake.first_name())
    last_name = factory.LazyAttribute(lambda _: fake.last_name())
    password = factory.PostGenerationMethodCall('set_password', 'testpass123')
    role = factory.Iterator([User.TEACHER, User.STUDENT])

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        """Override the default _create to use the custom manager."""
        password = kwargs.pop('password', None)
        user = super()._create(model_class, *args, **kwargs)
        if password:
            user.set_password(password)
            user.save()
        return user


class ProfileFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Profile

    user = factory.SubFactory(UserFactory)
    bio = factory.LazyAttribute(lambda _: fake.text())
    institution = factory.LazyAttribute(lambda _: fake.company())
