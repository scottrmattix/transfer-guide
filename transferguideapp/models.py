from django.db import models
from django.contrib.auth.models import User

#Model representing an external University that may or may not be accepted
class ExternalCollege(models.Model):
    college_name =  models.CharField(max_length=60)
    domestic_college = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.college_name}" 

#Model representing an external Course from an external university
class ExternalCourse(models.Model):
    college = models.ForeignKey(ExternalCollege, on_delete=models.CASCADE)
    mnemonic = models.CharField(max_length=20)
    course_number = models.CharField(max_length=20)
    course_name = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.mnemonic} ({self.course_number}): {self.course_name} from {self.college.college_name}"

#Model representing an internal UVA course
class InternalCourse(models.Model):
    id = models.BigAutoField(primary_key=True)
    mnemonic = models.CharField(max_length=30)
    #needs to support text characters for courses like 1000T
    course_number = models.CharField(max_length=30)
    course_name = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.mnemonic} ({self.course_number}): {self.course_name}"

#Model representing a courses transfer
class CourseTransfer(models.Model):
    external_course = models.ForeignKey(ExternalCourse, on_delete=models.CASCADE)
    internal_course = models.ForeignKey(InternalCourse, on_delete=models.CASCADE)
    accepted = models.BooleanField(default=False)

    def __str__(self):
        return f"External Course : {self.external_course} \n Internal Course: {self.internal_course} \n Accepted: {self.accepted}"

#model for favorited courses
class Favorites(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorite_items')
    course = models.ForeignKey(InternalCourse, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.course.id} {self.course.course_name} {self.course.course_number}"
