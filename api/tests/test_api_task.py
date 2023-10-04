from django.contrib.gis.geos import Point
from rest_framework.test import APIClient

# fixtures
from .test_setup_db import InitTestCase
from .test_api_recipe import recipe
from .test_api_profile import profile
from .test_api_video import video_sample, camera_config_form

from ..models import Site, Recipe, Profile, Video



class VideoListViewTests(InitTestCase):
    def setUp(self):
        site = Site.objects.create(name="ngwerere", geom=Point(28.329686, -15.334151))
        Recipe.objects.create(name="ngwerere_recipe", data=recipe)
        Profile.objects.create(name="some_profile", data=profile, site=site)
        # pass
    def tearDown(self):
        pass

    def test_create_task(self):
        client = APIClient()
        client.login(username='testuser', password='test1234')
        # create a camera config on site
        r = client.post(
            '/api/site/1/cameraconfig/',
            camera_config_form
        )
        # post a video
        r = client.post(
            "/api/video/",
            data=video_sample
        )
        video_id = r.json()["id"]
        # now also post a task, with
        r = client.post(
            f'/api/site/1/video/{video_id}/task/'
        )
