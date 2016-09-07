from concurrent import futures

from pdf_client.api import book
from pdf_client.api import content, section
from pdf_client.api import version


class TextProcessor(object):
    def process(self, text, section_id):
        pass


class MultiThreadWorker(object):
    processor = None

    threads = None
    _executor = None
    _future_list = []

    book_id = None
    section_id = None

    source_version_id = 1
    target_version_id = None

    create_version = False
    new_version_name = None

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
        self._executor = futures.ThreadPoolExecutor(max_workers=self.threads)

    def _process_section(self, section_id):
        text = content.Immediate(section_id, self.source_version_id).send_request()
        text = self.processor.process(text, section_id)
        if self.target_version_id:
            content.Post(section_id, self.target_version_id, text=text).send_request()
        return text, section_id

    def _recursive_submit(self, node):
        self._future_list.append(self._executor.submit(self._process_section, node['id']))
        for child in node['children']:
            self._recursive_submit(child)

    def submit_all(self):

        if self.create_version:
            new_version = version.Create(self.new_version_name).send_request()

            if not new_version:
                return []

            self.target_version_id = new_version['id']

        toc = book.Toc(self.book_id).send_request() if self.book_id else section.Toc(self.section_id).send_request()

        if not toc:
            return []

        self._recursive_submit(toc)
        return self._future_list
