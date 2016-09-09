import requests

ERROR_MESSAGE_NO_CONFIG = '''

No configuration found!
Add the following before you call send_request()

    from pdf_client import config
    config.load_from_file('...')

For more info, please visit https://github.com/nathanielove/pdf-client
'''


class BaseRequest(object):
    base_url = None
    partial_url = None
    url_params = None

    method = None
    data = None
    auth = None

    expected_status_code = None

    def __init__(self, *url_params, auth=None):
        self.url_params = [str(param) for param in url_params]
        self.auth = auth

    def get_base_url(self):
        return self.base_url

    def get_partial_url(self):
        return self.partial_url

    def get_full_url(self):
        return self.get_base_url() + self.get_partial_url() + '/'.join(self.url_params) + (
            '/' if self.url_params else '')

    def get_method(self):
        return self.method

    def get_data(self):
        return self.data

    def get_auth(self):
        return self.auth if self.auth else BaseRequest.auth

    def on_success(self, response):
        return response.json()

    def on_exception(self, e):
        return False

    def on_error(self, response):
        return False

    def execute(self):

        if self.base_url is None:
            raise Exception(ERROR_MESSAGE_NO_CONFIG)

        try:
            response = requests.request(method=self.get_method(), url=self.get_full_url(), data=self.get_data(),
                                        auth=self.get_auth())
        except requests.exceptions.RequestException as e:
            return self.on_exception(e)

        if response.status_code == self.expected_status_code:
            return self.on_success(response)
        else:
            return self.on_error(response)


class ReadOnlyRequest(BaseRequest):
    method = 'GET'
    expected_status_code = 200
