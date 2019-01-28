import os
from lib.authlete_sdk import AuthleteSdk
from lib.exceptions import ValidationError
from lib.utils import response_builder, logger


def handler(event, context):
    try:
        logger.info(event)
        authlete = AuthleteSdk(
            api_key=os.environ['AUTHLETE_API_KEY'],
            api_secret=os.environ['AUTHLETE_API_SECRET']
        )
        try:
            data = authlete.get_clientid_and_clientsecret_from_basic_header(
                headers=event['headers']
                )
        except ValidationError:
            token = authlete.get_access_token(
                body=event['body']
            )
            return response_builder(200, token)

        token = authlete.get_access_token(
            body=event['body'],
            client_id=data['client_id'],
            client_secret=data['client_secret']
        )
        return response_builder(200, token)
    except ValidationError as e:
        logger.error(e)
