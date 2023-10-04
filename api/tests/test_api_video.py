from rest_framework import status
from rest_framework.test import APIRequestFactory, APIClient
from django.contrib.gis.geos import Point
from django.core.files.uploadedfile import SimpleUploadedFile
from .test_setup_db import InitTestCase
# Create your tests here.
from ..models import Site, Recipe, Profile
from io import BytesIO
from datetime import datetime
import json
import os
import requests

# get some data for filling in the dbase
from .test_api_recipe import recipe
from .test_api_profile import profile


video_sample_url = "https://raw.githubusercontent.com/localdevices/pyorc/main/examples/ngwerere/ngwerere_20191103.mp4"
camconfig_url = "https://raw.githubusercontent.com/localdevices/pyorc/main/examples/ngwerere/ngwerere.json"

def prep_video_sample(video_sample_url):
    filename = os.path.split(video_sample_url)[-1]
    print(f"Downloading {video_sample_url}")
    r = requests.get(video_sample_url)
    obj = r.content
    # obj = BytesIO(r.content)
    # obj.seek(0)
    video_file = SimpleUploadedFile("ngwerere.mp4", obj, content_type="video/mp4")
    # files = {
    #     "file": video_file,
    # }
    msg = {
        "timestamp": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "camera_config": 1,
        "file": video_file
    }
    return msg


def camconfig(camconfig_url):
    r = requests.get(camconfig_url)
    return r.json()


camera_config = camconfig(camconfig_url)
video_sample = prep_video_sample(video_sample_url)

camera_config_form = {
    "name": "ngwerere_cam",
    "site": 1,
    "end_date": "2099-01-01",
    "camera_config": json.dumps(camera_config),
    "recipe": 1,
    "profile": 1
}


class VideoListViewTests(InitTestCase):
    def setUp(self):
        site = Site.objects.create(name="ngwerere", geom=Point(28.329686, -15.334151))
        Recipe.objects.create(name="ngwerere_recipe", data=recipe)
        Profile.objects.create(name="some_profile", data=profile, site=site)
        # pass
    def tearDown(self):
        pass


    # def setUpTestData(self):
    #     # TODO add user/group

    # def test_video_login_basic_auth(self):
    #     """
    #     If no questions exist, an appropriate message is displayed.
    #     """
    #     # try to create/list records
    #     client = APIClient()
    #     client.login(username='testuser', password='test1234')
    #     # create a site
    #     client.post(
    #         '/api/site/',
    #         {"name": "ngwerere", "geom": "SRID=4326;POINT (28.329686, -15.334151)"}
    #     )

    def test_add_camconfig(self):
        client = APIClient()
        client.login(username='testuser', password='test1234')
        # create a camera config on site
        r = client.post(
            '/api/site/1/cameraconfig/',
            camera_config_form
        )
        # print(r.json())
        # print(json.dumps(data))
        # post a video
        r = client.post(
            "/api/video/",
            data=video_sample
        )
        self.assertEquals(r.status_code, status.HTTP_201_CREATED)
        r = client.get("/api/site/1/video/1/")
        self.assertEquals(r.status_code, status.HTTP_200_OK)





