from django.forms import ModelChoiceField, Form, CharField 


# temporary solution, the form should be more dynamic to accept both already register courses as well as new courses
# Likely will need javacript to make this funciton correctly
class TransferRequestForm(Form):
    def __init__(self, external_queryset, internal_queryset, *args, **kwargs):
        self.external_course_name = CharField()
        self.external_course_college = CharField()
        self.external_course_mnemonic = CharField()
        self.external_course_number = CharField()
        self.external_course_id = ModelChoiceField(queryset=external_queryset)

        self.internal_course_id = ModelChoiceField(queryset=internal_queryset)
        super().__init__(*args, **kwargs)
