from urllib.parse import urlparse

from scrapy import signals
from scrapy.exceptions import NotConfigured
from scrapy.utils.misc import load_object


class StartUrlsLoader:

    FILE_HANDLERS = {
        'file': 'spider_feeder.file_handler.local.open',
        's3': 'spider_feeder.file_handler.s3.open',
    }

    @classmethod
    def from_crawler(cls, crawler):
        input_file_uri = crawler.settings.get('SPIDERFEEDER_INPUT_FILE', None)
        if not input_file_uri:
            raise NotConfigured('StartUrlsLoader requires SPIDERFEEDER_INPUT_FILE setting.')

        handlers = crawler.settings.getdict('SPIDERFEEDER_FILEHANDLERS', {})
        handlers = dict(cls.FILE_HANDLERS, **handlers)
        extension = cls(input_file_uri, handlers)

        crawler.signals.connect(extension.spider_openened, signal=signals.spider_opened)

        return extension

    def __init__(self, input_file_uri, handlers):
        self._input_file_uri = input_file_uri
        self._file_handlers = handlers

    def spider_openened(self, spider):
        with self._open_input_file() as f:
            content = f.read().decode('utf-8')
            spider.start_urls = content.splitlines()

    def _open_input_file(self):
        parsed = urlparse(self._input_file_uri)
        file_path = f'{parsed.netloc}{parsed.path}'
        open = load_object(self._file_handlers[parsed.scheme])
        return open(file_path)
        