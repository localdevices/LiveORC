from django.contrib.gis.geos import Point
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

# fixtures
from .test_setup_db import InitTestCase
from .test_api_recipe import recipe
from .test_api_profile import profile
from .test_api_video import camera_config_form, prep_video_sample, video_sample_url

from api.models import Site, Recipe, Profile, Video, VideoStatus, Task
from users.models import User, Institute

video_sample = prep_video_sample(video_sample_url)


class TaskViewTests(InitTestCase):
    def setUp(self):
        user = User.objects.get(pk=2)
        institute = Institute.objects.get(pk=1)
        site = Site.objects.create(name="ngwerere", geom=Point(28.329686, -15.334151), institute=institute, creator=user)
        Recipe.objects.create(name="ngwerere_recipe", data=recipe, institute=institute, creator=user)
        Profile.objects.create(name="some_profile", data=profile, site=site, creator=user)
        # pass
    def tearDown(self):
        pass

    def test_create_task(self):
        client = APIClient()
        client.login(username='user@institute1.com', password='test1234')
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
        # check if task creation is not possible as other user
        client.logout()
        client.login(username='user2@institute1.com', password='test1234')
        r = client.post(
            f'/api/site/1/video/{video_id}/task/'
        )
        self.assertEquals(r.status_code, status.HTTP_400_BAD_REQUEST)


