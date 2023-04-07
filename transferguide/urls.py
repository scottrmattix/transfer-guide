"""transferguide URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.contrib.auth.views import LogoutView
from transferguideapp.views import set_group, submit_transfer_request, account_info, favorites, add_favorite, delete_favorite, update_favorites, CourseSearch, submit_search, InternalCoursePage, ExternalCoursePage, UpdateInternal, UpdateExternal, UpdateCourses, submit_update, make_request, CourseRequest, HandleRequests, accept_request, reject_request

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', TemplateView.as_view(template_name="index.html"), name="home"),
    path('accounts/', include('allauth.urls')),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('request/', submit_transfer_request , name='request'),
    path('set_group/<int:user_id>', set_group , name='set_group'),
    path('account_info/', account_info , name='account_info'),

    path('search/', CourseSearch.as_view(), name='courseSearch'),
    path('search/clear/', submit_search, name='submit_search'), # this is for error handling

    path('internal/<int:pk>', InternalCoursePage.as_view(), name='internalcourse'),
    path('external/<int:pk>', ExternalCoursePage.as_view(), name='externalcourse'),

    path('internal/<int:pk>/update', UpdateInternal.as_view(), name='internalcourseUpdate'),
    path('external/<int:pk>/update', UpdateExternal.as_view(), name='externalcourseUpdate'),
    path('course/update/', UpdateCourses.as_view(), name='updateCourses'),
    path('course/update/submit', submit_update, name='submit_update'),

    path('favorites/', favorites, name='favorites'),
    path('favorites/update/', update_favorites, name='update_favorites'),

    path('internal/<int:pk>/request', CourseRequest.as_view(), name='courseRequest'),
    path('course/request', make_request, name='make_request'),
    path('handle/request', HandleRequests.as_view(), name='handleRequests'),
    path('handle/request/accept', accept_request, name='accept_request'),
    path('handle/request/reject', reject_request, name='reject_request'),

    path('add_favorite/<str:in_course_mnemonic>/<str:in_course_number>/<str:ex_course_mnemonic>/<str:ex_course_number>/', add_favorite, name='add_favorite'),
    path('favorites/delete/<int:favorite_id>/', delete_favorite, name='delete_favorite'),
    ]
