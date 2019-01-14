import json
import requests
from lib.exceptions import AuthleteApiError
from lib.settings import AUTHLETE_OPENID_CONFIGURATION_URL, AUTHLETE_JWK_INFORMATION_URL


class AuthleteSdk():
    def __init__(self, api_key, api_secret):
        self.api_key = api_key
        self.api_secret = api_secret

    def get_openid_configuration(self):
        response = requests.get(
            url=AUTHLETE_OPENID_CONFIGURATION_URL,
            auth=(self.api_key, self.api_secret)
        )

        if response.status_code is not 200:
            raise AuthleteApiError(
                endpoint=AUTHLETE_OPENID_CONFIGURATION_URL,
                status_code=response.status_code,
                message=response.text
            )

        return json.loads(response.text)

    def get_jwk_information(self):
        response = requests.get(
            url=AUTHLETE_JWK_INFORMATION_URL,
            auth=(self.api_key, self.api_secret)
        )

        if response.status_code is not 200:
            raise AuthleteApiError(
                endpoint=AUTHLETE_JWK_INFORMATION_URL,
                status_code=response.status_code,
                message=response.text
            )

        return json.loads(response.text)
