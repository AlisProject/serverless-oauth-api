import requests
import boto3
import os
import json
from .common import get_access_token

class TestIntrospection(object):
    def setup(self):
        self.access_token = get_access_token()

    def test_return_200_with_success(self, endpoint):
        response = requests.post(
            url=endpoint + '/introspection',
            data='token='+self.access_token
        )
        assert response.status_code == 200

        data = response.json()
        assert 'active' in data
        assert data['active'] is True

    def test_return_200_with_false(self, endpoint):
        response = requests.post(
            url=endpoint + '/introspection',
            data='token=xxxxxxx'
        )
        assert response.status_code == 200

        data = response.json()
        assert 'active' in data
        assert data['active'] is False

    def test_return_400_without_token(self, endpoint):
        response = requests.post(
            url=endpoint + '/introspection',
            data='aaaaa=xxxxxxx'
        )
        assert response.status_code == 400

        data = response.json()
        assert data['error_message'] == 'Missing token patameter'
