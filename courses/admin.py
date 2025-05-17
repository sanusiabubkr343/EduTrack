from django.contrib import admin

from courses.models import Enrollment, Course


# Register your models here.
admin.site.register(Course)
admin.site.register(Enrollment)
