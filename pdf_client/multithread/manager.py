from pdf_client.api import content, section

class BaseTextProcessor(object):
    def process(self, text, section_id):
        pass


class MultiThreadTextProcessor(object):
    processor = None

    section_id = None

    source_version_id = None
    target_version_id = None

    create = False
    new_name = None

    _executor = None
    future_list = []

    def _process_section(self, section_id):
        text = content.Immediate(section_id, self.source_version_id).send_request()
        text = self.processor.process(text)
        if self.target_version_id:
            content.Post(section_id, self.target_version_id, text=text).send_request()
        return text, section_id

    def _recursive_submit(self):
        pass