import json
import requests
from lib.exceptions import AuthleteApiError, ValidationError
from lib.settings import AUTHLETE_OPENID_CONFIGURATION_URL, API_DOMAIN, INTROSPECTION_ENDPOINT
from lib.settings import AUTHLETE_INTROSPECTION_URL, AUTHLETE_INTROSPECTION_SUCCESS_CODE
from lib.settings import AUTHLETE_USERINFO_URL, AUTHLETE_USERINFO_SUCCESS_CODE


class AuthleteSdk():
    def __init__(self, api_key, api_secret):
        self.api_key = api_key
        self.api_secret = api_secret

    def get_openid_configuration(self):
        response = requests.get(
            url=AUTHLETE_OPENID_CONFIGURATION_URL,
            auth=(self.api_key, self.api_secret)
        )

        if response.status_code != 200:
            raise AuthleteApiError(
                endpoint=AUTHLETE_OPENID_CONFIGURATION_URL,
                status_code=response.status_code,
                message=response.text
            )
        configuration = json.loads(response.text)
        return {
            'issuer': configuration['issuer'],
            'authorization_endpoint': configuration['authorization_endpoint'],
            'token_endpoint': configuration['token_endpoint'],
            'token_introspection_endpoint': API_DOMAIN + INTROSPECTION_ENDPOINT,
            'userinfo_endpoint': configuration['userinfo_endpoint'],
            'jwks_uri': configuration['jwks_uri'],
            'scopes_supported': configuration['scopes_supported'],
            'response_types_supported': configuration['response_types_supported'],
            'grant_types_supported': configuration['grant_types_supported'],
            'subject_types_supported': configuration['subject_types_supported'],
            'id_token_signing_alg_values_supported': ["RS256"],
            'token_endpoint_auth_methods_supported': configuration['token_endpoint_auth_methods_supported'],
            'claims_supported': configuration['claims_supported'],
            'code_challenge_methods_supported': ["S256"]
        }

    def verify_access_token(self, token):
        response = requests.post(
            url=AUTHLETE_INTROSPECTION_URL,
            auth=(self.api_key, self.api_secret),
            data={'parameters':'token='+token+'&token_type_hint=access_token'}
        )

        if response.status_code is not 200:
            raise AuthleteApiError(
                endpoint=AUTHLETE_INTROSPECTION_URL,
                status_code=response.status_code,
                message=response.text
            )

        result = json.loads(response.text)
        if result['resultCode'] != AUTHLETE_INTROSPECTION_SUCCESS_CODE:
            raise AuthleteApiError(
                endpoint=AUTHLETE_INTROSPECTION_URL,
                status_code=400,
                message=user_info['resultMessage']
            )
        return json.loads(result['responseContent'])

    def get_access_token_from_header(self, headers):
        auth = headers.get('Authorization', None)
        if not auth:
            raise ValidationError(
                status_code=401,
                message='Missing Authorization header'
            )

        parts = auth.split()

        if parts[0].lower() != 'bearer':
            raise ValidationError(
                status_code=401,
                message='Authorization header must start with Bearer'
            )

        elif len(parts) == 1:
            raise ValidationError(
                status_code=401,
                message='Token not found'
            )

        elif len(parts) > 2:
            raise ValidationError(
                status_code=401,
                message='Authorization header must be Bearer token'
            )

        return parts[1]

    def get_user_info(self, access_token):
        response = requests.post(
            url=AUTHLETE_USERINFO_URL,
            auth=(self.api_key, self.api_secret),
            data={'token':access_token}
        )

        if response.status_code != 200:
            raise AuthleteApiError(
                endpoint=AUTHLETE_USERINFO_URL,
                status_code=response.status_code,
                message=response.text
            )

        user_info = json.loads(response.text)
        if user_info['resultCode'] != AUTHLETE_USERINFO_SUCCESS_CODE:
            raise AuthleteApiError(
                endpoint=AUTHLETE_USERINFO_URL,
                status_code=401,
                message=user_info['resultMessage']
            )

        return json.loads(user_info['responseContent'])
