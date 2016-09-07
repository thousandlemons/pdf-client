import re

from pdf_client import config
from pdf_client.multithread.manager import TextProcessor, MultiThreadWorker


class ExampleProcessor(TextProcessor):
    def process(self, text, section_id):
        # print("Processing {id}".format(id=section_id))
        return re.sub(r'(?:\n|\r|\r\n?)+', '\n', text)


def main():
    config.load_from_file('../../config.json')

    worker = MultiThreadWorker(processor=ExampleProcessor(),
                               book=2,
                               threads=10,
                               target_version=29,
                               # create=True,
                               # new_name='Removed multiple newline'
                               )

    completed = worker.start()

    print("Source version: {id}".format(id=worker.source_version))
    print("Target version: {id}".format(id=worker.target_version))

    for future in completed:
        text, section_id = future.result()
        print('Completed section: {id}'.format(id=section_id))


main()
