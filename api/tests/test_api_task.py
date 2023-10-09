from django.contrib.gis.geos import Point
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

# fixtures
from .test_setup_db import InitTestCase
from .test_api_recipe import recipe
from .test_api_profile import profile
from .test_api_video import camera_config_form, prep_video_sample, video_sample_url

from ..models import Site, Recipe, Profile, Video, VideoStatus, Task

video_sample = prep_video_sample(video_sample_url)
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
        # as there is no water level yet, this should give a 400 error
        self.assertEquals(r.status_code, status.HTTP_400_BAD_REQUEST)
        timestamp = video_sample["timestamp"]
        # some fake water level
        h = 1182.3
        # now add the water level
        uri = reverse("api:site-timeseries-list", args=(["1"]))
        r = client.post(
            uri,
            data={
                "timestamp": timestamp,
                "h": h
            }
        )
        self.assertEquals(r.status_code, status.HTTP_201_CREATED)
        # Upon creation of a time series close in time to the video, the two should be automatically linked.
        # check if the video now has a time series associated with it. At this stage, the status should still be NEW
        # because no task is initiated yet.
        video = Video.objects.get(id=1)
        self.assertEquals(video.time_series is not None, True)
        self.assertEquals(video.status, VideoStatus.QUEUE)
        # One task should be made, check if there is indeed a total of one tasks in the full queryset
        self.assertEquals(len(Task.objects.all()), 1)



