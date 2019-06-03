import os
from lib.authlete_sdk import AuthleteSdk
from lib.exceptions import ValidationError, AuthleteApiError
from lib.cognito_user_pool import CognitoUserPool
from lib.utils import response_builder, logger, verify_supported_media_type


def handler(event, context):
    # 初期化処理
    token = {}
    authlete = None
    try:
        if verify_supported_media_type(event['headers']) is False:
            return response_builder(415, {
                'error_message': "This API only support 'content-type: application/x-www-form-urlencoded' media type"
            })

        authlete = AuthleteSdk(
            api_key=os.environ['AUTHLETE_API_KEY'],
            api_secret=os.environ['AUTHLETE_API_SECRET']
        )
    except Exception as e:
        logger.error(e)
        return response_builder(500, {
            'error_message': 'Internal Server Error'
        })

    # トークン取得処理
    try:
        grant_type = authlete.get_grant_type(
            body=event['body']
        )

        data = authlete.get_clientid_and_clientsecret(
            headers=event['headers'],
            body=event['body']
        )

        if grant_type == 'authorization_code':
            if data.get('client_secret') is None:
                token = authlete.get_access_token_from_code(
                    body=event['body'],
                    client_id=data['client_id']
                )
            else:
                token = authlete.get_access_token_from_code(
                    body=event['body'],
                    client_id=data['client_id'],
                    client_secret=data['client_secret']
                )
        elif grant_type == 'refresh_token':
            if data.get('client_secret') is None:
                token = authlete.get_access_token_from_refresh_token(
                    body=event['body'],
                    client_id=data['client_id']
                )
            else:
                token = authlete.get_access_token_from_refresh_token(
                    body=event['body'],
                    client_id=data['client_id'],
                    client_secret=data['client_secret']
                )
        else:
            return response_builder(400, {
                'error_message': 'invalid grant_type'
            })
    except ValidationError as e:
        logger.error(e)
        return response_builder(e.status_code, {
            'error_message': e.message
        })
    except AuthleteApiError as e:
        logger.error(e)
        if e.status_code != 500:
            return response_builder(e.status_code, {
                'error_message': e.message
            })
        return response_builder(500, {
            'error_message': 'Internal Server Error'
        })

    try:
        congito_user_pool = CognitoUserPool(
            user_pool_id=os.environ['COGNITO_USER_POOL_ID']
        )

        access_token = token.get('access_token')
        response_content = authlete.get_user_info(access_token=access_token)
        attributes = congito_user_pool.get_user_attributes(username=response_content['sub'])
        phone_number_verified = 'false'

        for attribute in attributes:
            if attribute['Name'] == 'phone_number_verified':
                phone_number_verified = attribute['Value']

        if phone_number_verified == 'true':
            return response_builder(200, token)
        else:
            return response_builder(403, {
                'error_message': 'phone_number must be verified'
            })

    except Exception as e:
        logger.error(e)
        return response_builder(500, {
            'error_message': 'Internal Server Error'
        })
