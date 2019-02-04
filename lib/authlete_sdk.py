import json
import requests
import base64
import binascii
from urllib.parse import parse_qs
from lib.exceptions import AuthleteApiError, ValidationError
from lib.settings import AUTHLETE_ERROR_400_LIST, AUTHLETE_JWK_INFORMATION_URL
from lib.settings import AUTHLETE_OPENID_CONFIGURATION_URL, API_DOMAIN, INTROSPECTION_ENDPOINT
from lib.settings import AUTHLETE_INTROSPECTION_URL, AUTHLETE_INTROSPECTION_SUCCESS_CODE
from lib.settings import AUTHLETE_USERINFO_URL, AUTHLETE_TOKEN_URL, AUTHLETE_USERINFO_SUCCESS_CODE
from lib.settings import AUTHLETE_ACCESS_TOKEN_SUCCESS_CODE, AUTHLETE_REFRESH_TOKEN_SUCCESS_CODE
from lib.settings import AUTHLETE_CLIENT_INFO_URL


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

    def verify_access_token(self, token):
        response = requests.post(
            url=AUTHLETE_INTROSPECTION_URL,
            auth=(self.api_key, self.api_secret),
            data={'parameters': 'token='+token+'&token_type_hint=access_token'}
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
                message=result['resultMessage']
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

    def get_clientid_and_clientsecret_from_basic_header(self, headers):
        auth = headers.get('Authorization', None)
        if not auth:
            raise ValidationError(
                status_code=401,
                message='Missing Authorization header'
            )

        parts = auth.split()

        if parts[0].lower() != 'basic':
            raise ValidationError(
                status_code=401,
                message='Authorization header must start with Basic'
            )

        elif len(parts) == 1:
            raise ValidationError(
                status_code=401,
                message='Token not found'
            )

        elif len(parts) > 2:
            raise ValidationError(
                status_code=401,
                message='Authorization header must be Basic token'
            )

        try:
            client_id, client_secret = base64.b64decode(parts[1].encode('utf-8')).decode('utf-8').split(':')
        except Exception:
            raise ValidationError(
                status_code=401,
                message='Authorization header must include correct base64 string'
            )

        return {
            'client_id': client_id,
            'client_secret': client_secret
        }

    def get_clientid_and_clientsecret(self, headers, body):
        try:
            return self.get_clientid_and_clientsecret_from_basic_header(
                headers=headers
            )
        except ValidationError:
            body = parse_qs(body)
            client_id = body.get('client_id', [None])[0]
            if client_id is None:
                raise ValidationError(
                    status_code=400,
                    message='Missing client_id'
                )
            if self.get_client_type(client_id) == 'CONFIDENTIAL':
                raise ValidationError(
                    status_code=400,
                    message='Missing client_secret'
                )
            return {
                'client_id': client_id
            }

    def get_user_info(self, access_token):
        response = requests.post(
            url=AUTHLETE_USERINFO_URL,
            auth=(self.api_key, self.api_secret),
            data={'token': access_token}
        )

        user_info = json.loads(response.text)
        if response.status_code != 200:
            raise AuthleteApiError(
                endpoint=AUTHLETE_USERINFO_URL,
                status_code=response.status_code,
                message=user_info.get('resultMessage')
            )

        if user_info['resultCode'] != AUTHLETE_USERINFO_SUCCESS_CODE:
            raise AuthleteApiError(
                endpoint=AUTHLETE_USERINFO_URL,
                status_code=401,
                message=user_info.get('resultMessage')
            )

        return json.loads(user_info.get('responseContent'))

    def get_client_type(self, client_id):
        response = requests.get(
            url=AUTHLETE_CLIENT_INFO_URL + '/' + client_id,
            auth=(self.api_key, self.api_secret)
        )

        client_info = json.loads(response.text)
        if response.status_code != 200:
            raise AuthleteApiError(
                endpoint=AUTHLETE_CLIENT_INFO_URL,
                status_code=response.status_code,
                message=client_info.get('resultMessage')
            )

        client_info = json.loads(response.text)
        return client_info['clientType']

    def get_grant_type(self, body):
        body = parse_qs(body)
        return body.get('grant_type', [None])[0]

    def get_access_token_from_refresh_token(self, body, client_id, client_secret=None):
        body = parse_qs(body)
        request_parameters = {
            'clientId': client_id
        }

        if client_secret is not None:
            request_parameters['clientSecret'] = client_secret

        request_parameters['parameters'] = 'grant_type=refresh_token&refresh_token=%s' % body.get('refresh_token', [''])[0]
        response = requests.post(
            url=AUTHLETE_TOKEN_URL,
            auth=(self.api_key, self.api_secret),
            data=request_parameters
        )

        token_info = json.loads(response.text)
        if response.status_code != 200:
            raise AuthleteApiError(
                endpoint=AUTHLETE_TOKEN_URL,
                status_code=response.status_code,
                message=token_info.get('resultMessage')
            )

        if token_info.get('resultCode') != AUTHLETE_REFRESH_TOKEN_SUCCESS_CODE:
            if token_info.get('resultCode') in AUTHLETE_ERROR_400_LIST:
                raise AuthleteApiError(
                    endpoint=AUTHLETE_TOKEN_URL,
                    status_code=400,
                    message=token_info.get('resultMessage')
                )
            else:
                raise AuthleteApiError(
                    endpoint=AUTHLETE_TOKEN_URL,
                    status_code=500,
                    message=token_info.get('resultMessage')
                )
        return json.loads(token_info.get('responseContent'))

    def get_access_token_from_code(self, body, client_id, client_secret=None):
        body = parse_qs(body)
        request_parameters = {
            'clientId': client_id
        }

        if client_secret is not None:
            request_parameters['clientSecret'] = client_secret

        request_parameters['parameters'] = 'grant_type=authorization_code&code=%s&redirect_uri=%s&code_verifier=%s' % (body.get('code', [''])[0], body.get('redirect_uri', [''])[0], body.get('code_verifier', [''])[0])
        response = requests.post(
            url=AUTHLETE_TOKEN_URL,
            auth=(self.api_key, self.api_secret),
            data=request_parameters
        )

        if response.status_code != 200:
            raise AuthleteApiError(
                endpoint=AUTHLETE_TOKEN_URL,
                status_code=response.status_code,
                message=response.text
            )

        token_info = json.loads(response.text)
        if token_info.get('resultCode') != AUTHLETE_ACCESS_TOKEN_SUCCESS_CODE:
            if token_info.get('resultCode') in AUTHLETE_ERROR_400_LIST:
                raise AuthleteApiError(
                    endpoint=AUTHLETE_TOKEN_URL,
                    status_code=400,
                    message=token_info.get('resultMessage')
                )
            else:
                raise AuthleteApiError(
                    endpoint=AUTHLETE_TOKEN_URL,
                    status_code=500,
                    message=token_info.get('resultMessage')
                )
        return json.loads(token_info.get('responseContent'))
