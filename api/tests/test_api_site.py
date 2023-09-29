from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APIRequestFactory, APIClient
from rest_framework import status
from .test_setup_db import InitTestCase
# Create your tests here.

class SiteListViewTests(InitTestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_site_not_allowed(self):
        """
        If no questions exist, an appropriate message is displayed.
        """
        # try to create/list records
        client = APIClient()
        r = client.post(
            '/api/site/',
            {"name": "geul", "geom": "SRID=4326;POINT (5.914115954402695 50.80678292086996)"}
        )
        self.assertEquals(r.status_code, status.HTTP_401_UNAUTHORIZED)
        r = client.get('/api/site/')
        self.assertEquals(r.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_site_login_basic_auth(self):
        client = APIClient()
        client.login(username='testuser', password='test1234')
        r = client.post(
            '/api/site/',
            {"name": "geul", "geom": "SRID=4326;POINT (5.914115954402695 50.80678292086996)"},
            follow=True
        )
        self.assertEquals(r.status_code, status.HTTP_201_CREATED)
        r = client.get('/api/site/', follow=True)
        self.assertEquals(r.status_code, status.HTTP_200_OK)
        r = client.get('/api/site/1', follow=True)
        self.assertEquals(r.status_code, status.HTTP_200_OK)
        self.assertEquals(r.json()["name"], "geul")

    def test_site_tokenized_auth(self):
        client = APIClient()
        r = client.post('/api/token/', {"username": "testuser", "password": "test1234"})
        token = r.json()["access"]
        headers = {"Authorization": f"Bearer {token}"}
        # now use token instead of basic auth
        r = client.post(
            '/api/site/',
            {"name": "geul", "geom": "SRID=4326;POINT (5.914115954402695 50.80678292086996)"},
            follow=True,
            headers=headers
        )
        self.assertEquals(r.status_code, status.HTTP_201_CREATED)
        r = client.get('/api/site/', follow=True, headers=headers)
        print(r.json())
        self.assertEquals(r.status_code, status.HTTP_200_OK)
        r = client.get('/api/site/1', follow=True, headers=headers)
        self.assertEquals(r.status_code, status.HTTP_200_OK)
        self.assertEquals(r.json()["name"], "geul")


