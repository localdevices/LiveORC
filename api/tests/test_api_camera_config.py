import json
import os
import uuid

from rest_framework.test import APIClient
from rest_framework import status
from .test_setup_db import InitTestCase

from .test_api_device import get_device_data
# Create your tests here.

from api.models import TaskForm, TaskFormStatus

cam_config = {
            "height": 1080,
            "width": 1920,
            "crs": "PROJCRS[\"Amersfoort / RD New\",BASEGEOGCRS[\"Amersfoort\",DATUM[\"Amersfoort\",ELLIPSOID[\"Bessel 1841\",6377397.155,299.1528128,LENGTHUNIT[\"metre\",1]]],PRIMEM[\"Greenwich\",0,ANGLEUNIT[\"degree\",0.0174532925199433]],ID[\"EPSG\",4289]],CONVERSION[\"RD New\",METHOD[\"Oblique Stereographic\",ID[\"EPSG\",9809]],PARAMETER[\"Latitude of natural origin\",52.1561605555556,ANGLEUNIT[\"degree\",0.0174532925199433],ID[\"EPSG\",8801]],PARAMETER[\"Longitude of natural origin\",5.38763888888889,ANGLEUNIT[\"degree\",0.0174532925199433],ID[\"EPSG\",8802]],PARAMETER[\"Scale factor at natural origin\",0.9999079,SCALEUNIT[\"unity\",1],ID[\"EPSG\",8805]],PARAMETER[\"False easting\",155000,LENGTHUNIT[\"metre\",1],ID[\"EPSG\",8806]],PARAMETER[\"False northing\",463000,LENGTHUNIT[\"metre\",1],ID[\"EPSG\",8807]]],CS[Cartesian,2],AXIS[\"easting (X)\",east,ORDER[1],LENGTHUNIT[\"metre\",1]],AXIS[\"northing (Y)\",north,ORDER[2],LENGTHUNIT[\"metre\",1]],USAGE[SCOPE[\"Engineering survey, topographic mapping.\"],AREA[\"Netherlands - onshore, including Waddenzee, Dutch Wadden Islands and 12-mile offshore coastal zone.\"],BBOX[50.75,3.2,53.7,7.22]],ID[\"EPSG\",28992]]",
            "resolution": 0.03,
            "lens_position": [
                192114.2861118754,
                313151.062216843,
                142.8365
            ],
            "gcps": {
                "src": [
                    [
                        1650,
                        624
                    ],
                    [
                        740,
                        320
                    ],
                    [
                        703,
                        166
                    ],
                    [
                        1062,
                        228
                    ],
                    [
                        1140,
                        204
                    ],
                    [
                        1674,
                        343
                    ]
                ],
                "dst": [
                    [
                        192111.36369042983,
                        313157.71636298846,
                        138.9234814814815
                    ],
                    [
                        192102.85935356488,
                        313152.9800096405,
                        138.526
                    ],
                    [
                        192100.1640354367,
                        313153.16390758357,
                        139.68307692307692
                    ],
                    [
                        192099.9702815698,
                        313158.9153213168,
                        138.45433333333332
                    ],
                    [
                        192098.38713148457,
                        313161.31339320523,
                        138.51090909090908
                    ],
                    [
                        192106.66182086038,
                        313165.6410030764,
                        138.5616
                    ]
                ],
                "h_ref": 92.36,
                "z_0": 138.27
            },
            "window_size": 20,
            "dist_coeffs": [
                [
                    0.0
                ],
                [
                    0.0
                ],
                [
                    0.0
                ],
                [
                    0.0
                ]
            ],
            "camera_matrix": [
                [
                    960.7855224609375,
                    0.0,
                    960.0
                ],
                [
                    0.0,
                    960.7855224609375,
                    540.0
                ],
                [
                    0.0,
                    0.0,
                    1.0
                ]
            ],
            "bbox": "POLYGON ((192105.83143541854 313146.7594177593, 192097.9736885897 313162.8536376775, 192106.27690422587 313166.9075506143, 192114.13465105472 313150.81333069614, 192105.83143541854 313146.7594177593))"
        }

recipe_file = os.path.join(
    os.path.dirname(__file__),
    "testdata",
    "hommerich_recipe.json"
)
profile_file = os.path.join(
    os.path.dirname(__file__),
    "testdata",
    "hommerich_profile.geojson"
)


with open(recipe_file, "r") as f:
    recipe = json.loads(f.read())

with open(profile_file, "r") as f:
    profile = json.loads(f.read())


class CameraConfigViewTests(InitTestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_camera_config(self):
        """
        If no questions exist, an appropriate message is displayed.
        """
        # try to create/list records
        client = APIClient()
        client.login(username='user@institute1.com', password='test1234')

        # create a site
        r = client.post(
            '/api/site/',
            {"name": "geul", "geom": "SRID=4326;POINT (5.914115954402695 50.80678292086996)", "institute": 1}
        )
        # make a profile and recipe
        r = client.post(
            '/api/site/1/profile/',
            {
                "name": "some_profile",
                "data": json.dumps(profile),
                "institute": 1}
        )
        self.assertEquals(r.status_code, status.HTTP_201_CREATED)
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

        # make a camera_config, with profile and recipe included
        r = client.post(
            '/api/site/1/cameraconfig/',
            {
                "name": "geul_cam",
                "end_date": "2024-01-01",
                "camera_config": json.dumps(cam_config),
                "profile": 1,
                "recipe": 1,
                "nodeorc_version": "0.1.0"
            }
        )
        self.assertEquals(r.status_code, status.HTTP_201_CREATED)
        # make a device with which we can test the task_form creation
        data = get_device_data()
        r = client.post(
            '/api/device/',
            data,
        )
        device_id = r.json()["id"]
        device_details = r.json()
        # remove non-serializable parts
        device_details.pop("message")
        # now see if a task_form can be produced using the current camera_config
        r = client.post(
            f'/api/site/1/cameraconfig/1/create_task/?device_id={device_id}&callback=discharge_post&callback=video_no_file_post',
        )
        self.assertEquals(r.status_code, status.HTTP_201_CREATED)
        # now request the prepared task form as device
        new_device_details = get_device_data()
        new_device_id = new_device_details["id"]
        # new_device_id = uuid.uuid4()
        # new_device_details = device_details
        # new_device_details["id"] = new_device_id
        url = f"/api/device/{new_device_id}/get_task_form/"
        r = client.get(
            url,
            data=new_device_details,
        )
        self.assertEquals(r.status_code, status.HTTP_204_NO_CONTENT)

        url = f"/api/device/{device_id}/get_task_form/"
        r = client.get(
            url,
            data=device_details
        )
        # patch the task form
        url = f"/api/device/{device_id}/patch_task_form/"
        task_id = r.json()["id"]
        r = client.patch(
            url,
            data={
                "id": task_id,
                "status": 3
            },
        )
        self.assertEquals(r.status_code, status.HTTP_200_OK)
        # check if the taskform indeed now is stored as ACCEPTED in the database
        self.assertEquals(
            TaskFormStatus(TaskForm.objects.get(pk=task_id).status),
            TaskFormStatus.ACCEPTED
        )
        # check the status of the task in the background
        # finally check if other user cannot access
        client.logout()
        client.login(
            username='user2@institute1.com',
            password='test1234'
        )
        r = client.post(
            '/api/site/1/cameraconfig/',
            {
                "name": "geul_cam2",
                "end_date": "2024-01-01",
                "camera_config": json.dumps(cam_config)
            }
        )
        self.assertEqual(r.status_code, status.HTTP_403_FORBIDDEN)


