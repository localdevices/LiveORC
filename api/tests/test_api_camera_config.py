from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APIRequestFactory, APIClient
from rest_framework import status
from .test_setup_db import InitTestCase
# Create your tests here.

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



class CameraConfigListViewTests(InitTestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_camera_config_not_allowed(self):
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
        import json
        r = client.post('/api/cameraconfig/',{"name": "geul_cam","site": 1,"end_date": "2024-01-01","camera_config": json.dumps(cam_config)})

        # create a camera config on site


