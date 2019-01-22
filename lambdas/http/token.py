import json
import os
from urllib.parse import parse_qs
from lib.authlete_sdk import AuthleteSdk
from lib.exceptions import ValidationError
from lib.utils import response_builder, logger

def handler(event, context):
    try:
        logger.info(event)
        body = parse_qs(event['body'])
        #token = body.get('token', None)

        authlete = AuthleteSdk(
            api_key=os.environ['AUTHLETE_API_KEY'],
            api_secret=os.environ['AUTHLETE_API_SECRET']
        )
        authlete.get_clientid_and_clientsecret_from_basic_header(headers=event['headers'])
    except ValidationError as e:
        logger.error(e)
