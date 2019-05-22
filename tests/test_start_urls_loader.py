from io import StringIO
from unittest.mock import Mock

import pytest
from scrapy import Spider, signals
from scrapy.crawler import Crawler
from scrapy.exceptions import NotConfigured

from spider_feeder.loaders import StartUrlsLoader


def return_string_io(content):
    def fn(file_path, encoding):
        return StringIO(content)
    return fn


custom_reader = Mock(side_effect=return_string_io('http://override.com'))


@pytest.fixture
def get_crawler():
    def _crawler(extended_settings={}):
        settings = {
            "EXTENSIONS": {"spider_feeder.loaders.StartUrlsLoader": 500},
        }
        settings.update(extended_settings)
        crawler = Crawler(Spider, settings=settings)
        crawler.spider = Spider("dummy")
        return crawler

    return _crawler


def test_start_urls_loader_not_configured(get_crawler):
    crawler = get_crawler()
    with pytest.raises(NotConfigured):
        StartUrlsLoader.from_crawler(crawler)


def test_start_urls_loader_should_register_signals(get_crawler, mocker):
    mock = mocker.patch('spider_feeder.file_handler.local.open')
    mock.side_effect = return_string_io('https://url1.com\nhttps://url2.com')

    crawler = get_crawler({'SPIDERFEEDER_INPUT_FILE': 'file:///tmp/input_file.txt'})
    StartUrlsLoader.from_crawler(crawler)

    crawler.signals.send_catch_log(signals.spider_opened, spider=crawler.spider)

    assert crawler.spider.start_urls == ['https://url1.com', 'https://url2.com']
    mock.assert_called_with('file:///tmp/input_file.txt', encoding='utf-8')


def test_start_urls_loader_should_open_file_given_scheme(get_crawler, mocker):
    mock = mocker.patch('spider_feeder.file_handler.s3.open')
    mock.side_effect = return_string_io('https://url1.com\nhttps://url2.com')

    crawler = get_crawler({'SPIDERFEEDER_INPUT_FILE': 's3://input_file.txt'})
    StartUrlsLoader.from_crawler(crawler)

    crawler.signals.send_catch_log(signals.spider_opened, spider=crawler.spider)

    assert crawler.spider.start_urls == ['https://url1.com', 'https://url2.com']
    mock.assert_called_with('s3://input_file.txt', encoding='utf-8')


def test_no_scheme_should_load_local_file(get_crawler, mocker):
    mock = mocker.patch('spider_feeder.file_handler.local.open')
    mock.side_effect = return_string_io('https://url1.com\nhttps://url2.com')

    crawler = get_crawler({'SPIDERFEEDER_INPUT_FILE': 'local.txt'})
    StartUrlsLoader.from_crawler(crawler)

    crawler.signals.send_catch_log(signals.spider_opened, spider=crawler.spider)

    mock.assert_called_with('local.txt', encoding='utf-8')


def test_should_override_reader(get_crawler, mocker):
    crawler = get_crawler({
        'SPIDERFEEDER_INPUT_FILE': 's3://input_file.txt',
        'SPIDERFEEDER_FILE_HANDLERS': {
            's3': 'tests.test_start_urls_loader.custom_reader'
        }
    })
    StartUrlsLoader.from_crawler(crawler)

    crawler.signals.send_catch_log(signals.spider_opened, spider=crawler.spider)

    assert crawler.spider.start_urls == ['http://override.com']


def test_uri_format_spider_attributes(get_crawler, mocker):
    mock = mocker.patch('spider_feeder.file_handler.local.open')
    mock.side_effect = return_string_io('https://url1.com\nhttps://url2.com')

    crawler = get_crawler({'SPIDERFEEDER_INPUT_FILE': '%(dir)s/%(input_file)s.txt'})
    crawler.spider.dir = '/tmp'
    crawler.spider.input_file = 'spider_input'
    StartUrlsLoader.from_crawler(crawler)

    crawler.signals.send_catch_log(signals.spider_opened, spider=crawler.spider)

    mock.assert_called_with('/tmp/spider_input.txt', encoding='utf-8')


def test_default_encoding(get_crawler, mocker):
    mock = mocker.patch('spider_feeder.file_handler.local.open')
    mock.side_effect = return_string_io('https://url1.com\nhttps://url2.com')

    crawler = get_crawler({'SPIDERFEEDER_INPUT_FILE': 'local.txt'})
    StartUrlsLoader.from_crawler(crawler)

    crawler.signals.send_catch_log(signals.spider_opened, spider=crawler.spider)

    mock.assert_called_with('local.txt', encoding='utf-8')


def test_file_encoding(get_crawler, mocker):
    mock = mocker.patch('spider_feeder.file_handler.local.open')
    mock.side_effect = return_string_io('https://url1.com\nhttps://url2.com')

    crawler = get_crawler({
        'SPIDERFEEDER_INPUT_FILE': 'local.txt',
        'SPIDERFEEDER_INPUT_FILE_ENCODING': 'latin-1'
    })
    StartUrlsLoader.from_crawler(crawler)

    crawler.signals.send_catch_log(signals.spider_opened, spider=crawler.spider)

    mock.assert_called_with('local.txt', encoding='latin-1')
