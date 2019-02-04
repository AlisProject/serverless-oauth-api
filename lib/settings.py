AUTHLETE_AUTHORIZATION_ISSUE_URL = 'https://api.authlete.com/api/auth/authorization/issue'
AUTHLETE_AUTHORIZATION_URL = 'https://api.authlete.com/api/auth/authorization'
AUTHLETE_OPENID_CONFIGURATION_URL = 'https://api.authlete.com/api/service/configuration'
AUTHLETE_INTROSPECTION_URL = 'https://api.authlete.com/api/auth/introspection/standard'
AUTHLETE_JWK_INFORMATION_URL = 'https://api.authlete.com/api/service/jwks/get'
AUTHLETE_USERINFO_URL = 'https://api.authlete.com/api/auth/userinfo/issue'
AUTHLETE_TOKEN_URL = 'https://api.authlete.com/api/auth/token'
AUTHLETE_CLIENT_INFO_URL = 'https://api.authlete.com/api/client/get'

AUTHLETE_INTROSPECTION_SUCCESS_CODE = 'A145001'
AUTHLETE_USERINFO_SUCCESS_CODE = 'A096001'
AUTHLETE_ACCESS_TOKEN_SUCCESS_CODE = 'A050001'
AUTHLETE_REFRESH_TOKEN_SUCCESS_CODE = 'A053001'

AUTHLETE_ERROR_400_LIST = [
    'A027201',  # client_idが不正
    'A049302',  # grant_typeが空
    'A049304',  # grant_typeが不正な値
    'A050302',  # codeが空
    'A050305',  # codeが間違ってる
    'A050311',  # codeが有効期限切れ
    'A050308',  # redirect_uriが空
    'A050309',  # redirect_uriが登録された値と違う
    'A050313',  # code_verifierが空
    'A050315',  # code_verifierが違う値
    'A053302',  # refresh_tokenが空
    'A053305',  # refresh_tokenが不正
    'A048308',  # client_secretが空
    'A048311'  # client_secretが不正
]
AUTHLETE_AUTHORIZATION_ERROR_CLIENT_ID_IS_NOT_FOUND                    = 'A010304'
AUTHLETE_AUTHORIZATION_ERROR_CODE_CHALLENGE_IS_INVALID                 = 'A124304'
AUTHLETE_AUTHORIZATION_ERROR_CODE_CHALLENGE_METHOD_IS_NOT_SUPPORTED    = 'A124306'
AUTHLETE_AUTHORIZATION_ERROR_DOES_NOT_CONTAIN_CLIENT_ID                = 'A010301'
AUTHLETE_AUTHORIZATION_ERROR_DOES_NOT_CONTAIN_CODE_CHALLENGE_PARAMETER = 'A124301'
AUTHLETE_AUTHORIZATION_ERROR_DOES_NOT_CONTAIN_REDIRECT_URI             = 'A011303'
AUTHLETE_AUTHORIZATION_ERROR_DOES_NOT_CONTAIN_RESPONSE_TYPE            = 'A009301'
AUTHLETE_AUTHORIZATION_ERROR_REDIRECT_URI_IS_NOT_REGISTERED            = 'A011304'
AUTHLETE_AUTHORIZATION_ERROR_RESPONSE_TYPE_IS_INVALID                  = 'A009304'
AUTHLETE_AUTHORIZATION_ISSUE_SUBJECT_DOES_NOT_CONTAIN                  = 'A042201'
AUTHLETE_AUTHORIZATION_SUCCESS_CODE                                    = 'A040001'
AUTHLETE_INTROSPECTION_SUCCESS_CODE                                    = 'A145001'
AUTHLETE_USERINFO_SUCCESS_CODE                                         = 'A096001'

API_DOMAIN = 'https://oauth2.alis.to'
INTROSPECTION_ENDPOINT = '/introspection'
