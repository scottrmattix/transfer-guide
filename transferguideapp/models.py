from django.db import models

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

# UVA Course Model
class Course(models.Model):
    subject = models.CharField(max_length=200, default="a")
    catalog_nbr = models.CharField(max_length=200, default="b")
    class_section = models.CharField(max_length=200, default="c")
    descr = models.CharField(max_length=200, default="d")

    @classmethod
    def create(cls, subject, catalog_nbr, class_section, descr):
        course = cls(subject=subject,
                     catalog_nbr=catalog_nbr,
                     class_section=class_section,
                     descr=descr)
        return course

    def __str__(self):
        s = f"{self.subject} {self.catalog_nbr}-{self.class_section}: {self.descr}"
        return s
