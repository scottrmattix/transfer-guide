
from .models import ExternalCollege, ExternalCourse, InternalCourse, CourseTransfer, Favorites, TransferRequest
from django.db.models import Q, Count, Case, When, Value, CharField, BooleanField

# Originally, all of this code was placed in the templates themselves, but
# as the complexity grew, I decided to move everything to get_context_data().
# However, views.py was getting cluttered, so I put everything in separate methods.

########################################################################################
# In order for us to reuse templates, the context dictionary entries of
# InternalCoursePage and ExternalCoursePage must match
########################################################################################

def context_course(context, course, request):
    context['foreign'] = set_foreign(course)
    context['checkbox'], collegeQ = handle_checkbox(course, request.session)
    unspecific, specific = favorite_filters(course, request.user)
    context['equivalents'] = create_annotations(course, specific, unspecific, collegeQ)

########################################################################################

def handle_checkbox(course, session):
    if "user_college_id" in session and course.get_model() == "internalcourse":
        checkbox = True
        collegeQ = Q(college__id=session["user_college_id"])
    else:
        checkbox = False
        collegeQ = ~Q(id=-1)
    return checkbox, collegeQ

def favorite_filters(course, user):
    unspecific = Q(coursetransfer__favorites__user=user)
    if course.get_model() == "internalcourse":
        specific = unspecific & Q(coursetransfer__internal_course=course)
    else:
        specific = unspecific & Q(coursetransfer__external_course=course)
    return unspecific, specific

def set_foreign(course):
    foreign = ""
    if course.get_model() == "externalcourse":
        if not course.college.domestic_college:
            foreign = "(Foreign)"
    return foreign

def create_annotations(course, specific, unspecific, collegeQ):
    return course.get_equivalent().annotate(
        totallikes=Count('coursetransfer__favorites', filter=unspecific),

        pagelikes=Count('coursetransfer__favorites', filter=specific),

        visibility=Case(When(collegeQ, then=Value('include')),
                        When(~collegeQ, then=Value('exclude')),
                        output_field=CharField()),

        color=Case(When(totallikes=0, then=Value('light')),
                   When(Q(totallikes__gte=1, pagelikes=0), then=Value('warning')),
                   When(Q(totallikes__gte=1, pagelikes__gte=1), then=Value('success')),
                   output_field=CharField()),

        action=Case(When(pagelikes=0, then=Value('Favorite')),
                    When(pagelikes__gte=1, then=Value('Unfavorite')),
                    output_field=CharField())
    )

########################################################################################
# In order for us to reuse templates, the context dictionary entries of
# CourseRequest, UpdateInternal, UpdateExternal, and UpdateCourses must match
########################################################################################

# define context for CourseRequest view
def context_course_request(context, course, request):
    if "user_college" in request.session:
        collegeID = request.session["user_college_id"]
        college = request.session["user_college"]
        q = Q(id=collegeID)
    else:
        collegeID = ""
        college = ""
        q = Q()

    context['colleges'] = ExternalCollege.objects.filter(~q).order_by('college_name')
    context['collegeID'] = collegeID
    context['college'] = college
    context['action'] = 'make_request'
    context['course'] = InternalCourse.objects.none()
    context['courseID'] = course.id
    context['title'] = "Course Transfer Request"
    context['link'] = True

# define context for UpdateInternal view
def context_update_internal(context, course):
    context['colleges'] = ExternalCollege.objects.none()
    context['collegeID'] = ""
    context['college'] = "University of Virginia"
    context['action'] = 'submit_update'
    context['course'] = course
    context['courseID'] = course.id
    context['title'] = "Edit UVA Course"
    context['link'] = False

# define context for UpdateExternal view
def context_update_external(context, course):
    q = Q(id=course.college.id)
    context['colleges'] = ExternalCollege.objects.filter(~q).order_by('college_name')
    context['collegeID'] = course.college.id
    context['college'] = course.college.college_name
    context['action'] = 'submit_update'
    context['course'] = course
    context['courseID'] = course.id
    context['title'] = "Edit External Course"
    context['link'] = False

# define context for UpdateCourses view
def context_update_course(context):
    context['colleges'] = ExternalCollege.objects.order_by('college_name')
    context['collegeID'] = ""
    context['college'] = "University of Virginia"
    context['action'] = 'submit_update'
    context['course'] = InternalCourse.objects.none()
    context['courseID'] = ""
    context['title'] = "Add Course"
    context['link'] = False

########################################################################################
# Context for ViewRequests view
########################################################################################


def context_view_requests(context):
    requests = TransferRequest.objects.all().annotate(
        color=Case(When(Q(condition=TransferRequest.pending), then=Value('light')),
                   When(Q(condition=TransferRequest.accepted), then=Value('success')),
                   When(Q(condition=TransferRequest.rejected), then=Value('danger')),
                   output_field=CharField()),
        btn=Case(When(Q(condition=TransferRequest.pending), then=Value('outline-dark')),
                 When(Q(condition=TransferRequest.accepted), then=Value('outline-success')),
                 When(Q(condition=TransferRequest.rejected), then=Value('outline-danger')),
                 output_field=CharField()),
        action=Case(When(Q(condition=TransferRequest.pending), then=Value(True)),
                    When(~Q(condition=TransferRequest.pending), then=Value(False)),
                    output_field=BooleanField()),
    )
    context["all"] = requests
    context["pending"] = requests.filter(condition=TransferRequest.pending)
    context["accepted"] = requests.filter(condition=TransferRequest.accepted)
    context["rejected"] = requests.filter(condition=TransferRequest.rejected)


