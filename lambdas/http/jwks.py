import json
import os
from lib.authlete_sdk import AuthleteSdk
from lib.exceptions import AuthleteApiError
from lib.utils import response_builder, logger

def handler(event, context):
    try:
        logger.info(event)
        authlete = AuthleteSdk(
            api_key=os.environ['AUTHLETE_API_KEY'],
            api_secret=os.environ['AUTHLETE_API_SECRET']
        )

        information = authlete.get_jwk_information()

    except AuthleteApiError as e:
        logger.error(e)
        return response_builder(500, {
            'error_message': 'Internal Server Error'
        })

    return response_builder(200, information)
