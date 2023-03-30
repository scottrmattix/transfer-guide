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

# helper methods for views

def update_favorites_helper(user, pid, sid, type):
    if type == "internalcourse":
        q = Q(internal_course=pid, external_course=sid)
        response = redirect('internalCourse', pk=pid)

    elif type == "externalcourse":
        q = Q(internal_course=sid, external_course=pid)
        response = redirect('externalCourse', pk=pid)

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


