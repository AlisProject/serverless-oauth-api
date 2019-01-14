import requests

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
