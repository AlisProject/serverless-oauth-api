import string
import random
import requests
import json
import boto3
from .common import api_deploy, api_remove, get_endpoint_url
from .conftest import option


class TestUsers(object):
    @classmethod
    def setup_class(cls):
        db_deploy(option.stage, option.region)
        api_deploy(option.stage, option.region)
        cls.dynamodb = boto3.resource('dynamodb', region_name=option.region)
        cls.endpoint = get_endpoint_url(option.stage, option.region)
        cls.user_id = cls._get_randam_value(cls)
        cls.email = cls.user_id + '@example.com'
        cls.users_table = cls.dynamodb.Table('users-' + option.stage)

    @classmethod
    def steardown_class(cls):
        api_remove(option.stage, option.region)
        db_remove(option.stage, option.region)
        cls._delete_all_tables(cls)

    def setup(self):
        self.email = self._get_randam_value() + '@example.com'

    def test_create(self):
        payload = {'email': self.email}
        url = self.endpoint + '/users/' + self.user_id
        r = requests.post(url, data=json.dumps(payload))
        user = self._get_user(user_id=self.user_id)

        assert r.status_code == 201
        assert user['Item']['email'] == self.email

    def test_update(self):
        payload = {'email': self.email}
        url = self.endpoint + '/users/' + self.user_id
        r = requests.put(url, data=json.dumps(payload))
        user = self._get_user(user_id=self.user_id)

        assert r.status_code == 204
        assert user['Item']['email'] == self.email

    def test_get(self):
        url = self.endpoint + '/users/' + self.user_id
        r = requests.get(url)
        data = r.json()

        assert r.status_code == 200
        assert 'email' in data
        assert 'user_id' in data
        assert 'createdAt' in data
        assert 'updatedAt' in data

    def test_list(self):
        url = self.endpoint + '/users'
        r = requests.get(url)
        items = r.json()

        assert r.status_code == 200
        for data in items:
            assert 'email' in data
            assert 'user_id' in data
            assert 'createdAt' in data
            assert 'updatedAt' in data

    def test_delete(self):
        url = self.endpoint + '/users/' + self.user_id
        r = requests.delete(url)
        user = self._get_user(user_id=self.user_id)

        assert r.status_code == 204
        assert 'Item' not in user

    def _get_user(self, user_id):
        return self.users_table.get_item(
            Key={
                'user_id': user_id
            }
        )

    def _get_randam_value(self):
        return ''.join([
            random.choice('%s%s' % (string.ascii_letters, string.digits))
            for i in range(10)
        ])

    def _delete_all_tables(self):
        self.users_table.delete()
