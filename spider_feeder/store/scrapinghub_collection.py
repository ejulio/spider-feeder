import os

from scrapinghub import ScrapinghubClient
from scrapinghub.client.utils import parse_job_key


class ScrapinghubCollectionStore:
    '''Store class abstracting `ScrapinghubClient`.
    No configuration for authentication is set. `ScrapinghubClient` loads from environment variables.
    For more information, please refer to https://python-scrapinghub.readthedocs.io/en/latest/client/apidocs.html#scrapinghub.client.ScrapinghubClient.
    The project is identified through `SHUB_JOBKEY` environment variable which is set in Scrapy Cloud.
    For more information, please refer to https://shub.readthedocs.io/en/stable/custom-images-contract.html.
    '''

    def __init__(self, settings):
        self._input_field = settings.get('SPIDERFEEDER_INPUT_FIELD')
        client = ScrapinghubClient()

        jobkey = parse_job_key(os.environ['SHUB_JOBKEY'])
        project = client.get_project(jobkey.project_id)

        collection_name = settings['SPIDERFEEDER_INPUT_URI'].replace('collections://', '')
        self._store = project.collections.get_store(collection_name)

    def __iter__(self):
        for item in self._store.iter():
            data = item['value']
            if self._input_field:
                if not isinstance(data, dict):
                    raise TypeError('Collection data is expected to be a dict when SPIDERFEEDER_INPUT_FIELD is set.')  # noqa

                yield (data[self._input_field], data)
            else:
                # TODO: Return dict {} instead of None
                yield (data, None)
