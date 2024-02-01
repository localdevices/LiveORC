from rest_framework.test import APIRequestFactory, APIClient
from django.contrib.gis.geos import Point
from .test_setup_db import InitTestCase
from rest_framework import status
# Create your tests here.
from api.models import Site
from users.models import User, Institute


import json
import os

def get_recipe(recipe_file):
    with open(recipe_file, "r") as f:
        return json.loads(f.read())


recipe_file = os.path.join(os.path.split(__file__)[0], "testdata", "ngwerere_recipe.json")
recipe = get_recipe(recipe_file)


class RecipeViewTests(InitTestCase):
    def setUp(self):
        user = User.objects.get(pk=2)
        institute = Institute.objects.get(pk=1)
        Site.objects.create(name="ngwerere", geom=Point(28.329686, -15.334151), creator=user, institute=institute)

        # pass
    def tearDown(self):
        pass

    def test_add_recipe(self):
        client = APIClient()
        client.login(username='user@institute1.com', password='test1234')
        # create a camera config on site
        r = client.post(
            '/api/recipe/',
            {
                "name": "general_recipe",
                "data": json.dumps(recipe),
                "institute": 1
            }
        )
        # check the request
        self.assertEquals(r.status_code, status.HTTP_201_CREATED)


