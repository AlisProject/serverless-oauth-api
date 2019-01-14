import json
import os
from lib.authlete_sdk import AuthleteSdk
from lib.exceptions import AuthleteApiError, ValidationError
from lib.cognito_user_pool import CognitoUserPool
from lib.utils import response_builder, logger
from botocore.exceptions import ClientError


def handler(event, context):
    try:
        logger.info(event)
        authlete = AuthleteSdk(
            api_key=os.environ['AUTHLETE_API_KEY'],
            api_secret=os.environ['AUTHLETE_API_SECRET']
        )

        congito_user_pool = CognitoUserPool(
            user_pool_id=os.environ['COGNITO_USER_POOL_ID']
        )

        access_token = authlete.get_access_token_from_header(headers=event['headers'])
        response_content = authlete.get_user_info(access_token=access_token)
        sub = congito_user_pool.get_user_sub_value(username=response_content['sub'])
    except ValidationError as e:
        return response_builder(e.status_code, {
            'error_message': e.message
        })
    except AuthleteApiError as e:
        if e.status_code != 401:
            logger.error(e)
            return response_builder(500, {
                'error_message': 'Internal Server Error'
            })

        return response_builder(e.status_code, {
            'error_message': e.message
        })
    except ClientError as e:
        logger.error(e)
        return response_builder(500, {
            'error_message': 'Internal Server Error'
        })
    return response_builder(200, {
        'sub': sub,
        'name': response_content['sub']
    })
