from django.urls import reverse
from django.shortcuts import redirect
from django.http import HttpResponseRedirect
from django.contrib.auth.models import Group, User



def set_group(request, user_id):
    if(request.method == 'POST'):
        group = request.POST.get('usertype', None)
        g = Group.objects.get(name=group)
        user = User.objects.get(id=user_id)
        user.groups.add(g) 
        user.save()
    return redirect('home') 
