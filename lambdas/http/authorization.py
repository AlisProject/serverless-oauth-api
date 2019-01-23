import json
import os
import re
import time
import urllib.parse
import urllib.request
from jose import jwk, jwt
from jose.utils import base64url_decode
from lib.authlete_sdk import AuthleteSdk
from lib.exceptions import AuthleteApiError
from lib.settings import AUTHLETE_AUTHORIZATION_SUCCESS_CODE
from lib.utils import response_builder, logger

keys_url = 'https://cognito-idp.{}.amazonaws.com/{}/.well-known/jwks.json'.format(os.environ['AWS_REGION'], os.environ['COGNITO_USER_POOL_ID'])
response = urllib.request.urlopen(keys_url)
keys = json.loads(response.read())['keys']

def verify_jwt_token(token):
    try:
        headers = jwt.get_unverified_headers(token)
        kid = headers['kid']
        key_index = -1
        for i in range(len(keys)):
            if kid == keys[i]['kid']:
                key_index = i
                break
        public_key = jwk.construct(keys[key_index])
        message, encoded_signature = str(token).rsplit('.', 1)
        decoded_signature = base64url_decode(encoded_signature.encode('utf-8'))
        if not public_key.verify(message.encode("utf8"), decoded_signature):
            return False
        claims = jwt.get_unverified_claims(token)
        if time.time() > claims['exp']:
            return False
    except Exception:
        return False
    return True

def handler(event, context):
    try:
        logger.info(event)

        # jwtの検証
        jwt_token = re.sub(r'Bearer\s+', '', event['headers'].get('Authorization', ''), flags=re.IGNORECASE)
        if not verify_jwt_token(jwt_token):
            return response_builder(400, {"error_message": "invalid jwt token"})

        # パラメーター設定
        claims = jwt.get_unverified_claims(jwt_token)
        params = urllib.parse.parse_qs(event.get('body', ''))
        params['subject'] = [claims['cognito:username']]
        params['sub'] = [claims['sub']]
        new_params = urllib.parse.urlencode(params, doseq=True)

        # authrazition API
        authlete = AuthleteSdk(
            api_key=os.environ['AUTHLETE_API_KEY'],
            api_secret=os.environ['AUTHLETE_API_SECRET']
        )
        authrazition_response = authlete.authorization_request(new_params)
        if authrazition_response['resultCode'] != AUTHLETE_AUTHORIZATION_SUCCESS_CODE:
            return response_builder(400, authrazition_response)

        # authorization issue API
        authrazition_issue_response = authlete.authorization_issue_request({
            "ticket": authrazition_response['ticket'],
            "subject": claims['cognito:username'],
            "sub": claims['sub']
        })
    except AuthleteApiError as e:
        logger.error(e)
        return response_builder(500, {
            'error_message': 'Internal Server Error'
        })
    return response_builder(200, authrazition_issue_response)
