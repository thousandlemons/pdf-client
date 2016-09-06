from pdf_client.api.base import BaseRequest


class VersionRequest(BaseRequest):
    def get_partial_url(self):
        return 'version/' + self.partial_url


class List(VersionRequest):
    method = 'GET'
    partial_url = 'list/'
    expected_status_code = 200


class Detail(VersionRequest):
    method = 'GET'
    partial_url = 'detail/'
    expected_status_code = 200


class Create(VersionRequest):
    method = 'PUT'
    partial_url = 'create/'
    expected_status_code = 201

    def __init__(self, name, auth=None):
        super().__init__(auth=auth)
        self.data = {
            'name': name
        }


class Update(VersionRequest):
    method = 'POST'
    partial_url = 'update/'
    expected_status_code = 200

    def __init__(self, *url_params, name, auth=None):
        super().__init__(*url_params, auth=auth)
        self.data = {
            'name': name
        }


class Delete(VersionRequest):
    method = 'DELETE'
    partial_url = 'delete/'
    expected_status_code = 204

    def on_success(self, response):
        return True
