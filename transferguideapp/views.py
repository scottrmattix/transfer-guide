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

def set_group(request, user_id):
    if(request.method == 'POST'):
        group = request.POST.get('usertype', None)
        g = Group.objects.get(name=group)
        user = User.objects.get(id=user_id)
        user.groups.add(g)
        user.save()
    return redirect('home')

class InternalCoursePage(generic.DetailView):
    template_name = 'course.html'
    model = InternalCourse
    context_object_name = 'course'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context_internal(context, self.request, self.object)


class ExternalCoursePage(generic.DetailView):
    template_name = 'course.html'
    model = ExternalCourse
    context_object_name = 'course'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context_external(context, self.request, self.object)

class CourseSearch(generic.ListView):
    template_name = 'search.html'
    model = InternalCourse
    context_object_name = 'course_list'

    def get_queryset(self):
        courses = search(self.request)
        return courses.order_by('course_number', 'mnemonic')

# a session error arises when .../search/ is visited without calling submit_search beforehand
# to bypass the issue, first visit .../search/error/.
def submit_search(request):
    request.session["search"] = {"college": "", "mnemonic": "", "number": "", "name": ""}
    if request.method == "POST":
        try:
            college = request.POST["college"]
            mnemonic = request.POST["mnemonic"]
            number = request.POST["number"]
            name = request.POST["name"]
        except Exception as e:
            return render(request, 'search.html', {'error_message': f"An error occurred: {e}"})
        else:
            request.session["search"]["college"] = college.upper()
            request.session["search"]["mnemonic"] = mnemonic.upper()
            request.session["search"]["number"] = number.upper()
            request.session["search"]["name"] = name
            return HttpResponseRedirect(reverse('courseSearch'))
    else:
        return render(request, 'search.html')

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


def favorites(request):
    f = Favorites.objects.filter(user=request.user)
    # f is the entire query set, to access individual fields do:
    # f[0].in_course.course_name, f[0].ex_course.course_id, etc

    return render(request, 'favorites2.html', {'favorites': f})

#not super sure if this is the best way to do it. need to test on the real database
def add_favorite(request, in_course_mnemonic=None, in_course_number=None, ex_course_mnemonic=None, ex_course_number=None):
    if in_course_mnemonic and in_course_number and ex_course_mnemonic and ex_course_number:
        in_course = get_object_or_404(InternalCourse, mnemonic=in_course_mnemonic, course_number=in_course_number)
        ex_course = get_object_or_404(ExternalCourse, mnemonic=ex_course_mnemonic, course_number=ex_course_number)
        favorite = Favorites(user=request.user, in_course=in_course, ex_course=ex_course)
        favorite.save()
        return redirect('favorites')
    else:
        raise Http404("Missing course information")

def create_favorite(request):
    if request.method == "POST":
        try:
            user = request.user
            primary_id = request.POST["primary"]
            secondary_id = request.POST["secondary"]
            course_type = request.POST["type"]
        except Exception as e:
            return render(request, request.path_info, {'error_message': f"An error occurred: {e}"})
        else:
            # InternalCoursePage view
            if course_type == "internalcourse":
                transfer = CourseTransfer.objects.get(internal_course=primary_id,
                                                      external_course=secondary_id)

            # ExternalCoursePage view
            else:
                transfer = CourseTransfer.objects.get(internal_course=secondary_id,
                                                      external_course=primary_id)

            # Validate transfer and user before creating favorite
            if not (user is None or transfer is None):
                favorite = Favorites(user=user, transfer=transfer)
                favorite.save()

            # Go back to InternalCoursePage
            if course_type == "internalcourse":
                course_id = transfer.internal_course.pk
                return redirect('internalCourse', pk=course_id)

            # Go back to ExternalCoursePage
            elif course_type == "externalcourse":
                course_id = transfer.external_course.pk
                return redirect('externalCourse', pk=course_id)

            # This shouldn't happen, but go back to search
            else:
                return render(request, 'search.html')

    # If not post request, go to search page
    else:
        return render(request, 'search.html')

def delete_favorite2(request):
    if request.method == "POST":
        try:
            user = request.user
            primary_id = request.POST["primary"]
            secondary_id = request.POST["secondary"]
            course_type = request.POST["type"]
        except Exception as e:
            return render(request, request.path_info, {'error_message': f"An error occurred: {e}"})
        else:
            # ExternalCoursePage view
            if course_type == "externalcourse":
                transfer = CourseTransfer.objects.get(internal_course=secondary_id,
                                                      external_course=primary_id)
            # InternalCoursePage or Favorites view
            else:
                transfer = CourseTransfer.objects.get(internal_course=primary_id,
                                                      external_course=secondary_id)

            # Validate user and transfer objects before deleting
            if not (user is None or transfer is None):
                favorite = Favorites.objects.get(user=user, transfer=transfer)
                favorite.delete()

            # Go back to InternalCoursePage
            if course_type == "internalcourse":
                course_id = transfer.internal_course.pk
                return redirect('internalCourse', pk=course_id)

            # Go back to ExternalCoursePage
            elif course_type == "externalcourse":
                course_id = transfer.external_course.pk
                return redirect('externalCourse', pk=course_id)

            # Go back to Favorites view
            else:
                return redirect('favorites')

    # If not post request, go to search page
    else:
        return render(request, 'search.html')


def delete_favorite(request, favorite_id):
    favorite = get_object_or_404(Favorites, id=favorite_id, user=request.user)
    favorite.delete()
    return redirect('favorites')
