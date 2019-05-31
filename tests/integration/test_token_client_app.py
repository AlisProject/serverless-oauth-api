import requests
import os
import base64
from .common import AuthleteSDKForTest
authlete_test_sdk = AuthleteSDKForTest(
    client_id=os.environ['TEST_AUTHLETE_CLIENT_APP_CLIENT_ID']
)


class TestTokenClientApp(object):
    def setup(self):
        self.code_verifier = authlete_test_sdk.get_code_verifier()
        self.code_challenge = authlete_test_sdk.get_code_challenge(self.code_verifier)
        self.authorization_code = authlete_test_sdk.get_authorization_code(self.code_challenge)
        self.authorization_code_by_phone_number_not_verified_user = authlete_test_sdk.get_authorization_code(self.code_challenge, False)

    def test_return_200_with_authorization_code(self, endpoint):
        response = requests.post(
            url=endpoint + '/token',
            headers={
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            data='grant_type=authorization_code&code='+self.authorization_code+'&redirect_uri=http://localhost&code_verifier='+self.code_verifier+'&client_id='+os.environ['TEST_AUTHLETE_CLIENT_APP_CLIENT_ID']
        )
        assert response.status_code == 200

        data = response.json()
        assert 'access_token' in data
        assert 'refresh_token' in data
        assert 'scope' in data
        assert 'id_token' in data
        assert 'token_type' in data
        assert 'expires_in' in data

    def test_return_415_with_unsupported_media_type(self, endpoint):
        response = requests.post(
            url=endpoint + '/token',
            headers={
                'Content-Type': 'application/json'
            },
            data='grant_type=authorization_code&code='+self.authorization_code+'&redirect_uri=http://localhost&code_verifier='+self.code_verifier+'&client_id='+os.environ['TEST_AUTHLETE_CLIENT_APP_CLIENT_ID']
        )
        assert response.status_code == 415

    def test_return_200_with_refresh_token(self, endpoint):
        refresh_token = authlete_test_sdk.get_refresh_token(
            code_verifier=self.code_verifier,
            code_challenge=self.code_challenge
        )
        response = requests.post(
            url=endpoint + '/token',
            headers={
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            data='grant_type=refresh_token&refresh_token='+refresh_token+'&client_id='+os.environ['TEST_AUTHLETE_CLIENT_APP_CLIENT_ID']
        )
        assert response.status_code == 200

        data = response.json()
        assert 'access_token' in data
        assert 'refresh_token' in data
        assert 'scope' in data
        assert 'token_type' in data
        assert 'expires_in' in data

    def test_return_400_with_missing_required_parameter(self, endpoint):
        response = requests.post(
            url=endpoint + '/token',
            headers={
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            data='grant_type=authorization_code&redirect_uri=http://localhost&code_verifier='+self.code_verifier+'&client_id='+os.environ['TEST_AUTHLETE_CLIENT_APP_CLIENT_ID']
        )
        assert response.status_code == 400
        error = response.json()
        assert error['error_message'] == "The value of 'code' in the token request is empty."

    def test_return_400_with_invalid_code(self, endpoint):
        response = requests.post(
            url=endpoint + '/token',
            headers={
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            data='grant_type=authorization_code&code=xxxxx&redirect_uri=http://localhost&code_verifier='+self.code_verifier+'&client_id='+os.environ['TEST_AUTHLETE_CLIENT_APP_CLIENT_ID']
        )
        assert response.status_code == 400
        error = response.json()
        assert error['error_message'] == 'No such authorization code.'

    def test_return_400_with_invalid_redirect_uri(self, endpoint):
        response = requests.post(
            url=endpoint + '/token',
            headers={
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            data='grant_type=authorization_code&code='+self.authorization_code+'&redirect_uri=http://example.com&code_verifier='+self.code_verifier+'&client_id='+os.environ['TEST_AUTHLETE_CLIENT_APP_CLIENT_ID']
        )
        assert response.status_code == 400
        error = response.json()
        assert error['error_message'] == 'The redirect URI contained in the token request does not match the one which was specified when the authorization code was created.'

    def test_return_400_with_invalid_grant_type(self, endpoint):
        response = requests.post(
            url=endpoint + '/token',
            headers={
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            data='grant_type=xxxxx&code='+self.authorization_code+'&redirect_uri=http://localhost&code_verifier='+self.code_verifier+'&client_id='+os.environ['TEST_AUTHLETE_CLIENT_APP_CLIENT_ID']
        )
        assert response.status_code == 400
        error = response.json()
        assert error['error_message'] == "invalid grant_type"

    def test_return_400_with_invalid_code_verifier(self, endpoint):
        response = requests.post(
            url=endpoint + '/token',
            headers={
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            data='grant_type=authorization_code&code='+self.authorization_code+'&redirect_uri=http://localhost&code_verifier=xxxxxx&client_id='+os.environ['TEST_AUTHLETE_CLIENT_APP_CLIENT_ID']
        )
        assert response.status_code == 400
        error = response.json()
        assert error['error_message'] == "The code challenge value computed with 'code_verifier' is different from 'code_challenge' contained in the authorization request."

    def test_return_400_with_missing_client_id(self, endpoint):
        response = requests.post(
            url=endpoint + '/token',
            headers={
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            data='grant_type=authorization_code&code='+self.authorization_code+'&redirect_uri=http://localhost&code_verifier='+self.code_verifier
        )
        assert response.status_code == 400
        error = response.json()
        assert error['error_message'] == 'Missing client_id'

    def test_return_403_with_phone_number_not_verified_user(self, endpoint):
        response = requests.post(
            url=endpoint + '/token',
            headers={
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            data='grant_type=authorization_code&code='+self.authorization_code_by_phone_number_not_verified_user+'&redirect_uri=http://localhost&code_verifier='+self.code_verifier+'&client_id='+os.environ['TEST_AUTHLETE_CLIENT_APP_CLIENT_ID']
        )

        assert response.status_code == 403
        error = response.json()
        assert error['error_message'] == 'phone_number must be verified'
