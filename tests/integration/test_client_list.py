import boto3
import os
import requests


class TestClientList(object):
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
        response = requests.get(
            endpoint + '/client/list',
            headers={
                'Authorization': f'Bearer {id_token}'
            },
            params={
                'start': '1',
                'end': '123'
            }
        )
        data = response.json()
        assert response.status_code == 200
        assert data['start'] == 1
        assert data['end'] == 123

    def test_return_401_invalid_jwt(self, endpoint):
        id_token = 'HOGE'
        response = requests.get(
            endpoint + '/client/list',
            headers={
                'Authorization': f'Bearer {id_token}'
            },
            params={
                'start': '1',
                'end': '123'
            }
        )
        data = response.json()
        assert response.status_code == 401
        assert data['error_message'] == 'invalid jwt token'
