import json
import os
from jose import jwt
from lib.authlete_sdk import AuthleteSdk
from lib.exceptions import AuthleteApiError, ValidationError
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
        params = json.loads(event.get('body', "{}"))
        subject = claims['cognito:username']
        clientid = params.get('clientid', "")

        authlete = AuthleteSdk(
            api_key=os.environ['AUTHLETE_API_KEY'],
            api_secret=os.environ['AUTHLETE_API_SECRET']
        )
        responce = authlete.delete_client(clientid, subject)
    except ValidationError as e:
        logger.error(e)
        return response_builder(400, {
            'error_message': 'client id does not exist'
        })
    except AuthleteApiError as e:
        logger.error(e)
        return response_builder(500, {
            'error_message': 'Internal Server Error'
        })

    return response_builder(200, responce)
