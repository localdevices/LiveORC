from rest_framework.test import APIRequestFactory, APIClient
from django.contrib.gis.geos import Point
from .test_setup_db import InitTestCase
from rest_framework import status
# Create your tests here.
from ..models import Site

import json
import os

def get_recipe(recipe_file):
    with open(recipe_file, "r") as f:
        return json.loads(f.read())


recipe_file = os.path.join(os.path.split(__file__)[0], "testdata", "ngwerere_recipe.json")
recipe = get_recipe(recipe_file)


class RecipeTests(InitTestCase):
    def setUp(self):
        Site.objects.create(name="ngwerere", geom=Point(28.329686, -15.334151))

        # pass
    def tearDown(self):
        pass

    def test_add_recipe(self):
        client = APIClient()
        client.login(username='testuser', password='test1234')
        # create a camera config on site
        r = client.post('/api/recipe/',{"name": "general_recipe", "data": json.dumps(recipe)})
        # check the request
        self.assertEquals(r.status_code, status.HTTP_201_CREATED)

