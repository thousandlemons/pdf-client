from api.base import ReadOnlyRequest


class SectionRequest(ReadOnlyRequest):
    def get_partial_url(self):
        return 'section/' + self.partial_url


class Detail(SectionRequest):
    partial_url = 'detail/'


class Children(SectionRequest):
    partial_url = 'children/'


class Versions(SectionRequest):
    partial_url = 'versions/'
