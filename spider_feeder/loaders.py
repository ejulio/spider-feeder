from urllib.parse import urlparse
import logging
from itertools import tee

from scrapy import signals
from scrapy.exceptions import NotConfigured
from scrapy.utils.misc import load_object

logger = logging.getLogger(__name__)


class BaseLoader:
    '''Base loader for `start_urls` and `start_requests` loaders.
    The data is loaded from `SPIDERFEEDER_INPUT_URI`.
    The given store is loaded according to the scheme in `SPIDERFEEDER_INPUT_URI`.
    Currently, the support is for local file system, Amazon AWS S3, and Scrapinghub Collections.
    The stores can be overriden or aggregated through `SPIDERFEEDER_STORES`.

    `SPIDERFEEDER_INPUT_URI` supports %(params) as in scrapy's `FEED_URI`.
    '''

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
            raise NotConfigured('Loader requires SPIDERFEEDER_INPUT_URI setting.')

        stores = cls.STORES
        stores = dict(stores, **crawler.settings.getdict('SPIDERFEEDER_STORES', {}))

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
        self.set_spider_input_data(spider, store)

    def _get_formatted_input_uri(self, spider):
        params = {k: getattr(spider, k) for k in dir(spider)}
        return self._input_uri % params

    def _get_store(self, input_uri):
        parsed = urlparse(input_uri)
        store_cls = load_object(self._stores[parsed.scheme])
        return store_cls(input_uri, self._crawler.settings)

    def set_spider_input_data(self, spider, store):
        raise NotImplementedError()


class StartUrlsLoader(BaseLoader):
    '''Loader setting spider.start_urls. For more information, please refer to BaseLoader.'''

    def set_spider_input_data(self, spider, store):
        store = _Iter(self._crawler, spider, store)
        spider.start_urls = (url for (url, _) in store)


class StartUrlsAndMetaLoader(BaseLoader):
    '''Loader setting spider.start_urls and spider.start_meta.
    For more information, please refer to BaseLoader.'''

    def set_spider_input_data(self, spider, store):
        store = _Iter(self._crawler, spider, store)
        (url_iter, meta_iter) = tee(store)
        spider.start_urls = (url for (url, _) in url_iter)
        setattr(spider, 'start_meta', (meta for (_, meta) in meta_iter))


class _Iter:

    def __init__(self, crawler, spider, store):
        self._crawler = crawler
        self._spider = spider
        self._store = store

    def __call__(self):
        yield from self

    def __iter__(self):
        for item in self._store:
            yield item
            self._crawler.stats.inc_value(f'spider_feeder/{self._spider.name}/url_count')
