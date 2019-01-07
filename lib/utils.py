import json
import logging
import decimal
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def response_builder(status_code, body={}):
    return {
        'statusCode': status_code,
        'body': json.dumps(body, cls=DecimalEncoder)
    }


class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, decimal.Decimal):
            return int(obj)
        return super(DecimalEncoder, self).default(obj)
