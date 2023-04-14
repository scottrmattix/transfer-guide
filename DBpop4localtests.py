from transferguideapp.models import InternalCourse, ExternalCollege, ExternalCourse, Favorites, CourseTransfer, TransferRequest

ExternalCollege(college_name="Virginia Tech", domestic_college=True).save()
ExternalCourse(college=ExternalCollege.objects.first(), mnemonic="MATH", course_number = "0000", course_name="blah").save()
InternalCourse(id=1, mnemonic="MATH", course_number="1111", course_name="halb", credits=3).save()
CourseTransfer(external_course=ExternalCourse.objects.last(), internal_course=InternalCourse.objects.last()).save()
