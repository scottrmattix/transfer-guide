from django.db import IntegrityError
from django.urls import reverse
from django.shortcuts import redirect, render
from django.http import HttpResponseRedirect
from django.contrib.auth.models import Group, User

from django.shortcuts import render, get_object_or_404
from django.views import generic
from transferguideapp.forms import SisSearchForm, TransferRequestForm
from .models import ExternalCourse, InternalCourse, ExternalCollege, CourseTransfer 
from .sis import request_data, unique_id 
import requests
import json

# Global variables for search parameters (this probably needs to be replaced)
setMnemonic = ""
setName = ""

def set_group(request, user_id):
    if(request.method == 'POST'):
        group = request.POST.get('usertype', None)
        g = Group.objects.get(name=group)
        user = User.objects.get(id=user_id)
        user.groups.add(g)
        user.save()
    return redirect('home')

class CourseSearch(generic.ListView):
    template_name = 'search.html'
    model = InternalCourse
    context_object_name = 'course_list'

    def get_queryset(self):
        if setMnemonic == "" and setName == "":
            return None

        courses = InternalCourse.objects
        if setMnemonic != "":
            courses = courses.filter(mnemonic=setMnemonic)
        if setName != "":
            courses = courses.filter(course_name__icontains=setName)

        return courses.order_by('course_number').order_by('mnemonic')

def submit_search(request):
    global setMnemonic
    global setName
    setMnemonic = ""
    setName = ""

    try:
        mnemonic = request.POST['mnemonic']
        name = request.POST['name']
    except Exception:
        return render(request, 'search.html', {
            'error_message': "An error occurred…",
        })
    else:
        if not all(x.isalpha() or x.isspace() for x in name + mnemonic):
            return render(request, 'search.html', {'error_message': "Invalid input detected."})
        if mnemonic != "":
            setMnemonic = mnemonic.upper()
        if name != "":
            setName = name
        return HttpResponseRedirect(reverse('courseSearch'))

def handle_transfer_request(request):
    transfer_form = TransferRequestForm(request.POST)
    if transfer_form.is_valid():
        external_course_name = transfer_form.cleaned_data['external_course_name']
        external_course_college = transfer_form.cleaned_data['external_course_college']
        external_course_mnemonic = transfer_form.cleaned_data['external_course_mnemonic']
        external_course_number = transfer_form.cleaned_data['external_course_number']
        internal_course_id = int(transfer_form.cleaned_data['internal_course_id'])
        internal_course_name = transfer_form.cleaned_data['internal_course_name']
        internal_course_mnemonic = transfer_form.cleaned_data['internal_course_mnemonic']
        internal_course_number = transfer_form.cleaned_data['internal_course_number']
        college = (None, False)
        extern = (None, False)
        intern = (None, False)
        try:
            college = ExternalCollege.objects.update_or_create(college_name = external_course_college)
        except IntegrityError:
            pass
        try:
            extern = ExternalCourse.objects.update_or_create(course_name = external_course_name, college = college[0], mnemonic = external_course_mnemonic, course_number = external_course_number)
        except IntegrityError:
            pass
        try:
            intern = InternalCourse.objects.update_or_create(course_name = internal_course_name, id = internal_course_id, mnemonic = internal_course_mnemonic, course_number = internal_course_number)
        except IntegrityError:
            pass
        try:
            CourseTransfer.objects.update_or_create(external_course = extern[0] , internal_course = intern[0])
        except IntegrityError:
            pass

        
        return redirect('home')

def handle_sis_request(request):
    sis_form = SisSearchForm(request.GET)
    transfer_form = TransferRequestForm()
    r = [{}]
    if sis_form.is_valid():
        mnemonic = sis_form.cleaned_data['mnemonic']
        course_number = sis_form.cleaned_data['course_number']
        page = sis_form.cleaned_data['page']
        query = {'page' : page}
        if not mnemonic == "":
            query['subject'] = mnemonic
        if not course_number == "":
            query['catalog_nbr'] = course_number
        r = unique_id(request_data(query))
    return render(request, 'request.html', {'transfer_form' : transfer_form , 'sis_form' : sis_form, 'r' : r})

def submit_transfer_request(request):
    r = [{}]
    if request.method == "POST":
        sis_form = SisSearchForm()
        transfer_form = TransferRequestForm(request.POST)
        if 'transfer' in request.POST:
            return handle_transfer_request(request)
    elif request.method == "GET":
        sis_form = SisSearchForm(request.GET)
        transfer_form = TransferRequestForm()
        if 'sis' in request.GET:
            return handle_sis_request(request)
    else:
        transfer_form = TransferRequestForm()
        sis_form = SisSearchForm()
    return render(request, 'request.html', {'transfer_form' : transfer_form , 'sis_form' : sis_form, 'r' : r})
