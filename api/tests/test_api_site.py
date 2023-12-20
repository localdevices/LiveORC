from rest_framework.test import APIClient, APITestCase
from rest_framework import status
from .test_setup_db import InitTestCase
# Create your tests here.


class SiteViewTests(InitTestCase):
    def setUp(self):
        self.client = APIClient()

    def tearDown(self):
        pass

    def test_site_not_allowed(self):
        """
        If no questions exist, an appropriate message is displayed.
        """
        # try to create/list records
        # client = APIClient()
        r = self.client.post(
            '/api/site/',
            {"name": "geul", "geom": "SRID=4326;POINT (5.914115954402695 50.80678292086996)"}
        )
        self.assertEqual(r.status_code, status.HTTP_401_UNAUTHORIZED)
        r = self.client.get('/api/site/')
        self.assertEqual(r.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_site_login_basic_auth(self):
        # client = APIClient()
        self.client.login(username='user@institute1.com', password='test1234')
        r = self.client.post(
            '/api/site/',
            {"name": "geul", "geom": "SRID=4326;POINT (5.914115954402695 50.80678292086996)", "institute": 1},
            follow=True
        )
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)
        r = self.client.get('/api/site/?institute=1', follow=True)
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        r = self.client.get('/api/site/1/', follow=True)
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertEqual(r.json()["name"], "geul")
        # now check if the user within the same institute can read, but not modify the site instance
        self.client.logout()
        self.client.login(username='user2@institute1.com', password='test1234')
        r = self.client.get('/api/site/1/', follow=True)
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        r = self.client.patch(
            '/api/site/1/',
            data={"name": "Hommerich"},
            follow=True
        )
        self.assertEqual(r.status_code, status.HTTP_403_FORBIDDEN)
        # now check if the original user is able to do the patch instead
        self.client.logout()
        self.client.login(username='user@institute1.com', password='test1234')
        r = self.client.patch(
            '/api/site/1/',
            data={"name": "Hommerich"},
            follow=True
        )
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        # now logout again and test if the user from a different institute cannot even read the record
        self.client.logout()
        self.client.login(username='user3@institute2.com', password='test1234')
        r = self.client.get('/api/site/1/', follow=True)
        self.assertEqual(r.status_code, status.HTTP_403_FORBIDDEN)

    def test_site_tokenized_auth(self):
        client = APIClient()
        r = client.post('/api/token/', {"email": "user@institute1.com", "password": "test1234"})
        token = r.json()["access"]
        headers = {"Authorization": f"Bearer {token}"}
        # now use token instead of basic auth
        r = client.post(
            '/api/site/',
            {"name": "geul", "geom": "SRID=4326;POINT (5.914115954402695 50.80678292086996)", "institute": 1},
            follow=True,
            headers=headers
        )
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)
        r = client.get('/api/site/', follow=True, headers=headers)
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        r = client.get('/api/site/1/', follow=True, headers=headers)
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertEqual(r.json()["name"], "geul")
        # again test if user 2 has access and user 3 not
        r = client.post('/api/token/', {"email": "user2@institute1.com", "password": "test1234"})
        token = r.json()["access"]
        headers = {"Authorization": f"Bearer {token}"}
        r = client.get('/api/site/1', follow=True, headers=headers)
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        r = client.post('/api/token/', {"email": "user3@institute2.com", "password": "test1234"})
        token = r.json()["access"]
        headers = {"Authorization": f"Bearer {token}"}
        r = client.get('/api/site/1', follow=True, headers=headers)
        self.assertEqual(r.status_code, status.HTTP_403_FORBIDDEN)



