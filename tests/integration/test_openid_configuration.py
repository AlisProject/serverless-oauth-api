import string
import random
import requests
import json
import boto3
from .common import api_deploy, api_remove, get_endpoint_url
from .conftest import option


class TestOpenidConfiguration(object):
    def test_return_200(self, endpoint):
        response = requests.get(
            endpoint + '/.well-known/openid-configuration'
        )
        data = response.json()

        assert response.status_code == 200
        assert 'issuer' in data
        assert 'authorization_endpoint' in data
        assert 'token_endpoint' in data
        assert 'userinfo_endpoint' in data
        assert 'jwks_uri' in data
