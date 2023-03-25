from django.contrib.auth.models import User
from transferguideapp.models import InternalCourse, ExternalCourse, Favorites, ExternalCollege

# replace 'admin' with the account you're logged in as!
user = User.objects.get(username='admin')

ec = ExternalCollege(college_name="VCU", domestic_college=True)
ec.save()

e = ExternalCourse(college=ec, mnemonic="CS", course_number="0000", course_name="some vcu class")
e.save()

i = InternalCourse(id=1, mnemonic="CS", course_number="9999", course_name="some UVA class")
i.save()

favorite = Favorites(user=user, in_course = i, ex_course = e)
favorite.save()
print(user.favorite_items.all())


