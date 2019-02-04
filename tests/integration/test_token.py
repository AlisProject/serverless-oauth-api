import requests
import os
import base64
from .common import get_authorization_code, get_token_for_client_authentication
from .common import get_code_verifier, get_code_challenge
from .common import get_refresh_token


class TestToken(object):
    def setup(self):
        self.code_verifier = get_code_verifier()
        self.code_challenge = get_code_challenge(self.code_verifier)
        self.authorization_code = get_authorization_code(self.code_challenge)

    def test_return_200_with_authorization_code(self, endpoint):
        response = requests.post(
            url=endpoint + '/token',
            headers={
                'Content-Type': 'application/x-www-form-urlencoded',
                'Authorization': 'Basic ' + get_token_for_client_authentication()
            },
            data='grant_type=authorization_code&code='+self.authorization_code+'&redirect_uri=http://localhost&code_verifier='+self.code_verifier
        )
        assert response.status_code == 200

        data = response.json()
        assert 'access_token' in data
        assert 'refresh_token' in data
        assert 'scope' in data
        assert 'id_token' in data
        assert 'token_type' in data
        assert 'expires_in' in data

    def test_return_200_with_refresh_token(self, endpoint):
        refresh_token = get_refresh_token(
            code_verifier=self.code_verifier,
            code_challenge=self.code_challenge
        )
        response = requests.post(
            url=endpoint + '/token',
            headers={
                'Content-Type': 'application/x-www-form-urlencoded',
                'Authorization': 'Basic '+get_token_for_client_authentication()
            },
            data='grant_type=refresh_token&refresh_token='+refresh_token
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
                'Content-Type': 'application/x-www-form-urlencoded',
                'Authorization': 'Basic '+get_token_for_client_authentication()
            },
            data='grant_type=authorization_code&redirect_uri=http://localhost&code_verifier='+self.code_verifier
        )
        assert response.status_code == 400
        error = response.json()
        assert error['error_message'] == "[A050302] The value of 'code' in the token request is empty."

    def test_return_400_with_invalid_code(self, endpoint):
        response = requests.post(
            url=endpoint + '/token',
            headers={
                'Content-Type': 'application/x-www-form-urlencoded',
                'Authorization': 'Basic '+get_token_for_client_authentication()
            },
            data='grant_type=authorization_code&code=xxxxxx&redirect_uri=http://localhost&code_verifier='+self.code_verifier
        )
        assert response.status_code == 400
        error = response.json()
        assert error['error_message'] == '[A050305] No such authorization code.'

    def test_return_400_with_invalid_redirect_uri(self, endpoint):
        response = requests.post(
            url=endpoint + '/token',
            headers={
                'Content-Type': 'application/x-www-form-urlencoded',
                'Authorization': 'Basic '+get_token_for_client_authentication()
            },
            data='grant_type=authorization_code&code='+self.authorization_code+'&redirect_uri=http://example.com&code_verifier='+self.code_verifier
        )
        assert response.status_code == 400
        error = response.json()
        assert error['error_message'] == '[A050309] The redirect URI contained in the token request does not match the one which was specified when the authorization code was created.'

    def test_return_400_with_invalid_grant_type(self, endpoint):
        response = requests.post(
            url=endpoint + '/token',
            headers={
                'Content-Type': 'application/x-www-form-urlencoded',
                'Authorization': 'Basic '+get_token_for_client_authentication()
            },
            data='grant_type=xxxxxx&code='+self.authorization_code+'&redirect_uri=http://localhost&code_verifier='+self.code_verifier
        )
        assert response.status_code == 400
        error = response.json()
        assert error['error_message'] == "invalid grant_type"

    def test_return_400_with_invalid_code_verifier(self, endpoint):
        response = requests.post(
            url=endpoint + '/token',
            headers={
                'Content-Type': 'application/x-www-form-urlencoded',
                'Authorization': 'Basic '+get_token_for_client_authentication()
            },
            data='grant_type=authorization_code&code='+self.authorization_code+'&redirect_uri=http://localhost&code_verifier=xxxxxxx'
        )
        assert response.status_code == 400
        error = response.json()
        assert error['error_message'] == "[A050315] The code challenge value computed with 'code_verifier' is different from 'code_challenge' contained in the authorization request."

    def test_return_400_with_invalid_basic_auth(self, endpoint):
        response = requests.post(
            url=endpoint + '/token',
            headers={
                'Content-Type': 'application/x-www-form-urlencoded',
                'Authorization': 'Basic xxxxxxx'
            },
            data='grant_type=authorization_code&code='+self.authorization_code+'&redirect_uri=http://localhost&code_verifier='+self.code_verifier
        )
        assert response.status_code == 400
        error = response.json()
        assert error['error_message'] == 'Missing client_id'

    def test_return_400_with_invalid_client_secret(self, endpoint):
        basicauth_str = os.environ['TEST_AUTHLETE_CLIENT_ID'] + ':xxxxxxx'
        basic_auth = base64.b64encode(basicauth_str.encode('utf-8')).decode('UTF-8')
        response = requests.post(
            url=endpoint + '/token',
            headers={
                'Content-Type': 'application/x-www-form-urlencoded',
                'Authorization': 'Basic '+basic_auth
            },
            data='grant_type=authorization_code&code='+self.authorization_code+'&redirect_uri=http://localhost&code_verifier='+self.code_verifier
        )
        assert response.status_code == 400
        error = response.json()
        assert error['error_message'] == '[A048311] The client credentials contained in the token request are invalid.'