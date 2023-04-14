from transferguideapp.models import ExternalCollege, ExternalCourse, InternalCourse, CourseTransfer, TimeStampMixin, Favorites, TransferRequest

vt = ExternalCollege(college_name = "Virginia Tech", domestic_college = True)
vt.save()

ec = ExternalCourse(college = vt, mnemonic = "MATH", course_number = 1000, course_name = "algebro")
ec.save()
ic = InternalCourse(id=1, mnemonic = "MATH", course_number = 2000, course_name = "algebrah", credits = 3)
ic.save()

CourseTransfer(external_course = ec, internal_course = ic, accepted = True).save()
