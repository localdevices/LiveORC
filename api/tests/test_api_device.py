import platform
import psutil
import requests
import uuid

from rest_framework.test import APIRequestFactory, APIClient
from rest_framework import status

from .test_setup_db import InitTestCase
from users.models import User, Institute

def get_ip():
    return requests.get('https://api.ipify.org').content.decode('utf8')

def get_device_data():
    data = {
        "id": str(uuid.uuid4()),
        "name": "TEST_DEVICE",
        "operating_system": platform.platform(),
        "processor": platform.processor(),
        "memory": psutil.virtual_memory().total / (1024**3),
        "ip_address": get_ip(),
    }
    return data

class DeviceTests(InitTestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_add_device(self):
        client = APIClient()
        client.login(username='user@institute1.com', password='test1234')
        # create a camera config on site
        data = get_device_data()
        r = client.post(
            '/api/device/',
            data,
        )
        # check the request
        self.assertEquals(r.status_code, status.HTTP_201_CREATED)


