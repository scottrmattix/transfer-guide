from django.forms import ModelChoiceField, ModelForm, Form, CharField
from transferguideapp.models import CourseTransfer, ExternalCollege, InternalCourse, ExternalCourse

"""
class ExternalCollegeForm(ModelForm):
    class Meta:
        model = ExternalCollege
        fields = ["college_name"]

class ExternalCourseForm(ModelForm):
    class Meta:
        model = ExternalCourse 
        fields = ["college", "mnemonic", "course_number", "course_name"]
        field_classes = {
                "college" : ExternalCollegeForm,
        }

class InternalCourseForm(ModelForm):
    class Meta:
        model = InternalCourse
        fields = ["mnemonic", "course_number", "course_name"]
"""

# temporary solution, the form should be more dynamic to accept both already register courses as well as new courses
class TransferRequestForm(Form):
    external_course_name = CharField()
    external_course_college = CharField()
    external_course_mnemonic = CharField()
    external_course_number = CharField()

    internal_course_name = CharField()
    internal_course_mnemonic = CharField()
    internal_course_number = CharField()
