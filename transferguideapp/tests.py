from django.test import TestCase
from .models import CourseTransfer, ExternalCourse, InternalCourse, ExternalCollege

# This test is just to verify that CI is working
#class TestFail(TestCase):
#    def test_fail(self):
#        self.assertTrue(False)


def clean_data():
    CourseTransfer.objects.all().delete()
    ExternalCourse.objects.all().delete()
    ExternalCollege.objects.all().delete()
    InternalCourse.objects.all().delete()


class TestModelCreation(TestCase):
    def test_course_transfer_create(self):
        inter_course = InternalCourse(course_name = "Advanced Software Development Techniques", course_number = "3240" , mnemonic = "CS")
        inter_course.save()
        exter_college = ExternalCollege(college_name = "Piedmont Valley Community College")
        exter_college.save()
        exter_course = ExternalCourse(course_name = "Software Development", course_number = "123", mnemonic = "CS", college = ExternalCollege.objects.get(college_name = "Piedmont Valley Community College"))
        exter_course.save()
        course_transfer = CourseTransfer(internal_course = InternalCourse.objects.get(course_number = "3240", mnemonic="CS"), external_course = ExternalCourse.objects.get(course_number = "123", mnemonic="CS"))
        course_transfer.save()
        self.assertEqual(str(course_transfer), str(CourseTransfer.objects.get(external_course = ExternalCourse.objects.get(course_number = "123", mnemonic = "CS"))))
        clean_data()



    def test_external_course_create(self):
        exter_college = ExternalCollege(college_name = "Piedmont Valley Community College")
        exter_college.save()
        exter_course = ExternalCourse(course_name = "Software Development", course_number = "123", mnemonic = "CS", college = ExternalCollege.objects.get(college_name = "Piedmont Valley Community College"))
        exter_course.save()
        self.assertEqual(str(exter_course), str(ExternalCourse.objects.get(course_number="123", mnemonic = "CS")))
        clean_data()


    def test_internal_course_create(self):
        inter_course = InternalCourse(course_name = "Advanced Software Development Techniques", course_number = "3240" , mnemonic = "CS")
        inter_course.save()
        self.assertEqual(str(inter_course), str(InternalCourse.objects.get(course_number="3240", mnemonic = "CS")))
        clean_data()



    def test_external_college_create(self):
        exter_college = ExternalCollege(college_name = "Piedmont Valley Community College")
        exter_college.save()
        self.assertEqual(str(exter_college), str(ExternalCollege.objects.get(college_name = "Piedmont Valley Community College")))
        clean_data()
