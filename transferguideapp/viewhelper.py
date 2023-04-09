from django.shortcuts import redirect, render, get_object_or_404
from .models import ExternalCourse, InternalCourse, ExternalCollege, CourseTransfer, Favorites, TransferRequest
from django.db.models import Q
from django.contrib import messages
import re
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

        check = Q(college=college, mnemonic=mnemonic, course_number=number) & ~Q(id=courseID)
        errorURL = "externalcourseUpdate"

    # Load Internal Course
    except ExternalCollege.DoesNotExist:
        courses = InternalCourse.objects
        vals = {'mnemonic': mnemonic, 'course_number': number, 'course_name': name}
        check = Q(mnemonic=mnemonic, course_number=number) & ~Q(id=courseID)
        errorURL = "internalcourseUpdate"

    # Check if new/edited course is a duplicate
    if courses.filter(check):
        error = "ERROR: another course already exists with this Mnemonic and Number at this college."
        # Go back to UpdateCourses view with error
        if courseID == -1:
            return redirect("updateCourses"), error
        # Go back to Update Internal/External view with error
        else:
            return redirect(errorURL, pk=courseID), error

    # Update / Add Course
    c, wasCreated = courses.filter(id=courseID).update_or_create(defaults=vals)

    # Go to Internal/External Course view without error
    return redirect(c.get_model(), pk=c.id), None


def request_course_helper(user, collegeID, mnemonic, number, name, courseID, url, comment):
    # Check valid url
    protocol = r"https?:\/\/(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9()@:%_\+.~#?&\/=]*)"
    noProtocol = r"[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&\/=]*)"
    if not (re.fullmatch(protocol, url) or re.fullmatch(noProtocol, url)):
        error = "Provided course link is invalid."
        return redirect("courseRequest", pk=courseID), error

    # check valid comment
    if not comment:
        error = "Inadequate explanation provided."
        return redirect("courseRequest", pk=courseID), error

    # Get Internal Course
    internal = InternalCourse.objects.get(id=courseID)

    # Get College
    try:
        college = ExternalCollege.objects.get(id=collegeID)
    except ExternalCollege.DoesNotExist:
        error = "Invalid External College."
        return redirect("courseRequest", pk=courseID), error

    # Get or Create External Course
    try:
        external = ExternalCourse.objects.get(college=college, mnemonic=mnemonic, course_number=number)
    except ExternalCourse.DoesNotExist:
        external = ExternalCourse.objects.create(college=college, mnemonic=mnemonic, course_number=number, course_name=name)

    # Get or Create CourseTransfer
    try:
        transfer = CourseTransfer.objects.get(internal_course=internal, external_course=external)
        if transfer.accepted:
            error = "This course equivalency has already been accepted."
            return redirect("courseRequest", pk=courseID), error

    except CourseTransfer.DoesNotExist:
        transfer = CourseTransfer.objects.create(internal_course=internal, external_course=external, accepted=False)

    # Get or Create TransferRequest
    try:
        request = TransferRequest.objects.get(user=user, transfer=transfer)
        error = "You have already made a transfer request for these two courses."
        return redirect("courseRequest", pk=courseID), error
    except TransferRequest.DoesNotExist:
        request = TransferRequest.objects.create(user=user, transfer=transfer, condition=TransferRequest.pending, url=url, comment=comment)

    # Return back to InternalCourse view without error
    return redirect("internalcourse", pk=courseID), None


def accept_request_helper(requestID, adminResponse):
    request = TransferRequest.objects.get(id=requestID)
    request.transfer.accepted = True
    request.transfer.save()
    TransferRequest.objects.filter(transfer=request.transfer).update(condition=TransferRequest.accepted, response=adminResponse)
    return redirect("handleRequests"), None

def reject_request_helper(requestID, adminResponse):
    request = TransferRequest.objects.get(id=requestID)
    request.transfer.accepted = False
    request.transfer.save()
    TransferRequest.objects.filter(transfer=request.transfer).update(condition=TransferRequest.rejected, response=adminResponse)
    return redirect("handleRequests"), None

