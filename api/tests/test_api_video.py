from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APIRequestFactory, APIClient
from rest_framework import status
from .test_setup_db import InitTestCase
# Create your tests here.
from .test_api_camera_config import cam_config
import json


class VideoListViewTests(InitTestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_video_login_basic_auth(self):
        """
        If no questions exist, an appropriate message is displayed.
        """
        # try to create/list records
        client = APIClient()
        client.login(username='testuser', password='test1234')

        # create a site
        client.post(
            '/api/site/',
            {"name": "geul", "geom": "SRID=4326;POINT (5.914115954402695 50.80678292086996)"}
        )
        r = client.post('/api/cameraconfig/',{"name": "geul_cam","site": 1,"end_date": "2024-01-01","camera_config": json.dumps(cam_config)})

        # create a camera config on site


