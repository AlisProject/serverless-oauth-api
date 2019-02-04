import sys
import subprocess
import boto3
import yaml
import os
import requests
import json
import base64
import hashlib


def get_endpoint_url(stage, region):
    cloudformation = boto3.client('cloudformation', region_name=region)
    f = open(os.path.dirname(__file__)+'/../../serverless.yml', 'r+')
    data = yaml.load(f)
    stackname = data['service'] + '-' + stage
    response = cloudformation.describe_stacks(
        StackName=stackname
    )

    for output in response['Stacks'][0]['Outputs']:
        if output['OutputKey'] == 'ServiceEndpoint':
            return output['OutputValue']


def api_deploy(stage, region):
    exec_cmd(os.path.dirname(__file__)+'/../../node_modules/.bin/serverless deploy --stage '+stage+ ' --region '+region)


def api_remove(stage, region):
    exec_cmd(os.path.dirname(__file__)+'/../../node_modules/.bin/serverless remove --stage '+stage+ ' --region '+region)


def exec_cmd(cmd):
    proc = subprocess.Popen(
        cmd,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT
    )

    while True:
        line = proc.stdout.readline()
        if line:
            sys.stdout.write(line.decode('utf-8'))

        if not line and proc.poll() is not None:
            break


def get_access_token(code_verifier, code_challenge):
    authlete_token = get_authlete_token()
    authorization_code = get_authorization_code(code_challenge)
    response = requests.post(
        url='https://api.authlete.com/api/auth/token',
        auth=(
            authlete_token.get('authlete_api_key'),
            authlete_token.get('authlete_api_secret')
        ),
        headers={'content-type': 'application/json'},
        data=json.dumps({
            'parameters': 'grant_type=authorization_code&code='+authorization_code+'&redirect_uri=http://localhost&code_verifier=' + code_verifier,
            'clientId': os.environ['TEST_AUTHLETE_CLIENT_ID'],
            'clientSecret': os.environ['TEST_AUTHLETE_CLIENT_SECRET']
        })
    )
    data = response.json()
    return data['accessToken']


def get_refresh_token(code_verifier, code_challenge):
    authlete_token = get_authlete_token()
    authorization_code = get_authorization_code(code_challenge)
    response = requests.post(
        url='https://api.authlete.com/api/auth/token',
        auth=(
            authlete_token.get('authlete_api_key'),
            authlete_token.get('authlete_api_secret')
        ),
        headers={'content-type': 'application/json'},
        data=json.dumps({
            'parameters': 'grant_type=authorization_code&code='+authorization_code+'&redirect_uri=http://localhost&code_verifier='+code_verifier,
            'clientId': os.environ['TEST_AUTHLETE_CLIENT_ID'],
            'clientSecret': os.environ['TEST_AUTHLETE_CLIENT_SECRET']
        })
    )
    data = response.json()
    return data['refreshToken']


def get_authorization_code(code_challenge):
    authlete_token = get_authlete_token()
    response = requests.post(
        url='https://api.authlete.com/api/auth/authorization',
        auth=(authlete_token.get('authlete_api_key'), authlete_token.get('authlete_api_secret')),
        headers={'content-type': 'application/json'},
        data=json.dumps({'parameters': 'code_challenge='+code_challenge+'&code_challenge_method=S256&response_type=code&client_id='+os.environ['TEST_AUTHLETE_CLIENT_ID']+'&redirect_uri=http://localhost&scope=openid%20read'})
    )
    data = response.json()

    response = requests.post(
        url='https://api.authlete.com/api/auth/authorization/issue',
        auth=(authlete_token.get('authlete_api_key'), authlete_token.get('authlete_api_secret')),
        headers={'content-type': 'application/json'},
        data=json.dumps({'ticket': data['ticket'], 'subject': os.environ['TEST_COGNITO_USER_ID']})
    )

    data = response.json()
    return data['authorizationCode']


def get_authlete_token():
    ssm = boto3.client('ssm')
    param = ssm.get_parameter(
        Name=os.environ['ALIS_APP_ID'] + 'ssmAutlteleApiKey'
    )
    authlete_api_key = param['Parameter']['Value']
    param = ssm.get_parameter(
        Name=os.environ['ALIS_APP_ID'] + 'ssmAutlteleApiSecret'
    )
    authlete_api_secret = param['Parameter']['Value']

    return {
        'authlete_api_key': authlete_api_key,
        'authlete_api_secret': authlete_api_secret
    }


def get_token_for_client_authentication():
    basicauth_str = os.environ['TEST_AUTHLETE_CLIENT_ID'] + ':' + os.environ[
        'TEST_AUTHLETE_CLIENT_SECRET']
    return base64.b64encode(basicauth_str.encode('utf-8')).decode('UTF-8')


def get_code_verifier(n_bytes=64):
    return base64.urlsafe_b64encode(os.urandom(n_bytes)).rstrip(b'=').decode(
        'utf-8')


def get_code_challenge(verifier):
    digest = hashlib.sha256(verifier.encode('utf-8')).digest()
    return base64.urlsafe_b64encode(digest).rstrip(b'=').decode('utf-8')
