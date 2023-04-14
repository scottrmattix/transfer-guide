from django.db import IntegrityError
from django.urls import reverse
from django.shortcuts import redirect, render, get_object_or_404
from django.http import HttpResponseRedirect, Http404, HttpResponseForbidden
from django.contrib.auth.models import Group, User
from django.views import generic
from transferguideapp.forms import SisSearchForm, TransferRequestForm
from .models import ExternalCourse, InternalCourse, ExternalCollege, CourseTransfer, Favorites, TransferRequest
from .sis import request_data, unique_id
from django.db.models import Q
from .searchfilters import search
from .context import context_course, context_course_request, context_update_internal, context_update_external, context_update_course, context_view_requests
from .viewhelper import update_favorites_helper, update_course_helper, request_course_helper, handle_request_helper
from django.contrib import messages
from helpermethods import course_title_format

def favorite_request(request, favorite_id):
    favorite = get_object_or_404(Favorites, id=favorite_id, user=request.user)

    tr, created = TransferRequest.objects.get_or_create(user=request.user, transfer = favorite.transfer)
    if created:
        tr.save()

    return redirect('/handle/request')


def add_external_college(request):

    if(request.method == 'POST'):
        college_name = request.POST['college']
        domestic_college = True
        if request.POST.get('domestic') == 'off':
            domestic_college = False
        normalized_name = course_title_format(college_name)
        if not ExternalCollege.objects.filter(college_name=normalized_name, domestic_college=domestic_college).exists():
            ExternalCollege(college_name=college_name, domestic_college=domestic_college).save()
        return HttpResponseRedirect('/course/update')


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
        context_course(context, self.object, self.request)
        return context


class ExternalCoursePage(generic.DetailView):
    template_name = 'course.html'
    model = ExternalCourse
    context_object_name = 'course'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context_course(context, self.object, self.request)
        return context

class CourseSearch(generic.ListView):
    template_name = 'search.html'
    model = InternalCourse
    context_object_name = 'course_list'

    def get_queryset(self):
        courses, query = search(self.request.session)
        if query == Q():
            return courses.none()
        else:
            return courses.filter(query).order_by('mnemonic', 'course_number')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['colleges'] = ExternalCollege.objects.values_list('college_name', flat=True).order_by('college_name')
        return context

class UpdateInternal(generic.DetailView):
    template_name = 'generalForm.html'
    model = InternalCourse
    # context_object_name = 'course'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # context['colleges'] = ExternalCollege.objects.order_by('college_name')
        # context['collegeID'] = ""
        # context['college'] = "University of Virginia"
        # context['action'] = 'submit_update'
        context_update_internal(context, self.object)
        return context

class UpdateExternal(generic.DetailView):
    template_name = 'generalForm.html'
    model = ExternalCourse
    # context_object_name = 'course'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # q = Q(id=self.object.college.id)
        # context['colleges'] = ExternalCollege.objects.filter(~q).order_by('college_name')
        # context['collegeID'] = self.object.college.id
        # context['college'] = self.object.college.college_name
        # context['action'] = 'submit_update'
        context_update_external(context, self.object)
        return context


class UpdateCourses(generic.ListView):
    template_name = 'generalForm.html'
    queryset = InternalCourse.objects.none()

    # def get_queryset(self):
    #     return ExternalCollege.objects.order_by('college_name')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # context['collegeID'] = ""
        # context['college'] = "University of Virginia"
        # context['action'] = 'submit_update'
        context_update_course(context)
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
            message = f"An error occurred: {e}"
            messages.add_message(request, messages.DEBUG, message)
        else:
            collegeID = int(collegeID) if collegeID else -1
            mnemonic = mnemonic.upper()
            number = number.upper()
            courseID = int(courseID) if courseID else -1

            redirect, type, message = update_course_helper(collegeID, mnemonic, number, name, courseID)
            if message:
                messages.add_message(request, type, message)
            return redirect
    return HttpResponseRedirect(reverse('courseSearch'))

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
            message = f"An error occurred: {e}"
            messages.add_message(request, messages.DEBUG, message)
        else:
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
    f = Favorites.objects.filter(user=request.user).order_by('-created_at')
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
            tab = request.POST["active-tab"]
        except Exception as e:
            message = f"An error occurred: {e}"
            messages.add_message(request, messages.DEBUG, message)
        else:
            request.session["course_tab"] = tab
            return update_favorites_helper(user, pid, sid, type)
    return HttpResponseRedirect(reverse('courseSearch'))


class CourseRequest(generic.DetailView):
    model = InternalCourse
    template_name = "generalForm.html"
    # context_object_name = "course"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # q = Q(id=self.request.session['user_college_id'])
        # context['colleges'] = ExternalCollege.objects.filter(~q).order_by(
        #     'college_name')
        # context['collegeID'] = self.request.session['user_college_id']
        # context['college'] = self.request.session['user_college']
        # context['action'] = 'make_request'
        context_course_request(context, self.object, self.request)
        return context

def make_request(request):
    if request.method == "POST":
        try:
            user = request.user
            collegeID = request.POST["collegeID"]
            mnemonic = request.POST["mnemonic"]
            number = request.POST["number"]
            name = request.POST["name"]
            courseID = request.POST["id"]
            url = request.POST["url"]
            comment = request.POST["comment"]
        except Exception as e:
            message = f"An error occurred: {e}"
            messages.add_message(request, messages.DEBUG, message)
        else:
            collegeID = int(collegeID) if collegeID else -1
            mnemonic = mnemonic.upper()
            number = number.upper()
            courseID = int(courseID) if courseID else -1

            redirect, type, message = request_course_helper(user, collegeID, mnemonic, number,
                                                            name, courseID, url, comment)
            if message:
                messages.add_message(request, type, message)
            return redirect
    return HttpResponseRedirect(reverse('courseSearch'))


def delete_favorite(request, favorite_id):
    favorite = get_object_or_404(Favorites, id=favorite_id, user=request.user)
    favorite.delete()
    return redirect('favorites')

class HandleRequests(generic.ListView):
    template_name = 'handleRequests.html'
    queryset = TransferRequest.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context_view_requests(context, self.request.user, self.request.session)
        return context


def accept_request(request):
    request.session["request_tab"] = "pending"
    if request.method == "POST":
        try:
            requestID = request.POST["requestID"]
            adminResponse = request.POST["adminResponse"]
            tab = request.POST["tab"]
        except Exception as e:
            message = f"An error occurred: {e}"
            messages.add_message(request, messages.DEBUG, message)
        else:
            request.session["request_tab"] = tab
            redirect = handle_request_helper(requestID, adminResponse, accepted=True)
            return redirect
    return HttpResponseRedirect(reverse('handleRequests'))

def reject_request(request):
    request.session["request_tab"] = "pending"
    if request.method == "POST":
        try:
            requestID = request.POST["requestID"]
            adminResponse = request.POST["adminResponse"]
            tab = request.POST["tab"]
        except Exception as e:
            message = f"An error occurred: {e}"
            messages.add_message(request, messages.DEBUG, message)
        else:
            request.session["request_tab"] = tab
            redirect = handle_request_helper(requestID, adminResponse, accepted=False)
            return redirect
    return HttpResponseRedirect(reverse('handleRequests'))
