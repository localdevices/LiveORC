from django.contrib.auth.models import User
from django.test import TestCase
def setupUsers():
    User.objects.create_superuser(username='testsuperuser',
                                  email='superuser@test.com',
                                  password='test1234')
    User.objects.create_user(username='testuser',
                             email='user@test.com',
                             password='test1234')
    User.objects.create_user(username='testuser2',
                             email='user2@test.com',
                             password='test1234')

def cleanup():
    """
    Clean up any temporary file storage
    """
    print("Clean up S3 storage before test. Not implemented yet.")

class InitTestCase(TestCase):
    '''
    This class initiates test dbase so that users are present and
    All tests for the api module should derive from this class instead of TestCase.

    We may consider moving this to a fixture.

    '''
    @classmethod
    def setUpTestData(cls):
        super(InitTestCase, cls).setUpTestData()
        cleanup()
        setupUsers()

    @classmethod
    def tearDownClass(cls):
        super(InitTestCase, cls).tearDownClass()


