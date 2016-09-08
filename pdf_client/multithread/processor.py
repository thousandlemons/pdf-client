from abc import abstractmethod


class TextProcessor(object):
    @abstractmethod
    def process(self, text, section_id):
        pass
