from django.db import models
from django.contrib.auth.models import User

#Model representing an external University that may or may not be accepted
class ExternalCollege(models.Model):
    college_name = models.CharField(max_length=60)
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
        return f"{self.mnemonic} {self.course_number}: {self.course_name}"

    def get_model(self):
        # this string matches the 'externalcourse' view name
        return self._meta.model_name

    def get_transfers(self):
        return self.coursetransfer_set.filter(accepted=True)

    def get_equivalent(self):
        transfers = self.coursetransfer_set.filter(accepted=True)
        intIDs = transfers.values_list('internal_course', flat=True).distinct()
        return InternalCourse.objects.filter(id__in=intIDs).order_by('course_number')

    def get_users(self):
        transfers = self.get_transfers()
        faves = Favorites.objects.filter(transfer__in=transfers)
        userIDs = faves.values_list('user', flat=True).distinct()
        return User.objects.filter(id__in=userIDs)

    def college_name(self):
        return self.college.college_name

#Model representing an internal UVA course
class InternalCourse(models.Model):
    id = models.BigAutoField(primary_key=True)
    mnemonic = models.CharField(max_length=30)
    #needs to support text characters for courses like 1000T
    course_number = models.CharField(max_length=30)
    course_name = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.mnemonic} {self.course_number}: {self.course_name}"

    def get_model(self):
        # this string matches the 'internalcourse' view name
        return self._meta.model_name

    def get_transfers(self):
        return self.coursetransfer_set.filter(accepted=True)

    def get_equivalent(self):
        transfers = self.coursetransfer_set.filter(accepted=True)
        extIDs = transfers.values_list('external_course', flat=True).distinct()
        return ExternalCourse.objects.filter(id__in=extIDs).order_by('college__college_name', 'course_number')

    def get_users(self):
        transfers = self.get_transfers()
        faves = Favorites.objects.filter(transfer__in=transfers)
        userIDs = faves.values_list('user', flat=True).distinct()
        return User.objects.filter(id__in=userIDs)

    def college_name(self):
        return "University of Virginia"

#Model representing a courses transfer
class CourseTransfer(models.Model):
    external_course = models.ForeignKey(ExternalCourse, on_delete=models.CASCADE)
    internal_course = models.ForeignKey(InternalCourse, on_delete=models.CASCADE)
    accepted = models.BooleanField(default=False)

    def __str__(self):
        return f"External Course : {self.external_course} \n Internal Course: {self.internal_course} \n Accepted: {self.accepted}"

    def get_users(self):
        faves = self.favorites_set.all()
        userIDs = faves.values_list('user', flat=True).distinct()
        return User.objects.filter(id__in=userIDs)

#model for favorited courses
class Favorites(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorite_items', default=None)
    transfer = models.ForeignKey(CourseTransfer, on_delete=models.CASCADE, default=None)

    def __str__(self):
        return f"{self.transfer.internal_course.mnemonic} {self.transfer.internal_course.course_number}: {self.transfer.internal_course.course_name} = {self.transfer.external_course.college} {self.transfer.external_course.mnemonic} {self.transfer.external_course.course_number}: {self.transfer.external_course.course_name} "
