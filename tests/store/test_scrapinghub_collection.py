import pytest
from scrapy.settings import Settings

from spider_feeder.store import scrapinghub_collection
from spider_feeder.store.scrapinghub_collection import ScrapinghubCollectionStore


PROJECT_ID = '1256'
COLLECTION_NAME = 'spider_feeder_unit_tests'
COLLECTION_OF_URLS_ONLY = [
    {'_key': '1', 'value': 'http://url1.com'},
    {'_key': '2', 'value': 'http://url2.com'}
]
COLLECTION_DATA = [
    {'_key': '1', 'value': {'url_id': '12356', 'input_url': 'http://url1.com'}},
    {'_key': '2', 'value': {'url_id': '65234', 'input_url': 'http://url2.com'}}
]


def scrapinghub_client_mocker(mocker, collection_data):
    collection = mocker.patch('scrapinghub.client.collections.Collection', autospec=True)
    collection.iter.return_value = iter(collection_data)

    collections = mocker.patch('scrapinghub.client.collections.Collections', autospec=True)
    collections.get_store.return_value = collection

    project = mocker.patch('scrapinghub.client.projects.Project', autospec=True)
    project.collections = collections

    client = mocker.patch('scrapinghub.ScrapinghubClient', autospec=True)
    client.get_project.return_value = project

    mocker.patch.object(scrapinghub_collection, 'ScrapinghubClient', return_value=client)

    return client


@pytest.fixture
def environment_vars_mocker(mocker):
    mock = mocker.patch.object(scrapinghub_collection, 'os')
    mock.environ = {
        'SHUB_JOBKEY': f'{PROJECT_ID}/1/1'
    }


def test_load_urls_if_input_field_does_not_exist(mocker, environment_vars_mocker):
    scrapinghub_client_mock = scrapinghub_client_mocker(mocker, COLLECTION_OF_URLS_ONLY)
    store = ScrapinghubCollectionStore(f'collections://{COLLECTION_NAME}', Settings())

    expected_urls = [x['value'] for x in COLLECTION_OF_URLS_ONLY]
    store_urls = [url for (url, _) in store]
    assert expected_urls == store_urls

    scrapinghub_client_mock.get_project.assert_called_with(PROJECT_ID)
    project = scrapinghub_client_mock.get_project(PROJECT_ID)
    project.collections.get_store.assert_called_with(COLLECTION_NAME)


@pytest.mark.parametrize('field', ['', None])
def test_load_urls_if_field_is_empty(field, mocker, environment_vars_mocker):
    scrapinghub_client_mocker(mocker, COLLECTION_OF_URLS_ONLY)
    store = ScrapinghubCollectionStore(f'collections://{COLLECTION_NAME}', Settings({
        'SPIDERFEEDER_INPUT_FIELD': field
    }))

    expected_urls = [x['value'] for x in COLLECTION_OF_URLS_ONLY]
    store_urls = [url for (url, _) in store]
    assert expected_urls == store_urls


def test_load_urls_and_meta(mocker, environment_vars_mocker):
    scrapinghub_client_mocker(mocker, COLLECTION_DATA)
    store = ScrapinghubCollectionStore(f'collections://{COLLECTION_NAME}', Settings({
        'SPIDERFEEDER_INPUT_FIELD': 'input_url'
    }))

    expected_meta = [x['value'] for x in COLLECTION_DATA]
    expected_urls = [x['value']['input_url'] for x in COLLECTION_DATA]
    store_urls = []
    store_meta = []
    for (url, meta) in store:
        store_urls.append(url)
        store_meta.append(meta)

    assert store_meta == expected_meta
    assert store_urls == expected_urls


def test_fail_if_input_field_collection_content_is_not_dict(mocker, environment_vars_mocker):
    scrapinghub_client_mocker(mocker, COLLECTION_OF_URLS_ONLY)
    store = ScrapinghubCollectionStore(f'collections://{COLLECTION_NAME}', Settings({
        'SPIDERFEEDER_INPUT_FIELD': 'input_url'
    }))

    with pytest.raises(TypeError) as e:
        for (url, meta) in store:
            pass

    assert 'Data is expected to be a dict when SPIDERFEEDER_INPUT_FIELD is set.' == e.value.args[0]  # noqa
