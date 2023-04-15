from django.shortcuts import redirect, render, get_object_or_404
from .models import ExternalCourse, InternalCourse, ExternalCollege, CourseTransfer, Favorites, TransferRequest
from django.db.models import Q
from django.contrib import messages
import re
from django.utils import timezone
from django.urls import reverse
from .sis import request_data, unique_id
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


    # Check that no empty strings were supplied
    if not (mnemonic and number and name):
        message = "No fields may be left empty"
        if courseID == -1:
            return redirect("updateCourses"), messages.ERROR, message
        else:
            return redirect(errorURL, pk=courseID), messages.ERROR, message


    # Check if new/edited course is a duplicate
    existing = courses.filter(check).first()
    if existing:
        existingURL = reverse(existing.get_model(), kwargs={'pk': existing.id})
        message = f"A <a href='{existingURL}' class='alert-link'>course</a> with this mnemonic and number already exists at this college."
        # Go back to UpdateCourses view with error
        if courseID == -1:
            return redirect("updateCourses"), messages.ERROR, message
        # Go back to Update Internal/External view with error
        else:
            return redirect(errorURL, pk=courseID), messages.ERROR, message

    # Update / Add Course
    c, wasCreated = courses.filter(id=courseID).update_or_create(defaults=vals)

    if wasCreated:
        # Go to new Internal/External Course view without error
        message = "Course successfully created."
    else:
        # Go to edited Internal/External Course view without error
        message = "Course successfully updated."
    return redirect(c.get_model(), pk=c.id), messages.SUCCESS, message


def request_course_helper(user, collegeID, mnemonic, number, name, courseID, url, comment):
    # check that no empty strings were provided
    if not (mnemonic and number and name and url and comment):
        message = "No fields may be left empty"
        return redirect("courseRequest", pk=courseID), messages.ERROR, message

    # Check valid url
    protocol = r"https?:\/\/(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9()@:%_\+.~#?&\/=]*)"
    noProtocol = r"[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&\/=]*)"
    if not (re.fullmatch(protocol, url) or re.fullmatch(noProtocol, url)):
        message = "Provided course link is invalid."
        return redirect("courseRequest", pk=courseID), messages.ERROR, message


    # Get Internal Course
    internal = InternalCourse.objects.get(id=courseID)

    # Get College
    try:
        college = ExternalCollege.objects.get(id=collegeID)
    except ExternalCollege.DoesNotExist:
        message = "The provided college could not be found."
        return redirect("courseRequest", pk=courseID), messages.ERROR, message

    # Get or Create External Course
    try:
        external = ExternalCourse.objects.get(college=college, mnemonic=mnemonic, course_number=number)
    except ExternalCourse.DoesNotExist:
        external = ExternalCourse.objects.create(college=college, mnemonic=mnemonic, course_number=number, course_name=name)

    # Get or Create CourseTransfer
    try:
        transfer = CourseTransfer.objects.get(internal_course=internal, external_course=external)
        if transfer.accepted:
            externalURL = reverse("externalcourse", kwargs={'pk': transfer.external_course.id})
            message = f"This <a href='{externalURL}' class='alert-link'>course equivalency</a> has already been accepted."
            return redirect("courseRequest", pk=courseID), messages.ERROR, message

    except CourseTransfer.DoesNotExist:
        transfer = CourseTransfer.objects.create(internal_course=internal, external_course=external, accepted=False)

    # Get or Create TransferRequest
    try:
        request = TransferRequest.objects.get(user=user, transfer=transfer)
        requestsURL = reverse("handleRequests")
        message = f"You have already made a <a href='{requestsURL}' class='alert-link'>transfer request</a> for these two courses."
        return redirect("courseRequest", pk=courseID), messages.ERROR, message
    except TransferRequest.DoesNotExist:
        request = TransferRequest.objects.create(user=user, transfer=transfer, condition=TransferRequest.pending, url=url, comment=comment)

    # Return back to InternalCourse view without error
    requestsURL = reverse("handleRequests")
    message = f"Your <a href='{requestsURL}' class='alert-link'>transfer request</a> is now pending."
    return redirect("internalcourse", pk=courseID), messages.SUCCESS, message


def handle_request_helper(requestID, adminResponse, accepted):
    condition = TransferRequest.accepted if accepted else TransferRequest.rejected
    request = TransferRequest.objects.get(id=requestID)
    request.transfer.accepted = accepted
    request.transfer.save()
    TransferRequest.objects.filter(transfer=request.transfer).update(condition=condition, response=adminResponse, updated_at=timezone.now())
    return redirect("handleRequests")


def sis_lookup_helper(sisMnemonic, sisNumber):
    if not (sisMnemonic and sisNumber):
        message = f"No fields may be left empty"
        return redirect("courseSearch"), messages.ERROR, message



    existing = InternalCourse.objects.filter(mnemonic=sisMnemonic,
                                             course_number=sisNumber).first()
    if False:
        existingURL = reverse(existing.get_model(), kwargs={'pk': existing.id})
        message = f"A <a href='{existingURL}' class='alert-link'>course</a> with this mnemonic and number already exists at this college."
        return redirect("courseSearch"), messages.INFO, message
    else:
        query = {'subject': sisMnemonic, 'catalog_nbr': sisNumber}
        if True:
        #try:
            r = unique_id(request_data(query))[0]
            print(r)
            c = InternalCourse(
                    #id=r['crse_id'],
                    mnemonic=r['subject'],
                    course_number=r['catalog_nbr'],
                    course_name=r['descr'],
                    #credits=r['units'],
                )
        #except Exception as e:
        #    message = f"An error occurred: {e}"
        #    return redirect("courseSearch"), messages.INFO, message
        #else:
            print("SUCCESS")
            c.save()
            courseURL = reverse(c.get_model(), kwargs={'pk': c.id})
            message = f"Your <a href='{courseURL}' class='alert-link'>course</a> was successfully added to the database."
            return redirect("courseSearch"), messages.SUCCESS, message

