import os
from urllib.parse import parse_qs
from lib.authlete_sdk import AuthleteSdk
from lib.exceptions import AuthleteApiError
from lib.utils import response_builder, logger, verify_supported_media_type


def handler(event, context):
    try:
        logger.info(event)
        if verify_supported_media_type(event['headers']) is False:
            return response_builder(415, {
                'error_message': "This API only support 'content-type: application/x-www-form-urlencoded' media type"
            })

        token = parse_qs(event['body']).get('token', None)
        if token is None:
            return response_builder(400, {
                'error_message': 'Missing token patameter'
            })
        authlete = AuthleteSdk(
            api_key=os.environ['AUTHLETE_API_KEY'],
            api_secret=os.environ['AUTHLETE_API_SECRET']
        )

        result = authlete.verify_access_token(
            token=token[0]
        )
    except AuthleteApiError as e:
        if e.status_code != 400:
            logger.error(e)
            return response_builder(500, {
                'error_message': 'Internal Server Error'
            })

        return response_builder(e.status_code, {
            'error_message': e.message
        })
    return response_builder(200, result)
