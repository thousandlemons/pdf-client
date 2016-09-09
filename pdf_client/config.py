import json

import requests # this import must be present for the load_from_file() method to work

from pdf_client.api.base import BaseRequest

KEY_BASE_URL = 'base_url'
KEY_AUTH_CLASS = 'auth_class'
KEY_AUTH_ARGS = 'auth_args'


def set_basic_auth(username, password):
    BaseRequest.auth = (username, password)


def set_auth(auth):
    BaseRequest.auth = auth


def set_base_url(base_url):
    BaseRequest.base_url = base_url


def load_from_file(filename):
    with open(filename, 'r') as file:
        data = json.loads(file.read().replace('\n', ''))
        set_base_url(data[KEY_BASE_URL])
        try:
            auth_class_name = data[KEY_AUTH_CLASS]
            auth_args = data[KEY_AUTH_ARGS]
            command = "requests.auth.{class_name}(*{args})".format(class_name=auth_class_name, args=auth_args)
            auth = eval(command, globals(), locals())
            set_auth(auth)
        except KeyError:
            pass
