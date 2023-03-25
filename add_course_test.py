from django.contrib.auth.models import User
from transferguideapp.models import InternalCourse, ExternalCourse, Favorites, ExternalCollege
from transferguideapp.views import add_favorite
from django.test import RequestFactory
from django.urls import reverse


user = User.objects.get(username='admin')
factory = RequestFactory()
in_course_mnemonic = 'CS'
in_course_number = '9999'
ex_course_mnemonic = 'AA'
ex_course_number = '1000'
in_course = InternalCourse.objects.get(mnemonic=in_course_mnemonic, course_number=in_course_number)
ex_course = ExternalCourse.objects.get(mnemonic=ex_course_mnemonic, course_number=ex_course_number)

# Call the add_favorite view with the appropriate arguments
url = reverse('add_favorite', args=[in_course.mnemonic, in_course.course_number, ex_course.mnemonic, ex_course.course_number])
request = factory.post(url, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
request.user = user
response = add_favorite(request, in_course_mnemonic, in_course_number, ex_course_mnemonic, ex_course_number)

# Verify that the favorite has been added to the user's list of favorites
favorites = user.favorite_items.all()
print(favorites)