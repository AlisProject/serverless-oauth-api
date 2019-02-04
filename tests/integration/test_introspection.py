import requests
import os
from .common import AuthleteSDKForTest
authlete_test_sdk = AuthleteSDKForTest(
    client_id=os.environ['TEST_AUTHLETE_SERVER_APP_CLIENT_ID'],
    client_secret=os.environ['TEST_AUTHLETE_SERVER_APP_CLIENT_SECRET']
)


class TestIntrospection(object):
    def setup(self):
        self.code_verifier = authlete_test_sdk.get_code_verifier()
        self.code_challenge = authlete_test_sdk.get_code_challenge(self.code_verifier)
        self.access_token = authlete_test_sdk.get_access_token(
            code_verifier=self.code_verifier,
            code_challenge=self.code_challenge
        )

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
