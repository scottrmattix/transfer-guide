from django.test import TestCase

# This test is just to verify that CI is working
class TestFail(TestCase):
    def test_fail(self):
        self.assertTrue(True)


class TestModelCreation(TestCase):
    def test_external_college_create():
    def test_external_course_create():
    def test_internal_course_create():
