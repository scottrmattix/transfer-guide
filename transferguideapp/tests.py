from django.test import TestCase


class TestFail(TestCase):
    def test_fail(self):
        self.assertTrue(True)
