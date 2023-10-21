from rest_framework.test import APIRequestFactory, APIClient
from django.contrib.gis.geos import Point
from .test_setup_db import InitTestCase
from rest_framework import status
# Create your tests here.
from users.models import User
from api.models import Site

import json
import os

def get_profile(profile_file):
    with open(profile_file, "r") as f:
        return json.loads(f.read())


profile_file = os.path.join(os.path.split(__file__)[0], "testdata", "ngwerere_profile.geojson")
profile = get_profile(profile_file)


class ProfileViewTests(InitTestCase):
    def setUp(self):
        user = User.objects.get(pk=2)
        Site.objects.create(name="ngwerere", geom=Point(28.329686, -15.334151), creator=user)

        # pass
    def tearDown(self):
        pass

    def test_add_recipe(self):
        client = APIClient()
        client.login(username='user@institute1.com', password='test1234')
        # create a camera config on site
        r = client.post('/api/site/1/profile/',{"name": "some_profile", "data": json.dumps(profile)})
        # check the request
        self.assertEquals(r.status_code, status.HTTP_201_CREATED)
        # check if user3 is not able to see the model
        client.logout()
        client.login(username="user3@institute2.com", password="test1234")
        r = client.get('/api/site/1/profile/1', follow=True)
        self.assertEquals(r.status_code, status.HTTP_403_FORBIDDEN)


