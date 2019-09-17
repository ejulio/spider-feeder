import json
from io import StringIO

from scrapy.settings import Settings
import pytest

from spider_feeder.store.file_store import FileStore


def custom_open():
    pass


def custom_parser():
    pass


SCHEMES_AND_OPENERS_TO_MOCK = [
    ('file://', 'spider_feeder.store.file_handler.local.open'),
    ('s3://', 'spider_feeder.store.file_handler.s3.open'),
    ('', 'spider_feeder.store.file_handler.local.open'),
    ('http://', 'spider_feeder.store.file_handler.http.open'),
    ('https://', 'spider_feeder.store.file_handler.http.open'),
]


@pytest.mark.parametrize('uri_scheme, file_opener', SCHEMES_AND_OPENERS_TO_MOCK)
def test_load_txt_file(mocker, uri_scheme, file_opener):
    file_content = StringIO('\n'.join(['http://url1.com', 'http://url2.com']))
    mock = mocker.patch(file_opener, return_value=file_content, autospec=True)

    settings = Settings()
    store = FileStore(f'{uri_scheme}temp.txt', settings)

    store_meta = []
    store_urls = []
    for (url, meta) in store:
        store_urls.append(url)
        store_meta.append(meta)

    mock.assert_called_with(f'{uri_scheme}temp.txt', encoding='utf-8', settings=settings)
    assert store_meta == [{}, {}]
    assert store_urls == ['http://url1.com', 'http://url2.com']


@pytest.mark.parametrize('uri_scheme, file_opener', SCHEMES_AND_OPENERS_TO_MOCK)
def test_load_csv_file(mocker, uri_scheme, file_opener):
    file_content = StringIO('\n'.join([
        '"url_id","url"',
        '"1","http://url1.com"',
        '"2","http://url2.com"'
    ]))
    mock = mocker.patch(file_opener, return_value=file_content, autospec=True)

    settings = Settings({
        'SPIDERFEEDER_INPUT_FIELD': 'url'
    })
    store = FileStore(f'{uri_scheme}temp.csv', settings)

    store_meta = []
    store_urls = []
    for (url, meta) in store:
        store_urls.append(url)
        store_meta.append(meta)

    mock.assert_called_with(f'{uri_scheme}temp.csv', encoding='utf-8', settings=settings)
    assert store_urls == ['http://url1.com', 'http://url2.com']
    assert store_meta == [
        {'url_id': '1', 'url': 'http://url1.com'},
        {'url_id': '2', 'url': 'http://url2.com'}
    ]


@pytest.mark.parametrize('uri_scheme, file_opener', SCHEMES_AND_OPENERS_TO_MOCK)
def test_load_json_file(mocker, uri_scheme, file_opener):
    file_content = StringIO(json.dumps([
        {'url_id': '1', 'url': 'http://url1.com'},
        {'url_id': '2', 'url': 'http://url2.com'}
    ]))
    mock = mocker.patch(file_opener, return_value=file_content, autospec=True)

    settings = Settings({
        'SPIDERFEEDER_INPUT_FIELD': 'url'
    })
    store = FileStore(f'{uri_scheme}temp.json', settings)

    store_meta = []
    store_urls = []
    for (url, meta) in store:
        store_urls.append(url)
        store_meta.append(meta)

    mock.assert_called_with(f'{uri_scheme}temp.json', encoding='utf-8', settings=settings)
    assert store_urls == ['http://url1.com', 'http://url2.com']
    assert store_meta == [
        {'url_id': '1', 'url': 'http://url1.com'},
        {'url_id': '2', 'url': 'http://url2.com'}
    ]


@pytest.mark.parametrize('uri_scheme, file_opener', SCHEMES_AND_OPENERS_TO_MOCK)
def test_get_file_format_from_setting(mocker, uri_scheme, file_opener):
    file_content = StringIO('\n'.join(['http://url1.com', 'http://url2.com']))
    mock = mocker.patch(file_opener, return_value=file_content, autospec=True)

    settings = Settings({
        'SPIDERFEEDER_INPUT_FORMAT': 'txt'
    })
    store = FileStore(f'{uri_scheme}temp', settings)

    store_meta = []
    store_urls = []
    for (url, meta) in store:
        store_urls.append(url)
        store_meta.append(meta)

    mock.assert_called_with(f'{uri_scheme}temp', encoding='utf-8', settings=settings)
    assert store_meta == [{}, {}]
    assert store_urls == ['http://url1.com', 'http://url2.com']


@pytest.mark.parametrize('uri_scheme, file_opener', SCHEMES_AND_OPENERS_TO_MOCK)
def test_get_file_format_setting_is_preferred_over_file_extension(mocker, uri_scheme, file_opener):
    file_content = StringIO('\n'.join(['http://url1.com', 'http://url2.com']))
    mock = mocker.patch(file_opener, return_value=file_content, autospec=True)

    settings = Settings({
        'SPIDERFEEDER_INPUT_FORMAT': 'txt'
    })
    store = FileStore(f'{uri_scheme}temp.csv', settings)

    store_meta = []
    store_urls = []
    for (url, meta) in store:
        store_urls.append(url)
        store_meta.append(meta)

    mock.assert_called_with(f'{uri_scheme}temp.csv', encoding='utf-8', settings=settings)
    assert store_meta == [{}, {}]
    assert store_urls == ['http://url1.com', 'http://url2.com']


def test_fail_if_input_field_and_not_dict_data(mocker):
    mocker.patch(
        'spider_feeder.store.file_handler.local.open',
        return_value=StringIO('\n'.join(['http://url1.com', 'http://url2.com'])),
        autospec=True
    )

    store = FileStore(f'temp.txt', Settings({
        'SPIDERFEEDER_INPUT_FIELD': 'url'
    }))

    with pytest.raises(TypeError) as e:
        for (url, meta) in store:
            pass

    assert 'Data is expected to be a dict when SPIDERFEEDER_INPUT_FIELD is set.' == e.value.args[0]


def test_file_encoding(mocker):
    mock = mocker.patch(
        'spider_feeder.store.file_handler.local.open',
        return_value=StringIO('\n'.join(['http://url1.com', 'http://url2.com'])),
        autospec=True
    )

    settings = Settings({
        'SPIDERFEEDER_INPUT_FILE_ENCODING': 'latin-1'
    })
    store = FileStore('temp.txt', settings)

    for (url, meta) in store:
        pass

    mock.assert_called_with('temp.txt', encoding='latin-1', settings=settings)


def test_custom_file_handler(mocker):
    mock = mocker.patch('tests.store.test_file_store.custom_open')
    mock.return_value = StringIO('\n'.join(['http://url1.com', 'http://url2.com']))

    settings = Settings({
        'SPIDERFEEDER_FILE_HANDLERS': {
            'sc': 'tests.store.test_file_store.custom_open'
        }
    })
    store = FileStore('sc://temp.txt', settings)

    for (url, meta) in store:
        pass

    mock.assert_called_with('sc://temp.txt', encoding='utf-8', settings=settings)


def test_custom_file_parser(mocker):
    content = StringIO('\n'.join(['http://url1.com', 'http://url2.com']))
    mocker.patch(
        'spider_feeder.store.file_handler.local.open',
        return_value=content,
        autospec=True
    )

    mock = mocker.patch('tests.store.test_file_store.custom_parser')
    mock.return_value = []

    settings = Settings({
        'SPIDERFEEDER_FILE_PARSERS': {
            'abc': 'tests.store.test_file_store.custom_parser'
        }
    })
    store = FileStore('temp.abc', settings)

    for (url, meta) in store:
        pass

    mock.assert_called_with(content, settings)
