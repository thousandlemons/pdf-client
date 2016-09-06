from pdf_client.api.base import ReadOnlyRequest


class ContentRequest(ReadOnlyRequest):
    def get_partial_url(self):
        return 'content/' + self.partial_url

    def on_success(self, response):
        return response.text


class Immediate(ContentRequest):
    partial_url = 'immediate/'


class Aggregate(ContentRequest):
    partial_url = 'aggregate/'


class Post(ContentRequest):
    method = 'POST'
    partial_url = 'post/'

    def __init__(self, *url_params, text, auth=None):
        super().__init__(*url_params, auth=auth)
        self.data = text

    def on_success(self, response):
        return True
