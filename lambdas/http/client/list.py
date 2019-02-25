import json
import os
from jose import jwt
from lib.authlete_sdk import AuthleteSdk
from lib.exceptions import AuthleteApiError
from lib.utils import response_builder, logger, verify_jwt_token, get_access_token_from_header

def handler(event, context):
    try:
        logger.info(event)

        # jwtの検証
        jwt_token = get_access_token_from_header(event['headers'])
        if not verify_jwt_token(jwt_token):
            return response_builder(401, {"error_message": "invalid jwt token"})

        # パラメーター設定
        claims = jwt.get_unverified_claims(jwt_token)
        params = event.get('multiValueQueryStringParameters', {})
        if params is None:
            params = {}
        params['subject'] = [claims['cognito:username']]

        authlete = AuthleteSdk(
            api_key=os.environ['AUTHLETE_API_KEY'],
            api_secret=os.environ['AUTHLETE_API_SECRET']
        )
        client_list = authlete.get_client_list(params)

    except AuthleteApiError as e:
        logger.error(e)
        return response_builder(500, {
            'error_message': 'Internal Server Error'
        })

    return response_builder(200, client_list)
