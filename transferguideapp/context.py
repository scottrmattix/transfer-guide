
from .models import ExternalCollege, ExternalCourse, InternalCourse, CourseTransfer, Favorites
from django.db.models import Q

# Originally, all of this code was placed in the templates themselves, but
# as the complexity grew, I decided to move everything to get_context_data().
# However, views.py was getting cluttered, so I put everything in separate methods.

# Definitions
    # 'equivalents' - queryset of courses equivalent to a given course
    # 'favorites' - queryset of courses equivalent to a given course AND favorited by the user
    # 'exclusives' - queryset of courses equivalent to a given course AND from a specific college
        # all InternalCourses are from UVA, so equal to 'equivalents'
    # 'equiv_url' - url to the opposite course view (external for internal and vice versa)
    # 'college_name' - course's college name (since InternalCourses don't have college field).
    # 'foreign' - string to display on course view when the college is foreign

# return query for external courses belonging to a specific college
def exclusive(request):
    college = ExternalCollege.objects.get(college_name=request.session['user_college'])
    return Q(college=college)

# return query for internal courses favorited by user
def internal_faves(request):
    faves = Favorites.objects.filter(user=request.user)
    intIDs = faves.values_list("transfer__internal_course", flat=True).distinct()
    return Q(id__in=intIDs)

# return query for external courses favorited by user
def external_faves(request):
    faves = Favorites.objects.filter(user=request.user)
    extIDs = faves.values_list("transfer__external_course", flat=True).distinct()
    return Q(id__in=extIDs)

# define context for InternalCoursePage view
def context_internal(context, request, course):
    equivalent = course.get_equivalent()
    context['equivalents'] = equivalent
    context['favorites'] = equivalent.filter(external_faves(request))
    context['exclusives'] = equivalent.filter(exclusive(request))
    context['foreign'] = ""
    return context

# define context for ExternalCoursePage view
def context_external(context, request, course):
    equivalent = course.get_equivalent()
    context['equivalents'] = equivalent
    context['favorites'] = equivalent.filter(internal_faves(request))
    context['exclusives'] = equivalent
    context['foreign'] = "" if course.college.domestic_college else "(Foreign)"
    return context
