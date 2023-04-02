from django.test import TestCase
from .models import CourseTransfer, ExternalCourse, InternalCourse, ExternalCollege, Favorites
from django.contrib.auth.models import Group, User
from .searchfilters import search, filterCollege, filterMnemonic, filterNumber, filterName
from django.test.client import RequestFactory, Client
from django.contrib.sessions.middleware import SessionMiddleware

# This test is just to verify that CI is working
#class TestFail(TestCase):
#    def test_fail(self):
#        self.assertTrue(False)


def clean_data():
    CourseTransfer.objects.all().delete()
    ExternalCourse.objects.all().delete()
    ExternalCollege.objects.all().delete()
    InternalCourse.objects.all().delete()


class TestModelCreation(TestCase):
    def test_course_transfer_create(self):
        inter_course = InternalCourse(course_name = "Advanced Software Development Techniques", course_number = "3240" , mnemonic = "CS")
        inter_course.save()
        exter_college = ExternalCollege(college_name = "Piedmont Valley Community College")
        exter_college.save()
        exter_course = ExternalCourse(course_name = "Software Development", course_number = "123", mnemonic = "CS", college = ExternalCollege.objects.get(college_name = "Piedmont Valley Community College"))
        exter_course.save()
        course_transfer = CourseTransfer(internal_course = InternalCourse.objects.get(course_number = "3240", mnemonic="CS"), external_course = ExternalCourse.objects.get(course_number = "123", mnemonic="CS"))
        course_transfer.save()
        self.assertEqual(str(course_transfer), str(CourseTransfer.objects.get(external_course = ExternalCourse.objects.get(course_number = "123", mnemonic = "CS"))))
        clean_data()

    def test_external_course_create(self):
        exter_college = ExternalCollege(college_name = "Piedmont Valley Community College")
        exter_college.save()
        exter_course = ExternalCourse(course_name = "Software Development", course_number = "123", mnemonic = "CS", college = ExternalCollege.objects.get(college_name = "Piedmont Valley Community College"))
        exter_course.save()
        self.assertEqual(str(exter_course), str(ExternalCourse.objects.get(course_number="123", mnemonic = "CS")))
        clean_data()


    def test_internal_course_create(self):
        inter_course = InternalCourse(course_name = "Advanced Software Development Techniques", course_number = "3240" , mnemonic = "CS")
        inter_course.save()
        self.assertEqual(str(inter_course), str(InternalCourse.objects.get(course_number="3240", mnemonic = "CS")))
        clean_data()



    def test_external_college_create(self):
        exter_college = ExternalCollege(college_name = "Piedmont Valley Community College")
        exter_college.save()
        self.assertEqual(str(exter_college), str(ExternalCollege.objects.get(college_name = "Piedmont Valley Community College")))
        clean_data()



class SearchTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        login = self.client.login(username='testuser', password='12345')

        for i in range(1,6):
            college = ExternalCollege.objects.create(college_name=f"college{i}",
                                                     domestic_college=True)
            external = ExternalCourse.objects.create(college=college,
                                                     mnemonic=f"mnemonic{i}",
                                                     course_number=f"number{i}",
                                                     course_name=f"name{i}")
            internal = InternalCourse.objects.create(mnemonic=f"mnemonic{i}",
                                                     course_number=f"number{i}",
                                                     course_name=f"name{i}")
            transfer = CourseTransfer.objects.create(internal_course=internal,
                                                     external_course=external,
                                                     accepted=True)
            if i % 2 == 1:
                favorite = Favorites.objects.create(user=self.user, transfer=transfer)
        return

    def test_same_user(self):
        self.assertEqual(Favorites.objects.first().user, Favorites.objects.last().user)


class FavoritesTests(TestCase):

    def setUp(self):
        
        self.user = User.objects.create_user(username='testuser', password='12345')

        # bogus CourseTransfer object used for testing
        self.transfer = CourseTransfer.objects.create( 
            external_course = ExternalCourse.objects.last(),
            internal_course = InternalCourse.objects.last(),
            accepted = True 
        )

        self.favorite = Favorites.objects.create(
            user = self.user,
            transfer = self.transfer
        )

    def test_quantity(self):
        count = Favorites.objects.filter(user=self.user).count()
        self.assertEquals(count, 1)

    def test_favorite_instance(self):
        self.assertEqual(self.favorite.user, self.user)
        self.assertEqual(self.favorite.transfer, self.transfer)
        
    def tearDown(self):
        self.favorite.delete()
        self.transfer.delete()
        self.user.delete()