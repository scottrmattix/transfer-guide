from django.forms import ChoiceField, ModelChoiceField, Form, CharField, RadioSelect




# temporary solution, the form should be more dynamic to accept both already register courses as well as new courses
class TransferRequestForm(Form):
    def __init__(self, queryset, *args, **kwargs):
        self.external_course_name = CharField()
        self.external_course_college = CharField()
        self.external_course_mnemonic = CharField()
        self.external_course_number = CharField()
        self.internal_course_id = ModelChoiceField(queryset=queryset)
        super().__init__(*args, **kwargs)
