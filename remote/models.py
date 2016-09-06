class RemoteModel(object):
    CONFIG = None

    def __init__(self, **kwargs):
        self.__load(kwargs)
        self.__insert_methods()

    def __load(self, data):
        if data is not False:
            self.__dict__.update(data)

    def __insert_methods(self):
        # go to config and find attribute "create"
        #   1) request class
        #   2) args
        #   3) kwargs
        # make_request()
        # self.load()
        pass


class Book(RemoteModel):
    pass


class Section(RemoteModel):
    pass


class Version(RemoteModel):
    CONFIG = {
        'request_package': 'api.version',
        'methods': [
            {
                'name': 'create',
                'request_class': 'Create',
                'args': [],
                'kwargs': [
                    'name'
                ],
                'on_success': '__load',
                'on_error': '_on_error'
            },

        ]
    }

    def _on_error(self, *args, **kwargs):
        pass


class Content(RemoteModel):
    version_id = None
    section_id = None
    text = None

    CONFIG = {
        'request_package': 'api.content',
        'methods': [
            {
                'name': 'post',
                'request_class': 'Post',
                'args': [
                    'section_id',
                    'version_id'
                ],
                'kwargs': [
                    'text'
                ]
            },

        ]
    }

    def __load(self, data):
        self.text = data
