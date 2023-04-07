from django.contrib import admin
from .models import InternalCourse, ExternalCourse, ExternalCollege, CourseTransfer, Notification, TransferRequest

admin.site.register(InternalCourse)
admin.site.register(ExternalCourse)
admin.site.register(ExternalCollege)
admin.site.register(CourseTransfer)
admin.site.register(Notification)
admin.site.register(TransferRequest)
