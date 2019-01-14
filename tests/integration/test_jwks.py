import string
import random
import requests
import json
import boto3
from .common import api_deploy, api_remove, get_endpoint_url
from .conftest import option

class TestGetJwkInformation(object):
    def test_return_200(self, endpoint):
        response = requests.get(
            endpoint + '/jwks'
        )
        data = response.json()

        assert response.status_code == 200
        assert 'keys' in data
