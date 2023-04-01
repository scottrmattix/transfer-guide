from django.db import IntegrityError
from django.urls import reverse
from django.shortcuts import redirect, render, get_object_or_404
from django.http import HttpResponseRedirect, Http404
from django.contrib.auth.models import Group, User
from django.views import generic
from transferguideapp.forms import SisSearchForm, TransferRequestForm
from .models import ExternalCourse, InternalCourse, ExternalCollege, CourseTransfer, Favorites
from .sis import request_data, unique_id
import requests
import json
import re
from .searchfilters import search
from .context import context_internal, context_external
from django.db.models import Q
from django.db import transaction

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
    try:
        college = ExternalCollege.objects.get(id=collegeID)

    except ExternalCollege.DoesNotExist:
        return redirect("formRequest", pk=courseID)

    courses = ExternalCourse.objects.filter(college=college,
                                            mnemonic=mnemonic,
                                            course_number=number)
    external_vals = {'college': college,
                     'mnemonic': mnemonic,
                     'course_number': number,
                     'course_name': name}

    #try:
    with transaction.atomic():
        external, wasCreated = courses.update_or_create(defaults=external_vals)
    internal = InternalCourse.objects.get(id=courseID)

    transfer_vals = {'internal_course': internal,
                     'external_course': external,
                     'accepted': True}

    existing = CourseTransfer.objects.filter(internal_course=internal,
                                             external_course=external)
    with transaction.atomic():
        transfer, wasCreated = existing.update_or_create(defaults=transfer_vals)
    return redirect("internalcourse", pk=courseID)

    #except IntegrityError:
    #    return redirect("courseRequest", pk=courseID)

