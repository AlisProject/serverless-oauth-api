import requests
import boto3
import os
import json

class TestUserInfo(object):
    def setup(self):
        ssm = boto3.client('ssm')
        param = ssm.get_parameter(
            Name=os.environ['ALIS_APP_ID'] + 'ssmAutlteleApiKey'
        )
        authlete_api_key = param['Parameter']['Value']
        param = ssm.get_parameter(
            Name=os.environ['ALIS_APP_ID'] + 'ssmAutlteleApiSecret'
        )
        authlete_api_secret = param['Parameter']['Value']

        response = requests.post(
            url='https://api.authlete.com/api/auth/authorization',
            auth=(authlete_api_key, authlete_api_secret),
            headers={'content-type': 'application/json'},
            data=json.dumps({'parameters':'code_challenge=hcCb3gToI1GPZeS_SIYWvaNT_5u0GB1oqOGQJqRKMSE&code_challenge_method=S256&response_type=code&client_id='+os.environ['TEST_AUTHLETE_CLIENT_ID']+'&redirect_uri=http://localhost&scope=openid%20read'})
        )
        data = response.json()

        response = requests.post(
            url='https://api.authlete.com/api/auth/authorization/issue',
            auth=(authlete_api_key, authlete_api_secret),
            headers={'content-type': 'application/json'},
            data=json.dumps({'ticket':data['ticket'], 'subject':os.environ['TEST_COGNITO_USER_ID']})
        )

        data = response.json()
        response = requests.post(
            url='https://api.authlete.com/api/auth/token',
            auth=(authlete_api_key, authlete_api_secret),
            headers={'content-type': 'application/json'},
            data=json.dumps({
                'parameters':'grant_type=authorization_code&code='+data['authorizationCode']+'&redirect_uri=http://localhost&code_verifier=7vN7KSmEl5qFeHeRZmfMsR7fl_BsluESjvl32W9el5A6WgsAbXCaqwK43BmXjs7cGw9hTQC9xmVb41xi8fL4CA',
                'clientId':os.environ['TEST_AUTHLETE_CLIENT_ID'],
                'clientSecret':os.environ['TEST_AUTHLETE_CLIENT_SECRET']
            })
        )
        data = response.json()
        self.access_token = data['accessToken']

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
