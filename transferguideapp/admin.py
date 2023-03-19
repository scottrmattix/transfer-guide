from django.contrib import admin
from .models import InternalCourse, ExternalCourse, ExternalCollege, CourseTransfer

admin.site.register(InternalCourse)
admin.site.register(ExternalCourse)
admin.site.register(ExternalCollege)
admin.site.register(CourseTransfer)
