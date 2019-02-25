import boto3
import os
import requests
import json


class TestClientDelete(object):
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
        client_id = os.environ['TEST_AUTHLETE_SERVER_APP_CLIENT_ID']
        response = requests.post(
            endpoint + '/client/delete',
            headers={
                'Authorization': f'Bearer {id_token}',
                'Content-Type': 'application/json'
            },
            data=json.dumps({
                'clientid': client_id
            })
        )
        response_json = response.json()
        assert response.status_code == 200
        assert response_json["resultCode"] == "A137001" 

    def test_return_401_invalid_jwt(self, endpoint):
        id_token = 'HOGE'
        client_id = os.environ['TEST_AUTHLETE_SERVER_APP_CLIENT_ID']
        response = requests.post(
            endpoint + '/client/delete',
            headers={
                'Authorization': f'Bearer {id_token}',
                'Content-Type': 'application/json'
            },
            data=json.dumps({
                'clientid': client_id
            })
        )
        response_json = response.json()
        assert response.status_code == 401
        assert response_json['error_message'] == 'invalid jwt token'

    def test_return_400_invalid_client_id(self, endpoint):
        id_token = self.__get_id_token()
        client_id = "123"
        response = requests.post(
            endpoint + '/client/delete',
            headers={
                'Authorization': f'Bearer {id_token}',
                'Content-Type': 'application/json'
            },
            data=json.dumps({
                'clientid': client_id
            })
        )
        response_json = response.json()
        assert response.status_code == 400
        assert response_json['error_message'] == 'client id does not exist'
