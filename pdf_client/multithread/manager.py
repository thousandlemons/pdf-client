from abc import abstractmethod
from concurrent import futures

from pdf_client.api import book
from pdf_client.api import content, section
from pdf_client.api import version


class TextProcessor(object):
    @abstractmethod
    def process(self, text, section_id):
        pass


class MultiThreadWorker(object):
    processor = None

    threads = None
    _executor = None
    _future_list = []

    book = None
    section = None

    source_version = None
    target_version = None

    create = False
    new_name = None

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
        self._executor = futures.ThreadPoolExecutor(max_workers=self.threads)

    def _process_section(self, section_id):
        text = content.Immediate(section_id, self.source_version).send_request()
        text = self.processor.process(text, section_id)
        if self.target_version:
            content.Post(section_id, self.target_version, text=text).send_request()
        return text, section_id

    def _recursive_submit(self, node):
        self._future_list.append(self._executor.submit(self._process_section, node['id']))
        for child in node['children']:
            self._recursive_submit(child)

    def start(self):

        if not self.source_version:
            self.source_version = version.List().send_request()[0]['id']

        if self.create:
            new_version = version.Create(self.new_name).send_request()

            if not new_version:
                return []

            self.target_version = new_version['id']

        toc = book.Toc(self.book).send_request() if self.book else section.Toc(self.section).send_request()

        if not toc:
            return []

        self._recursive_submit(toc)
        return futures.as_completed(self._future_list)
