from .models import InternalCourse, ExternalCourse, ExternalCollege
import re
from django.db.models import Q

# The purpose of this file is to make the get_queryset() function in the CourseSearch view
# less cluttered. Calling search() allows us to filter courses by college, mnemonic
# number, and name.

def set_user_college(request, college):
    if college:
        request.session["user_college_id"] = college.id
        request.session["user_college"] = college.college_name

def filterCollege(inputCollege):
    college = ExternalCollege.objects.filter(college_name__iexact=inputCollege).first()
    aliases = ["", "UVA", "UNIVERSITY OF VIRGINIA"]
    if inputCollege.upper() in aliases:
        courses = InternalCourse.objects
        q = Q()
    else:
        courses = ExternalCourse.objects
        q = Q(college=college)
    return q, courses, college

def filterMnemonic(inputMnemonic):
    return Q(mnemonic=inputMnemonic) if inputMnemonic else Q()

def filterNumber(inputNumber):
    return Q(course_number__startswith=inputNumber) if inputNumber else Q()

def filterName(inputName):
    q = Q()
    cleanName = re.sub(r"[,/&:.()?!'-]", " ", inputName).strip()
    if not cleanName:
        return q
    for word in cleanName.split():
        if word.isnumeric():
            n = int(word)
            if 0 < n < 6:
                r = ["I", "II", "III", "IV", "V"][n - 1]
                qU = Q(course_name__icontains=word) | Q(course_name__endswith=f" {r}") | Q(course_name__icontains=f" {r} ")
                q = q & qU
        else:
            q = q & Q(course_name__icontains=word)
    return q


def search(request):
    inputCollege = request.session["search"]["college"]
    inputMnemonic = request.session["search"]["mnemonic"]
    inputNumber = request.session["search"]["number"]
    inputName = request.session["search"]["name"]

    q1, courses, college = filterCollege(inputCollege)
    q2 = filterMnemonic(inputMnemonic)
    q3 = filterNumber(inputNumber)
    q4 = filterName(inputName)

    set_user_college(request, college)

    # WARNING: this is not true comparison, just the string representation
    # this is only good to check if they're empty
    if q1 == q2 == q3 == q4:
        return courses.none()
    else:
        return courses.filter(q1 & q2 & q3 & q4)

def debug(request):
    for key, value in request.session.items():
        print('{} => {}'.format(key, value))
