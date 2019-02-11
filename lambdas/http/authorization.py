import os
import urllib.parse
from jose import jwt
from lib.authlete_sdk import AuthleteSdk
from lib.exceptions import AuthleteApiError, ValidationError
from lib.settings import AUTHLETE_AUTHORIZATION_ERROR_CLIENT_ID_IS_NOT_FOUND
from lib.settings import AUTHLETE_AUTHORIZATION_ERROR_CODE_CHALLENGE_IS_INVALID
from lib.settings import AUTHLETE_AUTHORIZATION_ERROR_CODE_CHALLENGE_METHOD_IS_NOT_SUPPORTED
from lib.settings import AUTHLETE_AUTHORIZATION_ERROR_DOES_NOT_CONTAIN_CLIENT_ID
from lib.settings import AUTHLETE_AUTHORIZATION_ERROR_DOES_NOT_CONTAIN_CODE_CHALLENGE_PARAMETER
from lib.settings import AUTHLETE_AUTHORIZATION_ERROR_DOES_NOT_CONTAIN_REDIRECT_URI
from lib.settings import AUTHLETE_AUTHORIZATION_ERROR_DOES_NOT_CONTAIN_RESPONSE_TYPE
from lib.settings import AUTHLETE_AUTHORIZATION_ERROR_REDIRECT_URI_IS_NOT_REGISTERED
from lib.settings import AUTHLETE_AUTHORIZATION_ERROR_RESPONSE_TYPE_IS_INVALID
from lib.settings import AUTHLETE_AUTHORIZATION_SUCCESS_CODE
from lib.settings import AUTHLETE_AUTHORIZATION_ISSUE_SUBJECT_DOES_NOT_CONTAIN
from lib.utils import response_builder, logger, verify_jwt_token, get_access_token_from_header
from lib.utils import verify_scope_parameter, strip_authlete_code, verify_supported_media_type


def handler(event, context):
    try:
        logger.info(event)
        if verify_supported_media_type(event['headers']) is False:
            return response_builder(415, {
                'error_message': "This API only support 'content-type: application/x-www-form-urlencoded' media type"
            })

        # jwtの検証
        jwt_token = get_access_token_from_header(event['headers'])
        if not verify_jwt_token(jwt_token):
            return response_builder(401, {"error_message": "invalid jwt token"})

        # パラメーター設定
        claims = jwt.get_unverified_claims(jwt_token)
        params = urllib.parse.parse_qs(event.get('body', ''))
        params['subject'] = [claims['cognito:username']]
        params['sub'] = [claims['sub']]
        params['scope'] = params.get('scope', ['']) # scopeが無い場合は空配列で初期化
        params['scope'] = [params['scope'][0]]      # scopeが複数来たら最初だけ使う

        # scopeの検証
        if not verify_scope_parameter(params['scope'][0]):
            return response_builder(400, {"error_message": "invalid scope parameter. scope parameter must be 'openid read' or 'openid write'"})

        # authrazition API
        new_params = urllib.parse.urlencode(params, doseq=True)

        if urllib.parse.parse_qs(new_params).get('code_challenge_method') is None:
            return response_builder(400, {
                'error_message': "The authorization request does not contain 'code_challenge_method' parameter."
            })

        authlete = AuthleteSdk(
            api_key=os.environ['AUTHLETE_API_KEY'],
            api_secret=os.environ['AUTHLETE_API_SECRET']
        )
        authrazition_response = authlete.authorization_request(new_params)
        AUTHORIZATION_ERROR_CODES = [
            AUTHLETE_AUTHORIZATION_ERROR_CLIENT_ID_IS_NOT_FOUND
            ,AUTHLETE_AUTHORIZATION_ERROR_CODE_CHALLENGE_IS_INVALID
            ,AUTHLETE_AUTHORIZATION_ERROR_CODE_CHALLENGE_METHOD_IS_NOT_SUPPORTED
            ,AUTHLETE_AUTHORIZATION_ERROR_DOES_NOT_CONTAIN_CLIENT_ID
            ,AUTHLETE_AUTHORIZATION_ERROR_DOES_NOT_CONTAIN_CODE_CHALLENGE_PARAMETER
            ,AUTHLETE_AUTHORIZATION_ERROR_DOES_NOT_CONTAIN_REDIRECT_URI
            ,AUTHLETE_AUTHORIZATION_ERROR_DOES_NOT_CONTAIN_RESPONSE_TYPE
            ,AUTHLETE_AUTHORIZATION_ERROR_REDIRECT_URI_IS_NOT_REGISTERED
            ,AUTHLETE_AUTHORIZATION_ERROR_RESPONSE_TYPE_IS_INVALID
            ,AUTHLETE_AUTHORIZATION_SUCCESS_CODE
        ]
        if authrazition_response['resultCode'] in AUTHORIZATION_ERROR_CODES:
            return response_builder(400, {
                'error_message': strip_authlete_code(authrazition_response['resultMessage'])
            })

        # authorization issue API
        authrazition_issue_response = authlete.authorization_issue_request({
            "ticket": authrazition_response['ticket'],
            "subject": claims['cognito:username'],
            "sub": claims['sub']
        })
        if authrazition_issue_response['resultCode'] == AUTHLETE_AUTHORIZATION_ISSUE_SUBJECT_DOES_NOT_CONTAIN:
            return response_builder(400, {
                'error_message': strip_authlete_code(authrazition_response['resultMessage'])
            })
        if authrazition_issue_response['resultCode'] != AUTHLETE_AUTHORIZATION_SUCCESS_CODE:
            return response_builder(500, {
                'error_message': 'Internal Server Error'
            })
    except AuthleteApiError as e:
        logger.error(e)
        return response_builder(500, {
            'error_message': 'Internal Server Error'
        })
    except ValidationError as e:
        return response_builder(e.status_code, {
            'error_message': e.message
        })
    return response_builder(200, {
        'redirect_uri': authrazition_issue_response['responseContent']
    })
