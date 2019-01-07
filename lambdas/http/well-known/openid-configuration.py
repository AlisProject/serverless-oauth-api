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

        configuration = authlete.get_openid_configuration()
        print(configuration)

    except AuthleteApiError as e:
        logger.error(e)
        return response_builder(500, {
            'error_message': 'Internal Server Error'
        })

    return response_builder(200, configuration)
