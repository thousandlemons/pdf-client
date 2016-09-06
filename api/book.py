from api.base import ReadOnlyRequest


class BookRequest(ReadOnlyRequest):
    def get_partial_url(self):
        return 'book/' + self.partial_url


class List(BookRequest):
    partial_url = 'list/'


class Detail(BookRequest):
    partial_url = 'detail/'


class Toc(BookRequest):
    partial_url = 'toc/'
