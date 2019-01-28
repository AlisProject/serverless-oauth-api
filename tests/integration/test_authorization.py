import boto3
import json
import os
import random
import requests
import string
from .common import api_deploy, api_remove, get_endpoint_url
from .conftest import option

class TestAuthorization(object):
    def __get_id_token(self):
        client = boto3.client('cognito-idp')
        result = client.admin_initiate_auth(
                UserPoolId = os.environ['TEST_COGNITO_USER_POOL_ID'],
                ClientId = os.environ['TEST_COGNITO_CLIENT_ID'],
                AuthFlow = "ADMIN_NO_SRP_AUTH",
                AuthParameters = {
                    "USERNAME": os.environ['TEST_COGNITO_USER_ID'],
                    "PASSWORD": os.environ['TEST_COGNITO_USER_PASSWORD']
                    }
                )
        return result['AuthenticationResult']['IdToken']

    def test_return_200(self, endpoint):
        id_token = self.__get_id_token()
        response = requests.post(
            endpoint + '/authorization',
            headers={
                'Authorization': f'Bearer {id_token}'
            },
            data={
                'response_type': 'code',
                'client_id': os.environ['TEST_AUTHLETE_CLIENT_ID'],
                'redirect_uri': 'http://localhost',
                'scope': 'openid read',
                'code_challenge': 'hcCb3gToI1GPZeS_SIYWvaNT_5u0GB1oqOGQJqRKMSE',
                'code_challenge_method': 'S256',
                'subject': 'fugafuga',
                'sub': 'hogehgoe'
            }
        )
        data = response.json()
        assert response.status_code == 200
        assert 'authorizationCode' in data

    def test_return_401_invalid_jwt(self, endpoint):
        id_token = 'xxxxxx'
        response = requests.post(
            endpoint + '/authorization',
            headers={
                'Authorization': f'Bearer {id_token}'
            },
            data={
                'response_type': 'code',
                'client_id': os.environ['TEST_AUTHLETE_CLIENT_ID'],
                'redirect_uri': 'http://localhost',
                'scope': 'openid read',
                'code_challenge': 'hcCb3gToI1GPZeS_SIYWvaNT_5u0GB1oqOGQJqRKMSE',
                'code_challenge_method': 'S256',
                'subject': 'fugafuga',
                'sub': 'hogehgoe'
            }
        )
        data = response.json()
        assert response.status_code == 401
        assert data['error_message'] == 'invalid jwt token'

    def test_return_400_authlete_param_error(self, endpoint):
        id_token = self.__get_id_token()
        response = requests.post(
            endpoint + '/authorization',
            headers={
                'Authorization': f'Bearer {id_token}'
            },
            data={
                'response_type': 'code',
                'client_id': '12345',
                'redirect_uri': 'http://localhost',
                'scope': 'openid read',
                'code_challenge': 'hcCb3gToI1GPZeS_SIYWvaNT_5u0GB1oqOGQJqRKMSE',
                'code_challenge_method': 'S256',
                'subject': 'fugafuga',
                'sub': 'hogehgoe'
            }
        )
        data = response.json()
        assert response.status_code == 400
        assert data['resultMessage'].find("No client has the client ID") > -1
