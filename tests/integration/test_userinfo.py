import requests
import os
from .common import AuthleteSDKForTest
authlete_test_sdk = AuthleteSDKForTest(
    client_id=os.environ['TEST_AUTHLETE_SERVER_APP_CLIENT_ID'],
    client_secret=os.environ['TEST_AUTHLETE_SERVER_APP_CLIENT_SECRET']
)


class TestUserInfo(object):
    def setup(self):
        self.code_verifier = authlete_test_sdk.get_code_verifier()
        self.code_challenge = authlete_test_sdk.get_code_challenge(
            self.code_verifier)
        self.access_token = authlete_test_sdk.get_access_token(
            code_verifier=self.code_verifier,
            code_challenge=self.code_challenge
        )

    def test_return_200(self, endpoint):
        response = requests.get(
            url=endpoint + '/userinfo',
            headers={'Authorization': 'Bearer ' + self.access_token}
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
            headers={'Authorization': 'Basic ' + self.access_token}
        )
        assert response.status_code == 401

    def test_return_401_with_fake_accesstoken(self, endpoint):
        response = requests.get(
            url=endpoint + '/userinfo',
            headers={'Authorization': 'Bearer xxxxxxxxxxxxxxx'}
        )
        assert response.status_code == 401
