import decimal
import json
import logging
import os
import time
import urllib.request
from jose import jwk, jwt
from jose.utils import base64url_decode
from lib.exceptions import ValidationError
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def get_access_token_from_header(headers):
    auth = headers.get('Authorization', None)
    if not auth:
        raise ValidationError(
            status_code=401,
            message='Missing Authorization header'
        )

    parts = auth.split()

    if parts[0].lower() != 'bearer':
        raise ValidationError(
            status_code=401,
            message='Authorization header must start with Bearer'
        )

    elif len(parts) == 1:
        raise ValidationError(
            status_code=401,
            message='Token not found'
        )

    elif len(parts) > 2:
        raise ValidationError(
            status_code=401,
            message='Authorization header must be Bearer token'
        )

    return parts[1]

def response_builder(status_code, body={}):
    return {
        'statusCode': status_code,
        'body': json.dumps(body, cls=DecimalEncoder)
    }

def verify_jwt_token(token):
    try:
        keys_url = 'https://cognito-idp.{}.amazonaws.com/{}/.well-known/jwks.json'.format(os.environ['AWS_REGION'], os.environ['COGNITO_USER_POOL_ID'])
        response = urllib.request.urlopen(keys_url)
        keys = json.loads(response.read())['keys']
        headers = jwt.get_unverified_headers(token)
        kid = headers['kid']
        key_index = -1
        for i in range(len(keys)):
            if kid == keys[i]['kid']:
                key_index = i
                break
        public_key = jwk.construct(keys[key_index])
        message, encoded_signature = str(token).rsplit('.', 1)
        decoded_signature = base64url_decode(encoded_signature.encode('utf-8'))
        if not public_key.verify(message.encode("utf8"), decoded_signature):
            return False
        claims = jwt.get_unverified_claims(token)
        if time.time() > claims['exp']:
            return False
    except Exception:
        return False
    return True

class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, decimal.Decimal):
            return int(obj)
        return super(DecimalEncoder, self).default(obj)
