from urllib.parse import urlparse

from scrapy import signals
from scrapy.exceptions import NotConfigured
from scrapy.utils.misc import load_object


class StartUrlsLoader:

    READERS = {
        'file': 'spider_feeder.readers.open_local',
        's3': 'spider_feeder.readers.open_s3',
    }

    @classmethod
    def from_crawler(cls, crawler):
        input_file_uri = crawler.settings.get('SPIDERFEEDER_INPUT_FILE', None)
        if not input_file_uri:
            raise NotConfigured('StartUrlsLoader requires SPIDERFEEDER_INPUT_FILE setting.')

        readers = crawler.settings.getdict('SPIDERFEEDER_READERS', {})
        readers = dict(cls.READERS, **readers)
        extension = cls(input_file_uri, readers)

        crawler.signals.connect(extension.spider_openened, signal=signals.spider_opened)

        return extension

    def __init__(self, input_file_uri, readers):
        self._input_file_uri = input_file_uri
        self._readers = readers

    def spider_openened(self, spider):
        with self._open_input_file() as f:
            content = f.read().decode('utf-8')
            spider.start_urls = content.splitlines()

    def _open_input_file(self):
        parsed = urlparse(self._input_file_uri)
        file_path = f'{parsed.netloc}{parsed.path}'
        reader = load_object(self._readers[parsed.scheme])
        return reader(file_path)
        