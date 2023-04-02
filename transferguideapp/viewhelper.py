from django.shortcuts import redirect, render, get_object_or_404
from .models import ExternalCourse, InternalCourse, ExternalCollege, CourseTransfer, Favorites
from django.db.models import Q

# helper methods for views

def update_favorites_helper(user, pid, sid, type):
    if type == "internalcourse":
        q = Q(internal_course=pid, external_course=sid)
        response = redirect(type, pk=pid)

    elif type == "externalcourse":
        q = Q(internal_course=sid, external_course=pid)
        response = redirect(type, pk=pid)

    else:
        q = Q(internal_course=sid, external_course=pid)
        response = redirect('favorites')

    transfer = CourseTransfer.objects.filter(q).first()
    if transfer and user:
        try:
            Favorites.objects.get(user=user, transfer=transfer).delete()
        except Favorites.DoesNotExist:
            Favorites.objects.create(user=user, transfer=transfer)

    return response


def update_course_helper(collegeID, mnemonic, number, name, courseID):
    # Load External Course
    try:
        college = ExternalCollege.objects.get(id=collegeID)
        courses = ExternalCourse.objects
        vals = {'college': college, 'mnemonic': mnemonic, 'course_number': number,
                'course_name': name}

    # Load Internal Course
    except ExternalCollege.DoesNotExist:
        courses = InternalCourse.objects
        vals = {'mnemonic': mnemonic, 'course_number': number, 'course_name': name}

    # Update / Add Course
    c, wasCreated = courses.filter(id=courseID).update_or_create(defaults=vals)

    # Go to correct view
    return redirect(c.get_model(), pk=c.id)


def request_course_helper(collegeID, mnemonic, number, name, courseID):
    # Get College
    try:
        college = ExternalCollege.objects.get(id=collegeID)

    # Return to Request Form if Invalid College
    except ExternalCollege.DoesNotExist:
        return redirect("courseRequest", pk=courseID)

    # Update or Create External Course
    existing_external = ExternalCourse.objects.filter(college=college, mnemonic=mnemonic, course_number=number)
    external_vals = {'college': college, 'mnemonic': mnemonic, 'course_number': number, 'course_name': name}
    external, externalWasCreated = existing_external.update_or_create(defaults=external_vals)

    # Get Internal Course
    internal = InternalCourse.objects.get(id=courseID)

    # Update or Create CourseTransfer
    transfer_vals = {'internal_course': internal, 'external_course': external, 'accepted': True}
    existing_transfer = CourseTransfer.objects.filter(internal_course=internal, external_course=external)
    transfer, transferWasCreated = existing_transfer.update_or_create(defaults=transfer_vals)

    return redirect("internalcourse", pk=courseID)

