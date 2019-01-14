class AuthleteApiError(Exception):
    def __init__(self, endpoint, status_code, message):
        self._endpoint = endpoint
        self._status_code = status_code
        self._message = message

    def get_endpoint(self):
        return self._endpoint

    def get_status_code(self):
        return self._status_code

    def get_message(self):
        return self._message

    def __str__(self):
        return '[Authlete API Error]endpoint:' + str(self._endpoint) + ' status_code:' + \
               str(self._status_code) + ' message:' + str(self._message)

    endpoint = property(get_status_code)
    status_code = property(get_status_code)
    message = property(get_message)

class ValidationError(Exception):
    def __init__(self, status_code, message):
        self._status_code = status_code
        self._message = message


    def get_status_code(self):
        return self._status_code

    def get_message(self):
        return self._message

    def __str__(self):
        return '[Validation Error]status_code:' + \
               str(self._status_code) + ' message:' + str(self._message)

    status_code = property(get_status_code)
    message = property(get_message)
