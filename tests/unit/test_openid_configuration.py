import os
from lambdas.http.well_known.openid_configuration import handler
from lib.exceptions import AuthleteApiError
from unittest import TestCase


class TestOpenidConfiguration(TestCase):
    def test_return_500(self):
        os.environ['AUTHLETE_API_KEY'] = 'xxxxxxx'
        os.environ['AUTHLETE_API_SECRET'] = 'xxxxxxx'
        response = handler({}, {})
        assert response['statusCode'] == 500
        assert response['body'] == '{"error_message": "Internal Server Error"}'
