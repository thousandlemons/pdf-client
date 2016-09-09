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

    source_version = None
    target_version = None

    create = False
    name = None

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
        self._executor = futures.ThreadPoolExecutor(max_workers=self.threads)

    def _process_section(self, section_id):
        try:
            text = content.Immediate(section_id, self.source_version).send_request()
            text = self.processor.process(text, section_id)
            if self.target_version:
                content.Post(section_id, self.target_version, text=text).send_request()
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

        if not self.source_version:
            version_list = version.List().send_request()
            if not version_list:
                _LOGGER.error("Unable to find a default source version. Returning empty array.")
                return []
            self.source_version = version_list[0]['id']
        else:
            source_version = version.Detail(self.source_version).send_request()
            if not source_version:
                _LOGGER.error("Unable to find source version id={id}. Returning empty array.".format(
                    id=self.source_version))

        if self.target_version:
            if not version.Detail(self.target_version).send_request():
                _LOGGER.error("Unable to find target version id={id}. Returning empty array.".format(
                    id=self.target_version))
                return []

        elif self.create:
            if not self.name:
                _LOGGER.error("No version name specified. Returning empty array.")

            new_version = version.Create(self.name).send_request()

            if not new_version:
                _LOGGER.error("Unable to create a new version. Returning empty array.")
                return []

            self.target_version = new_version['id']

        else:
            _LOGGER.info("No target version specified. In read-only mode.")

        toc = book.Toc(self.book).send_request() if self.book else section.Toc(self.section).send_request()

        if not toc:
            _LOGGER.error(
                'No TOC found for book={book} or section={section}. Returning empty array.'.format(
                    book=self.book,
                    section=self.section))
            return []

        _LOGGER.info(
            "Starting job: section={section}, source_version={source}, target_version={target}".format(
                section=toc['id'],
                source=self.source_version,
                target=self.target_version))

        self._recursive_submit(toc)
        return futures.as_completed(self._future_list)
