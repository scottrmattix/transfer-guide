# this file is for scripts for testing to use in the django console. its not part of production. 
# exec(open('script.py').read()) 
from transferguideapp.models import ExternalCourse, ExternalCollege
vt = ExternalCollege(college_name = "Virginia Tech", domestic_college = False)
vt.save()
vtcalc1 = ExternalCourse(college = vt, mnemonic = "math", course_number = "1234", course_name = "calculus I")
vtcalc1.save()
print(ExternalCollege.objects.all())
print(ExternalCourse.objects.all())
ExternalCourse.objects.all().delete()
ExternalCollege.objects.all().delete()
ExternalCourse.objects.all().delete()
ExternalCollege.objects.all().delete()