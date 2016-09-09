import logging
from concurrent import futures

from pdf_client.api import book
from pdf_client.api import content, section
from pdf_client.api import version

_LOGGER = logging.getLogger(__name__)


class MultiThreadWorker(object):
    processor = None

    threads = 10
    _executor = None
    _future_list = []

    book = None
    section = None

    source = None
    target = None

    create = False
    name = None

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
        self._executor = futures.ThreadPoolExecutor(max_workers=self.threads)

    def _process_section(self, section_id):
        try:
            text = content.Immediate(section_id, self.source).execute()
            text = self.processor.process(text, section_id)
            if self.target:
                content.Post(section_id, self.target, text=text).execute()
            _LOGGER.info("Completed processing section id={id}".format(id=section_id))
            return section_id, text
        except Exception as e:
            _LOGGER.exception("Exception raised when processing section id={id}: {e}".format(id=section_id, e=e))
            raise e

    def _recursive_submit(self, node):
        section_id = node['id']
        self._future_list.append(self._executor.submit(self._process_section, section_id))
        _LOGGER.debug("Submitted processing job for section id={id}".format(id=section_id))
        for child in node['children']:
            self._recursive_submit(child)

    def start(self):

        if not self.source:
            version_list = version.List().execute()
            if not version_list:
                _LOGGER.error("Unable to find a default source version. Returning empty array.")
                return []
            self.source = version_list[0]['id']
        else:
            source_version = version.Detail(self.source).execute()
            if not source_version:
                _LOGGER.error("Unable to find source version id={id}. Returning empty array.".format(id=self.source))
                return []

        toc = book.Toc(self.book).execute() if self.book else section.Toc(self.section).execute()

        if not toc:
            if self.book:
                _LOGGER.error('No TOC found for book={book}. Returning empty array.'.format(book=self.book))
            else:
                _LOGGER.error('No TOC found for section={section}. Returning empty array.'.format(section=self.section))
            return []

        if self.target:
            if not version.Detail(self.target).execute():
                _LOGGER.error("Unable to find target version id={id}. Returning empty array.".format(id=self.target))
                return []

        elif self.create:
            if not self.name:
                _LOGGER.error("No version name specified. Returning empty array.")
                return []

            new_version = version.Create(self.name).execute()

            if not new_version:
                _LOGGER.error("Unable to create a new version. Returning empty array.")
                return []

            self.target = new_version['id']

        else:
            _LOGGER.info("No target version specified. In read-only mode.")

        _LOGGER.info("Starting job: section={section}, source={source}, target={target}".format(section=toc['id'],
                                                                                                source=self.source,
                                                                                                target=self.target))

        self._recursive_submit(toc)
        return futures.as_completed(self._future_list)
