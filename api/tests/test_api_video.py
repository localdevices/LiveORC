from django.test import client
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.gis.geos import Point
from django.core.files.uploadedfile import SimpleUploadedFile
from .test_setup_db import InitTestCase
# Create your tests here.
from api.models import Site, Recipe, CrossSection
from users.models import User, Institute
from datetime import datetime
import json
import os
import requests

# get some data for filling in the dbase
from .test_api_recipe import recipe
from .test_api_profile import profile


video_sample_url = "https://raw.githubusercontent.com/localdevices/pyorc/main/examples/ngwerere/ngwerere_20191103.mp4"
camconfig_url = "https://raw.githubusercontent.com/localdevices/pyorc/main/examples/ngwerere/ngwerere.json"
image_sample_url = "https://raw.githubusercontent.com/localdevices/pyorc/main/docs/ngwerere.jpg"
result_2d_sample_url = "https://raw.githubusercontent.com/localdevices/pyorc/main/examples/ngwerere_piv.nc"
result_2d_mask_url = "https://raw.githubusercontent.com/localdevices/pyorc/main/examples/ngwerere_masked.nc"


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
        "video_config": 1,
        "file": video_file
    }
    return msg

def prep_no_files_sample():
    msg = {
        "timestamp": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "video_config": 1,
    }
    return msg

def prep_image_sample(image_sample_url):
    filename = os.path.split(image_sample_url)[-1]
    print(f"Downloading {image_sample_url}")
    r = requests.get(image_sample_url)
    obj = r.content
    image_file = SimpleUploadedFile("ngwerere_result.jpg", obj, content_type="image/jpeg")
    # files = {
    #     "file": video_file,
    # }
    msg = {
        "timestamp": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "video_config": 1,
        "image": image_file
    }
    return msg

def prep_results_sample():
    src_urls = [result_2d_sample_url, result_2d_mask_url]
    dst_fns = ["2d.nc", "2d_mask.nc"]
    # prepare basic fields of msg content
    msg = {
        "timestamp": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "video_config": 1,
    }

    for url, fn in zip(src_urls, dst_fns):
        print(f"Downloading {url}")
        r = requests.get(url)
        obj = r.content
        result_file = SimpleUploadedFile(fn, obj, content_type="application/x-netcdf")
        msg[f"result_{os.path.split(fn)[-1].replace('.nc', '')}"] = result_file
    return msg



def camconfig(camconfig_url):
    r = requests.get(camconfig_url)
    return r.json()


camera_config = camconfig(camconfig_url)
video_sample = prep_video_sample(video_sample_url)
image_sample = prep_image_sample(image_sample_url)
results_sample = prep_results_sample()

# test also patching an already existing video with results
results_sample_patch = {
    "results_2d": results_sample["result_2d"],
    "results_2d_mask": results_sample["result_2d_mask"],
    "log_file": SimpleUploadedFile("orc.log", b"Some log content", content_type="text/plain")
}


no_files_sample = prep_no_files_sample()

camera_config_form = {
    "name": "ngwerere_cam",
    "site": 1,
    "end_date": "2099-01-01",
    "camera_config": json.dumps(camera_config),
}

video_config_form = {
    "name": "ngwerere_video_config",
    "camera_config": 1,
    "recipe": 1,
    "cross_section": 1,
}


