import os

from scrapinghub import ScrapinghubClient
from scrapinghub.client.utils import parse_job_key

from .base_store import BaseStore


class ScrapinghubCollectionStore(BaseStore):
    '''Store class abstracting `ScrapinghubClient`.
    No configuration for authentication is set. `ScrapinghubClient` loads from environment variables.
    For more information, please refer to https://python-scrapinghub.readthedocs.io/en/latest/client/apidocs.html#scrapinghub.client.ScrapinghubClient.
    The project is identified through `SHUB_JOBKEY` environment variable which is set in Scrapy Cloud.
    For more information, please refer to https://shub.readthedocs.io/en/stable/custom-images-contract.html.
    '''

    def __init__(self, input_uri, settings):
        super().__init__(settings)
        client = ScrapinghubClient()

        jobkey = parse_job_key(os.environ['SHUB_JOBKEY'])
        project = client.get_project(jobkey.project_id)

        collection_name = input_uri.replace('collections://', '')
        self._store = project.collections.get_store(collection_name)

    def read_input_items(self):
        for item in self._store.iter():
            yield item['value']
