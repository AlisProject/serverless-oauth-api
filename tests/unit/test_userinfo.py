import os
from lambdas.http.userinfo import handler
from unittest import TestCase


class TestUserInfo(TestCase):
    def test_return_500_with_authlete_error(self):
        os.environ['AUTHLETE_API_KEY'] = 'xxxxxxx'
        os.environ['AUTHLETE_API_SECRET'] = 'xxxxxxx'
        os.environ['COGNITO_USER_POOL_ID'] = 'xxxxxxx'
        response = handler({'headers':{'Authorization': 'Bearer xxxxxxxx'}}, {})
        assert response['statusCode'] == 500
        assert response['body'] == '{"error_message": "Internal Server Error"}'
