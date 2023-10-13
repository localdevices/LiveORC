from rest_framework import status
from rest_framework.test import APIRequestFactory, APIClient
from datetime import datetime

from .test_setup_db import InitTestCase
from ..models import Site
from django.contrib.gis.geos import Point
from users.models import User


class TimeSeriesViewTests(InitTestCase):
    def setUp(self):
        user = User.objects.get(pk=2)
        site = Site.objects.create(name="ngwerere", geom=Point(28.329686, -15.334151), creator=user)

    def tearDown(self):
        pass

    def test_add_timeseries(self):
        client = APIClient()
        client.login(username='user@institute1.com', password='test1234')
        # create a camera config on site
        r = client.post(
            '/api/site/1/timeseries/',
            data={
                "h": 0.0,
                "timestamp": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
            }
        )
        self.assertEquals(r.status_code, status.HTTP_201_CREATED)
