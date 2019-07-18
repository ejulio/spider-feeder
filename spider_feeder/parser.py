import json
from csv import DictReader

from scrapy.exceptions import NotConfigured


class TxtParser:

    def __init__(self, settings):
        pass

    def parse(self, fd):
        return fd.read().splitlines()



class CsvParser:

    def __init__(self, settings):
        if 'SPIDERFEEDER_INPUT_FIELD' not in settings:
            raise NotConfigured('Setting "SPIDERFEEDER_INPUT_FIELD" is required for csv files.')

        self._field = settings['SPIDERFEEDER_INPUT_FIELD']

    def parse(self, fd):
        data = DictReader(fd)
        return list(map(lambda x: x[self._field], data))


class JsonParser:
    def __init__(self, settings):
        if 'SPIDERFEEDER_INPUT_FIELD' not in settings:
            raise NotConfigured('Setting "SPIDERFEEDER_INPUT_FIELD" is required for json files.')

        self._field = settings['SPIDERFEEDER_INPUT_FIELD']
    
    def parse(self, fd):
        data = json.load(fd)
        return list(map(lambda x: x[self._field], data))
