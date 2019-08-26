from unittest.mock import Mock

import pytest
from scrapy import Spider, signals
from scrapy.crawler import Crawler
from scrapy.exceptions import NotConfigured

from spider_feeder.loaders import StartUrlsLoader


CustomS3Store = Mock()
CustomAbcStore = Mock()


@pytest.fixture
def get_crawler():
    def _crawler(settings={}):
        crawler = Crawler(Spider, settings=settings)
        crawler.spider = Spider("dummy")
        return crawler

    return _crawler


def test_start_urls_loader_not_configured(get_crawler):
    crawler = get_crawler()
    with pytest.raises(NotConfigured):
        StartUrlsLoader.from_crawler(crawler)


@pytest.mark.parametrize('scheme, store_cls', [
    ('s3://', 'spider_feeder.store.file_store.FileStore'),
    ('file://', 'spider_feeder.store.file_store.FileStore'),
    ('', 'spider_feeder.store.file_store.FileStore'),
    ('collections://', 'spider_feeder.store.scrapinghub_collection.ScrapinghubCollectionStore'),
])
def test_start_urls_loader_open_store_given_scheme(get_crawler, mocker, scheme, store_cls):
    mock = mocker.patch(store_cls)
    mock().__iter__.return_value = iter([('https://url1.com', {}), ('https://url2.com', {})])

    crawler = get_crawler({
        'EXTENSIONS': {'spider_feeder.loaders.StartUrlsLoader': 500},
        'SPIDERFEEDER_INPUT_URI': f'{scheme}input_file.txt'}
    )

    crawler.signals.send_catch_log(signals.spider_opened, spider=crawler.spider)

    assert list(crawler.spider.start_urls) == ['https://url1.com', 'https://url2.com']
    mock.assert_called_with(f'{scheme}input_file.txt', crawler.settings)
    assert crawler.stats.get_value(f'spider_feeder/{crawler.spider.name}/url_count') == 2


def test_should_override_store(get_crawler, mocker):
    crawler = get_crawler({
        'EXTENSIONS': {'spider_feeder.loaders.StartUrlsLoader': 500},
        'SPIDERFEEDER_INPUT_URI': 's3://input_file.txt',
        'SPIDERFEEDER_STORES': {
            's3': 'tests.test_loaders.CustomS3Store'
        }
    })

    crawler.signals.send_catch_log(signals.spider_opened, spider=crawler.spider)

    CustomS3Store.assert_called_once_with('s3://input_file.txt', crawler.settings)


def test_should_load_custom_store(get_crawler, mocker):
    crawler = get_crawler({
        'EXTENSIONS': {'spider_feeder.loaders.StartUrlsLoader': 500},
        'SPIDERFEEDER_INPUT_URI': 'abc://input_file.txt',
        'SPIDERFEEDER_STORES': {
            'abc': 'tests.test_loaders.CustomAbcStore'
        }
    })

    crawler.signals.send_catch_log(signals.spider_opened, spider=crawler.spider)

    CustomAbcStore.assert_called_once_with('abc://input_file.txt', crawler.settings)


def test_uri_format_spider_attributes(get_crawler, mocker):
    mock = mocker.patch('spider_feeder.store.file_store.FileStore')
    mock().__iter__.return_value = iter([('https://url1.com', {}), ('https://url2.com', {})])

    crawler = get_crawler({
        'EXTENSIONS': {'spider_feeder.loaders.StartUrlsLoader': 500},
        'SPIDERFEEDER_INPUT_URI': '%(dir)s/%(input_file)s.txt'}
    )
    crawler.spider.dir = '/tmp'
    crawler.spider.input_file = 'spider_input'

    crawler.signals.send_catch_log(signals.spider_opened, spider=crawler.spider)

    mock.assert_called_with('/tmp/spider_input.txt', crawler.settings)


def test_load_start_data(get_crawler, mocker):
    mock = mocker.patch('spider_feeder.store.file_store.FileStore')
    store_data = [
        ('https://url1.com', {'url_id': '1'}),
        ('https://url2.com', {'url_id': '2'}),
        ('https://url2.com', {'url_id': '2'}),
    ]
    mock().__iter__.return_value = iter(store_data)

    crawler = get_crawler({
        'EXTENSIONS': {'spider_feeder.loaders.StartUrlsAndMetaLoader': 500},
        'SPIDERFEEDER_INPUT_URI': 'input_file.csv',
    })

    crawler.signals.send_catch_log(signals.spider_opened, spider=crawler.spider)

    expetcted_urls = [url for (url, meta) in store_data]
    assert expetcted_urls == list(crawler.spider.start_urls)

    expetcted_meta = [meta for (url, meta) in store_data]
    assert expetcted_meta == list(crawler.spider.start_meta)

    assert crawler.stats.get_value(f'spider_feeder/{crawler.spider.name}/url_count') == 3
