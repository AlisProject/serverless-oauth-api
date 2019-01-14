import requests
import boto3
import os
import json
from .common import get_access_token

class TestUserInfo(object):
    def setup(self):
        self.access_token = get_access_token()

    def test_return_200(self, endpoint):
        response = requests.get(
            url=endpoint + '/userinfo',
            headers={'Authorization':'Bearer ' + self.access_token}
        )
        assert response.status_code == 200

        data = response.json()
        assert 'sub' in data
        assert 'name' in data
        assert data['name'] == os.environ['TEST_COGNITO_USER_ID']

    def test_return_401_without_authorization(self, endpoint):
        response = requests.get(
            url=endpoint + '/userinfo',
        )
        assert response.status_code == 401

    def test_return_401_with_missed_authorization(self, endpoint):
        response = requests.get(
            url=endpoint + '/userinfo',
            headers={'Authorization':'Basic ' + self.access_token}
        )
        assert response.status_code == 401

    def test_return_401_with_fake_accesstoken(self, endpoint):
        response = requests.get(
            url=endpoint + '/userinfo',
            headers={'Authorization':'Bearer xxxxxxxxxxxxxxx'}
        )
        assert response.status_code == 401
