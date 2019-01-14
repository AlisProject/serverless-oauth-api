import sys
import subprocess
import boto3
import yaml
import os
import requests
import json


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

def get_access_token():
    ssm = boto3.client('ssm')
    param = ssm.get_parameter(
        Name=os.environ['ALIS_APP_ID'] + 'ssmAutlteleApiKey'
    )
    authlete_api_key = param['Parameter']['Value']
    param = ssm.get_parameter(
        Name=os.environ['ALIS_APP_ID'] + 'ssmAutlteleApiSecret'
    )
    authlete_api_secret = param['Parameter']['Value']

    response = requests.post(
        url='https://api.authlete.com/api/auth/authorization',
        auth=(authlete_api_key, authlete_api_secret),
        headers={'content-type': 'application/json'},
        data=json.dumps({'parameters':'code_challenge=hcCb3gToI1GPZeS_SIYWvaNT_5u0GB1oqOGQJqRKMSE&code_challenge_method=S256&response_type=code&client_id='+os.environ['TEST_AUTHLETE_CLIENT_ID']+'&redirect_uri=http://localhost&scope=openid%20read'})
    )
    data = response.json()

    response = requests.post(
        url='https://api.authlete.com/api/auth/authorization/issue',
        auth=(authlete_api_key, authlete_api_secret),
        headers={'content-type': 'application/json'},
        data=json.dumps({'ticket':data['ticket'], 'subject':os.environ['TEST_COGNITO_USER_ID']})
    )

    data = response.json()
    response = requests.post(
        url='https://api.authlete.com/api/auth/token',
        auth=(authlete_api_key, authlete_api_secret),
        headers={'content-type': 'application/json'},
        data=json.dumps({
            'parameters':'grant_type=authorization_code&code='+data['authorizationCode']+'&redirect_uri=http://localhost&code_verifier=7vN7KSmEl5qFeHeRZmfMsR7fl_BsluESjvl32W9el5A6WgsAbXCaqwK43BmXjs7cGw9hTQC9xmVb41xi8fL4CA',
            'clientId':os.environ['TEST_AUTHLETE_CLIENT_ID'],
            'clientSecret':os.environ['TEST_AUTHLETE_CLIENT_SECRET']
        })
    )
    data = response.json()
    return data['accessToken']
