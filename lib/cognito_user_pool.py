import boto3
from botocore.exceptions import ClientError

class CognitoUserPool():
    def __init__(self, user_pool_id):
        self.user_pool_id = user_pool_id
        self.client = boto3.client('cognito-idp')

    def get_user_sub_value(self, username):
        try:
            response = self.client.admin_get_user(
                UserPoolId=self.user_pool_id,
                Username=username
            )
            for attribute in response['UserAttributes']:
                if attribute['Name'] == 'sub':
                    return attribute['Value']

        except ClientError as e:
            raise e
