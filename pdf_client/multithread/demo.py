from pdf_client import config
from pdf_client.multithread.manager import TextProcessor, MultiThreadWorker


class ExampleProcessor(TextProcessor):
    def process(self, text, section_id):
        # print("Processing {id}".format(id=section_id))
        return text


def main():
    config.load_from_file('../../config.json')

    processor = MultiThreadWorker(processor=ExampleProcessor(),
                                  book_id=2,
                                  threads=10,
                                  target_version_id=25,
                                  create_version=False,
                                  new_version_name='Test version')
    future_list = processor.submit_all()
    print(processor.target_version_id)
    for future in future_list:
        text, section_id = future.result()
        print('Completed {id}'.format(id=section_id))


main()
