from urllib.parse import urlparse
import logging
from os import path

from scrapy import signals
from scrapy.exceptions import NotConfigured
from scrapy.utils.misc import load_object

logger = logging.getLogger(__name__)


class StartUrlsLoader:

    STORES = {
        '': 'spider_feeder.store.file_store.FileStore',
        'file': 'spider_feeder.store.file_store.FileStore',
        's3': 'spider_feeder.store.file_store.FileStore',
        'collections': 'spider_feeder.store.scrapinghub_collection.ScrapinghubCollectionStore',
    }

    @classmethod
    def from_crawler(cls, crawler):
        input_uri = crawler.settings.get('SPIDERFEEDER_INPUT_URI', None)
        if not input_uri:
            raise NotConfigured('StartUrlsLoader requires SPIDERFEEDER_INPUT_URI setting.')

        stores = cls.STORES
        stores = dict(stores, **crawler.settings.get('SPIDERFEEDER_STORES', {}))

        extension = cls(crawler, input_uri, stores)
        crawler.signals.connect(extension.spider_opened, signal=signals.spider_opened)
        return extension

    def __init__(self, crawler, input_uri, stores):
        self._input_uri = input_uri
        self._crawler = crawler
        self._stores = stores

    def spider_opened(self, spider):
        input_uri = self._get_formatted_input_uri(spider)
        store = self._get_store(input_uri)
        spider.start_urls = [url for (url, _) in store]
        n_urls = len(spider.start_urls)
        logger.info(f'Loaded {n_urls} urls from {input_uri}.')
        self._crawler.stats.set_value(f'spider_feeder/{spider.name}/url_count', n_urls)

    def _get_formatted_input_uri(self, spider):
        params = {k: getattr(spider, k) for k in dir(spider)}
        return self._input_uri % params

    def _get_store(self, input_uri):
        parsed = urlparse(input_uri)
        store_cls = load_object(self._stores[parsed.scheme])
        return store_cls(input_uri, self._crawler.settings)
