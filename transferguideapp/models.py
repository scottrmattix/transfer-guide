from django.db import models

#Model representing an external University that may or may not be accepted
class ExternalCollege(models.Model):
    college_name =  models.CharField(max_length=60)
    domestic_college = models.BooleanField(default=True)

#Model representing an external Course from an external university
class ExternalCourse(models.Model):
    college = models.ForeignKey(ExternalCollege, on_delete=models.CASCADE)
    mnemonic = models.CharField(max_length=30)
    course_number = models.CharField(max_length=30)
    course_name = models.CharField(max_length=60)

#Model representing an internal UVA course
class InternalCourse(models.Model):
    mnemonic = models.CharField(max_length=30)
    #needs to support text characters for courses like 1000T
    course_number = models.CharField(max_length=30)
    course_name = models.CharField(max_length=60)

#Model representing a courses transfer
class CourseTransfer(models.Model):
    external_course = models.ForeignKey(ExternalCourse, on_delete=models.CASCADE)
    internal_course = models.ForeignKey(InternalCourse, on_delete=models.CASCADE)
    accepted = models.BooleanField(default=False)