class VideoViewTests(InitTestCase):
    def setUp(self):
        user = User.objects.get(pk=2)
        institute = Institute.objects.get(pk=1)
        site = Site.objects.create(name="ngwerere", geom=Point(28.329686, -15.334151), creator=user, institute=institute)
        Recipe.objects.create(name="ngwerere_recipe", data=recipe, creator=user, institute=institute)
        CrossSection.objects.create(name="some_cross_section", features=profile, site=site, creator=user)

    def tearDown(self):
        pass

    def test_add_video_patch_results(self):
        client = APIClient()
        client.login(username='user@institute1.com', password='test1234')
        # create a camera config on site
        r = client.post(
            '/api/site/1/cameraconfig/',
            camera_config_form
        )
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)
        r = client.post('/api/site/1/videoconfig/', video_config_form)
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)
        # post a video
        r = client.post(
            "/api/video/",
            data=video_sample
        )
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)
        # check if file is there, but image not
        self.assertIsNotNone(r.data["file"])
        self.assertIsNone(r.data["image"])
        self.assertIsNotNone(r.data["thumbnail"])

        r = client.get("/api/site/1/video/1/")
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        # make sure a second user with membership can see but not alter the video
        client.logout()
        client.login(username='user2@institute1.com', password='test1234')
        r = client.get("/api/site/1/video/1/")
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        r = client.patch(
            '/api/site/1/video/1/',
            data={"timestamp": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")}
            # follow=True
        )
        self.assertEqual(r.status_code, status.HTTP_403_FORBIDDEN)
        client.logout()
        client.login(username='user3@institute2.com', password='test1234')
        r = client.get("/api/site/1/video/1/")
        self.assertEqual(r.status_code, status.HTTP_403_FORBIDDEN)
        r = client.patch(
            '/api/site/1/video/1/',
            data={"timestamp": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")}
            # follow=True
        )
        self.assertEqual(r.status_code, status.HTTP_403_FORBIDDEN)
        client.logout()
        # log back in as original posting user and patch the video with results
        client.login(username='user@institute1.com', password='test1234')
        # now patch the video with new information
        r = client.patch(
            '/api/site/1/video/1/',
            data=results_sample_patch,
            # follow=True
        )
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        # also check presence of result files
        r = client.get("/api/site/1/video/1/result_2d/")
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        # check the content of the log file
        r = client.get("/api/site/1/video/1/log_file/")
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertIn("Some log content", r.content.decode())

    def test_add_image(self):
        client = APIClient()
        client.login(username='user@institute1.com', password='test1234')
        # create a camera config on site
        r = client.post(
            '/api/site/1/cameraconfig/',
            camera_config_form
        )
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)
        r = client.post('/api/site/1/videoconfig/', video_config_form)
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)
        # post a video with only the result image instead of full video
        r = client.post(
            "/api/video/",
            data=image_sample
        )
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)
        r = client.get("/api/site/1/video/1/")
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        # check if image is there, but file not
        self.assertIsNotNone(r.data["image"])
        self.assertIsNone(r.data["file"])
        self.assertIsNotNone(r.data["thumbnail"])
        # there should not be any result files yet, check this
        r = client.get("/api/site/1/video/1/result_2d/")
        self.assertEqual(r.status_code, status.HTTP_404_NOT_FOUND)
        assert "No result file" in r.text

    def test_add_no_files(self):
        client = APIClient()
        client.login(username='user@institute1.com', password='test1234')
        # create a camera config on site
        r = client.post(
            '/api/site/1/cameraconfig/',
            camera_config_form
        )
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)
        r = client.post('/api/site/1/videoconfig/', video_config_form)
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)
        # post a video with only the result image instead of full video
        r = client.post(
            "/api/video/",
            data=no_files_sample
        )
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)
        r = client.get("/api/site/1/video/1/")
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        # check if no files are present
        self.assertIsNone(r.data["file"])
        self.assertIsNone(r.data["image"])
        self.assertIsNone(r.data["thumbnail"])

    def test_add_results(self):
        client = APIClient()
        client.login(username='user@institute1.com', password='test1234')
        # create a camera config on site
        r = client.post(
            '/api/site/1/cameraconfig/',
            camera_config_form
        )
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)
        r = client.post('/api/site/1/videoconfig/', video_config_form)
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)
        # post a video with only the result image instead of full video
        r = client.post(
            "/api/video/",
            data=results_sample
        )
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)
        r = client.get("/api/site/1/video/1/")
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        # check if image is there, but file not
        self.assertIsNone(r.data["image"])
        self.assertIsNone(r.data["file"])
        self.assertIsNone(r.data["thumbnail"])
        # there should be a result in result_2d but not in result_1d as that was not included
        r = client.get("/api/site/1/video/1/result_2d/")
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        r = client.get("/api/site/1/video/1/result_1d/")
        self.assertEqual(r.status_code, status.HTTP_404_NOT_FOUND)




