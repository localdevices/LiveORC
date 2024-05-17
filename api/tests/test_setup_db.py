# from django.contrib.auth.models import User
from users.models import User, Institute, Group, Member
from users.management.commands.creategroups import add_group_permissions, READ_GROUPS, WRITE_GROUPS, MODELS, READ_PERMISSIONS, WRITE_PERMISSIONS
from django.test import TestCase


def setupUsers():
    # make the default groups (as if running manage.py creategroups)
    # add_group_permissions(READ_GROUPS, MODELS, READ_PERMISSIONS)
    # add_group_permissions(WRITE_GROUPS, MODELS, WRITE_PERMISSIONS)

    # make some Users
    User.objects.create_superuser(name='testsuperuser',
                                  email='superuser@test.com',
                                  password='test1234')
    testuser1 = User.objects.create_user(name='testuser',
                             email='user@institute1.com',
                             password='test1234')
    # testuser1.groups.add(2)
    testuser2 = User.objects.create_user(name='testuser2',
                             email='user2@institute1.com',
                             password='test1234')
    # testuser2.groups.add(1)
    testuser3 = User.objects.create_user(name='testuser3',
                             email='user3@institute2.com',
                             password='test1234')
    # testuser3.groups.add(2)
    # make some institutes
    institute1 = Institute.objects.create(name="institute1", owner=testuser1)
    institute2 = Institute.objects.create(name="institute2", owner=testuser3)
    # now update the users with the institute
    # user 3 belong to another institute, so that we can test if he/she is denied access to instances of test users
    # of institute1
    institute1.add_member(testuser2, "member")
    institute2.add_member(testuser3, "member")

    # testuser1.save()
    # testuser2.save()
    # testuser3.save()


def cleanup():
    """
    Clean up any temporary file storage
    """
    pass


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


