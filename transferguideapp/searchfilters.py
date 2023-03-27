from .models import InternalCourse, ExternalCourse, ExternalCollege
import re
from django.db.models import Q

# The purpose of this file is to make the get_queryset() function in the CourseSearch view
# less cluttered. Calling search() allows us to filter courses by college, mnemonic
# number, and name.

def chooseCollege(inputCollege):
    aliases = ["", "UVA", "UNIVERSITY OF VIRGINIA"]
    if inputCollege in aliases:
        courses = InternalCourse.objects
    else:
        college = ExternalCollege.objects.filter(college_name=inputCollege).first()
        courses = ExternalCourse.objects.none() if (college is None) else ExternalCourse.objects.filter(college=college)
    return courses

def filterMnemonic(courses, inputMnemonic):
    return courses if (inputMnemonic == "") else courses.filter(mnemonic=inputMnemonic)

def filterNumber(courses, inputNumber):
    return courses if (inputNumber == "") else courses.filter(course_number__startswith=inputNumber)

def filterName(courses, inputName):
    if inputName == "":
        return courses

    words = re.sub(r"[,/&:.()?!]", " ", inputName).strip().split()
    for w in words:
        if w.isnumeric():
            n = int(w)
            if 0 < n < 6:
                r = ["I", "II", "III", "IV", "V"][n - 1]
                courses = courses.filter(Q(course_name__icontains=w) |
                                         Q(course_name__endswith=f" {r}") |
                                         Q(course_name__icontains=f" {r} ") |
                                         Q(course_name__icontains=f" {r}:"))
                continue
        courses = courses.filter(course_name__icontains=w)
    return courses


def search(inputCollege, inputMnemonic, inputNumber, inputName):
    if inputMnemonic + inputNumber + inputName == "":
        return InternalCourse.objects.none()
    courses = chooseCollege(inputCollege)
    courses = filterMnemonic(courses, inputMnemonic)
    courses = filterNumber(courses, inputNumber)
    courses = filterName(courses, inputName)
    return courses
