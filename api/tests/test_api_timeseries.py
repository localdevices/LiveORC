from datetime import datetime
import pandas as pd

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIRequestFactory, APIClient

from .test_setup_db import InitTestCase
from ..models import Site
from django.contrib.gis.geos import Point
from users.models import User, Institute


class TimeSeriesViewTests(InitTestCase):
    def setUp(self):
        user = User.objects.get(pk=2)
        institute = Institute.objects.get(pk=1)
        site = Site.objects.create(name="ngwerere", geom=Point(28.329686, -15.334151), creator=user, institute=institute)

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
        # check if other user can read but not write
        client.logout()
        client.login(username='user2@institute1.com', password='test1234')
        r = client.get(
            '/api/site/1/timeseries/1',
            follow=True
        )
        self.assertEquals(r.status_code, status.HTTP_200_OK)

        r = client.post(
            '/api/site/1/timeseries/',
            data={
                "h": 1.0,
                "timestamp": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
            }
        )
        self.assertEquals(r.status_code, status.HTTP_403_FORBIDDEN)


        client.logout()
        client.login(username='user3@institute2.com', password='test1234')
        r = client.get(
            '/api/site/1/timeseries/1',
            follow=True
        )
        self.assertEquals(r.status_code, status.HTTP_403_FORBIDDEN)

        r = client.post(
            '/api/site/1/timeseries/',
            data={
                "h": 1.0,
                "timestamp": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
            }
        )
        self.assertEquals(r.status_code, status.HTTP_403_FORBIDDEN)

    def test_add_longer_timeseries_and_query(self):
        client = APIClient()
        client.login(username='user@institute1.com', password='test1234')
        # create a camera config on site
        # make a date range
        dr = pd.date_range("2000-01-01", "2000-01-02", freq="h")
        for n, ts in enumerate(dr):
            r = client.post(
                '/api/site/1/timeseries/',
                data={
                    "h": float(n),
                    "timestamp": ts.strftime("%Y-%m-%dT%H:%M:%SZ")
                }
            )
        self.assertEquals(r.status_code, status.HTTP_201_CREATED)
        uri = reverse("api:site-timeseries-list", args=(["1"]))
        # query in PIJSON format
        r = client.get(
            uri + "?startDateTime=2000-01-01T04:00:00:00Z" + "&endDateTime=2000-01-01T07:00:00:00Z" + "&format=pijson"
        )
        self.assertEquals(len(r.json()), 3)  # test for number of fields in pijson (always 3)
        self.assertEquals(len(r.json()["timeSeries"]), 9)  # test for number of variables (currently 9)
        self.assertEquals(len(r.json()["timeSeries"][0]["events"]), 4)  # test for number of records
        # query in csv format
        r = client.get(
            uri + "?startDateTime=2000-01-01T04:00:00:00Z" + "&endDateTime=2000-01-01T07:00:00:00Z" + "&format=csv"
        )
        self.assertEquals(len(r.content), 277)
