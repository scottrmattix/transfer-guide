from django.urls import reverse
from django.shortcuts import redirect
from django.http import HttpResponseRedirect
from django.contrib.auth.models import Group, User

from django.shortcuts import render, get_object_or_404
from django.views import generic
import requests
import json
from .models import InternalCourse

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


