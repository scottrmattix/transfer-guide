from django.db import models

#Model representing an external University that may or may not be accepted
class ExternalCollege(models.Model):
    college_name = models.CharField(max_length=60)
    domestic_college = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.college_name}"

    def get_fields(self):
        return [(field.name, field.value_to_string(self)) for field in ExternalCollege._meta.fields]

#Model representing an external Course from an external university
class ExternalCourse(models.Model):
    college = models.ForeignKey(ExternalCollege, on_delete=models.CASCADE)
    mnemonic = models.CharField(max_length=20)
    course_number = models.CharField(max_length=20)
    course_name = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.mnemonic} ({self.course_number}): {self.course_name} from {self.college.college_name}"

    def get_model(self):
        return self._meta.model_name

    def get_fields(self):
        return [(field.name, field.value_to_string(self)) for field in ExternalCourse._meta.fields]

    def get_equivalent(self):
        transfers = CourseTransfer.objects.all().filter(accepted=True, external_course=self)
        internalIDs = transfers.values_list('internal_course', flat=True)
        internals = InternalCourse.objects.all().filter(id__in=internalIDs)
        return internals

#Model representing an internal UVA course
class InternalCourse(models.Model):
    id = models.BigAutoField(primary_key=True)
    mnemonic = models.CharField(max_length=30)
    #needs to support text characters for courses like 1000T
    course_number = models.CharField(max_length=30)
    course_name = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.mnemonic} ({self.course_number}): {self.course_name}"

    def get_model(self):
        return self._meta.model_name

    def get_fields(self):
        return [(field.name, field.value_to_string(self)) for field in InternalCourse._meta.fields]

    def get_equivalent(self):
        transfers = CourseTransfer.objects.all().filter(accepted=True, internal_course=self)
        externalIDs = transfers.values_list('external_course', flat=True)
        externals = ExternalCourse.objects.all().filter(id__in=externalIDs)
        return externals

#Model representing a courses transfer
class CourseTransfer(models.Model):
    external_course = models.ForeignKey(ExternalCourse, on_delete=models.CASCADE)
    internal_course = models.ForeignKey(InternalCourse, on_delete=models.CASCADE)
    accepted = models.BooleanField(default=False)

    def __str__(self):
        return f"External Course : {self.external_course} \n Internal Course: {self.internal_course} \n Accepted: {self.accepted}"
