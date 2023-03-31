from django.db import IntegrityError
from django.urls import reverse
from django.shortcuts import redirect, render, get_object_or_404
from django.http import HttpResponseRedirect, Http404
from django.contrib.auth.models import Group, User
from django.views import generic
from transferguideapp.forms import SisSearchForm, TransferRequestForm
from .models import ExternalCourse, InternalCourse, ExternalCollege, CourseTransfer, Favorites
from .sis import request_data, unique_id
from django.db.models import Q
from .searchfilters import search
from .context import context_internal, context_external
from .viewhelper import update_favorites_helper, update_course_helper, request_course_helper

def account_info(request):
    user = request.user
    permissions = "User"
    if(user.groups.filter(name='admins').exists()):
        permissions = "Admin"
    if user.is_authenticated:
        return render(request, 'account_info.html', {'user': user, 'permissions': permissions})
    else:
        return redirect('home')

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
        return courses.order_by('mnemonic', 'course_number')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['colleges'] = ExternalCollege.objects.values_list('college_name', flat=True).order_by('college_name')
        return context

class UpdateInternal(generic.DetailView):
    template_name = 'editCourse.html'
    model = InternalCourse
    context_object_name = 'course'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['colleges'] = ExternalCollege.objects.order_by('college_name')
        context['collegeID'] = ""
        context['college'] = "University of Virginia"
        context['action'] = 'submit_update'
        return context

class UpdateExternal(generic.DetailView):
    template_name = 'editCourse.html'
    model = ExternalCourse
    context_object_name = 'course'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        q = Q(id=self.object.college.id)
        context['colleges'] = ExternalCollege.objects.filter(~q).order_by('college_name')
        context['collegeID'] = self.object.college.id
        context['college'] = self.object.college.college_name
        context['action'] = 'submit_update'
        return context


class UpdateCourses(generic.ListView):
    template_name = 'editCourse.html'
    context_object_name = 'colleges'

    def get_queryset(self):
        return ExternalCollege.objects.order_by('college_name')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['collegeID'] = ""
        context['college'] = "University of Virginia"
        context['action'] = 'submit_update'
        return context

def submit_update(request):
    if request.method == "POST":
        try:
            collegeID = request.POST["collegeID"]
            mnemonic = request.POST["mnemonic"]
            number = request.POST["number"]
            name = request.POST["name"]
            courseID = request.POST["id"]
        except Exception as e:
            return render(request, 'editCourse.html', {'error_message': f"An error occurred: {e}"})
        collegeID = int(collegeID) if collegeID else -1
        mnemonic = mnemonic.upper()
        number = number.upper()
        courseID = int(courseID) if courseID else -1
        return update_course_helper(collegeID, mnemonic, number, name, courseID)
    return HttpResponseRedirect(reverse('updateCourses'))

# a session error arises when .../search/ is visited without calling submit_search beforehand
# to bypass the issue, first visit .../search/clear/.
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
        request.session["search"]["college"] = college
        request.session["search"]["mnemonic"] = mnemonic.upper()
        request.session["search"]["number"] = number.upper()
        request.session["search"]["name"] = name
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

def update_favorites(request):
    if request.method == "POST":
        try:
            user = request.user
            pid = request.POST["primary"]
            sid = request.POST["secondary"]
            type = request.POST["type"]
        except Exception as e:
            return render(request, 'search.html', {'error_message': f"An error occurred: {e}"})
        return update_favorites_helper(user, pid, sid, type)
    return render(request, 'search.html')


class CourseRequest(generic.DetailView):
    model = InternalCourse
    context_object_name = "course"
    template_name = "requestForm.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        q = Q(id=self.request.session['user_college_id'])
        context['colleges'] = ExternalCollege.objects.filter(~q).order_by(
            'college_name')
        context['collegeID'] = self.request.session['user_college_id']
        context['college'] = self.request.session['user_college']
        context['action'] = 'make_request'
        return context

def make_request(request):
    if request.method == "POST":
        try:
            collegeID = request.POST["collegeID"]
            mnemonic = request.POST["mnemonic"]
            number = request.POST["number"]
            name = request.POST["name"]
            courseID = request.POST["id"]
        except Exception as e:
            return render(request, 'requestForm.html', {'error_message': f"An error occurred: {e}"})
        collegeID = int(collegeID) if collegeID else -1
        mnemonic = mnemonic.upper()
        number = number.upper()
        courseID = int(courseID) if courseID else -1
        return request_course_helper(collegeID, mnemonic, number, name, courseID)
    return HttpResponseRedirect(reverse('updateCourses'))




def delete_favorite(request, favorite_id):
    favorite = get_object_or_404(Favorites, id=favorite_id, user=request.user)
    favorite.delete()
    return redirect('favorites')
